# 🚢 Deployment Management

## What's Here?
Everything related to Docker, container orchestration, deployment, 
monitoring, and production operations.

## Quick Start:
```powershell
# Deploy to development
.\scripts\deploy\deploy-dev.ps1

# Open Control Center
Start-Process "http://localhost:8080"

# Check system health
.\monitoring\health-checks\check-all-services.sh
```

## Domains:
- **docker/** - Container configs, compose files
- **control-center/** - Visual dashboard for management
- **monitoring/** - Health checks, metrics, logs
- **scripts/** - Deployment automation scripts
- **environments/** - Dev, test, prod configurations

## For ChatBots:
When working in this domain, focus ONLY on:
✅ Docker containers and orchestration
✅ Deployment strategies and automation
✅ Environment configurations
✅ Monitoring, logging, and metrics
✅ Production operations and maintenance

Do NOT touch:
❌ Application code → See CORE/
❌ Build pipelines → See BUILD_MANAGEMENT/

---

**Current Status:**
- 16 Docker containers running
- Control Center accessible at http://localhost:8080
- All services monitored and logged
