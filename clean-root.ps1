# ========================================
# Clean Root - הזזת קבצים לתחומים הנכונים
# Moving files from root to correct domains
# ========================================

param(
    [switch]$WhatIf = $false  # רק הצגה, ללא ביצוע
)

$ErrorActionPreference = "Stop"

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🧹 ניקוי Root - הזזת קבצים לתחומים" -ForegroundColor Green
Write-Host "   Cleaning Root - Moving files to correct domains" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($WhatIf) {
    Write-Host "⚠️  מצב תצוגה בלבד (WhatIf Mode)" -ForegroundColor Yellow
    Write-Host "   לא יבוצעו שינויים אמיתיים" -ForegroundColor Yellow
    Write-Host ""
}

# נתיב Root
$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$deploymentPath = Join-Path $rootPath "DEPLOYMENT_MANAGEMENT"
$buildPath = Join-Path $rootPath "BUILD_MANAGEMENT"

Write-Host "📂 נתיב Root: $rootPath" -ForegroundColor Cyan
Write-Host ""

# ========================================
# שלב 1: העברת docs/ → DEPLOYMENT_MANAGEMENT/docs/
# ========================================

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📚 שלב 1: העברת docs/ לתחום Deployment" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$sourceDocs = Join-Path $rootPath "docs"
$targetDocs = Join-Path $deploymentPath "docs-archive"

if (Test-Path $sourceDocs) {
    Write-Host "✓ מצאתי: docs/" -ForegroundColor Green
    Write-Host "  מקור:  $sourceDocs" -ForegroundColor Gray
    Write-Host "  יעד:   $targetDocs" -ForegroundColor Gray
    
    if (-not $WhatIf) {
        # העבר את התיקייה
        if (Test-Path $targetDocs) {
            Write-Host "  ⚠️  docs-archive כבר קיים - ממזג..." -ForegroundColor Yellow
            Get-ChildItem $sourceDocs -Recurse | ForEach-Object {
                $relativePath = $_.FullName.Substring($sourceDocs.Length)
                $targetPath = Join-Path $targetDocs $relativePath
                
                if ($_.PSIsContainer) {
                    New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
                } else {
                    Copy-Item $_.FullName -Destination $targetPath -Force
                }
            }
            Remove-Item $sourceDocs -Recurse -Force
        } else {
            Move-Item $sourceDocs -Destination $targetDocs -Force
        }
        Write-Host "  ✅ הועבר בהצלחה!" -ForegroundColor Green
    } else {
        Write-Host "  [WhatIf] היה מעביר לכאן" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "  ⊘ docs/ לא נמצא (כנראה כבר הועבר)" -ForegroundColor DarkGray
}

Write-Host ""

# ========================================
# שלב 2: מחיקת ui/control-center (כפילות)
# ========================================

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🗑️  שלב 2: מחיקת ui/control-center (כפילות)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$sourceUI = Join-Path $rootPath "ui"

if (Test-Path $sourceUI) {
    Write-Host "✓ מצאתי: ui/" -ForegroundColor Green
    Write-Host "  נתיב: $sourceUI" -ForegroundColor Gray
    
    # בדוק אם יש בו רק control-center
    $items = Get-ChildItem $sourceUI
    if ($items.Count -eq 1 -and $items[0].Name -eq "control-center") {
        Write-Host "  ℹ️  ui/ מכיל רק control-center (שכבר ב-DEPLOYMENT_MANAGEMENT)" -ForegroundColor Cyan
        
        if (-not $WhatIf) {
            try {
                Remove-Item $sourceUI -Recurse -Force -ErrorAction Stop
                Write-Host "  ✅ נמחק!" -ForegroundColor Green
            } catch {
                Write-Host "  ⚠️  לא ניתן למחוק (קובץ נעול) - מדלג..." -ForegroundColor Yellow
                Write-Host "     אפשר למחוק ידנית אחר כך" -ForegroundColor Gray
            }
        } else {
            Write-Host "  [WhatIf] היה מוחק" -ForegroundColor DarkYellow
        }
    } else {
        Write-Host "  ⚠️  ui/ מכיל קבצים נוספים - לא נמחק!" -ForegroundColor Yellow
        $items | ForEach-Object { Write-Host "    - $($_.Name)" -ForegroundColor Gray }
    }
} else {
    Write-Host "  ⊘ ui/ לא נמצא (כנראה כבר נמחק)" -ForegroundColor DarkGray
}

Write-Host ""

# ========================================
# שלב 3: העברת קבצי ארגון
# ========================================

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 שלב 3: העברת קבצי ארגון ותיעוד" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# יצירת תיקיית project-docs
$projectDocsPath = Join-Path $rootPath "project-docs"

if (-not $WhatIf) {
    if (-not (Test-Path $projectDocsPath)) {
        New-Item -ItemType Directory -Path $projectDocsPath -Force | Out-Null
        Write-Host "✓ יצרתי: project-docs/" -ForegroundColor Green
    }
}

# קבצים להעברה
$filesToMove = @(
    "ORGANIZATION_AUDIT_AND_IMPROVEMENTS.md",
    "ORGANIZATION_COMPLETE.md",
    "REORGANIZATION_COMPLETE_REPORT.md",
    "REORGANIZATION_PLAN_3_DOMAINS.md"
)

foreach ($file in $filesToMove) {
    $sourcePath = Join-Path $rootPath $file
    $targetPath = Join-Path $projectDocsPath $file
    
    if (Test-Path $sourcePath) {
        Write-Host "  📄 $file" -ForegroundColor Cyan
        
        if (-not $WhatIf) {
            Move-Item $sourcePath -Destination $targetPath -Force
            Write-Host "     ✅ הועבר ל-project-docs/" -ForegroundColor Green
        } else {
            Write-Host "     [WhatIf] היה מעביר ל-project-docs/" -ForegroundColor DarkYellow
        }
    } else {
        Write-Host "  ⊘ $file לא נמצא" -ForegroundColor DarkGray
    }
}

Write-Host ""

# ========================================
# שלב 4: העברת סקריפט ארגון
# ========================================

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "⚙️  שלב 4: העברת סקריפטי ארגון" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$scriptToMove = "reorganize-to-3-domains.ps1"
$sourcePath = Join-Path $rootPath $scriptToMove
$targetPath = Join-Path $buildPath "tools\$scriptToMove"

if (Test-Path $sourcePath) {
    Write-Host "  📜 $scriptToMove" -ForegroundColor Cyan
    
    if (-not $WhatIf) {
        # וודא שתיקיית tools קיימת
        $toolsDir = Join-Path $buildPath "tools"
        if (-not (Test-Path $toolsDir)) {
            New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
        }
        
        Move-Item $sourcePath -Destination $targetPath -Force
        Write-Host "     ✅ הועבר ל-BUILD_MANAGEMENT/tools/" -ForegroundColor Green
    } else {
        Write-Host "     [WhatIf] היה מעביר ל-BUILD_MANAGEMENT/tools/" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "  ⊘ $scriptToMove לא נמצא" -ForegroundColor DarkGray
}

Write-Host ""

# ========================================
# שלב 5: קבצים שנשארים ב-root
# ========================================

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📌 שלב 5: קבצים שנשארים ב-root (מותרים)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$allowedInRoot = @(
    "README.md",               # המדריך הראשי - חובה!
    "QUICK_START.md",          # מדריך מהיר
    "project-docs",            # תיקיית תיעוד הארגון
    "BUILD_MANAGEMENT",        # תחום 1
    "CORE",                    # תחום 2
    "DEPLOYMENT_MANAGEMENT",   # תחום 3
    ".gitignore",
    ".git",
    "README.md.backup-*"       # גיבויים
)

Write-Host "קבצים מותרים ב-root:" -ForegroundColor Cyan
$allowedInRoot | ForEach-Object {
    Write-Host "  ✓ $_" -ForegroundColor Green
}

Write-Host ""

# ========================================
# שלב 6: דוח סיכום
# ========================================

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 סיכום" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($WhatIf) {
    Write-Host "⚠️  זה היה WhatIf Mode - לא בוצעו שינויים" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "להרצה אמיתית:" -ForegroundColor Cyan
    Write-Host "  .\clean-root.ps1" -ForegroundColor White
} else {
    Write-Host "✅ הניקוי הושלם!" -ForegroundColor Green
    Write-Host ""
    Write-Host "מבנה חדש:" -ForegroundColor Cyan
    Write-Host "  escriptorium/" -ForegroundColor White
    Write-Host "  ├── README.md                    ← מדריך ראשי" -ForegroundColor Gray
    Write-Host "  ├── QUICK_START.md               ← מדריך מהיר" -ForegroundColor Gray
    Write-Host "  ├── project-docs/                ← תיעוד הארגון" -ForegroundColor Gray
    Write-Host "  ├── 📦 CORE/                     ← קוד" -ForegroundColor Green
    Write-Host "  ├── 🏗️  BUILD_MANAGEMENT/        ← build + tools" -ForegroundColor Yellow
    Write-Host "  │   └── tools/                   ← סקריפטי ארגון" -ForegroundColor Gray
    Write-Host "  └── 🚢 DEPLOYMENT_MANAGEMENT/    ← Docker" -ForegroundColor Cyan
    Write-Host "      ├── docs-archive/            ← תיעוד deployment" -ForegroundColor Gray
    Write-Host "      └── control-center/          ← UI" -ForegroundColor Gray
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
