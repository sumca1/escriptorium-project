# 🌍 סביבות עבודה - eScriptorium

## 🎯 3 סביבות נפרדות

```
CORE/eScriptorium_UNIFIED/ (קוד אחד)
            ↓
    ┌───────┼───────┐
    ↓       ↓       ↓
  🟢 dev  🟡 test 🔴 prod
```

## 📊 השוואה

| תכונה | 🟢 DEV | 🟡 TEST | 🔴 PROD |
|-------|--------|---------|---------|
| **מטרה** | פיתוח מהיר | בדיקות | ייצור |
| **קוד** | Hot-reload | Frozen | Frozen |
| **Build** | 2-3 דקות | 2-3 דקות | 5-7 דקות |
| **שינוי קוד** | מיידי! | צריך rebuild | צריך rebuild |
| **Debug** | ✅ כן | ❌ לא | ❌ לא |
| **אבטחה** | ❌ לא | בינוני | ✅ מלא |
| **Port** | 8000 | 8081 | 80/443 |

## 🚀 התחלה מהירה

### אפשרות 1: עם סקריפט (מומלץ!)
```powershell
.\switch-environment.ps1 -Environment dev -Build -Up
```

### אפשרות 2: ידני
```powershell
cd DEPLOYMENT_MANAGEMENT\environments\dev
docker-compose up -d --build
```

## 📁 מבנה

```
environments/
├── dev/                    🟢 פיתוח
│   ├── docker-compose.yml  ← Hot-reload enabled
│   ├── .env.dev
│   └── README.md
├── test/                   🟡 בדיקות
│   ├── docker-compose.yml  ← Build frozen
│   ├── .env.test
│   └── README.md
└── prod/                   🔴 ייצור
    ├── docker-compose.yml  ← Production optimized
    ├── .env.prod           ← KEEP SECRET!
    └── README.md
```

## 🔄 Workflow טיפוסי

### יום פיתוח רגיל:

```
09:00 → התחל dev:
cd environments\dev
docker-compose up -d

09:01-17:00 → כתוב קוד:
code ..\..\..\CORE\eScriptorium_UNIFIED\
(שמור → רענן דפדפן → רואה שינויים!)

17:00 → בדוק ב-test:
cd ..\test
docker-compose up -d --build
docker-compose exec web pytest

17:10 → אם עבר → commit:
git add .
git commit -m "New feature"
git push

17:11 → סגור:
docker-compose down
```

### Deploy לייצור:

```
1. ודא test עובד ✅
2. Backup prod database
3. cd environments\prod
4. docker-compose up -d --build
5. migrations + collectstatic
6. בדוק health check
```

## 🎓 מדריכים מפורטים

- **🟢 DEV:** קרא `dev/README.md`
- **🟡 TEST:** קרא `test/README.md`
- **🔴 PROD:** קרא `prod/README.md`

## ⚠️ חשוב!

1. **אל תערבב סביבות!**
   - כל סביבה = network נפרד
   - כל סביבה = database נפרד
   - כל סביבה = ports שונים

2. **תמיד בדוק ב-test לפני prod!**

3. **prod = רק דרך CI/CD**
   - לא לעשות changes ידניים

## 🆘 עזרה מהירה

### כל הסביבות רצות?
```powershell
docker ps --filter name=escriptorium
```

### עצור הכל:
```powershell
docker stop $(docker ps -q --filter name=escriptorium)
```

### נקה הכל:
```powershell
docker-compose -f dev/docker-compose.yml down -v
docker-compose -f test/docker-compose.yml down -v
docker-compose -f prod/docker-compose.yml down -v
```

---

**מתחיל?** → התחל ב-`dev/`  
**מוכן לבדוק?** → עבור ל-`test/`  
**Deploy?** → עבור ל-`prod/` (זהירות!)
