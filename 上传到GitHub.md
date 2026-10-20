# 上传到 GitHub（零基础版 · 公开仓库）

本地已经做好了：`git init` + 三次提交都已完成，分支为 `main`，**16 个文件**已入库，`.git` 只有 219KB。
你只需要「把本地仓库推到 GitHub」这一件事。

---

## 第 0 步：你已经选了 Public，先认清这意味着什么

公开是你自己的决定，我按公开来配好了。三件事要心里有数：

| | 事实 |
|---|---|
| ✅ 好处 | raw 链接能直接当订阅地址；Actions 分钟数无限（私有仓库只有 2000 分钟/月） |
| ⚠️ 代价 | 全世界都能看到 `sources/` 里的地址；真被投诉时，处理方式是**禁用整个仓库** |
| 🎯 真实概率 | 公开的直播 m3u 仓库在 GitHub 上有几十上百个（`suxuang`、`YueChan`、`fanmingming/live` 都活了几年）。针对这类仓库的 DMCA 很少，真正被批量投诉的是**影视点播聚合接口**和**TVBox 的 spider JAR** |

所以公开可以，但要守一条线：

> **这个仓库永远只放直播 m3u。不要往里加影视点播的 `api.php/provide/vod` 接口，不要放 spider JAR。**
> 那两样东西是 GitHub 版权投诉的主要目标，一旦命中，封的是整个仓库、连带你的 3D 公司项目。

为此我已经做了三件事：
1. README 顶部加了「有什么 / 没有什么」对照表和免责声明（明确不托管、不转码、不担保）
2. 把 `dist/status.json`（229KB）、`dist/dead.m3u`、`sources/auto.m3u` 移出了仓库——这三样每 6 小时重生成一次，提交上去只会让 git 历史每月涨几十 MB
3. 加了 `.gitattributes` 统一换行符，避免 Windows 的 CRLF 推到 Linux 机器上出问题

---

## 方法一：网页拖拽上传（不装任何软件，约 5 分钟）

### 1. 建一个空仓库
1. 打开 https://github.com ，登录（没账号就注册）
2. 右上角 **`+`** → **New repository**
3. **Repository name** 填 `tv-source-check`
4. 选 **Public**
5. **下面三个勾全都不要勾**（Add a README / Add .gitignore / Choose a license）
   —— 勾了会在远程先产生文件，后面 `git push` 会冲突
6. 点 **Create repository**

### 2. 上传文件
1. 新建出来的页面上有一条链接 **`uploading an existing file`**，点它
2. 在资源管理器打开 `C:\Users\Jensen\WorkBuddy\2026-10-20-09-16-06\tv-source-check`
3. **先打开「查看」→ 勾上「隐藏的项目」**，否则你看不到 `.github` 和 `.gitignore`
4. 把这 **9 个** 拖进浏览器（拖内容，**不要拖整个 `tv-source-check` 文件夹**）：

```
.github          （隐藏，必须有——工作流就在里面）
.gitignore       （隐藏）
.gitattributes   （隐藏）
README.md
requirements.txt
上传到GitHub.md
dist
scripts
sources
```

5. 等列表全部出现（**16 个文件**：`dist` 里 3 个、`sources` 里 5 个、`scripts` 里 2 个、根目录 4 个、`.github` 里 1 个）
6. 页面底部点 **Commit changes**

### 3. 确认工作流在里面（关键）
点进 **`.github/workflows/check.yml`** 能不能看到内容。
如果 `.github` 没传上去（有些浏览器拖拽会漏隐藏文件夹），用下面的备选办法。

### 4. 开跑
1. 顶部 **Actions** 标签 → 如果出现绿色按钮问你是否启用，点 **I understand my workflows, go ahead and enable them**
2. 左边选 **源检测** → 右边 **Run workflow** → 绿色 **Run workflow**
3. 等 3~5 分钟，刷新，看是不是绿勾

---

### 备选：手工新建 workflow 文件（`.github` 没传上去时用）

1. 仓库页 **Add file** → **Create new file**
2. 文件名直接输入：`.github/workflows/check.yml`（打 `/` 会自动变成目录）
3. 把本地 `C:\Users\Jensen\WorkBuddy\2026-10-20-09-16-06\tv-source-check\.github\workflows\check.yml` 的内容整段复制进去
4. 底部 **Commit changes**

---

## 方法二：命令行（以后每次更新都走这个，最省事）

把两处 `你的用户名` 换掉。第一次 `push` 会弹窗要求登录，选
**「Sign in with your browser」**，浏览器点授权就完事，不用记 token。

```bash
cd C:\Users\Jensen\WorkBuddy\2026-10-20-09-16-06\tv-source-check

# 1. 换成你自己的身份（这样提交记录才会挂在你头像上）
git config user.name  "你的GitHub用户名"
git config user.email "你的GitHub邮箱"
git commit --amend --reset-author --no-edit

# 2. 关联远程仓库
git remote add origin https://github.com/你的用户名/tv-source-check.git

# 3. 推上去
git push -u origin main
```

推送成功后，**以后每次改完只需要三行**：

```bash
cd C:\Users\Jensen\WorkBuddy\2026-10-20-09-16-06\tv-source-check
git add -A
git commit -m "更新清单"
git push
```

> 顺手加一行 `git config --global core.quotepath false`，中文文件名就不会显示成 `\344\270\212...` 这种乱码。

---

## 方法三：GitHub Desktop（图形界面，不想碰命令行用这个）

1. 装 https://desktop.github.com ，打开后用 GitHub 账号登录
2. **File → Add local repository** → 选 `C:\Users\Jensen\WorkBuddy\2026-10-20-09-16-06\tv-source-check`
3. 它会识别到已有仓库（16 个文件的提交已经在里面了）
4. 点右上 **Publish repository** → **Name** 填 `tv-source-check`
5. ⚠️ **把 "Keep this code private" 的勾去掉**（默认是勾上的，不去掉就成私有仓库了）
6. **Publish repository**

以后更新就是：改完文件 → 左下角填一句说明 → **Commit to main** → 右上 **Push origin**。

---

## 跑通之后：直接把 raw 链接当订阅地址

公开仓库最大的好处在这里。推上去之后，这个地址直接粘进播放器就能用，永远指向最新实测通过的清单：

```
https://raw.githubusercontent.com/你的用户名/tv-source-check/main/dist/valid.m3u
```

TVBox / 影视壳 / TiviMate / PotPlayer / VLC 都认。**清单每 6 小时自动刷新，你不用重新导。**

顺带一个只有公开仓库才有的能力：在仓库页 README 顶部加徽章，显示当前可用率——

```markdown
![可用率](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/你的用户名/tv-source-check/main/dist/badge.json)
```

---

## 上传完，逐条打勾确认

- [ ] 仓库里能看到 16 个文件，`.github/workflows/check.yml` 也在
- [ ] **Actions** 标签里能看到「源检测」这个工作流
- [ ] 手动 Run 一次，5 分钟内跑完且是绿勾
- [ ] 跑完后仓库多了一条 `chore: 源检测结果 ...` 的提交（说明会自动回写结果）
- [ ] 点开 `dist/report.md`，能看到最新的可用率表格
- [ ] 用上面的 raw 链接，能在播放器里导入成功
- [ ] 仓库里**没有** `dist/status.json` 和 `dist/dead.m3u`（说明瘦身生效了）

---

## 常见问题对照表

| 现象 | 真正的原因 | 怎么修 |
|---|---|---|
| 找不到 `.github` 文件夹 | 资源管理器藏了隐藏项 | 查看 → 勾「隐藏的项目」；或用手工新建文件那招 |
| Actions 页面没有任何工作流 | `.github/workflows/check.yml` 没传上去 | 见「备选：手工新建 workflow 文件」 |
| 运行成功但最后一步红了 | 机器人没权限回写结果 | **Settings → Actions → General → Workflow permissions** → 选 **Read and write** → Save |
| 定时任务某天不跑了 | 60 天仓库没活动，GitHub 自动暂停定时任务 | Actions 页点 **Enable workflow**；或随便改一下 README 提交一次 |
| `push` 报 `rejected ... fetch first` | 建仓库时勾了 README，远程已有提交 | `git pull --rebase origin main` 然后再 `git push` |
| `push` 报 `Permission denied` / 一直要密码 | 用的还是账号密码 | 改用 Personal Access Token 当密码，或用 GitHub Desktop |
| raw 链接打开是 404 | 仓库还是 Private，或者分支不叫 `main` | 仓库 Settings 拉到最下面改成 Public；确认地址里是 `/main/` |
| 用几次后 raw 链接 404 | 已经是 Public，但文件路径写错 | 核对是 `dist/valid.m3u`，注意大小写 |
| 每次提交都很大的 diff | `status.json` 没被忽略 | 检查 `.gitignore` 里那三行在不在 |
| 担心被人投诉 | 只要不放点播接口和 spider，风险很低 | 保持仓库只含直播 m3u；来源有争议就删掉那几条 |

---

## 最后一句提醒

公开之后，这个仓库就是「一份公开的直播源清单」。**你以后往里加的任何东西都会立刻被所有人看到**，
所以那道线要守住：只放直播 m3u，不放点播聚合接口、不放 spider、不放任何音视频文件。
真的想折腾点播，另开一个私有仓库，或者干脆只在本地跑。
