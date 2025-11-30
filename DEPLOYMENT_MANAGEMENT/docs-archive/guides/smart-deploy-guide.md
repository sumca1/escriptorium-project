# 📘 מדריך Smart Deploy V2

## 🎯 מה זה?

**מערכת סקריפטים מודולרית וחכמה** עם:
- ✅ פס התקדמות צבעוני (אדום/צהוב/ירוק)
- ✅ שמירת מצב - המשך מנקודת כשלון
- ✅ בדיקות מקדימות אוטומטיות
- ✅ מודולרי - קטן + גדול

---

## 📁 מבנה הקבצים

```
SCRIPTS/
├── smart-deploy-v2.ps1          ← סקריפט ראשי
├── lib/
│   ├── progress-bar.ps1         ← פס התקדמות
│   ├── state-manager.ps1        ← שמירת מצב
│   ├── check-docker.ps1         ← בדיקת Docker
│   ├── check-source.ps1         ← בדיקת SOURCE
│   ├── check-environment.ps1    ← בדיקת סביבה
│   └── build-image.ps1          ← בניית image
```

---

## 🚀 שימוש

### 1️⃣ Build + Up (פעם ראשונה)

```powershell
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Build -Up
```

**מה זה עושה:**
```
שלב 1/6: בדיקת Docker
  ✅ Docker מותקן
  ✅ Docker רץ
  
שלב 2/6: בדיקת SOURCE
  ✅ SOURCE/ קיים
  ✅ app/ קיים
  
שלב 3/6: בדיקת סביבה
  ✅ docker-compose.yml קיים
  
שלב 4/6: בניית image
  🔨 בונה...
  ✅ Build הצליח! (45s)
  
שלב 5/6: הפעלת containers
  ✅ Containers הופעלו
  
שלב 6/6: אימות
  ✅ הכל רץ
  
╔════════════════════════════════════╗
║      ✅ הושלם! ⏱️  52s            ║
╚════════════════════════════════════╝
🌐 http://localhost:8000
```

---

### 2️⃣ המשך מכשלון (Resume)

נניח build נכשל:

```powershell
# נכשל בשלב 4/6
❌ נכשל בשלב 4: בניית image
💥 requirements.txt: not found
💡 הרץ: .\smart-deploy-v2.ps1 -Environment dev -Resume
```

תקן את הבעיה (תקן Dockerfile), ואז:

```powershell
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Resume
```

**מה זה עושה:**
```
🔄 ממשיך...

📊 מצב:
  ✅ שלב 1: בדיקת Docker
  ✅ שלב 2: בדיקת SOURCE
  ✅ שלב 3: בדיקת סביבה
  ⏳ שלב 4: בניית image ← כאן נעצרנו
  ⏳ שלב 5: הפעלת containers
  ⏳ שלב 6: אימות
  
▶️  ממשיך משלב 4...

שלב 4/6: בניית image
  🔨 בונה...
  ✅ Build הצליח! (42s)
  
... ממשיך עם שלב 5, 6
```

**תוצאה:** לא התחלת מהתחלה! ⚡

---

### 3️⃣ הצגת מצב

```powershell
.\SCRIPTS\smart-deploy-v2.ps1 -ShowState
```

**פלט:**
```
╔═══════════════════════════════════════╗
║   📊 מצב Deployment - dev            ║
╚═══════════════════════════════════════╝

סטטוס: 🔄 רץ
התקדמות: 4 / 6

שלבים:
  ✅ 1. בדיקת Docker
     ⏱️  0.8s
  ✅ 2. בדיקת SOURCE
     ⏱️  0.3s
  ✅ 3. בדיקת סביבה
     ⏱️  0.5s
  ❌ 4. בניית image
     💥 requirements.txt: not found
  ⏳ 5. הפעלת containers
  ⏳ 6. אימות

⚠️  שגיאות:
  • requirements.txt: not found
```

---

### 4️⃣ איפוס מצב

```powershell
.\SCRIPTS\smart-deploy-v2.ps1 -Reset
```

מחק את המצב השמור, התחל מחדש.

---

## 🎨 פס התקדמות

```
╔══════════════════════════════════════════════════════╗
║ ████████████████████████░░░░░░░░░░░░░░░░  60%       ║
║ ⏱️  00:45 / ~01:15 נותרו                             ║
║ 🔨 בונה Docker image...                             ║
╚══════════════════════════════════════════════════════╝
```

**צבעים:**
- 🟢 ירוק = הצלחה
- 🟡 צהוב = מתבצע
- 🔴 אדום = כשלון

---

## 🔧 Micro-Scripts (שימוש ישיר)

### בדיקת Docker

```powershell
. .\SCRIPTS\lib\check-docker.ps1
Assert-DockerReady
```

### בדיקת SOURCE

```powershell
. .\SCRIPTS\lib\check-source.ps1
Assert-SourceReady -ProjectRoot "I:\...\BiblIA_dataset"
```

### בניית Image

```powershell
. .\SCRIPTS\lib\build-image.ps1
Build-DockerImageSmart -Environment dev -EnvPath "I:\...\ENVIRONMENTS\dev"
```

---

## 📊 State File

הקובץ: `.deployment_state.json`

```json
{
  "environment": "dev",
  "startTime": "2025-11-12T13:45:00",
  "steps": [
    {
      "name": "בדיקת Docker",
      "status": "completed",
      "duration": 0.8
    },
    {
      "name": "בניית image",
      "status": "failed",
      "error": "requirements.txt: not found"
    }
  ],
  "currentStep": 3,
  "totalSteps": 6,
  "status": "failed"
}
```

---

## 💡 טיפים

### טיפ 1: Build מהיר

אם Image כבר קיים ולא השתנה:

```powershell
# יבדוק אוטומטית ויד

לג על build
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Build -Up

# פלט:
🧠 בודק אם צריך build...
  ✅ Image עדכני - דילוג על build
```

### טיפ 2: Down מהיר

```powershell
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Down
```

### טיפ 3: שימוש חוזר

```powershell
# build פעם אחת
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Build

# up/down כמה שרוצים
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Up
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Down
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Up
```

---

## 🎯 תרחישים נפוצים

### תרחיש 1: התחלה ראשונה

```powershell
# 1. הכן מבנה
.\SCRIPTS\setup-project-structure.ps1

# 2. build + up
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Build -Up

# 3. עבוד!
```

### תרחיש 2: שינוי בקוד

```powershell
# ערכת views.py ב-SOURCE/
# dev mount אותו אוטומטית - רענן דפדפן!
# אין build!
```

### תרחיש 3: שינוי ב-Dockerfile

```powershell
# 1. ערכת Dockerfile
# 2. build מחדש
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Build

# 3. restart
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Down
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Up
```

### תרחיש 4: build נכשל

```powershell
# 1. build נכשל
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Build -Up
# ❌ נכשל בשלב 4

# 2. הצג מצב
.\SCRIPTS\smart-deploy-v2.ps1 -ShowState

# 3. תקן בעיה

# 4. המשך
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Resume
```

---

## 🔗 חיבור למרכז הבקרה

ראה: `DASHBOARD_INTEGRATION.md`

---

**גרסה:** 2.0  
**תאריך:** 12 נובמבר 2025
