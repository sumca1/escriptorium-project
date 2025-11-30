# ========================================
# auto-start-terminal-server.ps1
# Start Terminal Server + Control Center Dashboard
# Clean version - November 13, 2025
# ========================================

param(
    [Parameter(Mandatory=$false)]
    [int]$Port = 3001,
    
    [Parameter(Mandatory=$false)]
    [switch]$Silent,
    
    [Parameter(Mandatory=$false)]
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

# Color functions
function Write-Info { 
    param($Message) 
    if (-not $Silent) { Write-Host "INFO: $Message" -ForegroundColor Cyan } 
}

function Write-Success { 
    param($Message) 
    if (-not $Silent) { Write-Host "SUCCESS: $Message" -ForegroundColor Green } 
}

function Write-Warning { 
    param($Message) 
    if (-not $Silent) { Write-Host "WARNING: $Message" -ForegroundColor Yellow } 
}

function Write-Error-Custom { 
    param($Message) 
    Write-Host "ERROR: $Message" -ForegroundColor Red 
}

Write-Info "Starting Terminal Server + Control Center Dashboard..."

# ========================================
# Find paths
# ========================================

# $PSScriptRoot = control-center\scripts\utilities
# control-center = 2 levels up
$controlCenterDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# Find servers directory
$serversDir = Join-Path $controlCenterDir "servers"
$terminalServerPath = Join-Path $serversDir "terminal-server.js"

Write-Host "   Control Center: $controlCenterDir" -ForegroundColor Gray
Write-Host "   Terminal Server: $terminalServerPath" -ForegroundColor Gray

# ========================================
# Check existence
# ========================================

if (-not (Test-Path $terminalServerPath)) {
    Write-Error-Custom "Terminal server not found: $terminalServerPath"
    exit 1
}

# ========================================
# Check port availability
# ========================================

function Test-PortAvailable {
    param([int]$PortNumber)
    
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $PortNumber)
        $listener.Start()
        $listener.Stop()
        return $true
    }
    catch {
        return $false
    }
}

# Find available port
$originalPort = $Port
while (-not (Test-PortAvailable -PortNumber $Port)) {
    Write-Warning "Port $Port busy, trying $(($Port + 1))..."
    $Port++
    
    if ($Port - $originalPort -gt 10) {
        Write-Error-Custom "No available port found after 10 attempts"
        exit 1
    }
}

if ($Port -ne $originalPort) {
    Write-Success "Found available port: $Port"
}

# ========================================
# Start Terminal Server
# ========================================

Write-Info "Starting Terminal Server on port $Port..."

try {
    # Check if node exists
    $nodeVersion = node --version 2>$null
    if (-not $nodeVersion) {
        Write-Error-Custom "Node.js not installed. Install from: https://nodejs.org"
        exit 1
    }
    
    Write-Host "   Node.js: $nodeVersion" -ForegroundColor Gray
    
    # Start terminal-server in separate window
    $params = @{
        FilePath = "node"
        ArgumentList = @($terminalServerPath, $Port.ToString())
        WorkingDirectory = $serversDir
        WindowStyle = "Normal"
    }
    
    Start-Process @params
    
    Write-Success "Terminal Server started in separate window (port $Port)"
    
} catch {
    Write-Error-Custom "Error starting Terminal Server: $_"
    exit 1
}

# ========================================
# Wait for server - health check
# ========================================

Write-Info "Waiting for server to be ready..."

$maxAttempts = 10
$attempt = 0
$serverReady = $false

while ($attempt -lt $maxAttempts -and -not $serverReady) {
    $attempt++
    Start-Sleep -Seconds 1
    
    try {
    $response = Invoke-WebRequest -Uri "http://localhost:$Port/status" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $serverReady = $true
            Write-Success "Server ready! (attempt $attempt/$maxAttempts)"
        }
    }
    catch {
        Write-Host "." -NoNewline
    }
}

if (-not $serverReady) {
    Write-Warning "Server did not respond after $maxAttempts seconds, but it may still be starting..."
}

# ========================================
# Start Dashboard Server (port 8080)
# ========================================

Write-Info "Starting Dashboard Server on port 8080..."

$dashboardServerPath = Join-Path $serversDir "dashboard-server.js"

if (Test-Path $dashboardServerPath) {
    try {
        # Start dashboard-server in separate window
        $dashboardParams = @{
            FilePath = "node"
            ArgumentList = @($dashboardServerPath)
            WorkingDirectory = $controlCenterDir
            WindowStyle = "Normal"
        }
        
        Start-Process @dashboardParams
        
        Write-Success "Dashboard Server started on http://localhost:8080"
        
        # Wait a bit for server to start
        Start-Sleep -Seconds 2
        
    } catch {
        Write-Warning "Error starting Dashboard Server: $_"
    }
} else {
    Write-Warning "Dashboard server not found: $dashboardServerPath"
}

# ========================================
# Open Dashboard in browser
# ========================================

if (-not $NoBrowser) {
    Write-Info "Opening Dashboard in browser..."
    
    # Open Dashboard via HTTP (not file://)
    Start-Process "http://localhost:8080/dashboard.html"
    
    Write-Success "Dashboard opened!"
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Terminal Server: http://localhost:$Port" -ForegroundColor Green
    Write-Host "  Dashboard Server: http://localhost:8080" -ForegroundColor Green
    Write-Host "  Dashboard URL: http://localhost:8080/dashboard.html" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
} else {
    Write-Success "Terminal Server running on http://localhost:$Port"
    Write-Success "Dashboard Server running on http://localhost:8080"
    Write-Info "Dashboard not opened (-NoBrowser flag)"
}

# ========================================
# End - wait forever so window stays open
# ========================================

Write-Success "All ready!"
Write-Host ""
Write-Host "TIP: Terminal Server continues running in background" -ForegroundColor Yellow
Write-Host "     To stop: Close this window (Ctrl+C or X)" -ForegroundColor Gray
Write-Host ""

# Wait forever so terminal window stays open
Write-Host "This terminal will stay open... (do not close!)" -ForegroundColor Cyan
Write-Host "   Checking server health every 30 seconds..." -ForegroundColor Gray
Write-Host ""

# Wait until user manually closes the window
try {
    while ($true) {
        Start-Sleep -Seconds 30
        
        # Check terminal-server health
        $terminalOk = $false
        $dashboardOk = $false
        
        try {
            $healthCheck = Invoke-WebRequest -Uri "http://localhost:$Port/status" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($healthCheck.StatusCode -eq 200) {
                $terminalOk = $true
            }
        } catch { }
        
        # Check dashboard-server health
        try {
            $dashboardCheck = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($dashboardCheck.StatusCode -eq 200) {
                $dashboardOk = $true
            }
        } catch { }
        
        # Display status
        $timestamp = Get-Date -Format 'HH:mm:ss'
        if ($terminalOk -and $dashboardOk) {
            Write-Host "$timestamp - All servers active (Terminal:$Port, Dashboard:8080)" -ForegroundColor Green
        } elseif ($terminalOk) {
            Write-Host "$timestamp - Terminal active ($Port) | Dashboard not responding (8080)" -ForegroundColor Yellow
        } elseif ($dashboardOk) {
            Write-Host "$timestamp - Dashboard active (8080) | Terminal not responding ($Port)" -ForegroundColor Yellow
        } else {
            Write-Host "$timestamp - Both servers not responding!" -ForegroundColor Red
        }
    }
} catch {
    Write-Host ""
    Write-Host "Stopping..." -ForegroundColor Red
}
