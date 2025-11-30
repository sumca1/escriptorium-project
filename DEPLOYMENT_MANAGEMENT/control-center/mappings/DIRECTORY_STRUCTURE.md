# 🗂️ מבנה תיקיות - Directory Structure

**תאריך עדכון אחרון:** 14 בנובמבר 2025  
**גרסה:** 1.0  
**אחראי:** Control Center Management System

---

## 🎯 מטרת המסמך

מיפוי מלא של מבנה התיקיות של הפרויקט, כולל:
- המבנה המקורי של eScriptorium
- מבנה החבילות החיצוניות
- מבנה 3 הדומיינים החדש
- נקודות חיבור בין תיקיות

---

## 📊 מבנה כללי - Overview

```
escriptorium/
│
├── 📦 CORE/                          ← דומיין 1: קוד אפליקציה
│   ├── eScriptorium_UNIFIED/         ← גרסת העבודה הראשית
│   ├── eScriptorium_CLEAN/           ← גרסת reference
│   └── README.md
│
├── 🏗️ BUILD_MANAGEMENT/              ← דומיין 2: בנייה ו-CI/CD
│   ├── ci-cd/
│   ├── testing/
│   ├── quality/
│   ├── versioning/
│   ├── documentation/
│   └── tools/
│
└── 🚢 DEPLOYMENT_MANAGEMENT/         ← דומיין 3: Docker ופריסה
    ├── docker/
    ├── control-center/               ← ⭐ אתה כאן!
    ├── monitoring/
    ├── scripts/
    └── environments/
```

---

## 📦 CORE - מבנה מפורט

### eScriptorium_UNIFIED (גרסת עבודה)
```
CORE/eScriptorium_UNIFIED/
│
├── app/                              ← Django application
│   ├── escriptorium/
│   │   ├── core/                     ← Core models & views
│   │   ├── users/                    ← User management
│   │   ├── api/                      ← REST API
│   │   ├── locale/                   ← Translations
│   │   │   ├── he/                   ← Hebrew translations
│   │   │   ├── en/
│   │   │   └── ...
│   │   └── settings/
│   │       ├── base.py
│   │       ├── development.py
│   │       └── production.py
│   │
│   └── manage.py
│
├── front/                            ← Vue.js frontend
│   ├── vue/
│   │   ├── components/
│   │   ├── locales/                  ← Frontend translations
│   │   │   ├── he.json               ← Hebrew UI
│   │   │   └── en.json
│   │   ├── router/
│   │   └── store/
│   │
│   ├── dist/                         ← Built files
│   ├── package.json
│   └── webpack.config.js
│
├── static/                           ← Static assets
├── media/                            ← User uploads
├── docker-compose.yml
├── Dockerfile
└── requirements.txt

נקודות חשובות:
✅ התיקייה הראשית לפיתוח
✅ כאן נמצא כל הקוד של eScriptorium
✅ משתלב עם BUILD_MANAGEMENT לבדיקות
✅ משתלב עם DEPLOYMENT_MANAGEMENT לפריסה
```

### eScriptorium_CLEAN (גרסת reference)
```
CORE/eScriptorium_CLEAN/
│
├── (מבנה זהה ל-UNIFIED)
└── README.md

מטרה:
✅ גרסת backup נקייה
✅ reference למבנה מקורי
✅ השוואה במקרה של בעיות
```

---

## 🏗️ BUILD_MANAGEMENT - מבנה מפורט

```
BUILD_MANAGEMENT/
│
├── ci-cd/                            ← GitHub Actions & CI/CD
│   ├── workflows/
│   │   ├── test.yml
│   │   ├── build.yml
│   │   └── deploy.yml
│   ├── scripts/
│   └── README.md
│
├── testing/                          ← Test suites
│   ├── unit/                         ← Unit tests
│   ├── integration/                  ← Integration tests
│   ├── e2e/                          ← End-to-end tests
│   ├── fixtures/                     ← Test data
│   └── README.md
│
├── quality/                          ← Code quality tools
│   ├── linting/
│   │   ├── .eslintrc.js
│   │   ├── .pylintrc
│   │   └── rules/
│   ├── formatting/
│   │   ├── .prettierrc
│   │   └── .editorconfig
│   └── static-analysis/
│
├── versioning/                       ← Version management
│   ├── CHANGELOG.md
│   ├── VERSION
│   └── release-scripts/
│
├── documentation/                    ← Build docs
│   ├── build-process.md
│   ├── testing-guide.md
│   └── ci-cd-setup.md
│
└── tools/                            ← Build utilities
    ├── code-generator/
    ├── migration-tools/
    └── README.md

ממשק ל-CORE:
→ קורא קוד מ-CORE/eScriptorium_UNIFIED/
→ מריץ בדיקות
→ מייצר artifacts

ממשק ל-DEPLOYMENT:
→ שולח artifacts לפריסה
→ מעדכן על הצלחה/כישלון
```

---

## 🚢 DEPLOYMENT_MANAGEMENT - מבנה מפורט

```
DEPLOYMENT_MANAGEMENT/
│
├── docker/                           ← Docker configurations
│   ├── Dockerfile.web
│   ├── Dockerfile.db
│   ├── Dockerfile.nginx
│   ├── docker-compose.dev.yml
│   ├── docker-compose.test.yml
│   ├── docker-compose.prod.yml
│   └── README.md
│
├── control-center/                   ← ⭐ Control Center
│   ├── .instructions/                ← AI chatbot instructions
│   │   ├── START_HERE.instructions.md
│   │   ├── project-manager.instructions.md
│   │   ├── session-tracking.instructions.md
│   │   └── smart-supervisor.instructions.md
│   │
│   ├── mappings/                     ← ⭐ מיפויים (אתה כאן!)
│   │   ├── PACKAGES_REGISTRY.md      ← רישום חבילות
│   │   ├── DIRECTORY_STRUCTURE.md    ← מבנה תיקיות (זה!)
│   │   ├── INTEGRATION_POINTS.md     ← נקודות אינטגרציה
│   │   └── DEPENDENCIES_MAP.md       ← מפת תלויות
│   │
│   ├── modules/                      ← Dashboard modules
│   │   ├── overview.js               ← ✅ פעיל
│   │   ├── files.js                  ← ✅ פעיל
│   │   ├── sync.js                   ← ✅ פעיל
│   │   ├── docs-improved.js          ← ✅ פעיל
│   │   ├── docker.js                 ← 🚧 בפיתוח
│   │   ├── packages.js               ← 🚧 בפיתוח (חדש!)
│   │   └── ...
│   │
│   ├── servers/
│   │   ├── dashboard-server.js       ← HTTP server (8080)
│   │   └── terminal-server.js        ← Terminal API (3001)
│   │
│   ├── scripts/
│   │   ├── START_DASHBOARD.bat
│   │   └── utilities/
│   │       └── auto-start-terminal-server.ps1
│   │
│   ├── docs/
│   │   ├── SESSION_LOG.md
│   │   ├── CURRENT_STATE.md
│   │   └── ...
│   │
│   ├── BUILD_MANAGER_DASHBOARD.html  ← ממשק ויזואלי
│   ├── CHAT_MANAGEMENT_DASHBOARD.html
│   └── README.md
│
├── monitoring/                       ← Health checks & monitoring
│   ├── health-checks/
│   ├── alerts/
│   └── dashboards/
│
├── scripts/                          ← Deployment scripts
│   ├── deploy/
│   │   ├── deploy-dev.ps1
│   │   ├── deploy-test.ps1
│   │   └── deploy-prod.ps1
│   ├── backup/
│   └── rollback/
│
└── environments/                     ← Environment configs
    ├── dev/
    ├── test/
    └── prod/

ממשק ל-CORE:
→ מקבל artifacts מ-BUILD_MANAGEMENT
→ פורס ל-containers
→ מנהל database migrations

ממשק ל-BUILD:
→ מעדכן על סטטוס פריסה
→ מבקש re-build במקרה של כישלון
```

---

## 🔗 נקודות חיבור בין דומיינים

### CORE ↔️ BUILD_MANAGEMENT
```
CORE מספק:
  → קוד מקור (Python, JavaScript)
  → הגדרות (settings, configs)
  → תלויות (requirements.txt, package.json)

BUILD מריץ:
  → Unit tests על CORE
  → Linting על קוד
  → Build של frontend (Vue.js)
  → יצירת artifacts

תיקיות משותפות:
  ❌ אין! שמירה על הפרדה
  
ממשק:
  → BUILD קורא מ-CORE (read-only)
  → BUILD כותב artifacts ל-temp directory
  → BUILD מעדכן DEPLOYMENT על הצלחה
```

### BUILD_MANAGEMENT ↔️ DEPLOYMENT_MANAGEMENT
```
BUILD מספק:
  → Artifacts מוכנים (built files)
  → Test results
  → Quality reports

DEPLOYMENT מקבל:
  → מעתיק artifacts ל-Docker images
  → פורס containers
  → מריץ health checks

תיקיות משותפות:
  ❌ אין! העברה דרך artifacts directory

ממשק:
  → BUILD כותב ל-temp/artifacts/
  → DEPLOYMENT קורא מ-temp/artifacts/
  → שניהם מעדכנים Control Center
```

### CORE ↔️ DEPLOYMENT_MANAGEMENT
```
⚠️ אין קשר ישיר!

CORE → BUILD → DEPLOYMENT

יוצא מן הכלל:
  → Hot reload בסביבת development
  → Logs נאספים מ-CORE ל-DEPLOYMENT monitoring
```

---

## 📦 חבילות חיצוניות - מיקום קבצים

### חבילת BiblIA (לדוגמה - לתכנון)
```
(אופציה 1 - תוך CORE)
CORE/eScriptorium_UNIFIED/
└── app/
    └── biblia/                       ← תיקייה חדשה
        ├── __init__.py
        ├── models.py
        ├── views.py
        ├── ocr_extensions/
        └── hebrew_nlp/

(אופציה 2 - חבילה נפרדת)
CORE/
├── eScriptorium_UNIFIED/
├── eScriptorium_CLEAN/
└── BiblIA_Extensions/                ← תיקייה חדשה
    ├── biblia/
    ├── setup.py
    ├── requirements.txt
    └── README.md

החלטה: טרם התקבלה
יש לתעד ב-PACKAGES_REGISTRY.md
```

---

## 📊 סטטיסטיקות תיקיות

| דומיין | תיקיות | קבצים | גודל | סטטוס |
|--------|---------|-------|------|-------|
| CORE | ~150 | ~2,500 | 275 MB | ✅ פעיל |
| BUILD_MANAGEMENT | ~20 | ~100 | 50 MB | 🔄 בפיתוח |
| DEPLOYMENT_MANAGEMENT | ~30 | ~150 | 5 MB | ✅ פעיל |
| **סה"כ** | **~200** | **~2,750** | **330 MB** | - |

*(מעודכן: 2025-11-14)*

---

## 🎯 תכנון עתידי

### תיקיות מתוכננות:
```
CORE/
└── Extensions/                       ← תיקייה חדשה
    ├── BiblIA/
    ├── CustomModels/
    └── Integrations/

BUILD_MANAGEMENT/
└── performance/                      ← תיקייה חדשה
    ├── benchmarks/
    └── profiling/

DEPLOYMENT_MANAGEMENT/
└── kubernetes/                       ← תיקייה חדשה (עתיד)
    ├── manifests/
    └── helm-charts/
```

---

## 🔗 קישורים נוספים

- [רישום חבילות](./PACKAGES_REGISTRY.md)
- [נקודות אינטגרציה](./INTEGRATION_POINTS.md)
- [מפת תלויות](./DEPENDENCIES_MAP.md)
- [Control Center Dashboard](../BUILD_MANAGER_DASHBOARD.html)

---

## 📝 היסטוריית שינויים

| תאריך | גרסה | שינוי | מבצע |
|-------|------|-------|------|
| 2025-11-14 | 1.0 | יצירה ראשונית עם מבנה 3 דומיינים | Control Center |

---

**הערה:** מסמך זה משתלב עם הדשבורד הויזואלי ומתעדכן אוטומטית.
