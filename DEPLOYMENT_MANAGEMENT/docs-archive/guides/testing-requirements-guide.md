# 🔍 מדריך בדיקות וצרכים - Requirements & Testing Guide

**תאריך יצירה:** 12 נובמבר 2025  
**מטרה:** לזהות מה חסר לכל סקריפט כדי שיעבוד 100% ללא שגיאות

---

## 📋 עקרון המדריך

### מה נבדוק:
1. ✅ **Prerequisites** - מה הסקריפט צריך כדי לרוץ
2. ✅ **Dependencies** - קבצים/תיקיות שחייבים להיות
3. ✅ **Environment** - משתני סביבה, הרשאות
4. ✅ **External Tools** - Docker, npm, וכו'
5. ✅ **Configuration** - קבצי config שחייבים להיות

### איך נבדוק:
```powershell
# בדיקה מסודרת לכל סקריפט:
1. הרץ בדיקת Prerequisites
2. הרץ בדיקת Dependencies
3. נסה להריץ את הסקריפט
4. תעד מה עובד ומה לא
5. תקן את מה שחסר
6. נסה שוב
```

---

## 🎯 חלק 1: הסקריפטים הקבועים (Core Scripts)

**אלו הסקריפטים שישמשו בכל סביבת עבודה:**

### 1️⃣ `dev-deploy.ps1` - פריסה לסביבת פיתוח

#### 📦 צרכים (Requirements):

```yaml
Prerequisites:
  ✅ PowerShell 5.1 ומעלה
  ✅ הרשאות הרצה (ExecutionPolicy)
  
External Tools:
  ✅ Docker Desktop מותקן
  ✅ Docker Desktop רץ (daemon active)
  ✅ docker-compose זמין
  ✅ npm מותקן (Node.js)
  ✅ node מותקן
  
Files & Directories:
  ✅ SCRIPTS/core/ui-functions.ps1 קיים
  ✅ SCRIPTS/core/docker-functions.ps1 קיים
  ✅ SCRIPTS/core/build-functions.ps1 קיים
  ✅ eScriptorium_CLEAN/front/ קיים
  ✅ eScriptorium_CLEAN/front/package.json קיים
  ✅ docker-compose.yml קיים (בroot או ב-eScriptorium_CLEAN)
  
Docker Configuration:
  ✅ Container: escriptorium_clean-web-1 מוגדר ב-docker-compose.yml
  ✅ Volume mounts לstatic/ מוגדרים
  ✅ Ports: 8082 פנוי
  
Network:
  ⚠️ אינטרנט (לnpm install)
  ⚠️ Docker registry access (למשיכת images)
```

#### 🧪 בדיקות (Tests):

```powershell
# Test 1: Prerequisites Check
Write-Host "=== Test 1: Prerequisites ===" -ForegroundColor Cyan

# PowerShell version
$psVersion = $PSVersionTable.PSVersion
if ($psVersion.Major -ge 5) {
    Write-Host "✓ PowerShell: $psVersion" -ForegroundColor Green
} else {
    Write-Host "✗ PowerShell: $psVersion (צריך 5.1+)" -ForegroundColor Red
}

# Execution Policy
$policy = Get-ExecutionPolicy
if ($policy -ne "Restricted") {
    Write-Host "✓ ExecutionPolicy: $policy" -ForegroundColor Green
} else {
    Write-Host "✗ ExecutionPolicy: Restricted (צריך לשנות)" -ForegroundColor Red
}

# Test 2: External Tools
Write-Host "`n=== Test 2: External Tools ===" -ForegroundColor Cyan

# Docker
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker: $dockerVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Docker: לא מותקן" -ForegroundColor Red
}

# docker-compose
try {
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ docker-compose: $composeVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ docker-compose: לא זמין" -ForegroundColor Red
}

# Docker daemon
try {
    docker ps 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker daemon: Running" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Docker daemon: Not running" -ForegroundColor Red
}

# npm
try {
    $npmVersion = npm --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ npm: v$npmVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ npm: לא מותקן" -ForegroundColor Red
}

# node
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ node: $nodeVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ node: לא מותקן" -ForegroundColor Red
}

# Test 3: Files & Directories
Write-Host "`n=== Test 3: Files & Directories ===" -ForegroundColor Cyan

$requiredFiles = @(
    "SCRIPTS\core\ui-functions.ps1",
    "SCRIPTS\core\docker-functions.ps1",
    "SCRIPTS\core\build-functions.ps1",
    "eScriptorium_CLEAN\front\package.json"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ $file (חסר!)" -ForegroundColor Red
    }
}

# docker-compose.yml
$dockerComposePaths = @(
    "docker-compose.yml",
    "eScriptorium_CLEAN\docker-compose.yml"
)

$foundDockerCompose = $false
foreach ($path in $dockerComposePaths) {
    if (Test-Path $path) {
        Write-Host "✓ docker-compose.yml נמצא ב-$path" -ForegroundColor Green
        $foundDockerCompose = $true
        break
    }
}

if (-not $foundDockerCompose) {
    Write-Host "✗ docker-compose.yml לא נמצא!" -ForegroundColor Red
}

# Test 4: Docker Configuration
Write-Host "`n=== Test 4: Docker Configuration ===" -ForegroundColor Cyan

if ($foundDockerCompose) {
    $dockerComposePath = if (Test-Path "docker-compose.yml") { "docker-compose.yml" } else { "eScriptorium_CLEAN\docker-compose.yml" }
    $content = Get-Content $dockerComposePath -Raw
    
    if ($content -match "web") {
        Write-Host "✓ Service 'web' מוגדר" -ForegroundColor Green
    } else {
        Write-Host "✗ Service 'web' לא מוגדר" -ForegroundColor Red
    }
    
    if ($content -match "8082") {
        Write-Host "✓ Port 8082 מוגדר" -ForegroundColor Green
    } else {
        Write-Host "⚠ Port 8082 לא מוגדר (אולי port אחר?)" -ForegroundColor Yellow
    }
}

# Test 5: Network
Write-Host "`n=== Test 5: Network ===" -ForegroundColor Cyan

try {
    $response = Test-Connection -ComputerName "registry.npmjs.org" -Count 1 -Quiet -ErrorAction SilentlyContinue
    if ($response) {
        Write-Host "✓ npm registry נגיש" -ForegroundColor Green
    } else {
        Write-Host "⚠ npm registry לא נגיש (בדוק אינטרנט)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ לא ניתן לבדוק גישה לnpm registry" -ForegroundColor Yellow
}

Write-Host "`n=== סיכום ===" -ForegroundColor Cyan
Write-Host "אם כל הבדיקות עברו (✓), הסקריפט אמור לרוץ בהצלחה!" -ForegroundColor Green
Write-Host "אם יש ✗ או ⚠, תקן אותם לפני הרצה." -ForegroundColor Yellow
```

#### 📊 טבלת סטטוס:

| רכיב | סטטוס | הערות |
|------|-------|-------|
| PowerShell | ✅ | גרסה 5.1+ |
| Docker | ⏳ | צריך בדיקה |
| npm/node | ⏳ | צריך בדיקה |
| קבצי core | ✅ | נוצרו |
| docker-compose.yml | ⏳ | צריך מציאה |
| Container config | ⏳ | צריך בדיקה |

---

### 2️⃣ `prod-deploy.ps1` - פריסה לייצור (עתידי)

#### 📦 צרכים:

```yaml
Prerequisites:
  ✅ כל מה ש-dev-deploy.ps1 צריך +
  ✅ SSH keys (לשרת ייצור)
  ✅ הרשאות admin
  
External Tools:
  ✅ Git (לtagging)
  ✅ rsync או scp (להעברת קבצים)
  
Files & Directories:
  ✅ backup/ directory
  ✅ .env.production
  
Configuration:
  ✅ Production server details
  ✅ Backup strategy
  ✅ Rollback plan
```

**סטטוס:** ⏳ טרם נוצר

---

### 3️⃣ `troubleshoot.ps1` - פתרון בעיות (עתידי)

#### 📦 צרכים:

```yaml
Prerequisites:
  ✅ SCRIPTS/core/ui-functions.ps1
  ✅ SCRIPTS/core/docker-functions.ps1
  ✅ SCRIPTS/lib/error-codes.ps1
  
External Tools:
  ✅ Docker
  ✅ docker-compose
  
Files & Directories:
  ✅ logs/ directory (לקריאת לוגים)
  
Features:
  ✅ Error detection
  ✅ Auto-fix capabilities
  ✅ Health checks
```

**סטטוס:** ⏳ טרם נוצר

---

### 4️⃣ `health-check.ps1` - בדיקת בריאות (עתידי)

#### 📦 צרכים:

```yaml
Prerequisites:
  ✅ SCRIPTS/core/ui-functions.ps1
  ✅ SCRIPTS/core/docker-functions.ps1
  
External Tools:
  ✅ Docker
  ✅ curl או Invoke-WebRequest
  
Configuration:
  ✅ Endpoints לבדיקה
  ✅ Expected responses
  ✅ Timeout settings
```

**סטטוס:** ⏳ טרם נוצר

---

## 🚫 חלק 2: הסקריפטים הנקודתיים (לא לבדיקה שוטפת)

**אלו סקריפטים שמשמשים למשימות חד-פעמיות או setup:**

### ❌ לא לבדוק:
- `setup-project-structure.ps1` - יצירת מבנה תיקיות (חד-פעמי)
- `create-v2-structure.ps1` - יצירת V2 (חד-פעמי)
- `compare-clean-vs-v2.ps1` - השוואה (כלי עזר)
- `switch-environment.ps1` - החלפת סביבה (ניהול)
- כל הסקריפטים ב-`scripts/lib/` - מיקרו-סקריפטים (deprecated)

**סיבה:** אלו כלים, לא חלק מזרימת העבודה הרגילה.

---

## 💾 חלק 3: State Management - שמירת מצב והמשך מנקודת כשלון

### ✅ כן! יישמנו את זה!

**איפה זה כבר קיים:**
- `SCRIPTS/lib/state-manager.ps1` - ניהול state
- `.deployment_state.json` - קובץ המצב

**איך זה עובד:**

```powershell
# 1. הגדרת שלבים
$steps = @(
    "CheckPrerequisites",
    "BuildFrontend",
    "DeployToDocker",
    "RestartServices",
    "Verify"
)

# 2. שמירת התקדמות
Set-DeploymentStep -Step "BuildFrontend" -Status "InProgress"

# 3. אם נכשל - שמור איפה
Set-DeploymentStep -Step "BuildFrontend" -Status "Failed" -Error $errorMessage

# 4. בריצה הבאה - המשך מאיפה שנפסק
$lastStep = Get-LastCompletedStep
if ($lastStep) {
    Write-Info "Resuming from: $lastStep"
    # דלג על שלבים שכבר הצליחו
}
```

### 🔧 הוספה ל-`dev-deploy.ps1`:

אוסיף את state management לסקריפט הקיים!

---

## 📋 חלק 4: Checklist מסודר לביצוע

### שלב 1: בדיקות ראשוניות (10 דק')

```powershell
# הרץ את סקריפט הבדיקה:
.\SCRIPTS\check-requirements.ps1

# צפי:
# - ✓✓✓ הכל ירוק → המשך
# - ✗✗✗ יש אדומים → תקן ראשון
```

### שלב 2: תיקון חסרים (זמן משתנה)

```yaml
אם Docker לא רץ:
  → הפעל Docker Desktop
  → המתן לאתחול
  
אם npm חסר:
  → התקן Node.js מ-https://nodejs.org
  
אם docker-compose.yml לא נמצא:
  → בדוק היכן הוא נמצא
  → עדכן את $DockerComposePath בסקריפט
```

### שלב 3: ריצה ראשונה (5-10 דק')

```powershell
# ריצה ראשונה עם state management:
.\SCRIPTS\dev-deploy.ps1 -Quick

# אם נכשל באמצע:
# המצב נשמר ב-.deployment_state.json
```

### שלב 4: המשך מנקודת כשלון (2-5 דק')

```powershell
# הסקריפט יזהה אוטומטית את המצב השמור:
.\SCRIPTS\dev-deploy.ps1 -Resume

# או ידנית:
.\SCRIPTS\dev-deploy.ps1 -StartFrom "RestartServices"
```

### שלב 5: אימות (2 דק')

```powershell
# וידוא שהכל עובד:
.\SCRIPTS\dev-deploy.ps1 -VerifyOnly

# צפי:
# ✓ Container: Running
# ✓ Container: Healthy
# ✓ Services: Up
```

---

## 📊 טבלת מעקב - מה עובד ומה לא

### Core Scripts:

| סקריפט | Prerequisites | Files | Docker | npm | Network | State Mgmt | סטטוס כללי |
|---------|--------------|-------|--------|-----|---------|------------|------------|
| `dev-deploy.ps1` | ⏳ | ✅ | ⏳ | ⏳ | ⏳ | ⏳ | **צריך בדיקה** |
| `prod-deploy.ps1` | - | - | - | - | - | - | **לא נוצר** |
| `troubleshoot.ps1` | - | - | - | - | - | - | **לא נוצר** |
| `health-check.ps1` | - | - | - | - | - | - | **לא נוצר** |

### Core Libraries:

| ספרייה | קיים | תקין | מתועד | נבדק |
|--------|------|------|-------|------|
| `ui-functions.ps1` | ✅ | ✅ | ✅ | ⏳ |
| `docker-functions.ps1` | ✅ | ✅ | ✅ | ⏳ |
| `build-functions.ps1` | ✅ | ✅ | ✅ | ⏳ |

---

## 🎯 התוכנית להמשך

### עכשיו (הבא):
1. ✅ צור `check-requirements.ps1` - סקריפט בדיקה אוטומטי
2. ✅ הוסף State Management ל-`dev-deploy.ps1`
3. ✅ הרץ בדיקה מלאה
4. ✅ תקן מה שלא עובד
5. ✅ עדכן טבלת מעקב

### אחר כך:
1. בנה `prod-deploy.ps1`
2. בנה `troubleshoot.ps1`
3. בנה `health-check.ps1`
4. בדיקות end-to-end

---

## 💡 טיפים לבדיקה

### טיפ 1: הרץ בדיקות לפני כל שינוי
```powershell
# לפני שמשנים משהו:
.\SCRIPTS\check-requirements.ps1 > before.txt

# אחרי שינוי:
.\SCRIPTS\check-requirements.ps1 > after.txt

# השווה:
Compare-Object (Get-Content before.txt) (Get-Content after.txt)
```

### טיפ 2: שמור לוגים
```powershell
# כל ריצה עם לוג:
.\SCRIPTS\dev-deploy.ps1 -Quick 2>&1 | Tee-Object -FilePath "logs\deploy-$(Get-Date -f 'yyyyMMdd-HHmmss').log"
```

### טיפ 3: בדוק state אחרי כשלון
```powershell
# ראה מה המצב:
Get-Content .deployment_state.json | ConvertFrom-Json | Format-List
```

---

**מוכן? בוא נתחיל בבדיקות! 🚀**

אני יכול ליצור:
1. ✅ `check-requirements.ps1` - סקריפט בדיקה מלא
2. ✅ להוסיף State Management ל-`dev-deploy.ps1`
3. ✅ להריץ בדיקה ראשונה

**מה תרצה שאעשה תחילה?**
