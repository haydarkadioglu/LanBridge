@echo off
title LAN CHAT
chcp 65001 >nul
cls

echo.
echo  ====================================
echo     LAN CHAT - Python Mesajlasma
echo  ====================================
echo.
echo  1) Sunucu (SERVER) baslat
echo  2) Istemci (CLIENT) baslat
echo  3) Cikis
echo.
set /p secim="Seciminiz (1/2/3): "

if "%secim%"=="1" (
    echo.
    echo  [*] Sunucu baslatiliyor...
    python server.py
    pause
)
if "%secim%"=="2" (
    echo.
    echo  [*] Client baslatiliyor...
    python client.py
    pause
)
if "%secim%"=="3" exit