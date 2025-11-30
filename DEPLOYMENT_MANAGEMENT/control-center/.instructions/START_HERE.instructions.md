---
description: נקודת כניסה יחידה לכל צ'אטבוט AI - Control Center Dashboard
applyTo: '**'
---

# 🚀 התחל כאן - Control Center Dashboard

**⚡ יש לך 3 קבצים לקרוא - זה הכל!**

---

## 📚 3 קבצי הוראות מרכזיים:

### 1️⃣ **START_HERE.instructions.md** ← אתה כאן! (5 דק')
**מה:** נקודת כניסה - flow בסיסי + חוקים

### 2️⃣ **PRIORITY_RULES.instructions.md** (3 דק')
**מה:** חוקי עדיפות - Critical/High/Medium - זמן = כסף!

### 3️⃣ **CONTROL_CENTER_OPERATIONS.md** (7 דק')
**מה:** הוראות ספציפיות - 12 modules - דוגמאות

**סה"כ זמן קריאה: 15 דקות** ✅

---

## 📖 מסמכים נוספים (קרא לפי הצורך):

ב-control-center/:
- **PROJECT_MANAGER.md** - סקירה מלאה של הפרויקט
- **ROADMAP.md** - תכנית פיתוח (20+ שבועות)
- **CHATBOT_QUICK_START.md** - onboarding מהיר (10 דק')
- **INDEX.md** - מרכז מדריכים

ב-control-center/docs/:
- **CURRENT_STATE.md** - מצב בזמן אמת (מעודכן כל session)
- **SESSION_LOG.md** - היסטוריה מלאה

**איך לקרוא:**
```
קרא: control-center/PROJECT_MANAGER.md
קרא: control-center/docs/CURRENT_STATE.md  
קרא: control-center/docs/SESSION_LOG.md (שורות 1-50)
```

---

## ⚡ קודם כל: חוקי עדיפות!

**⏱️ זמן = כסף!** לפני שאתה עושה כלום, קרא:

👉 **PRIORITY_RULES.instructions.md** - חוקים לפי רמת חשיבות

**למה זה קריטי?**
- 🔴 CRITICAL = אסור לטעות → עלות שגיאה גבוהה!
- 🟡 HIGH = חשוב מאוד → מונע בעיות
- 🔵 MEDIUM = מומלץ → חוסך זמן
- 🟢 LOW = נחמד → משפר UX

**קרא את זה תוך 2 דקות - יחסוך לך 30 דקות של טעויות!**

---

## 📋 סדר פעולות מהיר

### 🔴 שלב 1: הבנת המערכת (5 דקות)

**מה זה Control Center?**
- Dashboard ניהול מרכזי לפרויקט eScriptorium
- 12 modules (4 פעילים, 8 בפיתוח)
- 2 servers (Dashboard + Terminal)
- מערכת תיעוד מלאה

**מבנה:**
```
control-center/
├── app/dashboard.html           ← UI ראשי
├── modules/                     ← 12 modules
│   ├── ✅ overview.js
│   ├── ✅ files.js
│   ├── ✅ sync.js
│   ├── ✅ docs-improved.js
│   ├── ⚠️ docker.js
│   └── ❌ dashboard.js (לא קיים)
├── servers/
│   ├── dashboard-server.js (8080)
│   └── terminal-server.js (3001)
└── docs/
    ├── SESSION_LOG.md
    └── CURRENT_STATE.md
```

**מה פעיל:**
- ✅ Dashboard Server (port 8080)
- ✅ Overview Tab
- ✅ Files Tab (File Watcher)
- ✅ Sync Tab
- ✅ Docs Tab (2176+ lines)

**מה צריך:**
- ⚠️ Terminal Server (/execute endpoint)
- ❌ Docker Module (תלוי ב-Terminal)
- ❌ Dashboard Module
- ❌ Build/Deploy/Logs modules

---

### 🟡 שלב 2: קריאת המצב הנוכחי (2 דקות)

**קודם כל - קרא את המצב:**
```
1. קרא: control-center/docs/CURRENT_STATE.md
   → מה עובד עכשיו?
   
2. קרא: control-center/docs/SESSION_LOG.md (50 שורות אחרונות)
   → מה עשינו לאחרונה?
   
3. קרא: control-center/PROJECT_MANAGER.md
   → מה המבנה המלא?
```

**למה זה חשוב?**
- אתה יודע מה כבר נעשה
- אתה לא עושה עבודה כפולה
- אתה רואה את ההקשר המלא

---

### 🟢 שלב 3: זיהוי המשימה (1 דקה)

**שאל את עצמך:**

1. **מה המשתמש ביקש?**
   - תיקון Terminal Server?
   - יצירת module חדש?
   - תיעוד?
   - בדיקת מצב?

2. **האם זה כבר נעשה?**
   ```
   חפש ב-SESSION_LOG.md: "המילה המפתח מהמשימה"
   ```

3. **איזה קבצים צריך?**
   - Terminal Server? → `servers/terminal-server.js`
   - Docker Module? → `modules/docker.js`
   - Dashboard Module? → `modules/dashboard.js` (לא קיים)

---

### 🔵 שלב 4: תכנון (2 דקות)

**לפני שמתחיל לעבוד:**

1. **בדוק עדיפות:**
   - 🔴 CRITICAL = Terminal Server /execute
   - 🟡 HIGH = Dashboard Module
   - 🔵 MEDIUM = Docker Integration
   - 🟢 LOW = UI improvements

2. **אמוד זמן:**
   - Terminal Server fix: ~30 דק'
   - Dashboard Module: ~1 שעה
   - Docker Integration: ~2 שעות

3. **תכנן צעדים:**
   ```
   1. קרא את הקובץ הקיים
   2. הבן את המבנה
   3. עשה שינוי קטן
   4. בדוק שזה עובד
   5. תעד
   ```

---

### 🟢 שלב 5: ביצוע (משתנה)

**כללי עבודה:**

1. **קרא קודם:**
   ```
   אל תערוך קובץ לפני שקראת אותו!
   ```

2. **שינויים קטנים:**
   ```
   עדיף 10 שינויים קטנים מאשר 1 גדול
   ```

3. **בדוק אחרי כל שינוי:**
   ```
   npm run build
   node servers/dashboard-server.js
   בדוק בדפדפן
   ```

4. **תעד תוך כדי:**
   ```
   עדכן SESSION_LOG.md כל 15 דקות
   ```

---

### 🔴 שלב 6: בדיקה (5 דקות)

**Checklist חובה:**

- [ ] **הקוד עובד** - בדקתי בדפדפן
- [ ] **אין שגיאות** - בדקתי console (F12)
- [ ] **עדכנתי תיעוד** - SESSION_LOG.md + CURRENT_STATE.md
- [ ] **סנכרנתי docs** - הרצתי sync-docs-to-dashboard.ps1
- [ ] **ניקיתי** - מחקתי קבצים זמניים

---

### 🟢 שלב 7: תיעוד (3 דקות)

**תבנית תיעוד:**

```markdown
## 🔗 Session [תאריך] [שעה] - [כותרת קצרה] ✅

**משימה:** [מה המשתמש ביקש]

**קבצים ששינתי:**
- `נתיב/קובץ.js` - [מה שיניתי]

**מה עשיתי:**
1. ✅ [פעולה 1]
2. ✅ [פעולה 2]

**בעיות:**
- **בעיה:** [תיאור]
  - **פתרון:** [איך פתרתי]

**זמן:** X דקות

**המלצות לצ'אטבוט הבא:**
- [מה הוא צריך לדעת]

**סטטוס:** [x] הושלם / [ ] חלקי / [ ] נכשל
```

---

## 🇮🇱 חוקי יסוד (חובה!)

### חוק #1: כתוב בעברית בלבד!

**אתה חייב לכתוב כל תגובה, הסבר והודעה בעברית!**

✅ **כתוב בעברית:**
- תגובות למשתמש
- הסברים טכניים
- הודעות התקדמות
- תוצאות בדיקות
- סיכומים

❌ **אל תכתוב בעברית:**
- קוד תכנות: `function init()` ✅ לא `function התחל()` ❌
- פקודות shell: `npm install` ✅
- שמות קבצים: `dashboard.js` ✅
- URLs: `http://localhost:8080` ✅

---

### חוק #2: תעד הכל!

**כל session חייב לעדכן:**
1. `docs/SESSION_LOG.md` - מה עשית
2. `docs/CURRENT_STATE.md` - מה המצב עכשיו
3. הרץ: `sync-docs-to-dashboard.ps1` - סנכרון

---

### חוק #3: אל תמחק SESSION_LOG!

**SESSION_LOG.md הוא הזיכרון שלנו!**
- ✅ הוסף בתחילת הקובץ
- ❌ אל תמחק היסטוריה
- ❌ אל תקצץ את הקובץ

---

### חוק #4: בדוק לפני וש מסיים

**Checklist מינימלי:**
```powershell
# בדוק שרתים
Invoke-WebRequest http://localhost:8080 | Select StatusCode
Invoke-WebRequest http://localhost:3001 | Select StatusCode

# בדוק console
# פתח dashboard → F12 → Console → אין שגיאות אדומות

# סנכרן docs
cd scripts/utilities
.\sync-docs-to-dashboard.ps1 -Force
```

---

## 🛠️ כלים זמינים

### הפעלת המערכת:

**אופציה 1 - מהיר:**
```bash
cd control-center/scripts
START_DASHBOARD.bat
```

**אופציה 2 - מתקדם:**
```powershell
cd control-center/scripts/utilities
.\auto-start-terminal-server.ps1
# פרמטרים: -Port 4000 | -Silent | -NoBrowser
```

---

### בדיקת סטטוס:

```powershell
# Dashboard Server
Invoke-WebRequest http://localhost:8080 | Select StatusCode

# Terminal Server
Invoke-WebRequest http://localhost:3001 | Select StatusCode
```

---

### סנכרון מסמכים:

```powershell
cd control-center/scripts/utilities
.\sync-docs-to-dashboard.ps1         # רגיל
.\sync-docs-to-dashboard.ps1 -Watch  # מצב צפייה
.\sync-docs-to-dashboard.ps1 -Force  # כפוי
```

---

## 🎯 תרחישים נפוצים

### תרחיש 1: "תקן את Terminal Server"

**מה לעשות:**
```
1. קרא: servers/terminal-server.js
2. הוסף endpoint:
   app.post('/execute', async (req, res) => {
     const { command } = req.body;
     // הרץ פקודה
   })
3. בדוק: curl -X POST http://localhost:3001/execute
4. תעד ב-SESSION_LOG.md
```

**זמן:** ~30 דקות  
**עדיפות:** 🔴 CRITICAL

---

### תרחיש 2: "צור Dashboard Module"

**מה לעשות:**
```javascript
// modules/dashboard.js
export async function init() {
    console.log('מאתחל Dashboard...');
    await renderDashboard();
}

async function renderDashboard() {
    const container = document.getElementById('dashboard-content');
    container.innerHTML = `
        <h1>Dashboard</h1>
        <!-- תוכן -->
    `;
}
```

**זמן:** ~1 שעה  
**עדיפות:** 🟡 HIGH

---

### תרחיש 3: "שפר Docker Module"

**מה לעשות:**
```
1. וודא ש-Terminal Server עובד
2. פתח: modules/docker.js
3. השתמש ב-terminalConfig.executeCommand()
4. הצג containers בזמן אמת
```

**זמן:** ~2 שעות  
**עדיפות:** 🔵 MEDIUM (תלוי ב-Terminal)

---

## 📚 מסמכים למידה

### בסיסי (חובה):
1. **CHATBOT_QUICK_START.md** (5 דק')
2. **PROJECT_MANAGER.md** (3 דק')
3. **ROADMAP.md** (2 דק')

### מתקדם (לפי צורך):
4. **MODULE_DEVELOPMENT_GUIDE.md** - איך לפתח module
5. **CATALOG.md** - מפת כל המערכות
6. **docs/HOW_TO_START.md** - מדריך הפעלה מפורט

---

## 🚫 מה לא לעשות!

### ❌ אל תעשה:

1. **אל תמחק SESSION_LOG.md** - זה הזיכרון שלנו!
2. **אל תערוך dashboard.html** ללא בקשה מפורשת
3. **אל תריץ פקודות Docker ידנית** - השתמש בסקריפטים
4. **אל תשאיר קבצים זמניים** - מחק אותם!
5. **אל תדלג על תיעוד** - זה חלק מהעבודה!
6. **אל תעשה שינויים גדולים** - עדיף הרבה קטנים
7. **אל תשכח לסנכרן docs** - הרץ sync-docs-to-dashboard.ps1

---

## 💡 טיפים חכמים

### 🎯 Tip #1: חפש לפני שממציא
```
יש בעיה? חפש ב-SESSION_LOG.md
אולי מישהו פתר את זה כבר!
```

### 🎯 Tip #2: תבנית קוד מוכנה
```javascript
// כל module צריך:
export async function init() {
    console.log('מאתחל...');
    await render();
}

async function render() {
    const container = document.getElementById('XXX-content');
    container.innerHTML = `...`;
}
```

### 🎯 Tip #3: בדוק את הקונסול
```
תמיד פתח F12 בדפדפן
זה יראה לך שגיאות מיד!
```

### 🎯 Tip #4: השתמש ב-data-loader
```javascript
// קריאת SESSION_LOG:
import dataLoader from './data-loader.js';
const log = await dataLoader.getSessionLog();
```

---

## 📞 צריך עזרה?

### 1. בדוק את התיעוד
- PROJECT_MANAGER.md
- ROADMAP.md
- SESSION_LOG.md
- CHATBOT_QUICK_START.md

### 2. חפש בקוד
```powershell
# חפש דוגמה:
Select-String "export async function init" modules/*.js
```

### 3. שאל את המשתמש
```
אם באמת תקוע - שאל!
עדיף לשאול מאשר לטעות.
```

---

## 🏆 המטרה שלך

**ברגע שתסיים:**
- ✅ משימה הושלמה
- ✅ הכל עובד בלי שגיאות
- ✅ תיעוד מלא ב-SESSION_LOG.md
- ✅ הצ'אטבוט הבא יודע מה עשית

**בהצלחה!** 🚀

---

**גרסה:** 1.0  
**תאריך:** 14 נובמבר 2025  
**מיועד ל:** צ'אטבוטים חדשים ב-Control Center Dashboard  
**מבוסס על:** eScriptorium_V2 Instructions System
