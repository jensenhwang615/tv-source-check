#!/usr/bin/env python3
"""真实起播测速——测「点开这个台要等多久、会不会卡」，而不是测 TCP 握手。

为什么不能只看 check.py 里那个 latency_ms：

  latency_ms 量的是「发出请求 → 收到响应头」。这个数字和电视上的体感几乎无关：
  - IPTV 模板（124.165.251.82）握手飞快（90ms），但它同时只服务少数用户，
    上行带宽小，一拉分片就慢，电视上转圈 2~3 秒才出画面
  - 境外转发 VPS（74.91.26.218）握手要 1.5 秒（跨洋握手三次），但分片已经在
    CDN 边缘缓存里，一旦连上就跑满带宽，起播反而更快更稳

  所以「延迟低」在这个场景里经常等于「更慢」。

本脚本量三件事，都按电视播放器的真实行为来：

  1. ttfb    —— 拉第一个分片到收到首字节的时间 ≈ 点开后的黑屏时长
  2. 码率    —— 分片大小 / 分片时长，算出这路流的实际视频码率
  3. 吞吐    —— 连拉 N 个分片的平均下载速度，和码率一比就知道会不会卡
                （吞吐 < 码率 × 1.3 就会周期性缓冲）

用法：
    python scripts/bench.py                          # 测 valid.m3u 里全部
    python scripts/bench.py --playlist sources/streams.m3u
    python scripts/bench.py --match "CCTV"           # 只测名字含 CCTV 的
    python scripts/bench.py --write-rank             # 结果写进 sources/local_rank.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check import parse_hls_attrs, pick_best_variant, session  # noqa: E402


@dataclass
class Bench:
    name: str
    url: str
    host: str = ""
    ttfb_ms: int | None = None      # 首分片首字节耗时（≈ 起播黑屏时长）
    m3u8_ms: int | None = None      # 拉 m3u8 本身耗时
    seg_kb: int = 0                 # 首分片大小
    seg_sec: float = 0.0            # 首分片对应的播放时长（秒）
    kbps: int = 0                   # 该路流码率
    speed_kbps: int = 0             # 实测下载吞吐
    ratio: float = 0.0              # 吞吐 / 码率，>1.3 才不卡
    segments: int = 0               # 实际拉到几个分片
    err: str = ""

    @property
    def score(self) -> float:
        """越低越好：起播时间 + 卡顿惩罚。"""
        if self.err:
            return 1e9
        ttfb = self.ttfb_ms or 5000
        # 吞吐不够 = 会周期性缓冲，按缺口大小罚分
        penalty = 0.0
        if self.ratio and self.ratio < 1.3:
            penalty = (1.3 - self.ratio) * 3000
        elif not self.ratio:
            penalty = 2000
        return ttfb + penalty


def _ext_segment_duration(text: str) -> float:
    """从 #EXTINF 拿分片时长。"""
    for ln in text.splitlines():
        if ln.startswith("#EXTINF:"):
            try:
                return float(ln[8:].split(",")[0].strip())
            except ValueError:
                continue
    return 0.0


def _segments(text: str, base: str, limit: int) -> list[str]:
    out = []
    for ln in text.splitlines():
        s = ln.strip()
        if s and not s.startswith("#"):
            out.append(urljoin(base, s))
            if len(out) >= limit:
                break
    return out


def bench_one(name: str, url: str, timeout: float, nseg: int,
              probe_bytes: int = 0) -> Bench:
    """probe_bytes > 0 时只读前这么多字节来测吞吐（快，适合全量扫）。

    为什么不总是读完：IPTV 模板的 1080p 分片常有 5~10MB，在带宽不够的源上
    读完整片要几十秒，全量扫一遍会跑到天亮。前 1MB 足以算出真实速度。
    """
    b = Bench(name=name, url=url, host=urlparse(url).hostname or "")
    t0 = time.perf_counter()
    try:
        r = session().get(url, timeout=timeout)
        b.m3u8_ms = int((time.perf_counter() - t0) * 1000)
        if r.status_code != 200:
            b.err = f"m3u8 HTTP {r.status_code}"
            return b
        text = r.text
        base = r.url
    except Exception as e:  # noqa: BLE001
        b.err = f"{type(e).__name__}"
        return b

    # 多码率主列表：挑最高码率那一路（播放器默认行为）
    if "#EXT-X-STREAM-INF" in text:
        v = pick_best_variant(text, base)
        if v:
            # pick_best_variant 返回 (url, RESOLUTION)，不是单个字符串
            base = v[0]
            try:
                r2 = session().get(base, timeout=timeout)
                text = r2.text
                base = r2.url
            except Exception as e:  # noqa: BLE001
                b.err = f"variant {type(e).__name__}"
                return b

    segs = _segments(text, base, nseg)
    if not segs:
        b.err = "没有分片地址"
        return b

    dur = _ext_segment_duration(text)
    b.seg_sec = dur

    # --- 第 1 个分片：测首字节（起播延迟）+ 下载速度（算吞吐）---
    t1 = time.perf_counter()
    try:
        r3 = session().get(segs[0], timeout=timeout, stream=True)
        if r3.status_code != 200:
            b.err = f"分片 HTTP {r3.status_code}"
            return b
        clen = r3.headers.get("content-length")
        body = b""
        first_byte_at = None
        cap = probe_bytes if probe_bytes > 0 else 0
        for chunk in r3.iter_content(16384):
            if first_byte_at is None:
                first_byte_at = time.perf_counter()
            body += chunk
            if cap and len(body) >= cap:
                break
        t_end = time.perf_counter()
    except Exception as e:  # noqa: BLE001
        b.err = f"分片 {type(e).__name__}"
        return b

    if not body:
        b.err = "分片为空"
        return b

    b.ttfb_ms = int(((first_byte_at or t_end) - t1) * 1000)
    total_bytes = int(clen) if (clen and clen.isdigit()) else len(body)
    b.seg_kb = total_bytes // 1024
    dl = max(t_end - (first_byte_at or t1), 0.001)

    # 吞吐：首字节之后的实际下载速度（把握手和 TTFB 摘出去）
    b.speed_kbps = int(len(body) * 8 / dl / 1000)

    # 码率：用整片大小（content-length）÷ 分片时长；拿不到长度就退化成已读部分
    if dur > 0:
        b.kbps = int(total_bytes * 8 / dur / 1000)
        b.ratio = round(b.speed_kbps / b.kbps, 2) if b.kbps else 0.0
    elif b.seg_kb:
        # 没有 EXTINF 时长，用常见 10s 分片估个大概，只用于粗判
        b.kbps = int(b.seg_kb * 8 / 10)
        b.ratio = round(b.speed_kbps / b.kbps, 2) if b.kbps else 0.0

    # --- 后续分片：只验能不能拿到（不读满），看 CDN 是否连续可用 ---
    ok = 1
    for s in segs[1:]:
        try:
            rr = session().get(s, timeout=timeout, stream=True)
            if rr.status_code == 200:
                ok += 1
                rr.close()
        except Exception:  # noqa: BLE001
            break
    b.segments = ok
    return b


def parse_playlist(path: str) -> list[tuple[str, str]]:
    out, cur = [], None
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            if ln.startswith("#EXTINF"):
                m = re.search(r'tvg-name="([^"]*)"', ln)
                if m:
                    cur = m.group(1)
                else:
                    cur = ln.rsplit(",", 1)[-1].strip()
            elif ln and not ln.startswith("#") and cur:
                out.append((cur, ln.strip()))
                cur = None
    return out


def fmt(b: Bench) -> str:
    if b.err:
        return f"  {'✗':2} {b.name:26} {b.err}"
    mark = "✓" if b.ratio >= 1.3 and (b.ttfb_ms or 9999) < 1200 else "!"
    return (
        f"  {mark:2} {b.name:26} 起播{b.ttfb_ms:>5}ms  "
        f"码率{b.kbps:>5}k  吞吐{b.speed_kbps:>5}k  "
        f"{b.ratio:>4.1f}x  分片{b.segments}/{b.seg_kb}KB"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--playlist", nargs="*", default=["dist/valid.m3u"])
    ap.add_argument("--match", default="", help="只测名字匹配这个正则的频道")
    ap.add_argument("--timeout", type=float, default=8.0)
    ap.add_argument("--concurrency", type=int, default=4,
                    help="并行测几台主机；同一主机内部始终串行")
    ap.add_argument("--segments", type=int, default=3)
    ap.add_argument("--probe-bytes", type=int, default=1536,
                    help="每条只读这么多 KB 来测吞吐（默认 1536KB）。0 = 读完整片，最准但很慢")
    ap.add_argument("--write-rank", action="store_true",
                    help="把排名写进 sources/local_rank.json")
    ap.add_argument("--rank-file", default="sources/local_rank.json")
    args = ap.parse_args()

    items: list[tuple[str, str]] = []
    for p in args.playlist:
        if os.path.exists(p):
            items.extend(parse_playlist(p))
    seen = set()
    uniq = []
    for n, u in items:
        if u in seen:
            continue
        seen.add(u)
        uniq.append((n, u))

    if args.match:
        pat = re.compile(args.match, re.I)
        uniq = [(n, u) for n, u in uniq if pat.search(n)]

    print(f"[i] 待测 {len(uniq)} 条，每条拉 {args.segments} 个分片"
          f"（吞吐只读前 {args.probe_bytes}KB）")
    print(f"[i] 按主机分组：同主机串行、不同主机并行——电视同时只看一台，"
          f"并发测同一台会把带宽抢掉，测出来的数字偏低好几倍")
    print(f"[i] 判读：✓ = 起播 <1.2s 且吞吐够；! = 会转圈或卡顿\n")

    # 按主机分组：组内串行，组间并行。
    # 这不只是「减少干扰」，而是还原真实场景：家里电视同时只播一个台，
    # 单条源能拿到多少带宽就是多少。并发测同一主机会互相抢，
    # 曾经把 CCTV-5 测成 0.3x，串行复测其实是 1.1x，差了 4 倍。
    from collections import defaultdict
    by_host: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for n, u in uniq:
        by_host[urlparse(u).hostname or "?"].append((n, u))

    t0 = time.perf_counter()
    results: list[Bench] = []
    cap = args.probe_bytes * 1024 if args.probe_bytes > 0 else 0

    def _run_host(pairs: list[tuple[str, str]]) -> list[Bench]:
        out = []
        for n, u in pairs:
            try:
                out.append(bench_one(n, u, args.timeout, args.segments, cap))
            except Exception as e:  # noqa: BLE001
                b = Bench(name=n, url=u)
                b.err = type(e).__name__
                out.append(b)
        return out

    done = 0
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as ex:
        futs = [ex.submit(_run_host, pairs) for pairs in by_host.values()]
        for f in futs:
            try:
                batch = f.result()
            except Exception:  # noqa: BLE001
                continue
            results.extend(batch)
            done += len(batch)
            print(f"[i] {done}/{len(uniq)}", flush=True)

    elapsed = time.perf_counter() - t0
    results.sort(key=lambda b: b.score)

    print(f"\n=== 按真实体感排序（耗时 {elapsed:.0f}s）===\n")
    last_host = None
    for b in results:
        if b.host != last_host:
            print()
            last_host = b.host
        print(fmt(b))

    ok = [b for b in results if not b.err]
    good = [b for b in ok if b.ratio >= 1.3 and (b.ttfb_ms or 9999) < 1200]
    print(f"\n[s] {len(ok)}/{len(results)} 能播，其中 {len(good)} 条起播快且带宽够")

    # 按主机汇总
    print("\n=== 各主机平均表现 ===")
    from collections import defaultdict
    agg = defaultdict(list)
    for b in ok:
        agg[b.host].append(b)
    for host, bs in sorted(agg.items(),
                           key=lambda kv: sum(x.score for x in kv[1]) / len(kv[1])):
        n = len(bs)
        ttfb = sum(x.ttfb_ms or 0 for x in bs) / n
        spd = sum(x.speed_kbps for x in bs) / n
        rat = sum(x.ratio for x in bs) / n
        print(f"  {host:34} n={n:2}  起播{ttfb:>6.0f}ms  吞吐{spd:>6.0f}k  {rat:>4.1f}x")

    if args.write_rank:
        rank = {}
        if os.path.exists(args.rank_file):
            try:
                rank = json.load(open(args.rank_file, encoding="utf-8"))
            except Exception:  # noqa: BLE001
                rank = {}
        # 存三类数据，curate 各取所需：
        #   urls  —— 单条源的家庭实测分（起播 + 卡顿惩罚），用来排主线路
        #   hosts —— 主机平均分，新源（没单独测过）按主机估
        #   bad   —— 明确测过带宽不够的 URL，curate 会排到最后
        urls, hosts, bad = {}, {}, []
        for b in ok:
            urls[b.url] = {
                "score": round(b.score),
                "ratio": b.ratio,
                "ttfb": b.ttfb_ms,
                "kbps": b.speed_kbps,
            }
            if b.ratio and b.ratio < 0.5:
                bad.append(b.url)
        by_host = {}
        for b in ok:
            by_host.setdefault(b.host, []).append(b)
        for h, bs in by_host.items():
            hosts[h] = {
                "score": round(sum(x.score for x in bs) / len(bs)),
                "ratio": round(sum(x.ratio for x in bs) / len(bs), 2),
                "n": len(bs),
            }
        rank["updated"] = time.strftime("%Y-%m-%d %H:%M")
        rank["note"] = ("本文件是「家庭宽带实测」的结果，不是机房测的。"
                        "curate.py 用它来决定哪个源排前面。"
                        "重跑 scripts/bench.py --write-rank 即可更新。")
        rank["urls"] = urls
        rank["hosts"] = hosts
        rank["bad"] = sorted(set(bad))
        json.dump(rank, open(args.rank_file, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(f"\n[s] 已写入 {args.rank_file}"
              f"（{len(urls)} 条 URL / {len(hosts)} 个主机 / {len(bad)} 条带宽不足）")

    return 0


if __name__ == "__main__":
    sys.exit(main())
