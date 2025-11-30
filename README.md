# escriptorium-project
# 🎯 eScriptorium Project

> **Organized into 3 Independent Domains**

---

## 🌅 Welcome! Where Would You Like to Go?

### 📦 [CORE](CORE/README.md) - Application Code
**Work on:** eScriptorium features, bug fixes, functionality, BiblIA extensions

**Contains:**
- Django backend
- Vue.js frontend
- Language support modules
- Application Docker configuration

🔗 [Enter CORE →](CORE/README.md)

---

### 🏗️ [BUILD_MANAGEMENT](BUILD_MANAGEMENT/README.md) - Build & CI/CD
**Work on:** Build processes, testing, code quality, releases, CI/CD pipelines

**Contains:**
- GitHub Actions & CI/CD configs
- Unit, integration, E2E tests
- Linting & code quality tools
- Version management & releases
- Development documentation

🔗 [Enter BUILD_MANAGEMENT →](BUILD_MANAGEMENT/README.md)

---

### 🚢 [DEPLOYMENT_MANAGEMENT](DEPLOYMENT_MANAGEMENT/README.md) - Docker & Deployment
**Work on:** Docker containers, deployment, monitoring, production operations

**Contains:**
- Docker configurations
- Control Center dashboard
- Health checks & monitoring
- Deployment automation scripts
- Environment configurations (dev/test/prod)

🔗 [Enter DEPLOYMENT_MANAGEMENT →](DEPLOYMENT_MANAGEMENT/README.md)

---

## 🤖 For ChatBots & AI Assistants

**IMPORTANT:** When entering this directory, always ask the user which domain they want to work in!

### Greeting Script:
```
User: "בוקר טוב" or enters escriptorium/

Bot: "בוקר טוב! 🌅

      במה תרצה להתקדם היום?
      
      1️⃣ 📦 CORE - עבודה על קוד eScriptorium
         (features, bug fixes, BiblIA extensions)
      
      2️⃣ 🏗️ BUILD - ניהול בניית הפרויקט  
         (CI/CD, testing, code quality, releases)
      
      3️⃣ 🚢 DEPLOY - ניהול Docker ופריסה
         (containers, monitoring, deployment)
      
      הקלד: core / build / deploy"
```

### Context Loading:
- **If user chooses CORE:** Load CORE/README.md + CORE/ARCHITECTURE.md
- **If user chooses BUILD:** Load BUILD_MANAGEMENT/README.md + CI/CD docs
- **If user chooses DEPLOY:** Load DEPLOYMENT_MANAGEMENT/README.md + docker configs

### Golden Rule:
🚫 **Never mix contexts!** 
- In DEPLOY domain? Don't suggest code changes!
- In CORE domain? Don't suggest docker configs!
- In BUILD domain? Don't touch deployment or core code!

---

## 📊 Project Statistics

| Domain | Purpose | Size | Status |
|--------|---------|------|--------|
| CORE | Application Code | ~275 MB | ✅ Active |
| BUILD_MANAGEMENT | Build & CI/CD | ~50 MB | 🔄 Growing |
| DEPLOYMENT_MANAGEMENT | Docker & Ops | ~5 MB | ✅ Active |

---

## 🗺️ Navigation Map

```
escriptorium/
│
├── 📦 CORE/
│   ├── eScriptorium_UNIFIED/     ← Main application
│   ├── eScriptorium_CLEAN/       ← Reference copy
│   └── README.md
│
├── 🏗️ BUILD_MANAGEMENT/
│   ├── ci-cd/                    ← GitHub Actions
│   ├── testing/                  ← Test suites
│   ├── quality/                  ← Linting, formatting
│   ├── versioning/               ← Releases, changelog
│   ├── documentation/            ← Dev guides
│   └── tools/                    ← Build utilities
│
└── 🚢 DEPLOYMENT_MANAGEMENT/
    ├── docker/                   ← Docker configs
    ├── control-center/           ← Management UI
    ├── monitoring/               ← Health checks
    ├── scripts/                  ← Deploy scripts
    └── environments/             ← Dev/test/prod configs
```

---

## 📚 Additional Documentation

- [Reorganization Plan](REORGANIZATION_PLAN_3_DOMAINS.md) - How we got here
- [Organization Audit](ORGANIZATION_AUDIT_AND_IMPROVEMENTS.md) - Analysis
- [Original Structure](ORGANIZATION_COMPLETE.md) - Historical reference

---

## 🚀 Quick Start

### For Developers (CORE):
```bash
cd CORE/eScriptorium_UNIFIED
docker-compose up
```

### For Build Engineers (BUILD_MANAGEMENT):
```bash
cd BUILD_MANAGEMENT
./ci-cd/setup-github-actions.sh
./testing/run-all-tests.sh
```

### For DevOps (DEPLOYMENT_MANAGEMENT):
```powershell
cd DEPLOYMENT_MANAGEMENT
.\scripts\deploy\deploy-dev.ps1
```

---

**Version:** 2.0 (3-Domain Architecture)  
**Last Updated:** נובמבר 13, 2025  
**Status:** 🟢 Active Development
