#!/usr/bin/env python3
"""从 iptv-org 的总清单里抽出 CCTV / CGTN 系列，写 sources/cctv_iptvorg.m3u。

为什么要单独一个文件：以前央视组的源是从 5 个清单里混着捡的，同一个 CCTV-1
能有七八个来路的地址（auto.m3u 一家就贡献几十条），谁排前面取决于当时谁的
握手快，结果同一个台今天用 A 的源、明天用 B 的源，稳定性没法谈。

现在规矩很简单：**央视组只认这一个文件**。check.py 里其它清单的 CCTV 条目
（不管它叫 CCTV-1 还是 CCTV-1 HD）全部跳过，不参与央视组选源。

上游 iptv-org 的两个事实要说清楚：
  1. 它有 CCTV-5+（php.jdshipin.com），但**没有 CCTV-5**——
     频道条目 CCTV5.cn 在库里存在，可流地址是 0 条（被人报死了）。
     所以 CCTV-5 只能靠 sources/cctv_extra.m3u 手工补，本脚本会把它拼进来。
  2. 它给的 CCTV-1~17 绝大多数指向同一台 74.91.26.218（晚高峰会劣化）。
     这是上游的选择，不是本脚本能改的。

用法：
    python scripts/fetch_cctv.py                 # 拉上游 + 拼接手工补充
    python scripts/fetch_cctv.py --offline FILE  # 用本地 m3u 文件代替上游（调试用）
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from check import UA, parse_m3u          # noqa: E402
from curate import classify              # noqa: E402

UPSTREAM = "https://iptv-org.github.io/iptv/index.m3u"
OUT = ROOT / "sources" / "cctv_iptvorg.m3u"
EXTRA = ROOT / "sources" / "cctv_extra.m3u"

HEADER = [
    "# 央视 / CGTN 系列｜由 scripts/fetch_cctv.py 自动生成，不要手改",
    "#",
    "# 上游：https://iptv-org.github.io/iptv/index.m3u（每 6 小时随检测重新拉一次）",
    "# 补充：sources/cctv_extra.m3u（手工维护：iptv-org 漏收或收错的那几个台）",
    "#",
    "# 这个文件是「央视组唯一允许的输入」：其它清单里的 CCTV 条目一律不进央视组，",
    "# 免得同一个台被七八个来路的地址重复喂进来。",
    "#",
    "# 序号规则见 scripts/curate.py 的 CCTV_ORDER：CCTV-5 → CCTV-5+ → CCTV-6 → …",
]


def fetch_upstream(timeout: float = 60.0) -> list:
    s = requests.Session()
    # 和 check.py 同一条规矩：测源 / 拉清单必须直连，不能被环境代理接管，
    # 否则拿到的是代理伪造的响应（IDE 沙箱里尤其明显）。
    s.trust_env = False
    s.headers.update({"User-Agent": UA})
    r = s.get(UPSTREAM, timeout=timeout)
    r.raise_for_status()
    return parse_m3u(r.text)


def pick_cctv(channels: list) -> list:
    """只留央视 / CGTN，并且按 URL 去重。"""
    out, seen = [], set()
    for c in channels:
        got = classify(c.name)
        if not got or got[0] != "央视":
            continue          # 付费频道、CCTV+ 海外版、撞关键词的片子都在这里被挡掉
        u = (c.url or "").strip()
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(c)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="从 iptv-org 抽取央视源")
    ap.add_argument("--offline", default="", help="用本地 m3u 文件代替上游（调试用）")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    if args.offline:
        chans = parse_m3u(Path(args.offline).read_text(encoding="utf-8-sig"))
        print(f"[i] 离线模式：读 {args.offline}，共 {len(chans)} 条")
    else:
        chans = fetch_upstream()
        print(f"[i] 上游 index.m3u 共 {len(chans)} 条")

    picked = pick_cctv(chans)
    print(f"[i] 其中央视 / CGTN {len(picked)} 条")

    extra: list = []
    if EXTRA.exists():
        extra = parse_m3u(EXTRA.read_text(encoding="utf-8-sig"))
        print(f"[i] 手工补充 {len(extra)} 条（{EXTRA.name}）")

    lines = ["#EXTM3U"] + HEADER
    for c in picked + extra:
        raw = list(c.raw or [f'#EXTINF:-1,{c.name}'])
        # iptv-org 的 group-title 是它自己的分类（News / Movies / Sports…），
        # 直接透传会让检测报告里冒出十几个「分组」，看着像清单坏了。
        # 统一改成「央视」，反正这一份文件的每一条都是央视组。
        raw[0] = re.sub(r'group-title="[^"]*"', 'group-title="央视"', raw[0])
        if 'group-title=' not in raw[0]:
            raw[0] = raw[0].replace("#EXTINF:-1", '#EXTINF:-1 group-title="央视"', 1)
        lines.extend(raw)
        lines.append(c.url)

    # newline="\n"：Windows 上 write_text 默认会把 \n 换成 \r\n，
    # 和其它 sources/*.m3u 的换行不一致，git diff 会整份文件标成改动。
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    names = sorted({classify(c.name)[1] for c in picked + extra if classify(c.name)})
    print(f"[✓] 写入 {args.out}：{len(picked) + len(extra)} 条 / {len(names)} 个台")
    print("    台：" + "、".join(n.split(" ")[0] for n in names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
