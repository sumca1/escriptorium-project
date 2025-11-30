# 🔴 PROD Environment - סביבת ייצור

## ⚠️ אזהרה!
**זוהי סביבת PRODUCTION - משתמשים אמיתיים!**

## 🎯 מטרה
סביבה לייצור - **מאובטחת, מאופטמת, יציבה**

## 🔒 תכונות אבטחה
- ✅ **Read-only filesystem** - אין כתיבה לקוד
- ✅ **No privileges** - containers לא-root
- ✅ **Secrets management** - סיסמאות בטוחות
- ✅ **SSL/TLS** - HTTPS בלבד
- ✅ **Resource limits** - הגבלת CPU/Memory
- ✅ **Health checks** - ניטור אוטומטי
- ✅ **Automated backups** - גיבוי יומי

## ⚡ אופטימיזציה
- ✅ **4 uwsgi workers** - ביצועים מקסימליים
- ✅ **Static files optimized** - compression + caching
- ✅ **Database tuning** - PostgreSQL מאופטם
- ✅ **Redis persistence** - appendonly mode

## 🚀 הפעלה (פעם אחת!)

### לפני ההפעלה הראשונה:

1. **ערוך .env.prod:**
```powershell
code .env.prod
# שנה את כל ה-CHANGE_ME!
```

2. **הכן SSL certificates:**
```powershell
# אם יש לך certificates:
cp cert.pem ssl_certs/
cp key.pem ssl_certs/

# או צור self-signed (לא מומלץ!):
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl_certs/key.pem -out ssl_certs/cert.pem
```

### Build + Deploy:
```powershell
cd DEPLOYMENT_MANAGEMENT\environments\prod
docker-compose up -d --build
```

Build: **~5-7 דקות** (optimization מלא!)

### הרצת migrations:
```powershell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```

## 🔗 נקודות גישה

- **Application:** <https://your-domain.com>
- **Admin:** <https://your-domain.com/admin>
- **Health check:** <https://your-domain.com/health>

## 📊 ניטור

### בדיקת health:
```powershell
docker-compose ps
# כולם אמורים להיות healthy!
```

### לוגים:
```powershell
# לוגים אחרונים:
docker-compose logs --tail=100 web

# לוגים חיים:
docker-compose logs -f web nginx

# לוגי שגיאות בלבד:
docker-compose logs web | grep ERROR
```

### בדיקת ביצועים:
```powershell
# CPU/Memory:
docker stats escriptorium_prod_web

# Database connections:
docker-compose exec db psql -U escriptorium -c "SELECT count(*) FROM pg_stat_activity;"
```

## 💾 גיבויים

### Backup אוטומטי:
- רץ כל יום ב-02:00
- נשמר ב-`postgres_backup` volume
- שומר 7 ימים אחרונים

### Backup ידני:
```powershell
docker-compose exec db pg_dump -U escriptorium escriptorium_prod | gzip > backup_$(Get-Date -Format 'yyyyMMdd').sql.gz
```

### Restore:
```powershell
gunzip < backup_20251130.sql.gz | docker-compose exec -T db psql -U escriptorium escriptorium_prod
```

## 🔄 עדכון (Deploy חדש)

### 1. גרסה חדשה מוכנה ב-test:
```powershell
# ודא שטסטים עברו!
cd ..\test
docker-compose exec web pytest
# ✅ All passed
```

### 2. Backup לפני עדכון:
```powershell
cd ..\prod
docker-compose exec db pg_dump -U escriptorium escriptorium_prod | gzip > backup_before_update_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql.gz
```

### 3. Pull קוד חדש:
```powershell
cd ..\..\..\CORE\eScriptorium_UNIFIED
git pull origin main
```

### 4. Build + Deploy:
```powershell
cd ..\..\..\DEPLOYMENT_MANAGEMENT\environments\prod
docker-compose up -d --build
```

### 5. Migrations:
```powershell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
```

### 6. בדוק:
```
https://your-domain.com/health
```

## ⏱️ זמני ביצוע

| פעולה | זמן |
|-------|-----|
| Build מלא | 5-7 דקות |
| Start | 30 שניות |
| Health check stabilization | 60 שניות |
| Backup | 1-5 דקות |
| Deploy חדש (עם downtime) | ~8 דקות |
| Zero-downtime deploy | ~15 דקות |

## 🚨 פתרון בעיות

### Container לא healthy:
```powershell
# בדוק logs:
docker-compose logs web

# רענן:
docker-compose restart web

# אם לא עוזר - rebuild:
docker-compose up -d --build web
```

### Database connection errors:
```powershell
# בדוק connections:
docker-compose exec db psql -U escriptorium -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# אם יותר מדי - restart:
docker-compose restart web
```

### מחסור ב-memory:
```powershell
# הוסף swap או הגדל limits ב-docker-compose.yml
```

### SSL errors:
```powershell
# ודא certificates תקינים:
openssl x509 -in ssl_certs/cert.pem -text -noout
```

## 📁 מבנה קבצים

```
prod/
├── docker-compose.yml    ← הגדרות containers
├── .env.prod            ← משתני סביבה (סודי!)
├── .env.prod.example    ← תבנית
├── ssl_certs/           ← SSL certificates
│   ├── cert.pem
│   └── key.pem
└── README.md            ← המדריך הזה
```

## 🎓 Best Practices

1. **אל תריץ ישירות על server:**
   - השתמש ב-CI/CD (GitHub Actions)
   - Deploy אוטומטי אחרי tests

2. **ניטור מתמיד:**
   - Sentry לשגיאות
   - Prometheus למטריקות
   - Uptime monitoring (UptimeRobot)

3. **גיבויים:**
   - יומי אוטומטי ✅
   - לפני כל deploy ✅
   - העתק לcloud storage ✅

4. **עדכונים:**
   - תכנן maintenance window
   - הודע למשתמשים
   - בדוק ב-test קודם!

5. **אבטחה:**
   - עדכן passwords כל 90 ימים
   - SSL certificates לפני תפוגה
   - Docker images עדכניים

## ⚠️ אזהרות קריטיות!

**❌ לעולם אל:**
- תריץ עם DEBUG=True
- תשתמש בסיסמאות חלשות
- תעלה .env.prod ל-Git
- תעשה changes ישירות ב-prod
- תשכח backups

**✅ תמיד:**
- בדוק ב-test קודם
- עשה backup לפני deploy
- נטר logs
- תעדכן dependencies
- שמור .env.prod מאובטח

## 🔐 אבטחת .env.prod

```powershell
# הצפן:
gpg -c .env.prod

# שמור git:
git add .env.prod.gpg
git commit -m "Update prod env (encrypted)"

# פענח בשרת:
gpg -d .env.prod.gpg > .env.prod
```

---

**צריך לפתח?** → עבור ל-`../dev/`  
**צריך לבדוק?** → עבור ל-`../test/`  
**בעיה ב-prod?** → 🚨 **עשה backup מיידי!**
