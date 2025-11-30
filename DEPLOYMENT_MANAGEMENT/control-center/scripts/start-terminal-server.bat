@echo off
REM Start Terminal Server - Batch Launcher
REM This opens a new PowerShell window with the auto-start script

echo.
echo ========================================
echo Starting Terminal Server...
echo ========================================
echo.

REM Get current directory (this script is in scripts/)
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Use relative path to auto-start script
start pwsh -NoExit -File "%SCRIPT_DIR%utilities\auto-start-terminal-server.ps1" -NoBrowser

echo.
echo Terminal Server window opened!
echo You can close this window now.
echo.
timeout /t 3
