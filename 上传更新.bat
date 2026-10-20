@echo off
chcp 936 >nul
setlocal
cd /d "%~dp0"

echo ==========================================
echo    TV 源清单 - 上传更新
echo ==========================================
echo.

where git >nul 2>nul
if errorlevel 1 (
  echo [X] 没找到 git。请先安装 Git for Windows。
  pause
  exit /b 1
)

echo [1/4] 先同步线上（把上次自动检测的结果拉回来）...
git pull --ff-only --quiet
if errorlevel 1 (
  echo     [!] 直接拉取没成功，先判断是网络问题还是文件冲突...
  git fetch --quiet
  if errorlevel 1 (
    echo.
    echo [X] 连不上 GitHub。检查网络或代理设置后重新运行。
    pause
    exit /b 1
  )
  echo     网络正常，是本地文件和线上结果撞了。丢弃本地 dist 后重试...
  git checkout -- dist >nul 2>nul
  git pull --ff-only --quiet
  if errorlevel 1 (
    echo [X] 还是拉不下来。请把下面这段内容发给我：
    git status
    pause
    exit /b 1
  )
)
echo     完成。

echo.
echo [2/4] 检查改了哪些文件...
set CHANGED=0
git status --porcelain sources scripts .github | findstr /r "." >nul && set CHANGED=1
if "%CHANGED%"=="0" (
  echo     源文件和脚本都没有改动，不需要上传。
  echo.
  echo     如果你只是想马上刷新清单，可以手动触发一次检测：
  echo     https://github.com/jensenhwang615/tv-source-check/actions
  echo     打开后点 Run workflow
  echo.
  pause
  exit /b 0
)
git status --short sources scripts .github
echo.

echo [3/4] 提交改动...
git add sources scripts .github
git commit -q -m "update: 源清单更新 %DATE% %TIME%"
if errorlevel 1 (
  echo [X] 提交失败，把上面的报错发给我。
  pause
  exit /b 1
)
echo     完成。

echo.
echo [4/4] 推送到 GitHub...
git push
if errorlevel 1 (
  echo [X] 推送失败，把上面的报错发给我。
  pause
  exit /b 1
)

echo.
echo ==========================================
echo    上传成功
echo ==========================================
echo.
echo   GitHub 收到 sources 目录的改动后会自动开始检测，大约 3~5 分钟。
echo   想看进度就打开：
echo   https://github.com/jensenhwang615/tv-source-check/actions
echo.
echo   跑完后订阅地址不变，播放器里点「更新列表」即可：
echo   https://gh-proxy.com/https://raw.githubusercontent.com/jensenhwang615/tv-source-check/main/dist/valid.m3u
echo.
echo   注意：检测是在 GitHub 的机器上跑的，结果通常比在家里跑更准，
echo   尤其是香港台。以线上 report.md 的数字为准。
echo.
pause
