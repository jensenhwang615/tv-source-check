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

from curate import build_m3u, curate

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
        # 必须忽略环境里的 http_proxy / https_proxy。
        # 否则在 IDE 沙箱里跑（127.0.0.1:2404 之类）时，请求会被代理接管，
        # 代理对 IPTV 域名返回的是「频道没有配置任何服务器」「not available in
        # your area」这类伪造响应 —— 实测过：同一台 74.91 走代理全挂，
        # 直连 200 且内容正常。测源必须直连，否则量到的不是用户电视看到的东西。
        s.trust_env = False
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


def result_from_dict(d: dict) -> Result:
    """从 status.json 的一条记录还原 Result（--from-status 复用旧结果时用）。"""
    st = d.get("status") or "DEAD"
    detail = d.get("detail") or ""
    # 和 check_channel 里同一条规则：403 是「拒绝访问」而不是「源没了」。
    # 写在这里，才能用 --from-status 把上一轮判成 DEAD 的 403 批量修正过来，
    # 不必为了改一个判定规则把几百条源重新联网测一遍。
    if st == "DEAD" and detail == "HTTP 403":
        st, detail = "BLOCKED", "HTTP 403 拒绝访问（地域封锁/防盗链，换网络再试）"
    return Result(
        name=d.get("name") or "",
        group=d.get("group") or "",
        url=d.get("url") or "",
        status=st,
        latency_ms=d.get("latency_ms"),
        resolution=d.get("resolution"),
        detail=detail,
        idx=d.get("idx") or 0,
        raw=d.get("raw") or [],
    )


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

    # 走到这里说明不是 HLS。要区分「真·裸流（TS/FLV/MP4）」和「一段错误提示文字」。
    # 老版本把任何非网页响应都算「裸流可读」，于是
    # `http://.../cctv5hd.m3u8` 返回的 41 字节 "the content is not available in your area"
    # 被当成可用源写进清单 —— 电视上点开就黑屏。这类地域封锁提示必须判死。
    ctype = info.get("ctype", "")
    if any(t in ctype for t in ("video/", "mpegurl", "mp2t")):
        return "OK", ms, None, f"裸流可读 ({len(body)}B, {ctype}){note}"
    if body[:1] == b"\x47" or body[:3] == b"FLV" or b"ftyp" in body[:16]:
        return "OK", ms, None, f"裸流可读 ({len(body)}B){note}"

    text = body[:200].decode("utf-8", "ignore").strip()
    if text:
        printable = sum(1 for ch in text if ch.isprintable() or ch in "\r\n\t")
        if printable / len(text) > 0.9:
            one = " ".join(text.split())[:70]
            return "DEAD", ms, None, f"返回提示文字而非视频流: {one}"

    return "SUSPECT", ms, None, f"无法识别的响应 ({len(body)}B, {ctype or '无 content-type'})"


def check_channel(ch: Channel, timeout: float, idx: int = 0, blocked: set[str] | None = None) -> Result:
    status, ms, res, detail = probe(ch.url, timeout)
    host = urlparse(ch.url).hostname or ""

    # 央视官网源单独豁免。
    #
    # 这套地址（tv.cctv.com 背后，路径带 cdrmldcctv）走的是金山云/网宿/腾讯云/
    # 百度云/火山这些国内 CDN。它们在中国大陆家里实测 20~270Mbps，但 GitHub 的
    # runner 在 Azure 境外机房，到百度云、火山这类国内节点经常路由不通。
    #
    # 具体表现：同一份清单，家里跑 16 个台全通，Actions 跑只剩 12 个台，
    # 缺的 CCTV-5/6/9/14 在清单里退回成慢的第三方源——用户在电视上看到的就是
    # 「换了新源，这几个台还是卡」。
    #
    # 判 BLOCKED 的含义是「换网络可播」，正好对应这里的情况。但 404 不能豁免：
    # 那是地址真的没了，换什么网络都不会好。
    _is_official = "cdrmldcctv" in ch.url or "/hls_cdrm/" in ch.url
    if _is_official and status in ("DEAD", "SUSPECT") and "404" not in detail:
        return Result(ch.name, ch.group, ch.url, "BLOCKED", ms, res,
                      f"官方源在境外机房不可达（国内家宽可播）: {detail}", idx, ch.raw)

    # 403 单独算一类：它说的是「服务器认得你但拒绝服务」，成因基本是地域封锁、
    # 防盗链或 IP 黑名单，而不是「这个源没了」（那是 404）。香港台尤其如此——
    # 翡翠台、明珠台、凤凰这几个的一组源在广东家宽上几乎全 403，在境外机房却正常。
    # 判死会把整组香港台从清单里删掉，所以统一降级成 BLOCKED 保留下来。
    if status == "DEAD" and detail == "HTTP 403":
        return Result(ch.name, ch.group, ch.url, "BLOCKED", ms, res,
                      "HTTP 403 拒绝访问（地域封锁/防盗链，换网络再试）", idx, ch.raw)

    # 被站点按 IP 限流 / 封禁，和「源本身死了」是两件事：
    # 前者换个 IP（家里宽带、换网络）就能看，不该判死、也不该踢出 valid.m3u。
    #
    # 但这条豁免不能滥用。以前只要主机在 --blocked-host 里，任何失败都算 BLOCKED，
    # 于是「频道 xxx 没有配置任何源」这种明确的错误 JSON、以及
    # "the content is not available in your area" 这种地域封锁提示，
    # 全都以 BLOCKED 的身份赖在清单里 —— 电视上点开就是黑屏。
    # 只有「拿不到内容」型失败（HTTP 错误码、空响应、超时）才算限流。
    _NOT_THROTTLE = ("提示文字", "返回网页", "无法识别")
    if blocked and host in blocked and status in ("DEAD", "SUSPECT") \
            and not any(k in detail for k in _NOT_THROTTLE):
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
# 「同频道优先选不同主机」的去重逻辑在 curate.py 里（_pick_diverse），
# 这里不再重复实现一份，避免两边算法漂移。
def write_m3u(
    path: Path,
    results: list[Result],
    keep_per_name: int = 2,
    header: list[str] | None = None,
) -> dict:
    """写「可直接订阅」的清单：剔除付费/误采、统一命名、按台序排列。

    整理规则全部在 curate.py 里，这里只负责调用。返回统计信息给报告用。
    """
    entries, stats = curate(results, keep_per_name)
    path.write_text(build_m3u(entries, header), encoding="utf-8")
    return stats


def write_m3u_raw(path: Path, results: list[Result]) -> None:
    """写原始清单（失效明细用）：保持原样，方便对着排查是哪条挂了。"""
    seen: set[str] = set()
    lines = ["#EXTM3U"]
    for r in results:
        key = r.url.strip()
        if key in seen:
            continue
        seen.add(key)
        lines.extend(r.raw)
        lines.append(r.url)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_report(
    results: list[Result],
    tvbox: list[dict],
    ratio: float,
    started: datetime,
    curate_stats: dict | None = None,
) -> str:
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

    if curate_stats and (curate_stats.get("kept") or curate_stats.get("dropped_total")):
        kept = curate_stats.get("kept", 0)
        dropped = curate_stats.get("dropped_total", 0)
        out += [
            "",
            "## 清单整理",
            "",
            f"可用 {len(ok) + len(blocked)} 条 → 去重合并后写进 `valid.m3u` 的 **{kept} 条**。"
            f"另有 {dropped} 条不进清单（付费频道 / 名字撞关键词的误采内容）。",
            "",
        ]
        names = curate_stats.get("dropped_names") or {}
        if names:
            out += ["被剔除的内容：", ""]
            for n, c in sorted(names.items(), key=lambda kv: -kv[1]):
                out.append(f"- `{n}`")
            out.append("")

        missing = curate_stats.get("missing_cctv") or []
        out += [
            "台号规则：每个频道一个固定编号（央视 = 频道号本身，CCTV-5 恒为 5 号台），"
            "不随本轮测通情况移动。某个台本轮没测通时台号留空，后面的台不会顶上来。",
            "",
        ]
        if missing:
            out += [
                f"本轮央视 1-17 中未测通、台号留空的有 **{len(missing)} 个**："
                + "、".join(m.split(" ")[0] for m in missing),
                "",
            ]
        else:
            out += ["本轮央视 1-17 全部有可用源。", ""]

    if tvbox:
        out += ["", "## TVBox 接口", "", "| 接口 | 状态 | 内容 |", "|---|---|---|"]
        for t in tvbox:
            name = t["url"] if len(t["url"]) < 60 else t["url"][:57] + "..."
            out.append(f"| `{name}` | {t['status']} | {t['detail']} |")

    # 「最快的 10 条」只统计真正进了 valid.m3u 的，
    # 否则会出现「某个已被剔除的付费台/误采内容跑得最快」这种自我矛盾的场面。
    kept_urls = (curate_stats or {}).get("kept_urls") or set()
    kept_names = (curate_stats or {}).get("kept_names") or {}
    ok_sorted = sorted(
        [r for r in ok if r.latency_ms is not None and (not kept_urls or r.url in kept_urls)],
        key=lambda r: r.latency_ms,
    )
    if ok_sorted:
        out += ["", "## 最快的 10 条", "", "| 频道 | 延迟 | 分辨率 |", "|---|---|---|"]
        seen_canon: set[str] = set()
        shown = 0
        for r in ok_sorted:
            canon = kept_names.get(r.url, r.name)
            if canon in seen_canon:      # 同一个台的多条线路只报最快的那个
                continue
            seen_canon.add(canon)
            out.append(f"| {canon} | {r.latency_ms}ms | {r.resolution or '-'} |")
            shown += 1
            if shown >= 10:
                break
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
    ap.add_argument(
        "--from-status",
        default="",
        help="复用已有的 status.json，不重新联网检测（只改整理规则时用，几秒出结果）",
    )
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

    results: list[Result] = []
    tvbox_results: list[dict] = []

    if args.from_status:
        # 只改整理规则、不想重新联网跑一遍时用这个：
        # 拿上次的 status.json 复用检测结论，几秒内就能生成新的 valid.m3u 和报告。
        src = Path(args.from_status)
        data = json.loads(src.read_text(encoding="utf-8"))
        results = [result_from_dict(c) for c in data.get("channels", [])]
        tvbox_results = data.get("tvbox") or []
        started = datetime.fromisoformat(data["checked_at"])
        print(f"[i] 复用 {src} 的检测结果：{len(results)} 条（不重新联网）")
    else:
        channels: list[Channel] = []
        for p in args.playlist:
            fp = Path(p)
            if fp.exists():
                channels.extend(parse_m3u(fp.read_text(encoding="utf-8-sig")))
            else:
                print(f"[!] 找不到 {p}，跳过")
        print(f"[i] 解析到 {len(channels)} 条直播源")

        if channels:
            # 同一台主机上的源串行测，不同主机之间并行。
            #
            # 这条是必须的。有些 IPTV 网关就是家用宽带搭的（比如 124.165.251.82），
            # 单条请求 50~150ms 很健康，但十几条并发打过去就整片超时。
            # 全并发测法会把这类主机上的源全部判死，于是明明能播的台（央视 1-15 都在它上面）
            # 从清单里整片消失。按 host 串行之后测出来才是真实可用性。
            by_host: dict[str, list[tuple[int, Channel]]] = {}
            for i, c in enumerate(channels):
                by_host.setdefault(urlparse(c.url).hostname or f"_{i}", []).append((i, c))

            def run_host(items: list[tuple[int, Channel]]) -> list[Result]:
                got: list[Result] = []
                for i, c in items:
                    try:
                        got.append(check_channel(c, args.timeout, i, blocked))
                    except Exception as e:  # noqa: BLE001
                        got.append(
                            Result(c.name, c.group, c.url, "DEAD", None, None,
                                   f"{type(e).__name__}", i, c.raw)
                        )
                    time.sleep(0.15)     # 给弱主机留口气
                return got

            total = len(channels)
            with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
                futures = [ex.submit(run_host, items) for items in by_host.values()]
                done = 0
                for fut in as_completed(futures):
                    batch = fut.result()
                    results.extend(batch)
                    done += len(batch)
                    if done % 20 < len(batch) or done >= total:
                        oks = sum(1 for r in results if r.status == "OK")
                        print(f"[i] {done}/{total} 已检测, 当前可用 {oks}", flush=True)

        results.sort(key=lambda r: r.idx)

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
    stats = write_m3u(
        out_dir / "valid.m3u",
        ok + blocked,
        args.keep_per_name,
        header=[
            "# 央视 + 广东 + 港澳 + 体育｜每 6 小时自动重新检测",
            "#",
            "# 用法：把这个文件当 M3U 播放列表导入即可，分组已按「央视 → 广东 → 香港 → 澳门 → 体育」排好。",
            "# 同一频道有多条线路时，标注 (线路2) (线路3)，任意一条能播就用那条。",
            "#",
            "# 本文件由 scripts/check.py 自动生成，手工修改会在下次运行时被覆盖。",
            "# 想长期保留自己的源，请写进 sources/ 目录下的清单。",
        ],
    )
    write_m3u_raw(out_dir / "dead.m3u", [r for r in results if r.status in ("DEAD", "SUSPECT")])
    (out_dir / "report.md").write_text(
        build_report(results, tvbox_results, ratio, started, stats), encoding="utf-8"
    )
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
    # 徽章只报「清单里有多少条」，不报可用率。
    # 原因一: 分母里混着 auto.m3u 几百条自动采集的地域封锁源, 百分比常年 10% 出头,
    #         挂在公开仓库首页会被误读成「这项目废了」。条数才是用户真正关心的。
    # 原因二: 必须用整理后的条数（stats["kept"]），不能用检测通过的条数——
    #         后者包含被剔除的付费台和重复线路，和用户真正订阅到的数量对不上。
    n_kept = stats.get("kept", len(ok))
    color = "brightgreen" if n_kept >= 60 else "green" if n_kept >= 40 else "yellow" if n_kept >= 20 else "red"
    (out_dir / "badge.json").write_text(
        json.dumps(
            {"schemaVersion": 1, "label": "清单条数", "message": f"{n_kept} 条", "color": color},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"[✓] 可用 {len(ok)}/{counted} = {ratio:.1%}，被限流 {len(blocked)} 条（换 IP 可播，已保留在 valid.m3u），"
        f"整理后 {n_kept} 条写入 {out_dir}/"
    )
    if args.fail_if_below and ratio < args.fail_if_below:
        print(f"[!] 可用率低于阈值 {args.fail_if_below:.0%}，退出码 1（GitHub 会给你发失败邮件）")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
