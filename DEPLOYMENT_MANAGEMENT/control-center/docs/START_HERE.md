# 🚀 מדריך הפעלת מרכז הבקרה
## eScriptorium Control Center - Quick Start Guide

---

## 📋 סיכום מהיר

**מרכז הבקרה מורכב מ-3 רכיבים:**

1. **Terminal Server** (Port 3000) - מבצע פקודות PowerShell
2. **Dashboard Server** (Port 8080) - מגיש את ממשק המשתמש
3. **Dashboard UI** - הממשק הגרפי (dashboard.html)

---

## ⚡ הפעלה מהירה (3 אפשרויות)

### ✅ **אפשרות 1: VBScript Launcher (הכי פשוט!)**

```
1. לחץ פעמיים על: start-servers.vbs
2. זהו! השרתים עולים אוטומטית
```

**מיקום הקובץ:**
```
i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center\start-servers.vbs
```

---

### 🔷 **אפשרות 2: Batch File**

```
1. לחץ פעמיים על: start-terminal-server.bat
2. מסוף PowerShell ייפתח עם השרתים
```

**מיקום הקובץ:**
```
i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center\start-terminal-server.bat
```

---

### ⚡ **אפשרות 3: PowerShell ידני**

```powershell
# פתח PowerShell והרץ:
cd i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center
.\scripts\utilities\auto-start-terminal-server.ps1 -NoBrowser
```

---

## 🎯 יצירת קיצור דרך בדסקטופ

רוצה לחיצה אחת מהדסקטופ? הרץ:

```powershell
cd i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center
.\create-shortcut.ps1
```

זה יוצר קיצור דרך בדסקטופ בשם **"Start Terminal Server"** 🎉

---

## 🔍 איך לדעת שהכל עובד?

### בדיקת Terminal Server (Port 3000):
```powershell
Invoke-WebRequest http://localhost:3000/health
```

**תוצאה מצופה:**
```
StatusCode: 200
Content: {"status":"healthy","timestamp":"..."}
```

---

### בדיקת Dashboard Server (Port 8080):
```powershell
Invoke-WebRequest http://localhost:8080
```

**תוצאה מצופה:**
```
StatusCode: 200
Content: <!DOCTYPE html>...
```

---

### פתיחת ממשק המשתמש:
```
http://localhost:8080
```

או פשוט פתח בדפדפן:
```
i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center\dashboard.html
```

---

## 🛠️ פתרון בעיות נפוצות

### ❌ "Cannot connect to terminal server"

**פתרון:**
1. הרץ את `start-servers.vbs` או `start-terminal-server.bat`
2. המתן 5 שניות
3. רענן את הדפדפן (F5)

---

### ❌ "Port 3000 is already in use"

**פתרון:**
```powershell
# מצא את התהליך שתופס את הפורט
Get-NetTCPConnection -LocalPort 3000 -State Listen | ForEach-Object {
    Get-Process -Id $_.OwningProcess | Select Name, Id
}

# סגור את התהליך (החלף <PID> במספר שקיבלת)
Stop-Process -Id <PID> -Force
```

---

### ❌ "Dashboard Server not responding"

**פתרון:**
```powershell
# הפעל את dashboard-server ידנית
cd i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center
node dashboard-server.js
```

---

## 📁 מבנה הקבצים

```
control-center/
│
├── dashboard.html                    ← ממשק המשתמש הראשי
├── terminal-server.js                ← שרת ביצוע פקודות (Port 3000)
├── dashboard-server.js               ← שרת HTTP (Port 8080)
│
├── start-servers.vbs                 ← 🌟 VBScript launcher (מומלץ!)
├── start-terminal-server.bat         ← Batch launcher
├── create-shortcut.ps1               ← יוצר קיצור דרך בדסקטופ
│
└── scripts/
    └── utilities/
        └── auto-start-terminal-server.ps1  ← הסקריפט המרכזי
```

---

## 💡 טיפים

### 1. הפעלה אוטומטית בהפעלת המחשב

צור Task Scheduler task שמריץ את `start-servers.vbs` בהפעלת Windows:

```powershell
# יצירת task אוטומטי
$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center\start-servers.vbs"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "eScriptorium Control Center" -Description "Start terminal and dashboard servers"
```

---

### 2. בדיקת סטטוס מהיר

```powershell
# בדוק את שני השרתים במכה אחת
@(3000, 8080) | ForEach-Object {
    $port = $_
    try {
        $test = Invoke-WebRequest "http://localhost:$port" -TimeoutSec 2
        Write-Host "✅ Port $port - Active" -ForegroundColor Green
    } catch {
        Write-Host "❌ Port $port - Inactive" -ForegroundColor Red
    }
}
```

---

### 3. עצירת השרתים

```powershell
# עצור את כל התהליכים של node (שרתים)
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "✅ כל השרתים נסגרו" -ForegroundColor Green
```

---

## 🎉 סיכום

| שיטת הפעלה | קלות | מהירות | מומלץ ל... |
|-----------|------|--------|-----------|
| **start-servers.vbs** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | כולם! הכי פשוט |
| **start-terminal-server.bat** | ⭐⭐⭐⭐ | ⚡⚡⚡ | משתמשי Windows |
| **PowerShell ידני** | ⭐⭐⭐ | ⚡⚡ | מפתחים |
| **קיצור דרך Desktop** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | שימוש יומיומי |

---

## 📞 עזרה נוספת

- **בעיות טכניות**: בדוק את `SESSION_LOG.md`
- **שאלות**: עיין ב-`CHATBOT_ONBOARDING.md`
- **עדכונים**: `CURRENT_STATE.md`

---

**גרסה:** 1.0  
**תאריך:** 12 נובמבר 2025  
**סטטוס:** ✅ פעיל ונבדק
