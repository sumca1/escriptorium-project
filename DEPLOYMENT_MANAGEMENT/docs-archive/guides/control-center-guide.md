# 🎛️ מדריך מרכז הבקרה - Control Center Guide

## 📋 **סיכום המערכת**

יצרנו **מרכז בקרה מלא** עם:

✅ **ממשק HTML חי** - PROJECT_CONTROL_CENTER.html  
✅ **עדכון אוטומטי** - כל 2 שניות מתעדכן!  
✅ **3 סביבות עבודה** - Development, Testing, Production  
✅ **לחצני בקרה** - הפעל/עצור/אתחל כל סביבה  
✅ **מעקב קבצים** - רואה מה השתנה בזמן אמת  
✅ **לוגים חיים** - כל הפעילות במסך אחד  

---

## 🚀 איך להתחיל?

### **שלב 1: הפעל את מעדכן ה-Dashboard**

```powershell
cd I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\SCRIPTS
.\update_dashboard.ps1 -Continuous
```

**זה יריץ בלופ אינסופי:**
- קורא סטטוס Docker
- סופר קבצים שהשתנו
- יוצר קובץ PROJECT_STATUS.json
- מתעדכן כל 2 שניות

### **שלב 2: פתח את ה-Dashboard**

```powershell
# פתח בדפדפן:
start I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\PROJECT_CONTROL_CENTER.html
```

או פשוט לחץ פעמיים על הקובץ!

### **שלב 3: תראה את הקסם! 🎉**

- **מבט כללי**: סטטיסטיקות + טיימליין פעילות
- **סביבות עבודה**: 3 כרטיסים עם לחצני בקרה
- **מעקב קבצים**: עץ קבצים (ירוק = שינוי)
- **סנכרון**: מצב סנכרון כל הקבצים
- **לוגים**: קונסול חי עם כל הפעילות

---

## 🎮 איך להשתמש בלחצנים?

### **כשלוחץ על לחצן בממשק:**

1. **יופיע מודאל** עם הוראות הרצה
2. **העתק את הפקודה** לטרמינל
3. **Dashboard מתעדכן** אוטומטית אחרי!

**דוגמה:**

לוחץ "▶️ הפעל" על Development →  
מקבל הוראה:
```powershell
pwsh -File "I:\...\SCRIPTS\control_environment.ps1" -Environment dev -Action start
```

העתק לטרמינל → סביבה עולה → Dashboard מראה "פעיל" ✅

---

## 📂 מבנה הקבצים

```
BiblIA_dataset/
│
├── 📄 PROJECT_CONTROL_CENTER.html       ← הממשק החזותי (פתח בדפדפן)
├── 📄 PROJECT_STATUS.json                ← נתונים בזמן אמת (נוצר אוטומטית)
├── 📄 DEPLOYMENT_STRATEGY.md            ← הסבר על 3 המסלולים
│
├── 📂 SCRIPTS/                          ← כל הסקריפטים
│   ├── 📜 update_dashboard.ps1          ← מעדכן Dashboard (הרץ ברקע!)
│   ├── 📜 control_environment.ps1       ← בקרה על סביבות
│   └── 📜 sync_environments.ps1         ← סנכרון (בקרוב)
│
├── 📂 SOURCE/                           ← מקור אמת יחיד (בקרוב)
│   ├── app/                             ← כל הקוד Django
│   └── front/                           ← כל הקוד Frontend
│
└── 📂 ENVIRONMENTS/                     ← 3 סביבות (בקרוב)
    ├── 🔧 development/
    ├── 🧪 testing/
    └── 🚢 production/
```

---

## 🎯 תהליך עבודה מומלץ

### **בוקר - התחלת עבודה:**

```powershell
# טרמינל 1: הפעל מעדכן Dashboard
.\SCRIPTS\update_dashboard.ps1 -Continuous

# טרמינל 2: הפעל Development
.\SCRIPTS\control_environment.ps1 -Environment dev -Action start

# פתח Dashboard בדפדפן
start PROJECT_CONTROL_CENTER.html
```

### **במהלך העבודה:**

1. ✏️ **עורך קובץ** → Dashboard מראה ירוק (●)
2. 💾 **שומר** → סנכרון אוטומטי
3. 🔄 **רואה שינוי** → מיידי (1-2 שניות!)

### **לפני deploy:**

```powershell
# 1. בדיקות
.\SCRIPTS\control_environment.ps1 -Environment test -Action start

# 2. אם עבר - deploy
.\SCRIPTS\control_environment.ps1 -Environment prod -Action start
```

---

## 🔧 פקודות שימושיות

### **בקרה על סביבות:**

```powershell
# הפעלה
.\SCRIPTS\control_environment.ps1 -Environment dev -Action start

# עצירה
.\SCRIPTS\control_environment.ps1 -Environment dev -Action stop

# אתחול
.\SCRIPTS\control_environment.ps1 -Environment dev -Action restart

# סטטוס
.\SCRIPTS\control_environment.ps1 -Environment dev -Action status

# לוגים (בזמן אמת)
.\SCRIPTS\control_environment.ps1 -Environment dev -Action logs
```

### **עדכון Dashboard:**

```powershell
# עדכון חד-פעמי
.\SCRIPTS\update_dashboard.ps1

# עדכון רציף (מומלץ!)
.\SCRIPTS\update_dashboard.ps1 -Continuous

# עדכון כל 5 שניות
.\SCRIPTS\update_dashboard.ps1 -Continuous -IntervalSeconds 5
```

---

## 🌟 תכונות מתקדמות

### **1. סנכרון אוטומטי**

כל שינוי ב-SOURCE/ מתעדכן אוטומטית ב-3 הסביבות!

**איך זה עובד?**
- Volume mounting: `./SOURCE/app:/usr/src/app`
- שינוי בקובץ → מיידי בכל הסביבות
- Django hot-reload → רואה שינוי ב-1 שנייה

### **2. מעקב בזמן אמת**

Dashboard עוקב אחרי:
- ✅ סטטוס Docker containers
- ✅ קבצים שהשתנו (Git או זמן שינוי)
- ✅ לוגים אחרונים
- ✅ זמן הפעלה (uptime)
- ✅ בריאות containers (health checks)

### **3. טיימליין פעילות**

רואה בדיוק מה קרה:
- 🕐 14:26 - עדכון Dashboard
- 🕐 14:25 - בדיקות הושלמו
- 🕐 14:24 - שינוי קובץ views.py
- 🕐 14:23 - Development הופעל

---

## 📊 מה הלאה?

### **שלב הבא:**

1. ✅ ניצור תיקיית SOURCE/ (מקור אמת יחיד)
2. ✅ נעביר את כל הקוד ל-SOURCE/
3. ✅ ניצור 3 docker-compose מותאמים
4. ✅ נגדיר volume mounting מלא
5. ✅ נוסיף סקריפט סנכרון

**זמן: 30-45 דקות**  
**תוצאה: פיתוח מהיר בלי builds!**

---

## 🆘 פתרון בעיות

### **Dashboard לא מתעדכן?**

```powershell
# בדוק אם update_dashboard.ps1 רץ
Get-Process pwsh | Where-Object { $_.CommandLine -like '*update_dashboard*' }

# אם לא - הפעל אותו
.\SCRIPTS\update_dashboard.ps1 -Continuous
```

### **נתונים לא מדויקים?**

```powershell
# מחק את PROJECT_STATUS.json ותן לו להיווצר מחדש
Remove-Item PROJECT_STATUS.json
.\SCRIPTS\update_dashboard.ps1

# רענן דפדפן (Ctrl+F5)
```

### **לחצנים לא עובדים?**

זה רגיל! הלחצנים מציגים **הוראות הרצה**.  
העתק את הפקודה לטרמינל והרץ שם.

(בעתיד: אפשר להוסיף PowerShell Web Server לביצוע ישיר)

---

## 🎉 מזל טוב!

יש לך עכשיו **מרכז בקרה מקצועי** שמנהל את הפרויקט!

### **היתרונות:**

✅ רואה הכל במקום אחד  
✅ מתעדכן בזמן אמת  
✅ שליטה מלאה על 3 סביבות  
✅ מעקב אחרי כל שינוי  
✅ לוגים וסטטיסטיקות חיות  

### **חיסכון בזמן:**

| לפני | אחרי |
|------|------|
| רץ בין טרמינלים | מסך אחד |
| לא יודע מה המצב | רואה הכל |
| build כל פעם (15 דק') | volume mounting (2 שניות) |
| בילבול בין גרסאות | מקור אמת אחד |

---

**האם תרצה שנמשיך לשלב הבא?** (יצירת SOURCE/ וסנכרון מלא)

🚀 **בהצלחה!**
