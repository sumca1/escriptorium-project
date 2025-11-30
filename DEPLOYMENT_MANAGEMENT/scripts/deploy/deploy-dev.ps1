<#
.SYNOPSIS
    Development Deployment - סקריפט ראשי לסביבת פיתוח
    
.DESCRIPTION
    מתחבר ל-PROJECT_CONTROL_CENTER
    מזהה שינויים אוטומטית ומריץ רק מה שצריך
    
.PARAMETER Force
    הרץ הכל גם אם אין שינויים
    
.PARAMETER SkipDetection
    דלג על זיהוי שינויים והרץ הכל

.NOTES
    Version: 1.0
    Date: 12 November 2025
    Integration: PROJECT_CONTROL_CENTER - Development Button
#>

param(
    [switch]$Force,
    [switch]$SkipDetection,
    [switch]$Quick
)

# ═══════════════════════════════════════════════════════════════════════════
# Setup
# ═══════════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

# Paths
$ScriptRoot = Split-Path -Parent $PSCommandPath
$CorePath = Join-Path $ScriptRoot "core"
$LibPath = Join-Path $ScriptRoot "lib"

# Load libraries
. (Join-Path $CorePath "ui-functions.ps1")
. (Join-Path $CorePath "docker-functions.ps1")
. (Join-Path $CorePath "build-functions.ps1")
. (Join-Path $LibPath "file-change-tracker.ps1")

# Configuration
$Environment = "Development"
$ContainerName = "escriptorium_clean-web-1"
$FrontendPath = "eScriptorium_CLEAN\front"
$DockerComposePath = "eScriptorium_CLEAN"  # Where docker-compose.yml is located

# ═══════════════════════════════════════════════════════════════════════════
# Header
# ═══════════════════════════════════════════════════════════════════════════

Write-Box -Lines @(
    "🚀 Development Deployment",
    "Environment: $Environment",
    "Mode: $(if ($Force) { 'Force' } elseif ($SkipDetection) { 'Full' } elseif ($Quick) { 'Quick' } else { 'Smart' })",
    "Time: $(Get-Date -Format 'HH:mm:ss')"
) -Color Cyan

# ═══════════════════════════════════════════════════════════════════════════
# Step 1: File Change Detection
# ═══════════════════════════════════════════════════════════════════════════

$changes = @()
$requiredActions = @()

if (-not $SkipDetection -and -not $Force) {
    Write-Header "Step 1: Detecting File Changes"
    
    Initialize-ChangeTracker
    $changes = Get-ChangedFiles
    
    if ($changes.Count -eq 0) {
        Show-ChangesReport -Changes $changes -Actions @()
        Write-Box -Lines @("✅ No changes detected", "System is up to date") -Color Green
        exit 0
    }
    
    $requiredActions = Get-RequiredActions -Changes $changes
    Show-ChangesReport -Changes $changes -Actions $requiredActions
    
    # Confirmation
    Write-Host "`n⚠️  Found $($changes.Count) changes requiring $($requiredActions.Count) actions" -ForegroundColor Yellow
    Write-Host "   Continue with deployment? (Y/N): " -NoNewline -ForegroundColor Cyan
    $response = Read-Host
    if ($response -ne "Y" -and $response -ne "y") {
        Write-Warning-Custom "Deployment cancelled by user"
        exit 0
    }
}
else {
    Write-Header "Step 1: Running in $(if ($Force) { 'Force' } else { 'Full' }) mode - skipping change detection"
    
    # Run all actions
    $requiredActions = @(
        @{ Action = "npm_install"; Priority = 1 },
        @{ Action = "build_frontend"; Priority = 2 },
        @{ Action = "deploy_static"; Priority = 3 },
        @{ Action = "restart_web"; Priority = 4 }
    )
}

# ═══════════════════════════════════════════════════════════════════════════
# Step 2: Prerequisites Check
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Step 2: Prerequisites Check"

$prereqPassed = $true

# Docker
if (-not (Test-DockerInstalled)) {
    Write-Error-Custom "Docker not installed"
    $prereqPassed = $false
}
elseif (-not (Test-DockerRunning)) {
    Write-Error-Custom "Docker not running"
    $prereqPassed = $false
}
else {
    Write-Success "Docker: Running"
}

# npm (if needed)
$needsNpm = $requiredActions | Where-Object { $_.Action -in @("npm_install", "build_frontend") }
if ($needsNpm) {
    if (-not (Test-NpmInstalled)) {
        Write-Error-Custom "npm not installed"
        $prereqPassed = $false
    }
    else {
        Write-Success "npm: Available"
    }
}

if (-not $prereqPassed) {
    Write-Box -Lines @("❌ Prerequisites check failed", "Fix issues and try again") -Color Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════
# Step 3: Execute Actions
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Step 3: Executing Required Actions"

$executedActions = @()
$failedActions = @()

foreach ($actionObj in $requiredActions) {
    $action = $actionObj.Action
    
    Write-Info "▶️  Executing: $action"
    
    try {
        switch ($action) {
            "npm_install" {
                if (-not $Quick) {
                    Push-Location $FrontendPath
                    $result = Install-NpmDependencies -UseNpmCi
                    Pop-Location
                    
                    if ($result) {
                        Write-Success "npm install completed"
                        $executedActions += $action
                    }
                    else {
                        throw "npm install failed"
                    }
                }
                else {
                    Write-Info "Skipped (Quick mode)"
                }
            }
            
            "build_frontend" {
                Push-Location $FrontendPath
                $result = Build-Frontend
                Pop-Location
                
                if ($result) {
                    Write-Success "Frontend build completed"
                    $executedActions += $action
                }
                else {
                    throw "Frontend build failed"
                }
            }
            
            "deploy_static" {
                # Copy dist files to container
                $distPath = Join-Path $FrontendPath "dist"
                if (Test-Path $distPath) {
                    $files = Get-ChildItem -Path $distPath -File
                    $copied = 0
                    
                    foreach ($file in $files) {
                        $success = Copy-ToContainer `
                            -SourcePath $file.FullName `
                            -DestinationPath "/usr/src/app/static/" `
                            -ContainerName $ContainerName
                        
                        if ($success) { $copied++ }
                    }
                    
                    Write-Success "Deployed $copied/$($files.Count) files"
                    $executedActions += $action
                }
                else {
                    Write-Warning-Custom "dist/ not found - skipping"
                }
            }
            
            "compile_translations" {
                $result = Invoke-ContainerCommand `
                    -ContainerName $ContainerName `
                    -Command "python manage.py compilemessages -l he"
                
                if ($result) {
                    Write-Success "Translations compiled"
                    $executedActions += $action
                }
                else {
                    throw "Translation compilation failed"
                }
            }
            
            "restart_web" {
                $result = Restart-DockerService -Services @("web")
                
                if ($result) {
                    Write-Success "Web service restarted"
                    $executedActions += $action
                }
                else {
                    throw "Web restart failed"
                }
            }
            
            "restart_all" {
                $result = Restart-DockerService -Services @("web", "nginx")
                
                if ($result) {
                    Write-Success "All services restarted"
                    $executedActions += $action
                }
                else {
                    throw "Service restart failed"
                }
            }
            
            default {
                Write-Warning-Custom "Unknown action: $action"
            }
        }
    }
    catch {
        Write-Error-Custom "Action failed: $action - $_"
        $failedActions += $action
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# Step 4: Verification
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Step 4: Verification"

$health = Test-ContainerHealth -ContainerName $ContainerName

if ($health.IsRunning) {
    Write-Success "Container is running"
    
    if (-not $health.HasErrors) {
        Write-Success "No errors in logs"
    }
    else {
        Write-Warning-Custom "Some errors found in logs"
        if ($health.Logs) {
            $health.Logs | Select-Object -First 5 | ForEach-Object {
                Write-Host "  $_" -ForegroundColor DarkYellow
            }
        }
    }
}
else {
    Write-Error-Custom "Container is not running"
}

# ═══════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════

$duration = ((Get-Date) - $StartTime).TotalSeconds
$durationStr = "$([Math]::Round($duration, 1))s"

$status = if ($failedActions.Count -eq 0) { "Success" } 
          elseif ($executedActions.Count -gt 0) { "Partial" }
          else { "Failed" }

# Save to tracking table
Save-TrackingEntry `
    -Environment $Environment `
    -Actions $executedActions `
    -Status $status `
    -Duration $durationStr `
    -Changes $changes

# Display summary
Write-Host ""
Write-Box -Lines @(
    "📊 Deployment Summary",
    "Environment: $Environment",
    "Status: $status",
    "Duration: $durationStr",
    "Actions: $($executedActions.Count)/$($requiredActions.Count)",
    "Changes: $($changes.Count) files"
) -Color $(if ($status -eq "Success") { "Green" } elseif ($status -eq "Partial") { "Yellow" } else { "Red" })

if ($failedActions.Count -gt 0) {
    Write-Host "`n❌ Failed Actions:" -ForegroundColor Red
    $failedActions | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
}

Write-Host ""

# Exit code
exit $(if ($status -eq "Success") { 0 } else { 1 })
