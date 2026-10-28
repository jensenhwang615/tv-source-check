# 源可用性报告

检测时间: 2026-10-28 20:27 (UTC+8)　耗时 104s

**共 333 条 · 可用 147 (47%) · 失效 153 · 可疑 9 · 被限流 22 · 跳过 2**

## 按分组

| 分组 | 可用 / 总数 | 被限流 | 可用率 |
|---|---|---|---|
| 香港 | 53 / 121 | 10 | 48% |
| 广东 | 21 / 92 | 5 | 24% |
| 央视 | 42 / 75 | 0 | 56% |
| 体育 | 21 / 33 | 5 | 75% |
| 体育·国际免费 | 6 / 6 | 0 | 100% |
| 体育·足球(第三方) | 4 / 4 | 0 | 100% |
| 体育·国内 | 0 / 1 | 1 | — |
| Sports | 0 / 1 | 1 | — |

## 被限流（不是失效）

以下 22 条来自 `ali.hlspull.yximgs.com`, `bantel-cdn1.iptvperu.tv`, `bp-livetytv.bestv.cn`, `di-g7ij0rwh.vo.lswcdn.net`, `di-yx2saj20.vo.lswcdn.net`, `distribution.sportitalialive.it`, `gcksc.v.kcdnvip.com`, `hoytv-live-stream.hoy.tv`, `livepull-tcms.sztv.com.cn`, `pili-live-rtmp.tvliving.gdmztv.com`, `rthktv32-live.akamaized.net`, `rthktv33-live.akamaized.net`, `rthktv34-live.akamaized.net`, `rthktv35-live.akamaized.net`, `zdf-hls-19.akamaized.net`。这些地址此前实测可播，本次是本机 IP 被站点限流/封锁才失败；**已保留在 valid.m3u 里**，换个 IP（家里宽带、手机热点）通常就能看。


## 失效 / 可疑明细

| 频道 | 分组 | 状态 | 原因 | 延迟 |
|---|---|---|---|---|
| 河源公共 | 广东 | DEAD | 超时 >8.0s | -ms |
| 河源综合 | 广东 | DEAD | 超时 >8.0s | -ms |
| 珠江卫视 | 广东 | DEAD | 超时 >8.0s | -ms |
| 番禺综合 | 广东 | DEAD | 超时 >8.0s | -ms |
| 广东卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 guangdonghd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f5 | 45ms |
| 广东卫视 (线路2) | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdws \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 23ms |
| 珠江频道 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 zhujianghd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55 | 23ms |
| 广东体育 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 guangdongty \u6ca1\u6709\u914d\u7f6e\u4efb\u4f5 | 23ms |
| 深圳卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 shenzhenhd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55 | 23ms |
| 深圳卫视 (线路2) | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 szws \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 24ms |
| 深圳都市 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 szmv \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 23ms |
| 南方卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 nanfang \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u6 | 23ms |
| 大湾区卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 dawanqu \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u6 | 23ms |
| 广东公共 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdgg \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 23ms |
| 广东影视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdys \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 23ms |
| 广东都市 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdds \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 24ms |
| 翡翠台 (线路2) | 香港 | DEAD | 超时 >8.0s | -ms |
| 明珠台 (线路2) | 香港 | DEAD | 超时 >8.0s | -ms |
| CCTV-世界地理 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-兵器科技 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-卫生健康 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-央视台球 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-央视高网 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-女性时尚 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-怀旧剧场 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-文化精品 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-电视指南 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-第一剧场 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-风云剧场 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-风云足球 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-风云音乐 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV中学生 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV发现之旅 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV老故事 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CGTN Documentary English Ⓢ | 央视 | DEAD | 变体: 连接失败/DNS 解析不了 | 364ms |
| CGTN Español | 央视 | DEAD | 变体: 连接失败/DNS 解析不了 | 40ms |
| CGTN Français | 央视 | DEAD | 变体: 连接失败/DNS 解析不了 | 40ms |
| CGTN Pусский | 央视 | DEAD | 变体: 连接失败/DNS 解析不了 | 41ms |
| 东莞生活资讯 | 广东 | DEAD | HTTP 404 | 7037ms |
| 云浮公共 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 云浮综合 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 南方卫视 | 广东 | DEAD | 超时 >8.0s | -ms |
| 嘉佳卡通 | 广东 | DEAD | 超时 >8.0s | -ms |
| 大湾区卫视 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 大湾区卫视 | 广东 | DEAD | 超时 >8.0s | -ms |
| 广东-广州塔与海心桥视角 | 广东 | DEAD | 超时 >8.0s | -ms |
| 广东-车八岭国家级自然保护区 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东公共 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东卫视 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东卫视 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东卫视 | 广东 | DEAD | HTTP 404 | 1449ms |
| 广东卫视4K | 广东 | DEAD | HTTP 404 | 1230ms |
| 广东少儿 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东影视 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东文化 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东新闻 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东民生 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东经济科教 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广州影视 | 广东 | DEAD | 超时 >8.0s | -ms |
| 广州法治 | 广东 | DEAD | 超时 >8.0s | -ms |
| 河源公共 | 广东 | DEAD | 超时 >8.0s | -ms |
| 河源综合 | 广东 | DEAD | 超时 >8.0s | -ms |
| 深圳东部 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 深圳众创TV | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 深圳卫视 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 深圳卫视 | 广东 | DEAD | HTTP 404 | 1231ms |
| 深圳卫视 | 广东 | DEAD | HTTP 500 | 1563ms |
| 深圳龙岗 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 清新公共 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 清新综合 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 珠江卫视 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 珠江卫视 | 广东 | DEAD | 超时 >8.0s | -ms |
| 珠海生活 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 番禺综合 | 广东 | DEAD | 超时 >8.0s | -ms |
| 阳江公共 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 阳江公共 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 阳江公共 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 阳江公共 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 阳江综合 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 阳江综合 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 阳江综合 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 阳江综合 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 魅力广东 | 广东 | DEAD | 超时 >8.0s | -ms |
| BSTV (Hong Kong) (576p) | 香港 | DEAD | 超时 >8.0s | -ms |
| Canal Macau | 香港 | DEAD | 超时 >8.0s | -ms |
| HOY资讯台 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| Phoenix Chinese Channel (720p) | 香港 | DEAD | 超时 >8.0s | -ms |
| Phoenix InfoNews Channel (720p) | 香港 | DEAD | 超时 >8.0s | -ms |
| TDM Entertainment | 香港 | DEAD | 超时 >8.0s | -ms |
| TDM Information | 香港 | DEAD | 超时 >8.0s | -ms |
| TDM Ou Mun | 香港 | DEAD | 超时 >8.0s | -ms |
| TDM Sport | 香港 | DEAD | 超时 >8.0s | -ms |
| TVB Finance (Sports & Information Channel) | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| TVB J1 | 香港 | DEAD | HTTP 409 | 509ms |
| TVB News Channel | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| TVB Plus | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| TVB Plus | 香港 | DEAD | 变体: 超时 >8.0s | 500ms |
| TVBS欢乐台 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| TVB无线新闻 | 香港 | DEAD | HTTP 523 | 1295ms |
| TVB无线新闻（备用） | 香港 | DEAD | 超时 >8.0s | -ms |
| TVB无线星河 | 香港 | DEAD | 超时 >8.0s | -ms |
| TVB明珠台 | 香港 | DEAD | 响应体为空 | 3296ms |
| TVB星河 | 香港 | DEAD | HTTP 404 | 3860ms |
| TVB生活台 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| TVB翡翠台 | 香港 | DEAD | HTTP 404 | 1714ms |
| TVB翡翠台 | 香港 | DEAD | HTTP 523 | 2925ms |
| TVB翡翠台（备用） | 香港 | DEAD | 超时 >8.0s | -ms |
| VIUTV1 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| Viu6 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| iHOY 爱历史 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 凤凰中文台 | 香港 | DEAD | HTTP 404 | 1230ms |
| 凤凰中文高清 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 凤凰卫视 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 凤凰电影 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 凤凰资讯 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 凤凰资讯台 | 香港 | DEAD | HTTP 404 | 1669ms |
| 凤凰资讯高清 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 凤凰香港 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 凤凰香港台 | 香港 | DEAD | HTTP 404 | 1230ms |
| 华丽翡翠台 | 香港 | DEAD | HTTP 523 | 2926ms |
| 华丽翡翠台 | 香港 | DEAD | HTTP 404 | 2553ms |
| 房山无线频道 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 房山有线频道 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 无线新闻台 | 香港 | DEAD | 超时 >8.0s | -ms |
| 明珠台 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 明珠台 | 香港 | DEAD | 超时 >8.0s | -ms |
| 有线新闻 | 香港 | DEAD | 超时 >8.0s | -ms |
| 港台电视31 | 香港 | DEAD | HTTP 404 | 1087ms |
| 港台电视32 | 香港 | DEAD | HTTP 404 | 1104ms |
| 澳视卫星 | 香港 | DEAD | SSL 握手失败 | -ms |
| 澳视澳门 | 香港 | DEAD | SSL 握手失败 | -ms |
| 石景山有线 | 香港 | DEAD | 超时 >8.0s | -ms |
| 翡翠台 backup | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 香港卫视 | 香港 | DEAD | HTTP 404 | 1230ms |
| 香港卫视 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| FIFA+ | 体育 | DEAD | HTTP 404 | 1459ms |
| WOWOWライブ | 体育 | DEAD | InvalidURL | -ms |
| 五星体育 | 体育 | DEAD | SSL 握手失败 | -ms |
| 五星体育 | 体育 | DEAD | HTTP 404 | 2080ms |
| 五星体育 | 体育 | DEAD | 返回提示文字而非视频流: 此时段不提供电视网络转播服务 | 646ms |
| 劲爆体育 | 体育 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 劲爆体育 | 体育 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-1 HD (1080p) | 央视 | DEAD | 返回提示文字而非视频流: the content is not available in your area | 58ms |
| CCTV-4 America (1080p) | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-4K HD (1080p) | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv4khd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u | 101ms |
| CCTV-5+ (1080p) | 央视 | DEAD | 变体: HTTP 403 | 488ms |
| CCTV-6 [Geo-blocked] | 央视 | DEAD | HTTP 500 | 5044ms |
| CCTV-13 HD (1080p) | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-16 HD (1080p) | 央视 | DEAD | 返回提示文字而非视频流: the content is not available in your area | 24ms |
| CGTN Russian (1080p) | 央视 | DEAD | 超时 >8.0s | -ms |
| CGTN Spanish (1080p) | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-5 体育 | 央视 | DEAD | 返回提示文字而非视频流: the content is not available in your area | 23ms |
| CCTV-5 体育 | 央视 | DEAD | 返回提示文字而非视频流: the content is not available in your area | 23ms |
| CCTV+ 1 (600p) [Not 24/7] | 央视 | SUSPECT | 变体: 分片 HTTP 404 | 681ms |
| CCTV+ 2 (600p) [Not 24/7] | 央视 | SUSPECT | 变体: 分片 HTTP 404 | 278ms |
| 广东体育 | 广东 | SUSPECT | 返回网页而非视频流 | 743ms |
| 广东珠江 | 广东 | SUSPECT | 返回网页而非视频流 | 53ms |
| 深圳卫视4K | 广东 | SUSPECT | 返回网页而非视频流 | 2435ms |
| HOY78 | 香港 | SUSPECT | 返回网页而非视频流 | 255ms |
| 澳门体育 | 香港 | SUSPECT | 返回网页而非视频流 | 143ms |
| 澳门综艺 | 香港 | SUSPECT | 返回网页而非视频流 | 45ms |
| 翡翠台4K | 香港 | SUSPECT | 返回网页而非视频流 | 80ms |

## 清单整理

可用 169 条 → 去重合并后写进 `valid.m3u` 的 **84 条**。另有 34 条不进清单（付费频道 / 名字撞关键词的误采内容）。

被剔除的内容：

- `CCTV-Billiards (1080p)`
- `CCTV-Culture of Quality SD (1080p)`
- `CCTV-Golf & Tennis (1080p)`
- `CCTV-Health (1080p)`
- `CCTV-Nostalgia Theater (1080p)`
- `CCTV-Storm Football (1080p)`
- `CCTV-Storm Music (1080p)`
- `CCTV-Storm Theater (1080p)`
- `CCTV-The First Theater (1080p)`
- `CCTV-Weapon & Technology (1080p)`
- `CCTV-Women's Fashion SD (1080p)`
- `CCTV-World Geography SD (1080p)`
- `CCTV怀旧剧场`
- `CCTV文化精品`
- `CCTV第一剧场`
- `CGTN记录`
- `Guangzhou TV`
- `Shenzhen Satellite TV (2160p)`
- `广东-汕头市小公园`
- `梅州二套`
- `Golden Jade (1080p)`
- `HOY Infotainment (1080p) [Geo-blocked]`
- `Hong Kong International Business Channel (1080p) [Geo-blocked]`
- `Phoenix Ⓖ`
- `RTHK TV 31 (1080p) [Geo-blocked]`
- `RTHK TV 32 (1080p) [Geo-blocked]`
- `RTHK TV 33 (1080p) [Geo-blocked]`
- `RTHK TV 34 (1080p) [Geo-blocked]`
- `RTHK TV 35 (1080p) [Geo-blocked]`
- `Right Now TV (720p)`
- `TVBS新闻台`
- `华丽翡翠台`
- `特种兵之火凤凰`
- `福建漳州醉美沙滩翡翠湾`

台号规则：每个频道一个固定编号，不随本轮测通情况移动。某个台本轮没测通时台号留空，后面的台不会顶上来。央视组按显示顺序连续编号（CCTV-5 是 5、CCTV-5+ 是 6、CCTV-6 是 7），这样不管播放器按文件顺序还是按 tvg-chno 排，次序都一样。

本轮央视 1-17 中未测通、台号留空的有 **1 个**：CCTV-16

另有 2 个台按用户要求「不管通不通都要在清单里」，但本轮一条都没测通，名字后面标了「（本期未测通）」：CCTV-5+ 体育赛事、CCTV-5 体育


## 最快的 10 条

| 频道 | 延迟 | 分辨率 |
|---|---|---|
| TyC Sports | 23ms | 1920x1080 |
| beIN SPORTS XTRA | 40ms | 1920x1080 |
| DD Sports | 45ms | 1920x1080 |
| NBC Sports NOW | 46ms | 1920x1080 |
| CCTV-9 纪录 | 62ms | 1920x1080 |
| CCTV-11 戏曲 | 66ms | - |
| FIFA+ | 70ms | 1280x720 |
| CCTV-6 电影 | 70ms | - |
| CCTV-14 少儿 | 71ms | - |
| CCTV-3 综艺 | 74ms | - |
