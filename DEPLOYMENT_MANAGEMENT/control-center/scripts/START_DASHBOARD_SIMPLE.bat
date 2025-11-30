@echo off
REM ========================================
REM Simple Dashboard Launcher - All in One Window
REM ========================================

echo.
echo ========================================
echo     Starting BiblIA Dashboard
echo ========================================
echo.

REM Get paths
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
cd ..
set CONTROL_CENTER_ROOT=%CD%

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed!
    pause
    exit /b 1
)

echo [1/2] Starting servers...
echo.

REM Start Terminal Server (port 3001) - in separate window so it stays open
start "Terminal Server (Port 3001)" node "%CONTROL_CENTER_ROOT%\servers\terminal-server.js" 3001

REM Wait a moment for Terminal Server to start
timeout /t 2 /nobreak >nul

REM Start Dashboard Server (port 8080) - in background, no window
start /B node "%CONTROL_CENTER_ROOT%\servers\dashboard-server.js" >nul 2>&1

echo    Terminal Server: Running in separate window (port 3001)
echo    Dashboard Server: Starting on port 8080...
echo.

REM Wait for servers to start
timeout /t 3 /nobreak >nul

echo [2/2] Opening Dashboard in browser...
echo.

REM Open browser once
start http://localhost:8080/dashboard.html

echo.
echo ========================================
echo     Dashboard is now running!
echo ========================================
echo.
echo Terminal Server: http://localhost:3001 (running in separate window)
echo Dashboard:       http://localhost:8080/dashboard.html
echo.
echo IMPORTANT: Terminal Server is in a separate window - do not close it!
echo            To stop everything, close both windows.
echo.
echo Press any key to close this window (Terminal Server will keep running)...
pause >nul

echo.
echo Closing this window...
echo (Terminal Server will keep running in its own window)
timeout /t 2 /nobreak >nul
