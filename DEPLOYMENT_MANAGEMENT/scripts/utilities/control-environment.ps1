# ========================================
# 🚀 סקריפט שליטה בסביבות - Environment Controller
# ========================================
# מטרה: לאפשר הפעלה/עצירה/אתחול של 3 הסביבות
#        דרך ה-Dashboard או מהטרמינל
# ========================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('dev', 'test', 'prod', 'development', 'testing', 'production')]
    [string]$Environment,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'logs')]
    [string]$Action
)

$ErrorActionPreference = "Stop"

# נתיבים
$ProjectRoot = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset"
$EnvDir = Join-Path $ProjectRoot "ENVIRONMENTS"

# תרגום שמות ארוכים לקצרים
$envMap = @{
    'development' = 'dev'
    'testing' = 'test'
    'production' = 'prod'
}

$envShort = if ($envMap.ContainsKey($Environment)) { $envMap[$Environment] } else { $Environment }

# נתיב לסביבה
$envPath = Join-Path $EnvDir $envShort

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🎮 בקר סביבות - Environment Controller                     ║
║                                                                ║
║   📍 סביבה: $($envShort.ToUpper().PadRight(49))║
║   🎯 פעולה: $($Action.PadRight(49))║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ========================================
# בדיקת תיקייה
# ========================================
if (-not (Test-Path $envPath)) {
    Write-Warning "⚠️  תיקיית הסביבה לא קיימת: $envPath"
    Write-Host "`n📁 יוצר תיקייה..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $envPath -Force | Out-Null
    
    # יצירת docker-compose.yml בסיסי
    $composeFile = Join-Path $envPath "docker-compose.yml"
    @"
# Docker Compose - $envShort Environment
version: '3.8'

services:
  web:
    build:
      context: ../../SOURCE
    volumes:
      - ../../SOURCE/app:/usr/src/app
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - HOT_RELOAD=True
"@ | Out-File $composeFile -Encoding UTF8
    
    Write-Host "✅ נוצר docker-compose.yml בסיסי" -ForegroundColor Green
}

# ========================================
# פונקציות בקרה
# ========================================

function Start-Environment {
    Write-Host "`n🚀 מפעיל סביבת $envShort..." -ForegroundColor Green
    
    $composeFile = Join-Path $envPath "docker-compose.yml"
    
    if (-not (Test-Path $composeFile)) {
        Write-Error "❌ קובץ docker-compose.yml לא קיים!"
        return
    }
    
    Push-Location $envPath
    
    try {
        Write-Host "  📦 בונה containers..." -ForegroundColor Cyan
        docker-compose build 2>&1 | ForEach-Object {
            if ($_ -match 'Step|Successfully|ERROR') {
                Write-Host "    $_"
            }
        }
        
        Write-Host "`n  ▶️  מפעיל containers..." -ForegroundColor Cyan
        docker-compose up -d
        
        Write-Host "`n  ⏳ ממתין לאתחול (10 שניות)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        Write-Host "`n  🔍 בודק סטטוס..." -ForegroundColor Cyan
        docker-compose ps
        
        Write-Host "`n✅ הסביבה $envShort פעילה!" -ForegroundColor Green
        
        # עדכון Dashboard
        & "$ProjectRoot\SCRIPTS\update_dashboard.ps1"
    }
    catch {
        Write-Error "❌ שגיאה בהפעלת הסביבה: $_"
    }
    finally {
        Pop-Location
    }
}

function Stop-Environment {
    Write-Host "`n⏹️  עוצר סביבת $envShort..." -ForegroundColor Yellow
    
    $composeFile = Join-Path $envPath "docker-compose.yml"
    
    if (-not (Test-Path $composeFile)) {
        Write-Warning "⚠️  הסביבה לא מוגדרת (אין docker-compose.yml)"
        return
    }
    
    Push-Location $envPath
    
    try {
        docker-compose down
        Write-Host "`n✅ הסביבה $envShort נעצרה" -ForegroundColor Green
        
        # עדכון Dashboard
        & "$ProjectRoot\SCRIPTS\update_dashboard.ps1"
    }
    catch {
        Write-Error "❌ שגיאה בעצירת הסביבה: $_"
    }
    finally {
        Pop-Location
    }
}

function Restart-Environment {
    Write-Host "`n🔄 מאתחל סביבת $envShort..." -ForegroundColor Cyan
    
    Stop-Environment
    Start-Sleep -Seconds 3
    Start-Environment
}

function Get-EnvironmentStatus {
    Write-Host "`n📊 סטטוס סביבת $envShort:" -ForegroundColor Cyan
    
    $composeFile = Join-Path $envPath "docker-compose.yml"
    
    if (-not (Test-Path $composeFile)) {
        Write-Host "  ⚠️  הסביבה לא מוגדרת" -ForegroundColor Yellow
        return
    }
    
    Push-Location $envPath
    
    try {
        Write-Host "`n  🐳 Containers:" -ForegroundColor Cyan
        docker-compose ps
        
        Write-Host "`n  📊 משאבים:" -ForegroundColor Cyan
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker-compose ps -q)
    }
    catch {
        Write-Warning "⚠️  לא ניתן לקבל סטטוס: $_"
    }
    finally {
        Pop-Location
    }
}

function Show-EnvironmentLogs {
    Write-Host "`n📝 לוגים של סביבת $envShort:" -ForegroundColor Cyan
    
    $composeFile = Join-Path $envPath "docker-compose.yml"
    
    if (-not (Test-Path $composeFile)) {
        Write-Host "  ⚠️  הסביבה לא מוגדרת" -ForegroundColor Yellow
        return
    }
    
    Push-Location $envPath
    
    try {
        docker-compose logs --tail 50 --follow
    }
    catch {
        Write-Warning "⚠️  לא ניתן להציג לוגים: $_"
    }
    finally {
        Pop-Location
    }
}

# ========================================
# הפעלת הפעולה המבוקשת
# ========================================

switch ($Action) {
    'start' { Start-Environment }
    'stop' { Stop-Environment }
    'restart' { Restart-Environment }
    'status' { Get-EnvironmentStatus }
    'logs' { Show-EnvironmentLogs }
}

Write-Host "`n✅ פעולה הושלמה!" -ForegroundColor Green
Write-Host "📂 פתח את PROJECT_CONTROL_CENTER.html לראות עדכון`n" -ForegroundColor Cyan
