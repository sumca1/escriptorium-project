# 🚀 הפעלת Dashboard - מדריך מהיר

## ✨ הדרך הכי פשוטה (מומלץ!)

**פשוט לחץ פעמיים על הקובץ:**
```
📁 START_DASHBOARD.bat
```

**זהו! הקובץ יפעיל אוטומטית:**
- ✅ Terminal Server (ברקע - פורט 3001)
- ✅ HTTP Server (פורט 8080)
- ✅ Dashboard בדפדפן

---

## 📋 אפשרויות נוספות

### אופציה 1: דרך PowerShell (אם BAT לא עובד)
```powershell
# הפעל Terminal Server ברקע
.\scripts\utilities\auto-start-terminal-server.ps1

# הפעל HTTP Server
python -m http.server 8080

# פתח דפדפן
start http://localhost:8080/dashboard.html
```

### אופציה 2: הפעלה ידנית (debug mode)
```powershell
# טרמינל 1 - Terminal Server
cd escriptorium\ui\control-center
node terminal-server.js

# טרמינל 2 - HTTP Server  
python -m http.server 8080
```

---

## 🔧 פתרון בעיות

### ❌ "Node.js is not installed"
**פתרון:** התקן Node.js מ: https://nodejs.org/

### ❌ "לא הצלחנו להתחבר לשרת"
**פתרון:** 
1. וודא ש-Node.js מותקן (`node --version`)
2. הרץ את `START_DASHBOARD.bat` שוב
3. אם עדיין לא עובד - הרץ ידנית: `node terminal-server.js`

### ❌ "Port 8080 is already in use"
**פתרון:** סגור תהליכים על פורט 8080:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

---

## 📊 מה כל שרת עושה?

| שרת | פורט | תפקיד |
|-----|------|-------|
| **Terminal Server** | 3001 | מריץ פקודות PowerShell מ-Dashboard |
| **HTTP Server** | 8080 | מגיש את קבצי Dashboard |

---

## 🎯 URL-ים חשובים

- **Dashboard:** http://localhost:8080/dashboard.html
- **Terminal Server Health:** http://localhost:3001/health
- **Control Center:** http://localhost:8080/

---

## 💡 טיפים

1. **השרת ברקע:** Terminal Server רץ ברקע - אין צורך להשאיר חלון פתוח
2. **בדיקת מצב:** לחץ על "🔌 התחבר לשרת" ב-Dashboard לבדוק חיבור
3. **עצירה:** לחץ כל מקש ב-START_DASHBOARD.bat לעצור את כל השרתים

---

**נוצר:** 12 נובמבר 2025  
**גרסה:** 1.0 - Auto-Start Edition
