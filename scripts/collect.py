#!/usr/bin/env python3
"""从公开上游清单里采集「央视 + 广东」两类源，去重后写入 sources/auto.m3u。

它只负责「挑」，不负责「测」——能不能播交给 check.py。
上游只取公开的 FTA（免费开路）电视频道索引，不含点播。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import requests

from check import Channel, parse_attrs, parse_m3u

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def norm_group(name: str, group: str, rules: list[dict]) -> str | None:
    haystack = f"{name} {group}".lower()
    for rule in rules:
        for kw in rule["include"]:
            if kw.lower() in haystack:
                return rule["name"]
    return None


def clean_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name).strip()
    return name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="sources/collect.json")
    ap.add_argument("--out", default="sources/auto.m3u")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    rules = cfg["groups"]
    max_per_name = int(cfg.get("max_per_name", 3))

    seen_urls: set[str] = set()
    per_name: dict[str, int] = {}
    picked: list[Channel] = []
    stats: list[tuple[str, int, int]] = []

    for url in cfg["upstreams"]:
        short = url.split("/")[3] if url.count("/") > 3 else url
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": UA})
            if r.status_code >= 400:
                print(f"[!] {short} HTTP {r.status_code}, 跳过")
                continue
            r.encoding = r.encoding or "utf-8"
            chans = parse_m3u(r.text)
        except Exception as e:  # noqa: BLE001
            print(f"[!] {short} 拉取失败 {type(e).__name__}, 跳过")
            continue

        kept = 0
        for ch in chans:
            if not ch.url:
                continue
            group = norm_group(ch.name, ch.group, rules)
            if not group:
                continue
            key = ch.url.strip()
            if key in seen_urls:
                continue
            name_key = clean_name(ch.name).lower()
            if per_name.get(name_key, 0) >= max_per_name:
                continue
            seen_urls.add(key)
            per_name[name_key] = per_name.get(name_key, 0) + 1
            attrs = parse_attrs(ch.raw[0]) if ch.raw else {}
            picked.append(
                Channel(
                    name=clean_name(ch.name),
                    url=ch.url,
                    group=group,
                    raw=[
                        '#EXTINF:-1 tvg-id="{}" tvg-name="{}" tvg-logo="{}" group-title="{}",{}'.format(
                            attrs.get("tvg-id", "").replace('"', ""),
                            clean_name(ch.name).replace('"', ""),
                            attrs.get("tvg-logo", ""),
                            group,
                            clean_name(ch.name),
                        )
                    ],
                )
            )
            kept += 1
        stats.append((short, len(chans), kept))

    order = {r["name"]: i for i, r in enumerate(rules)}
    picked.sort(key=lambda c: (order.get(c.group, 99), c.name))

    lines = ["#EXTM3U"]
    for c in picked:
        lines.extend(c.raw)
        lines.append(c.url)
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n上游贡献：")
    for short, total, kept in stats:
        print(f"  {short:20s} 读到 {total:5d} 条 → 命中 {kept:4d} 条")
    per_group: dict[str, int] = {}
    for c in picked:
        per_group[c.group] = per_group.get(c.group, 0) + 1
    print(f"\n[✓] 去重后共 {len(picked)} 条 " + " ".join(f"{k}={v}" for k, v in per_group.items()))
    print(f"    已写入 {args.out}（下一步用 check.py 实测）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
