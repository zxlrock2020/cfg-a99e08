@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === 1/3 重新生成静态订阅（输出到 dist\） ===
python build_sub.py %* || goto :err
echo === 2/3 部署到 Cloudflare Pages ===
call wrangler pages deploy dist --project-name cfg-a99e08 --branch main --commit-dirty=true || goto :err
echo === 3/3 同步到 GitHub（镜像，可删） ===
git add -A
git -c user.email=zxlrock2020@users.noreply.github.com -c user.name=zxlrock2020 commit -m "sub update %date% %time%" >nul 2>&1
git push >nul 2>&1
echo.
echo 完成：https://cfg-a99e08.pages.dev/
pause
exit /b 0
:err
echo 失败：检查 13315 是否可达（Clash 里 VPS IP 要有 DIRECT 规则）
pause
