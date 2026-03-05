@echo off
chcp 65001 >nul
title LLCAR Auto Manuals Downloader

:menu
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║       LLCAR Auto Manuals Downloader v2.1                      ║
echo ║       LONG LIFE CAR MANUALS                                   ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  Выберите режим работы:
echo.
echo  [1] 📋 Интерактивная консоль (полный функционал)
echo  [2] 🚀 Автоматическая загрузка (все источники)
echo  [3] 🔍 Просмотр конкретного канала
echo  [0] 🚪 Выход
echo.
set /p choice="Ваш выбор: "

if "%choice%"=="1" goto interactive
if "%choice%"=="2" goto auto
if "%choice%"=="3" goto browse
if "%choice%"=="0" exit
goto menu

:interactive
cls
python main_v2.py --interactive
goto menu

:auto
cls
python main_v2.py
pause
goto menu

:browse
cls
echo.
echo Введите имя канала (без @)
echo Примеры: avtomanualy, autobook_original
echo.
set /p channel="Канал: "
if "%channel%"=="" goto menu
python main_v2.py --browse %channel%
pause
goto menu
