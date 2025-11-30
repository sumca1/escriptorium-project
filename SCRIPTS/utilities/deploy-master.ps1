<#
.SYNOPSIS
    Master Deploy Script - מנהל deployments
    
.DESCRIPTION
    סקריפט master לניהול פריסות:
    - Up: מעלה את המערכת
    - Down: מוריד את המערכת
    - Restart: מאתחל
    - Status: בודק סטטוס
    
.PARAMETER Environment
    סביבה: dev, test, prod
    
.PARAMETER Action
    פעולה: up, down, restart, status, full
    
.PARAMETER Up
    קיצור ל-Action up
    
.PARAMETER Down
    קיצור ל-Action down
    
.PARAMETER Restart
    קיצור ל-Action restart
    
.EXAMPLE
    .\deploy-master.ps1 -Environment dev -Up
    .\deploy-master.ps1 -Environment dev -Restart
    .\deploy-master.ps1 -Action full -Environment dev
#>

param(
    [ValidateSet('dev','test','prod')]
    [string]$Environment = 'dev',
    
    [ValidateSet('up','down','restart','status','full')]
    [string]$Action,
    
    [switch]$Up,
    [switch]$Down,
    [switch]$Restart
)

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSCommandPath

# קבע Action מ-switches
if ($Up) { $Action = 'up' }
elseif ($Down) { $Action = 'down' }
elseif ($Restart) { $Action = 'restart' }
elseif (-not $Action) { $Action = 'status' }

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              🚀 Master Deploy Script                           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "⚙️  סביבה: $Environment" -ForegroundColor Yellow
Write-Host "🎯 פעולה: $Action`n" -ForegroundColor Yellow

# בחר את הסקריפט המתאים
$deployScript = Join-Path $ScriptRoot "deploy\deploy-$Environment.ps1"

if (-not (Test-Path $deployScript)) {
    Write-Host "❌ סקריפט לא נמצא: $deployScript" -ForegroundColor Red
    exit 1
}

# הרץ לפי Action
switch ($Action) {
    'up' {
        Write-Host "🚀 מעלה את המערכת..." -ForegroundColor Cyan
        & $deployScript
    }
    'down' {
        Write-Host "🛑 מוריד את המערכת..." -ForegroundColor Yellow
        $dockerComposePath = "..\..\CORE\eScriptorium_UNIFIED"
        Push-Location $dockerComposePath
        docker-compose down
        Pop-Location
    }
    'restart' {
        Write-Host "🔄 מאתחל את המערכת..." -ForegroundColor Yellow
        $dockerComposePath = "..\..\CORE\eScriptorium_UNIFIED"
        Push-Location $dockerComposePath
        docker-compose restart
        Pop-Location
    }
    'status' {
        Write-Host "📊 בודק סטטוס..." -ForegroundColor Cyan
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    }
    'full' {
        Write-Host "🎯 הרצה מלאה: Build + Deploy..." -ForegroundColor Cyan
        Write-Host "`n1️⃣  Build..." -ForegroundColor Yellow
        $buildScript = Join-Path $ScriptRoot "utilities\build-master.ps1"
        if (Test-Path $buildScript) {
            & $buildScript -Environment $Environment
        }
        
        Write-Host "`n2️⃣  Deploy..." -ForegroundColor Yellow
        & $deployScript
    }
}

Write-Host "`n✅ $Action הושלם!" -ForegroundColor Green
