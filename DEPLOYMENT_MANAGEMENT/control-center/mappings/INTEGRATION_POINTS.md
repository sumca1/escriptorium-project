# 🔗 נקודות אינטגרציה - Integration Points

**תאריך עדכון אחרון:** 14 בנובמבר 2025  
**גרסה:** 1.0  
**אחראי:** Control Center Management System

---

## 🎯 מטרת המסמך

תיעוד מלא של כל נקודות החיבור והממשקים בין:
- 3 הדומיינים (CORE, BUILD, DEPLOYMENT)
- חבילות פנימיות וחיצוניות
- שרתים ושירותים
- מערכות ניהול

---

## 📊 מפת אינטגרציה כללית

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 User/Developer                        │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│           🚢 DEPLOYMENT_MANAGEMENT                           │
│                 Control Center                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Dashboard (8080) ◄──► Terminal Server (3001)     │     │
│  │         ▲                        ▲                  │     │
│  │         │                        │                  │     │
│  │         ▼                        ▼                  │     │
│  │  Modules ◄──► Docs ◄──► Mappings                   │     │
│  └────────────────────────────────────────────────────┘     │
│               │                                              │
│               ▼                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Docker Compose ◄──► Monitoring                    │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│           🏗️ BUILD_MANAGEMENT                                │
│  ┌────────────────────────────────────────────────────┐     │
│  │  CI/CD ◄──► Testing ◄──► Quality                   │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│           📦 CORE                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Django ◄──► Vue.js ◄──► Database                  │     │
│  │    ▲           ▲            ▲                       │     │
│  │    │           │            │                       │     │
│  │    ▼           ▼            ▼                       │     │
│  │  API ◄──► Celery ◄──► Redis                        │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔌 אינטגרציות בתוך DEPLOYMENT_MANAGEMENT

### 1. Control Center ↔️ Dashboard Server (פנימי)
```yaml
סוג: HTTP/WebSocket
פורט: 8080
כיוון: דו-כיווני
פרוטוקול: HTTP/1.1, WebSocket

נקודות קצה (Endpoints):
  GET /dashboard.html:
    תיאור: טעינת הדשבורד הראשי
    response: HTML + JavaScript
    
  GET /api/modules/:name:
    תיאור: טעינת מודול דינמי
    params: name (string)
    response: JavaScript module
    
  GET /api/docs/:file:
    תיאור: קריאת קובץ תיעוד
    params: file (string)
    response: Markdown content
    
  GET /api/mappings/:type:
    תיאור: קריאת מיפוי
    params: type (packages|structure|integration|dependencies)
    response: JSON/Markdown
    
  WebSocket /ws/updates:
    תיאור: עדכונים בזמן אמת
    events: file-change, build-status, deployment-status

דוגמת קריאה:
  fetch('http://localhost:8080/api/mappings/packages')
    .then(r => r.json())
    .then(data => console.log(data))

סטטוס: ✅ פעיל
```

### 2. Control Center ↔️ Terminal Server
```yaml
סוג: REST API
פורט: 3001
כיוון: Control Center → Terminal Server
פרוטוקול: HTTP/1.1

נקודות קצה:
  POST /execute:
    תיאור: הרצת פקודה בטרמינל
    body: {command: string, cwd: string}
    response: {output: string, exitCode: number}
    
  GET /status:
    תיאור: סטטוס השרת
    response: {status: 'running', uptime: number}

דוגמת שימוש:
  POST http://localhost:3001/execute
  Body: {
    "command": "Get-ChildItem",
    "cwd": "C:/projects"
  }

סטטוס: 🚧 חלקי (חסר /execute)
תלויות: PowerShell 7+
```

### 3. Dashboard ↔️ Modules
```yaml
סוג: JavaScript Module Loading
כיוון: Dashboard → Modules
פרוטוקול: ES6 Modules

מודולים זמינים:
  - overview.js: ✅ פעיל
  - files.js: ✅ פעיל
  - sync.js: ✅ פעיל
  - docs-improved.js: ✅ פעיל
  - docker.js: 🚧 בפיתוח
  - packages.js: 🔄 מתוכנן (חדש!)
  - mappings.js: 🔄 מתוכנן (חדש!)

טעינת מודול:
  import('./modules/overview.js')
    .then(module => module.init())

ממשק מודול (interface):
  export function init() { ... }
  export function render(container) { ... }
  export function cleanup() { ... }

סטטוס: ✅ פעיל (4/7 מודולים)
```

### 4. Dashboard ↔️ Docs System
```yaml
סוג: File Reading
כיוון: דו-כיווני
פרוטוקול: HTTP GET

קבצים נתמכים:
  - docs/SESSION_LOG.md
  - docs/CURRENT_STATE.md
  - docs/PROJECT_MANAGER.md
  - docs/ROADMAP.md
  - mappings/*.md (חדש!)
  - .instructions/*.md

API:
  GET /api/docs/:file
  Response: {content: string, lastModified: timestamp}

סנכרון:
  → File Watcher מזהה שינויים
  → Sync script מעדכן dashboard
  → WebSocket מודיע ללקוח
  → UI מתרענן אוטומטית

סטטוס: ✅ פעיל
תדירות: Real-time (2s polling)
```

### 5. Modules ↔️ Mappings (חדש!)
```yaml
סוג: Data Integration
כיוון: Modules → Mappings
פרוטוקול: JavaScript/JSON

מטרה:
  מודולים יכולים לקרוא מיפויים ולהציג אותם בצורה ויזואלית

דוגמה:
  // מודול packages.js
  fetch('/api/mappings/packages')
    .then(r => r.json())
    .then(packages => {
      renderPackagesTable(packages);
      renderDependencyGraph(packages);
    })

מודולים מתוכננים:
  - packages.js: הצגת רישום חבילות
  - structure.js: הצגת עץ תיקיות
  - integration.js: הצגת מפת אינטגרציה
  - dependencies.js: גרף תלויות

סטטוס: 🔄 בתכנון
```

---

## 🔌 אינטגרציות בין דומיינים

### DEPLOYMENT ↔️ BUILD_MANAGEMENT

#### 1. Artifacts Pipeline
```yaml
סוג: File Transfer
כיוון: BUILD → DEPLOYMENT
פרוטוקול: File System

תהליך:
  1. BUILD מריץ בדיקות על CORE
  2. BUILD יוצר artifacts (built files)
  3. BUILD כותב ל-temp/artifacts/
  4. BUILD מעדכן Control Center (webhook)
  5. DEPLOYMENT קורא מ-temp/artifacts/
  6. DEPLOYMENT פורס ל-Docker
  7. DEPLOYMENT מעדכן Control Center

תיקיות:
  BUILD כותב:     temp/artifacts/build-{timestamp}/
  DEPLOYMENT קורא: temp/artifacts/latest/

API:
  POST /api/build-complete
  Body: {
    buildId: string,
    status: 'success' | 'failure',
    artifacts: string[],
    timestamp: number
  }

סטטוס: 🔄 מתוכנן
```

#### 2. Status Updates
```yaml
סוג: Event Notifications
כיוון: דו-כיווני
פרוטוקול: WebSocket / HTTP Webhooks

אירועים:
  BUILD → DEPLOYMENT:
    - build_started
    - tests_passed / tests_failed
    - artifacts_ready
    - quality_check_complete
    
  DEPLOYMENT → BUILD:
    - deployment_started
    - deployment_success / deployment_failed
    - health_check_passed
    - rollback_requested

דוגמה:
  ws.send(JSON.stringify({
    event: 'build_started',
    buildId: '20251114-001',
    branch: 'main'
  }))

סטטוס: 🔄 מתוכנן
```

### DEPLOYMENT ↔️ CORE

#### 1. Docker Deployment
```yaml
סוג: Container Orchestration
כיוון: DEPLOYMENT → CORE
פרוטוקול: Docker Compose

תהליך:
  1. DEPLOYMENT מקבל artifacts מ-BUILD
  2. DEPLOYMENT בונה Docker images
  3. DEPLOYMENT מריץ docker-compose up
  4. CORE containers עולים
  5. DEPLOYMENT מריץ health checks
  6. DEPLOYMENT מעדכן Control Center

קובץ תצורה:
  docker/docker-compose.yml

נקודות חיבור:
  - Web: 8082 (nginx)
  - Database: 5432 (PostgreSQL)
  - Cache: 6379 (Redis)
  - Queue: 5555 (Celery Flower)

סטטוס: ✅ פעיל
```

#### 2. Logs & Monitoring
```yaml
סוג: Log Aggregation
כיוון: CORE → DEPLOYMENT
פרוטוקול: Docker Logs API

תהליך:
  1. CORE כותב logs (Django, Celery)
  2. Docker captures stdout/stderr
  3. DEPLOYMENT קורא logs (docker logs)
  4. DEPLOYMENT מנתח logs
  5. DEPLOYMENT מציג ב-Control Center

API:
  GET /api/logs/:container
  Response: {
    logs: string[],
    errors: number,
    warnings: number
  }

סטטוס: 🚧 חלקי
```

### BUILD ↔️ CORE

#### 1. Code Analysis
```yaml
סוג: Static Analysis
כיוון: BUILD → CORE (read-only)
פרוטוקול: File System

תהליך:
  1. BUILD קורא קוד מ-CORE
  2. BUILD מריץ linters (eslint, pylint)
  3. BUILD מריץ tests
  4. BUILD מייצר דוחות
  5. BUILD מעדכן Control Center

כלים:
  - ESLint (JavaScript)
  - Pylint (Python)
  - Black (Python formatter)
  - Prettier (JavaScript formatter)

דוחות:
  BUILD_MANAGEMENT/quality/reports/
    ├── lint-report.json
    ├── test-results.xml
    └── coverage.html

סטטוס: 🔄 מתוכנן
```

#### 2. Test Execution
```yaml
סוג: Test Runner
כיוון: BUILD → CORE (read-only)
פרוטוקול: pytest, jest

תהליך:
  1. BUILD קורא tests מ-CORE
  2. BUILD מריץ pytest (Python)
  3. BUILD מריץ jest (JavaScript)
  4. BUILD אוסף coverage
  5. BUILD מייצר דוחות

דוגמה:
  cd CORE/eScriptorium_UNIFIED
  pytest app/tests/ --cov=app --cov-report=html

סטטוס: 🔄 מתוכנן
```

---

## 🔌 אינטגרציות חיצוניות

### 1. GitHub (עתידי)
```yaml
סוג: CI/CD Integration
כיוון: GitHub ↔️ BUILD_MANAGEMENT
פרוטוקול: GitHub Actions

תהליך:
  1. Push to GitHub
  2. GitHub Actions מופעלים
  3. Actions מריצים BUILD_MANAGEMENT/ci-cd/
  4. תוצאות נשלחות ל-Control Center

סטטוס: 🔄 מתוכנן
```

### 2. Docker Hub (עתידי)
```yaml
סוג: Container Registry
כיוון: DEPLOYMENT → Docker Hub
פרוטוקול: Docker Push/Pull

תהליך:
  1. DEPLOYMENT בונה images
  2. DEPLOYMENT מתייג (tag) images
  3. DEPLOYMENT דוחף (push) ל-Docker Hub
  4. Production שולף (pull) מ-Docker Hub

סטטוס: 🔄 מתוכנן
```

---

## 📋 טבלת סיכום

| אינטגרציה | כיוון | פרוטוקול | סטטוס |
|-----------|-------|----------|-------|
| Dashboard ↔️ Server | דו-כיווני | HTTP/WS | ✅ פעיל |
| Dashboard ↔️ Terminal | חד-כיווני | HTTP | 🚧 חלקי |
| Dashboard ↔️ Modules | חד-כיווני | ES6 | ✅ פעיל |
| Dashboard ↔️ Docs | דו-כיווני | HTTP | ✅ פעיל |
| Modules ↔️ Mappings | חד-כיווני | JSON | 🔄 מתוכנן |
| BUILD → DEPLOYMENT | חד-כיווני | Files | 🔄 מתוכנן |
| DEPLOYMENT ↔️ BUILD | דו-כיווני | WS/HTTP | 🔄 מתוכנן |
| DEPLOYMENT → CORE | חד-כיווני | Docker | ✅ פעיל |
| CORE → DEPLOYMENT | חד-כיווני | Logs | 🚧 חלקי |
| BUILD → CORE | קריאה | FS | 🔄 מתוכנן |

---

## 🎯 תכנון עתידי

### אינטגרציות חדשות מתוכננות:
1. **Real-time Collaboration** - WebRTC בין צ'אטבוטים
2. **API Gateway** - ממשק מאוחד לכל הדומיינים
3. **Event Bus** - RabbitMQ לתקשורת async
4. **Metrics Collection** - Prometheus + Grafana

---

## 🔗 קישורים נוספים

- [רישום חבילות](./PACKAGES_REGISTRY.md)
- [מבנה תיקיות](./DIRECTORY_STRUCTURE.md)
- [מפת תלויות](./DEPENDENCIES_MAP.md)
- [Control Center Dashboard](../BUILD_MANAGER_DASHBOARD.html)

---

## 📝 היסטוריית שינויים

| תאריך | גרסה | שינוי | מבצע |
|-------|------|-------|------|
| 2025-11-14 | 1.0 | יצירה ראשונית | Control Center |

---

**הערה:** מסמך זה מתעדכן אוטומטית ומשתלב עם הדשבורד הויזואלי.
