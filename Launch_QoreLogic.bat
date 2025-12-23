@echo off
title QoreLogic System Launcher
echo --------------------------------------------------------------------------------
echo   Q O R E L O G I C   S Y S T E M   L A U N C H E R
echo --------------------------------------------------------------------------------
echo.
echo Initializing environment...
cd /d "%~dp0"

:: Check for PowerShell
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PowerShell is not installed or not in PATH.
    pause
    exit /b 1
)

:: Run the One-Click PowerShell Script
powershell -NoProfile -ExecutionPolicy Bypass -File "start_system.ps1"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] System launch failed with exit code %errorlevel%.
    pause
)
