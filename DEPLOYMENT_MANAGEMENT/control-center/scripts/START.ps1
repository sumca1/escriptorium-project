# ========================================
# סקריפט הפעלה מהיר (Quick Start Script)
# ========================================

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 מרכז הבקרה - הפעלה מהירה" -ForegroundColor Green
Write-Host "   Control Center - Quick Start" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# עבור לתיקייה הנכונה
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$controlCenterRoot = Split-Path -Parent $scriptDir
$appDir = Join-Path $controlCenterRoot "app"

# וידוא שתיקיית app קיימת
if (-not (Test-Path $appDir)) {
    Write-Host "❌ תיקיית app לא נמצאה!" -ForegroundColor Red
    Write-Host "   צפוי: $appDir" -ForegroundColor Yellow
    exit 1
}

Set-Location $appDir

Write-Host "✅ תיקייה נוכחית: $appDir" -ForegroundColor Green
Write-Host ""

# העתק קבצי תיעוד אם לא קיימים או ישנים
$rootDir = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset"
$files = @("SESSION_LOG.md", "CURRENT_STATE.md")

foreach ($file in $files) {
    $source = Join-Path $rootDir $file
    $dest = Join-Path $appDir $file
    
    if (Test-Path $source) {
        $needsCopy = $false
        
        if (-not (Test-Path $dest)) {
            $needsCopy = $true
            Write-Host "📄 העתקת $file (קובץ חדש)..." -ForegroundColor Yellow
        } else {
            $sourceTime = (Get-Item $source).LastWriteTime
            $destTime = (Get-Item $dest).LastWriteTime
            if ($sourceTime -gt $destTime) {
                $needsCopy = $true
                Write-Host "📄 עדכון $file (גרסה חדשה יותר)..." -ForegroundColor Yellow
            }
        }
        
        if ($needsCopy) {
            Copy-Item $source $dest -Force
            Write-Host "   ✅ הועתק בהצלחה!" -ForegroundColor Green
        } else {
            Write-Host "   ✓ $file מעודכן" -ForegroundColor DarkGreen
        }
    } else {
        Write-Host "   ⚠️ $file לא נמצא במקור" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🌐 מפעיל שרת HTTP..." -ForegroundColor Yellow
Write-Host ""
Write-Host "   הדשבורד יפתח אוטומטית ב:" -ForegroundColor White
Write-Host "   http://localhost:8080/dashboard.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  לעצירה: לחץ Ctrl+C" -ForegroundColor Red
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# המתן שנייה
Start-Sleep -Seconds 1

# פתח בדפדפן
Start-Process "http://localhost:8080/dashboard.html"

# הפעל שרת
python -m http.server 8080
