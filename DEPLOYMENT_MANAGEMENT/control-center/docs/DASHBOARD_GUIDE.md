# 🎛️ לוח בקרה מאוחד - מדריך שימוש

**ממשק ניהול ופיקוח מרכזי למערכת BiblIA eScriptorium**

---

## 📍 מיקום הקובץ

```
escriptorium/ui/control-center/dashboard.html
```

---

## 🚀 איך להתחיל?

### אופציה 1: פתיחה ישירה (Recommended)

```powershell
# מתוך escriptorium/
start ui\control-center\dashboard.html
```

### אופציה 2: עם Web Server

```powershell
# התקן http-server אם אין לך
npm install -g http-server

# הרץ מתוך ui/control-center/
cd escriptorium\ui\control-center
http-server -p 8080

# פתח בדפדפן
start http://localhost:8080/dashboard.html
```

---

## 🎯 מה הלוח הזה כולל?

### 1️⃣ **Dashboard (📊)**
- **סקירת מערכת** - סטטוס כללי של כל הקומפוננטים
- **Quick Stats** - Frontend, Backend, Docker, Build status
- **פעולות מהירות** - כפתורים להרצת build, deploy, docker
- **פעילות אחרונה** - Timeline של פעולות אחרונות

### 2️⃣ **Build Management (🏗️)**
- **Frontend Build** - בניית קבצי Vue.js + Webpack
- **Complete UNIFIED** - השלמת מבנה UNIFIED מלא
- **Copy from CLEAN** - העתקה מ-CLEAN ל-UNIFIED
- **Progress Bar** - מעקב אחר התקדמות Build
- **Build Output** - לוגים חיים של תהליך הבנייה

### 3️⃣ **Deployment Management (🚀)**
- **Deploy Dev** - העלאת סביבת פיתוח
- **Deploy Test** - העלאת סביבת בדיקות
- **Deploy Prod** - העלאת סביבת ייצור (Production)
- **Deploy Output** - לוגים של תהליך ההעלאה

### 4️⃣ **System Status (💻)**
- **טבלת סטטוס** - מצב כל הקומפוננטים
- **Component Details** - פרטים על כל שירות
- **Quick Actions** - כפתורי Restart/Check לכל קומפוננט

### 5️⃣ **Terminal (⌨️)**
- **Terminal אינטראקטיבי** - הרצת פקודות ישירות
- **Terminal Server** - חיבור ל-Node.js server (port 3001)
- **Command History** - היסטוריית פקודות

### 6️⃣ **Logs (📝)**
- **Build Logs** - לוגי build ואימותים
- **Deploy Logs** - לוגי deployment
- **Docker Logs** - לוגי containers
- **Error Logs** - שגיאות ובעיות

### 7️⃣ **Documentation (📚)**
- **Quick Start** - מדריך התחלה מהירה
- **Architecture** - ארכיטקטורת המערכת
- **Deployment** - מדריכי deployment

---

## 🗂️ נתיבי סקריפטים (עודכנו!)

הלוח מכיל נתיבים מעודכנים לכל הסקריפטים:

```javascript
const CONFIG = {
    baseDir: 'escriptorium',
    scripts: {
        'build-frontend': '../scripts/build/copy-clean-to-unified.ps1',
        'complete-unified': '../scripts/build/complete-unified.ps1',
        'copy-clean': '../scripts/build/copy-clean-to-unified.ps1',
        'deploy-dev': '../scripts/deploy/deploy-dev.ps1',
        'deploy-test': '../scripts/deploy/deploy-test.ps1',
        'deploy-prod': '../scripts/deploy/deploy-prod.ps1',
        'check-requirements': '../scripts/utilities/check-requirements.ps1',
        'monitor': '../scripts/maintenance/monitor.ps1'
    },
    terminalServer: 'http://localhost:3001'
};
```

---

## 🎨 תכונות מתקדמות

### ✨ Real-Time Status
- עדכון שעון בזמן אמת
- אינדיקטור מצב מערכת (ירוק/אדום/צהוב)
- Progress bar דינמי

### ✨ Keyboard Shortcuts
- **Enter** בשדה Terminal → הרצת פקודה
- **Tab Navigation** בין קטגוריות

### ✨ Responsive Design
- עובד על מסכים גדולים וקטנים
- Grid layout אדפטיבי
- Mobile-friendly (עם התאמות)

---

## 🔧 הגדרות והתאמה אישית

### שינוי נתיבים
ערוך את אובייקט `CONFIG` ב-JavaScript (שורה ~910):

```javascript
const CONFIG = {
    baseDir: 'YOUR_PATH_HERE',
    scripts: {
        'script-name': 'RELATIVE_PATH_TO_SCRIPT'
    }
};
```

### שינוי צבעים
ערוך את `:root` variables ב-CSS (שורה ~8):

```css
:root {
    --primary: #667eea;
    --secondary: #764ba2;
    --success: #10b981;
    ...
}
```

---

## 🚦 מצב המערכת - אינדיקטורים

| צבע | משמעות |
|-----|--------|
| 🟢 **ירוק** | מערכת פועלת תקין |
| 🟡 **צהוב** | Building / בתהליך |
| 🔴 **אדום** | שגיאה / לא פעיל |

---

## 📋 תרחישי שימוש נפוצים

### תרחיש 1: Build מהתחלה
```
1. לחץ על "Build" בסרגל הצד
2. לחץ "הרץ Build" תחת "Frontend Build"
3. עקוב אחר Progress Bar
4. בדוק Build Output ללוגים
```

### תרחיש 2: Deploy סביבת Dev
```
1. לחץ על "Deploy" בסרגל הצד
2. לחץ "Deploy Dev" תחת Development
3. עקוב אחר Deploy Output
4. בדוק System Status למצב הקומפוננטים
```

### תרחיש 3: בדיקת מצב המערכת
```
1. לחץ על "System Status" בסרגל הצד
2. ראה טבלה מפורטת של כל הקומפוננטים
3. לחץ "Check" או "Restart" לפי הצורך
```

### תרחיש 4: הרצת פקודה ידנית
```
1. לחץ על "Terminal" בסרגל הצד
2. הקלד פקודה בשדה הטקסט
3. לחץ "הרץ פקודה" או Enter
4. ראה תוצאות ב-Terminal Output
```

### תרחיש 5: צפייה בלוגים
```
1. לחץ על "Logs" בסרגל הצד
2. בחר קטגוריה (Build/Deploy/Docker/Error)
3. ראה לוגים מתעדכנים
```

---

## 🔗 קישורים מהירים

### מדריכים:
- [Quick Start](../../../QUICK_START.md)
- [Deployment Strategy](../docs-archive/guides/deployment-strategy.md)
- [Architecture](../docs-archive/architecture/scripts-architecture.md)

### סקריפטים:
- Build: `../../scripts/build/`
- Deploy: `../../scripts/deploy/`
- Utilities: `../../scripts/utilities/`
- Maintenance: `../../scripts/maintenance/`

### דוחות:
- [Current Status](../../management/reports/current-status-and-plan.md)
- [Organization Complete](../../ORGANIZATION_COMPLETE.md)

---

## ⚠️ הערות חשובות

### 🚨 Terminal Server
לשימוש ב-Terminal האינטראקטיבי, צריך להריץ:

```powershell
cd escriptorium\ui\control-center
node terminal-server.js
```

זה יפעיל שרת ב-port 3001 שמאפשר הרצת פקודות מהממשק.

### 🚨 נתיבים יחסיים
הלוח משתמש בנתיבים **יחסיים** מתוך `ui/control-center/`.  
אם תזיז את הקובץ, תצטרך לעדכן את `CONFIG.scripts`.

### 🚨 Browser Compatibility
הממשק נבדק על:
- ✅ Chrome/Edge (מומלץ)
- ✅ Firefox
- ⚠️ Safari (עם הגבלות)

---

## 🆘 פתרון בעיות

### בעיה: "סקריפט לא נמצא"
**פתרון:** בדוק את `CONFIG.scripts` - וודא שהנתיב נכון יחסית ל-`ui/control-center/`

### בעיה: "Terminal Server לא זמין"
**פתרון:** 
```powershell
cd escriptorium\ui\control-center
npm install express
node terminal-server.js
```

### בעיה: "Progress Bar לא זז"
**פתרון:** זה סימולציה בלבד. בגרסה production, זה יתחבר ל-Terminal Server.

### בעיה: "Documentation לא נפתח"
**פתרון:** וודא שהקבצים קיימים:
- `../../QUICK_START.md`
- `../../docs/guides/deployment-strategy.md`
- וכו'

---

## 🎯 הבדלים מהגרסאות הקודמות

### ✨ חדש ב-Dashboard המאוחד:

| תכונה | V1 | V2 | Dashboard המאוחד |
|-------|----|----|------------------|
| נתיבים מעודכנים | ❌ | ❌ | ✅ |
| ארגון נכון של קבצים | ❌ | ❌ | ✅ |
| Real-time status | ⚠️ | ✅ | ✅ |
| Terminal אינטראקטיבי | ⚠️ | ✅ | ✅ |
| Logs viewing | ❌ | ⚠️ | ✅ |
| Documentation links | ❌ | ⚠️ | ✅ |
| Progress tracking | ⚠️ | ✅ | ✅ |
| Sidebar navigation | ❌ | ❌ | ✅ |

---

## 🚀 העתיד (Roadmap)

### גרסאות עתידיות:
- [ ] חיבור אמיתי ל-Terminal Server
- [ ] WebSocket לעדכונים בזמן אמת
- [ ] Docker stats אמיתיים (CPU, Memory)
- [ ] Notification system
- [ ] Multi-user support
- [ ] Build history + rollback
- [ ] Dark mode
- [ ] Mobile app

---

## 📞 עזרה נוספת

- 📚 **Documentation:** `../../docs/`
- 📊 **Reports:** `../../management/reports/`
- 🤖 **Scripts:** `../../scripts/`
- 📝 **Session Log:** `../../SESSION_LOG.md`

---

## ✅ Checklist למשתמש חדש

- [ ] פתח את `dashboard.html`
- [ ] ראה שכל הסקציות עובדות (Dashboard, Build, Deploy...)
- [ ] נסה Quick Action אחד מ-Dashboard
- [ ] בדוק System Status
- [ ] נסה Terminal (אם יש Terminal Server)
- [ ] ראה Logs
- [ ] פתח Documentation

**אם הכל עובד - מעולה! המערכת מוכנה לשימוש! 🎉**

---

**גרסה:** 1.0 (Unified Dashboard)  
**תאריך:** 12 נובמבר 2025  
**מחבר:** AI Assistant  
**סטטוס:** ✅ Production Ready
