# ============================================
# Pull and Mirror Images Script
# ============================================
# משוך תמונות base מ-GitHub ומעתיק ל-Registry מקומי
# עוקף חסימות NetFree

param(
    [string]$LocalRegistry = "localhost:5001",
    [switch]$SkipPull,
    [switch]$SkipPush
)

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🔄 Pull & Mirror Images                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# רשימת תמונות
$images = @(
    @{Name="node"; Tag="18-alpine"; Use="Frontend builds"},
    @{Name="registry"; Tag="latest"; Use="Docker Registry"},
    @{Name="postgres"; Tag="15-alpine"; Use="Database"},
    @{Name="python"; Tag="3.10-slim"; Use="Python apps"}
)

$githubRegistry = "ghcr.io/sumca1/escriptorium-project"
$totalImages = $images.Count
$currentImage = 0

Write-Host "📦 תמונות לטיפול: $totalImages`n" -ForegroundColor Yellow

foreach ($image in $images) {
    $currentImage++
    $imageName = "$($image.Name):$($image.Tag)"
    $githubImage = "$githubRegistry/$imageName"
    $localImage = "$LocalRegistry/$imageName"
    
    Write-Host "[$currentImage/$totalImages] 🔄 $imageName" -ForegroundColor Cyan
    Write-Host "    שימוש: $($image.Use)" -ForegroundColor Gray
    
    # Pull from GitHub
    if (-not $SkipPull) {
        Write-Host "    📥 משוך מ-GitHub..." -ForegroundColor Yellow
        docker pull $githubImage 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    ✅ הורד בהצלחה" -ForegroundColor Green
        } else {
            Write-Host "    ❌ שגיאה בהורדה - מדלג" -ForegroundColor Red
            continue
        }
    }
    
    # Tag for local registry
    Write-Host "    🏷️  Tag ל-Registry מקומי..." -ForegroundColor Yellow
    docker tag $githubImage $localImage
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✅ Tagged" -ForegroundColor Green
    } else {
        Write-Host "    ❌ שגיאה ב-tag - מדלג" -ForegroundColor Red
        continue
    }
    
    # Push to local registry
    if (-not $SkipPush) {
        Write-Host "    ⬆️  Push ל-Registry מקומי..." -ForegroundColor Yellow
        docker push $localImage 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    ✅ הועלה ל-$LocalRegistry" -ForegroundColor Green
        } else {
            Write-Host "    ❌ שגיאה ב-push" -ForegroundColor Red
        }
    }
    
    Write-Host ""
}

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║     ✅ סיום!                                             ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "🔍 בודק תמונות ב-Registry המקומי...`n" -ForegroundColor Cyan
try {
    $catalog = (Invoke-WebRequest -Uri "http://$LocalRegistry/v2/_catalog" -UseBasicParsing).Content | ConvertFrom-Json
    Write-Host "📦 תמונות זמינות ב-$LocalRegistry`:" -ForegroundColor Yellow
    $catalog.repositories | ForEach-Object {
        Write-Host "   ✓ $_" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ לא הצליח לבדוק Registry (אולי לא רץ?)" -ForegroundColor Yellow
}

Write-Host "`n🎯 הצעד הבא:" -ForegroundColor Magenta
Write-Host "   cd CORE\eScriptorium_UNIFIED" -ForegroundColor White
Write-Host "   docker build -t localhost:5001/escriptorium:mybuild -f Dockerfile.localregistry ." -ForegroundColor White
Write-Host "`n   זה יבנה תמונה מקומית בלי תלות באינטרנט! 🚀" -ForegroundColor Cyan
