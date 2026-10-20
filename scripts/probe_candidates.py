#!/usr/bin/env python3
"""从公开上游里捞指定频道的所有候选源，逐条实测，挑出能用的。

为什么需要它：`check.py` 只测已经写进清单的源，而某个台（典型是 CCTV-4、CCTV-5）
一旦只剩一条可用源，那条源挂了就等于整个台消失。这个脚本用来「补给」——
把上游里所有同名候选都拉下来实测，通过的追加进 streams.m3u。

用法：
    # 只看不写
    python scripts/probe_candidates.py --match "CCTV-4,CCTV-5"

    # 把通过的追加进主清单
    python scripts/probe_candidates.py --match "CCTV-1,CCTV-2" --append --group 央视
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check import Channel, parse_m3u, probe, session  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
COLLECT = ROOT / "sources" / "collect.json"
STREAMS = ROOT / "sources" / "streams.m3u"


def load_upstreams() -> list[str]:
    cfg = json.loads(COLLECT.read_text(encoding="utf-8"))
    return cfg.get("upstreams", [])


def grab(url: str, timeout: float) -> list[Channel]:
    try:
        r = session().get(url, timeout=timeout, allow_redirects=True)
        if r.status_code != 200:
            print(f"  [!] {url} → HTTP {r.status_code}", file=sys.stderr)
            return []
        return parse_m3u(r.text)
    except Exception as e:  # noqa: BLE001
        print(f"  [!] {url} → {type(e).__name__}", file=sys.stderr)
        return []


def keep(ch: Channel, pats: list[re.Pattern], args) -> bool:
    name = (ch.name or "").strip()
    if not ch.url.lower().startswith(("http://", "https://")):
        return False
    if not args.allow_ipv6 and "//[" in ch.url:
        return False
    return any(p.search(name) for p in pats)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--match", required=True, help="频道名匹配，逗号分隔；按正则处理")
    ap.add_argument("--timeout", type=float, default=8.0)
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--append", action="store_true", help="把通过的追加进 streams.m3u")
    ap.add_argument("--group", default="央视", help="追加时的 group-title")
    ap.add_argument("--max-per-chno", type=int, default=4, help="每个频道最多追加几条")
    ap.add_argument("--allow-ipv6", action="store_true")
    args = ap.parse_args()

    pats = [re.compile(p.strip(), re.I) for p in args.match.split(",") if p.strip()]
    print(f"[i] 抓取上游清单…")
    cands: list[Channel] = []
    for u in load_upstreams():
        got = grab(u, max(args.timeout * 3, 20))
        hit = [c for c in got if keep(c, pats, args)]
        print(f"    {len(got):5} 条 → 命中 {len(hit):3}  {u.split('/')[-1]}")
        cands.extend(hit)

    # 去重：同一 URL 只测一次
    uniq: dict[str, Channel] = {}
    for c in cands:
        uniq.setdefault(c.url, c)
    print(f"[i] 去重后 {len(uniq)} 条候选，开始并发实测…\n")

    def work(item: tuple[str, Channel]):
        url, ch = item
        status, latency, res, detail = probe(url, args.timeout)
        return ch, status, latency, res, detail

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        rows = list(ex.map(work, uniq.items()))

    ok = [r for r in rows if r[1] == "OK"]
    ok.sort(key=lambda r: (r[0].name, r[2] or 99999))

    print(f"{'状态':8} {'延迟':>7}  {'频道':32} 主机")
    print("-" * 92)
    for ch, status, latency, res, detail in sorted(rows, key=lambda r: (r[1] != "OK", r[0].name)):
        host = urlparse(ch.url).hostname or "-"
        lat = f"{latency}ms" if latency is not None else "-"
        print(f"{status:8} {lat:>7}  {ch.name[:32]:32} {host}")

    print(f"\n[✓] 可用 {len(ok)}/{len(rows)}")

    if args.append and ok:
        text = STREAMS.read_text(encoding="utf-8")
        have = set(re.findall(r"^(https?://\S+)$", text, re.M))
        per: dict[str, int] = {}
        added = 0
        blocks: list[str] = []
        for ch, _st, _lat, _res, _detail in ok:
            if ch.url in have:
                continue
            key = ch.name
            if per.get(key, 0) >= args.max_per_chno:
                continue
            per[key] = per.get(key, 0) + 1
            blocks.append(f'#EXTINF:-1 tvg-name="{ch.name}" group-title="{args.group}",{ch.name}\n{ch.url}')
            added += 1
        if blocks:
            if not text.endswith("\n"):
                text += "\n"
            text += "\n" + "\n".join(blocks) + "\n"
            STREAMS.write_text(text, encoding="utf-8")
        print(f"[✓] 追加 {added} 条到 {STREAMS.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
