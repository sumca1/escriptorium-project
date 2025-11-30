# 🔧 Simple Control Center Reorganizer
# Version: 1.0 - Simplified
# Date: November 13, 2025

$controlCenterPath = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\DEPLOYMENT_MANAGEMENT\control-center"

Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Magenta
Write-Host "  🔧 Control Center Reorganization" -ForegroundColor Magenta
Write-Host "="*80 -ForegroundColor Magenta

# Check if directory exists
if (-not (Test-Path $controlCenterPath)) {
    Write-Host "❌ Error: Control Center directory not found!" -ForegroundColor Red
    Write-Host "Expected: $controlCenterPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n📍 Working on: $controlCenterPath" -ForegroundColor Cyan

# Create subdirectories
$subdirs = @("app", "servers", "docs", "scripts", "runtime", "backups")

Write-Host "`n📁 Creating subdirectories..." -ForegroundColor Cyan
foreach ($dir in $subdirs) {
    $path = Join-Path $controlCenterPath $dir
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "  ✅ Created: $dir/" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️ Exists: $dir/" -ForegroundColor Gray
    }
}

# Move files by pattern
Write-Host "`n📦 Moving files..." -ForegroundColor Cyan

# HTML/JS files to app/
$appFiles = @("*.html", "service-worker.js")
foreach ($pattern in $appFiles) {
    Get-ChildItem -Path $controlCenterPath -Filter $pattern -File | ForEach-Object {
        $target = Join-Path $controlCenterPath "app\$($_.Name)"
        if (-not (Test-Path $target)) {
            Move-Item -Path $_.FullName -Destination $target -Force
            Write-Host "  ✅ app/$($_.Name)" -ForegroundColor Green
        }
    }
}

# Server files
$serverFiles = @("*-server.js", "package*.json")
foreach ($pattern in $serverFiles) {
    Get-ChildItem -Path $controlCenterPath -Filter $pattern -File | ForEach-Object {
        $target = Join-Path $controlCenterPath "servers\$($_.Name)"
        if (-not (Test-Path $target)) {
            Move-Item -Path $_.FullName -Destination $target -Force
            Write-Host "  ✅ servers/$($_.Name)" -ForegroundColor Green
        }
    }
}

# Documentation
Get-ChildItem -Path $controlCenterPath -Filter "*.md" -File | ForEach-Object {
    $target = Join-Path $controlCenterPath "docs\$($_.Name)"
    if (-not (Test-Path $target)) {
        Move-Item -Path $_.FullName -Destination $target -Force
        Write-Host "  ✅ docs/$($_.Name)" -ForegroundColor Green
    }
}

# Scripts
$scriptPatterns = @("*.ps1", "*.bat", "*.vbs")
foreach ($pattern in $scriptPatterns) {
    Get-ChildItem -Path $controlCenterPath -Filter $pattern -File | ForEach-Object {
        $target = Join-Path $controlCenterPath "scripts\$($_.Name)"
        if (-not (Test-Path $target)) {
            Move-Item -Path $_.FullName -Destination $target -Force
            Write-Host "  ✅ scripts/$($_.Name)" -ForegroundColor Green
        }
    }
}

# Runtime files
$runtimeFiles = @(".terminal-server.pid", ".terminal-server-job.txt")
foreach ($file in $runtimeFiles) {
    $sourcePath = Join-Path $controlCenterPath $file
    if (Test-Path $sourcePath) {
        $target = Join-Path $controlCenterPath "runtime\$file"
        Move-Item -Path $sourcePath -Destination $target -Force
        Write-Host "  ✅ runtime/$file" -ForegroundColor Green
    }
}

# Backup files
Get-ChildItem -Path $controlCenterPath -Filter "*BACKUP*" -File | ForEach-Object {
    $target = Join-Path $controlCenterPath "backups\$($_.Name)"
    if (-not (Test-Path $target)) {
        Move-Item -Path $_.FullName -Destination $target -Force
        Write-Host "  ✅ backups/$($_.Name)" -ForegroundColor Green
    }
}

# Create .gitignore
Write-Host "`n🔒 Creating .gitignore..." -ForegroundColor Cyan
$gitignoreContent = @"
# Runtime files
runtime/
*.pid
*.log

# Logs
logs/*.log

# Backups
backups/

# Node modules
servers/node_modules/

# OS files
.DS_Store
Thumbs.db
"@

$gitignorePath = Join-Path $controlCenterPath ".gitignore"
$gitignoreContent | Out-File -FilePath $gitignorePath -Encoding UTF8
Write-Host "  ✅ Created .gitignore" -ForegroundColor Green

# Create main INDEX.md
Write-Host "`n📄 Creating INDEX.md..." -ForegroundColor Cyan
$indexContent = @"
# 🎛️ Control Center - Directory Index

## 📂 Directory Structure

``````
control-center/
├── app/              → Frontend files (HTML, JS, CSS)
├── servers/          → Backend Node.js servers
├── docs/             → Documentation
├── scripts/          → Startup scripts
├── runtime/          → Runtime files (gitignored)
├── backups/          → Backup files (gitignored)
├── data/             → Dashboard data
├── logs/             → Log files
└── modules/          → Reusable modules
``````

## 🚀 Quick Start

### Start Control Center:
``````powershell
.\scripts\START_DASHBOARD.bat
``````

### Access:
- Control Center: http://localhost:3002

---

**Version:** 2.0 (Reorganized)
**Last Updated:** $(Get-Date -Format "yyyy-MM-dd HH:mm")
"@

$indexPath = Join-Path $controlCenterPath "INDEX.md"
$indexContent | Out-File -FilePath $indexPath -Encoding UTF8
Write-Host "  ✅ Created INDEX.md" -ForegroundColor Green

# Summary
Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Magenta
Write-Host "  ✅ Control Center Reorganization Complete!" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Magenta

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "  - Created 6 subdirectories" -ForegroundColor White
Write-Host "  - Moved files by type" -ForegroundColor White
Write-Host "  - Created .gitignore" -ForegroundColor White
Write-Host "  - Created INDEX.md" -ForegroundColor White

Write-Host "`n🎯 Control Center is now organized!" -ForegroundColor Green
Write-Host ""
