@echo off
chcp 65001 >nul
title LLCAR Diagnostica

echo.
echo  LLCAR Diagnostica - Запуск приложения
echo  ======================================
echo.

:: Проверяем наличие .venv
if not exist ".venv\Scripts\activate.bat" (
    echo  [!] Python venv не найден. Запустите deploy\deploy.bat
    pause
    exit /b 1
)

:: Убиваем старые процессы на портах 8000 и 8080 (если есть)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1

:: Запускаем API сервер в фоне
echo  [1/2] Запуск API сервера (порт 8000)...
set SKIP_PPLX_EMBED=1
start "LLCAR API" /min cmd /c "call .venv\Scripts\activate.bat && uvicorn api.server:app --host 0.0.0.0 --port 8000"

:: Ждём пока API стартует
echo        Ожидание загрузки моделей...
timeout /t 5 /nobreak >nul

:: Проверяем API
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo        API ещё загружается, ждём ещё 10 сек...
    timeout /t 10 /nobreak >nul
)

:: Запускаем HTTP сервер
echo  [2/2] Запуск веб-сервера (порт 8080)...
start "LLCAR Web" /min cmd /c "npx http-server -p 8080 -s"

:: Ждём веб-сервер
timeout /t 2 /nobreak >nul

:: Открываем браузер
echo.
echo  Открываю http://localhost:8080/frontend/
start http://localhost:8080/frontend/

echo.
echo  ========================================
echo  API:  http://localhost:8000/health
echo  Web:  http://localhost:8080/frontend/
echo  ========================================
echo.
echo  Оба сервера запущены в фоне.
echo  Чтобы остановить — закройте окна "LLCAR API" и "LLCAR Web"
echo  или нажмите любую клавишу для остановки обоих.
echo.
pause

:: При нажатии клавиши — останавливаем оба
echo  Останавливаю серверы...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1
echo  Готово.
