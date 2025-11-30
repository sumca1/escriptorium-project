# 🔄 Reorganize to 3 Domains - Automatic Reorganization Script
# Purpose: Reorganize escriptorium project into 3 separate domains
# Version: 1.0
# Date: November 13, 2025

<#
.SYNOPSIS
    Reorganizes escriptorium into 3 independent domains: CORE, BUILD_MANAGEMENT, DEPLOYMENT_MANAGEMENT

.DESCRIPTION
    This script implements the 3-domain architecture:
    1. CORE/ - eScriptorium application code
    2. BUILD_MANAGEMENT/ - Build, CI/CD, testing
    3. DEPLOYMENT_MANAGEMENT/ - Docker, deployment, monitoring

.PARAMETER DryRun
    Shows what would be done without making changes

.PARAMETER StepByStep
    Asks for confirmation before each major step

.PARAMETER Backup
    Creates backup before changes (default: true)

.EXAMPLE
    .\reorganize-to-3-domains.ps1
    Full automatic reorganization with backup

.EXAMPLE
    .\reorganize-to-3-domains.ps1 -DryRun
    See what would happen without changes

.EXAMPLE
    .\reorganize-to-3-domains.ps1 -StepByStep
    Manual confirmation for each step
#>

param(
    [switch]$DryRun,
    [switch]$StepByStep,
    [bool]$Backup = $true
)

# Colors
$colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Header = "Magenta"
    Question = "Yellow"
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $colors[$Color]
}

function Write-Header {
    param([string]$Text)
    Write-Host "`n" -NoNewline
    Write-ColorOutput "="*80 -Color "Header"
    Write-ColorOutput "  $Text" -Color "Header"
    Write-ColorOutput "="*80 -Color "Header"
}

function Request-Confirmation {
    param([string]$Question)
    if (-not $StepByStep) { return $true }
    
    Write-ColorOutput "`n$Question (Y/N): " -Color "Question"
    $response = Read-Host
    return $response -eq "Y" -or $response -eq "y"
}

# Configuration
$rootPath = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium"
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
$backupPath = Join-Path $rootPath "backups\reorganization-backup-$timestamp"

Write-Header "🔄 3-Domain Reorganization Tool"
Write-ColorOutput "Root: $rootPath" -Color "Info"
Write-ColorOutput "Mode: $(if($DryRun){'DRY RUN'}elseif($StepByStep){'STEP-BY-STEP'}else{'AUTOMATIC'})" -Color $(if($DryRun){'Warning'}else{'Success'})

# Check if directory exists
if (-not (Test-Path $rootPath)) {
    Write-ColorOutput "❌ Error: Root directory not found!" -Color "Error"
    exit 1
}

# Create backup
if ($Backup -and -not $DryRun) {
    Write-Header "📦 Creating Backup"
    if (Request-Confirmation "Create full backup before reorganization?") {
        try {
            New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
            
            # Backup only key directories (not the huge UNIFIED)
            $backupItems = @(
                "ui", "scripts", "management", "docs", 
                "README.md", "ORGANIZATION_COMPLETE.md", "*.ps1"
            )
            
            foreach ($item in $backupItems) {
                $sourcePath = Join-Path $rootPath $item
                if (Test-Path $sourcePath) {
                    Copy-Item -Path $sourcePath -Destination $backupPath -Recurse -Force
                    Write-ColorOutput "  ✅ Backed up: $item" -Color "Success"
                }
            }
            
            Write-ColorOutput "✅ Backup created: $backupPath" -Color "Success"
        }
        catch {
            Write-ColorOutput "⚠️ Warning: Backup failed: $_" -Color "Warning"
            if (-not (Request-Confirmation "Continue without backup?")) {
                exit 1
            }
        }
    }
}

# Define new structure
$newStructure = @{
    "CORE" = @{
        Description = "Application source code"
        Items = @("eScriptorium_UNIFIED", "eScriptorium_CLEAN")
        Readme = @"
# 📦 eScriptorium Core Application

## What's Here?
The main eScriptorium application code - Django backend, Vue.js frontend, 
and BiblIA language extensions.

## Quick Start:
``````bash
cd eScriptorium_UNIFIED
docker-compose up
``````

## Structure:
- **eScriptorium_UNIFIED/** - Main application (active development)
- **eScriptorium_CLEAN/** - Clean reference copy (16 containers working)

## This Directory Contains ONLY:
✅ Application source code
✅ Django backend (app/)
✅ Vue.js frontend (front/)
✅ BiblIA extensions (language_support/)
✅ Docker configuration for running the app

## NOT Here (see other domains):
❌ Build scripts → See BUILD_MANAGEMENT/
❌ Deployment tools → See DEPLOYMENT_MANAGEMENT/

---

**For ChatBots:** When in this domain, focus ONLY on application code, 
features, bug fixes, and functionality. Do not suggest build or deployment changes.
"@
    }
    
    "BUILD_MANAGEMENT" = @{
        Description = "Build, CI/CD, testing, quality management"
        Items = @()  # Will be populated from escriptorium_V2
        Readme = @"
# 🏗️ Build Management

## What's Here?
Everything related to building, testing, and quality assurance of 
the eScriptorium project.

## Quick Start:
``````bash
# Setup CI/CD
./ci-cd/setup-github-actions.sh

# Run tests
./testing/run-all-tests.sh

# Check quality
./quality/run-linters.sh
``````

## Domains:
- **ci-cd/** - GitHub Actions, automated pipelines
- **testing/** - Unit, integration, E2E tests
- **quality/** - Linting, formatting, coverage
- **versioning/** - Releases, changelogs, git workflows
- **documentation/** - Dev guides, API docs, ADRs
- **tools/** - Build utilities and helpers

## For ChatBots:
When working in this domain, focus ONLY on:
✅ Build processes and automation
✅ Testing frameworks and test cases
✅ Code quality tools and standards
✅ CI/CD pipeline configuration
✅ Version management and releases

Do NOT touch:
❌ Core application code → See CORE/
❌ Docker/deployment → See DEPLOYMENT_MANAGEMENT/

---

**Note:** This domain is extracted from best practices in escriptorium_V2/
"@
    }
    
    "DEPLOYMENT_MANAGEMENT" = @{
        Description = "Docker, deployment, monitoring, operations"
        Items = @("ui", "scripts", "management", "logs", "backups", "data")
        Readme = @"
# 🚢 Deployment Management

## What's Here?
Everything related to Docker, container orchestration, deployment, 
monitoring, and production operations.

## Quick Start:
``````powershell
# Deploy to development
.\scripts\deploy\deploy-dev.ps1

# Open Control Center
Start-Process "http://localhost:3002"

# Check system health
.\monitoring\health-checks\check-all-services.sh
``````

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
- Control Center accessible at http://localhost:3002
- All services monitored and logged
"@
    }
}

# Phase 1: Create new directories
Write-Header "📁 Phase 1: Creating New Directory Structure"

if (Request-Confirmation "Create 3 main domain directories?") {
    foreach ($domain in $newStructure.Keys) {
        $domainPath = Join-Path $rootPath $domain
        
        if (-not $DryRun) {
            if (-not (Test-Path $domainPath)) {
                New-Item -ItemType Directory -Path $domainPath -Force | Out-Null
                Write-ColorOutput "  ✅ Created: $domain/" -Color "Success"
            } else {
                Write-ColorOutput "  ℹ️ Exists: $domain/" -Color "Info"
            }
        } else {
            Write-ColorOutput "  [DRY RUN] Would create: $domain/" -Color "Info"
        }
    }
}

# Phase 2: Move CORE items
Write-Header "📦 Phase 2: Moving CORE Items"

if (Request-Confirmation "Move eScriptorium code to CORE/?") {
    $coreItems = $newStructure["CORE"].Items
    foreach ($item in $coreItems) {
        $sourcePath = Join-Path $rootPath $item
        $targetPath = Join-Path $rootPath "CORE\$item"
        
        if (Test-Path $sourcePath) {
            if (-not $DryRun) {
                try {
                    if (-not (Test-Path $targetPath)) {
                        Move-Item -Path $sourcePath -Destination $targetPath -Force
                        Write-ColorOutput "  ✅ Moved: $item → CORE/" -Color "Success"
                    } else {
                        Write-ColorOutput "  ℹ️ Already exists: CORE/$item" -Color "Info"
                    }
                }
                catch {
                    Write-ColorOutput "  ❌ Failed to move $item`: $($_.Exception.Message)" -Color "Error"
                }
            } else {
                Write-ColorOutput "  [DRY RUN] Would move: $item → CORE/" -Color "Info"
            }
        }
    }
}

# Phase 3: Setup BUILD_MANAGEMENT from escriptorium_V2
Write-Header "🏗️ Phase 3: Setting Up BUILD_MANAGEMENT"

if (Request-Confirmation "Setup BUILD_MANAGEMENT structure?") {
    $buildPath = Join-Path $rootPath "BUILD_MANAGEMENT"
    $v2Path = Join-Path (Split-Path $rootPath -Parent) "escriptorium_V2"
    
    # Create subdirectories
    $buildDirs = @("ci-cd", "testing", "quality", "versioning", "documentation", "tools")
    
    foreach ($dir in $buildDirs) {
        $dirPath = Join-Path $buildPath $dir
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
            Write-ColorOutput "  ✅ Created: BUILD_MANAGEMENT/$dir/" -Color "Success"
        } else {
            Write-ColorOutput "  [DRY RUN] Would create: BUILD_MANAGEMENT/$dir/" -Color "Info"
        }
    }
    
    # Copy relevant files from V2 if exists
    if (Test-Path $v2Path) {
        Write-ColorOutput "`n  📋 Analyzing escriptorium_V2 for build artifacts..." -Color "Info"
        
        # Look for CI/CD files
        $ciFiles = Get-ChildItem -Path $v2Path -Filter "*.yml" -Recurse | Where-Object { $_.Name -like "*build*" -or $_.Name -like "*test*" -or $_.Name -like "*ci*" }
        foreach ($file in $ciFiles) {
            Write-ColorOutput "  ℹ️ Found CI file: $($file.Name)" -Color "Info"
        }
        
        # Look for test files
        $testFiles = Get-ChildItem -Path $v2Path -Filter "*test*" -Recurse -Directory
        foreach ($dir in $testFiles) {
            Write-ColorOutput "  ℹ️ Found test dir: $($dir.Name)" -Color "Info"
        }
    }
}

# Phase 4: Move DEPLOYMENT_MANAGEMENT items
Write-Header "🚢 Phase 4: Moving DEPLOYMENT_MANAGEMENT Items"

if (Request-Confirmation "Move deployment-related items to DEPLOYMENT_MANAGEMENT/?") {
    $deployPath = Join-Path $rootPath "DEPLOYMENT_MANAGEMENT"
    $deployItems = $newStructure["DEPLOYMENT_MANAGEMENT"].Items
    
    foreach ($item in $deployItems) {
        $sourcePath = Join-Path $rootPath $item
        $targetPath = Join-Path $deployPath $item
        
        if (Test-Path $sourcePath) {
            if (-not $DryRun) {
                try {
                    if (-not (Test-Path $targetPath)) {
                        Move-Item -Path $sourcePath -Destination $targetPath -Force
                        Write-ColorOutput "  ✅ Moved: $item → DEPLOYMENT_MANAGEMENT/" -Color "Success"
                    } else {
                        Write-ColorOutput "  ℹ️ Already exists: DEPLOYMENT_MANAGEMENT/$item" -Color "Info"
                    }
                }
                catch {
                    Write-ColorOutput "  ❌ Failed to move $item`: $($_.Exception.Message)" -Color "Error"
                }
            } else {
                Write-ColorOutput "  [DRY RUN] Would move: $item → DEPLOYMENT_MANAGEMENT/" -Color "Info"
            }
        }
    }
    
    # Create additional deployment subdirectories
    $deployDirs = @("docker", "orchestration", "monitoring\health-checks", "monitoring\metrics", "monitoring\logs", "environments\dev", "environments\test", "environments\prod")
    
    foreach ($dir in $deployDirs) {
        $dirPath = Join-Path $deployPath $dir
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
            Write-ColorOutput "  ✅ Created: DEPLOYMENT_MANAGEMENT/$dir/" -Color "Success"
        } else {
            Write-ColorOutput "  [DRY RUN] Would create: DEPLOYMENT_MANAGEMENT/$dir/" -Color "Info"
        }
    }
    
    # Rename ui/control-center to just control-center
    $controlCenterOld = Join-Path $deployPath "ui\control-center"
    $controlCenterNew = Join-Path $deployPath "control-center"
    
    if ((Test-Path $controlCenterOld) -and -not $DryRun) {
        Move-Item -Path $controlCenterOld -Destination $controlCenterNew -Force
        Remove-Item -Path (Join-Path $deployPath "ui") -Force -ErrorAction SilentlyContinue
        Write-ColorOutput "  ✅ Reorganized: control-center" -Color "Success"
    }
}

# Phase 5: Create README files
Write-Header "📝 Phase 5: Creating README Files"

if (Request-Confirmation "Create README.md files for each domain?") {
    foreach ($domain in $newStructure.Keys) {
        $readmePath = Join-Path $rootPath "$domain\README.md"
        $readmeContent = $newStructure[$domain].Readme
        
        if (-not $DryRun) {
            $readmeContent | Out-File -FilePath $readmePath -Encoding UTF8
            Write-ColorOutput "  ✅ Created: $domain/README.md" -Color "Success"
        } else {
            Write-ColorOutput "  [DRY RUN] Would create: $domain/README.md" -Color "Info"
        }
    }
}

# Phase 6: Create main README with navigation
Write-Header "📄 Phase 6: Creating Main README"

if (Request-Confirmation "Create main README.md with navigation?") {
    $mainReadme = @"
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
``````
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
``````

### Context Loading:
- **If user chooses CORE:** Load `CORE/README.md` + `CORE/ARCHITECTURE.md`
- **If user chooses BUILD:** Load `BUILD_MANAGEMENT/README.md` + CI/CD docs
- **If user chooses DEPLOY:** Load `DEPLOYMENT_MANAGEMENT/README.md` + docker configs

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

``````
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
``````

---

## 📚 Additional Documentation

- [Reorganization Plan](REORGANIZATION_PLAN_3_DOMAINS.md) - How we got here
- [Organization Audit](ORGANIZATION_AUDIT_AND_IMPROVEMENTS.md) - Analysis
- [Original Structure](ORGANIZATION_COMPLETE.md) - Historical reference

---

## 🚀 Quick Start

### For Developers (CORE):
``````bash
cd CORE/eScriptorium_UNIFIED
docker-compose up
``````

### For Build Engineers (BUILD_MANAGEMENT):
``````bash
cd BUILD_MANAGEMENT
./ci-cd/setup-github-actions.sh
./testing/run-all-tests.sh
``````

### For DevOps (DEPLOYMENT_MANAGEMENT):
``````powershell
cd DEPLOYMENT_MANAGEMENT
.\scripts\deploy\deploy-dev.ps1
``````

---

**Version:** 2.0 (3-Domain Architecture)  
**Last Updated:** $(Get-Date -Format "MMMM dd, yyyy")  
**Status:** 🟢 Active Development
"@
    
    $mainReadmePath = Join-Path $rootPath "README.md"
    if (-not $DryRun) {
        # Backup old README
        if (Test-Path $mainReadmePath) {
            Copy-Item $mainReadmePath "$mainReadmePath.backup-$timestamp"
        }
        $mainReadme | Out-File -FilePath $mainReadmePath -Encoding UTF8
        Write-ColorOutput "  ✅ Created: README.md (old backed up)" -Color "Success"
    } else {
        Write-ColorOutput "  [DRY RUN] Would create main README.md" -Color "Info"
    }
}

# Phase 7: Create .gitignore for each domain
Write-Header "🔒 Phase 7: Creating .gitignore Files"

if (Request-Confirmation "Create .gitignore files?") {
    $gitignores = @{
        "CORE" = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/

# Node
node_modules/
npm-debug.log*

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
"@
        "BUILD_MANAGEMENT" = @"
# Test results
*.xml
*.log
coverage/
.coverage
htmlcov/

# Build artifacts
dist/
build/
*.egg-info/

# CI/CD
.github-workflow-runs/
"@
        "DEPLOYMENT_MANAGEMENT" = @"
# Runtime
*.pid
*.log
logs/

# Environment files
.env
.env.local
*.env.dev
*.env.prod

# Data
data/*.json
backups/

# Control Center
control-center/runtime/
control-center/node_modules/
"@
    }
    
    foreach ($domain in $gitignores.Keys) {
        $gitignorePath = Join-Path $rootPath "$domain\.gitignore"
        if (-not $DryRun) {
            $gitignores[$domain] | Out-File -FilePath $gitignorePath -Encoding UTF8
            Write-ColorOutput "  ✅ Created: $domain/.gitignore" -Color "Success"
        } else {
            Write-ColorOutput "  [DRY RUN] Would create: $domain/.gitignore" -Color "Info"
        }
    }
}

# Summary Report
Write-Header "📊 Summary Report"

$report = @"

✅ 3-Domain Reorganization Complete!

📂 New Structure Created:

   📦 CORE/
      └── Application source code
      
   🏗️ BUILD_MANAGEMENT/
      └── Build, CI/CD, testing, quality
      
   🚢 DEPLOYMENT_MANAGEMENT/
      └── Docker, deployment, monitoring

📝 Files Created:
   - 3 domain README.md files
   - 1 main README.md with navigation
   - 3 .gitignore files

$(if ($Backup -and -not $DryRun) {
"💾 Backup Location:
   $backupPath"
})

🎯 What's Next:

   1. Review each domain's README.md
   2. Test that all paths work correctly
   3. Update any absolute paths in code/configs
   4. Train ChatBots with new structure
   5. Update documentation links

⏱️ Reorganization completed in: $(((Get-Date) - $startTime).TotalSeconds) seconds

🤖 ChatBot Integration Ready!
   - User says "בוקר טוב"
   - Bot asks which domain (core/build/deploy)
   - Bot loads appropriate context
   - Work stays isolated per domain

"@

$startTime = Get-Date
Write-ColorOutput $report -Color "Success"

# Save report
if (-not $DryRun) {
    $reportPath = Join-Path $rootPath "DEPLOYMENT_MANAGEMENT\logs\reorganization-3domains-$timestamp.log"
    New-Item -ItemType Directory -Path (Split-Path $reportPath) -Force | Out-Null
    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-ColorOutput "`n📄 Report saved: $reportPath" -Color "Info"
}

Write-Header "🎉 Done!"
Write-ColorOutput "3-Domain architecture is ready! Check README.md for navigation." -Color "Success"

if ($DryRun) {
    Write-ColorOutput "`n⚠️ This was a DRY RUN - no changes were made." -Color "Warning"
    Write-ColorOutput "Run without -DryRun to apply changes." -Color "Info"
}
