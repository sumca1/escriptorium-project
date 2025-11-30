# 🏗️ ארכיטקטורת סקריפטים - Script Architecture

## 📐 עיקרון: Hierarchical Modular Design

```
סקריפטים ראשיים (Master Scripts)
         ↓
חבילות משימות (Task Packages)
         ↓
Micro-Scripts (lib/)
```

---

## 🎯 רמה 1: Master Scripts (5 סקריפטים ראשיים)

### 1. `deploy-master.ps1` - מאסטר כללי
```powershell
# שימוש:
.\SCRIPTS\deploy-master.ps1 -Action [action] -Environment [env]

# Actions:
- setup      → התקנה ראשונית מלאה
- build      → build בלבד
- deploy     → deploy בלבד
- full       → build + deploy + test
- restart    → restart services
- cleanup    → ניקוי
```

**מה הוא מריץ:**
- setup → setup-master.ps1
- build → build-master.ps1
- deploy → deploy-master.ps1 (ספציפי)
- full → build-master + deploy-master + verify-master

---

### 2. `setup-master.ps1` - התקנה ראשונית
```powershell
# שימוש:
.\SCRIPTS\setup-master.ps1 [-Full] [-QuickCheck]

# מה הוא עושה:
1. בדיקת דרישות (check-prerequisites.ps1)
2. יצירת מבנה (setup-project-structure.ps1)
3. העתקת SOURCE (copy-source-files.ps1)
4. יצירת .env files (create-env-files.ps1)
5. אימות (verify-setup.ps1)
```

**מריץ:**
- lib/check-docker.ps1
- lib/check-source.ps1
- auto-fix/setup-source-directory.ps1
- auto-fix/create-docker-compose.ps1
- auto-fix/create-dockerfile.ps1

---

### 3. `build-master.ps1` - בניית Images
```powershell
# שימוש:
.\SCRIPTS\build-master.ps1 -Environment [dev|test|prod] [-Force]

# מה הוא עושה:
1. בדיקת SOURCE (lib/check-source.ps1)
2. בדיקת environment (lib/check-environment.ps1)
3. בניית image (lib/build-image.ps1)
4. אימות build (verify-build.ps1)
```

**מריץ:**
- lib/check-source.ps1
- lib/check-environment.ps1
- lib/build-image.ps1
- lib/state-manager.ps1
- lib/progress-bar.ps1

---

### 4. `deploy-master.ps1` - הפעלת Containers
```powershell
# שימוש:
.\SCRIPTS\deploy-master.ps1 -Environment [dev|test|prod] [-Up | -Down | -Restart]

# מה הוא עושה:
1. בדיקת Docker (lib/check-docker.ps1)
2. הפעלת containers (docker-compose up)
3. בדיקת health (verify-containers.ps1)
4. הרצת migrations (run-migrations.ps1 - אם צריך)
```

**מריץ:**
- lib/check-docker.ps1
- auto-fix/start-postgres.ps1
- auto-fix/run-migrations.ps1

---

### 5. `troubleshoot-master.ps1` - פתרון בעיות
```powershell
# שימוש:
.\SCRIPTS\troubleshoot-master.ps1 [-AutoFix] [-ErrorCode ERR_XXXX]

# מה הוא עושה:
1. סריקת שגיאות (scan-errors.ps1)
2. זיהוי error codes (lib/error-codes.ps1)
3. הצעת תיקונים
4. ביצוע auto-fix (אם ניתן)
```

**מריץ:**
- lib/error-codes.ps1
- auto-fix/*.ps1 (לפי הצורך)

---

## 📦 רמה 2: Task Packages (חבילות משימות)

### Package 1: Setup Tasks
```
setup-project-structure.ps1
copy-source-files.ps1
create-env-files.ps1
verify-setup.ps1
```

### Package 2: Build Tasks
```
prepare-build.ps1
build-frontend.ps1
build-backend.ps1
verify-build.ps1
```

### Package 3: Deploy Tasks
```
start-containers.ps1
verify-containers.ps1
run-migrations.ps1
collectstatic.ps1
```

### Package 4: Maintenance Tasks
```
cleanup-volumes.ps1
cleanup-images.ps1
backup-db.ps1
restore-db.ps1
```

### Package 5: Troubleshooting Tasks
```
scan-errors.ps1
diagnose-docker.ps1
diagnose-build.ps1
diagnose-deploy.ps1
```

---

## 🔧 רמה 3: Micro-Scripts (lib/)

### קיימים כבר:
```
lib/progress-bar.ps1         ← פס התקדמות
lib/state-manager.ps1        ← ניהול מצב
lib/check-docker.ps1         ← בדיקת Docker
lib/check-source.ps1         ← בדיקת SOURCE
lib/check-environment.ps1    ← בדיקת Environment
lib/build-image.ps1          ← בניית Images
lib/error-codes.ps1          ← מערכת Error Codes
```

### חדשים:
```
lib/docker-helpers.ps1       ← פונקציות עזר Docker
lib/file-helpers.ps1         ← פונקציות עזר קבצים
lib/json-helpers.ps1         ← פונקציות עזר JSON
lib/logging.ps1              ← מערכת לוגים
```

---

## 🩹 רמה 4: Auto-Fix Scripts (auto-fix/)

### תיקונים אוטומטיים:
```
auto-fix/fix-docker-not-running.ps1
auto-fix/fix-container-already-running.ps1
auto-fix/setup-source-directory.ps1
auto-fix/copy-app-to-source.ps1
auto-fix/copy-front-to-source.ps1
auto-fix/fix-requirements-path.ps1
auto-fix/fix-npm-install.ps1
auto-fix/create-docker-compose.ps1
auto-fix/create-dockerfile.ps1
auto-fix/create-env-file.ps1
auto-fix/start-postgres.ps1
auto-fix/run-migrations.ps1
```

---

## 🎮 דוגמאות שימוש

### התקנה ראשונית (פעם אחת):
```powershell
.\SCRIPTS\setup-master.ps1 -Full
```

### Build סביבת dev:
```powershell
.\SCRIPTS\build-master.ps1 -Environment dev
```

### Deploy + Start:
```powershell
.\SCRIPTS\deploy-master.ps1 -Environment dev -Up
```

### Workflow מלא (build + deploy + verify):
```powershell
.\SCRIPTS\deploy-master.ps1 -Action full -Environment dev
```

### פתרון בעיה:
```powershell
# סריקה אוטומטית
.\SCRIPTS\troubleshoot-master.ps1 -AutoFix

# תיקון שגיאה ספציפית
.\SCRIPTS\troubleshoot-master.ps1 -ErrorCode ERR_3001 -AutoFix
```

### Cleanup:
```powershell
.\SCRIPTS\deploy-master.ps1 -Action cleanup
```

---

## 📊 תרשים זרימה

```
משתמש מריץ:
  .\SCRIPTS\deploy-master.ps1 -Action full -Environment dev
          ↓
deploy-master.ps1 קורא:
  - Action = full
  - Environment = dev
          ↓
מריץ ברצף:
  1. build-master.ps1 -Environment dev
          ↓ מריץ:
          - lib/check-source.ps1
          - lib/check-environment.ps1
          - lib/build-image.ps1
          ↓
  2. deploy-master.ps1 -Environment dev -Up
          ↓ מריץ:
          - lib/check-docker.ps1
          - start-containers.ps1
          - verify-containers.ps1
          ↓
  3. verify-master.ps1 -Environment dev
          ↓ מריץ:
          - verify-build.ps1
          - verify-containers.ps1
          - run-migrations.ps1 (אם צריך)
          ↓
          ✅ הושלם!
```

---

## 🎯 יתרונות הארכיטקטורה

### ✅ פשטות למשתמש
- 5 סקריפטים ראשיים בלבד!
- שמות ברורים: setup, build, deploy, troubleshoot
- פרמטרים אחידים

### ✅ גמישות למפתח
- Micro-scripts ניתנים לשימוש חוזר
- קל להוסיף תכונות חדשות
- קל לתחזק

### ✅ Resumable
- כל master script משתמש ב-state-manager
- אפשר ל-resume מכל נקודה

### ✅ Troubleshooting חכם
- מערכת error codes
- auto-fix אוטומטי
- הצעות תיקון ברורות

### ✅ ממשק בקרה פשוט
- 5 כפתורים ראשיים בדשבורד
- רשימת error codes
- מדריכים מוטמעים

---

## 🔮 מיפוי לממשק בקרה

### כפתורים ראשיים:
```html
[🚀 Setup]      → setup-master.ps1 -Full
[🔨 Build]      → build-master.ps1 -Environment dev
[▶️  Deploy]     → deploy-master.ps1 -Environment dev -Up
[🔄 Restart]    → deploy-master.ps1 -Environment dev -Restart
[🩹 Fix Issues] → troubleshoot-master.ps1 -AutoFix
```

### רשימת Scripts זמינה:
- Setup Tasks (4)
- Build Tasks (4)
- Deploy Tasks (4)
- Maintenance Tasks (4)
- Troubleshooting Tasks (5)

### רשימת Error Codes:
- Docker (ERR_1001-1004)
- SOURCE (ERR_2001-2003)
- Build (ERR_3001-3003)
- Environment (ERR_4001-4003)
- Database (ERR_5001-5002)

---

**גרסה:** 1.0  
**תאריך:** 12 נובמבר 2025  
**סטטוס:** 📐 Architecture Design
