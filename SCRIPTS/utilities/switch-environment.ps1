# ========================================
# 🔄 החלפה בין סביבות
# ========================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment,
    
    [switch]$Build,
    [switch]$Up,
    [switch]$Down,
    [switch]$Status
)

$ProjectRoot = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium"
$envPath = Join-Path $ProjectRoot "DEPLOYMENT_MANAGEMENT\environments\$Environment"

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🔄 החלפת סביבה → $Environment                ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# בדוק שהתיקייה קיימת
if (-not (Test-Path $envPath)) {
    Write-Host "❌ שגיאה: תיקייה לא נמצאה: $envPath" -ForegroundColor Red
    exit 1
}

Push-Location $envPath

try {
    if ($Down) {
        Write-Host "🛑 מוריד סביבה נוכחית..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "✅ הורד!" -ForegroundColor Green
    }

    if ($Build) {
        Write-Host "`n🔨 בונה סביבה $Environment..." -ForegroundColor Yellow
        
        $startTime = Get-Date
        docker-compose build
        $duration = (Get-Date) - $startTime
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Build הושלם! ($('{0:mm}:{0:ss}' -f $duration))" -ForegroundColor Green
        } else {
            Write-Host "❌ Build נכשל!" -ForegroundColor Red
            Pop-Location
            exit 1
        }
    }

    if ($Up) {
        Write-Host "`n🚀 מעלה סביבה $Environment..." -ForegroundColor Green
        docker-compose up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n⏳ ממתין להתייצבות (5 שניות)..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            
            Write-Host "`n📊 סטטוס Containers:" -ForegroundColor Cyan
            docker-compose ps
            
            # הצג נקודות גישה
            Write-Host "`n🔗 נקודות גישה:" -ForegroundColor Cyan
            switch ($Environment) {
                "dev" {
                    Write-Host "   • Application: http://localhost:8000" -ForegroundColor White
                    Write-Host "   • Frontend: http://localhost:8080" -ForegroundColor White
                    Write-Host "   • PostgreSQL: localhost:5432" -ForegroundColor White
                }
                "test" {
                    Write-Host "   • Application: http://localhost:8081" -ForegroundColor White
                    Write-Host "   • PostgreSQL: localhost:5433" -ForegroundColor White
                }
                "prod" {
                    Write-Host "   • Application: http://localhost (80)" -ForegroundColor White
                    Write-Host "   • HTTPS: https://localhost (443)" -ForegroundColor White
                }
            }
            
            Write-Host "`n✅ סביבה $Environment פעילה!" -ForegroundColor Green
        } else {
            Write-Host "❌ Up נכשל!" -ForegroundColor Red
            Pop-Location
            exit 1
        }
    }

    if ($Status) {
        Write-Host "`n📊 סטטוס סביבה: $Environment" -ForegroundColor Cyan
        docker-compose ps
    }

} finally {
    Pop-Location
}

Write-Host "`n💡 פקודות שימושיות:" -ForegroundColor Yellow
Write-Host "   • לוגים: docker-compose -f $envPath\docker-compose.yml logs -f" -ForegroundColor Gray
Write-Host "   • עצור: docker-compose -f $envPath\docker-compose.yml down" -ForegroundColor Gray
Write-Host "   • כניסה: docker-compose -f $envPath\docker-compose.yml exec web bash`n" -ForegroundColor Gray
