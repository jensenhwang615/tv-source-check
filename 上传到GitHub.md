# 上传到 GitHub（零基础版）

本地已经做好了：`git init` + 首次提交都已完成，分支为 `main`，19 个文件已入库。
你只需要「把本地仓库推到 GitHub」这一件事。

---

## 第 0 步：先决定仓库是私有还是公开（这一步最重要，别跳过）

| | Private（推荐） | Public |
|---|---|---|
| 谁能看到 `sources/` 里的地址 | 只有你 | 所有人 |
| DMCA / 版权投诉风险 | 基本没有 | 落在你这个账号上 |
| raw 链接能不能直接当订阅地址 | ❌ 要登录才能拉 | ✅ 可以直接订阅 |
| Actions 免费额度 | 2000 分钟/月（本项目约 480，够用） | 无限 |
| 定时任务会不会自动停 | 60 天没提交会自动暂停 | 不会 |

**建议先选 Private。** 理由：`sources/` 里放的是第三方转播节点，公开仓库等于公开分发，
真出问题时被封的是你整个账号（连带你的 3D 公司项目）。私有仓库唯一的代价是
`dist/valid.m3u` 不能直接用 URL 订阅，需要下载下来导进播放器——对你其实没影响。

> 想公开也可以，但把 `sources/` 清空、只留脚本，当技术演示。

---

## 方法一：网页拖拽上传（不装任何软件，约 5 分钟）

### 1. 建一个空仓库
1. 打开 https://github.com ，登录（没账号就注册）
2. 右上角 **`+`** → **New repository**
3. **Repository name** 填 `tv-source-check`
4. 选 **Private**
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

5. 等列表全部出现（19 个文件）→ 页面底部点 **Commit changes**

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

仓库地址里把 `你的用户名` 换掉。第一次 `push` 会弹窗要求登录，选
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

> 小技巧：加一行 `git config --global core.quotepath false`，中文文件名就不会显示成乱码。

---

## 方法三：GitHub Desktop（图形界面，不想碰命令行用这个）

1. 装 https://desktop.github.com ，打开后用 GitHub 账号登录
2. **File → Add local repository** → 选 `C:\Users\Jensen\WorkBuddy\2026-10-20-09-16-06\tv-source-check`
3. 它会识别到已有仓库（19 个文件的提交已经在里面了）
4. 点右上 **Publish repository**
5. **Name** 填 `tv-source-check`，**把 "Keep this code private" 勾上** → **Publish repository**

以后更新就是：改完文件 → 左下角填一句说明 → **Commit to main** → 右上 **Push origin**。

---

## 上传完，逐条打勾确认

- [ ] 仓库里能看到 19 个文件，`.github/workflows/check.yml` 也在
- [ ] **Actions** 标签里能看到「源检测」这个工作流
- [ ] 手动 Run 一次，5 分钟内跑完且是绿勾
- [ ] 跑完后仓库多了一条 `chore: 源检测结果 ...` 的提交（说明会自动回写结果）
- [ ] 点开 `dist/report.md`，能看到最新的可用率表格

四项全绿就说明整套流水线在云端跑通了。之后每 6 小时自动跑一次，你不用管。

---

## 常见问题对照表

| 现象 | 真正的原因 | 怎么修 |
|---|---|---|
| 找不到 `.github` 文件夹 | 资源管理器藏了隐藏项 | 查看 → 勾「隐藏的项目」；或用手工新建文件那招 |
| Actions 页面没有任何工作流 | `.github/workflows/check.yml` 没传上去 | 见「备选：手工新建 workflow 文件」 |
| 运行成功但最后一步红了 | 机器人没权限 copy 结果回去 | **Settings → Actions → General → Workflow permissions** → 选 **Read and write** → Save |
| 定时任务某天不跑了 | 私有仓库 60 天没提交，GitHub 自动暂停定时任务 | Actions 页点 **Enable workflow**；或随便改一下 README 提交一次 |
| `push` 报 `rejected ... fetch first` | 建仓库时勾了 README，远程已有提交 | `git pull --rebase origin main` 然后再 `git push` |
| `push` 报 `Permission denied` / 一直要密码 | 用的还是 HTTPS 密码 | 改用 Personal Access Token 当密码，或用 GitHub Desktop |
| 私有仓库的 raw 链接打开是 404 | 私有仓库的 raw 必须带 token | 正常现象。改成「网页下载 `dist/valid.m3u` → 播放器导入本地文件」 |
| 跑一次花掉多少额度 | 约 4 分钟/次 × 120 次/月 ≈ 480 分钟 | 免费额度 2000 分钟/月，够用；想省就改 cron 为 `0 */12 * * *` |

---

## 最后一句提醒

上传之后，**这个仓库里存的是别人的服务器地址**。私有仓库自己用没问题；
一旦改成 Public，就等于你在替这些节点做公开分发，风险会落到账号上。
真要公开分享，把 `sources/` 清空、只留 `scripts/` 和 `README.md` 当技术演示更稳妥。
