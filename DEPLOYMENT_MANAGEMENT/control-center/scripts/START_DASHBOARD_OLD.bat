@echo off
REM ========================================
REM Auto-Start Terminal Server + Dashboard
REM ========================================

echo.
echo ========================================
echo     Starting BiblIA Dashboard
echo ========================================
echo.

REM Get current directory (this script is in scripts/)
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Go to control-center root, then to app/
cd ..
set CONTROL_CENTER_ROOT=%CD%
cd app
set APP_DIR=%CD%

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/3] Starting Terminal Server in background...
start /B powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "%CONTROL_CENTER_ROOT%\scripts\utilities\auto-start-terminal-server-clean.ps1" -Silent -NoBrowser

timeout /t 5 /nobreak >nul

echo [2/3] Waiting for servers to start...
REM auto-start-terminal-server-clean.ps1 starts both:
REM   - Terminal Server (port 3001)
REM   - Dashboard Server (port 8080)

timeout /t 2 /nobreak >nul

echo [3/3] Opening Dashboard in browser...
start http://localhost:8080/dashboard.html

echo.
echo ========================================
echo     Dashboard is now running!
echo ========================================
echo.
echo Terminal Server: http://localhost:3001
echo Dashboard:       http://localhost:8080/dashboard.html
echo.
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping servers...
taskkill /F /FI "WINDOWTITLE eq terminal-server.js*" >nul 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8080" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3001" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>nul

echo Done!
timeout /t 2 /nobreak >nul
