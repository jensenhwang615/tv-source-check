#!/usr/bin/env python3
"""把检测通过的源整理成一份「人能看」的 m3u。

上游清单里同一个台会出现几十种名字（CCTV17 / CCTV-17 农业农村 / CCTV-1 HD (1080p)），
还混着三类不该出现的东西：

  1. 付费频道     —— CCTV-高尔夫网球、CCTV-怀旧剧场、华丽翡翠台（TVB 付费台）
  2. 名字撞关键词 —— 《特种兵之火凤凰》被当成香港凤凰台、"翡翠湾沙滩"被当成翡翠台
  3. 别的地区     —— 台湾 TVBS 混进香港组

这个模块负责：剔除 1/2/3 → 统一命名 → 按「分组 + 台序」排序 → 同台多线路编号。
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# 家庭实测排名（scripts/bench.py --write-rank 生成）
# ---------------------------------------------------------------------------
# 为什么需要这个文件：check.py 量的是「握手延迟」，但电视上卡不卡取决于
# 「这路流的码率，源站给不给得起带宽」。两者经常是反向的 ——
# 山西联通 IPTV 模板握手 100ms（看着比境外 VPS 快 10 倍），可它码率 8Mbps、
# 实际只给得出 1.7Mbps，电视上每看两秒缓冲一次；而境外 VPS 握手 580ms，
# 码率 2Mbps、带宽给足，反而流畅。
#
# 所以选源顺序以这个文件的实测分为准，latency_ms 只在没有实测数据时兜底。
_RANK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sources", "local_rank.json",
)

# 没有实测数据时的默认分。比任何实测过的差源都不如，但比测过带宽不足的好。
_SCORE_UNKNOWN = 5000
# 测过带宽不足（吞吐 < 码率一半）的源：排最后，但不删——
# 万一大面积断流，留着当最后一个能点的选项总比空台强。
_SCORE_STARVED = 9000
# 判死档：永远不选。目前只有央视官网灰屏源用这一档。
_SCORE_DROP = 1e9
# 央视官网源（tv.cctv.com 背后的 CDN）——**整条剔除，不是降级**。
#
# 曾经以为这是最优解：带宽 20~270Mbps，起播 10~200ms，ratio 90 倍以上，
# 把第三方源（ratio 0.1~2）按在地上打。但实测抽帧出来是**全灰**：
#
#   $ ffmpeg -i "<官网 m3u8>" -t 18 -vf "fps=1/3" f%02d.png
#   [h264] top block unavailable for requested intra mode
#   [h264] error while decoding MB 2 0
#   → f01~f06.png 全是 480x270 的纯灰色块，顶部几条噪点
#
# 换 ffmpeg 7.1 重测结果一样，不是解码器版本问题。往下查容器层反而是干净的：
# TS 加扰标志全 0、清单里没有 EXT-X-KEY、PES 起始码正常。也就是说它不是
# 标准 DRM，而是 H.264 码流本身解不出画面 —— 路径里的 `cdrm`（CDRM）大概
# 就是央视自己做的一层载荷处理，只有官网播放器能还原。
#
# 佐证是对照组：同一套 ffmpeg 命令去抽第三方源（124.165 的 CCTV-1），画面正常。
# 录满 60 秒再看仍是灰褐色加顶部噪点，不是「起播缺 IDR 帧」的临时现象。
#
# 所以留着它是有害的：用户点「线路2」会看到一片灰，比卡顿更让人以为坏了。
# 直接不收录。sources/official.m3u 保留作研究留档，但 check 不跑它。
# 实现见 _is_drm_cctv()：命中就返回 _SCORE_DROP，并在主循环里直接跳过。

# 实测带宽严重不足的主机（吞吐只有码率的 0.2 倍，看 2 秒缓冲 8 秒）。
# 这些机器握手特别快（100ms），如果不显式压低，按延迟排序会排到最前面——
# 这正是「换了源反而更卡」的原因。
#   124.165.251.82  山西联通 IPTV 模板公网暴露端口，8~9Mbps 码率 / 1.7Mbps 上行
#   gmxw.7766.org   同类，8~10Mbps 码率 / 1.8Mbps 上行
_STARVED_HOSTS = {"124.165.251.82", "gmxw.7766.org"}

# ---------------------------------------------------------------------------
# 一级源：电视台 / 广电 / 运营商自己运营的地址
# ---------------------------------------------------------------------------
# 选源顺序是「一级源 → 第三方备用」，判断依据是域名归属，不是主观感觉。
# 这些域名背后是持牌机构自己在发流，掉线概率和画质都比第三方转播节点高一个档次：
#   官方频道自己的 CDN   cgtn.com（CGTN）、cctvplus.com（央视国际）
#   地方广电自有服务器   gztv.com（广州台）、hyrtv.cn（河源台）、pybtv.cn（番禺台）、
#                        sun0769.com（东莞台）、cztv.com（浙江广电华数）
#   持牌播出平台         bestv.cn（百视通，五星体育官方播出方）
#   官方 OTT             fengshows.cn（凤凰）、hoy.tv（香港开电视）、rthk.hk（港台）
#
# 注意：这里说的是「谁在发流」，不是「播什么」。浙江广电的 CDN 上转 CCTV-13，
# 仍算一级源——因为运维责任在浙江广电，比某个海外小 VPS 靠谱得多。
_PRIMARY_SUFFIX = (
    ".cgtn.com",
    ".cctvplus.com",
    ".gztv.com",
    ".hyrtv.cn",
    ".pybtv.cn",
    ".sun0769.com",
    ".cztv.com",
    ".bestv.cn",
    ".fengshows.cn",
    ".hoy.tv",
    ".rthk.hk",
    ".gdbtv.com",
    ".gdtv.cn",
)
# 一级源的分数折扣。乘 0.05 的意思是：即使它比某个第三方源慢 20 倍，
# 也仍然排前面；只有慢到 20 倍以上（基本等于废了）才会被第三方顶掉。
_PRIMARY_DISCOUNT = 0.05


def _is_drm_cctv(url: str) -> bool:
    """是不是央视官网直播（tv.cctv.com 那套）—— 解出来是灰屏。

    特征：路径里带 cdrmldcctv（官方转码分档目录）或 /hls_cdrm/。第三方就算
    域名长得像（比如 gcksc.v.kcdnvip.com 也是 kcdnvip），路径里不会有这一段。

    这类源一律不收录，见上面那段注释。
    """
    u = url or ""
    return "cdrmldcctv" in u or "/hls_cdrm/" in u


def _is_primary(url: str) -> bool:
    """是不是「一级源」——电视台 / 广电 / 运营商自己在发流。

    只看域名归属。命中就享受 _PRIMARY_DISCOUNT 的排序折扣，排到第三方前面。
    """
    h = urlparse(url or "").hostname or ""
    if not h:
        return False
    h = h.lower()
    return any(h == s.lstrip(".") or h.endswith(s) for s in _PRIMARY_SUFFIX)


def _score(r) -> float:
    """这条源在家里的体感分，越小越好。

    取值顺序：官网灰屏源（判死）→ 本 URL 实测分 → 同主机均分 → 延迟兜底，
    最后一级源再乘 _PRIMARY_DISCOUNT 做优先。带宽明显不够的直接丢到 9000 档。
    """
    url = (r.url or "").strip()
    if _is_drm_cctv(url):
        return _SCORE_DROP
    if url in _RANK_BAD:
        return _SCORE_STARVED
    if (urlparse(url).hostname or "") in _STARVED_HOSTS:
        return _SCORE_STARVED

    s = _base_score(r, url)
    # 一级源优先：打折后排在第三方前面。
    # 放在最后而不是最前，是因为「优先」不等于「免检」——真测出带宽不够
    # （上面那几条 9000 档）就先保住这个结论，不能因为它是官方的就硬推上去。
    if _is_primary(url):
        s *= _PRIMARY_DISCOUNT
    return s


def _base_score(r, url: str) -> float:
    """不看「是不是官方」，只算这条源本身的体感分。"""
    rec = _RANK_URLS.get(url)
    if rec:
        s = float(rec.get("score") or _SCORE_UNKNOWN)
        # ratio < 1 说明带宽跟不上码率，一定会周期性缓冲，按缺口加罚
        ratio = float(rec.get("ratio") or 0)
        if ratio and ratio < 1.3:
            s += (1.3 - ratio) * 2500
        return s
    # 没单独测过，用主机历史表现估
    h = urlparse(url).hostname or ""
    hrec = _RANK_HOSTS.get(h)
    if hrec:
        s = float(hrec.get("score") or _SCORE_UNKNOWN)
        ratio = float(hrec.get("ratio") or 0)
        if ratio and ratio < 1.3:
            s += (1.3 - ratio) * 2500
        return s
    # 完全没数据：用握手延迟做粗估（毫秒），再加上「码率未知」的保守罚分
    lat = r.latency_ms if getattr(r, "latency_ms", None) else 3000
    return _SCORE_UNKNOWN / 2 + lat


def _load_rank() -> tuple[dict, dict, set]:
    try:
        d = json.load(open(_RANK_PATH, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}, {}, set()
    return d.get("urls") or {}, d.get("hosts") or {}, set(d.get("bad") or [])


_RANK_URLS, _RANK_HOSTS, _RANK_BAD = _load_rank()

# ---------------------------------------------------------------------------
# 分组顺序：数字小的排前面
# ---------------------------------------------------------------------------
GROUP_ORDER = {
    "央视": 10,
    "广东": 20,
    "香港": 30,
    "澳门": 35,
    "体育·国内": 40,
    "体育·国际": 50,
    "体育·足球(第三方)": 60,
}

# 每个分组在播放器里的起始台号。给每个台分配独立台号后，
# 即使播放器忽略文件内的排列顺序、非要按「频道号」重排，出来的也是这个次序。
GROUP_BASE = {
    "央视": 1,
    "广东": 101,
    "香港": 201,
    "澳门": 251,
    "体育·国内": 301,
    "体育·国际": 311,
    "体育·足球(第三方)": 331,
}

# ---------------------------------------------------------------------------
# 不收录：付费频道与误采内容（小写匹配）
# ---------------------------------------------------------------------------
EXCLUDE = {
    # 央视旗下付费数字频道（需要单独订阅，不是免费开路台）
    "billiards": "央视付费·台球",
    "golf": "央视付费·高尔夫网球",
    "nostalgia": "央视付费·怀旧剧场",
    "storm football": "央视付费·风云足球",
    "storm music": "央视付费·风云音乐",
    "storm theater": "央视付费·风云剧场",
    "first theater": "央视付费·第一剧场",
    "weapon": "央视付费·兵器科技",
    "women's fashion": "央视付费·女性时尚",
    "world geography": "央视付费·世界地理",
    "health": "央视付费·卫生健康",
    "culture of quality": "央视付费·文化精品",
    "cctv怀旧剧场": "央视付费",
    "cctv文化精品": "央视付费",
    "cctv第一剧场": "央视付费",
    "cctv风云": "央视付费",
    "cctv台球": "央视付费",
    "cctv高尔夫": "央视付费",
    # TVB / 其他付费台
    "华丽翡翠": "TVB 付费频道",
    "golden jade": "TVB 付费频道（华丽翡翠台英文名）",
    "无线明珠": "付费",
    # 名字撞关键词的误采
    "特种兵": "电视剧，不是频道",
    "翡翠湾": "风景摄像头",
    "沙滩": "风景摄像头",
    # 非香港内容
    "tvbs": "台湾 TVBS，不是香港 TVB",
    "tvb8": "海外付费",
    # 央视对外频道（英文名 CCTV+，内容是面向海外的中国报道，不是国内 CCTV 频道）
    "cctv+": "央视对外频道 CCTV+，不是国内 CCTV",
}

# ---------------------------------------------------------------------------
# 央视：1-17 是免费开路台
# ---------------------------------------------------------------------------
CCTV_CN = {
    1: "综合", 2: "财经", 3: "综艺", 4: "中文国际", 5: "体育", 6: "电影",
    7: "国防军事", 8: "电视剧", 9: "纪录", 10: "科教", 11: "戏曲",
    12: "社会与法", 13: "新闻", 14: "少儿", 15: "音乐", 16: "奥林匹克",
    17: "农业农村",
}

CGTN_CN = {"": "英语", "英语": "英语", "纪录": "纪录", "西语": "西语",
           "法语": "法语", "阿语": "阿语", "俄语": "俄语"}

# ---------------------------------------------------------------------------
# 地方台别名：规范名 -> (分组, 序号, [别名])
# 序号决定组内先后，随便留空档方便以后插台
# ---------------------------------------------------------------------------
LOCAL = [
    # ---- 广东 ----
    ("广东卫视",    "广东", 10, ["广东卫视", "guangdong satellite", "gdws", "广东卫视高清"]),
    ("珠江频道",    "广东", 20, ["珠江频道", "广东珠江", "珠江台", "zhujiang"]),
    ("广东体育",    "广东", 30, ["广东体育", "gdtv体育", "guangdong sports"]),
    ("大湾区卫视",  "广东", 40, ["大湾区卫视", "广东大湾区", "大湾区"]),
    ("南方卫视",    "广东", 50, ["南方卫视", "南方台"]),
    ("广东公共",    "广东", 60, ["广东公共", "广东公共频道"]),
    ("广东影视",    "广东", 70, ["广东影视"]),
    ("广东都市",    "广东", 80, ["广东都市", "广东都市频道"]),
    ("广东民生",    "广东", 90, ["广东民生", "广东新闻"]),
    ("深圳卫视",    "广东", 100, ["深圳卫视"]),
    ("深圳都市",    "广东", 110, ["深圳都市", "深圳都市频道"]),
    ("深圳娱乐",    "广东", 115, ["深圳娱乐"]),
    ("广州综合",    "广东", 120, ["广州综合", "广州电视台综合"]),
    ("广州新闻",    "广东", 130, ["广州新闻"]),
    ("广州竞赛",    "广东", 140, ["广州竞赛"]),
    ("南国都市",    "广东", 150, ["南国都市"]),
    ("东莞新闻综合", "广东", 160, ["东莞新闻综合", "东莞综合", "东莞新闻"]),
    ("佛山综合",    "广东", 170, ["佛山综合", "佛山电视台"]),
    ("佛山公共",    "广东", 175, ["佛山公共"]),
    ("南海频道",    "广东", 180, ["南海"]),
    ("顺德频道",    "广东", 185, ["顺德"]),
    ("珠海综合",    "广东", 190, ["珠海综合", "珠海一台"]),
    ("中山综合",    "广东", 200, ["中山综合"]),
    ("惠州综合",    "广东", 210, ["惠州综合", "惠州一台"]),
    ("江门综合",    "广东", 220, ["江门综合"]),
    ("肇庆综合",    "广东", 230, ["肇庆综合"]),
    ("汕头综合",    "广东", 240, ["汕头综合"]),
    ("湛江综合",    "广东", 250, ["湛江综合"]),
    ("茂名综合",    "广东", 260, ["茂名综合"]),
    ("梅州综合",    "广东", 270, ["梅州综合", "梅州梅江"]),
    ("河源综合",    "广东", 280, ["河源综合"]),
    ("河源公共",    "广东", 290, ["河源公共"]),
    ("番禺综合",    "广东", 300, ["番禺综合", "番禺"]),

    # ---- 香港 ----
    ("翡翠台",        "香港", 10, ["翡翠台", "tvb翡翠", "jade", "无线翡翠"]),
    ("明珠台",        "香港", 20, ["明珠台", "pearl"]),
    ("TVB Plus",      "香港", 30, ["tvb plus", "tvbplus"]),
    ("无线新闻台",    "香港", 40, ["无线新闻", "tvb新闻", "无线新闻台"]),
    ("TVB娱乐新闻台", "香港", 50, ["tvb娱乐新闻", "娱乐新闻台"]),
    ("TVB星河",       "香港", 60, ["tvb星河", "星河频道"]),
    ("ViuTV",         "香港", 70, ["viutv", "viu tv", "viu"]),
    ("ViuTVsix",      "香港", 75, ["viutvsix", "viu six"]),
    ("HOY TV",        "香港", 80, ["hoy tv", "hoytv", "香港开电视"]),
    ("HOY 资讯台",    "香港", 85, ["hoy 资讯", "hoy资讯"]),
    ("RTHK 31",       "香港", 90, ["rthk31", "rthk 31", "港台31"]),
    ("RTHK 32",       "香港", 95, ["rthk32", "rthk 32", "港台32"]),
    ("RTHK 33",       "香港", 100, ["rthk33", "rthk 33", "港台33"]),
    ("RTHK 34",       "香港", 105, ["rthk34", "rthk 34", "港台34"]),
    ("RTHK 35",       "香港", 110, ["rthk35", "rthk 35", "港台35"]),
    ("凤凰卫视中文台", "香港", 120, ["凤凰卫视中文", "凤凰中文", "凤凰卫视台"]),
    ("凤凰卫视资讯台", "香港", 130, ["凤凰卫视资讯", "凤凰资讯"]),
    ("凤凰卫视香港台", "香港", 140, ["凤凰卫视香港", "凤凰香港"]),
    ("香港卫视",      "香港", 150, ["香港卫视", "hkstv"]),
    ("有线新闻台",    "香港", 160, ["有线新闻", "icable新闻"]),

    # ---- 澳门 ----
    ("澳视澳门",  "澳门", 10, ["澳视澳门", "澳门澳视"]),
    ("澳视卫星",  "澳门", 20, ["澳视卫星"]),
    ("澳门卫视",  "澳门", 30, ["澳门卫视"]),
    ("澳门资讯",  "澳门", 40, ["澳门资讯"]),

    # ---- 体育（国内）----
    ("五星体育",  "体育·国内", 10, ["五星体育", "smg五星"]),
    ("劲爆体育",  "体育·国内", 20, ["劲爆体育", "sitv劲爆"]),

    # ---- 体育（国际免费）----
    ("beIN SPORTS XTRA", "体育·国际", 10, ["bein sports xtra", "bein xtra"]),
    ("FIFA+",           "体育·国际", 20, ["fifa+", "fifa plus"]),
    ("NBC Sports NOW",  "体育·国际", 30, ["nbc sports now"]),
    ("DD Sports",       "体育·国际", 40, ["dd sports"]),
    ("Sportitalia",     "体育·国际", 50, ["sportitalia"]),
    ("TyC Sports",      "体育·国际", 60, ["tyc sports"]),
    ("Eurosport",       "体育·国际", 70, ["eurosport"]),
    ("DAZN",            "体育·国际", 80, ["dazn"]),

    # ---- 体育（第三方足球转播）----
    ("ESPN 拉美",    "体育·足球(第三方)", 10, ["espn lat", "espn deports", "espn 拉美", "espn deportes"]),
]

# 别名索引（长别名优先，避免 "凤凰卫视台" 被 "凤凰卫视" 抢先匹配）
_ALIAS_INDEX: list[tuple[str, str, int, str]] = []
for canon, group, order, aliases in LOCAL:
    for a in aliases:
        _ALIAS_INDEX.append((canon, group, order, a.lower()))
_ALIAS_INDEX.sort(key=lambda x: -len(x[3]))

# ---------------------------------------------------------------------------
# 台号：每个频道一个「固定」编号，与本次收录到几条无关
# ---------------------------------------------------------------------------
# 关键点：绝不能用「计数器 +1」分配台号。那样一旦中间某个台（比如 CCTV-4）
# 这次没测通，后面的台号会整体前移，于是 CCTV-6 顶上 4 号位，播放器里看到
# 的就是「3 号台是 CCTV-3，4 号台却是 CCTV-6」——错位比留空难看得多。
# 固定编号的含义是：CCTV-5 永远是 5 号台，没源就空着；广东卫视永远是 101。
CCTV_CHNO: dict[str, int] = {f"CCTV-{n} {cn}": n for n, cn in CCTV_CN.items()}
CCTV_CHNO["CCTV-5+ 体育赛事"] = 18
CCTV_CHNO["CCTV-4K 超高清"] = 19
CCTV_CHNO["CCTV-8K 超高清"] = 20
for _i, _cn in enumerate(["英语", "纪录", "西语", "法语", "阿语", "俄语"]):
    CCTV_CHNO[f"CGTN {_cn}"] = 21 + _i


def _build_chno_map() -> dict[tuple[str, str], int]:
    """(分组, 规范名) → 固定台号。在模块加载时算一次，此后不再变化。"""
    m: dict[tuple[str, str], int] = {}
    for canon, n in CCTV_CHNO.items():
        m[("央视", canon)] = n
    # 地方台：按 LOCAL 表里出现的先后，在各自分组的基准号上顺排。
    # 位置只取决于 LOCAL 的书写顺序，不取决于这次测通了哪些台。
    counter: dict[str, int] = {}
    for canon, group, _order, _aliases in LOCAL:
        if (group, canon) in m:
            continue
        k = counter.get(group, 0)
        m[(group, canon)] = GROUP_BASE.get(group, 900) + k
        counter[group] = k + 1
    return m


CHNO_MAP = _build_chno_map()


def _clean(name: str) -> str:
    """去掉画质后缀与常见修饰，只留下频道名本体。"""
    s = name.strip()
    # 全角括号转半角，方便统一处理
    s = s.replace("（", "(").replace("）", ")")
    # 去掉 (720p) (1080p) (576i) HD SD 4K 之类
    s = re.sub(r"\((?:1080|720|576|480)[pi]?\)", "", s, flags=re.I)
    s = re.sub(r"\[(?:not\s*24/7|geo-blocked|offline)\]", "", s, flags=re.I)
    s = re.sub(r"\b(?:hd|sd|fhd|uhd)\b", "", s, flags=re.I)
    # 线路标记交给后面的编号逻辑，先剥掉
    s = re.sub(r"\((?:线路|备用|line)\s*\d*\)", "", s)
    s = re.sub(r"\s+", " ", s).strip(" -_·")
    return s


def _match_cctv(s: str) -> tuple[str, int] | None:
    """央视系列。返回 (规范名, 排序键) 或 None。"""
    up = s.upper().replace(" ", "")

    # CGTN 优先（避免被 CCTV 规则吃掉）
    m = re.match(r"^CGTN(.*)$", up)
    if m:
        tail = m.group(1).strip("-·_ ")
        cn = CGTN_CN.get(tail, CGTN_CN.get(tail[:2], None))
        if cn is None:
            return None
        order = 300 + (list(CGTN_CN.values()).index(cn) * 5)
        return f"CGTN {cn}", order

    # CCTV+ 海外版（与 CCTV-1 不是同一个台，单独排）
    m = re.match(r"^CCTV\+[-]?(\d)", up)
    if m:
        return f"CCTV+ {m.group(1)}", 280 + int(m.group(1))

    # CCTV-4K / 8K
    m = re.match(r"^CCTV[-]?(4K|8K)", up)
    if m:
        k = m.group(1)
        return f"CCTV-{k} 超高清", 270 if k == "4K" else 275

    # CCTV-5+
    if re.match(r"^CCTV[-]?5\+", up) or re.match(r"^CCTV5PLUS", up):
        return "CCTV-5+ 体育赛事", 250

    # CCTV-N
    # 注意：不能用 \b —— 中文也算 \w，`CCTV-1综合` 里 1 和「综」之间没有词边界，
    # 用 \b 会把所有已经规范命名过的台全部判成不匹配。用否定前瞻排除多位数即可。
    m = re.match(r"^CCTV[-]?(\d{1,2})(?!\d)", up)
    if m:
        n = int(m.group(1))
        if n not in CCTV_CN:
            return None          # 18 以上不是台号，多是"CCTV5+高清"之类没洗净，丢弃
        return f"CCTV-{n} {CCTV_CN[n]}", n * 10

    return None


def classify(name: str) -> tuple[str, str, int] | None:
    """原始频道名 → (分组, 规范名, 组内排序键)。返回 None 表示不收录。"""
    if not name:
        return None
    low = name.lower()

    # 1) 黑名单
    for k in EXCLUDE:
        if k in low:
            return None

    # 2) 央视 / CGTN
    hit = _match_cctv(_clean(name))
    if hit:
        cname, order = hit
        return "央视", cname, order

    # 3) 地方台（别名表，长别名优先）
    s = _clean(name).lower().replace(" ", "")
    for canon, group, order, alias in _ALIAS_INDEX:
        if alias.replace(" ", "") in s:
            return group, canon, order

    return None


# ---------------------------------------------------------------------------
# 排序与编号
# ---------------------------------------------------------------------------
# 个别频道允许多留几条线路。
# 央视 1-17 是刚需且最容易断，留 2 条；一旦全断，对应台号就会空出来。
KEEP_OVERRIDE = {"翡翠台": 3, "广东卫视": 2, "深圳卫视": 2}
for _n in CCTV_CN:
    KEEP_OVERRIDE[f"CCTV-{_n} {CCTV_CN[_n]}"] = 2


def _diverse(items: list, n: int) -> list:
    """同组内最多挑 n 条：第一条挑体感最好的，其余优先换主机做备份。

    以前这里是「按延迟排序 + 强制不同主机」，有两个问题：
      1. 延迟低 ≠ 好看，选出过 8Mbps/1.7Mbps 的源当主线路，电视上一直缓冲
      2. 强制不同主机导致线路2 常常差得多，其实用户几乎不会用到线路2
    现在改成：主线路只看实测分；线路2 起才考虑主机多样性，但差值太大就不换。
    """
    items = sorted(items, key=_score)
    if not items:
        return []
    first = items[0]
    chosen = [first]
    best = _score(first)
    used_host = {urlparse(first.url).hostname or ""}
    for it in items[1:]:
        if len(chosen) >= n:
            break
        h = urlparse(it.url).hostname or ""
        s = _score(it)
        # 换主机做备份是有价值的（同一台服务器挂了两条一起死），
        # 但代价不能超过 2.5 倍——否则所谓的备份比主线路差一个数量级，等于没有。
        if h in used_host and s > best * 1.2:
            continue
        if h not in used_host and s > best * 2.5:
            continue
        chosen.append(it)
        used_host.add(h)
    # 还是不够 n 条，就把剩下的按分补齐——但只补「分数还过得去」的。
    # 无条件补齐的后果很具体：某台只有 1 条官方源（分数 10），为了凑够 2 条，
    # 会把实测 0.2x 的 IPTV 模板塞成「线路2」。用户点到线路2 就是卡死，
    # 而线路1 本来好好的。宁缺毋滥：官方源在的时候，一条就够。
    for it in items:
        if len(chosen) >= n:
            break
        if it in chosen:
            continue
        if _score(it) > max(best * 3, 200):
            continue
        chosen.append(it)
    return chosen


def _pick_diverse(items: list, n: int) -> list:
    """先挑实测通过的线路；只有凑不够时，才补一条 BLOCKED 当后备。

    BLOCKED 是「403 / 本机 IP 被限流」这类换网络才能播的源。它们的响应时间往往
    比真能播的源还短，如果只按延迟排序，会被优先挑进清单 —— 电视上第一条线路
    点开就是黑屏。所以 OK 必须无条件排前面。
    """
    ok = [x for x in items if x.status == "OK"]
    other = [x for x in items if x.status != "OK"]
    chosen = _diverse(ok, n)
    if len(chosen) < n and other:
        chosen += _diverse(other, n - len(chosen))
    return chosen


def _extra_lines(raw: list[str]) -> list[str]:
    """保留 #EXTVLCOPT / #KODIPROP 这类指令行，丢掉旧的 #EXTINF（我们会重写）。"""
    return [ln for ln in raw if not ln.lstrip().startswith("#EXTINF")]


@dataclass
class Entry:
    """一条整理好的播放列表条目。"""
    group: str
    name: str            # 带线路号的显示名，如「翡翠台 (线路2)」
    canon: str           # 不带线路号的规范名，用来判断是不是同一个台
    order: int = 0       # 组内台序（决定排列先后）
    chno: int = 0        # 播放器台号
    url: str = ""
    extra: list[str] = field(default_factory=list)   # #EXTVLCOPT 之类的附加指令


def curate(results: list, keep_per_name: int = 2) -> tuple[list[Entry], dict]:
    """整理成有序清单。

    返回 (entries, stats)
      entries: 已排序、已编号、已分配台号
      stats:   统计信息（收录/剔除/去重数量），写进报告用
    """
    seen_url: set[str] = set()
    buckets: dict[tuple[str, str, int], list] = {}
    dropped: dict[str, int] = {}

    for r in results:
        if r.status not in ("OK", "BLOCKED"):
            continue
        url = (r.url or "").strip()
        if not url or url in seen_url:
            continue
        if _is_drm_cctv(url):
            # 央视官网源，拉下来是灰屏，收了反而害人
            seen_url.add(url)
            dropped["[灰屏] 央视官网源"] = dropped.get("[灰屏] 央视官网源", 0) + 1
            continue
        seen_url.add(url)

        got = classify(r.name)
        if got is None:
            name = r.name.strip()
            dropped[name] = dropped.get(name, 0) + 1
            continue
        group, canon, order = got
        buckets.setdefault((group, canon, order), []).append(r)

    entries: list[Entry] = []
    for (group, canon, order), items in buckets.items():
        n = KEEP_OVERRIDE.get(canon, keep_per_name)
        picks = _pick_diverse(items, n)
        for i, r in enumerate(picks, 1):
            label = canon if i == 1 else f"{canon} (线路{i})"
            entries.append(
                Entry(group=group, name=label, canon=canon, order=order, url=r.url,
                      extra=_extra_lines(r.raw or []))
            )

    # 排序：分组权重 → 组内台序 → 线路上限内的原始顺序
    # 注意不能只按名字排：字符串比较会把 "CCTV-10" 排在 "CCTV-2" 前面（空格 < '0'）。
    entries.sort(key=lambda e: (GROUP_ORDER.get(e.group, 999), e.order, e.name))

    # 分配台号：查固定表。同一个台的多条线路共用一个台号，
    # 也不会因为某个台这次没测通而让后面的台号整体挪位。
    for e in entries:
        e.chno = CHNO_MAP.get((e.group, e.canon), 999)

    # 央视 1-17 里这一轮没测通的台，列出来让用户知道是「缺台」而不是「乱序」
    got_cctv = {e.canon for e in entries if e.group == "央视"}
    missing = [c for c in (f"CCTV-{n} {cn}" for n, cn in CCTV_CN.items())
               if c not in got_cctv]

    stats = {
        "kept": len(entries),
        "kept_urls": {e.url for e in entries},
        "kept_names": {e.url: e.canon for e in entries},   # url → 规范名，报告里显示用
        "dropped_names": dropped,
        "dropped_total": sum(dropped.values()),
        "missing_cctv": missing,
    }
    return entries, stats


def build_m3u(entries: list[Entry], header: list[str] | None = None) -> str:
    lines = ["#EXTM3U"]
    if header:
        lines.extend(header)
    last_group = None
    for e in entries:
        if last_group is not None and e.group != last_group:
            lines.append("")
        last_group = e.group
        lines.append(
            f'#EXTINF:-1 tvg-chno="{e.chno}" tvg-name="{e.name}" group-title="{e.group}",{e.name}'
        )
        lines.extend(e.extra)
        lines.append(e.url)
    return "\n".join(lines) + "\n"
