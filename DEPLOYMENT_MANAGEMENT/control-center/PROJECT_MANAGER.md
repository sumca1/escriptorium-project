# 🎯 מנהל פרויקט - Control Center Dashboard
**מערכת ניהול מקיפה עבור לוח הבקרה של BiblIA**

---

## 📋 סקירה כללית

**מטרת הפרויקט:** לוח בקרה מרכזי לניהול פרויקט BiblIA eScriptorium

**מיקום:** `escriptorium/DEPLOYMENT_MANAGEMENT/control-center/`

**שרת:** `http://localhost:8080/dashboard.html`

---

## 🏗️ ארכיטקטורה

### מבנה תיקיות

```
control-center/
│
├── 📁 app/                          ← ממשק משתמש
│   ├── dashboard.html              ← דף ראשי (טאבים)
│   └── index.html                  ← דף נחיתה
│
├── 📁 modules/                      ← מודולים של הטאבים
│   ├── overview.js                 ← מבט כללי ✅
│   ├── docker.js                   ← ניהול Docker
│   ├── build.js                    ← מערכת Build
│   ├── deploy.js                   ← Deploy & Release
│   ├── files.js                    ← מעקב קבצים ✅
│   ├── logs.js                     ← לוגים
│   ├── errors.js                   ← ניהול שגיאות
│   ├── scripts.js                  ← הרצת סקריפטים
│   ├── terminal.js                 ← טרמינל מובנה
│   ├── sync.js                     ← סנכרון ✅
│   ├── docs-improved.js            ← מערכת תיעוד ✅✅✅
│   ├── data-loader.js              ← טעינת נתונים ✅
│   ├── file-watcher.js             ← מעקב אחר שינויים ✅
│   ├── terminal-config.js          ← הגדרות טרמינל
│   └── markdown-converter.js       ← המרת Markdown
│
├── 📁 servers/                      ← שרתים
│   ├── dashboard-server.js         ← שרת Dashboard (8080) ✅
│   └── terminal-server.js          ← שרת Terminal (3001)
│
├── 📁 scripts/                      ← סקריפטי ניהול
│   ├── START_DASHBOARD.bat         ← הפעלה מהירה ✅
│   └── utilities/
│       └── sync-docs-to-dashboard.ps1  ← סנכרון מסמכים ✅
│
├── 📁 docs/                         ← מסמכי תיעוד
│   ├── SESSION_LOG.md              ← תיעוד סשנים ✅
│   ├── CURRENT_STATE.md            ← מצב נוכחי ✅
│   ├── CONTROL_CENTER_PLAN.md      ← תכנון
│   └── README_*.md                 ← מדריכים
│
├── 📁 data/                         ← קבצי נתונים
│   └── system-state.json
│
└── 📁 logs/                         ← לוגים
    └── (נוצרים אוטומטית)
```

---

## 🎨 טאבים במערכת

### ✅ טאבים פעילים

| טאב | תיאור | סטטוס | קובץ |
|-----|-------|-------|------|
| **מבט כללי** | סטטיסטיקות ולינקים מהירים | ✅ פעיל | `overview.js` |
| **קבצים** | מעקב אחר שינויים בקבצים | ✅ פעיל | `files.js` |
| **סנכרון** | סנכרון environments | ✅ פעיל | `sync.js` |
| **תיעוד** | צפייה במסמכים (TOC, Search, Links) | ✅✅✅ מלא | `docs-improved.js` |

### ⚠️ טאבים בפיתוח

| טאב | תיאור | סטטוס | פעולה נדרשת |
|-----|-------|-------|-------------|
| **Dashboard** | ראשי - מידע על מערכת | 🚧 חסר | צריך ליצור `dashboard.js` |
| **Docker** | ניהול containers | 🚧 חלקי | צריך לחבר Terminal Server |
| **Build** | מערכת build | 🚧 חלקי | אינטגרציה עם scripts |
| **Deploy** | פריסה לסביבות | 🚧 חלקי | חיבור לסקריפטים |
| **Logs** | צפייה בלוגים | 🚧 חלקי | קריאה מ-`logs/` |
| **Errors** | ניהול שגיאות | 🚧 חלקי | מערכת tracking |
| **Scripts** | הרצת סקריפטים | 🚧 חלקי | אינטגרציה עם Terminal |
| **Terminal** | טרמינל מובנה | 🚧 חלקי | תלוי ב-Terminal Server |

---

## 🔧 רכיבים טכניים

### שרתים

#### Dashboard Server (port 8080)
- **קובץ:** `servers/dashboard-server.js`
- **מטרה:** מגיש את כל ממשק הדשבורד
- **נתיבים:**
  - `/` → `dashboard.html`
  - `/app/*` → קבצי HTML/JS/CSS
  - `/modules/*` → מודולי JavaScript
  - `/docs/*` → מסמכי תיעוד
  - `/project-docs/*` → מסמכי פרויקט
- **סטטוס:** ✅ פעיל

#### Terminal Server (port 3001)
- **קובץ:** `servers/terminal-server.js`
- **מטרה:** הרצת פקודות shell מהדשבורד
- **API:**
  - `POST /execute` - הרצת פקודה
  - `GET /status` - סטטוס שרת
- **סטטוס:** ⚠️ פועל אבל חסר `/execute` endpoint

---

### מערכת נתונים

#### data-loader.js
**מה הוא עושה:**
- טוען `SESSION_LOG.md` ו-`CURRENT_STATE.md`
- מנתח Docker status (סטטי כרגע)
- Cache חכם (30 שניות TTL)

**נתיבים:**
- ✅ `docs/SESSION_LOG.md`
- ✅ `docs/CURRENT_STATE.md`
- ❌ `.file-changes-state.json` (לא קיים)

---

### מערכת File Watcher

#### file-watcher.js
**מה הוא עושה:**
- עוקב אחר שינויים בקבצים
- Hash-based comparison (Last-Modified)
- רענון אוטומטי רק בשינוי

**קבצים במעקב:**
- ✅ `docs/SESSION_LOG.md`
- ✅ `docs/CURRENT_STATE.md`

**תכונות:**
- 🔄 בדיקה כל 2 שניות
- 🎯 Callback על שינוי
- 🛑 Stop/Start/Change Interval

---

### מערכת תיעוד (docs-improved.js)

**התכונות המלאות:**
- ✅ **TOC Sidebar** - ניווט היררכי עם 6 רמות
- ✅ **Level Filter** - סינון לפי רמת כותרת (1-6)
- ✅ **Expand/Collapse** - ◀/▼ arrows
- ✅ **In-document Search** - חיפוש עם הדגשה
- ✅ **Document Cross-linking** - לינקים אוטומטיים בין מסמכים
- ✅ **Smart File Discovery** - מציאה אוטומטית של קבצים
- ✅ **Scroll Spy** - מעקב אחר מיקום בדף
- ✅ **Markdown Rendering** - עם syntax highlighting
- ✅ **Mobile Responsive** - TOC מתקפל

**קבצים:**
- `docs-improved.js` - 2176+ שורות
- `markdown-converter.js` - המרת MD→HTML

---

## 📝 סקריפטים

### sync-docs-to-dashboard.ps1
**מיקום:** `scripts/utilities/sync-docs-to-dashboard.ps1`

**מה הוא עושה:**
```powershell
# מעתיק מסמכים מהפרויקט לדשבורד
BiblIA_dataset/SESSION_LOG.md → control-center/docs/SESSION_LOG.md
BiblIA_dataset/CURRENT_STATE.md → control-center/docs/CURRENT_STATE.md
```

**מצבי הפעלה:**
- סנכרון חד-פעמי: `.\sync-docs-to-dashboard.ps1`
- מצב Watch: `.\sync-docs-to-dashboard.ps1 -Watch`
- כפה סנכרון: `.\sync-docs-to-dashboard.ps1 -Force`

**אינטגרציה:**
- ✅ רץ אוטומטית ב-`START_DASHBOARD.bat`

---

### START_DASHBOARD.bat
**מיקום:** `scripts/START_DASHBOARD.bat`

**תהליך הפעלה:**
```
[1/3] Syncing documentation files...
      ↓
      sync-docs-to-dashboard.ps1
      
[2/3] Starting servers...
      ↓
      Terminal Server (port 3001) ← חלון נפרד
      Dashboard Server (port 8080) ← רקע
      
[3/3] Opening Dashboard in browser...
      ↓
      http://localhost:8080/dashboard.html
```

---

## 🚀 מערכת הפעלה מתקדמת

### auto-start-terminal-server.ps1
**מיקום:** `scripts/utilities/auto-start-terminal-server.ps1`  
**גודל:** 288 שורות  
**גרסה:** Clean Edition (12 נובמבר 2025)

**תכונות מרכזיות:**

#### 1️⃣ **בחירת פורט חכמה**
```powershell
# אם פורט 3001 תפוס, מחפש פורט זמין אוטומטית
$Port = 3001
while (-not (Test-PortAvailable -PortNumber $Port)) {
    $Port++
}
```

#### 2️⃣ **מצבי הפעלה**

| פרמטר | תיאור | דוגמה |
|-------|-------|-------|
| `-Port` | בחירת פורט מותאם | `.\auto-start-terminal-server.ps1 -Port 4000` |
| `-Silent` | ללא הודעות (רקע) | `.\auto-start-terminal-server.ps1 -Silent` |
| `-NoBrowser` | ללא פתיחת דפדפן | `.\auto-start-terminal-server.ps1 -NoBrowser` |

#### 3️⃣ **בדיקות אוטומטיות**
- ✅ בדיקת קיום `start-terminal-server.ps1` (הסקריפט הראשי)
- ✅ בדיקת קיום `dashboard.html`
- ✅ בדיקת זמינות פורט
- ✅ מציאת נתיבים אוטומטית (5 levels up navigation)

#### 4️⃣ **תהליך ההפעלה**
```
1. מוצא נתיבים:
   - BiblIA_dataset/ (root)
   - start-terminal-server.ps1 (הסקריפט הראשי)
   - dashboard.html (הממשק)

2. בודק זמינות פורט:
   - מנסה 3001
   - אם תפוס → מנסה 3002, 3003... (עד 10 ניסיונות)

3. מפעיל שרתים:
   - Terminal Server (חלון נפרד)
   - Dashboard Server (רקע)

4. פותח דפדפן:
   - http://localhost:8080/dashboard.html
   - (אלא אם -NoBrowser)
```

#### 5️⃣ **דוגמאות שימוש**

**הפעלה רגילה:**
```powershell
cd scripts\utilities
.\auto-start-terminal-server.ps1
```

**הפעלה שקטה (רקע):**
```powershell
.\auto-start-terminal-server.ps1 -Silent -NoBrowser
```

**פורט מותאם:**
```powershell
.\auto-start-terminal-server.ps1 -Port 4000
```

**שילוב כל האפשרויות:**
```powershell
.\auto-start-terminal-server.ps1 -Port 5000 -Silent -NoBrowser
```

---

### start-terminal-server.bat
**מיקום:** `scripts/start-terminal-server.bat`  
**מטרה:** Wrapper נוח ל-Windows

**תוכן:**
```batch
@echo off
cd /d "%~dp0utilities"
powershell -ExecutionPolicy Bypass -File auto-start-terminal-server.ps1
pause
```

**שימוש:**
- לחיצה כפולה על הקובץ → הכל מתנהל אוטומטית!

---

### 🎯 מדריכי הפעלה קיימים

| מדריך | גודל | תוכן | מיקום |
|-------|------|------|--------|
| **HOW_TO_START.md** | מפורט | הפעלה אוטומטית + ידנית | `docs/HOW_TO_START.md` |
| **START_HERE.md** | מקיף | מדריך מלא עם אפשרויות | `docs/START_HERE.md` |

---

## 🎯 משימות עתידיות

### 🔴 עדיפות גבוהה

1. **תיקון Terminal Server**
   - הוסף `/execute` endpoint
   - תמיכה ב-POST requests
   - טיפול בפקודות async

2. **Dashboard Module**
   - צור `modules/dashboard.js`
   - מידע על מערכת
   - גרפים וסטטיסטיקות

3. **Docker Integration**
   - חבר ל-Terminal Server המתוקן
   - הצג containers בזמן אמת
   - Start/Stop/Restart פקודות

### 🟡 עדיפות בינונית

4. **Build System Integration**
   - חיבור לסקריפטי build
   - Progress bar בזמן אמת
   - Log streaming

5. **Deploy Module**
   - בחירת environment (dev/test/prod)
   - Deploy workflow
   - Rollback capability

6. **Logs Viewer**
   - קריאה מ-`logs/`
   - Live tail
   - סינון ו-Search

### 🟢 עדיפות נמוכה

7. **Error Tracking**
   - ניהול שגיאות ידועות
   - פתרונות מומלצים
   - Knowledge base

8. **Scripts Runner**
   - רשימת סקריפטים זמינים
   - הרצה ישירה מהדשבורד
   - שמירת היסטוריה

9. **Advanced Analytics**
   - Build times tracking
   - Success/failure rates
   - Performance metrics

---

## 🔐 אבטחה

### הרשאות גישה
- 🔒 **Local only** - השרת מקשיב רק על `localhost`
- 🔒 **No authentication** - מיועד לסביבת פיתוח מקומית
- 🔒 **File system access** - מוגבל לנתיבים מוגדרים

### המלצות
- ❌ אל תחשוף את השרת לאינטרנט
- ✅ השתמש רק ב-localhost
- ✅ הרץ כמשתמש רגיל (לא admin)

---

## 📊 מדדי הצלחה

### טאבים פעילים: 4/12 (33%)
- ✅ Overview
- ✅ Files
- ✅ Sync
- ✅ Docs

### רכיבים תשתיתיים: 5/7 (71%)
- ✅ Dashboard Server
- ✅ Data Loader
- ✅ File Watcher
- ✅ Docs System
- ✅ Sync Script
- ⚠️ Terminal Server (חלקי)
- ❌ Error Tracking

---

## 🚀 מדריך מהיר

### להתחיל לעבוד:

1. **הפעל את הדשבורד:**
   ```bash
   cd escriptorium/DEPLOYMENT_MANAGEMENT/control-center/scripts
   START_DASHBOARD.bat
   ```

2. **עדכן מסמכים:**
   ```bash
   # ערוך SESSION_LOG.md או CURRENT_STATE.md בשורש הפרויקט
   # ואז:
   cd scripts/utilities
   .\sync-docs-to-dashboard.ps1
   ```

3. **פתח בדפדפן:**
   ```
   http://localhost:8080/dashboard.html
   ```

---

## 📞 תמיכה ותיעוד

### מסמכים נוספים:
- `docs/CONTROL_CENTER_PLAN.md` - תכנון מפורט
- `docs/DASHBOARD_GUIDE.md` - מדריך שימוש
- `scripts/utilities/README_SYNC_DOCS.md` - מדריך סנכרון

### קבצי הגדרות:
- `app/dashboard.html` - הגדרות טאבים ו-UI
- `modules/terminal-config.js` - הגדרות Terminal Server
- `servers/dashboard-server.js` - הגדרות שרת

---

## 🏆 הישגים עד כה

### ✅ הושלם
- ✨ מערכת תיעוד מלאה עם TOC/Search/Links
- ✨ סנכרון אוטומטי של מסמכים
- ✨ File Watcher חכם
- ✨ טאב Overview עם נתונים מ-SESSION_LOG
- ✨ ממשק נקי וייעודי

### 🚧 בתהליך
- Terminal Server endpoint `/execute`
- Docker real-time integration
- Build system UI

### 📋 מתוכנן
- Error tracking system
- Scripts runner UI
- Advanced analytics

---

**גרסה:** 1.0  
**תאריך:** 13 נובמבר 2025  
**סטטוס:** 🟢 פעיל - Control Center Dashboard
**מתחזק:** BiblIA Team
