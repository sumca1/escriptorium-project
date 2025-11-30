# ========================================
# 🚀 הפעלת מערכת OCR + Dashboard - All-in-One
# ========================================

param(
    [Parameter(Mandatory=$false)]
    [switch]$Quick,
    
    [Parameter(Mandatory=$false)]
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

# צבעים
function Write-Header { param($Message) Write-Host "`n╔══════════════════════════════════════════╗" -ForegroundColor Cyan; Write-Host "║  $Message" -ForegroundColor Cyan; Write-Host "╚══════════════════════════════════════════╝`n" -ForegroundColor Cyan }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error-Custom { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Step { param($Num, $Message) Write-Host "`n[$Num/6] $Message" -ForegroundColor Yellow }

Write-Header "🚀 מפעיל מערכת OCR BiblIA + Dashboard"

# נתיבים
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$CONTROL_CENTER = Split-Path -Parent $SCRIPT_DIR
$ESCRIPTORIUM_ROOT = Split-Path -Parent (Split-Path -Parent $CONTROL_CENTER)
$DOCKER_DIR = Join-Path $ESCRIPTORIUM_ROOT "CORE\eScriptorium_UNIFIED"
$SERVERS_DIR = Join-Path $CONTROL_CENTER "servers"

Write-Info "📁 תיקיית Docker: $DOCKER_DIR"
Write-Info "📁 תיקיית Servers: $SERVERS_DIR"

# ========================================
# שלב 1: בדיקת Docker Desktop
# ========================================
Write-Step 1 "בודק Docker Desktop..."

try {
    docker ps | Out-Null
    Write-Success "Docker Desktop פעיל"
} catch {
    Write-Warning "Docker Desktop לא פעיל, מנסה להפעיל..."
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    Write-Info "ממתין ל-Docker Desktop..."
    $maxAttempts = 30
    $attempt = 0
    $dockerReady = $false
    
    while ($attempt -lt $maxAttempts) {
        $attempt++
        try {
            docker ps | Out-Null
            $dockerReady = $true
            break
        } catch {
            Write-Host "  ניסיון $attempt/$maxAttempts..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
        }
    }
    
    if (-not $dockerReady) {
        Write-Error-Custom "Docker Desktop לא הצליח להתחיל"
        exit 1
    }
    
    Write-Success "Docker Desktop מוכן!"
}

# ========================================
# שלב 2: הפעלת Terminal Server
# ========================================
Write-Step 2 "מפעיל Terminal Server..."

# בדוק אם כבר רץ
$terminalServerRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001/status" -TimeoutSec 2 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        $terminalServerRunning = $true
        Write-Success "Terminal Server כבר פועל"
    }
} catch {
    Write-Info "Terminal Server לא פועל, מפעיל..."
}

if (-not $terminalServerRunning) {
    # הפעל בחלון נפרד
    $nodeProcess = Start-Process pwsh -ArgumentList @(
        "-NoExit"
        "-Command"
        "cd '$SERVERS_DIR'; node terminal-server.js 3001"
    ) -PassThru
    
    Write-Info "ממתין ל-Terminal Server..."
    Start-Sleep -Seconds 3
    
    # בדוק שהוא פועל
    $attempt = 0
    $serverReady = $false
    while ($attempt -lt 10) {
        $attempt++
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3001/status" -TimeoutSec 2 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                $serverReady = $true
                break
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    
    if ($serverReady) {
        Write-Success "Terminal Server פועל על http://localhost:3001"
    } else {
        Write-Warning "Terminal Server עשוי לקחת עוד כמה שניות להתחיל"
    }
}

# ========================================
# שלב 3: הפעלת eScriptorium Containers
# ========================================
Write-Step 3 "בודק סטטוס קונטיינרים..."

Push-Location $DOCKER_DIR

$containers = docker-compose ps -q
if ($containers) {
    Write-Info "נמצאו קונטיינרים קיימים"
    
    if (-not $Quick) {
        $runningContainers = docker-compose ps --services --filter "status=running"
        $totalServices = (docker-compose config --services).Count
        $runningCount = ($runningContainers | Measure-Object).Count
        
        Write-Info "פועלים: $runningCount/$totalServices"
        
        if ($runningCount -lt $totalServices) {
            Write-Warning "לא כל הקונטיינרים פועלים"
            $answer = Read-Host "להפעיל את כולם? (Y/n)"
            if ($answer -ne 'n') {
                Write-Info "מפעיל קונטיינרים..."
                docker-compose up -d
                Write-Success "קונטיינרים הופעלו!"
            }
        } else {
            Write-Success "כל הקונטיינרים פועלים!"
        }
    }
} else {
    Write-Warning "אין קונטיינרים, האם לבנות ולהעלות? (זה יכול לקחת זמן)"
    $answer = Read-Host "(Y/n)"
    
    if ($answer -ne 'n') {
        Write-Info "בונה ומעלה קונטיינרים..."
        docker-compose up -d --build
        Write-Success "מערכת הועלתה!"
    }
}

Pop-Location

# ========================================
# שלב 4: Dashboard Server (אופציונלי)
# ========================================
Write-Step 4 "בודק Dashboard Server..."

$dashboardRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 2 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        $dashboardRunning = $true
        Write-Success "Dashboard Server פועל"
    }
} catch {
    Write-Info "Dashboard Server לא פועל (אופציונלי)"
}

# ========================================
# שלב 5: פתיחת דפדפן
# ========================================
Write-Step 5 "פותח דשבורדים..."

if (-not $NoBrowser) {
    Start-Sleep -Seconds 2
    
    Write-Info "פותח Control Center Dashboard..."
    Start-Process "http://localhost:3001"
    
    # אם יש קונטיינרים פועלים, פתח גם את eScriptorium
    $runningContainers = docker ps --format "{{.Names}}" | Select-String "web"
    if ($runningContainers) {
        Start-Sleep -Seconds 2
        Write-Info "פותח eScriptorium..."
        Start-Process "http://localhost"
    }
} else {
    Write-Info "דפדפן לא נפתח (דגל NoBrowser)"
}

# ========================================
# שלב 6: סיכום
# ========================================
Write-Step 6 "סיכום המערכת"

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ המערכת פועלת!                                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📊 כתובות זמינות:" -ForegroundColor Cyan
Write-Host "   🎛️  Control Center:  http://localhost:3001" -ForegroundColor White
Write-Host "   💻 Terminal API:     http://localhost:3001/status" -ForegroundColor White

Push-Location $DOCKER_DIR
$runningContainers = docker-compose ps --services --filter "status=running"
if ($runningContainers) {
    Write-Host "   🐳 eScriptorium:      http://localhost" -ForegroundColor White
    Write-Host "`n🐳 קונטיינרים פועלים:" -ForegroundColor Cyan
    docker-compose ps
}
Pop-Location

if ($dashboardRunning) {
    Write-Host "   📊 Dashboard Server:  http://localhost:8080" -ForegroundColor White
}

Write-Host "`n💡 פקודות שימושיות:" -ForegroundColor Yellow
Write-Host "   docker-compose ps              # סטטוס קונטיינרים" -ForegroundColor Gray
Write-Host "   docker-compose logs -f web     # לוגים של web" -ForegroundColor Gray
Write-Host "   docker-compose restart         # אתחול" -ForegroundColor Gray
Write-Host "   docker-compose down            # עצירה" -ForegroundColor Gray

Write-Host "`n✨ מערכת מוכנה לשימוש!" -ForegroundColor Green
Write-Host ""
