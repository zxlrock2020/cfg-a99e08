@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === 1/3 重新生成静态订阅 ===
python build_sub.py || goto :err
echo === 2/3 提交 ===
git add -A
git -c user.email=zxlrock2020@users.noreply.github.com -c user.name=zxlrock2020 commit -m "sub update %date% %time%" || echo (无变化，跳过提交)
echo === 3/3 推送 ===
git push
echo.
echo 完成。GitHub Pages 约 30-60 秒后生效。
pause
exit /b 0
:err
echo 生成失败：检查服务器 13315 是否可达（Clash 里给 VPS IP 加 DIRECT 规则）
pause
