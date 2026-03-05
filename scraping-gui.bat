@echo off
chcp 65001 >nul 2>&1
title LLCAR Scraping GUI

echo ========================================
echo    LLCAR Scraping - Web Interface
echo ========================================
echo.

cd /d "%~dp0backend"

echo Starting web server on http://localhost:5000 ...
echo.
echo   Main page:    http://localhost:5000
echo   Scraping GUI: http://localhost:5000/scraping
echo.
echo Press Ctrl+C to stop.
echo ========================================
echo.

start "" http://localhost:5000/scraping

python web_control.py
