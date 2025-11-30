# 🔧 סקריפט השלמת UNIFIED - Complete Missing Files
# מטרה: להעתיק את הקבצים החסרים מ-CLEAN ל-UNIFIED

$SOURCE_CLEAN = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN"
$TARGET_UNIFIED = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\eScriptorium_UNIFIED"

Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🔧 השלמת קבצים חסרים ל-UNIFIED        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ====================
# שלב 1: בדיקת קיום תיקיות
# ====================

Write-Host "📂 בודק קיום תיקיות..." -ForegroundColor Yellow

if (-not (Test-Path $SOURCE_CLEAN)) {
    Write-Host "❌ שגיאה: תיקיית CLEAN לא נמצאה!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $TARGET_UNIFIED)) {
    Write-Host "❌ שגיאה: תיקיית UNIFIED לא נמצאה!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ תיקיות נמצאו!" -ForegroundColor Green
Write-Host ""

# ====================
# שלב 2: העתקת קבצים חסרים
# ====================

$filescopied = 0
$filesfailed = 0

# 1. docker-compose.yml - קריטי!
Write-Host "📦 מעתיק docker-compose.yml..." -ForegroundColor Yellow
try {
    $dockerComposeSource = "$SOURCE_CLEAN\docker-compose.integrated.yml"
    $dockerComposeTarget = "$TARGET_UNIFIED\docker-compose.yml"
    
    if (Test-Path $dockerComposeSource) {
        Copy-Item $dockerComposeSource $dockerComposeTarget -Force
        Write-Host "  ✅ docker-compose.yml הועתק!" -ForegroundColor Green
        $filescopied++
    } else {
        Write-Host "  ⚠️  docker-compose.integrated.yml לא נמצא ב-CLEAN!" -ForegroundColor Yellow
        $filesfailed++
    }
} catch {
    Write-Host "  ❌ שגיאה בהעתקת docker-compose: $($_.Exception.Message)" -ForegroundColor Red
    $filesfailed++
}

Write-Host ""

# 2. language_support app - הרחבה BiblIA
Write-Host "🌍 מעתיק language_support (BiblIA feature)..." -ForegroundColor Yellow
try {
    $langSupportSource = "$SOURCE_CLEAN\app\apps\language_support"
    $langSupportTarget = "$TARGET_UNIFIED\app\apps\language_support"
    
    if (Test-Path $langSupportSource) {
        if (Test-Path $langSupportTarget) {
            Write-Host "  ⚠️  language_support כבר קיים - מדלג" -ForegroundColor Yellow
        } else {
            Copy-Item $langSupportSource $langSupportTarget -Recurse -Force
            $fileCount = (Get-ChildItem $langSupportTarget -File -Recurse).Count
            Write-Host "  ✅ language_support הועתק! ($fileCount קבצים)" -ForegroundColor Green
            $filescopied++
        }
    } else {
        Write-Host "  ⚠️  language_support לא נמצא ב-CLEAN!" -ForegroundColor Yellow
        $filesfailed++
    }
} catch {
    Write-Host "  ❌ שגיאה בהעתקת language_support: $($_.Exception.Message)" -ForegroundColor Red
    $filesfailed++
}

Write-Host ""

# 3. requirements.txt
Write-Host "📋 מעתיק requirements.txt..." -ForegroundColor Yellow
try {
    # בדוק ברמה הראשית
    if (Test-Path "$SOURCE_CLEAN\requirements.txt") {
        Copy-Item "$SOURCE_CLEAN\requirements.txt" "$TARGET_UNIFIED\" -Force
        Write-Host "  ✅ requirements.txt (root) הועתק!" -ForegroundColor Green
        $filescopied++
    }
    
    # בדוק בתוך app/
    if (Test-Path "$SOURCE_CLEAN\app\requirements.txt") {
        Copy-Item "$SOURCE_CLEAN\app\requirements.txt" "$TARGET_UNIFIED\app\" -Force
        Write-Host "  ✅ requirements.txt (app/) הועתק!" -ForegroundColor Green
        $filescopied++
    }
    
    if (-not (Test-Path "$SOURCE_CLEAN\requirements.txt") -and -not (Test-Path "$SOURCE_CLEAN\app\requirements.txt")) {
        Write-Host "  ⚠️  requirements.txt לא נמצא!" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ שגיאה בהעתקת requirements.txt: $($_.Exception.Message)" -ForegroundColor Red
    $filesfailed++
}

Write-Host ""

# 4. .env file (אם קיים)
Write-Host "🔐 מעתיק .env..." -ForegroundColor Yellow
try {
    if (Test-Path "$SOURCE_CLEAN\.env") {
        Copy-Item "$SOURCE_CLEAN\.env" "$TARGET_UNIFIED\" -Force
        Write-Host "  ✅ .env הועתק!" -ForegroundColor Green
        $filescopied++
    } else {
        Write-Host "  ℹ️  .env לא נמצא (לא קריטי)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ❌ שגיאה בהעתקת .env: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 5. translations/ (Translation Hub)
Write-Host "🌐 מעתיק translations/..." -ForegroundColor Yellow
try {
    if (Test-Path "$SOURCE_CLEAN\translations") {
        if (Test-Path "$TARGET_UNIFIED\translations") {
            Write-Host "  ⚠️  translations/ כבר קיים - מדלג" -ForegroundColor Yellow
        } else {
            Copy-Item "$SOURCE_CLEAN\translations" "$TARGET_UNIFIED\translations" -Recurse -Force
            $fileCount = (Get-ChildItem "$TARGET_UNIFIED\translations" -File -Recurse).Count
            Write-Host "  ✅ translations/ הועתק! ($fileCount קבצים)" -ForegroundColor Green
            $filescopied++
        }
    } else {
        Write-Host "  ℹ️  translations/ לא נמצא (אולי לא נדרש)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ❌ שגיאה בהעתקת translations/: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# ====================
# שלב 3: ניקוי קבצים מיותרים
# ====================

Write-Host "🧹 מנקה קבצים מיותרים..." -ForegroundColor Yellow

# מחק backup files
$backupsRemoved = 0
Get-ChildItem "$TARGET_UNIFIED\*.backup*" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Host "  🗑️  נמחק: $($_.Name)" -ForegroundColor Gray
    $backupsRemoved++
}

if ($backupsRemoved -eq 0) {
    Write-Host "  ℹ️  לא נמצאו קבצי backup למחיקה" -ForegroundColor Cyan
}

Write-Host ""

# העבר SQL files לתיקיית backups
$sqlFiles = Get-ChildItem "$TARGET_UNIFIED\*.sql" -ErrorAction SilentlyContinue
if ($sqlFiles) {
    $backupDir = "$TARGET_UNIFIED\backups"
    if (-not (Test-Path $backupDir)) {
        New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
    }
    
    foreach ($sqlFile in $sqlFiles) {
        Move-Item $sqlFile.FullName "$backupDir\" -Force
        Write-Host "  📦 הועבר לbackups/: $($sqlFile.Name)" -ForegroundColor Gray
    }
}

Write-Host ""

# ====================
# שלב 4: בדיקת שלמות
# ====================

Write-Host "🔍 בודק שלמות..." -ForegroundColor Yellow
Write-Host ""

$checks = @{
    "docker-compose.yml" = Test-Path "$TARGET_UNIFIED\docker-compose.yml"
    "app/manage.py" = Test-Path "$TARGET_UNIFIED\app\manage.py"
    "app/apps/core" = Test-Path "$TARGET_UNIFIED\app\apps\core"
    "app/apps/taba_pipeline" = Test-Path "$TARGET_UNIFIED\app\apps\taba_pipeline"
    "app/apps/cerberus_integration" = Test-Path "$TARGET_UNIFIED\app\apps\cerberus_integration"
    "front/" = Test-Path "$TARGET_UNIFIED\front"
    "Dockerfile" = Test-Path "$TARGET_UNIFIED\Dockerfile"
    "nginx/" = Test-Path "$TARGET_UNIFIED\nginx"
}

$passed = 0
$failed = 0

foreach ($item in $checks.GetEnumerator() | Sort-Object Key) {
    if ($item.Value) {
        Write-Host "  ✅ $($item.Key)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "  ❌ $($item.Key)" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           📊 סיכום ביצוע                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📦 קבצים הועתקו: $filescopied" -ForegroundColor Green
Write-Host "  ❌ נכשלו: $filesfailed" -ForegroundColor $(if ($filesfailed -gt 0) { "Red" } else { "Gray" })
Write-Host "  🗑️  Backups נמחקו: $backupsRemoved" -ForegroundColor Gray
Write-Host ""
Write-Host "  ✅ בדיקות עברו: $passed / $($checks.Count)" -ForegroundColor $(if ($passed -eq $checks.Count) { "Green" } else { "Yellow" })
Write-Host ""

if ($passed -eq $checks.Count) {
    Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   🎉 UNIFIED מושלם ומוכן לשימוש!        ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 השלבים הבאים:" -ForegroundColor Cyan
    Write-Host "  1. cd `"$TARGET_UNIFIED\front`"" -ForegroundColor White
    Write-Host "  2. npm install" -ForegroundColor White
    Write-Host "  3. npm run build" -ForegroundColor White
    Write-Host "  4. cd .." -ForegroundColor White
    Write-Host "  5. docker-compose build" -ForegroundColor White
    Write-Host "  6. docker-compose up -d" -ForegroundColor White
} else {
    Write-Host "⚠️  יש $failed בדיקות שנכשלו - בדוק את השגיאות למעלה" -ForegroundColor Yellow
}

Write-Host ""
