# 源可用性报告

检测时间: 2026-10-20 17:35 (UTC+8)　耗时 299s

**共 602 条 · 可用 227 (39%) · 失效 286 · 可疑 42 · 被限流 18 · 跳过 29**

## 按分组

| 分组 | 可用 / 总数 | 被限流 | 可用率 |
|---|---|---|---|
| 央视 | 116 / 344 | 1 | 34% |
| 香港 | 55 / 121 | 10 | 50% |
| 广东 | 24 / 93 | 5 | 27% |
| 体育 | 20 / 32 | 2 | 67% |
| 体育·国际免费 | 6 / 6 | 0 | 100% |
| 体育·足球(第三方) | 4 / 4 | 0 | 100% |
| 体育·国内 | 1 / 1 | 0 | 100% |
| Sports | 1 / 1 | 0 | 100% |

## 被限流（不是失效）

以下 18 条来自 `8.138.7.223`, `ali.hlspull.yximgs.com`, `distribution.sportitalialive.it`, `gcksc.v.kcdnvip.com`, `hoytv-live-stream.hoy.tv`, `ldcctvwbcdbd.a.bdydns.com`, `livepull-tcms.sztv.com.cn`, `pili-live-rtmp.tvliving.gdmztv.com`, `rthktv32-live.akamaized.net`, `rthktv33-live.akamaized.net`, `rthktv34-live.akamaized.net`, `rthktv35-live.akamaized.net`, `zdf-hls-19.akamaized.net`。这些地址此前实测可播，本次是本机 IP 被站点限流/封锁才失败；**已保留在 valid.m3u 里**，换个 IP（家里宽带、手机热点）通常就能看。


## 失效 / 可疑明细

| 频道 | 分组 | 状态 | 原因 | 延迟 |
|---|---|---|---|---|
| CCTV-6 电影 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-9 纪录 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-14 少儿 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-1 综合 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv1 \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670 | 65ms |
| CCTV-5 体育 | 央视 | DEAD | 返回提示文字而非视频流: the content is not available in your area | 34ms |
| CCTV-13 新闻 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv132m \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u | 35ms |
| CCTV-15 音乐 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv15 \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u67 | 34ms |
| CCTV-5+ 体育赛事 | 央视 | DEAD | 超时 >8.0s | -ms |
| 珠江卫视 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 番禺综合 | 广东 | DEAD | 超时 >8.0s | -ms |
| CCTV-6 HD (1080p) | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-5 体育 | 央视 | DEAD | 返回提示文字而非视频流: the content is not available in your area | 34ms |
| CCTV-5+ 体育赛事 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv5phd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u | 34ms |
| CCTV-4K 超高清 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv4k \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u67 | 35ms |
| 广东卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 guangdonghd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f5 | 34ms |
| 广东卫视 (线路2) | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdws \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 34ms |
| 珠江频道 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 zhujianghd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55 | 34ms |
| 广东体育 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 guangdongty \u6ca1\u6709\u914d\u7f6e\u4efb\u4f5 | 34ms |
| 深圳卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 shenzhenhd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55 | 34ms |
| 深圳卫视 (线路2) | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 szws \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 34ms |
| 深圳都市 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 szmv \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 35ms |
| 南方卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 nanfang \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u6 | 36ms |
| 大湾区卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 dawanqu \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u6 | 34ms |
| 广东公共 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdgg \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 35ms |
| 广东影视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdys \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 34ms |
| 广东都市 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdds \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 34ms |
| 翡翠台 (线路2) | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 明珠台 (线路2) | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-1 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-1 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-1 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-1 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-1 HD (1080p) | 央视 | DEAD | 返回提示文字而非视频流: the content is not available in your area | 33ms |
| CCTV-10 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-10 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-10 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-10科教 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-11 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-11 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-11戏曲 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-12 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-12 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-12 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-12社会与法 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-13 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-13 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-13新闻 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-14 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-14 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-14 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-14少儿 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-15 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-15 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-15 (1080p) | 央视 | DEAD | HTTP 404 | 811ms |
| CCTV-15音乐 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-16 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-16 HD (1080p) | 央视 | DEAD | 返回提示文字而非视频流: the content is not available in your area | 34ms |
| CCTV-16奥林匹克 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-16奥林匹克 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-16奥林匹克 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-17农业农村 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-17农业农村 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-17农业农村 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-1综合 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-2 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-2 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-2 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-2 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-2财经 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-3 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-3 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-3 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-3 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-3综艺 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-4 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-4 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-4 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-4 中文国际（美） Ⓢ | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-4K | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-4K HD (1080p) | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv4khd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u | 137ms |
| CCTV-4中文国际 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-5 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-5 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-5 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-5 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-5+ | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-5+ | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-5+ | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-5+ | 央视 | DEAD | HTTP 500 | 1913ms |
| CCTV-5+体育赛事 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-5体育 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-6 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-6 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-6 HD (1080p) | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-6 [Geo-blocked] | 央视 | DEAD | HTTP 500 | 1714ms |
| CCTV-6电影 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-7 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-7 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-7 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-7 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-7国防军事 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-8 | 央视 | DEAD | SSL 握手失败 | -ms |
| CCTV-8 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-8电视剧 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-9 | 央视 | DEAD | HTTP 404 | 1490ms |
| CCTV-9 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-9 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-9纪录 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
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
| CCTV1 | 央视 | DEAD | HTTP 404 | 3388ms |
| CCTV1 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV1 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV10 | 央视 | DEAD | HTTP 404 | 1330ms |
| CCTV10 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV10 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV11 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV11 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV11 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV12 | 央视 | DEAD | HTTP 404 | 2593ms |
| CCTV12 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV12 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV13 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV13 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV13 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV14 | 央视 | DEAD | HTTP 404 | 1330ms |
| CCTV14 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV14 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV15 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV15 | 央视 | DEAD | HTTP 404 | 1230ms |
| CCTV15 | 央视 | DEAD | HTTP 500 | 1611ms |
| CCTV16 | 央视 | DEAD | HTTP 404 | 1330ms |
| CCTV16 | 央视 | DEAD | HTTP 404 | 1231ms |
| CCTV17 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV17 | 央视 | DEAD | HTTP 404 | 1230ms |
| CCTV2 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV2 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV2 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV3 | 央视 | DEAD | HTTP 404 | 1330ms |
| CCTV3 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV3 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV4 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV4 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV4 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV4K | 央视 | DEAD | HTTP 404 | 1229ms |
| CCTV4K真4K | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV5 | 央视 | DEAD | HTTP 404 | 1330ms |
| CCTV5 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV5 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV5+ | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV5+ | 央视 | DEAD | HTTP 500 | 1615ms |
| CCTV6 | 央视 | DEAD | HTTP 404 | 1330ms |
| CCTV6 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV6 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV7 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV7 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV7 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV8 | 央视 | DEAD | HTTP 404 | 1330ms |
| CCTV8 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV8 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV9 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV9 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV9 | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CGTN | 央视 | DEAD | HTTP 500 | 1619ms |
| CGTN | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CGTN | 央视 | DEAD | 超时 >8.0s | -ms |
| CGTN Documentary English Ⓢ | 央视 | DEAD | 变体: 连接失败/DNS 解析不了 | 444ms |
| CGTN Español | 央视 | DEAD | 变体: 连接失败/DNS 解析不了 | 31ms |
| CGTN Français | 央视 | DEAD | 变体: 连接失败/DNS 解析不了 | 31ms |
| CGTN Pусский | 央视 | DEAD | 变体: 连接失败/DNS 解析不了 | 30ms |
| CGTN العربية | 央视 | DEAD | 超时 >8.0s | -ms |
| CGTN俄语 | 央视 | DEAD | 超时 >8.0s | -ms |
| CGTN俄语 | 央视 | DEAD | 变体: 超时 >8.0s | 50ms |
| CGTN法语 | 央视 | DEAD | 变体: 超时 >8.0s | 58ms |
| CGTN纪录 | 央视 | DEAD | 超时 >8.0s | -ms |
| 东莞生活资讯 | 广东 | DEAD | HTTP 404 | 6667ms |
| 云浮公共 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 云浮综合 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 南方卫视 | 广东 | DEAD | 超时 >8.0s | -ms |
| 嘉佳卡通 | 广东 | DEAD | 超时 >8.0s | -ms |
| 大湾区卫视 | 广东 | DEAD | 超时 >8.0s | -ms |
| 广东-广州塔与海心桥视角 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东-车八岭国家级自然保护区 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东公共 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东卫视 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东卫视 | 广东 | DEAD | HTTP 404 | 1330ms |
| 广东卫视4K | 广东 | DEAD | HTTP 404 | 1330ms |
| 广东少儿 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 广东影视 | 广东 | DEAD | 连接失败/DNS 解析不了 | -ms |
| ... | | | 其余 128 条见 status.json | |

## 清单整理

可用 245 条 → 去重合并后写进 `valid.m3u` 的 **90 条**。另有 35 条不进清单（付费频道 / 名字撞关键词的误采内容）。

被剔除的内容：

- `华丽翡翠台`
- `CCTV怀旧剧场`
- `CCTV文化精品`
- `CCTV第一剧场`
- `CCTV+ 1 (600p) [Not 24/7]`
- `CCTV-Billiards (1080p)`
- `CCTV-Culture of Quality SD (1080p)`
- `CCTV-Health (1080p)`
- `CCTV-Nostalgia Theater (1080p)`
- `CCTV-Storm Football (1080p)`
- `CCTV-Storm Music (1080p)`
- `CCTV-Storm Theater (1080p)`
- `CCTV-Weapon & Technology (1080p)`
- `CCTV-Women's Fashion SD (1080p)`
- `CCTV-Golf & Tennis (1080p)`
- `CCTV-The First Theater (1080p)`
- `CCTV-World Geography SD (1080p)`
- `Guangzhou TV`
- `Golden Jade (1080p)`
- `RTHK TV 31 (1080p) [Geo-blocked]`
- `Right Now TV (720p)`
- `TVBS新闻台`
- `特种兵之火凤凰`
- `福建漳州醉美沙滩翡翠湾`
- `Shenzhen Satellite TV (2160p)`
- `广东-汕头市小公园`
- `梅州二套`
- `HOY Infotainment (1080p) [Geo-blocked]`
- `Hong Kong International Business Channel (1080p) [Geo-blocked]`
- `Phoenix Ⓖ`
- `RTHK TV 32 (1080p) [Geo-blocked]`
- `RTHK TV 33 (1080p) [Geo-blocked]`
- `RTHK TV 34 (1080p) [Geo-blocked]`
- `RTHK TV 35 (1080p) [Geo-blocked]`

台号规则：每个频道一个固定编号（央视 = 频道号本身，CCTV-5 恒为 5 号台），不随本轮测通情况移动。某个台本轮没测通时台号留空，后面的台不会顶上来。

本轮央视 1-17 全部有可用源。


## 最快的 10 条

| 频道 | 延迟 | 分辨率 |
|---|---|---|
| CCTV-9 纪录 | 3ms | 1920x1080 |
| DD Sports | 14ms | 1920x1080 |
| NBC Sports NOW | 20ms | 1920x1080 |
| TyC Sports | 23ms | 1920x1080 |
| 无线新闻台 | 25ms | - |
| TVB娱乐新闻台 | 43ms | - |
| CGTN 阿语 | 48ms | - |
| CGTN 英语 | 54ms | - |
| CGTN 纪录 | 56ms | - |
| beIN SPORTS XTRA | 59ms | 1920x1080 |
