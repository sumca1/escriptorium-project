# ========================================
# auto-start-terminal-server.ps1
# הפעלת Terminal Server + Control Center Dashboard
# גרסה נקייה - 12 נובמבר 2025
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

# פונקציות צבעים
function Write-Info { 
    param($Message) 
    if (-not $Silent) { Write-Host "ℹ️  $Message" -ForegroundColor Cyan } 
}

function Write-Success { 
    param($Message) 
    if (-not $Silent) { Write-Host "✅ $Message" -ForegroundColor Green } 
}

function Write-Warning { 
    param($Message) 
    if (-not $Silent) { Write-Host "⚠️  $Message" -ForegroundColor Yellow } 
}

function Write-Error-Custom { 
    param($Message) 
    Write-Host "❌ $Message" -ForegroundColor Red 
}

Write-Info "מפעיל Terminal Server + Control Center Dashboard..."

# ========================================
# מציאת נתיבים
# ========================================

# $PSScriptRoot = i:\...\BiblIA_dataset\escriptorium\ui\control-center\scripts\utilities
# control-center = 2 levels up
# BiblIA_dataset = 3 more levels up
# Total: 5 levels up from PSScriptRoot

$controlCenterDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$bibliaDatasetDir = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $controlCenterDir))
$smartScriptPath = Join-Path $bibliaDatasetDir "scripts\start-terminal-server.ps1"
$dashboardPath = Join-Path $controlCenterDir "dashboard.html"

Write-Host "   📂 BiblIA_dataset: $bibliaDatasetDir" -ForegroundColor Gray
Write-Host "   📜 Script: $smartScriptPath" -ForegroundColor Gray
Write-Host "   📊 Dashboard: $dashboardPath" -ForegroundColor Gray

# ========================================
# בדיקות קיום
# ========================================

if (-not (Test-Path $smartScriptPath)) {
    Write-Error-Custom "לא נמצא הסקריפט הראשי: $smartScriptPath"
    exit 1
}

if (-not (Test-Path $dashboardPath)) {
    Write-Error-Custom "לא נמצא Dashboard: $dashboardPath"
    exit 1
}

# ========================================
# בדיקת זמינות פורט
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

# מציאת פורט זמין
$originalPort = $Port
while (-not (Test-PortAvailable -PortNumber $Port)) {
    Write-Warning "פורט $Port תפוס, מנסה $(($Port + 1))..."
    $Port++
    
    if ($Port - $originalPort -gt 10) {
        Write-Error-Custom "לא נמצא פורט זמין אחרי 10 ניסיונות"
        exit 1
    }
}

if ($Port -ne $originalPort) {
    Write-Success "נמצא פורט זמין: $Port"
}

# ========================================
# הפעלת Terminal Server (דרך הסקריפט החכם)
# ========================================

Write-Info "מפעיל Terminal Server על פורט $Port..."

try {
    # קריאה לסקריפט הראשי עם -NoBrowser
    $params = @{
        FilePath = "pwsh"
        ArgumentList = @(
            "-NoExit"
            "-File"
            $smartScriptPath
            "-Port"
            $Port.ToString()
            "-NoBrowser"
        )
        WindowStyle = "Normal"
    }
    
    Start-Process @params
    
    Write-Success "Terminal Server מופעל בחלון נפרד (פורט $Port)"
    
} catch {
    Write-Error-Custom "שגיאה בהפעלת Terminal Server: $_"
    exit 1
}

# ========================================
# Wait for server - health check
# ========================================

Write-Info "ממתין לשרת להיות מוכן..."

$maxAttempts = 10
$attempt = 0
$serverReady = $false

while ($attempt -lt $maxAttempts -and -not $serverReady) {
    $attempt++
    Start-Sleep -Seconds 1
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $serverReady = $true
            Write-Success "שרת מוכן! (ניסיון $attempt/$maxAttempts)"
        }
    }
    catch {
        Write-Host "." -NoNewline
    }
}

if (-not $serverReady) {
    Write-Warning "השרת לא עלה אחרי $maxAttempts שניות, אבל ייתכן שהוא עדיין עולה..."
}

# ========================================
# הפעלת Dashboard Server (פורט 8080)
# ========================================

Write-Info "מפעיל Dashboard Server על פורט 8080..."

$dashboardServerPath = Join-Path $controlCenterDir "dashboard-server.js"

if (Test-Path $dashboardServerPath) {
    try {
        # בדיקה אם node קיים
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-Host "   📦 Node.js: $nodeVersion" -ForegroundColor Gray
            
            # הפעלת dashboard-server בחלון נפרד
            $dashboardParams = @{
                FilePath = "node"
                ArgumentList = @($dashboardServerPath)
                WorkingDirectory = $controlCenterDir
                WindowStyle = "Normal"
            }
            
            Start-Process @dashboardParams
            
            Write-Success "Dashboard Server מופעל על http://localhost:8080"
            
            # המתן קצר לשרת לעלות
            Start-Sleep -Seconds 2
            
        } else {
            Write-Warning "Node.js לא מותקן - Dashboard Server לא הופעל"
            Write-Host "   💡 להתקנה: https://nodejs.org" -ForegroundColor Gray
        }
    } catch {
        Write-Warning "שגיאה בהפעלת Dashboard Server: $_"
    }
} else {
    Write-Warning "לא נמצא: $dashboardServerPath"
}

# ========================================
# פתיחת Dashboard בדפדפן
# ========================================

if (-not $NoBrowser) {
    Write-Info "פותח Dashboard בדפדפן..."
    
    # פתיחת Dashboard דרך HTTP (לא file://)
    Start-Process "http://localhost:8080/dashboard.html"
    
    Write-Success "Dashboard נפתח!"
    Write-Host ""
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  ✅ Terminal Server: http://localhost:$Port" -ForegroundColor Green
    Write-Host "  ✅ Dashboard Server: http://localhost:8080" -ForegroundColor Green
    Write-Host "  ✅ Dashboard URL: http://localhost:8080/dashboard.html" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
} else {
    Write-Success "Terminal Server פועל על http://localhost:$Port"
    Write-Success "Dashboard Server פועל על http://localhost:8080"
    Write-Info "Dashboard לא נפתח (דגל -NoBrowser)"
}

# ========================================
# End - wait forever so window stays open
# ========================================

Write-Success "הכל מוכן! 🎉"
Write-Host ""
Write-Host "💡 טיפ: Terminal Server ממשיך לרוץ ברקע" -ForegroundColor Yellow
Write-Host "   לעצירה: סגור את החלון הזה Ctrl+C או X" -ForegroundColor Gray
Write-Host ""

# Wait forever so terminal window stays open
Write-Host "⏳ המסוף הזה ישאר פתוח... לא לסגור!" -ForegroundColor Cyan
Write-Host "   📊 בודק תקינות שרתים כל 30 שניות..." -ForegroundColor Gray
Write-Host ""

# Wait until user manually closes the window
try {
    while ($true) {
        Start-Sleep -Seconds 30
        
        # Check terminal-server health
        $terminalOk = $false
        $dashboardOk = $false
        
        try {
            $healthCheck = Invoke-WebRequest -Uri "http://localhost:$Port/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
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
            Write-Host "$timestamp - ✅ כל השרתים פעילים (Terminal:$Port, Dashboard:8080)" -ForegroundColor Green
        } elseif ($terminalOk) {
            Write-Host "$timestamp - ⚠️  Terminal פעיל ($Port) | Dashboard לא מגיב (8080)" -ForegroundColor Yellow
        } elseif ($dashboardOk) {
            Write-Host "$timestamp - ⚠️  Dashboard פעיל (8080) | Terminal לא מגיב ($Port)" -ForegroundColor Yellow
        } else {
            Write-Host "$timestamp - ❌ שני השרתים לא מגיבים!" -ForegroundColor Red
        }
    }
} catch {
    Write-Host ""
    Write-Host "🛑 עוצר..." -ForegroundColor Red
}
