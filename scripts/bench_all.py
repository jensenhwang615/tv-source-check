#!/usr/bin/env python3
"""全量测速，把每条源的 ratio 固化下来。

和 bench.py 的区别：
  bench.py 是「测几条看看」，本脚本是「把清单里所有源过一遍」，
  所以做了三件 bench.py 没做的事：

  1. 边测边写 .tmp/bench.jsonl —— 中途被打断（卡死、Ctrl-C、超时）
     已测的部分不丢，可以断点续跑（--resume 跳过已测的 URL）。
  2. 按主机分组，组内串行。同一台机器并发会互抢带宽 —— 实测把
     CCTV-5 测成 0.3x，串行复测 1.1x，差 4 倍，数据完全失真。
  3. 每条只读 probe_bytes 字节就切断。分片常有 5~10MB，全读一遍
     要 17 分钟，而判断「带宽够不够」只需要前 512KB。

输出 sources/local_rank.json：
  urls  —— 每条 URL 的分（score 越小越好）
  hosts —— 按主机聚合的均分，用来给「没单独测过的同主机源」估分
  bad   —— ratio < 0.5 的 URL，curate 会直接丢到最后一档

用法：
  python scripts/bench_all.py --playlist sources/streams.m3u sources/backup.m3u \\
      sources/hk.m3u sources/sports.m3u --resume
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bench import bench_one  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSONL = os.path.join(ROOT, ".tmp", "bench.jsonl")
OUT_RANK = os.path.join(ROOT, "sources", "local_rank.json")


def parse_playlist(paths: list[str]) -> list[tuple[str, str]]:
    """返回 [(频道名, url)]，去重（同 URL 只测一次）。"""
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for p in paths:
        if not os.path.exists(p):
            continue
        cur = ""
        with open(p, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#EXTINF"):
                    cur = line.split(",", 1)[-1].strip()
                elif line.startswith("http") and line not in seen:
                    seen.add(line)
                    pairs.append((cur or "?", line))
    return pairs


def load_done() -> dict[str, dict]:
    """断点续跑：读已经测过的 URL。"""
    done: dict[str, dict] = {}
    if not os.path.exists(OUT_JSONL):
        return done
    with open(OUT_JSONL, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            done[rec["url"]] = rec
    return done


def host_of(url: str) -> str:
    from urllib.parse import urlparse

    return urlparse(url).hostname or ""


def score_of(rec: dict) -> float:
    """本文件的 score 只表示「起播多久出画面」，也就是首字节时间，单位毫秒。

    带宽不够的罚分**不在这里做**，统一由 curate.py 的 _score 补上。
    分开的理由：罚分公式只该有一份。曾经两边各算一次，同一个源被罚了两遍，
    分数虚高到没法横向比较（ratio 0.5 的源实际 2300 分被记成 4300）。
    """
    ttfb = rec.get("ttfb_ms")
    return 3000.0 if ttfb is None else float(ttfb)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--playlist", nargs="+", required=True)
    ap.add_argument("--timeout", type=float, default=8.0)
    ap.add_argument("--segments", type=int, default=2)
    ap.add_argument("--probe-bytes", type=int, default=524288, help="每条最多读这么多字节就停")
    ap.add_argument("--concurrency", type=int, default=5, help="同时测几个主机")
    ap.add_argument("--resume", action="store_true", help="跳过 jsonl 里已测过的 URL")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(OUT_JSONL), exist_ok=True)
    pairs = parse_playlist(args.playlist)
    done = load_done() if args.resume else {}

    todo = [(n, u) for n, u in pairs if u not in done]
    print(f"共 {len(pairs)} 条，已测 {len(done)} 条，待测 {len(todo)} 条", flush=True)
    if not todo:
        return _write_rank(done)

    # 按主机分组：同一台的源必须排队测，否则并发互抢带宽，数据失真
    by_host: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for n, u in todo:
        by_host[host_of(u)].append((n, u))
    print(f"分布在 {len(by_host)} 个主机上", flush=True)

    fout = open(OUT_JSONL, "a", encoding="utf-8")
    t0 = time.time()
    done_n = 0

    def _run_host(items: list[tuple[str, str]]) -> list[dict]:
        out = []
        for name, url in items:
            try:
                b = bench_one(name, url, timeout=args.timeout, nseg=args.segments,
                              probe_bytes=args.probe_bytes)
                out.append({
                    "name": name, "url": url, "host": host_of(url),
                    "ttfb_ms": b.ttfb_ms, "m3u8_ms": b.m3u8_ms,
                    "kbps": b.kbps, "speed_kbps": b.speed_kbps,
                    "ratio": round(b.ratio, 3), "err": b.err or "",
                })
            except Exception as e:  # 单条炸了不能拖垮整批
                out.append({
                    "name": name, "url": url, "host": host_of(url),
                    "ttfb_ms": None, "m3u8_ms": None, "kbps": 0,
                    "speed_kbps": 0, "ratio": 0, "err": f"{type(e).__name__}: {e}",
                })
        return out

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(_run_host, items): h for h, items in by_host.items()}
        for fut in as_completed(futs):
            for rec in fut.result():
                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                done_n += 1
                done[rec["url"]] = rec
                ok = "OK " if rec["ratio"] >= 1.3 else "SLOW"
                print(f"[{done_n:3d}/{len(todo)}] {ok} ratio={rec['ratio']:6.1f}x "
                      f"{rec['name'][:16]:18s} {rec['url'][:62]} {rec['err']}", flush=True)
            fout.flush()
    fout.close()
    print(f"耗时 {time.time() - t0:.0f}s", flush=True)
    return _write_rank(done)


def _write_rank(done: dict[str, dict]) -> int:
    urls: dict[str, dict] = {}
    bad: list[str] = []
    host_acc: dict[str, list[dict]] = defaultdict(list)

    for url, rec in done.items():
        if rec.get("err"):
            # 测出错的（404、超时）不写进排名，让 curate 走主机均分或延迟兜底。
            # 但 ratio 极低的要进 bad，那是真的带宽不够。
            if (rec.get("ratio") or 0) >= 0.5:
                continue
        urls[url] = {"score": round(score_of(rec), 1), "ratio": rec.get("ratio") or 0,
                     "kbps": rec.get("kbps") or 0, "ttfb_ms": rec.get("ttfb_ms")}
        if (rec.get("ratio") or 0) < 0.5:
            bad.append(url)
        h = rec.get("host") or host_of(url)
        if h:
            host_acc[h].append(rec)

    hosts: dict[str, dict] = {}
    for h, recs in host_acc.items():
        good = [r for r in recs if not r.get("err")]
        if not good:
            continue
        hosts[h] = {
            "score": round(sum(score_of(r) for r in good) / len(good), 1),
            "ratio": round(sum(r.get("ratio") or 0 for r in good) / len(good), 2),
            "n": len(good),
        }

    data = {"urls": urls, "hosts": hosts, "bad": bad}
    with open(OUT_RANK, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print(f"\n写入 {OUT_RANK}: {len(urls)} 条 URL / {len(hosts)} 个主机 / {len(bad)} 条带宽不足")
    print("\n主机排名（前 12）：")
    for h, v in sorted(hosts.items(), key=lambda kv: kv[1]["score"])[:12]:
        print(f"  {v['score']:8.0f} ratio{v['ratio']:7.1f}x n={v['n']:<2d} {h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
