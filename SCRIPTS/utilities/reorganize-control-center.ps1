# 🔧 Reorganize Control Center - Automatic Organization Script
# Purpose: Clean up and organize the control-center directory structure
# Version: 1.0
# Date: November 13, 2025

<#
.SYNOPSIS
    Reorganizes the control-center directory into a cleaner structure

.DESCRIPTION
    This script:
    1. Creates organized subdirectories (app/, servers/, docs/, scripts/, runtime/, backups/)
    2. Moves files to appropriate locations
    3. Updates references in HTML/JS files
    4. Creates .gitignore for runtime files
    5. Generates a summary report

.PARAMETER DryRun
    If specified, shows what would be done without making changes

.PARAMETER Backup
    Creates a backup before making changes (default: true)

.EXAMPLE
    .\reorganize-control-center.ps1
    Reorganizes with backup

.EXAMPLE
    .\reorganize-control-center.ps1 -DryRun
    Shows what would be changed without doing it
#>

param(
    [switch]$DryRun,
    [bool]$Backup = $true
)

# Colors for output
$colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Header = "Magenta"
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

# Configuration
$controlCenterPath = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center"
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
$backupPath = Join-Path $controlCenterPath "backups\backup-$timestamp"

Write-Header "🔧 Control Center Reorganization Tool"
Write-ColorOutput "Directory: $controlCenterPath" -Color "Info"
Write-ColorOutput "Mode: $(if($DryRun){'DRY RUN - No changes will be made'}else{'LIVE - Files will be moved'})" -Color $(if($DryRun){'Warning'}else{'Success'})

# Check if directory exists
if (-not (Test-Path $controlCenterPath)) {
    Write-ColorOutput "❌ Error: Control Center directory not found!" -Color "Error"
    exit 1
}

# Create backup if requested
if ($Backup -and -not $DryRun) {
    Write-Header "📦 Creating Backup"
    try {
        New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
        Copy-Item -Path "$controlCenterPath\*" -Destination $backupPath -Recurse -Force
        Write-ColorOutput "✅ Backup created: $backupPath" -Color "Success"
    }
    catch {
        Write-ColorOutput "⚠️ Warning: Could not create backup: $_" -Color "Warning"
    }
}

# Define new structure
$newStructure = @{
    "app" = @{
        Description = "HTML, CSS, and frontend JavaScript files"
        Files = @("index.html", "index-v1.html", "dashboard.html", "dashboard-simple.html", 
                  "service-worker.js", "test-button-debug.html")
    }
    "servers" = @{
        Description = "Node.js server files"
        Files = @("terminal-server.js", "dashboard-server.js", "package.json", "package-lock.json")
    }
    "docs" = @{
        Description = "Documentation files"
        Files = @("*.md") # All markdown files
    }
    "scripts" = @{
        Description = "Startup and utility scripts"
        Files = @("*.ps1", "*.bat", "*.vbs", "*.sh")
    }
    "runtime" = @{
        Description = "Runtime files (gitignored)"
        Files = @(".terminal-server.pid", ".terminal-server-job.txt")
    }
    "backups" = @{
        Description = "Backup files"
        Files = @("dashboard-BACKUP-*.html", "*-backup-*", "*-BACKUP-*")
    }
}

# Directories that should remain at root level
$keepAtRoot = @("data", "logs", "modules")

Write-Header "📊 Analysis Phase"

# Scan current files
$currentFiles = Get-ChildItem -Path $controlCenterPath -File
Write-ColorOutput "Found $($currentFiles.Count) files in control-center" -Color "Info"

# Categorize files
$moveActions = @()
foreach ($file in $currentFiles) {
    $fileName = $file.Name
    $targetDir = $null
    
    # Check each category
    foreach ($category in $newStructure.Keys) {
        foreach ($pattern in $newStructure[$category].Files) {
            if ($fileName -like $pattern) {
                $targetDir = $category
                break
            }
        }
        if ($targetDir) { break }
    }
    
    if ($targetDir) {
        $moveActions += [PSCustomObject]@{
            File = $fileName
            From = $controlCenterPath
            To = Join-Path $controlCenterPath $targetDir
            Category = $targetDir
        }
    }
    else {
        Write-ColorOutput "  ⚠️ No category for: $fileName (will stay at root)" -Color "Warning"
    }
}

Write-ColorOutput "`n📋 Files to be moved: $($moveActions.Count)" -Color "Info"

# Group by category
$groupedActions = $moveActions | Group-Object -Property Category
foreach ($group in $groupedActions) {
    Write-ColorOutput "  $($group.Name): $($group.Count) files" -Color "Cyan"
}

# Execution Phase
if (-not $DryRun) {
    Write-Header "🚀 Execution Phase"
    
    # Create new directories
    foreach ($dir in $newStructure.Keys) {
        $dirPath = Join-Path $controlCenterPath $dir
        if (-not (Test-Path $dirPath)) {
            Write-ColorOutput "  📁 Creating: $dir/" -Color "Info"
            New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        }
    }
    
    # Move files
    $movedCount = 0
    $failedCount = 0
    
    foreach ($action in $moveActions) {
        try {
            $sourcePath = Join-Path $action.From $action.File
            $targetPath = Join-Path $action.To $action.File
            
            if (Test-Path $sourcePath) {
                Move-Item -Path $sourcePath -Destination $targetPath -Force
                Write-ColorOutput "  ✅ Moved: $($action.File) → $($action.Category)/" -Color "Success"
                $movedCount++
            }
            else {
                Write-ColorOutput "  ⚠️ Not found: $($action.File)" -Color "Warning"
            }
        }
        catch {
            Write-ColorOutput "  ❌ Failed: $($action.File) - $_" -Color "Error"
            $failedCount++
        }
    }
    
    Write-ColorOutput "`n📊 Results: $movedCount moved, $failedCount failed" -Color $(if($failedCount -eq 0){'Success'}else{'Warning'})
    
    # Create README files in each subdirectory
    Write-Header "📝 Creating README Files"
    
    foreach ($dir in $newStructure.Keys) {
        $dirPath = Join-Path $controlCenterPath $dir
        $readmePath = Join-Path $dirPath "README.md"
        
        $readmeContent = @"
# 📁 $dir/

**Purpose:** $($newStructure[$dir].Description)

## Contents

$(if ($dir -eq "app") {
"- `index.html` - Control Center V2 (main interface)
- `index-v1.html` - Control Center V1 (legacy)
- `dashboard.html` - Dashboard view
- `dashboard-simple.html` - Simplified dashboard
- `service-worker.js` - Service worker for PWA features
- `test-button-debug.html` - Debug utilities"
} elseif ($dir -eq "servers") {
"- `terminal-server.js` - Terminal server backend
- `dashboard-server.js` - Dashboard data server
- `package.json` - Node.js dependencies
- `package-lock.json` - Dependency lock file"
} elseif ($dir -eq "docs") {
"All documentation markdown files are stored here.

See [../INDEX.md](../INDEX.md) for a complete list."
} elseif ($dir -eq "scripts") {
"Startup and utility scripts for Control Center.

- `.ps1` files - PowerShell scripts
- `.bat` files - Windows batch files  
- `.vbs` files - VBScript files"
} elseif ($dir -eq "runtime") {
"**⚠️ This directory is gitignored**

Runtime files that are created during execution:
- `.terminal-server.pid` - Process ID file
- `.terminal-server-job.txt` - Job tracking file

These files should not be committed to version control."
} elseif ($dir -eq "backups") {
"**⚠️ This directory is gitignored**

Backup files are stored here automatically.

Format: `dashboard-BACKUP-YYYY-MM-DD-HHMM.html`"
})

---

**Created:** $(Get-Date -Format "yyyy-MM-dd HH:mm")  
**Part of:** Control Center Reorganization v1.0
"@
        
        if (-not $DryRun) {
            $readmeContent | Out-File -FilePath $readmePath -Encoding UTF8
            Write-ColorOutput "  ✅ Created: $dir/README.md" -Color "Success"
        }
    }
    
    # Create .gitignore
    Write-Header "🔒 Creating .gitignore"
    
    $gitignoreContent = @"
# Control Center .gitignore
# Created: $(Get-Date -Format "yyyy-MM-dd HH:mm")

# Runtime files
runtime/
.terminal-server.pid
.terminal-server-job.txt
*.pid

# Logs
logs/*.log
logs/*.txt

# Backups
backups/

# Node modules
servers/node_modules/
node_modules/

# Package locks (optional - uncomment if needed)
# servers/package-lock.json

# OS files
.DS_Store
Thumbs.db
desktop.ini

# Editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
*.tmp
*.temp
"@
    
    $gitignorePath = Join-Path $controlCenterPath ".gitignore"
    $gitignoreContent | Out-File -FilePath $gitignorePath -Encoding UTF8
    Write-ColorOutput "  ✅ Created: .gitignore" -Color "Success"
    
    # Create main INDEX.md
    Write-Header "📚 Creating INDEX.md"
    
    $indexContent = @"
# 🎛️ Control Center - Directory Index

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd HH:mm")  
**Version:** 2.0 (Reorganized)

---

## 📂 Directory Structure

``````
control-center/
├── 📁 app/              → Frontend files (HTML, CSS, JS)
├── 📁 servers/          → Backend Node.js servers
├── 📁 docs/             → Documentation (all .md files)
├── 📁 scripts/          → Startup and utility scripts
├── 📁 runtime/          → Runtime files (gitignored)
├── 📁 backups/          → Backup files (gitignored)
├── 📁 data/             → Dashboard data files
├── 📁 logs/             → Log files
├── 📁 modules/          → Reusable modules
└── 📄 INDEX.md          → This file
``````

---

## 🚀 Quick Start

### Start Control Center:
``````powershell
# Using batch file:
.\scripts\START_DASHBOARD.bat

# Using PowerShell:
.\scripts\start-dashboard.ps1

# Using VBScript (silent):
.\scripts\start-servers.vbs
``````

### Access:
- **Control Center V2:** http://localhost:3002
- **Control Center V1:** http://localhost:3002/index-v1.html
- **Terminal Server:** http://localhost:3003

---

## 📁 Directory Details

### app/ - Frontend Files
Main application files for the Control Center interface.

**Key Files:**
- `index.html` - Main interface (V2)
- `index-v1.html` - Legacy interface (V1)
- `dashboard.html` - Dashboard view

[See app/README.md for details](app/README.md)

---

### servers/ - Backend Servers
Node.js server files for terminal and dashboard services.

**Services:**
- Terminal Server (port 3003)
- Dashboard Server (port 3002)

[See servers/README.md for details](servers/README.md)

---

### docs/ - Documentation
All markdown documentation files.

**Topics:**
- Control Center guides
- Integration documentation
- Current state reports
- Session logs

[See docs/README.md for details](docs/README.md)

---

### scripts/ - Startup Scripts
Scripts to start, stop, and manage Control Center services.

**Available Scripts:**
- `start-dashboard.ps1` - Start dashboard server
- `start-servers.vbs` - Start all servers (silent)
- `START_DASHBOARD.bat` - Windows batch starter
- `create-shortcut.ps1` - Create desktop shortcut

[See scripts/README.md for details](scripts/README.md)

---

### data/ - Dashboard Data
JSON configuration files for dashboard functionality.

**Files:**
- `dashboard-data.json` - Main dashboard data
- `project-status.json` - Project status information
- `terminal-server-info.json` - Terminal server configuration

---

### logs/ - Log Files
Runtime logs from servers and services.

**⚠️ Note:** Logs older than 7 days are automatically cleaned.

---

### modules/ - Reusable Modules
Shared JavaScript modules used across the application.

---

## 🔄 Maintenance

### Backup Created
A backup was created before reorganization:
``````
backups/backup-$timestamp/
``````

### Restore from Backup
``````powershell
# If something went wrong:
Copy-Item -Path "backups/backup-$timestamp/*" -Destination "." -Recurse -Force
``````

---

## 📝 Documentation

For complete documentation, see:
- [CONTROL_CENTER_SUMMARY.md](docs/CONTROL_CENTER_SUMMARY.md)
- [DASHBOARD_GUIDE.md](docs/DASHBOARD_GUIDE.md)
- [HOW_TO_START.md](docs/HOW_TO_START.md)

---

## 🆘 Troubleshooting

### Servers not starting?
1. Check if ports 3002 and 3003 are free
2. Verify Node.js is installed: ``node --version``
3. Install dependencies: ``cd servers && npm install``

### Files not found?
After reorganization, files are in subdirectories:
- HTML files → `app/`
- Server files → `servers/`
- Scripts → `scripts/`

---

**Need help?** Check [docs/](docs/) for guides or see SESSION_LOG.md for recent changes.
"@
    
    $indexPath = Join-Path $controlCenterPath "INDEX.md"
    $indexContent | Out-File -FilePath $indexPath -Encoding UTF8
    Write-ColorOutput "  ✅ Created: INDEX.md" -Color "Success"
    
} else {
    Write-Header "🔍 Dry Run Complete"
    Write-ColorOutput "No changes were made. Run without -DryRun to apply changes." -Color "Info"
}

# Summary Report
Write-Header "📊 Summary Report"

$report = @"

✅ Control Center Reorganization Complete!

📂 New Structure:
   - app/         : $(($moveActions | Where-Object {$_.Category -eq "app"}).Count) files
   - servers/     : $(($moveActions | Where-Object {$_.Category -eq "servers"}).Count) files
   - docs/        : $(($moveActions | Where-Object {$_.Category -eq "docs"}).Count) files
   - scripts/     : $(($moveActions | Where-Object {$_.Category -eq "scripts"}).Count) files
   - runtime/     : $(($moveActions | Where-Object {$_.Category -eq "runtime"}).Count) files
   - backups/     : $(($moveActions | Where-Object {$_.Category -eq "backups"}).Count) files

📝 Files Created:
   - 6 README.md files (one per subdirectory)
   - 1 INDEX.md (main navigation)
   - 1 .gitignore (runtime files)

$(if ($Backup -and -not $DryRun) {
"💾 Backup Location:
   $backupPath"
})

🎯 Next Steps:
   1. Open INDEX.md to verify structure
   2. Test services: .\scripts\start-dashboard.ps1
   3. Update any bookmarks or shortcuts
   4. Review and customize README files

⏱️ Total Time: $(((Get-Date) - $startTime).TotalSeconds) seconds

"@

$startTime = Get-Date # Define start time at beginning
Write-ColorOutput $report -Color "Success"

Write-Header "🎉 Done!"
Write-ColorOutput "Control Center is now organized and ready to use!" -Color "Success"

# Save report
if (-not $DryRun) {
    $reportPath = Join-Path $controlCenterPath "logs\reorganization-$timestamp.log"
    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-ColorOutput "`n📄 Report saved to: $reportPath" -Color "Info"
}
