# ========================================
# 🐳 Docker Registry Local Setup
# ========================================
# מקים Docker Registry מקומי על המחשב שלך
# פועל בפורט 5000 (ברירת מחדל)
# חוסם את NetFree מלחסום Docker Hub

param(
    [int]$Port = 5000,
    [string]$VolumeName = "docker_registry",
    [switch]$Stop,
    [switch]$Remove
)

Write-Host "╔═══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🐳 Docker Registry Setup               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ============================================
# Stop & Remove
# ============================================
if ($Stop -or $Remove) {
    Write-Host "🛑 עוצר Registry...`n" -ForegroundColor Yellow
    docker stop docker-registry 2>&1 | Out-Null
    
    if ($Remove) {
        Write-Host "🗑️ מוחק Registry...`n" -ForegroundColor Yellow
        docker rm docker-registry 2>&1 | Out-Null
        docker volume rm $VolumeName 2>&1 | Out-Null
        
        Write-Host "✅ Registry הוסר!" -ForegroundColor Green
    } else {
        Write-Host "✅ Registry נעצר!" -ForegroundColor Green
    }
    exit 0
}

# ============================================
# Create Registry
# ============================================
Write-Host "📦 יוצר Docker Volume...`n" -ForegroundColor Cyan
docker volume create $VolumeName

Write-Host "🚀 מפעיל Registry Container...`n" -ForegroundColor Cyan
Write-Host "💡 משתמש בתמונה מ-GitHub Container Registry (עקיפת NetFree)`n" -ForegroundColor Yellow

docker run -d `
  --name docker-registry `
  --restart=always `
  -p ${Port}:5000 `
  -v ${VolumeName}:/var/lib/registry `
  -e REGISTRY_STORAGE_DELETE_ENABLED=true `
  ghcr.io/sumca1/escriptorium-project/registry:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n╔═══════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ Registry פועל בהצלחה!               ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "📍 כתובת Registry:" -ForegroundColor Cyan
    Write-Host "   http://localhost:$Port`n" -ForegroundColor White
    
    Write-Host "🔧 הגדרות Docker:" -ForegroundColor Yellow
    Write-Host '   הוסף ל-daemon.json:' -ForegroundColor White
    Write-Host '   {' -ForegroundColor White
    Write-Host '     "insecure-registries": ["localhost:' -NoNewline -ForegroundColor White
    Write-Host "$Port" -NoNewline -ForegroundColor Cyan
    Write-Host '"]' -ForegroundColor White
    Write-Host "   }`n" -ForegroundColor White
    
    Write-Host "📋 פקודות שימושיות:" -ForegroundColor Yellow
    Write-Host "   • Tag image:    docker tag IMAGE localhost:$Port/IMAGE" -ForegroundColor White
    Write-Host "   • Push image:   docker push localhost:$Port/IMAGE" -ForegroundColor White
    Write-Host "   • Pull image:   docker pull localhost:$Port/IMAGE" -ForegroundColor White
    Write-Host "   • Stop:         .\setup-registry.ps1 -Stop" -ForegroundColor White
    Write-Host "   • Remove:       .\setup-registry.ps1 -Remove`n" -ForegroundColor White
    
    Write-Host "🎯 צעד הבא:" -ForegroundColor Magenta
    Write-Host "   1. הפעל מחדש את Docker Desktop" -ForegroundColor White
    Write-Host "   2. Push image: docker tag ghcr.io/sumca1/escriptorium-project:latest localhost:$Port/escriptorium:latest" -ForegroundColor White
    Write-Host "   3.             docker push localhost:$Port/escriptorium:latest`n" -ForegroundColor White
    
} else {
    Write-Host "❌ שגיאה ביצירת Registry!" -ForegroundColor Red
    exit 1
}
