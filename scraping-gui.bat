@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
title LLCAR Control Panel

echo ========================================
echo       LLCAR Control Panel
echo ========================================
echo.

cd /d "%~dp0backend"

echo  Starting on http://localhost:5000 ...
echo.
echo   Home:      http://localhost:5000
echo   Downloads: http://localhost:5000/downloads
echo   Scraping:  http://localhost:5000/scraping
echo.
echo  Both can run simultaneously.
echo  Press Ctrl+C to stop.
echo ========================================
echo.

start "" http://localhost:5000

python web_control.py
