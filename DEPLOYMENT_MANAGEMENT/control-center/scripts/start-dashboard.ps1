# ========================================
# סקריפט להפעלת Dashboard עם שרת HTTP
# Start Dashboard with HTTP Server
# ========================================

param(
    [int]$Port = 8080
)

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 מפעיל מרכז הבקרה (Starting Control Center Dashboard)" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# קביעת נתיבים - הסקריפט נמצא ב-scripts/, צריך לעבור ל-app/
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$controlCenterRoot = Split-Path -Parent $scriptDir
$appDir = Join-Path $controlCenterRoot "app"

# וידוא שתיקיית app קיימת
if (-not (Test-Path $appDir)) {
    Write-Host "❌ תיקיית app לא נמצאה!" -ForegroundColor Red
    Write-Host "   צפוי: $appDir" -ForegroundColor Yellow
    exit 1
}

Write-Host "📂 תיקיית העבודה: $appDir" -ForegroundColor Cyan
Write-Host ""

# בדוק אם Python קיים
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
}

if ($pythonCmd) {
    Write-Host "✅ Python נמצא!" -ForegroundColor Green
    Write-Host "📡 מתחיל שרת HTTP על פורט $Port..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 פתח בדפדפן:" -ForegroundColor Yellow
    Write-Host "   http://localhost:$Port/dashboard.html" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  לעצירה: לחץ Ctrl+C" -ForegroundColor Red
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    # המתן שניה ואז פתח בדפדפן
    Start-Sleep -Seconds 1
    Start-Process "http://localhost:$Port/dashboard.html"
    
    # עבור לתיקיית app והפעל שרת HTTP
    Push-Location $appDir
    try {
        & $pythonCmd -m http.server $Port
    } finally {
        Pop-Location
    }
    
} else {
    Write-Host "❌ Python לא נמצא במערכת!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 פתרונות אלטרנטיביים:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1️⃣  התקן Python:" -ForegroundColor Cyan
    Write-Host "   https://www.python.org/downloads/" -ForegroundColor White
    Write-Host ""
    Write-Host "2️⃣  השתמש ב-Node.js (אם מותקן):" -ForegroundColor Cyan
    Write-Host "   npx http-server -p $Port" -ForegroundColor White
    Write-Host ""
    Write-Host "3️⃣  פתח דרך VSCode:" -ForegroundColor Cyan
    Write-Host "   לחץ ימני על dashboard.html → 'Open with Live Server'" -ForegroundColor White
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    
    # בדוק אם npx זמין
    if (Get-Command npx -ErrorAction SilentlyContinue) {
        Write-Host ""
        Write-Host "✅ Node.js נמצא! משתמש ב-http-server..." -ForegroundColor Green
        Write-Host ""
        Start-Sleep -Seconds 1
        Start-Process "http://localhost:$Port/dashboard.html"
        
        # עבור לתיקיית app והפעל שרת
        Push-Location $appDir
        try {
            npx http-server -p $Port
        } finally {
            Pop-Location
        }
    }
}
