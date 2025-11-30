# 🚀 מדריך הפעלה מהיר - מערכת OCR + Dashboard

## ✨ מה הושלם

### 1. **Terminal Server v2.0** ✅
- פועל על `http://localhost:3001`
- תומך ב-PowerShell 7+ 
- API endpoints להרצת פקודות

### 2. **Docker Monitor** ✅
- מעקב בזמן אמת אחרי קונטיינרים
- מייצר `docker-status.json` כל 5 שניות
- פועל ברקע באופן אוטומטי

### 3. **Control Center Dashboard** ✅
- דשבורד מסועף ויפהפה
- 6 טאבים: Dashboard, Terminal, Scripts, Errors, Guides, Status
- אינטגרציה חיה עם Docker
- עדכון אוטומטי

### 4. **סקריפט הפעלה אוטומטי** ✅
- `start-ocr-system.ps1` - מפעיל הכל במהלך אחד

---

## 🎯 איך להשתמש

### הפעלה מהירה של הכל:

```powershell
cd "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\DEPLOYMENT_MANAGEMENT\control-center\scripts"

.\start-ocr-system.ps1 -Quick
```

הסקריפט:
1. ✅ בודק ומפעיל Docker Desktop
2. ✅ מפעיל Terminal Server (Port 3001)
3. ✅ בודק קונטיינרים ומציע להעלות
4. ✅ מפעיל Dashboard Server (אופציונלי)
5. ✅ פותח דפדפן
6. ✅ מציג סיכום

### פתיחת הדשבורד בלבד:

```powershell
Start-Process "http://localhost:3001"
```

---

## 🎛️ תכונות הדשבורד

### **טאב 📊 Dashboard:**
- **סטטוס Docker בזמן אמת** - בראש הדף
  - ספירת קונטיינרים: פועלים/כבויים/סה"כ
  - אחוז זמינות
  - רשימת כל הקונטיינרים עם סטטוס
  - עדכון אוטומטי כל 5 שניות

- **3 סביבות Deployment:**
  - 🚀 Development
  - 🧪 Testing  
  - 🚨 Production

- **טבלת היסטוריה** - 10 deployments אחרונים

- **6 Master Scripts:**
  - Setup, Build, Deploy, Restart, Troubleshoot, Full Workflow

### **טאב 💻 Terminal:**
- טרמינל PowerShell מובנה בדפדפן
- הרצת פקודות ישירות
- היסטוריית פקודות
- תמיכה מלאה בעברית

### **טאב 🤖 Scripts:**
- רשימת כל הסקריפטים הזמינים
- סינון לפי קטגוריה
- העתקת פקודות בקליק

### **טאב 🚨 Error Codes:**
- מערכת Error Codes מלאה
- סינון לפי קטגוריה
- פתרונות מובנים

### **טאב 📚 Guides:**
- תיעוד מלא
- מדריכי שימוש

### **טאב 📈 Status:**
- סטטיסטיקות מערכת
- בדיקת חיבור

---

## 🔧 פקודות שימושיות

### ניהול Docker:
```powershell
# סטטוס קונטיינרים
docker ps

# כל הקונטיינרים (כולל כבויים)
docker ps -a

# הפעלת קונטיינרים
cd "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\CORE\eScriptorium_UNIFIED"
docker-compose up -d

# עצירת קונטיינרים
docker-compose down

# לוגים
docker-compose logs -f web
```

### ניהול הסרברים:
```powershell
# הפעלת Terminal Server
cd "i:\...\control-center\servers"
node terminal-server.js 3001

# הפעלת Docker Monitor
node docker-monitor.js

# הפעלת Dashboard Server
node dashboard-server.js
```

---

## 📊 מצב נוכחי

### סרברים פועלים:
- ✅ Terminal Server (Port 3001)
- ✅ Dashboard Server (Port 8080)  
- ✅ Docker Monitor (ברקע)

### Docker:
- ✅ Docker Desktop פועל
- 📦 1/5 קונטיינרים פועלים:
  - ✅ escriptorium_es (Elasticsearch)
  - ⏹️ config-web-1
  - ⏹️ config-redis-1
  - ⏹️ config-db-1
  - ⏹️ (עוד 1)

### קבצים שנוצרו:
- ✅ `start-ocr-system.ps1` - סקריפט הפעלה אוטומטי
- ✅ `docker-monitor.js` - מוניטור Docker
- ✅ `docker-integration.js` - אינטגרציה עם הדשבורד
- ✅ `docker-status.json` - נתונים בזמן אמת

---

## 🌐 כתובות

| שירות | כתובת | תיאור |
|-------|--------|-------|
| **Control Center** | http://localhost:3001 | דשבורד מרכזי מסועף |
| **Terminal API** | http://localhost:3001/status | API של Terminal Server |
| **Dashboard (legacy)** | http://localhost:8080 | Dashboard ישן |
| **eScriptorium OCR** | http://localhost | המערכת הראשית (כשפועלת) |

---

## 🎨 מה ייחודי בדשבורד הזה?

1. **אינטגרציה חיה עם Docker** - רואה בזמן אמת מה קורה
2. **עיצוב מסועף ויפה** - ממשק עברי מלא
3. **טרמינל מובנה** - לא צריך לצאת מהדפדפן
4. **אוטומציה מלאה** - הכל מתעדכן לבד
5. **Error Codes מתועדים** - כל שגיאה עם פתרון
6. **היסטוריית Deployments** - מעקב אחר שינויים

---

## 🚀 צעדים הבאים

### להפעיל את מערכת ה-OCR המלאה:

1. **הפעל את כל הקונטיינרים:**
```powershell
cd "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\CORE\eScriptorium_UNIFIED"
docker-compose up -d
```

2. **המתן לכל הקונטיינרים:**
```powershell
docker-compose ps
```

3. **גש ל-eScriptorium:**
```
http://localhost
```

4. **עקוב אחר הסטטוס בדשבורד:**
```
http://localhost:3001
```

---

## 💡 טיפים

- **F12** - פתח Console בדפדפן לראות לוגים
- **רענן הדף** - עדכון מיידי של נתונים
- **טאב Terminal** - הרץ פקודות ישירות
- **סטטוס Docker** - תמיד מוצג בראש הדף

---

## 🎉 סיכום

✅ המערכת מוכנה ופועלת!  
✅ הדשבורד מחובר ל-Docker בזמן אמת  
✅ כל הסקריפטים זמינים  
✅ התיעוד מלא  

**כל מה שנשאר הוא להפעיל את הקונטיינרים ולהתחיל לעבוד!** 🚀
