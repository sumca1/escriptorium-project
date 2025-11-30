# 💎 פירורי מידע טכניים חשובים מ-eScriptorium BiblIA

> **מקור**: חולצו מ-22 קבצי תיעוד נוספים  
> **מטרה**: לשמור מידע טכני חיוני שלא נכלל במדריך הראשי

---

## 🐳 ארכיטקטורת Docker מפורטת

### מבנה השירותים המלא
```
nginx:8081 → web:8000 (Django)
           → channelserver:5000 (WebSockets)
           ↓
         db:5432 (PostgreSQL)
         redis:6379 (Cache & Broker)
         ↓
         celery-main (High priority tasks)
         celery-live (Real-time tasks)  
         celery-low-priority (Background)
         celery-gpu (OCR processing)
```

### תפקידי שירותים:
- **nginx**: Proxy + SSL + Static files
- **web**: Django app + API + Auth
- **channelserver**: WebSocket server עבור updates בזמן אמת
- **celery-gpu**: עיבוד OCR עם GPU acceleration
- **flower:5555**: ניטור Celery tasks

---

## 🔧 תיקונים טכניים קריטיים

### 1. תיקון JSON Serialization Error
```python
# app/escriptorium/settings.py - הוסף:
import json
from django.utils.functional import Promise
from django.utils.encoding import force_str

class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_str(obj)
        return super().default(obj)

# החלף encoder ב-REST framework
import rest_framework.utils.json
rest_framework.utils.json.JSONEncoder = LazyEncoder
```

### 2. תיקון Docker Compose Warnings
```yaml
# מחק את השורה הזו מ-docker-compose.yml:
version: "3.9"  # ← מחק

# השאר רק:
services:
  web:
    # ...
```

### 3. תיקון Frontend Build Issues
```powershell
# Script: front/fix_frontend_build.ps1
cd front
Remove-Item -Recurse -Force dist, tmp_build -ErrorAction SilentlyContinue
npm run build -- --outputDir tmp_build
if (Test-Path "tmp_build/index.html") {
    Move-Item tmp_build dist
    docker-compose up -d web nginx
    Write-Host "✅ Frontend fixed successfully"
}
```

---

## 🛠️ כלי אוטומציה מתקדמים

### מערכת תחזוקה חדשה (במקום פקודות ידניות):

#### הגישה הישנה (מורכבת):
```powershell
docker exec -u root escriptorium-web-1 python manage.py compilemessages -l he
docker restart escriptorium-web-1
python remove_po_duplicates.py
cd front && npm install && npm run start
```

#### הגישה החדשה (פשוטה):
```powershell
py -3 app/maintenance_check.py --fix --docker
```

### סקריפטי הפעלה מתקדמים:
```powershell
# start_escriptorium.ps1 עם פרמטרים:
-SkipChecks        # דלג על בדיקות מערכת  
-RebuildFrontend   # בנה מחדש ממשק
-RestartDB         # אתחל מסד נתונים
-Help              # עזרה מפורטת
```

---

## 🌐 פרטי מערכת התרגומים

### מבנה קבצים:
```
frontend: vue/locales/he.json (850+ מפתחות)
backend:  app/locale/he/LC_MESSAGES/django.po
bridge:   vue/exports/i18nInjector.js (נוצר אוטומטית)
```

### דוגמת שימוש ב-Namespaces:
```javascript
// במקום:
$t('Task state')

// השתמש:
$t('documentTasks.Task state')
```

### תהליך Build אוטומטי:
1. עריכת `he.json`
2. `npm run build` → יוצר `i18nInjector.js`
3. `registerMessages()` נקרא אוטומטית ברכיבים

---

## 🗂️ קבצים חדשים שנוצרו לפרויקט

### קבצי הפעלה:
- `start-escriptorium.bat` - הפעלה פשוטה
- `start-escriptorium.ps1` - עם פרמטרים
- `start_escriptorium.ps1` - מקיף ביותר

### כלי עזר:
- `app/create_superuser.py` - יצירת משתמש אוטומטית
- `app/tools/compile_he_messages.py` - קומפול עברית
- `app/tools/i18n_settings.py` - הגדרות בינלאומיות

### קבצי תצורה:
- `variables.env` - הגדרות BiblIA
- `requirements-local.txt` - תלויות פיתוח
- `docker-compose.yml` - קונפיגורציה מעודכנת

---

## ⚙️ הגדרות קריטיות

### נתיבי מודלים ונתונים:
```
models: G:\OCR_Arabic_Testing\models
training_data: G:\OCR_Arabic_Testing\training_data
media: escriptorium/media/
static_collected: escriptorium/static_collected/
```

### משתמש ניהול ברירת מחדל:
```
username: koperberg
password: koperberg123
email: koperberg@biblia-project.com
permissions: Staff + Superuser
```

### פורטים:
```
Main UI: localhost:8081 (nginx)
Admin: localhost:8081/admin
Maintenance: localhost:8081/system/maintenance/
Development: localhost:9000 (direct Django)
Flower (Celery): localhost:5555
```

---

## 🔍 פקודות ניפוי שגיאות

### בדיקת תקינות מערכת:
```powershell
py -3 escriptorium_cli.py status      # סטטוס כללי
py -3 escriptorium_cli.py audit       # ביקורת מקיפה
py -3 escriptorium_cli.py docker logs # לוגי Docker
```

### בדיקת Kraken OCR:
```powershell
cd app
python test_kraken_detailed.py
```

### בדיקת תרגומים:
```powershell
py -3 escriptorium_cli.py translation check
py -3 escriptorium_cli.py translation validate
```

---

## 📋 סימוכין לקבצים מעניינים

מהקבצים שנבדקו, אלו הכי שווים לעיון עתידי:
- `DOCKER_PATHS_GUIDE.md` - פירוט מלא של Docker
- `QUICK_FIXES.md` - תיקונים טכניים ספציפיים
- `NEW_MAINTENANCE_APPROACH.md` - כלי אוטומציה
- `DOCUMENTATION_INDEX.md` - מפה של כל הכלים

---

**סיכום**: הפירורים האלה מכילים מידע טכני מתקדם שלא נכלל במדריך הראשי, אבל חשוב לשמירה למקרה של פתרון בעיות עמוקות או פיתוח מתקדם.