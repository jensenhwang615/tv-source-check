# 上传到 GitHub（零基础版 · 公开仓库）

本地已经做好了：仓库已建好并提交完毕，分支为 `main`，**16 个文件**已入库，`.git` 不到 300KB。
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
3. 把这 **6 个** 拖进浏览器（拖内容，**不要拖整个 `tv-source-check` 文件夹**）：

```
README.md
requirements.txt
上传到GitHub.md
dist
scripts
sources
```

4. 页面底部点 **Commit changes**

> ⚠️ **不要试图拖 `.github`、`.gitignore`、`.gitattributes`**。GitHub 网页上传对以点开头的文件名
> 一律拒绝，会弹出 **`This file is hidden.`**。这不是你的操作问题，是它的限制。
> 这三个文件用下一步「手工新建」的方式补上。

### 3. 手工新建 3 个隐藏文件（必做）
仓库页 → **Add file** → **Create new file** → 输入下面的文件名 → 粘贴内容 → **Commit changes**。

内容不用自己找，已经有现成的副本（都是看得见的 `.txt`，双击就能打开复制）：

```
C:\Users\Jensen\WorkBuddy\2026-10-20-09-16-06\粘贴到GitHub用\
```

| 复制这个文件 | 在 GitHub 上输入的文件名 | 作用 |
|---|---|---|
| `1-gitignore.txt` | `.gitignore` | 忽略临时文件，让公开仓库保持精简 |
| `2-gitattributes.txt` | `.gitattributes` | 统一换行符（可选，建议加） |
| `3-check.yml.txt` | `.github/workflows/check.yml` | **工作流本体，没有它 Actions 不会跑** |

> 输 `.github/workflows/check.yml` 时不用管目录存不存在，打 `/` 会自动帮你建文件夹。

### 4. 确认工作流在里面（关键）
点进 **`.github/workflows/check.yml`** 能不能看到内容。看不到就是这一步漏了。

### 5. 开跑
1. 顶部 **Actions** 标签 → 如果出现绿色按钮问你是否启用，点 **I understand my workflows, go ahead and enable them**
2. 左边选 **源检测** → 右边 **Run workflow** → 绿色 **Run workflow**
3. 等 3~5 分钟，刷新，看是不是绿勾

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

> **如果报 `! [rejected] main -> main (fetch first)`**：说明你已经在网页上提交过一次了。
> 本地这份是完整的 16 个文件（含网页传不上去的三个隐藏文件），直接覆盖远程最干净：
>
> ```bash
> git push -u --force origin main
> ```
>
> 覆盖掉的只是你网页上那次「缺了隐藏文件」的提交，内容都在本地，不会丢任何东西。

第一次 `push` 会弹出 Git Credential Manager 的窗口，选 **Sign in with your browser**，
浏览器里点一下授权即可，不用手输 token。这个登录方式我已经帮你配好了
（`git config --global credential.helper manager`），以后 push 不会再问。

推送成功后，日常更新见下面这一节。

---

## 日常更新（只上传源，别碰 dist）

**双击 `上传更新.bat` 就行**，它把这四步串起来了：

1. 先把线上最新的检测结果拉回本地（避免冲突）
2. 列出你改了哪些源文件
3. 提交
4. 推送，然后告诉你到哪看进度

没有任何改动时会提示「不需要上传」，不会产生空提交。

不用脚本的话，手动三行：

```bash
cd C:\Users\Jensen\WorkBuddy\2026-10-20-09-16-06\tv-source-check
git pull --ff-only
git add sources
git commit -m "更新源"
git push
```

### 三个必须遵守的规矩

**1. 只 `git add sources`，不要 `git add -A`。**
`dist/` 是 GitHub Actions 跑完自动写回来的产物。你本地手动跑检测也会改 `dist/`，
两边都改就会撞车，push 时报 `rejected / fetch first`。
`dist` 交给机器人管，你只管 `sources/`。

**2. 推送后必须等 Actions 跑完，清单才真的变。**
你推上去的只是「候选源清单」，`dist/valid.m3u`（订阅用的那份）是机器人在 GitHub 的机器上
实测一遍后生成的，约 3~5 分钟。

**3. 别指望本地检测结果。**
在家里跑，香港台会成片失败、国内 CDN 也可能因为代理出口在境外而大量 403。
**以 Actions 的结果为准**，这也是当初上 Actions 的唯一理由。

### 想立刻刷新一次（不改任何文件）怎么办

打开 https://github.com/jensenhwang615/tv-source-check/actions → 左侧「源检测」→
右上 **Run workflow** → 绿色按钮。等 3~5 分钟，`dist/` 会被机器人更新。

### 怎么确认推送成功

| 看哪里 | 正常的样子 |
|---|---|
| 终端最后一行 | `main -> main` 或 `Everything up-to-date` |
| 仓库首页提交列表 | 出现一条你名字的 `update: 源清单更新 ...` |
| Actions 页面 | 多了一条黄色（运行中）→ 变绿（成功） |
| 订阅地址加 `?t=1` 后缀 | 内容有变化（raw 有缓存，不加参数可能还是旧的） |

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
| 拖 `.github` / `.gitignore` 弹 **`This file is hidden.`** | GitHub 网页上传**不支持**以点开头的文件名 | 这 3 个改用 **Add file → Create new file** 手工新建，内容复制 `粘贴到GitHub用\` 里的 txt（见方法一第 3 步） |
| 找不到 `.github` 文件夹 | 资源管理器藏了隐藏项 | 查看 → 勾「隐藏的项目」 |
| Actions 页面没有任何工作流 | `.github/workflows/check.yml` 没传上去 | 见方法一第 3 步「手工新建 3 个隐藏文件」 |
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
