# 🎛️ מדריך שימוש - Control Center Dashboard

## 🌐 כתובות זמינות

| דשבורד | כתובת | מומלץ ל... |
|--------|--------|------------|
| **Dashboard (מומלץ)** | http://localhost:3001/app/dashboard.html | הרצת סקריפטים, בניה, deployment |
| **Index** | http://localhost:3001/app/index.html | ממשק חלופי עם 6 טאבים |

---

## ✅ מה עובד עכשיו (אחרי התיקון)

### 1. **חיבור ל-Terminal Server** ✅
- הדשבורד מחובר לפורט 3001
- אינדיקטור חיבור בראש הדף
- עדכון אוטומטי כל 2 שניות

### 2. **הרצת פקודות PowerShell** ✅
- טרמינל מובנה בדפדפן
- תמיכה ב-PowerShell 7+
- היסטוריית פקודות
- output בזמן אמת

### 3. **Quick Actions** ✅
- כפתורים מהירים להפעלה
- Deploy Dev/Test/Prod
- Check Requirements
- Master Scripts

### 4. **Docker Monitor** ✅
- סטטוס קונטיינרים בזמן אמת
- ספירה: פועלים/כבויים/סה"כ
- עדכון אוטומטי כל 5 שניות

---

## 🚀 איך להשתמש

### הרצת פקודה בטרמינל:

1. **פתח את הדשבורד:**
   ```
   http://localhost:3001/app/dashboard.html
   ```

2. **גלול לסקציית Terminal** (או לחץ על טאב Terminal)

3. **כתוב פקודה**, למשל:
   ```powershell
   Get-Date
   ```

4. **לחץ Enter** או על כפתור "הרץ"

5. **התוצאה תופיע מיד** 🎉

### דוגמאות לפקודות:

```powershell
# בדיקת גרסת PowerShell
$PSVersionTable.PSVersion

# רשימת קבצים
Get-ChildItem

# סטטוס Docker
docker ps

# בדיקת דרישות המערכת
cd "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\SCRIPTS"
.\utilities\check-requirements.ps1

# הפעלת build
.\build\build-master.ps1 -Environment dev
```

---

## 🎯 תכונות מתקדמות

### 1. **Deploy Buttons**
בחלק העליון של הדשבורד יש 3 כרטיסים צבעוניים:

- **🚀 Development** (כחול) - deployment מהיר לפיתוח
- **🧪 Testing** (ורוד) - בדיקות מקיפות
- **🚨 Production** (כתום) - פריסה זהירה לייצור

לחץ על אחד מהם → הפקודה תועתק → הדבק בטרמינל

### 2. **Master Scripts**
6 סקריפטים ראשיים:
- 🏗️ Setup - התקנה ראשונית
- 🔨 Build - בניית Docker images
- ▶️ Deploy & Start - הפעלת containers
- 🔄 Restart - אתחול
- 🩹 Troubleshoot - תיקון בעיות
- ⚡ Full Workflow - הכל ביחד

### 3. **Status Bar**
בתחתית המסך:
- 🟢 Terminal Server Status
- ⏰ Last Update Time  
- ✅ Health Status

---

## 🐳 Docker Integration

### מה רואים:
- **כרטיס גדול בראש הדף** עם:
  - מספר קונטיינרים פועלים
  - מספר קונטיינרים כבויים
  - אחוז זמינות
  - רשימה מלאה של כל הקונטיינרים

### מה אפשר לעשות:
```powershell
# הצג קונטיינרים
docker ps

# הפעל את כולם
cd "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\CORE\eScriptorium_UNIFIED"
docker-compose up -d

# עצור הכל
docker-compose down

# לוגים
docker-compose logs -f web
```

---

## 📊 טבלת Deployment History

בתחתית הדשבורד תראה טבלה עם:
- ⏰ זמן
- 🌍 סביבה (Dev/Test/Prod)
- ⚙️ Actions
- ✅ סטטוס
- ⏱️ משך
- 📝 שינויים

---

## 🎨 טיפים

### 💡 Tip #1: טרמינל מהיר
לחץ `Ctrl+L` כדי למחוק את המסך

### 💡 Tip #2: העתקת פקודות
כל הכפתורים מעתיקים את הפקודה ל-clipboard

### 💡 Tip #3: רענון
F5 מרענן את הדשבורד (אבל נתוני Docker מתעדכנים אוטומטית)

### 💡 Tip #4: Console
F12 → פתח Console בדפדפן לראות לוגים מפורטים

### 💡 Tip #5: דשבורדים מרובים
אפשר לפתוח כמה טאבים במקביל

---

## 🔧 פתרון בעיות

### ❌ "שגיאה בחיבור לשרת"
**פתרון:**
```powershell
cd "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\DEPLOYMENT_MANAGEMENT\control-center\servers"
node terminal-server.js 3001
```

### ❌ "Docker status not available"
**פתרון:**
```powershell
# הפעל Docker Monitor
cd "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\DEPLOYMENT_MANAGEMENT\control-center\servers"
node docker-monitor.js
```

### ❌ "נראה שאתה לא מחובר"
**פתרון:**
1. בדוק שTerminal Server רץ
2. רענן את הדף (F5)
3. בדוק את Status Bar בתחתית

---

## 🚀 דוגמה מלאה: בניית OCR

### צעד 1: הפעל את הסרברים
```powershell
# הרץ את הסקריפט האוטומטי
cd "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\DEPLOYMENT_MANAGEMENT\control-center\scripts"
.\start-ocr-system.ps1 -Quick
```

### צעד 2: פתח את הדשבורד
```
http://localhost:3001/app/dashboard.html
```

### צעד 3: בדוק דרישות
בטרמינל:
```powershell
cd "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\SCRIPTS"
.\utilities\check-requirements.ps1
```

### צעד 4: בנה את המערכת
בטרמינל:
```powershell
.\build\build-master.ps1 -Environment dev
```

### צעד 5: הפעל
בטרמינל:
```powershell
.\deploy\deploy-master.ps1 -Environment dev -Up
```

### צעד 6: עקוב אחר הסטטוס
הדשבורד יציג:
- ✅ Docker containers מופעלים
- 📊 Progress bar
- 🐳 רשימת קונטיינרים

---

## 🎉 סיכום

✅ **הדשבורד מחובר ופועל!**  
✅ **אפשר להריץ כל פקודה**  
✅ **Docker מנוטר בזמן אמת**  
✅ **הכל בממשק אחד יפה**

**תהנה! 🚀**

---

## 📞 עזרה נוספת

- 📄 תיעוד מלא: `QUICK_START_OCR_DASHBOARD.md`
- 🎛️ README: `control-center/README.md`
- 📚 מדריכים: `control-center/docs/`
