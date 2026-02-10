cd /d "%~dp0"
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0generate_list.ps1"
if errorlevel 1 exit /b %errorlevel%
timeout /t 5 /nobreak
git add -A
git commit -m "addition"
git push
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0auto_jules.ps1" %*
