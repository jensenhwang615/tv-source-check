#!/usr/bin/env python3
"""批量抓央视官网直播的真实播放地址。

为什么值得单独做一个：

  央视官网 https://tv.cctv.com/live/cctvN/ 是免费公开直播，走的是金山云 / 网宿
  这类大厂 CDN，实测单条能给 30~200Mbps。而公开流传的第三方转播源（海外小 VPS、
  各地 IPTV 模板）上行普遍只有 1.5~2Mbps，却塞 8~10Mbps 的码率，
  电视上就是看两秒缓冲八秒。

  也就是说：**画质和流畅度的问题，换到官方源就一次性解决了。**

  但官方的播放地址是播放器动态取回来的（先请求 p.data.cctv.com 的埋点接口、
  再拿 streamUrl），静态爬 HTML 拿不到，只能开浏览器监听网络请求。

  每个台分到的 CDN 域名还不一样（CCTV-1 在 kcdnvip.com，CCTV-2 在 wscdns.com），
  所以不能按一个模板套全部——必须逐台抓。

用法：
    python scripts/fetch_official.py                 # 抓 1~17 台
    python scripts/fetch_official.py --channels 1,5  # 只抓指定的
    python scripts/fetch_official.py --append        # 顺手写进 sources/official.m3u
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CCTV_CN = {
    1: "综合", 2: "财经", 3: "综艺", 4: "中文国际", 5: "体育", 6: "电影",
    7: "国防军事", 8: "电视剧", 9: "纪录", 10: "科教", 11: "戏曲",
    12: "社会与法", 13: "新闻", 14: "少儿", 15: "音乐", 16: "奥林匹克",
    17: "农业农村",
}

# 埋点/统计域名，不是播放地址
_NOISE = ("p.data.cctv.com", "data.cctv.com", "cctv.com/play.")


def _belongs(url: str, n: int) -> bool:
    """这个地址是不是第 n 台的。

    官网播放页下方有「推荐频道」位，播放器会顺手预加载别的台，
    所以一次嗅探经常抓到隔壁台的地址。CCTV-9 和 CCTV-14 就都抓到过 CCTV-13 的。
    不按频道号过滤的话，清单里会出现「9 号台播的是 13 台」。
    """
    return bool(re.search(rf"cctv{n}([^0-9]|$)", url))


def _usable(url: str) -> bool:
    """能不能进清单。

    排除 AV1 那套路径：`/live/hls_cdrm/enc1/av1/cctvN/...` 确实存在且带宽很高，
    但它是 AV1 编码，绝大多数电视盒子和智能电视只解 H.264，播出来是黑屏或只有声音。
    """
    return "/av1/" not in url and "av1/" not in url.split("?")[0][-12:]


def sniff(page: str, wait: int) -> list[str]:
    """开一次 headless Edge，把这个页面请求过的 m3u8 全捞出来。"""
    try:
        p = subprocess.run(
            [sys.executable, os.path.join(HERE, "sniff_m3u8.py"), page, str(wait)],
            capture_output=True, text=True, timeout=wait + 60,
            cwd=ROOT,
        )
        out = p.stdout
    except subprocess.TimeoutExpired:
        return []
    urls = re.findall(r"https://[^\s\"'\\]+?\.m3u8[^\s\"'\\]*", out)
    keep = []
    for u in urls:
        if any(n in u for n in _NOISE):
            continue
        if u not in keep:
            keep.append(u)
    return keep


def _variants(u: str) -> list[str]:
    """同一个流的不同写法，按「越可能拿到高码率」排序。"""
    out = [u]
    # 官网地址带 b=200-2100（码率区间，单位 kbps）。抬高上限试试能不能拿 1080P
    if "b=200-2100" in u:
        out.append(u.replace("b=200-2100", "b=200-4000"))
        out.append(u.replace("b=200-2100", "b=1000-4000"))
    # index.m3u8 常常对应一个主列表；_720P / _1080P 是分档目录
    base = u.split("?")[0]
    if base.endswith("/index.m3u8"):
        stem = base[: -len("/index.m3u8")]
        q = u[len(base):]
        out.append(f"{stem}_1080P/playlist.m3u8?wsApp=HLS")
        out.append(f"{stem}_720P/playlist.m3u8?wsApp=HLS")
        out.append(f"{stem}_1080P/index.m3u8{q}")
        out.append(f"{stem}_720P/index.m3u8{q}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", default=",".join(str(n) for n in CCTV_CN))
    ap.add_argument("--wait", type=int, default=18, help="每个页面等几秒让播放器起播")
    ap.add_argument("--append", action="store_true", help="写进 sources/official.m3u")
    ap.add_argument("--out", default=os.path.join(ROOT, ".tmp", "official_raw.json"))
    args = ap.parse_args()

    chans = [int(x) for x in args.channels.split(",") if x.strip()]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    result: dict[str, list[str]] = {}
    for n in chans:
        page = f"https://tv.cctv.com/live/cctv{n}/"
        print(f"[i] CCTV-{n} {CCTV_CN.get(n, '')} ...", flush=True)
        urls = sniff(page, args.wait)
        result[str(n)] = urls
        if urls:
            for u in urls[:3]:
                print(f"      {u[:110]}")
        else:
            print("      （没抓到）")
        time.sleep(1.5)

    json.dump(result, open(args.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    got = sum(1 for v in result.values() if v)
    print(f"\n[s] {got}/{len(chans)} 个台抓到地址，原始结果存 {args.out}")

    if args.append:
        sys.path.insert(0, HERE)
        from bench import bench_one  # noqa: E402

        lines = [
            "#EXTM3U",
            "# 央视官网直播源（tv.cctv.com）。地址由 scripts/fetch_official.py 抓取。",
            "# 走金山云 / 网宿 / 腾讯云 / 百度云 / 火山 CDN，带宽比第三方转播源高一个数量级。",
            "# 全部 H.264，不用 av1 那套路径（很多电视盒子解不了 AV1）。",
        ]
        best: dict[int, tuple] = {}
        for n_str, urls in result.items():
            n = int(n_str)
            seeds = [u for u in urls if _belongs(u, n) and _usable(u)]
            if not seeds:
                print(f"   CCTV-{n:<3} 没有抓到属于它自己的地址")
                continue
            cands: list[str] = []
            for u in seeds:
                for v in _variants(u):
                    if _belongs(v, n) and _usable(v) and v not in cands:
                        cands.append(v)
            got = []
            for u in cands[:8]:
                b = bench_one(f"CCTV-{n}", u, 8, 2, 768 * 1024)
                if b.err:
                    continue
                got.append((b.ratio, b.kbps, u))
                tag = "✓" if b.ratio >= 1.3 else "!"
                print(f"   {tag} CCTV-{n:<3} 码率{b.kbps:>5}k 吞吐{b.speed_kbps:>7}k "
                      f"{b.ratio:>7.1f}x  {u[:80]}")
            if not got:
                print(f"   CCTV-{n:<3} 全部失败")
                continue
            # 选择标准：先保证流畅（吞吐 ≥ 码率 2 倍，留足余量），
            # 在这个前提下挑码率最高的——码率才对应画质。
            # 只按 ratio 排会一路选到 200kbps 的糊画面：那个 ratio 最高，但没法看。
            smooth = [x for x in got if x[0] >= 2.0]
            pick = max(smooth, key=lambda x: x[1]) if smooth else max(got, key=lambda x: x[0])
            best[n] = pick
            print(f"   → CCTV-{n} 选 {pick[1]}k {pick[0]:.1f}x")

        for n in sorted(best):
            _, _, u = best[n]
            lines.append(
                f'#EXTINF:-1 tvg-name="CCTV-{n} {CCTV_CN[n]}" group-title="央视",'
                f"CCTV-{n} {CCTV_CN[n]}"
            )
            lines.append(u)
        out = os.path.join(ROOT, "sources", "official.m3u")
        open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        missing = [n for n in CCTV_CN if n not in best]
        print(f"\n[s] 写进 {out}（{len(best)} 个台）")
        if missing:
            print(f"[!] 没拿到: {['CCTV-%d' % n for n in missing]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
