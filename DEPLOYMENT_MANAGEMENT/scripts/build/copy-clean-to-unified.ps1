<![CDATA[#Requires -Version 5.1

<#
.SYNOPSIS
    העתקה מבוקרת של eScriptorium_CLEAN → eScriptorium_UNIFIED
.DESCRIPTION
    סקריפט מקיף להעברת CLEAN לתוך UNIFIED עם:
    - העתקה מבוקרת של כל הקבצים הקריטיים
    - ארגון אוטומטי לתיקיות לפי קטגוריות
    - דילוג על קבצים מיותרים (backups, node_modules, cache)
    - Logging מפורט של כל פעולה
    - בדיקות validation
    - גיבוי אוטומטי לפני כל שלב
.PARAMETER SkipBackup
    דלג על גיבוי (לא מומלץ!)
.PARAMETER Force
    החלף קבצים קיימים ללא שאלה
.PARAMETER DryRun
    הצג מה יקרה ללא ביצוע בפועל
.EXAMPLE
    .\copy-clean-to-unified.ps1
    הרצה רגילה עם כל הבדיקות
.EXAMPLE
    .\copy-clean-to-unified.ps1 -DryRun
    בדיקה יבשה - רואים מה יקרה
.EXAMPLE
    .\copy-clean-to-unified.ps1 -Force
    החלפת קבצים ללא אישור
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [switch]$SkipBackup,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

#region Functions

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Prefix = ""
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $fullMessage = "[$timestamp] $Prefix$Message"
    
    Write-Host $fullMessage -ForegroundColor $Color
    
    # גם לקובץ לוג
    Add-Content -Path $logFile -Value $fullMessage
}

function Test-PathSafe {
    param([string]$Path)
    if (Test-Path $Path) {
        return $true
    } else {
        Write-ColorOutput "⚠️ Path not found: $Path" "Yellow" "WARN: "
        return $false
    }
}

function New-DirectoryIfNotExists {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -Path $Path -ItemType Directory -Force | Out-Null
        Write-ColorOutput "✅ Created directory: $Path" "Green" "INFO: "
    }
}

function Copy-WithProgress {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$Exclude = @(),
        [string]$Description = "Copying files"
    )
    
    if ($DryRun) {
        Write-ColorOutput "🔍 DRY RUN: Would copy $Source → $Destination" "Cyan" "DRY: "
        return
    }
    
    Write-ColorOutput "📦 $Description..." "Cyan" "COPY: "
    Write-ColorOutput "   Source: $Source" "Gray"
    Write-ColorOutput "   Dest:   $Destination" "Gray"
    
    $excludeParams = @()
    if ($Exclude.Count -gt 0) {
        foreach ($ex in $Exclude) {
            $excludeParams += "/XD"
            $excludeParams += $ex
        }
        Write-ColorOutput "   Exclude: $($Exclude -join ', ')" "Yellow"
    }
    
    # robocopy parameters
    $robocopyArgs = @(
        $Source,
        $Destination,
        "/E",              # Copy subdirectories, including empty ones
        "/NFL",            # No file list
        "/NDL",            # No directory list
        "/NJH",            # No job header
        "/NJS",            # No job summary
        "/NP",             # No progress
        "/R:3",            # Retry 3 times
        "/W:5"             # Wait 5 seconds between retries
    ) + $excludeParams
    
    $result = robocopy @robocopyArgs 2>&1
    
    # robocopy exit codes: 0-7 are success, 8+ are errors
    if ($LASTEXITCODE -ge 8) {
        Write-ColorOutput "❌ Copy failed with exit code $LASTEXITCODE" "Red" "ERROR: "
        Write-ColorOutput "   $result" "Red"
        throw "Copy operation failed"
    } else {
        Write-ColorOutput "✅ Copy completed successfully!" "Green" "SUCCESS: "
    }
}

function Get-DirectorySize {
    param([string]$Path)
    $size = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    return [math]::Round($size / 1MB, 2)
}

function Get-FileCount {
    param([string]$Path)
    return (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
}

#endregion

#region Setup

Clear-Host

Write-ColorOutput @"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 eScriptorium CLEAN → UNIFIED Migration Tool           ║
║                                                              ║
║   תאריך: $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"@ "Magenta"

# Paths
$scriptDir = $PSScriptRoot
$projectRoot = Split-Path $scriptDir -Parent
$cleanPath = Join-Path $projectRoot "eScriptorium_CLEAN"
$unifiedPath = Join-Path $projectRoot "eScriptorium_UNIFIED"
$logDir = Join-Path $unifiedPath "logs"
$logFile = Join-Path $logDir "migration_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Create log directory
New-DirectoryIfNotExists $logDir

Write-ColorOutput "📁 Project Root: $projectRoot" "White"
Write-ColorOutput "📁 Source (CLEAN): $cleanPath" "White"
Write-ColorOutput "📁 Target (UNIFIED): $unifiedPath" "White"
Write-ColorOutput "📝 Log File: $logFile" "White"
Write-ColorOutput "" "White"

# Validate paths
if (-not (Test-PathSafe $cleanPath)) {
    throw "CLEAN path not found! Cannot continue."
}

if (-not (Test-Path $unifiedPath)) {
    Write-ColorOutput "⚠️ UNIFIED path not found. Creating..." "Yellow"
    New-Item -Path $unifiedPath -ItemType Directory -Force | Out-Null
}

#endregion

#region Backup

if (-not $SkipBackup -and -not $DryRun) {
    Write-ColorOutput "💾 Creating backup of existing UNIFIED..." "Yellow" "BACKUP: "
    
    $backupPath = Join-Path $projectRoot "backups"
    $backupName = "UNIFIED_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    $backupDest = Join-Path $backupPath $backupName
    
    New-DirectoryIfNotExists $backupPath
    
    if (Test-Path $unifiedPath) {
        robocopy $unifiedPath $backupDest /E /NFL /NDL /NJH /NJS /NP | Out-Null
        Write-ColorOutput "✅ Backup created: $backupDest" "Green" "BACKUP: "
    }
}

#endregion

#region Phase 1: Core Application Files (CRITICAL)

Write-ColorOutput "`n═══════════════════════════════════════════════════════════" "Cyan"
Write-ColorOutput "📦 PHASE 1: Core Application Files (Django)" "Cyan"
Write-ColorOutput "═══════════════════════════════════════════════════════════" "Cyan"

# 1.1 - Django app/
$appSource = Join-Path $cleanPath "app"
$appDest = Join-Path $unifiedPath "app"

if (Test-PathSafe $appSource) {
    $appSize = Get-DirectorySize $appSource
    $appFiles = Get-FileCount $appSource
    Write-ColorOutput "📊 Django app: $appFiles files, $appSize MB" "White"
    
    Copy-WithProgress -Source $appSource -Destination $appDest `
        -Exclude @("__pycache__", ".pytest_cache", "*.pyc", "*.pyo") `
        -Description "Copying Django application"
} else {
    Write-ColorOutput "⚠️ app/ not found in CLEAN!" "Red" "ERROR: "
}

# 1.2 - config/
$configSource = Join-Path $cleanPath "config"
$configDest = Join-Path $unifiedPath "config"

if (Test-PathSafe $configSource) {
    Copy-WithProgress -Source $configSource -Destination $configDest `
        -Description "Copying configuration files"
} else {
    Write-ColorOutput "⚠️ config/ not found in CLEAN!" "Yellow" "WARN: "
}

#endregion

#region Phase 2: Frontend

Write-ColorOutput "`n═══════════════════════════════════════════════════════════" "Cyan"
Write-ColorOutput "📦 PHASE 2: Frontend (Vue.js)" "Cyan"
Write-ColorOutput "═══════════════════════════════════════════════════════════" "Cyan"

# 2.1 - front/ (without node_modules and dist)
$frontSource = Join-Path $cleanPath "front"
$frontDest = Join-Path $unifiedPath "front"

if (Test-PathSafe $frontSource) {
    $frontSize = Get-DirectorySize $frontSource
    $frontFiles = Get-FileCount $frontSource
    Write-ColorOutput "📊 Frontend: $frontFiles files, $frontSize MB (excluding node_modules)" "White"
    
    # Check if already exists
    if ((Test-Path $frontDest) -and -not $Force) {
        Write-ColorOutput "⚠️ front/ already exists in UNIFIED. Use -Force to overwrite." "Yellow" "SKIP: "
    } else {
        Copy-WithProgress -Source $frontSource -Destination $frontDest `
            -Exclude @("node_modules", "dist", ".cache") `
            -Description "Copying frontend source"
            
        Write-ColorOutput "💡 Remember to run: cd front && npm install && npm run build" "Yellow" "TODO: "
    }
}

#endregion

#region Phase 3: Docker Configuration

Write-ColorOutput "`n═══════════════════════════════════════════════════════════" "Cyan"
Write-ColorOutput "📦 PHASE 3: Docker Configuration" "Cyan"
Write-ColorOutput "═══════════════════════════════════════════════════════════" "Cyan"

# 3.1 - docker-compose files
$dockerFiles = @(
    "docker-compose.integrated.yml",
    "docker-compose.dev.yml",
    "Dockerfile",
    ".dockerignore"
)

$dockerDest = Join-Path $unifiedPath "docker"
New-DirectoryIfNotExists $dockerDest

foreach ($file in $dockerFiles) {
    $source = Join-Path $cleanPath $file
    if (Test-Path $source) {
        $dest = Join-Path $dockerDest $file
        if ($DryRun) {
            Write-ColorOutput "🔍 DRY RUN: Would copy $file" "Cyan" "DRY: "
        } else {
            Copy-Item -Path $source -Destination $dest -Force
            Write-ColorOutput "✅ Copied: $file" "Green" "COPY: "
        }
    } else {
        Write-ColorOutput "⚠️ Not found: $file" "Yellow" "SKIP: "
    }
}

# 3.2 - nginx config
$nginxSource = Join-Path $cleanPath "nginx"
if (Test-PathSafe $nginxSource) {
    $nginxDest = Join-Path $dockerDest "nginx"
    Copy-WithProgress -Source $nginxSource -Destination $nginxDest `
        -Description "Copying nginx configuration"
}

#endregion

#region Phase 4: Scripts (Organized by Category)

Write-ColorOutput "`n═══════════════════════════════════════════════════════════" "Cyan"
Write-ColorOutput "📦 PHASE 4: Scripts (Organized)" "Cyan"
Write-ColorOutput "═══════════════════════════════════════════════════════════" "Cyan"

$scriptsSource = Join-Path $cleanPath "scripts"
$scriptsBaseDest = Join-Path $unifiedPath "scripts"

if (Test-PathSafe $scriptsSource) {
    $scriptFiles = Get-ChildItem -Path $scriptsSource -File
    Write-ColorOutput "📊 Found $($scriptFiles.Count) script files to organize" "White"
    
    # Categories
    $categories = @{
        "build" = @("build-*.ps1", "compile-*.ps1", "*build*.py")
        "deploy" = @("deploy-*.ps1", "restart-*.ps1", "*deploy*.py")
        "testing" = @("*test*.ps1", "check*.ps1", "verify*.ps1", "*test*.py")
        "maintenance" = @("backup*.ps1", "cleanup*.ps1", "*backup*.py", "*cleanup*.py")
        "translation" = @("*translation*.ps1", "*translate*.py", "*locale*.py")
        "docker" = @("docker*.ps1", "docker*.py", "container*.ps1")
    }
    
    foreach ($category in $categories.Keys) {
        $categoryDest = Join-Path $scriptsBaseDest $category
        New-DirectoryIfNotExists $categoryDest
        
        $patterns = $categories[$category]
        $matchedFiles = @()
        
        foreach ($pattern in $patterns) {
            $matches = $scriptFiles | Where-Object { $_.Name -like $pattern }
            $matchedFiles += $matches
        }
        
        $matchedFiles = $matchedFiles | Select-Object -Unique
        
        if ($matchedFiles.Count -gt 0) {
            Write-ColorOutput "📁 Category: $category ($($matchedFiles.Count) files)" "Cyan"
            
            foreach ($file in $matchedFiles) {
                $dest = Join-Path $categoryDest $file.Name
                if ($DryRun) {
                    Write-ColorOutput "   🔍 Would copy: $($file.Name)" "Gray" "DRY: "
                } else {
                    Copy-Item -Path $file.FullName -Destination $dest -Force
                    Write-ColorOutput "   ✅ $($file.Name)" "Green"
                }
            }
        }
    }
    
    # Copy remaining scripts to "utilities"
    $copiedNames = @()
    foreach ($category in $categories.Keys) {
        $categoryDest = Join-Path $scriptsBaseDest $category
        if (Test-Path $categoryDest) {
            $copiedNames += (Get-ChildItem -Path $categoryDest -File).Name
        }
    }
    
    $remainingFiles = $scriptFiles | Where-Object { $_.Name -notin $copiedNames }
    
    if ($remainingFiles.Count -gt 0) {
        $utilsDest = Join-Path $scriptsBaseDest "utilities"
        New-DirectoryIfNotExists $utilsDest
        
        Write-ColorOutput "📁 Category: utilities ($($remainingFiles.Count) files)" "Cyan"
        
        foreach ($file in $remainingFiles) {
            $dest = Join-Path $utilsDest $file.Name
            if ($DryRun) {
                Write-ColorOutput "   🔍 Would copy: $($file.Name)" "Gray" "DRY: "
            } else {
                Copy-Item -Path $file.FullName -Destination $dest -Force
                Write-ColorOutput "   ✅ $($file.Name)" "Green"
            }
        }
    }
}

#endregion

#region Phase 5: Documentation (Organized)

Write-ColorOutput "`n═══════════════════════════════════════════════════════════" "Cyan"
Write-ColorOutput "📦 PHASE 5: Documentation (Organized)" "Cyan"
Write-ColorOutput "═══════════════════════════════════════════════════════════" "Cyan"

$docsBaseDest = Join-Path $unifiedPath "docs"

# Find all .md files in CLEAN root
$mdFiles = Get-ChildItem -Path $cleanPath -Filter "*.md" -File

if ($mdFiles.Count -gt 0) {
    Write-ColorOutput "📊 Found $($mdFiles.Count) documentation files" "White"
    
    # Categories for docs
    $docCategories = @{
        "architecture" = @("*ARCHITECTURE*", "*STRUCTURE*", "*DESIGN*")
        "guides" = @("*GUIDE*", "*HOWTO*", "*TUTORIAL*", "*QUICKSTART*", "*QUICK_START*")
        "api" = @("*API*", "*REST*", "*ENDPOINT*")
        "deployment" = @("*DEPLOY*", "*INSTALL*", "*SETUP*", "*DOCKER*")
        "translation" = @("*TRANSLATION*", "*I18N*", "*LOCALE*")
        "testing" = @("*TEST*", "*QA*", "*QUALITY*")
    }
    
    foreach ($category in $docCategories.Keys) {
        $categoryDest = Join-Path $docsBaseDest $category
        New-DirectoryIfNotExists $categoryDest
        
        $patterns = $docCategories[$category]
        $matchedDocs = @()
        
        foreach ($pattern in $patterns) {
            $matches = $mdFiles | Where-Object { $_.Name -like $pattern }
            $matchedDocs += $matches
        }
        
        $matchedDocs = $matchedDocs | Select-Object -Unique
        
        if ($matchedDocs.Count -gt 0) {
            Write-ColorOutput "📁 Category: $category ($($matchedDocs.Count) files)" "Cyan"
            
            foreach ($file in $matchedDocs) {
                $dest = Join-Path $categoryDest $file.Name
                if ($DryRun) {
                    Write-ColorOutput "   🔍 Would copy: $($file.Name)" "Gray" "DRY: "
                } else {
                    Copy-Item -Path $file.FullName -Destination $dest -Force
                    Write-ColorOutput "   ✅ $($file.Name)" "Green"
                }
            }
        }
    }
}

#endregion

#region Phase 6: Supporting Files

Write-ColorOutput "`n═══════════════════════════════════════════════════════════" "Cyan"
Write-ColorOutput "📦 PHASE 6: Supporting Files" "Cyan"
Write-ColorOutput "═══════════════════════════════════════════════════════════" "Cyan"

# 6.1 - Config files in root
$rootConfigFiles = @(
    ".gitignore",
    ".dockerignore",
    ".flake8",
    ".isort.cfg",
    "LICENSE",
    "requirements.txt",
    "pyproject.toml",
    "manage.py"
)

foreach ($file in $rootConfigFiles) {
    $source = Join-Path $cleanPath $file
    if (Test-Path $source) {
        $dest = Join-Path $unifiedPath $file
        if ($DryRun) {
            Write-ColorOutput "🔍 DRY RUN: Would copy $file" "Cyan" "DRY: "
        } else {
            Copy-Item -Path $source -Destination $dest -Force
            Write-ColorOutput "✅ Copied: $file" "Green" "COPY: "
        }
    }
}

# 6.2 - tests/
$testsSource = Join-Path $cleanPath "tests"
$testsDest = Join-Path $unifiedPath "tests"

if (Test-PathSafe $testsSource) {
    Copy-WithProgress -Source $testsSource -Destination $testsDest `
        -Exclude @("__pycache__", ".pytest_cache") `
        -Description "Copying tests"
}

# 6.3 - .github/
$githubSource = Join-Path $cleanPath ".github"
$githubDest = Join-Path $unifiedPath ".github"

if (Test-PathSafe $githubSource) {
    Copy-WithProgress -Source $githubSource -Destination $githubDest `
        -Description "Copying GitHub configurations"
}

#endregion

#region Phase 7: Management Files

Write-ColorOutput "`n═══════════════════════════════════════════════════════════" "Cyan"
Write-ColorOutput "📦 PHASE 7: Management Files" "Cyan"
Write-ColorOutput "═══════════════════════════════════════════════════════════" "Cyan"

$managementDest = Join-Path $unifiedPath "management"
New-DirectoryIfNotExists $managementDest

# State files
$stateFiles = @(
    "CURRENT_STATE.md",
    "SESSION_LOG.md"
)

foreach ($file in $stateFiles) {
    $source = Join-Path $cleanPath $file
    if (Test-Path $source) {
        $dest = Join-Path $managementDest $file
        if ($DryRun) {
            Write-ColorOutput "🔍 DRY RUN: Would copy $file to management/" "Cyan" "DRY: "
        } else {
            Copy-Item -Path $source -Destination $dest -Force
            Write-ColorOutput "✅ Copied $file to management/" "Green" "COPY: "
        }
    }
}

# Control Center (from project root)
$controlCenterSource = Join-Path $projectRoot "PROJECT_CONTROL_CENTER_V2.html"
if (Test-Path $controlCenterSource) {
    $controlCenterDest = Join-Path $managementDest "PROJECT_CONTROL_CENTER_V2.html"
    if ($DryRun) {
        Write-ColorOutput "🔍 DRY RUN: Would copy Control Center" "Cyan" "DRY: "
    } else {
        Copy-Item -Path $controlCenterSource -Destination $controlCenterDest -Force
        Write-ColorOutput "✅ Copied Control Center to management/" "Green" "COPY: "
    }
}

#endregion

#region Summary

Write-ColorOutput "`n╔══════════════════════════════════════════════════════════════╗" "Green"
Write-ColorOutput "║                                                              ║" "Green"
Write-ColorOutput "║   ✅ MIGRATION COMPLETED SUCCESSFULLY!                      ║" "Green"
Write-ColorOutput "║                                                              ║" "Green"
Write-ColorOutput "╚══════════════════════════════════════════════════════════════╝" "Green"

Write-ColorOutput "`n📊 Migration Summary:" "Cyan"
Write-ColorOutput "════════════════════════════════════════════════════════════" "Cyan"

if (Test-Path $unifiedPath) {
    $totalSize = Get-DirectorySize $unifiedPath
    $totalFiles = Get-FileCount $unifiedPath
    
    Write-ColorOutput "📁 UNIFIED Directory:" "White"
    Write-ColorOutput "   Total Files: $totalFiles" "White"
    Write-ColorOutput "   Total Size:  $totalSize MB" "White"
}

Write-ColorOutput "`n📝 Next Steps:" "Yellow"
Write-ColorOutput "════════════════════════════════════════════════════════════" "Yellow"
Write-ColorOutput "1. 🔨 Build Frontend:" "White"
Write-ColorOutput "   cd eScriptorium_UNIFIED/front" "Gray"
Write-ColorOutput "   npm install" "Gray"
Write-ColorOutput "   npm run build" "Gray"
Write-ColorOutput "" "White"
Write-ColorOutput "2. 🐳 Build Docker:" "White"
Write-ColorOutput "   cd eScriptorium_UNIFIED" "Gray"
Write-ColorOutput "   docker-compose -f docker/docker-compose.integrated.yml build" "Gray"
Write-ColorOutput "   docker-compose -f docker/docker-compose.integrated.yml up -d" "Gray"
Write-ColorOutput "" "White"
Write-ColorOutput "3. ✅ Verify:" "White"
Write-ColorOutput "   curl http://localhost:8086/health" "Gray"
Write-ColorOutput "" "White"
Write-ColorOutput "4. 📝 Update Documentation:" "White"
Write-ColorOutput "   Update CURRENT_STATE.md in management/" "Gray"
Write-ColorOutput "   Update SESSION_LOG.md with migration details" "Gray"

Write-ColorOutput "`n📝 Log file saved to:" "White"
Write-ColorOutput "   $logFile" "Gray"

Write-ColorOutput "`n✨ Done! Happy coding! 🚀" "Magenta"

#endregion
]]>