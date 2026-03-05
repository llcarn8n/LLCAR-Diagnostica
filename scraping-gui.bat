@echo off
chcp 65001 >nul
title LLCAR Scraping GUI

echo ====================================
echo   LLCAR Scraping Management GUI
echo ====================================
echo.

cd /d "%~dp0"

:: --- API server on port 8000 ---
netstat -ano 2>nul | findstr ":8000.*LISTENING" >nul 2>&1
if %errorlevel%==0 goto api_ok
echo Starting API server...
start "LLCAR API" cmd /c "call .venv\Scripts\activate.bat && set SKIP_PPLX_EMBED=1 && python -m uvicorn api.server:app --host 0.0.0.0 --port 8000"
timeout /t 5 /nobreak >nul
:api_ok
echo [OK] API on port 8000

:: --- Web server: use 8080 if running, else start on 8090 ---
set WEB_PORT=8090

netstat -ano 2>nul | findstr ":8080.*LISTENING" >nul 2>&1
if %errorlevel%==0 (
    set WEB_PORT=8080
    goto open_browser
)

echo Starting web server on port 8090...
start "LLCAR Scraping Web" cmd /c "npx http-server -p 8090 -c-1"
timeout /t 2 /nobreak >nul

:open_browser
echo [OK] Opening browser...
start http://localhost:%WEB_PORT%/frontend/scraping.html

echo.
echo   API docs: http://localhost:8000/docs
echo.
pause
