<#
.SYNOPSIS
    Master Setup Script - מריץ את כל סקריפטי ההתקנה והתצורה
    
.DESCRIPTION
    סקריפט master שמריץ בסדר נכון:
    1. בדיקת דרישות מקדימות
    2. התקנת dependencies
    3. הגדרת סביבה
    4. בדיקות אינטגרציה
    
.PARAMETER Full
    הרץ התקנה מלאה כולל Docker והכל
    
.PARAMETER Quick
    התקנה מהירה - רק הכרחי
    
.EXAMPLE
    .\setup-master.ps1 -Full
    .\setup-master.ps1 -Quick
#>

param(
    [switch]$Full,
    [switch]$Quick
)

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSCommandPath

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║            🔧 Master Setup Script                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# בדיקות מקדימות
Write-Host "1️⃣  בודק דרישות מקדימות..." -ForegroundColor Yellow
$checkScript = Join-Path $ScriptRoot "utilities\check-requirements.ps1"
if (Test-Path $checkScript) {
    & $checkScript
} else {
    Write-Host "   ⚠️  check-requirements.ps1 לא נמצא, ממשיך..." -ForegroundColor Yellow
}

# Docker
if ($Full) {
    Write-Host "`n2️⃣  בודק Docker..." -ForegroundColor Yellow
    try {
        $dockerRunning = docker ps 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Docker פעיל" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Docker לא רץ - נא להפעיל Docker Desktop" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "   ❌ Docker לא מותקן" -ForegroundColor Red
        exit 1
    }
}

# בנייה
Write-Host "`n3️⃣  מריץ setup של הפרויקט..." -ForegroundColor Yellow
$setupScript = Join-Path $ScriptRoot "build\setup-project-structure.ps1"
if (Test-Path $setupScript) {
    & $setupScript
} else {
    Write-Host "   ⚠️  setup-project-structure.ps1 לא נמצא" -ForegroundColor Yellow
}

# Node.js dependencies
Write-Host "`n4️⃣  מתקין Node.js dependencies..." -ForegroundColor Yellow
$controlCenterServers = Join-Path $ScriptRoot "..\control-center\servers"
if (Test-Path $controlCenterServers) {
    Push-Location $controlCenterServers
    if (Test-Path "package.json") {
        Write-Host "   📦 מריץ npm install..." -ForegroundColor Cyan
        npm install
    }
    Pop-Location
}

# סיכום
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  ✅ Setup הושלם בהצלחה!                        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📋 הצעדים הבאים:" -ForegroundColor Cyan
Write-Host "   1. הרץ: .\SCRIPTS\build-master.ps1" -ForegroundColor White
Write-Host "   2. הרץ: .\SCRIPTS\deploy-master.ps1 -Environment dev -Up" -ForegroundColor White
