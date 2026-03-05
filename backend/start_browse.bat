@echo off
chcp 65001 >nul
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║   LLCAR Auto Manuals - Просмотр канала                        ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

if "%1"=="" (
    echo Использование: start_browse.bat имя_канала
    echo.
    echo Примеры:
    echo   start_browse.bat avtomanualy
    echo   start_browse.bat autobook_original
    echo.
    set /p channel="Введите имя канала (без @): "
    if "!channel!"=="" (
        echo Канал не указан!
        pause
        exit /b
    )
    python main_v2.py --browse !channel!
) else (
    python main_v2.py --browse %1
)

pause
