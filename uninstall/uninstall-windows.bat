@echo off
setlocal enabledelayedexpansion
title Dezinstalare GDC Production Manager

echo ==================================================
echo  Dezinstalare GDC Production Manager
echo ==================================================
echo.

REM Opreste aplicatia daca ruleaza, ca sa nu ramana fisiere blocate.
taskkill /F /IM GDCProductionManager.exe >nul 2>&1
taskkill /F /IM "GDC Production Manager Monitor.exe" >nul 2>&1

set /p DELETE_DATA="Stergi si datele salvate (conturi, proiecte, licenta)? [y/N] "
echo.

REM Aplicatia e un .exe portabil, langa acest script (nu are instalator real).
if exist "%~dp0GDCProductionManager.exe" (
    echo Sterg %~dp0GDCProductionManager.exe ...
    del /f /q "%~dp0GDCProductionManager.exe"
)
if exist "%~dp0GDC Production Manager Monitor.exe" (
    del /f /q "%~dp0GDC Production Manager Monitor.exe"
)

if /i "%DELETE_DATA%"=="y" (
    if exist "%APPDATA%\GDCProductionManager" (
        echo Sterg datele din %APPDATA%\GDCProductionManager ...
        rmdir /s /q "%APPDATA%\GDCProductionManager"
    )
) else (
    echo Pastrez datele din %APPDATA%\GDCProductionManager ^(le poti sterge manual oricand^).
)

echo.
echo Dezinstalare terminata.
echo Poti sterge acum si acest folder (dezarhivat), daca vrei.
pause
