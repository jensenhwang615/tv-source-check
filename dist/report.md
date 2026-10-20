# 源可用性报告

检测时间: 2026-10-20 17:42 (UTC+8)　耗时 55s

**共 131 条 · 可用 109 (84%) · 失效 20 · 可疑 0 · 被限流 2 · 跳过 0**

## 按分组

| 分组 | 可用 / 总数 | 被限流 | 可用率 |
|---|---|---|---|
| 央视 | 78 / 88 | 2 | 91% |
| 广东 | 11 / 23 | 0 | 48% |
| 香港 | 9 / 9 | 0 | 100% |
| 体育·国际免费 | 6 / 6 | 0 | 100% |
| 体育·足球(第三方) | 4 / 4 | 0 | 100% |
| 体育·国内 | 1 / 1 | 0 | 100% |
| Sports | 1 / 1 | 0 | 100% |

## 被限流（不是失效）

以下 18 条来自 `8.138.7.223`, `ali.hlspull.yximgs.com`, `distribution.sportitalialive.it`, `gcksc.v.kcdnvip.com`, `hoytv-live-stream.hoy.tv`, `ldcctvwbcdbd.a.bdydns.com`, `livepull-tcms.sztv.com.cn`, `pili-live-rtmp.tvliving.gdmztv.com`, `rthktv32-live.akamaized.net`, `rthktv33-live.akamaized.net`, `rthktv34-live.akamaized.net`, `rthktv35-live.akamaized.net`, `zdf-hls-19.akamaized.net`。这些地址此前实测可播，本次是本机 IP 被站点限流/封锁才失败；**已保留在 valid.m3u 里**，换个 IP（家里宽带、手机热点）通常就能看。


## 被限流（不是失效）

以下 2 条来自 `74.91.26.218`。这些地址此前实测可播，本次是本机 IP 被站点限流/封锁才失败；**已保留在 valid.m3u 里**，换个 IP（家里宽带、手机热点）通常就能看。


## 失效 / 可疑明细

| 频道 | 分组 | 状态 | 原因 | 延迟 |
|---|---|---|---|---|
| CCTV-1 综合 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv1 \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670 | 499ms |
| CCTV-13 新闻 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv132m \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u | 236ms |
| CCTV-15 音乐 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv15 \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u67 | 232ms |
| CCTV-16 奥林匹克 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv16 \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u67 | 255ms |
| CCTV8 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-6 HD (1080p) | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-5+ 体育赛事 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv5phd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u | 235ms |
| CCTV-4K 超高清 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv4k \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u67 | 257ms |
| 广东卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 guangdonghd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f5 | 216ms |
| 广东卫视 (线路2) | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdws \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 253ms |
| 珠江频道 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 zhujianghd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55 | 249ms |
| 广东体育 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 guangdongty \u6ca1\u6709\u914d\u7f6e\u4efb\u4f5 | 251ms |
| 深圳卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 shenzhenhd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55 | 247ms |
| 深圳卫视 (线路2) | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 szws \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 1245ms |
| 深圳都市 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 szmv \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 233ms |
| 南方卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 nanfang \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u6 | 252ms |
| 大湾区卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 dawanqu \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u6 | 250ms |
| 广东公共 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdgg \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 241ms |
| 广东影视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdys \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 256ms |
| 广东都市 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdds \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 234ms |

## 清单整理

可用 111 条 → 去重合并后写进 `valid.m3u` 的 **71 条**。另有 14 条不进清单（付费频道 / 名字撞关键词的误采内容）。

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
| 深圳卫视 | 28ms | - |
| 广东民生 | 32ms | - |
| CCTV-13 新闻 | 35ms | 1280x720 |
| CCTV-5 体育 | 35ms | - |
| 广州新闻 | 48ms | - |
| CCTV-15 音乐 | 51ms | - |
| 河源综合 | 61ms | - |
| CCTV-9 纪录 | 89ms | 1280x720 |
| CCTV-11 戏曲 | 94ms | - |
| 东莞新闻综合 | 94ms | - |
