# 🕸️ מפת תלויות - Dependencies Map

**תאריך עדכון אחרון:** 14 בנובמבר 2025  
**גרסה:** 1.0  
**אחראי:** Control Center Management System

---

## 🎯 מטרת המסמך

מיפוי מלא של כל התלויות בפרויקט:
- תלויות בין דומיינים
- תלויות בין חבילות
- תלויות חיצוניות (npm, pip)
- תלויות runtime (services)

---

## 📊 גרף תלויות ראשי

```
                    ┌──────────────┐
                    │    User      │
                    └──────┬───────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │     DEPLOYMENT_MANAGEMENT            │
        │      (Control Center)                │
        └──────┬───────────────────────┬───────┘
               │                       │
               ▼                       ▼
    ┌─────────────────┐    ┌─────────────────┐
    │ BUILD_MANAGEMENT│    │   Docker Compose│
    └────────┬────────┘    └────────┬────────┘
             │                      │
             ▼                      ▼
      ┌─────────────┐       ┌─────────────┐
      │    Tests    │       │ Containers  │
      └─────┬───────┘       └─────┬───────┘
            │                     │
            └──────────┬──────────┘
                       ▼
                 ┌───────────┐
                 │   CORE    │
                 │(eScriptorium)│
                 └─────┬─────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌────────┐   ┌─────────┐   ┌────────┐
    │ Django │   │ Vue.js  │   │Database│
    └────────┘   └─────────┘   └────────┘
```

---

## 🔗 תלויות בין דומיינים

### CORE Dependencies
```yaml
תלויות פנימיות:
  אין: CORE עצמאי

תלויות חיצוניות:
  - Python 3.10+
  - Django 4.2+
  - PostgreSQL 13+
  - Redis 7+
  - Celery 5+
  - Node.js 18+ (לבניית frontend)
  - Vue.js 3.x

משתמשים ב-CORE:
  - BUILD_MANAGEMENT (קורא קוד לבדיקות)
  - DEPLOYMENT_MANAGEMENT (פורס containers)

סטטוס: ✅ יציב
```

### BUILD_MANAGEMENT Dependencies
```yaml
תלויות פנימיות:
  → CORE (read-only): קריאת קוד לבדיקות

תלויות חיצוניות:
  - pytest (Python testing)
  - jest (JavaScript testing)
  - eslint (JavaScript linting)
  - pylint (Python linting)
  - coverage.py (code coverage)

משתמשים ב-BUILD:
  - DEPLOYMENT_MANAGEMENT (מקבל artifacts)

סטטוס: 🔄 בפיתוח
```

### DEPLOYMENT_MANAGEMENT Dependencies
```yaml
תלויות פנימיות:
  → BUILD_MANAGEMENT: מקבל artifacts
  → CORE: פורס containers

תלויות חיצוניות:
  - Docker Engine 20+
  - Docker Compose 2+
  - Node.js 18+ (Control Center servers)
  - PowerShell 7+ (automation scripts)

משתמשים ב-DEPLOYMENT:
  - Users (דרך Control Center)
  - CI/CD (אוטומציה)

סטטוס: ✅ פעיל
```

---

## 📦 תלויות חבילות CORE

### Python Dependencies (requirements.txt)
```txt
# Django Core
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.0

# Database
psycopg2-binary==2.9.9
redis==5.0.1

# Celery
celery==5.3.4
kombu==5.3.4

# OCR & Image Processing
Pillow==10.1.0
pytesseract==0.3.10

# NLP (Hebrew)
hebrew-tokenizer==2.3.0

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1

סה"כ: ~45 חבילות
סטטוס: ✅ מתועד ב-requirements.txt
```

### JavaScript Dependencies (package.json)
```json
{
  "dependencies": {
    "vue": "^3.3.8",
    "vue-router": "^4.2.5",
    "vuex": "^4.1.0",
    "axios": "^1.6.2",
    "marked": "^10.0.0"
  },
  "devDependencies": {
    "webpack": "^5.89.0",
    "webpack-cli": "^5.1.4",
    "babel-loader": "^9.1.3",
    "vue-loader": "^17.3.1",
    "eslint": "^8.54.0"
  }
}

סה"כ: ~30 חבילות
סטטוס: ✅ מתועד ב-package.json
```

---

## 🐳 תלויות Runtime (Docker Services)

### docker-compose.yml
```yaml
services:
  web:
    depends_on:
      - db
      - redis
    
  db:
    image: postgres:13
    # אין תלויות
  
  redis:
    image: redis:7-alpine
    # אין תלויות
  
  celery:
    depends_on:
      - db
      - redis
  
  nginx:
    depends_on:
      - web

סדר הפעלה:
  1. db, redis (במקביל)
  2. web, celery (אחרי 1)
  3. nginx (אחרי 2)

סטטוס: ✅ מתועד
```

---

## 🔗 תלויות Control Center

### Modules Dependencies
```yaml
overview.js:
  תלויות: אין
  סטטוס: ✅ עצמאי

files.js:
  תלויות: 
    - dashboard-server.js (file listing API)
  סטטוס: ✅ פעיל

sync.js:
  תלויות:
    - file-watcher (מזהה שינויים)
    - sync-docs-to-dashboard.ps1
  סטטוס: ✅ פעיל

docs-improved.js:
  תלויות:
    - dashboard-server.js (docs API)
    - marked.js (markdown parsing)
  סטטוס: ✅ פעיל

docker.js:
  תלויות:
    - terminal-server.js (/execute endpoint)
    - Docker Engine
  סטטוס: 🚧 חלקי (חסר /execute)

packages.js (מתוכנן):
  תלויות:
    - mappings/PACKAGES_REGISTRY.md
    - dashboard-server.js
  סטטוס: 🔄 בתכנון

mappings.js (מתוכנן):
  תלויות:
    - mappings/*.md
    - d3.js (גרפים)
  סטטוס: 🔄 בתכנון
```

### Servers Dependencies
```yaml
dashboard-server.js:
  תלויות:
    - Node.js 18+
    - http module (built-in)
    - fs/promises module (built-in)
  פורט: 8080
  סטטוס: ✅ פעיל

terminal-server.js:
  תלויות:
    - Node.js 18+
    - child_process module (built-in)
    - PowerShell 7+
  פורט: 3001
  סטטוס: 🚧 חלקי
```

---

## 📊 מטריצת תלויות

### תלויות בין מודולים
| מודול | overview | files | sync | docs | docker | packages |
|-------|----------|-------|------|------|--------|----------|
| overview | - | ❌ | ❌ | ❌ | ❌ | ❌ |
| files | ❌ | - | ❌ | ❌ | ❌ | ❌ |
| sync | ❌ | ✅ | - | ❌ | ❌ | ❌ |
| docs | ❌ | ❌ | ❌ | - | ❌ | ❌ |
| docker | ❌ | ❌ | ❌ | ❌ | - | ❌ |
| packages | ❌ | ❌ | ❌ | ✅ | ❌ | - |

**מסקנה:** מודולים עצמאיים - ✅ אדריכלות טובה!

### תלויות בין שרתים
| שרת | dashboard | terminal |
|-----|-----------|----------|
| dashboard | - | ❌ |
| terminal | ❌ | - |

**מסקנה:** שרתים עצמאיים - ✅ אדריכלות טובה!

---

## 🚨 תלויות בעייתיות / חסרות

### 1. Terminal Server - /execute endpoint
```yaml
בעיה: 
  docker.js זקוק ל-/execute אבל הוא לא מוטמע

פתרון:
  השלם את terminal-server.js:
    POST /execute
    Body: {command: string, cwd: string}
    Response: {output: string, exitCode: number}

עדיפות: 🔴 HIGH
תלוי ב: PowerShell 7+
משפיע על: docker.js module
```

### 2. Marked.js - חסר ב-docs-improved.js
```yaml
בעיה:
  docs-improved.js מצפה ל-marked.js לפרסור markdown
  אבל הוא לא נטען

פתרון:
  הוסף ב-dashboard.html:
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

עדיפות: 🟡 MEDIUM
תלוי ב: CDN או local copy
משפיע על: docs-improved.js rendering
```

### 3. D3.js - חסר למודול mappings (עתידי)
```yaml
בעיה:
  mappings.js יזדקק ל-d3.js לגרפי תלויות
  אבל עדיין לא נוסף

פתרון:
  הוסף ב-dashboard.html:
    <script src="https://d3js.org/d3.v7.min.js"></script>

עדיפות: 🟢 LOW (מתוכנן)
תלוי ב: D3.js v7+
משפיע על: mappings.js graphs
```

---

## 🔄 תלויות מעגליות (Circular Dependencies)

### בדיקה:
```
CORE → BUILD → DEPLOYMENT → CORE?
  ❌ לא! DEPLOYMENT לא תלוי ב-CORE ישירות
  ✅ DEPLOYMENT רק פורס containers

CORE → BUILD → CORE?
  ❌ לא! BUILD רק קורא (read-only)
  ✅ אין כתיבה חזרה

DEPLOYMENT ↔️ BUILD?
  ❌ לא! חד-כיווני:
  ✅ BUILD → DEPLOYMENT (artifacts)
  ✅ DEPLOYMENT מעדכן סטטוס (לא תלות)
```

**מסקנה:** ✅ אין תלויות מעגליות!

---

## 📦 תלויות חיצוניות (External)

### CDNs
```yaml
בשימוש:
  - (כרגע אין)

מתוכנן:
  - marked.js (markdown)
  - d3.js (graphs)
  - chart.js (charts)

חלופות:
  → העתק לוקלית (offline support)
  → npm install + webpack bundle
```

### APIs חיצוניים
```yaml
בשימוש:
  - (כרגע אין)

מתוכנן:
  - GitHub API (CI/CD status)
  - Docker Hub API (image info)
```

---

## 🎯 המלצות

### 1. תיעוד אוטומטי
```bash
# צור סקריפט לחילוץ תלויות:
python scripts/extract-dependencies.py

# פלט:
# - dependencies.json
# - dependency-graph.svg
```

### 2. בדיקת גרסאות
```bash
# בדוק תאימות גרסאות:
npm audit
pip check
```

### 3. עדכון תלויות
```bash
# עדכן בזהירות:
npm update
pip install --upgrade -r requirements.txt
```

---

## 🔗 קישורים נוספים

- [רישום חבילות](./PACKAGES_REGISTRY.md)
- [מבנה תיקיות](./DIRECTORY_STRUCTURE.md)
- [נקודות אינטגרציה](./INTEGRATION_POINTS.md)
- [Control Center Dashboard](../BUILD_MANAGER_DASHBOARD.html)

---

## 📝 היסטוריית שינויים

| תאריך | גרסה | שינוי | מבצע |
|-------|------|-------|------|
| 2025-11-14 | 1.0 | יצירה ראשונית | Control Center |

---

**הערה:** מסמך זה מתעדכן אוטומטית ומשתלב עם הדשבורד הויזואלי.
