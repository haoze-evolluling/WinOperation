@echo off
cd /d "%~dp0"
title WinMaster

REM -- Check if already running as admin
fltmc >nul 2>&1
if %errorlevel% equ 0 goto :admin

REM -- Not admin: request elevation
echo [WinMaster] Requesting administrator privileges...
powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit /b

:admin
echo.
echo   ========================================
echo      WinMaster - Local System Manager
echo   ========================================
echo.
echo   Starting server at http://127.0.0.1:8080
echo   Browser will open automatically.
echo   Close this window or press Ctrl+C to stop.
echo.
python main.py

if exist .exit_marker (
    del .exit_marker
    exit /b
)

echo.
echo [WinMaster] Server stopped.
pause
