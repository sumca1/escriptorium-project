<#
.SYNOPSIS
    Master Build Script - בונה את כל הקומפוננטות
    
.DESCRIPTION
    מריץ build לכל חלקי הפרויקט:
    - Frontend (Vue.js)
    - Docker images
    - Assets
    
.PARAMETER Environment
    סביבה לבנייה: dev, test, prod
    
.PARAMETER NoBuild
    דלג על Docker build
    
.EXAMPLE
    .\build-master.ps1 -Environment dev
#>

param(
    [ValidateSet('dev','test','prod')]
    [string]$Environment = 'dev',
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSCommandPath
$StartTime = Get-Date

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              🏗️  Master Build Script                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "⚙️  סביבה: $Environment" -ForegroundColor Yellow
Write-Host "📅 זמן התחלה: $($StartTime.ToString('HH:mm:ss'))`n" -ForegroundColor Gray

# Frontend Build
Write-Host "1️⃣  בונה Frontend..." -ForegroundColor Yellow
$frontendPath = "..\..\CORE\eScriptorium_UNIFIED\front"
if (Test-Path $frontendPath) {
    Push-Location $frontendPath
    if (Test-Path "package.json") {
        Write-Host "   📦 מריץ npm build..." -ForegroundColor Cyan
        npm run build
    }
    Pop-Location
    Write-Host "   ✅ Frontend הושלם" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Frontend לא נמצא" -ForegroundColor Yellow
}

# Docker Build
if (-not $NoBuild) {
    Write-Host "`n2️⃣  בונה Docker images..." -ForegroundColor Yellow
    $dockerComposePath = "..\..\CORE\eScriptorium_UNIFIED"
    if (Test-Path "$dockerComposePath\docker-compose.yml") {
        Push-Location $dockerComposePath
        Write-Host "   🐳 מריץ docker-compose build..." -ForegroundColor Cyan
        docker-compose build
        Pop-Location
        Write-Host "   ✅ Docker images הושלמו" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  docker-compose.yml לא נמצא" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n2️⃣  דולג על Docker build (NoBuild)" -ForegroundColor Gray
}

# סיכום
$Duration = (Get-Date) - $StartTime
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  ✅ Build הושלם בהצלחה!                        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "⏱️  זמן כולל: $($Duration.ToString('mm\:ss'))" -ForegroundColor Cyan
Write-Host "`n📋 הצעד הבא:" -ForegroundColor Cyan
Write-Host "   .\SCRIPTS\deploy-master.ps1 -Environment $Environment -Up" -ForegroundColor White
