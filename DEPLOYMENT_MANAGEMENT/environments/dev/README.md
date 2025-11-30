# 🟢 DEV Environment - סביבת פיתוח

## 🎯 מטרה
סביבה לפיתוח מהיר עם **hot-reload** - כל שינוי בקוד נראה מיד!

## ⚡ תכונות
- ✅ **Hot Reload** - שינויים מיידיים ללא build
- ✅ **Debug Mode** - לוגים מפורטים
- ✅ **Direct Volume Mount** - קוד מחובר ישירות
- ✅ **Fast Startup** - ~30 שניות
- ⚠️ **לא מאובטח** - רק לפיתוח מקומי!

## 🚀 הפעלה מהירה

### הפעלה ראשונה:
```powershell
cd DEPLOYMENT_MANAGEMENT\environments\dev
docker-compose up -d --build
```

Build: **~2-3 דקות** (פעם אחת!)

### הפעלה רגילה:
```powershell
docker-compose up -d
```

Start: **~10 שניות** ⚡

### עצירה:
```powershell
docker-compose down
```

## 🔗 נקודות גישה

- **Django Admin:** http://localhost:8000/admin
- **API:** http://localhost:8000/api/
- **Frontend:** http://localhost:8080
- **Redis:** localhost:6379
- **PostgreSQL:** localhost:5432

## 💻 עבודה יומיומית

### 1. ערוך קוד ב-VS Code:
```powershell
code ../../../CORE/eScriptorium_UNIFIED/app/views.py
```

### 2. שמור (Ctrl+S)

### 3. רענן דפדפן
**זהו! השינוי חי!** ✨

### אין צורך ב:
- ❌ docker-compose build
- ❌ docker-compose restart
- ❌ המתנה

## 📊 ניטור

### צפייה בלוגים:
```powershell
docker-compose logs -f web
```

### סטטוס:
```powershell
docker-compose ps
```

### כניסה לקונטיינר:
```powershell
docker-compose exec web bash
```

## 🐛 פתרון בעיות

### בעיה: שינויים לא נראים
```powershell
# וודא שvolumes מחוברים:
docker-compose exec web ls -la /usr/src/app
# אמור לראות את הקבצים שלך
```

### בעיה: Port תפוס
```powershell
# שחרר port:
docker stop $(docker ps -q --filter "publish=8000")
```

### בעיה: Database ריק
```powershell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## ⏱️ זמני ביצוע

| פעולה | זמן |
|-------|-----|
| Build ראשון | 2-3 דקות |
| Start עוקב | 10 שניות |
| שינוי קוד → רואה תוצאה | **5 שניות** ⚡ |
| Stop | 5 שניות |

## 🔄 Workflow יומי

```
09:00 → docker-compose up -d (10 שניות)
09:01 → code CORE/eScriptorium_UNIFIED/
09:01-17:00 → כתיבת קוד + שמירה + רענון דפדפן
17:00 → docker-compose down (5 שניות)
```

**אין builds במהלך היום!** 🎉

## 📁 מבנה קבצים

```
dev/
├── docker-compose.yml    ← הגדרות containers
├── .env.dev             ← משתני סביבה
└── README.md            ← המדריך הזה
```

## 🎓 טיפים

1. **פתח 2 terminals:**
   - Terminal 1: `docker-compose logs -f web`
   - Terminal 2: עבודה רגילה

2. **השתמש ב-Django Debug Toolbar:**
   - נטען אוטומטית ב-dev
   - רואה queries, timing, etc.

3. **Hot Reload לא עובד ל:**
   - שינויים ב-settings.py (צריך restart)
   - שינויים ב-requirements.txt (צריך build)
   - שינויים ב-Dockerfile (צריך build)

## ⚠️ חשוב!

**סביבה זו לפיתוח בלבד!**

- ❌ לא להריץ בייצור
- ❌ לא מאובטח
- ❌ לא מאופטם
- ✅ מושלם לפיתוח מהיר

---

**רוצה סביבת בדיקות?** → עבור ל-`../test/`  
**מוכן לייצור?** → עבור ל-`../prod/`
