# 📖 eScriptorium BiblIA - מדריך מלא ומאוחד

> **🎯 גרסה מאוחדת ונקייה - הכל במקום אחד**  
> **תאריך עדכון אחרון:** 22 אוקטובר 2025  
> **חדש:** השוואת מנועי OCR (Kraken vs Tesseract)

---

## 📋 תוכן העניינים
1. [סקירה כללית](#סקירה-כללית)
2. [התקנה והפעלה](#התקנה-והפעלה)
3. [כלי CLI מתקדמים](#כלי-cli-מתקדמים)
4. [מערכת התרגומים](#מערכת-התרגומים)
5. [פתרון בעיות](#פתרון-בעיות)
6. [פיתוח ותחזוקה](#פיתוח-ותחזוקה)

### 🚨 **מדריכי עזרה מיוחדים**
- 🛠️ [מדריך פתרון בעיות מפורט](./TROUBLESHOOTING_GUIDE.md)
- 🚨 [פתרון עמוד עריכה ריק](./FRONTEND_FILES_FIX_GUIDE.md)
- 🔬 [השוואת מנועי OCR](./COMPARISON_FEATURE_STATUS.md) ← **חדש 22 אוק' 2025!**

---

## 🎯 סקירה כללית

eScriptorium היא פלטפורמת OCR (זיהוי תווים אופטי) מתקדמת המיועדת לעבודה עם כתבי יד היסטוריים וטקסטים עתיקים. גרסה זו מותאמת במיוחד לעבודה עם טקסטים עבריים ופרוייקט BiblIA.

### ✨ תכונות עיקריות:
- 🔤 **זיהוי OCR מתקדם** באמצעות Kraken 6.0.0 ו-Tesseract
- 🔬 **השוואת מנועים** - Kraken vs Tesseract side-by-side ← **חדש!**
- 🌐 **ממשק דו-לשוני** (עברית ואנגלית) עם תמיכת RTL מלאה
- 📚 **ניהול פרוייקטים** ומסמכים מתקדם
- ✏️ **עורך טקסט חכם** לתיקון וחיפוש
- 🎯 **אימון מודלים** מותאמים אישית
- 📊 **ניתוח איכות** וסטטיסטיקות מפורטות (CER, WER, Accuracy)
- 🛠️ **כלי CLI מתקדמים** לניהול המערכת
- 💾 **ייצוא מתקדם** - CSV, JSON, ALTO XML

### 🏗️ ארכיטקטורה טכנית:
- **Backend**: Django 4.2.13 + PostgreSQL
- **Frontend**: Vue.js 3 + Chart.js עם תמיכה בעברית
- **OCR Engines**: Kraken 6.0.0 + Tesseract 5.x + PyTorch
- **Infrastructure**: Docker + nginx

---

## 🚀 התקנה והפעלה

### דרישות מערכת
- **Python 3.11+**
- **Node.js 22.11.0+**
- **Docker & Docker Compose**
- **Windows 10/11**

### הפעלה מהירה - 3 שלבים

#### 🚀 שלב 1: הפעלת השרת
```powershell
cd "G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\app"
py -3 manage.py runserver 8082
```

#### 🌐 שלב 2: גישה למערכת
- **כתובת**: http://localhost:8082
- **משתמש**: `koperberg`
- **סיסמה**: `koperberg123`
- **הרשאות**: Staff + Superuser

#### 🛠️ שלב 3: גישה לכלי ניהול
- **פאנל ניהול**: http://localhost:8082/admin
- **כלי תחזוקה**: http://localhost:8082/system/maintenance/

### הפעלה מתקדמת (אוטומטית)
```powershell
# מתיקיית escriptorium הראשית:
.\start_escriptorium.ps1

# עם פרמטרים:
.\start_escriptorium.ps1 -SkipChecks      # דלג על בדיקות
.\start_escriptorium.ps1 -RebuildFrontend # בנה מחדש UI
.\start_escriptorium.ps1 -RestartDB       # אתחל DB
```

---

## 🛠️ כלי CLI מתקדמים

### 3 דרכי גישה לכלים

#### 1. 🖥️ CLI ישיר (מהיר ביותר)
```powershell
cd escriptorium
py -3 escriptorium_cli.py status
py -3 escriptorium_cli.py audit
py -3 escriptorium_cli.py maintenance --fix
```

#### 2. 🎯 Django Management Commands
```powershell
cd escriptorium/app
py -3 manage.py escriptorium_cli status
py -3 manage.py escriptorium_cli docker web
py -3 manage.py escriptorium_cli translation check
```

#### 3. 🌐 ממשק Web (Staff בלבד)
`http://localhost:8082/system/maintenance/`

### פקודות זמינות

#### 📊 מידע מערכת
```powershell
py -3 escriptorium_cli.py status    # סטטוס כללי (ברירת מחדל)
py -3 escriptorium_cli.py audit     # ביקורת מקיפה
py -3 escriptorium_cli.py help      # עזרה מפורטת
```

#### 🔧 תחזוקה ותיקונים
```powershell
py -3 escriptorium_cli.py maintenance         # בדיקה יומית
py -3 escriptorium_cli.py maintenance --fix   # תיקונים אוטומטיים
py -3 escriptorium_cli.py fix                 # תיקונים מהירים
```

#### 🐳 ניהול Docker
```powershell
py -3 escriptorium_cli.py docker status    # סטטוס containers
py -3 escriptorium_cli.py docker web       # הפעלת web services
py -3 escriptorium_cli.py docker logs      # צפיה בלוגים
py -3 escriptorium_cli.py docker restart   # הפעלה מחדש
```

#### 🌐 כלי תרגומים
```powershell
py -3 escriptorium_cli.py translation check     # בדיקת תרגומים
py -3 escriptorium_cli.py translation compile   # קומפול Django
py -3 escriptorium_cli.py translation validate  # אימות תרגומים
```

### תרחישי שימוש נפוצים

#### 🌅 בדיקה יומית
```powershell
py -3 escriptorium_cli.py status
py -3 escriptorium_cli.py maintenance --fix
```

#### 🚀 הפעלת המערכת
```powershell
py -3 escriptorium_cli.py docker web
py -3 escriptorium_cli.py docker logs
```

#### 🔧 פתרון בעיות
```powershell
py -3 escriptorium_cli.py audit
py -3 escriptorium_cli.py fix
py -3 escriptorium_cli.py maintenance --fix --docker
```

---

## 🌐 מערכת התרגומים

### ארכיטקטורה
- **Frontend**: `vue/locales/he.json` (850+ מפתחות)
- **Backend**: `app/locale/he/LC_MESSAGES/django.po`
- **כיסוי עברי**: 99.8% מושלם
- **נבי אוטומטי**: דרך `i18nInjector.js`

### קבצים חשובים
```
front/vue/locales/he.json              # תרגומי Vue.js
app/locale/he/LC_MESSAGES/django.po    # תרגומי Django
front/vue/exports/i18nInjector.js      # גשר התרגומים (נוצר אוטומטית)
```

### הוספת תרגומים חדשים

#### Frontend (Vue.js)
1. ערוך `front/vue/locales/he.json`
2. הוסף מפתחות מובנים: `"section.component.action": "התרגום"`
3. בנה מחדש: `npm run build`
4. השתמש ברכיבים: `$t('section.component.action')`

#### Backend (Django)
```powershell
cd app
python manage.py makemessages -l he    # חילוץ מחרוזות חדשות
# ערוך django.po
python manage.py compilemessages        # קומפול
```

### פתרון בעיות תרגום

#### תרגום לא מופיע
1. **בדוק קבצי מקור**: וודא שהמפתח קיים ב-`he.json`
2. **namespace**: השתמש בנכון: `$t('namespace.key')`
3. **build**: הרץ `npm run build`
4. **קונסול דפדפן**: חפש שגיאות $t()

#### מפתח חסר ב-he.json אבל קיים ב-django.po
1. העתק מ-django.po
2. הוסף ל-namespace המתאים ב-he.json
3. עדכן Vue component לשימוש ב-namespace
4. בנה מחדש

---

## 🔧 פתרון בעיות

### בעיות נפוצות

#### שגיאת חיבור למסד נתונים
```powershell
.\start_escriptorium.ps1 -RestartDB
# או
py -3 escriptorium_cli.py docker restart
```

#### Frontend לא נטען / UI שבור
```powershell
.\start_escriptorium.ps1 -RebuildFrontend
# או מהתיקיה front/:
cd front
./fix_frontend_build.ps1
```

#### בעיות Kraken OCR
```powershell
cd app
python test_kraken_detailed.py
```

#### בעיות הרשאות PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 🚨 עמודי עריכה לא טוענים נתונים (404 על קבצי JS/CSS)
**תסמינים**: עמוד `/document/X/part/Y/edit/` נטען אבל העורך ריק או לא פעיל

**אבחון מהיר**:
```powershell
# בדוק לוגי nginx לשגיאות 404
docker logs escriptorium_clean-nginx-1 --tail=10
```
אם יש שגיאות כמו:
- `GET /static/editor.js HTTP/1.1" 404`
- `GET /static/css/rtl-hebrew.css HTTP/1.1" 404`

**פתרון מהיר** (העתקה ידנית של קבצים):
```powershell
# 1. וודא ש-Docker רץ
docker-compose up -d

# 2. העתק קבצי פרונט-אנד חיוניים
docker cp front/dist/editor.js escriptorium_clean-web-1:/usr/src/app/static/
docker cp front/dist/editor.css escriptorium_clean-web-1:/usr/src/app/static/
docker cp front/dist/imagesPage.js escriptorium_clean-web-1:/usr/src/app/static/
docker cp front/dist/imagesPage.css escriptorium_clean-web-1:/usr/src/app/static/

# 3. יצור קובץ תמיכה בעברית (אם חסר)
echo '/* RTL Hebrew Support */ .rtl { direction: rtl; text-align: right; }' > rtl-hebrew.css
docker cp rtl-hebrew.css escriptorium_clean-web-1:/usr/src/app/static/css/

# 4. רענן דפדפן ובדוק שהעמוד עובד
```

**פתרון קבוע** (תיקון Docker Volume):
```yaml
# הוסף לdocker-compose.override.yml:
services:
  web:
    volumes:
      - ./front/dist:/usr/src/app/static/js:ro
      - ./app/static:/usr/src/app/static:rw
```

**הערה חשובה**: בעיה זו נפוצה כי תיקיית `front/dist` לא מועתקת אוטומטית לקונטיינר Docker.

### לוגים וניפוי

#### מיקום לוגים
- **Django**: בטרמינל השרת
- **PostgreSQL**: `docker logs escriptorium-postgres`
- **Frontend**: Developer Tools בדפדפן
- **nginx**: `docker logs escriptorium-nginx`

#### פקודות ניפוי
```powershell
py -3 escriptorium_cli.py audit        # ביקורת מערכת
py -3 escriptorium_cli.py docker logs  # לוגי Docker
py -3 manage.py check                   # בדיקת Django
```

---

## 🔬 פיתוח ותחזוקה

### מצב פיתוח
```powershell
# Frontend watch mode
cd front
npm run start

# Django debug (בטרמינל נפרד)
cd app
python manage.py runserver
```

### בדיקות איכות
```powershell
cd front
npm run i18n:check        # בדיקת תרגומים

cd app  
python manage.py check    # בדיקת Django
python manage.py test     # הרצת בדיקות
```

### גיבויים
```powershell
# גיבוי מסד נתונים
docker exec escriptorium-postgres pg_dump -U postgres escriptorium > backup.sql

# גיבוי קבצי המערכת
py -3 escriptorium_cli.py backup
```

### מבנה הפרויקט
```
escriptorium/
├── app/                          # Django backend
│   ├── apps/                    # אפליקציות Django
│   │   ├── core/               # אפליקציה מרכזית
│   │   ├── users/              # ניהול משתמשים
│   │   └── reporting/          # דיווחים
│   ├── escriptorium/           # הגדרות פרויקט
│   ├── locale/he/              # תרגומי Backend
│   └── manage.py               # כלי ניהול Django
├── front/                       # Vue.js frontend
│   ├── vue/                    # קבצי Vue.js
│   │   ├── locales/           # תרגומי Frontend
│   │   ├── components/        # רכיבי Vue
│   │   └── exports/           # גשרי מידע
│   ├── dist/                  # קבצים מובנים
│   └── package.json           # תלויות npm
├── media/                      # קבצי משתמש
├── static_collected/           # קבצים סטטיים
├── escriptorium_cli.py        # כלי CLI ראשי
└── start_escriptorium.ps1     # סקריפט הפעלה
```

---

## 📚 משאבים נוספים

### תיעוד טכני
- [Kraken OCR Documentation](https://kraken.re/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Vue.js Documentation](https://vuejs.org/)

### כלים מומלצים לפיתוח
- **IDE**: VSCode עם הרחבות Python ו-Vue
- **Browser**: Firefox/Chrome עם Developer Tools
- **Git**: לניהול גרסאות (מומלץ מאוד!)

---

## 🎉 סיכום

מערכת eScriptorium BiblIA מספקת פלטפורמה מושלמת לעבודה עם טקסטים עבריים עתיקים:

✅ **הפעלה קלה** - 3 שלבים פשוטים  
✅ **כלי ניהול מתקדמים** - CLI ו-Web interface  
✅ **תמיכה מלאה בעברית** - UI ו-OCR  
✅ **גמישות טכנית** - Docker + Python + Vue.js  
✅ **תיעוד מקיף** - הכל במדריך אחד זה  

---

**eScriptorium BiblIA** - פיתוח מתקדם לזיהוי טקסטים עבריים עתיקים 📜✨

> 💡 **טיפ**: שמור מדריך זה בטאבים - הוא מכיל את כל מה שתצטרך!