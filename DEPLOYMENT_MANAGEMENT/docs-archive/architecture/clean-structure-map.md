# 📊 מפת מבנה eScriptorium_CLEAN - Structure Map

> **תאריך סריקה:** 12 נובמבר 2025  
> **מטרה:** ניתוח מפורט של המבנה לצורך מיגרציה ל-UNIFIED

---

## 📈 סטטיסטיקה כללית

| תיקייה | קבצים | גודל (MB) | עדיפות להעתקה |
|---------|-------|-----------|---------------|
| **app/** | 1,287 | 135.07 | 🔴 קריטי |
| **front/** | 53,107 | 331.44 | 🔴 קריטי |
| **backups/** | 498 | 3,823.71 | 🟢 לא להעתיק |
| **node_modules/** | 10,424 | 63.85 | 🟡 npm install |
| **scripts/** | 408 | 3.85 | 🔴 קריטי |
| **docs/** | 405 | 4.30 | 🟡 ארגון מחדש |
| **translations/** | 19 | 0.71 | 🔴 קריטי |
| **config/** | 14 | 0.57 | 🔴 קריטי |
| **tests/** | 26 | 0.31 | 🟡 חשוב |
| **.github/** | 135 | 3.30 | 🟡 חשוב |

**סה"כ:** ~66,000 קבצים, ~4,600 MB

---

## 🔴 קריטי - חובה להעתיק

### 1. app/ (Django Application)
**גודל:** 1,287 קבצים, 135 MB  
**תיאור:** הקוד Python של Django - הלב של המערכת

**תת-תיקיות חשובות:**
- `app/escriptorium/` - Django project ראשי
- `app/core/` - Models, Views, URLs
- `app/api/` - REST API
- `app/locale/` - תרגומי Django (.po files)
- `app/static/` - Static files
- `app/templates/` - Django templates

**פעולה:**
```powershell
# העתקה מלאה, מינוס cache
robocopy eScriptorium_CLEAN\app eScriptorium_UNIFIED\app /E /XD __pycache__ .pytest_cache
```

---

### 2. front/ (Vue.js Frontend)
**גודל:** 53,107 קבצים, 331 MB  
**תיאור:** Frontend Vue.js עם כל הקומפוננטות

**⚠️ שים לב:** הרוב זה node_modules (10,424 קבצים, 64 MB)

**תת-תיקיות חשובות:**
- `front/vue/` - Vue components
- `front/vue/locales/` - תרגומים (he.json)
- `front/dist/` - Built files (אם קיים)
- `front/src/` - Source files
- `package.json` - Dependencies

**פעולה:**
```powershell
# העתקה ללא node_modules
robocopy eScriptorium_CLEAN\front eScriptorium_UNIFIED\front /E /XD node_modules dist

# אחר כך בנייה ב-UNIFIED:
cd eScriptorium_UNIFIED\front
npm install
npm run build
```

---

### 3. scripts/ (Automation Scripts)
**גודל:** 408 קבצים, 3.85 MB  
**תיאור:** 240+ סקריפטי PowerShell + Python לאוטומציה

**קטגוריות:**
- Build scripts: `build-*.ps1`, `compile-*.ps1`
- Deploy scripts: `deploy-*.ps1`, `restart-*.ps1`
- Test scripts: `*test*.ps1`, `check*.ps1`
- Maintenance: `backup*.ps1`, `cleanup*.ps1`
- Utilities: כלים שונים

**פעולה:**
```powershell
# ✅ לא להעתיק עיוור! לארגן לפי קטגוריות:

# Build
New-Item -Path eScriptorium_UNIFIED\scripts\build -ItemType Directory -Force
Copy-Item eScriptorium_CLEAN\scripts\build-*.ps1 eScriptorium_UNIFIED\scripts\build\
Copy-Item eScriptorium_CLEAN\scripts\compile-*.ps1 eScriptorium_UNIFIED\scripts\build\

# Deploy
New-Item -Path eScriptorium_UNIFIED\scripts\deploy -ItemType Directory -Force
Copy-Item eScriptorium_CLEAN\scripts\deploy-*.ps1 eScriptorium_UNIFIED\scripts\deploy\
Copy-Item eScriptorium_CLEAN\scripts\restart-*.ps1 eScriptorium_UNIFIED\scripts\deploy\

# Testing
New-Item -Path eScriptorium_UNIFIED\scripts\testing -ItemType Directory -Force
Copy-Item eScriptorium_CLEAN\scripts\*test*.ps1 eScriptorium_UNIFIED\scripts\testing\
Copy-Item eScriptorium_CLEAN\scripts\check*.ps1 eScriptorium_UNIFIED\scripts\testing\

# Maintenance
New-Item -Path eScriptorium_UNIFIED\scripts\maintenance -ItemType Directory -Force
Copy-Item eScriptorium_CLEAN\scripts\backup*.ps1 eScriptorium_UNIFIED\scripts\maintenance\
Copy-Item eScriptorium_CLEAN\scripts\cleanup*.ps1 eScriptorium_UNIFIED\scripts\maintenance\
```

---

### 4. translations/ (Translation Hub)
**גודל:** 19 קבצים, 0.71 MB  
**תיאור:** מערכת התרגום האחודה עם 2,295 תרגומים

**קבצים:**
- ✅ `he.json` - כבר הועתק
- ✅ `translation_loader.py` - כבר הועתק
- ✅ `README.md` - כבר הועתק
- ✅ סקריפטים נוספים

**סטטוס:** ✅ כבר הועבר ל-UNIFIED!

---

### 5. config/ (Configuration)
**גודל:** 14 קבצים, 0.57 MB  
**תיאור:** קבצי הגדרות קריטיים

**קבצים חשובים:**
- `variables.env` - 🔐 משתני סביבה (סודות!)
- `uwsgi.ini` - הגדרות uwsgi
- `settings/` - Django settings
- `.env`, `.env.example`

**פעולה:**
```powershell
robocopy eScriptorium_CLEAN\config eScriptorium_UNIFIED\config /E
```

---

### 6. docker/ (Docker Configs)
**תיאור:** קבצי Docker

**קבצים:**
- `docker-compose.integrated.yml` - 16 services
- `docker-compose.dev.yml` - Development
- `Dockerfile`
- `nginx.conf` - הגדרות Nginx

**סטטוס:** ✅ חלקית הועתק - צריך להשלים

---

## 🟡 חשוב - להעתיק + לארגן

### 7. docs/ (Documentation)
**גודל:** 405 קבצים, 4.30 MB  
**בעיה:** תיעוד מפוזר בכל הפרויקט

**פעולה:**
```powershell
# לא להעתיק הכל! לארגן לפי נושאים:

# Architecture
New-Item eScriptorium_UNIFIED\docs\architecture -ItemType Directory -Force
Copy-Item eScriptorium_CLEAN\docs\ARCHITECTURE*.md eScriptorium_UNIFIED\docs\architecture\

# Guides
New-Item eScriptorium_UNIFIED\docs\guides -ItemType Directory -Force
Copy-Item eScriptorium_CLEAN\docs\*GUIDE*.md eScriptorium_UNIFIED\docs\guides\

# API
New-Item eScriptorium_UNIFIED\docs\api -ItemType Directory -Force
Copy-Item eScriptorium_CLEAN\docs\API*.md eScriptorium_UNIFIED\docs\api\

# Deployment
New-Item eScriptorium_UNIFIED\docs\deployment -ItemType Directory -Force
Copy-Item eScriptorium_CLEAN\docs\DEPLOY*.md eScriptorium_UNIFIED\docs\deployment\
```

---

### 8. tests/ (Tests)
**גודל:** 26 קבצים, 0.31 MB  
**תיאור:** טסטים של המערכת

**פעולה:**
```powershell
robocopy eScriptorium_CLEAN\tests eScriptorium_UNIFIED\tests /E
```

---

### 9. .github/ (GitHub Configs)
**גודל:** 135 קבצים, 3.30 MB  
**תיאור:** הוראות AI, workflows, templates

**תת-תיקיות:**
- `.github/instructions/` - ✅ כבר הועתק
- `.github/workflows/` - CI/CD
- `.github/ISSUE_TEMPLATE/`

**פעולה:**
```powershell
# instructions כבר הועתק, השלם את השאר
robocopy eScriptorium_CLEAN\.github eScriptorium_UNIFIED\.github /E
```

---

## 🟢 לא להעתיק

### 10. backups/ (3,823 MB!)
**סיבה:** קבצי גיבוי ישנים, גדולים מדי

**פעולה:** דלג!

---

### 11. node_modules/ (10,424 קבצים)
**סיבה:** יווצר מחדש עם `npm install`

**פעולה:** דלג! הרץ `npm install` ב-UNIFIED

---

### 12. eScriptorium_V2/ (851 קבצים, 54 MB)
**סיבה:** גרסה ישנה, לא רלוונטי

**פעולה:** דלג!

---

## 📋 רשימת קבצים בודדים חשובים (שורש)

**קבצי הגדרה:**
- `.dockerignore`
- `.gitignore`
- `.flake8`
- `.isort.cfg`
- `LICENSE`
- `README.md`
- `requirements.txt` (אם קיים)

**קבצי מצב:**
- `CURRENT_STATE.md` → העתק ל-`management/`
- `SESSION_LOG.md` → העתק ל-`management/`

**סקריפטים ראשיים:**
- `build.py` (אם קיים)
- `docker_commands.py`
- `manage.py` (Django)

**פעולה:**
```powershell
# העתק קבצי config
Copy-Item eScriptorium_CLEAN\.dockerignore eScriptorium_UNIFIED\
Copy-Item eScriptorium_CLEAN\.gitignore eScriptorium_UNIFIED\
Copy-Item eScriptorium_CLEAN\.flake8 eScriptorium_UNIFIED\
Copy-Item eScriptorium_CLEAN\LICENSE eScriptorium_UNIFIED\

# העתק קבצי מצב לתיקיית management
Copy-Item eScriptorium_CLEAN\CURRENT_STATE.md eScriptorium_UNIFIED\management\
Copy-Item eScriptorium_CLEAN\SESSION_LOG.md eScriptorium_UNIFIED\management\
```

---

## 🎯 סיכום - סדר העתקה מומלץ

### שלב 1: Core Files (קריטי)
1. ✅ config/ - הגדרות
2. ✅ app/ - Django code
3. ✅ translations/ - כבר הועתק

### שלב 2: Frontend
4. ✅ front/ (ללא node_modules)
5. ⏭️ npm install + build

### שלב 3: Infrastructure
6. ✅ docker/ - קבצי Docker
7. ✅ nginx/ - הגדרות nginx

### שלב 4: Automation
8. ⏭️ scripts/ - ארגון מחדש לקטגוריות
9. ⏭️ automation/ - סקריפטי high-level

### שלב 5: Support Files
10. ⏭️ tests/ - טסטים
11. ⏭️ docs/ - תיעוד מאורגן
12. ⏭️ .github/ - GitHub configs

### שלב 6: Management
13. ⏭️ CURRENT_STATE.md → management/
14. ⏭️ SESSION_LOG.md → management/

---

## 🔍 Dependencies Map - תלויות

### Django Dependencies (Python)
- Django 3.x+
- PostgreSQL
- Redis
- Celery
- uwsgi
- ראה: `app/requirements.txt` או `pyproject.toml`

### Frontend Dependencies (Node)
- Vue.js 2.x
- Webpack
- Babel
- ראה: `front/package.json`

### System Dependencies
- Docker
- Docker Compose
- PostgreSQL client
- Redis
- Nginx

---

## ⚠️ נקודות לשים לב

### 1. Paths בקוד
חיפוש לביצוע:
```powershell
# חפש paths ישנים שצריך לעדכן
grep -r "eScriptorium_CLEAN" eScriptorium_UNIFIED/
```

### 2. Environment Variables
וודא עדכון ב-`config/variables.env`:
- `BASE_DIR`
- `STATIC_ROOT`
- `MEDIA_ROOT`
- כל path אבסולוטי

### 3. Docker Networks
שמות networks ב-docker-compose עשויים להשתנות

### 4. Ports
UNIFIED יכול להיות על port שונה:
- CLEAN: 8085
- UNIFIED: 8086? (להחליט)

---

**גרסה:** 1.0  
**סטטוס:** ✅ מפת מבנה מוכנה  
**צעד הבא:** תוכנית העתקה מפורטת

