# 🚀 Core Scripts System - המדריך המלא

**נוצר:** 12 נובמבר 2025  
**גרסה:** 1.0  
**עיקרון:** כל סקריפט = מומחה בתחומו. אפס כפילויות.

---

## 📚 מבנה המערכת

```
SCRIPTS/
├── core/                                    ← ספריות ליבה (משותפות)
│   ├── ui-functions.ps1                     ← תצוגה: colors, progress bars, boxes
│   ├── docker-functions.ps1                 ← Docker: checks, containers, deploy
│   └── build-functions.ps1                  ← Build: npm, webpack, verification
│
├── dev-deploy.ps1                           ← סקריפט ראשי לפיתוח ✨
├── prod-deploy.ps1                          ← (עתיד) סקריפט ייצור
└── troubleshoot.ps1                         ← (עתיד) פתרון בעיות

lib/                                         ← מיקרו-סקריפטים ישנים (deprecated)
```

---

## 🎯 הפילוסופיה

### ✅ מה עשינו נכון:

1. **ספריות ליבה משותפות**
   - `ui-functions.ps1` - כל הצגת הUI במקום אחד
   - `docker-functions.ps1` - כל Docker במקום אחד
   - `build-functions.ps1` - כל Build במקום אחד

2. **סקריפטים ראשיים פשוטים**
   - טוענים את הספריות
   - קוראים לפונקציות המתאימות
   - לא משכפלים קוד

3. **פס התקדמות מקצועי**
   ```
   [━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ✓] 100%
   ```

### ❌ מה הימנענו:

1. **588 סקריפטים** שכל אחד עושה חצי עבודה
2. **כפילויות קוד** - כל progress bar נכתב מחדש
3. **בלאגן** - לא יודעים איזה סקריפט לקרוא

---

## 🚀 שימוש מהיר

### הרצה רגילה (Standard):
```powershell
.\SCRIPTS\dev-deploy.ps1
```

**מה זה עושה:**
1. ✅ בודק Docker
2. ✅ npm ci (מהיר)
3. ✅ npm run build
4. ✅ העתקה ל-Docker
5. ✅ Restart services
6. ✅ אימות

**זמן:** ~3-5 דקות

---

### הרצה מהירה (Quick):
```powershell
.\SCRIPTS\dev-deploy.ps1 -Quick
```

**מה זה מדלג:**
- ⚡ לא מריץ npm install (אם node_modules קיים)

**זמן:** ~1-2 דקות

---

### הרצה מלאה (Force):
```powershell
.\SCRIPTS\dev-deploy.ps1 -Force
```

**מה זה עושה:**
1. 🗑️ מוחק node_modules
2. 🗑️ מנקה npm cache
3. 🗑️ מוחק dist/
4. ✅ npm install מחדש
5. ✅ npm run build מחדש
6. ✅ deploy מחדש

**זמן:** ~5-10 דקות

---

### רק בדיקה (Verify):
```powershell
.\SCRIPTS\dev-deploy.ps1 -VerifyOnly
```

**מה זה עושה:**
- ✅ בודק Docker
- ✅ בודק Container health
- ❌ לא בונה
- ❌ לא פורס

**זמן:** ~10 שניות

---

## 📖 הספריות - מדריך מפורט

### 1️⃣ ui-functions.ps1

**מה יש בו:**

```powershell
# Basic output
Write-Header "כותרת"               # ═══ כותרת ═══
Write-Success "הצלחה"              # ✓ הצלחה
Write-Error-Custom "שגיאה"         # ✗ שגיאה
Write-Warning-Custom "אזהרה"       # ⚠ אזהרה
Write-Info "מידע"                  # ℹ מידע
Write-Step 1 "שלב ראשון"           # [1] שלב ראשון

# Progress bars
Show-ProgressBar -Activity "בונה" -Percent 75
# Output: בונה [━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━─────────────] 75%

Show-ProgressBarComplete -Activity "בונה" -Success
# Output: בונה [━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ✓] 100%

Show-ThinProgressBar -Activity "npm install" -Percent 45 -Color Yellow
# Output: npm install [━━━━━━━━━━━━━━─────────────────] 45%

# Boxes
Write-Box -Lines @("שורה 1", "שורה 2") -Color Green
# Output:
# ╔════════════╗
# ║  שורה 1    ║
# ║  שורה 2    ║
# ╚════════════╝

# Tables
Write-Table -Headers @("קובץ", "סטטוס") -Rows @(
    @("editor.js", "✓"),
    @("vendor.js", "✓")
)
# Output:
# ┌──────────────┬──────────┐
# │ קובץ         │ סטטוס    │
# ├──────────────┼──────────┤
# │ editor.js    │ ✓        │
# │ vendor.js    │ ✓        │
# └──────────────┴──────────┘

# Spinner
Show-Spinner -Message "ממתין..."  # ⠋ ממתין...
Stop-Spinner -Message "סיים" -Success  # ✓ סיים
```

**איך משתמשים:**

```powershell
# בראש הסקריפט:
. "$PSScriptRoot\core\ui-functions.ps1"

# בגוף הסקריפט:
Write-Header "Building Frontend"
Show-ProgressBar -Activity "Build" -Percent 50
Write-Success "Build complete"
```

---

### 2️⃣ docker-functions.ps1

**מה יש בו:**

```powershell
# Prerequisite checks
Test-DockerInstalled                 # → $true/$false
Test-DockerComposeInstalled          # → $true/$false
Test-DockerRunning                   # → $true/$false

# Container operations
Test-ContainerRunning -ContainerName "web-1"  # → $true/$false
Start-DockerContainers -WorkingDirectory "."  # → $true/$false
Stop-DockerContainers                         # → $true/$false
Restart-DockerService -Services @("web", "nginx")

# File operations
Copy-ToContainer `
    -SourcePath "dist/editor.js" `
    -ContainerName "web-1" `
    -DestinationPath "/usr/src/app/static/editor.js"

# Execute commands
$result = Invoke-ContainerCommand `
    -ContainerName "web" `
    -Command "python manage.py check"

if ($result.Success) {
    Write-Success "Command succeeded"
}

# Health checks
$health = Test-ContainerHealth -ContainerName "web-1"
# Returns: @{ IsRunning, HasErrors, Status, Logs }

# Smart start
Start-ContainerIfNeeded -ContainerName "web-1"
# Starts only if not already running
```

**דוגמה מלאה:**

```powershell
. "$PSScriptRoot\core\docker-functions.ps1"

# Check prerequisites
if (-not (Test-DockerInstalled)) {
    Write-Error "Docker not installed"
    exit 1
}

if (-not (Test-DockerRunning)) {
    Write-Error "Docker not running"
    exit 1
}

# Ensure container is running
if (Start-ContainerIfNeeded -ContainerName "web-1") {
    Write-Success "Container ready"
    
    # Deploy file
    Copy-ToContainer `
        -SourcePath "dist/editor.js" `
        -ContainerName "web-1" `
        -DestinationPath "/usr/src/app/static/editor.js"
    
    # Restart
    Restart-DockerService -Services @("web")
    
    # Verify
    $health = Test-ContainerHealth -ContainerName "web-1"
    if ($health.Status -eq "Healthy") {
        Write-Success "Deployment successful"
    }
}
```

---

### 3️⃣ build-functions.ps1

**מה יש בו:**

```powershell
# Prerequisites
Test-NpmInstalled     # → $true/$false
Test-NodeInstalled    # → $true/$false

# Install dependencies
Install-NpmDependencies `
    -FrontendPath "front" `
    -UseNpmCi                    # מהיר יותר מ-npm install
# Shows progress bar during install

# Build
Build-Frontend `
    -FrontendPath "front" `
    -BuildCommand "npm run build"
# Shows progress bar + elapsed time

# Verify
$result = Test-BuildOutput `
    -FrontendPath "front" `
    -RequiredFiles @("dist/editor.js", "dist/vendor.js")

if ($result.Success) {
    Write-Success "All files present"
} else {
    Write-Error "Missing: $($result.MissingFiles -join ', ')"
}

# Statistics
$stats = Get-BuildStatistics -FrontendPath "front"
# Returns: @{ TotalFiles, TotalSize, LargestFile, LargestSize }

# Clean
Remove-NodeModules -FrontendPath "front"
Clear-NpmCache
Reset-BuildEnvironment -FrontendPath "front"  # מחיקה מלאה
```

**דוגמה מלאה:**

```powershell
. "$PSScriptRoot\core\build-functions.ps1"

$frontPath = "eScriptorium_CLEAN\front"

# Check prerequisites
if (-not (Test-NpmInstalled)) {
    Write-Error "npm not found"
    exit 1
}

# Install (fast mode)
if (Install-NpmDependencies -FrontendPath $frontPath -UseNpmCi) {
    # Build
    if (Build-Frontend -FrontendPath $frontPath) {
        # Verify
        $check = Test-BuildOutput -FrontendPath $frontPath
        
        if ($check.Success) {
            # Show stats
            $stats = Get-BuildStatistics -FrontendPath $frontPath
            Write-Info "Built $($stats.TotalFiles) files ($($stats.TotalSize) MB)"
        }
    }
}
```

---

## 🎨 דוגמאות שימוש

### דוגמה 1: סקריפט deployment פשוט

```powershell
# my-deploy.ps1

param([switch]$Quick)

# Load libraries
. "$PSScriptRoot\core\ui-functions.ps1"
. "$PSScriptRoot\core\docker-functions.ps1"
. "$PSScriptRoot\core\build-functions.ps1"

Write-Header "My Custom Deployment"

# Check Docker
if (-not (Test-DockerRunning)) {
    Write-Error-Custom "Docker not running"
    exit 1
}

# Build (if not Quick)
if (-not $Quick) {
    if (-not (Build-Frontend -FrontendPath "front")) {
        Write-Error-Custom "Build failed"
        exit 1
    }
}

# Deploy
Copy-ToContainer `
    -SourcePath "front/dist/editor.js" `
    -ContainerName "web-1" `
    -DestinationPath "/usr/src/app/static/editor.js"

# Restart
Restart-DockerService -Services @("web")

Write-Success "Deployment complete!"
```

---

### דוגמה 2: סקריפט בדיקת בריאות

```powershell
# health-check.ps1

. "$PSScriptRoot\core\ui-functions.ps1"
. "$PSScriptRoot\core\docker-functions.ps1"

Write-Header "System Health Check"

# Check Docker
Write-Step 1 "Checking Docker"
$dockerOK = Test-DockerRunning
if ($dockerOK) {
    Write-Success "Docker: Running"
} else {
    Write-Error-Custom "Docker: Not running"
}

# Check Container
Write-Step 2 "Checking Container"
$health = Test-ContainerHealth -ContainerName "web-1"

$statusColor = switch ($health.Status) {
    "Healthy" { "Green" }
    "Running with errors" { "Yellow" }
    default { "Red" }
}

Write-Host "Status: " -NoNewline
Write-Host $health.Status -ForegroundColor $statusColor

if ($health.HasErrors) {
    Write-Warning-Custom "Recent errors in logs:"
    $health.Logs | Select-Object -Last 5 | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Yellow
    }
}

# Summary
if ($dockerOK -and $health.IsRunning -and -not $health.HasErrors) {
    Write-Box -Lines @("✅ System Healthy") -Color Green
} else {
    Write-Box -Lines @("⚠️ Issues Detected") -Color Yellow
}
```

---

### דוגמה 3: סקריפט ניקוי

```powershell
# clean-all.ps1

param([switch]$Force)

. "$PSScriptRoot\core\ui-functions.ps1"
. "$PSScriptRoot\core\build-functions.ps1"

Write-Header "Cleaning Build Environment"

if (-not $Force) {
    Write-Warning-Custom "This will delete node_modules, dist/, and cache"
    $confirm = Read-Host "Continue? (y/N)"
    if ($confirm -ne 'y') {
        Write-Info "Cancelled"
        exit 0
    }
}

# Clean
Reset-BuildEnvironment -FrontendPath "front"

Write-Success "Cleanup complete!"
```

---

## 🔧 פתרון בעיות

### בעיה: "Cannot find ui-functions.ps1"

**פתרון:**
```powershell
# וודא שהנתיב נכון:
. "$PSScriptRoot\core\ui-functions.ps1"

# אם הסקריפט לא ב-SCRIPTS/, תקן:
$CorePath = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\SCRIPTS\core"
. "$CorePath\ui-functions.ps1"
```

---

### בעיה: Progress bar לא מופיע

**סיבה:** Terminal לא תומך ב-ANSI escape codes

**פתרון:**
```powershell
# השתמש ב-Write-Progress של PowerShell:
Write-Progress -Activity "Building" -PercentComplete 75
```

---

### בעיה: Docker functions לא עובדים

**בדיקה:**
```powershell
# וודא שDocker רץ:
docker ps

# וודא שdocker-compose זמין:
docker-compose --version
```

---

## 📊 השוואה: לפני ואחרי

### ❌ לפני (588 סקריפטים):

```powershell
# בכל סקריפט מחדש:
function Write-Success {
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Show-ProgressBar {
    # 50 שורות קוד...
}

function Test-Docker {
    # 30 שורות קוד...
}

# סה"כ: 588 סקריפטים × 100 שורות = 58,800 שורות כפילות! 😱
```

### ✅ אחרי (ספריות ליבה):

```powershell
# בכל סקריפט:
. "$PSScriptRoot\core\ui-functions.ps1"
. "$PSScriptRoot\core\docker-functions.ps1"

Write-Success "זה עובד!"
Show-ProgressBar -Activity "Build" -Percent 100
Test-DockerRunning

# סה"כ: 3 קבצי ליבה + N סקריפטים קצרים
# חיסכון: ~95% פחות קוד! 🎉
```

---

## 🚀 מה הלאה?

### סקריפטים נוספים לפיתוח:

1. **`prod-deploy.ps1`** - deployment לייצור
2. **`troubleshoot.ps1`** - פתרון בעיות אוטומטי
3. **`rollback.ps1`** - חזרה לגרסה קודמת
4. **`health-monitor.ps1`** - מעקב בזמן אמת

### תכונות נוספות:

1. **Logging** - כתיבה ללוגים אוטומטית
2. **Error Codes** - מזהים אחידים לשגיאות
3. **Auto-Fix** - תיקונים אוטומטיים
4. **Dashboard** - ממשק גרפי

---

## 📝 חוקי זהב

1. **אל תשכפל קוד** - אם אתה כותב אותו דבר פעמיים, תעביר לספרייה
2. **פונקציה אחת = משימה אחת** - כל פונקציה עושה דבר אחד טוב
3. **תיעוד ברור** - כל פונקציה עם `.SYNOPSIS` ו-`.EXAMPLE`
4. **טעינה עם dot-sourcing** - `. file.ps1` ולא `Import-Module`
5. **אל תשתמש ב-Export-ModuleMember** - זה מונע dot-sourcing

---

## 🎯 סיכום

**בנינו:**
- ✅ 3 ספריות ליבה (ui, docker, build)
- ✅ 1 סקריפט ראשי (`dev-deploy.ps1`)
- ✅ פס התקדמות יפה שאתה אוהב: `[━━━━━━━ ✓]`
- ✅ ארכיטקטורה נקייה ללא כפילויות

**התוצאה:**
- 🚀 פריסה ב-1-2 דקות (Quick mode)
- 🎨 תצוגה מקצועית
- 🧩 קל להוסיף סקריפטים חדשים
- 📦 קל לתחזוקה

---

**גרסה:** 1.0  
**תאריך:** 12 נובמבר 2025  
**סטטוס:** ✅ מוכן לשימוש
