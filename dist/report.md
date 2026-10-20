# 源可用性报告

检测时间: 2026-10-20 20:10 (UTC+8)　耗时 83s

**共 140 条 · 可用 100 (72%) · 失效 38 · 可疑 1 · 被限流 1 · 跳过 0**

## 按分组

| 分组 | 可用 / 总数 | 被限流 | 可用率 |
|---|---|---|---|
| 央视 | 65 / 70 | 0 | 93% |
| 香港 | 10 / 32 | 1 | 32% |
| 广东 | 14 / 27 | 0 | 52% |
| 体育·国际免费 | 6 / 6 | 0 | 100% |
| 体育·足球(第三方) | 4 / 4 | 0 | 100% |
| 体育·国内 | 1 / 1 | 0 | 100% |

## 被限流（不是失效）

以下 1 条来自 `ali.hlspull.yximgs.com`。这些地址此前实测可播，本次是本机 IP 被站点限流/封锁才失败；**已保留在 valid.m3u 里**，换个 IP（家里宽带、手机热点）通常就能看。


## 失效 / 可疑明细

| 频道 | 分组 | 状态 | 原因 | 延迟 |
|---|---|---|---|---|
| CCTV-5+ 体育赛事 | 央视 | DEAD | 超时 >6.0s | -ms |
| CCTV-6 HD (1080p) | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-5+ 体育赛事 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv5phd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u | 267ms |
| CCTV-4K 超高清 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv4k \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u67 | 254ms |
| 广东卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 guangdonghd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f5 | 247ms |
| 广东卫视 (线路2) | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdws \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 268ms |
| 珠江频道 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 zhujianghd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55 | 262ms |
| 广东体育 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 guangdongty \u6ca1\u6709\u914d\u7f6e\u4efb\u4f5 | 1325ms |
| 深圳卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 shenzhenhd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55 | 1064ms |
| 深圳卫视 (线路2) | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 szws \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 267ms |
| 深圳都市 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 szmv \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 263ms |
| 南方卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 nanfang \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u6 | 264ms |
| 大湾区卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 dawanqu \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u6 | 266ms |
| 广东公共 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdgg \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 263ms |
| 广东都市 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdds \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 1346ms |
| 梅州二套 | 广东 | DEAD | HTTP 502 | 892ms |
| 梅州综合 | 广东 | DEAD | HTTP 502 | 822ms |
| HOY TV | 香港 | DEAD | 超时 >6.0s | -ms |
| HOY TV | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| HOY TV (1080p) [Geo-blocked] | 香港 | DEAD | 超时 >6.0s | -ms |
| HOY TV Ⓖ | 香港 | DEAD | 超时 >6.0s | -ms |
| TVB娱乐新闻台 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| TVB无线新闻 | 香港 | DEAD | HTTP 523 | 3556ms |
| TVB无线新闻（备用） | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| TVB星河 | 香港 | DEAD | 超时 >6.0s | -ms |
| TVB星河 | 香港 | DEAD | 超时 >6.0s | -ms |
| TVB星河 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 无线新闻 | 香港 | DEAD | 超时 >6.0s | -ms |
| 无线新闻台 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 无线新闻台 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 澳视卫星 | 香港 | DEAD | 超时 >6.0s | -ms |
| 澳视卫星 | 香港 | DEAD | SSL 握手失败 | -ms |
| 澳视澳门 | 香港 | DEAD | 超时 >6.0s | -ms |
| 澳视澳门 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 澳视澳门 | 香港 | DEAD | SSL 握手失败 | -ms |
| 澳门卫视 | 香港 | DEAD | 连接失败/DNS 解析不了 | -ms |
| 香港卫视 | 香港 | DEAD | HTTP 404 | 918ms |
| 香港卫视 | 香港 | DEAD | 超时 >6.0s | -ms |
| CCTV+ 1 (600p) [Not 24/7] | 央视 | SUSPECT | 变体: 分片 HTTP 404 | 197ms |

## 清单整理

可用 101 条 → 去重合并后写进 `valid.m3u` 的 **72 条**。另有 13 条不进清单（付费频道 / 名字撞关键词的误采内容）。

被剔除的内容：

- `珠江卫视`
- `CCTV怀旧剧场`
- `CCTV文化精品`
- `CCTV第一剧场`
- `CCTV-Billiards (1080p)`
- `CCTV-Culture of Quality SD (1080p)`
- `CCTV-Health (1080p)`
- `CCTV-Nostalgia Theater (1080p)`
- `CCTV-Storm Football (1080p)`
- `CCTV-Storm Music (1080p)`
- `CCTV-Storm Theater (1080p)`
- `CCTV-Weapon & Technology (1080p)`
- `CCTV-Women's Fashion SD (1080p)`

台号规则：每个频道一个固定编号（央视 = 频道号本身，CCTV-5 恒为 5 号台），不随本轮测通情况移动。某个台本轮没测通时台号留空，后面的台不会顶上来。

本轮央视 1-17 全部有可用源。


## 最快的 10 条

| 频道 | 延迟 | 分辨率 |
|---|---|---|
| 广州竞赛 | 10ms | - |
| 河源综合 | 54ms | - |
| CCTV-13 新闻 | 71ms | - |
| CGTN 法语 | 73ms | - |
| 广东民生 | 73ms | - |
| 河源公共 | 83ms | - |
| 深圳卫视 | 92ms | - |
| CCTV-5 体育 | 111ms | - |
| CCTV-8 电视剧 | 113ms | - |
| CCTV-1 综合 | 115ms | - |
