@echo off
chcp 65001 >nul
cd /d "%~dp0"
python build_sub.py >> refresh.log 2>&1
if errorlevel 1 (echo %date% %time% build failed >> refresh.log & exit /b 1)
call wrangler pages deploy dist --project-name cfg-a99e08 --branch main --commit-dirty=true >> refresh.log 2>&1
git add -A >nul 2>&1
git -c user.email=zxlrock2020@users.noreply.github.com -c user.name=zxlrock2020 commit -m "auto refresh %date%" >nul 2>&1
git push >nul 2>&1
echo %date% %time% refreshed >> refresh.log
