# ✅ רשימת בדיקה - עבודה עם Dashboard

## 🎯 מטרה
לעבוד עם הדשבורד ולהפעיל את מערכת ה-OCR מתחילה ועד סוף

---

## צעד 1️⃣: 💻 הרצת פקודות PowerShell

### מצב: ⬜ לא הושלם

### מה לעשות:
1. פתח את הדשבורד: http://localhost:3001/app/dashboard.html
2. גלול למטה ל"Terminal Emulator"
3. הרץ את הפקודות הבאות:

```powershell
# בדיקה בסיסית
Get-Date

# מידע על PowerShell
$PSVersionTable.PSVersion

# רשימת קבצים
Get-ChildItem . | Select-Object -First 5

# סטטוס Docker
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### ✅ סימן הצלחה:
- [ ] ראית את התאריך והשעה
- [ ] ראית את גרסת PowerShell
- [ ] ראית רשימת קבצים
- [ ] ראית טבלת Docker

---

## צעד 2️⃣: 🐳 צפייה בסטטוס Docker

### מצב: ⬜ לא הושלם

### מה לעשות:
1. גלול לראש הדף בדשבורד
2. חפש כרטיס "סטטוס Docker בזמן אמת"
3. צפה בנתונים:
   - מספר קונטיינרים פועלים
   - מספר קונטיינרים כבויים
   - אחוז זמינות
   - רשימת קונטיינרים

### ✅ סימן הצלחה:
- [ ] הכרטיס מוצג בראש הדף
- [ ] הנתונים מתעדכנים (המתן 5 שניות ורענן)
- [ ] רואה את הסטטוס: "1 פועלים / 5 סה"כ"

### 📊 סטטוס נוכחי (כרגע):
- 🟢 פועלים: 1 (escriptorium_es)
- ⏹️ כבויים: 4 
- 📦 סה"כ: 5
- 📈 זמינות: 20%

---

## צעד 3️⃣: 🔨 בניית מערכת ה-OCR

### מצב: ⬜ לא הושלם

### שלב 1: הכנה

```powershell
cd "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\CORE\eScriptorium_UNIFIED"
```

**בדוק:**
- [ ] הפקודה רצה ללא שגיאה
- [ ] אתה בתיקייה הנכונה

### שלב 2: בדיקת קבצים

```powershell
Get-ChildItem -Filter "docker-compose*.yml" | Select-Object Name
```

**בדוק:**
- [ ] ראית קובץ `docker-compose.yml`
- [ ] יתכן גם `docker-compose.override.yml_example`

### שלב 3: סטטוס נוכחי

```powershell
docker-compose ps
```

**בדוק:**
- [ ] הפקודה רצה
- [ ] ראית רשימת קונטיינרים (או "NAME IMAGE COMMAND...")

### שלב 4: ניקוי (אופציונלי)

```powershell
docker-compose down
```

**בדוק:**
- [ ] הפקודה רצה
- [ ] הקונטיינרים נעצרו

### שלב 5: בנייה והפעלה ⏳ (זה ייקח זמן!)

```powershell
docker-compose up -d --build
```

**המתן 5-15 דקות!**

**צפה בהתקדמות:**
- [ ] רואה הורדות (Downloading...)
- [ ] רואה בנייה (Building...)
- [ ] רואה הפעלה (Starting...)

### שלב 6: מעקב אחר לוגים (אופציונלי)

```powershell
docker-compose logs -f --tail=50
```

**לחץ Ctrl+C כדי לעצור**

**בדוק:**
- [ ] רואה לוגים זורמים
- [ ] אין שגיאות אדומות קריטיות

### שלב 7: אימות הצלחה

```powershell
docker-compose ps
```

**בדוק:**
- [ ] כל הקונטיינרים במצב "Up"
- [ ] אין "Exited" או "Restarting"

### ✅ סימני הצלחה:
- [ ] Build הושלם ללא שגיאות קריטיות
- [ ] כל הקונטיינרים פועלים
- [ ] בדשבורד: "15/15 פועלים" (או דומה)

---

## צעד 4️⃣: 🚀 Deployment והרצה

### מצב: ⬜ לא הושלם

### בדיקת הקונטיינרים העיקריים:

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**חפש:**
- [ ] `web-1` - Up (פורט 8000)
- [ ] `nginx-1` - Up (פורט 80)
- [ ] `db-1` - Up (פורט 5432)
- [ ] `redis-1` - Up (פורט 6379)
- [ ] `elasticsearch-1` - Up (פורט 9200)

### בדיקת Health:

```powershell
docker-compose ps
```

**וודא שכולם healthy (או Up)**

### פתיחת האפליקציה:

1. פתח דפדפן
2. גש ל: http://localhost
3. או: http://localhost:80

**בדוק:**
- [ ] האתר נטען
- [ ] רואה דף כניסה/ראשי
- [ ] אין שגיאות 502/503

### ✅ סימני הצלחה:
- [ ] כל הקונטיינרים פועלים
- [ ] האתר נגיש
- [ ] ניתן להיכנס למערכת

---

## 🎉 סיכום סופי

### כשתסיים את כל הצעדים:

- ✅ טרמינל עובד ומריץ פקודות
- ✅ Docker מנוטר בזמן אמת
- ✅ המערכת נבנתה בהצלחה
- ✅ כל הקונטיינרים פועלים
- ✅ האפליקציה זמינה

### 📊 מה תראה בדשבורד:
- כרטיס Docker יראה: "15/15 פועלים" (100% זמינות)
- כל הקונטיינרים עם ✅
- עדכון אוטומטי כל 5 שניות

---

## 🆘 אם משהו לא עובד

### בעיה: פקודה לא רצה בטרמינל
**פתרון:**
1. בדוק שTerminal Server רץ
2. רענן את הדשבורד (F5)
3. נסה שוב

### בעיה: Docker לא מראה נתונים
**פתרון:**
1. וודא ש-Docker Desktop פועל
2. בדוק ש-docker-monitor.js רץ
3. רענן את הדף

### בעיה: Build נכשל
**פתרון:**
1. הרץ: `docker-compose down`
2. הרץ: `docker system prune -f`
3. נסה שוב: `docker-compose up -d --build`

### בעיה: קונטיינרים נופלים (Exited)
**פתרון:**
1. הרץ: `docker-compose logs [container-name]`
2. חפש שגיאות
3. תקן את הבעיה
4. הרץ: `docker-compose up -d`

---

## 📞 עזרה נוספת

- 📄 `HOW_TO_USE_DASHBOARD.md` - מדריך מלא
- 📄 `QUICK_START_OCR_DASHBOARD.md` - התחלה מהירה
- 🌐 Dashboard: http://localhost:3001/app/dashboard.html

**בהצלחה! 🚀**
