@echo off
title LanBridge Chat
chcp 65001 >nul
cls

echo.
echo  ====================================
echo       LanBridge - LAN Chat App
echo  ====================================
echo.
echo  1) Start SERVER
echo  2) Start CLIENT
echo  3) Exit
echo.
set /p choice="Your choice (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo  [*] Starting server...
    python server.py
    pause
)
if "%choice%"=="2" (
    echo.
    echo  [*] Starting client...
    python client.py
    pause
)
if "%choice%"=="3" exit
