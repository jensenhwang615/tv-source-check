#!/usr/bin/env python3
"""检测 IPTV 直播源 / TVBox 接口是否真的可用。

设计原则:
  1. 只看"能不能真的播", 不看 HTTP 200 —— 大量失效源会返回 200 + 一个网页。
  2. HLS 一定往下钻: 主列表 -> 选码率最高的变体 -> 拉第一个分片。
  3. 组播地址(rtp/udp/igmp)无法从云端验证, 直接标记 SKIP, 不谎报。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
SKIP_SCHEMES = ("rtp://", "udp://", "igmp://", "rtmp://")
TZ8 = timezone(timedelta(hours=8))

_local = threading.local()


def session() -> requests.Session:
    s = getattr(_local, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept": "*/*", "Accept-Language": "zh-CN,zh;q=0.9"})
        _local.s = s
    return s


# ----------------------------------------------------------------------------
# 数据结构
# ----------------------------------------------------------------------------
@dataclass
class Channel:
    name: str
    url: str = ""
    group: str = ""
    raw: list[str] = field(default_factory=list)   # 原始 #EXTINF 及附属指令行


@dataclass
class Result:
    name: str
    group: str
    url: str
    status: str          # OK / DEAD / SUSPECT / SKIP
    latency_ms: int | None = None
    resolution: str | None = None
    detail: str = ""
    idx: int = 0
    raw: list[str] = field(default_factory=list)


# ----------------------------------------------------------------------------
# 解析
# ----------------------------------------------------------------------------
def parse_attrs(line: str) -> dict[str, str]:
    return {k: v for k, v in re.findall(r'([\w-]+)="([^"]*)"', line)}


def parse_hls_attrs(line: str) -> dict[str, str]:
    """HLS 标签的属性是「不加引号」的，和 m3u 的 EXTINF 不一样，必须分开解析。"""
    out: dict[str, str] = {}
    for k, v in re.findall(r'([A-Za-z0-9-]+)=("[^"]*"|[^,]*)', line):
        out[k.upper()] = v.strip().strip('"')
    return out


def parse_m3u(text: str) -> list[Channel]:
    channels: list[Channel] = []
    cur: Channel | None = None
    for raw_line in text.splitlines():
        s = raw_line.strip()
        if not s or s.startswith("#EXTM3U"):
            continue
        if s.startswith("#EXTINF"):
            if cur and cur.url:
                channels.append(cur)
            attrs = parse_attrs(s)
            name = s.split(",", 1)[1].strip() if "," in s else attrs.get("tvg-name", "未命名")
            cur = Channel(name=name, group=attrs.get("group-title", ""), raw=[s])
        elif s.startswith("#"):
            if cur is not None:
                cur.raw.append(s)
        else:
            if cur is None:
                channels.append(Channel(name=s, url=s, raw=[s]))
            else:
                cur.url = s
                channels.append(cur)
                cur = None
    if cur and cur.url:
        channels.append(cur)
    return channels


# ----------------------------------------------------------------------------
# 底层抓取
# ----------------------------------------------------------------------------
def origin_ref(url: str) -> str:
    """把 URL 的源站地址当作 Referer。国内 IPTV 网关和百视通这类 CDN 会校验它。"""
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}/" if p.scheme and p.netloc else ""


def fetch(url: str, timeout: float, limit: int = 65536, ref: str | None = None) -> dict:
    headers = {"Referer": ref} if ref else None
    r = session().get(url, timeout=timeout, stream=True, allow_redirects=True, headers=headers)
    info = {
        "status": r.status_code,
        "ctype": r.headers.get("content-type", "").lower(),
        "final": r.url,
        "len_hint": r.headers.get("content-length"),
    }
    body = b""
    try:
        for chunk in r.iter_content(16384):
            body += chunk
            if len(body) >= limit:
                break
    finally:
        r.close()
    info["body"] = body
    return info


def pick_best_variant(text: str, base: str):
    """从多码率主列表中挑带宽最高的一路。"""
    lines = text.splitlines()
    best = None
    for i, ln in enumerate(lines):
        if not ln.startswith("#EXT-X-STREAM-INF"):
            continue
        attrs = parse_hls_attrs(ln)
        try:
            bw = int(attrs.get("BANDWIDTH", "0") or 0)
        except ValueError:
            bw = 0
        uri = ""
        for j in range(i + 1, min(i + 8, len(lines))):
            cand = lines[j].strip()
            if cand and not cand.startswith("#"):
                uri = cand
                break
        if uri and (best is None or bw > best[0]):
            best = (bw, urljoin(base, uri), attrs.get("RESOLUTION"))
    return (best[1], best[2]) if best else None


def first_segment(text: str, base: str):
    for ln in text.splitlines():
        s = ln.strip()
        if s and not s.startswith("#"):
            return urljoin(base, s)
    return None


# ----------------------------------------------------------------------------
# 单条检测
# ----------------------------------------------------------------------------
def probe(url: str, timeout: float, depth: int = 0, ref: str | None = None) -> tuple[str, int | None, str | None, str]:
    if url.lower().startswith(SKIP_SCHEMES):
        return "SKIP", None, None, "组播/RTMP, 只能在本地网络验证"

    t0 = time.perf_counter()
    try:
        info = fetch(url, timeout, ref=ref)
        # 两条容错，都是为了不把「能播」误判成「死」：
        #  1) 401/403 常见是防盗链 —— 补源站 Referer 再试一次；
        #  2) 404/429/5xx 常见是并发太快被临时挡 —— 退避一次再试。
        # 实测过：连着打同一台 CDN 会整片 404，隔 1 秒单条请求又是 200。
        if info["status"] in (401, 403) and ref is None:
            cand = origin_ref(url)
            if cand:
                info = fetch(url, timeout, ref=cand)
                if info["status"] < 400:
                    ref = cand
        if info["status"] in (403, 404, 429, 500, 502, 503, 504):
            time.sleep(0.8)
            info = fetch(url, timeout, ref=ref)
            if info["status"] < 400:
                ref = ref or origin_ref(url)
    except requests.exceptions.SSLError:
        return "DEAD", None, None, "SSL 握手失败"
    except requests.exceptions.Timeout:
        return "DEAD", None, None, f"超时 >{timeout}s"
    except requests.exceptions.ConnectionError:
        return "DEAD", None, None, "连接失败/DNS 解析不了"
    except Exception as e:  # noqa: BLE001
        return "DEAD", None, None, f"{type(e).__name__}"
    ms = int((time.perf_counter() - t0) * 1000)
    note = ", 需 Referer" if ref else ""

    if info["status"] >= 400:
        return "DEAD", ms, None, f"HTTP {info['status']}"

    body = info["body"]
    if not body:
        return "DEAD", ms, None, "响应体为空"

    if b"#EXTM3U" in body[:1024]:
        text = body.decode("utf-8", "ignore")
        if "#EXT-X-STREAM-INF" in text:
            if depth >= 2:
                return "OK", ms, None, "多码率主列表可读" + note
            variant = pick_best_variant(text, info["final"])
            if not variant:
                return "SUSPECT", ms, None, "主列表解析不出子流"
            vurl, res = variant
            sub_status, _, sub_res, sub_detail = probe(vurl, timeout, depth + 1, ref)
            return sub_status, ms, res or sub_res, f"变体: {sub_detail}"
        seg = first_segment(text, info["final"])
        if not seg:
            return "SUSPECT", ms, None, "播放列表是空的"
        try:
            seg_info = fetch(seg, timeout, limit=8192, ref=ref)
        except Exception as e:  # noqa: BLE001
            return "SUSPECT", ms, None, f"分片请求失败 {type(e).__name__}"
        if seg_info["status"] >= 400 or not seg_info["body"]:
            return "SUSPECT", ms, None, f"分片 HTTP {seg_info['status']}"
        return "OK", ms, None, f"HLS 分片可下载 ({len(seg_info['body'])}B){note}"

    head = body[:512].lstrip().lower()
    if head.startswith(b"<html") or head.startswith(b"<!doctype") or b"<html" in head:
        return "SUSPECT", ms, None, "返回网页而非视频流"
    return "OK", ms, None, f"裸流可读 ({len(body)}B){note}"


def check_channel(ch: Channel, timeout: float, idx: int = 0, blocked: set[str] | None = None) -> Result:
    status, ms, res, detail = probe(ch.url, timeout)
    host = urlparse(ch.url).hostname or ""
    # 被站点按 IP 限流 / 封禁，和「源本身死了」是两件事：
    # 前者换个 IP（家里宽带、换网络）就能看，不该判死、也不该踢出 valid.m3u。
    if blocked and host in blocked and status in ("DEAD", "SUSPECT"):
        status = "BLOCKED"
        detail = f"本机 IP 被该站限流/封锁（此前可播）: {detail}"
    return Result(ch.name, ch.group, ch.url, status, ms, res, detail, idx, ch.raw)


# ----------------------------------------------------------------------------
# TVBox 接口检测
# ----------------------------------------------------------------------------
def check_tvbox(url: str, timeout: float, deep: int = 0) -> dict:
    out = {"url": url, "status": "DEAD", "sites": 0, "lives": 0, "repos": 0, "detail": ""}
    if not url.lower().startswith(("http://", "https://")):
        out["status"] = "SKIP"
        out["detail"] = "不是 http 地址"
        return out
    try:
        info = fetch(url, timeout, limit=4_000_000)
    except Exception as e:  # noqa: BLE001
        out["detail"] = f"{type(e).__name__}"
        return out
    if info["status"] >= 400:
        out["detail"] = f"HTTP {info['status']}"
        return out
    text = info["body"].decode("utf-8-sig", "ignore").strip()
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        out["detail"] = "不是合法 JSON (可能返回了网页)"
        out["status"] = "SUSPECT"
        return out
    if not isinstance(data, dict):
        out["status"] = "SUSPECT"
        out["detail"] = "顶层不是对象"
        return out

    sites = data.get("sites") or []
    lives = data.get("lives") or []
    repos = data.get("urls") or []
    out["sites"] = len(sites) if isinstance(sites, list) else 0
    out["lives"] = len(lives) if isinstance(lives, list) else 0
    out["repos"] = len(repos) if isinstance(repos, list) else 0
    has_spider = bool(data.get("spider"))

    if out["sites"] == 0 and out["lives"] == 0 and out["repos"] == 0:
        out["status"] = "SUSPECT"
        out["detail"] = "JSON 里没有任何 sites/lives/urls"
        return out

    out["status"] = "OK"
    bits = [f"{out['sites']} 站点"]
    if out["lives"]:
        bits.append(f"{out['lives']} 直播")
    if out["repos"]:
        bits.append(f"{out['repos']} 子仓")
    if has_spider:
        bits.append("含 spider(远程加载, 权限较高)")
    out["detail"] = ", ".join(bits)

    # 深度检测: 抽查 N 个站点的采集 API 是否有返回
    if deep and isinstance(sites, list):
        ok = 0
        tested = 0
        for site in sites:
            if tested >= deep:
                break
            api = (site or {}).get("api", "")
            if not api or not str(api).startswith(("http://", "https://")):
                continue
            tested += 1
            sep = "&" if "?" in api else "?"
            try:
                r = session().get(f"{api}{sep}ac=list", timeout=timeout)
                if r.status_code < 400 and len(r.content) > 50:
                    ok += 1
            except Exception:  # noqa: BLE001
                pass
        out["detail"] += f"; API 抽查 {ok}/{tested} 有响应"
        if tested >= 2 and ok == 0:
            out["status"] = "SUSPECT"
    return out


# ----------------------------------------------------------------------------
# 输出
# ----------------------------------------------------------------------------
def pick_diverse(items: list[Result], n: int) -> list[Result]:
    """同一频道最多留 n 条，但优先选不同主机的线路——避免整份清单压在单台服务器上。"""
    items = sorted(items, key=lambda x: x.latency_ms if x.latency_ms is not None else 99999)
    chosen: list[Result] = []
    hosts: set[str] = set()
    for it in items:
        h = urlparse(it.url).hostname or ""
        if h in hosts:
            continue
        chosen.append(it)
        hosts.add(h)
        if len(chosen) >= n:
            return chosen
    for it in items:
        if it not in chosen:
            chosen.append(it)
            if len(chosen) >= n:
                break
    return chosen


def write_m3u(path: Path, results: list[Result], keep_per_name: int = 0) -> None:
    # 同一个 URL 可能在手工清单和 auto.m3u 里各出现一次（名字不同），只保留先出现的那个——
    # 手工清单在 --playlist 里排前面，所以留下的是人写的那条友好命名。
    seen_urls: set[str] = set()
    deduped: list[Result] = []
    for r in results:
        key = r.url.strip()
        if key in seen_urls:
            continue
        seen_urls.add(key)
        deduped.append(r)
    results = deduped
    if keep_per_name:
        grouped: dict[str, list[Result]] = {}
        for r in results:
            grouped.setdefault(r.name, []).append(r)
        order = {id(r): i for i, r in enumerate(results)}
        trimmed: list[Result] = []
        for items in grouped.values():
            trimmed.extend(pick_diverse(items, keep_per_name))
        results = sorted(trimmed, key=lambda r: order[id(r)])
    lines = ["#EXTM3U"]
    for r in results:
        lines.extend(r.raw)
        lines.append(r.url)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_report(results: list[Result], tvbox: list[dict], ratio: float, started: datetime) -> str:
    ok = [r for r in results if r.status == "OK"]
    dead = [r for r in results if r.status == "DEAD"]
    suspect = [r for r in results if r.status == "SUSPECT"]
    skip = [r for r in results if r.status == "SKIP"]
    blocked = [r for r in results if r.status == "BLOCKED"]

    groups: dict[str, list[Result]] = {}
    for r in results:
        groups.setdefault(r.group or "未分组", []).append(r)

    out = [
        "# 源可用性报告",
        "",
        f"检测时间: {started:%Y-%m-%d %H:%M} (UTC+8)　耗时 {int((datetime.now(TZ8) - started).total_seconds())}s",
        "",
        f"**共 {len(results)} 条 · 可用 {len(ok)} ({ratio:.0%}) · 失效 {len(dead)} · 可疑 {len(suspect)}"
        f" · 被限流 {len(blocked)} · 跳过 {len(skip)}**",
        "",
        "## 按分组",
        "",
        "| 分组 | 可用 / 总数 | 被限流 | 可用率 |",
        "|---|---|---|---|",
    ]
    for g, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        g_ok = sum(1 for i in items if i.status == "OK")
        g_bl = sum(1 for i in items if i.status == "BLOCKED")
        denom = len(items) - g_bl
        rate = f"{g_ok / denom:.0%}" if denom else "—"
        out.append(f"| {g} | {g_ok} / {len(items)} | {g_bl} | {rate} |")

    if blocked:
        hosts = sorted({urlparse(r.url).hostname or "" for r in blocked})
        out += [
            "",
            "## 被限流（不是失效）",
            "",
            f"以下 {len(blocked)} 条来自 {', '.join(f'`{h}`' for h in hosts)}。"
            "这些地址此前实测可播，本次是本机 IP 被站点限流/封锁才失败；"
            "**已保留在 valid.m3u 里**，换个 IP（家里宽带、手机热点）通常就能看。",
            "",
        ]

    if dead or suspect:
        out += ["", "## 失效 / 可疑明细", "", "| 频道 | 分组 | 状态 | 原因 | 延迟 |", "|---|---|---|---|---|"]
        for r in (dead + suspect)[:200]:
            out.append(
                f"| {r.name} | {r.group or '-'} | {r.status} | {r.detail} | "
                f"{r.latency_ms if r.latency_ms is not None else '-'}ms |"
            )
        if len(dead) + len(suspect) > 200:
            out.append(f"| ... | | | 其余 {len(dead) + len(suspect) - 200} 条见 status.json | |")

    if tvbox:
        out += ["", "## TVBox 接口", "", "| 接口 | 状态 | 内容 |", "|---|---|---|"]
        for t in tvbox:
            name = t["url"] if len(t["url"]) < 60 else t["url"][:57] + "..."
            out.append(f"| `{name}` | {t['status']} | {t['detail']} |")

    ok_sorted = sorted([r for r in ok if r.latency_ms is not None], key=lambda r: r.latency_ms)
    if ok_sorted:
        out += ["", "## 最快的 10 条", "", "| 频道 | 延迟 | 分辨率 |", "|---|---|---|"]
        for r in ok_sorted[:10]:
            out.append(f"| {r.name} | {r.latency_ms}ms | {r.resolution or '-'} |")
    out.append("")
    return "\n".join(out)


# ----------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="检测 IPTV 源与 TVBox 接口")
    ap.add_argument(
        "--playlist",
        nargs="+",
        default=["sources/streams.m3u"],
        help="m3u 播放列表，可以给多个，合并检测",
    )
    ap.add_argument("--tvbox", default="sources/tvbox.txt", help="TVBox 接口列表, 一行一个")
    ap.add_argument("--out", default="dist", help="输出目录")
    ap.add_argument("--timeout", type=float, default=8.0)
    ap.add_argument("--concurrency", type=int, default=24)
    ap.add_argument("--deep", type=int, default=0, help="TVBox 抽查几个站点的采集 API (0=关闭)")
    ap.add_argument("--keep-per-name", type=int, default=2, help="valid.m3u 里每个频道最多保留几条线路")
    ap.add_argument("--fail-if-below", type=float, default=0.0, help="可用率低于此值则退出码 1")
    ap.add_argument(
        "--blocked-host",
        nargs="*",
        default=[],
        help="这些主机的失败判为 BLOCKED（本机 IP 被限流），不计入失效、不踢出 valid.m3u",
    )
    args = ap.parse_args()
    blocked = {h.strip() for h in args.blocked_host if h.strip()}

    started = datetime.now(TZ8)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    channels: list[Channel] = []
    for p in args.playlist:
        fp = Path(p)
        if fp.exists():
            channels.extend(parse_m3u(fp.read_text(encoding="utf-8-sig")))
        else:
            print(f"[!] 找不到 {p}，跳过")
    print(f"[i] 解析到 {len(channels)} 条直播源")

    results: list[Result] = []
    if channels:
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futures = {ex.submit(check_channel, c, args.timeout, i, blocked): c for i, c in enumerate(channels)}
            done = 0
            for fut in as_completed(futures):
                done += 1
                try:
                    results.append(fut.result())
                except Exception as e:  # noqa: BLE001
                    c = futures[fut]
                    idx = next(i for i, ch in enumerate(channels) if ch is c)
                    results.append(
                        Result(c.name, c.group, c.url, "DEAD", None, None, f"{type(e).__name__}", idx, c.raw)
                    )
                if done % 20 == 0 or done == len(channels):
                    oks = sum(1 for r in results if r.status == "OK")
                    print(f"[i] {done}/{len(channels)} 已检测, 当前可用 {oks}", flush=True)

    results.sort(key=lambda r: r.idx)

    tvbox_results: list[dict] = []
    tb = Path(args.tvbox)
    if tb.exists():
        urls = [
            ln.strip()
            for ln in tb.read_text(encoding="utf-8-sig").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        for u in urls:
            tvbox_results.append(check_tvbox(u, args.timeout, args.deep))
        print(f"[i] 检测 {len(tvbox_results)} 个 TVBox 接口")

    ok = [r for r in results if r.status == "OK"]
    blocked = [r for r in results if r.status == "BLOCKED"]
    counted = len(results) - len(blocked)
    ratio = len(ok) / counted if counted else 0.0

    # 被限流的那批不算「死」，留在 valid.m3u 里——换个 IP 就能播
    write_m3u(out_dir / "valid.m3u", ok + blocked, args.keep_per_name)
    write_m3u(out_dir / "dead.m3u", [r for r in results if r.status in ("DEAD", "SUSPECT")])
    (out_dir / "report.md").write_text(build_report(results, tvbox_results, ratio, started), encoding="utf-8")
    (out_dir / "status.json").write_text(
        json.dumps(
            {
                "checked_at": started.isoformat(),
                "summary": {
                    "total": len(results),
                    "ok": len(ok),
                    "dead": sum(1 for r in results if r.status == "DEAD"),
                    "suspect": sum(1 for r in results if r.status == "SUSPECT"),
                    "skip": sum(1 for r in results if r.status == "SKIP"),
                    "blocked": len(blocked),
                    "ratio": round(ratio, 4),
                },
                "channels": [asdict(r) for r in results],
                "tvbox": tvbox_results,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    color = "brightgreen" if ratio >= 0.9 else "green" if ratio >= 0.7 else "yellow" if ratio >= 0.5 else "red"
    (out_dir / "badge.json").write_text(
        json.dumps(
            {"schemaVersion": 1, "label": "源可用率", "message": f"{ratio:.0%}", "color": color},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"[✓] 可用 {len(ok)}/{counted} = {ratio:.1%}，被限流 {len(blocked)} 条（换 IP 可播，已保留在 valid.m3u），结果已写入 {out_dir}/")
    if args.fail_if_below and ratio < args.fail_if_below:
        print(f"[!] 可用率低于阈值 {args.fail_if_below:.0%}，退出码 1（GitHub 会给你发失败邮件）")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
