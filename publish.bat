@echo off
REM ===== Artemis Strength — one-click publish =====
REM Double-click this file to rebuild + deploy your site.
cd /d "%~dp0"
title Artemis Strength - Publish

echo.
echo  ===== Publishing Artemis Strength =====
echo.

REM 1. Regenerate exercise pages, sitemap, robots (safe if data unchanged)
echo [1/3] Building pages...
python build_seo.py
if errorlevel 1 (
  echo.
  echo  BUILD FAILED - nothing was deployed. See the error above.
  pause
  exit /b 1
)

REM 2. Commit changes
echo.
set "msg="
set /p "msg=[2/3] Describe what changed (press Enter for 'update'): "
if "%msg%"=="" set "msg=update"
git add -A
git commit -m "%msg%" 1>nul 2>nul
if errorlevel 1 echo      (no new changes to commit - will still push)

REM 3. Push -> triggers auto-deploy on the server
echo.
echo [3/3] Deploying...
git push deploy main
if errorlevel 1 (
  echo.
  echo  PUSH FAILED - check your internet or the 'deploy' remote setup.
  pause
  exit /b 1
)

echo.
echo  ===== DONE - your site will update in a moment =====
echo.
pause
