# 🏗️ סקריפט יצירת מבנה מושלם ל-escriptorium/

$BASE = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium"
$SOURCE_CLEAN = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN"

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🏗️  בונה מבנה escriptorium/ מושלם          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ====================
# שלב 1: יצירת מבנה תיקיות
# ====================

Write-Host "📁 יוצר מבנה תיקיות..." -ForegroundColor Yellow
Write-Host ""

$folders = @{
    # מערכות eScriptorium
    "eScriptorium_UNIFIED" = "מערכת eScriptorium מאורגנת ומושלמת"
    "eScriptorium_CLEAN" = "גרסה עובדת (כבר קיים)"
    
    # ניהול ופיקוח
    "management" = "מערכת ניהול ופיקוח"
    "management\dashboards" = "דשבורדים ויזואליים"
    "management\state" = "מצב ותיעוד"
    "management\supervisor" = "מערכת פיקוח אוטומטית"
    "management\reports" = "דוחות והיסטוריה"
    
    # ממשק משתמש
    "ui" = "ממשק משתמש מרכזי"
    "ui\control-center" = "מרכז בקרה"
    "ui\monitoring" = "ממשקי ניטור"
    "ui\assets" = "CSS, JS, תמונות"
    
    # סקריפטים
    "scripts" = "סקריפטי אוטומציה"
    "scripts\build" = "סקריפטי build"
    "scripts\deploy" = "סקריפטי deploy"
    "scripts\maintenance" = "תחזוקה"
    "scripts\testing" = "בדיקות"
    "scripts\utilities" = "כלי עזר"
    
    # תיעוד
    "docs" = "תיעוד מלא"
    "docs\architecture" = "ארכיטקטורה"
    "docs\guides" = "מדריכים"
    "docs\api" = "תיעוד API"
    
    # לוגים ונתונים
    "logs" = "לוגי מערכת"
    "backups" = "גיבויים"
    "data" = "נתונים"
}

foreach ($folder in $folders.GetEnumerator()) {
    $path = Join-Path $BASE $folder.Key
    if (-not (Test-Path $path)) {
        New-Item -Path $path -ItemType Directory -Force | Out-Null
        Write-Host "  ✅ נוצר: $($folder.Key)" -ForegroundColor Green
        Write-Host "     └─ $($folder.Value)" -ForegroundColor Gray
    } else {
        Write-Host "  ⏭️  כבר קיים: $($folder.Key)" -ForegroundColor Yellow
    }
}

Write-Host ""

# ====================
# שלב 2: השלמת eScriptorium_UNIFIED
# ====================

Write-Host "🔧 משלים eScriptorium_UNIFIED..." -ForegroundColor Yellow
Write-Host ""

$TARGET_UNIFIED = Join-Path $BASE "eScriptorium_UNIFIED"
$filescopied = 0

# 1. docker-compose.yml
Write-Host "  📦 מעתיק docker-compose.yml..." -ForegroundColor Cyan
$dockerSource = Join-Path $SOURCE_CLEAN "docker-compose.integrated.yml"
$dockerTarget = Join-Path $TARGET_UNIFIED "docker-compose.yml"

if ((Test-Path $dockerSource) -and -not (Test-Path $dockerTarget)) {
    Copy-Item $dockerSource $dockerTarget -Force
    Write-Host "    ✅ docker-compose.yml הועתק!" -ForegroundColor Green
    $filescopied++
} elseif (Test-Path $dockerTarget) {
    Write-Host "    ⏭️  docker-compose.yml כבר קיים" -ForegroundColor Yellow
} else {
    Write-Host "    ❌ docker-compose.integrated.yml לא נמצא ב-CLEAN!" -ForegroundColor Red
}

# 2. language_support
Write-Host "  🌍 מעתיק language_support..." -ForegroundColor Cyan
$langSource = Join-Path $SOURCE_CLEAN "app\apps\language_support"
$langTarget = Join-Path $TARGET_UNIFIED "app\apps\language_support"

if ((Test-Path $langSource) -and -not (Test-Path $langTarget)) {
    Copy-Item $langSource $langTarget -Recurse -Force
    $fileCount = (Get-ChildItem $langTarget -File -Recurse).Count
    Write-Host "    ✅ language_support הועתק! ($fileCount קבצים)" -ForegroundColor Green
    $filescopied++
} elseif (Test-Path $langTarget) {
    Write-Host "    ⏭️  language_support כבר קיים" -ForegroundColor Yellow
} else {
    Write-Host "    ⚠️  language_support לא נמצא ב-CLEAN" -ForegroundColor Yellow
}

# 3. requirements.txt
Write-Host "  📋 מעתיק requirements.txt..." -ForegroundColor Cyan
if (Test-Path "$SOURCE_CLEAN\requirements.txt") {
    if (-not (Test-Path "$TARGET_UNIFIED\requirements.txt")) {
        Copy-Item "$SOURCE_CLEAN\requirements.txt" "$TARGET_UNIFIED\" -Force
        Write-Host "    ✅ requirements.txt הועתק!" -ForegroundColor Green
        $filescopied++
    } else {
        Write-Host "    ⏭️  requirements.txt כבר קיים" -ForegroundColor Yellow
    }
}

# 4. .env
Write-Host "  🔐 מעתיק .env..." -ForegroundColor Cyan
if (Test-Path "$SOURCE_CLEAN\.env") {
    if (-not (Test-Path "$TARGET_UNIFIED\.env")) {
        Copy-Item "$SOURCE_CLEAN\.env" "$TARGET_UNIFIED\" -Force
        Write-Host "    ✅ .env הועתק!" -ForegroundColor Green
        $filescopied++
    } else {
        Write-Host "    ⏭️  .env כבר קיים" -ForegroundColor Yellow
    }
} else {
    Write-Host "    ℹ️  .env לא קיים ב-CLEAN (לא קריטי)" -ForegroundColor Cyan
}

Write-Host ""

# ====================
# שלב 3: יצירת קבצי README
# ====================

Write-Host "📝 יוצר קבצי README..." -ForegroundColor Yellow
Write-Host ""

# README ראשי ל-escriptorium/
$readmeMain = @"
# 📁 escriptorium/ - מרכז מערכות eScriptorium

> תיקייה זו מכילה את כל מה שקשור ל-eScriptorium - מערכות, ניהול, ממשק, וסקריפטים

---

## 📂 מבנה התיקייה

### 🎯 מערכות eScriptorium

- **eScriptorium_UNIFIED/** - מערכת eScriptorium מאורגנת ומושלמת
  - כל התכונות של eScriptorium
  - הרחבות BiblIA (taba_pipeline, cerberus, language_support)
  - קוד נקי ומסודר
  
- **eScriptorium_CLEAN/** - גרסה עובדת ויציבה
  - 16 Docker containers פעילים
  - 2,295 תרגומים
  - הכל עובד!

---

### 🎛️ ניהול ופיקוח (management/)

- **dashboards/** - דשבורדים ויזואליים
- **state/** - מצב נוכחי ותיעוד
- **supervisor/** - מערכת פיקוח אוטומטית
- **reports/** - דוחות והיסטוריה

---

### 🖥️ ממשק משתמש (ui/)

- **control-center/** - מרכז בקרה ראשי
- **monitoring/** - ממשקי ניטור
- **assets/** - CSS, JS, תמונות

---

### 🔧 סקריפטים (scripts/)

- **build/** - בנייה וקומפילציה
- **deploy/** - פריסה והפעלה
- **maintenance/** - תחזוקה
- **testing/** - בדיקות
- **utilities/** - כלי עזר

---

### 📚 תיעוד (docs/)

- **architecture/** - ארכיטקטורה
- **guides/** - מדריכים
- **api/** - תיעוד API

---

## 🚀 התחלה מהירה

### הפעלת eScriptorium_UNIFIED:
``````powershell
cd eScriptorium_UNIFIED
docker-compose up -d
``````

### גישה למרכז בקרה:
``````powershell
start ui/control-center/dashboard.html
``````

---

**תאריך יצירה:** $(Get-Date -Format "dd/MM/yyyy")
"@

$readmeMain | Out-File -FilePath (Join-Path $BASE "README.md") -Encoding UTF8 -Force
Write-Host "  ✅ README.md ראשי נוצר" -ForegroundColor Green

# README למערכת ניהול
$readmeManagement = @"
# 🎛️ management/ - מערכת ניהול ופיקוח

> מערכת ניהול אוטומטית למעקב, פיקוח, ודיווח על מערכות eScriptorium

---

## 📂 תיקיות

### dashboards/
דשבורדים ויזואליים למעקב בזמן אמת:
- Build status
- Translation progress
- Docker health
- System metrics

### state/
מצב נוכחי של המערכת:
- CURRENT_STATE.md
- SESSION_LOG.md
- קבצי JSON עם נתונים

### supervisor/
מערכת פיקוח אוטומטית:
- ניטור רציף
- התראות אוטומטיות
- תיקון בעיות אוטומטי

### reports/
דוחות והיסטוריה:
- דוחות יומיים/שבועיים
- ניתוחי ביצועים
- היסטוריית שינויים

---

**תאריך יצירה:** $(Get-Date -Format "dd/MM/yyyy")
"@

$readmeManagement | Out-File -FilePath (Join-Path $BASE "management\README.md") -Encoding UTF8 -Force
Write-Host "  ✅ README.md למערכת ניהול נוצר" -ForegroundColor Green

# README לממשק משתמש
$readmeUI = @"
# 🖥️ ui/ - ממשק משתמש

> ממשקים ויזואליים לניהול ומעקב אחר מערכות eScriptorium

---

## 📂 תיקיות

### control-center/
מרכז בקרה ראשי:
- Dashboard מרכזי
- לחצני בקרה
- סטטוס כללי

### monitoring/
ממשקי ניטור:
- Container health
- Build progress
- Translation status
- Error logs

### assets/
משאבים ויזואליים:
- CSS styles
- JavaScript
- תמונות ואייקונים
- פונטים

---

**תאריך יצירה:** $(Get-Date -Format "dd/MM/yyyy")
"@

$readmeUI | Out-File -FilePath (Join-Path $BASE "ui\README.md") -Encoding UTF8 -Force
Write-Host "  ✅ README.md לממשק משתמש נוצר" -ForegroundColor Green

# README לסקריפטים
$readmeScripts = @"
# 🔧 scripts/ - סקריפטי אוטומציה

> סקריפטים לבנייה, פריסה, תחזוקה ובדיקות

---

## 📂 תיקיות

### build/
סקריפטי בנייה:
- build-frontend.ps1
- compile-translations.ps1
- generate-static.ps1

### deploy/
סקריפטי פריסה:
- deploy-dev.ps1
- deploy-test.ps1
- deploy-prod.ps1
- restart-services.ps1

### maintenance/
תחזוקה:
- cleanup.ps1
- backup.ps1
- update-dependencies.ps1

### testing/
בדיקות:
- run-tests.ps1
- validate-build.ps1
- check-health.ps1

### utilities/
כלי עזר:
- copy-files.ps1
- sync-environments.ps1
- generate-reports.ps1

---

**תאריך יצירה:** $(Get-Date -Format "dd/MM/yyyy")
"@

$readmeScripts | Out-File -FilePath (Join-Path $BASE "scripts\README.md") -Encoding UTF8 -Force
Write-Host "  ✅ README.md לסקריפטים נוצר" -ForegroundColor Green

Write-Host ""

# ====================
# שלב 4: יצירת .gitkeep לתיקיות ריקות
# ====================

Write-Host "📌 יוצר .gitkeep לתיקיות ריקות..." -ForegroundColor Yellow
Write-Host ""

$emptyFolders = @(
    "logs",
    "backups",
    "data",
    "management\reports",
    "ui\assets"
)

foreach ($folder in $emptyFolders) {
    $gitkeepPath = Join-Path $BASE "$folder\.gitkeep"
    if (-not (Test-Path $gitkeepPath)) {
        New-Item -Path $gitkeepPath -ItemType File -Force | Out-Null
        Write-Host "  ✅ .gitkeep נוצר ב-$folder" -ForegroundColor Green
    }
}

Write-Host ""

# ====================
# שלב 5: בדיקת שלמות
# ====================

Write-Host "🔍 בודק שלמות..." -ForegroundColor Yellow
Write-Host ""

$checks = @{
    "eScriptorium_UNIFIED/" = Test-Path (Join-Path $BASE "eScriptorium_UNIFIED")
    "eScriptorium_UNIFIED/docker-compose.yml" = Test-Path (Join-Path $BASE "eScriptorium_UNIFIED\docker-compose.yml")
    "eScriptorium_UNIFIED/app/" = Test-Path (Join-Path $BASE "eScriptorium_UNIFIED\app")
    "management/" = Test-Path (Join-Path $BASE "management")
    "management/dashboards/" = Test-Path (Join-Path $BASE "management\dashboards")
    "ui/" = Test-Path (Join-Path $BASE "ui")
    "ui/control-center/" = Test-Path (Join-Path $BASE "ui\control-center")
    "scripts/" = Test-Path (Join-Path $BASE "scripts")
    "scripts/build/" = Test-Path (Join-Path $BASE "scripts\build")
    "docs/" = Test-Path (Join-Path $BASE "docs")
}

$passed = 0
$total = $checks.Count

foreach ($check in $checks.GetEnumerator() | Sort-Object Key) {
    if ($check.Value) {
        Write-Host "  ✅ $($check.Key)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "  ❌ $($check.Key)" -ForegroundColor Red
    }
}

Write-Host ""

# ====================
# סיכום
# ====================

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              📊 סיכום ביצוע                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "  📁 תיקיות נוצרו: $($folders.Count)" -ForegroundColor Green
Write-Host "  📄 קבצים הועתקו: $filescopied" -ForegroundColor Green
Write-Host "  📝 README קבצים: 4" -ForegroundColor Green
Write-Host "  📌 .gitkeep קבצים: $($emptyFolders.Count)" -ForegroundColor Green
Write-Host ""
Write-Host "  ✅ בדיקות עברו: $passed / $total" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })
Write-Host ""

if ($passed -eq $total) {
    Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   🎉 המבנה מושלם ומוכן לשימוש!              ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "📂 מבנה escriptorium/ מוכן:" -ForegroundColor Cyan
    Write-Host "  ├─ eScriptorium_UNIFIED/    ← מערכת מושלמת" -ForegroundColor White
    Write-Host "  ├─ management/              ← ניהול ופיקוח" -ForegroundColor White
    Write-Host "  ├─ ui/                      ← ממשק משתמש" -ForegroundColor White
    Write-Host "  ├─ scripts/                 ← אוטומציה" -ForegroundColor White
    Write-Host "  └─ docs/                    ← תיעוד" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 הצעד הבא:" -ForegroundColor Cyan
    Write-Host "  cd escriptorium\eScriptorium_UNIFIED" -ForegroundColor White
    Write-Host "  docker-compose build" -ForegroundColor White
    Write-Host "  docker-compose up -d" -ForegroundColor White
} else {
    Write-Host "⚠️  יש $($total - $passed) בדיקות שנכשלו" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📄 קרא את README.md ב-escriptorium/ למידע נוסף" -ForegroundColor Cyan
Write-Host ""
