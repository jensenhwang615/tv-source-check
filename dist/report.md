# 源可用性报告

检测时间: 2026-10-20 17:24 (UTC+8)　耗时 37s

**共 131 条 · 可用 110 (84%) · 失效 20 · 可疑 1 · 被限流 0 · 跳过 0**

## 按分组

| 分组 | 可用 / 总数 | 被限流 | 可用率 |
|---|---|---|---|
| 央视 | 79 / 88 | 0 | 90% |
| 广东 | 11 / 23 | 0 | 48% |
| 香港 | 9 / 9 | 0 | 100% |
| 体育·国际免费 | 6 / 6 | 0 | 100% |
| 体育·足球(第三方) | 4 / 4 | 0 | 100% |
| 体育·国内 | 1 / 1 | 0 | 100% |

## 失效 / 可疑明细

| 频道 | 分组 | 状态 | 原因 | 延迟 |
|---|---|---|---|---|
| CCTV-1 综合 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv1 \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670 | 533ms |
| CCTV-13 新闻 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv132m \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u | 853ms |
| CCTV-15 音乐 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv15 \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u67 | 286ms |
| CCTV-16 奥林匹克 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv16 \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u67 | 234ms |
| CCTV-5+ 体育赛事 | 央视 | DEAD | 超时 >8.0s | -ms |
| CCTV-6 HD (1080p) | 央视 | DEAD | 连接失败/DNS 解析不了 | -ms |
| CCTV-5+ 体育赛事 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv5phd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u | 255ms |
| CCTV-4K 超高清 | 央视 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 cctv4k \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u67 | 264ms |
| 广东卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 guangdonghd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f5 | 273ms |
| 广东卫视 (线路2) | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdws \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 263ms |
| 珠江频道 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 zhujianghd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55 | 263ms |
| 广东体育 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 guangdongty \u6ca1\u6709\u914d\u7f6e\u4efb\u4f5 | 269ms |
| 深圳卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 shenzhenhd \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55 | 273ms |
| 深圳卫视 (线路2) | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 szws \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 232ms |
| 深圳都市 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 szmv \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 807ms |
| 南方卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 nanfang \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u6 | 256ms |
| 大湾区卫视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 dawanqu \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u6 | 266ms |
| 广东公共 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdgg \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 272ms |
| 广东影视 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdys \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 247ms |
| 广东都市 | 广东 | DEAD | 返回提示文字而非视频流: {"error":"\u9891\u9053 gdds \u6ca1\u6709\u914d\u7f6e\u4efb\u4f55\u670d | 274ms |
| CCTV+ 1 (600p) [Not 24/7] | 央视 | SUSPECT | 变体: 分片 HTTP 404 | 299ms |

## 清单整理

可用 110 条 → 去重合并后写进 `valid.m3u` 的 **54 条**。另有 13 条不进清单（付费频道 / 名字撞关键词的误采内容）。

被剔除的内容：

- `珠江卫视`
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

台号规则：每个频道一个固定编号（央视 = 频道号本身，CCTV-5 恒为 5 号台），不随本轮测通情况移动。某个台本轮没测通时台号留空，后面的台不会顶上来。

本轮央视 1-17 全部有可用源。


## 最快的 10 条

| 频道 | 延迟 | 分辨率 |
|---|---|---|
| 广东民生 | 28ms | - |
| 深圳卫视 | 37ms | - |
| CCTV-4 中文国际 | 53ms | - |
| CCTV-3 综艺 | 59ms | 854x480 |
| 河源公共 | 59ms | - |
| CCTV-8 电视剧 | 69ms | 854x480 |
| 广州新闻 | 71ms | - |
| 河源综合 | 72ms | - |
| CCTV-5 体育 | 77ms | 1920x1080 |
| CGTN 英语 | 81ms | - |
