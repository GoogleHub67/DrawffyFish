@echo off
:: Windows Terminal Bootstrapper Launcher
title Drawffyfish - Active Lichess Server Console Monitor
cd /d "%~dp0"

echo ----------------------------------------------------
echo   Drawffyfish Execution Bootstrap Wrapper Script
echo ----------------------------------------------------

:: Verify environment assets are fully generated
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment environment layer mapping missed!
    echo Please right-click "win_setup.ps1" and run with PowerShell first.
    pause
    exit /b 1
)

:: Secure credential pipeline definitions
if exist ".env" (
    echo [INFO] Loading Lichess credential overrides from local .env map file...
    for /f "usebackq tokens=1,2 delims==" %%i in (".env") do (
        if not "%%i"=="" set "%%i=%%j"
    )
) else (
    echo [WARN] .env credentials mapping file not found. Using config.yml defaults.
)

:: Spin up operational virtual loop environment
call .venv\Scripts\activate.bat

echo [LAUNCH] Initiating Main Event Listener Loops...
python main.py

echo ----------------------------------------------------
echo [SHUTDOWN] Engine connection loop terminated cleanly.
pause
