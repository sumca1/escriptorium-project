<#
.SYNOPSIS
    Production Deployment - סקריפט ראשי לסביבת ייצור
    
.DESCRIPTION
    מתחבר ל-PROJECT_CONTROL_CENTER
    פריסה זהירה ובטוחה לייצור עם גיבויים
    
.PARAMETER Confirm
    דרוש אישור לפני פריסה
    
.PARAMETER Backup
    צור גיבוי לפני פריסה

.NOTES
    Version: 1.0
    Date: 12 November 2025
    Integration: PROJECT_CONTROL_CENTER - Production Button
    ⚠️  CRITICAL: Production environment - handle with care!
#>

param(
    [switch]$Confirm = $true,
    [switch]$Backup = $true,
    [switch]$Force
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
$Environment = "Production"
$ContainerName = "escriptorium_clean-web-1"
$BackupPath = "backups\prod-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# ═══════════════════════════════════════════════════════════════════════════
# Header
# ═══════════════════════════════════════════════════════════════════════════

Write-Box -Lines @(
    "🚨 Production Deployment",
    "Environment: $Environment",
    "⚠️  CRITICAL: Handle with care!",
    "Time: $(Get-Date -Format 'HH:mm:ss')"
) -Color Red

# ═══════════════════════════════════════════════════════════════════════════
# Safety Confirmation
# ═══════════════════════════════════════════════════════════════════════════

if ($Confirm -and -not $Force) {
    Write-Host "`n⚠️  PRODUCTION DEPLOYMENT WARNING" -ForegroundColor Red -BackgroundColor Yellow
    Write-Host "   This will deploy to PRODUCTION environment!" -ForegroundColor Red
    Write-Host "   Have you:" -ForegroundColor Yellow
    Write-Host "   ✓ Tested in Development?" -ForegroundColor Yellow
    Write-Host "   ✓ Verified in Testing?" -ForegroundColor Yellow
    Write-Host "   ✓ Reviewed all changes?" -ForegroundColor Yellow
    Write-Host "   ✓ Notified the team?" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Type 'DEPLOY TO PRODUCTION' to continue: " -NoNewline -ForegroundColor Red
    $response = Read-Host
    
    if ($response -ne "DEPLOY TO PRODUCTION") {
        Write-Box -Lines @("❌ Deployment cancelled", "Safety first!") -Color Green
        exit 0
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# Step 1: Pre-Deployment Checks
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Step 1: Pre-Deployment Safety Checks"

$safetyChecks = @{
    Total = 0
    Passed = 0
    Failed = 0
}

# Check 1: Testing deployment success
Write-Info "Check 1/5: Previous Testing Status"
$safetyChecks.Total++

if (Test-Path "tracking-deployment.json") {
    $tracking = Get-Content "tracking-deployment.json" -Raw | ConvertFrom-Json
    $lastTest = $tracking.Entries | Where-Object { $_.Environment -eq "Testing" } | Select-Object -Last 1
    
    if ($lastTest -and $lastTest.Status -eq "Success") {
        $timeSince = ((Get-Date) - [DateTime]::Parse($lastTest.Timestamp)).TotalHours
        Write-Success "Testing passed $([Math]::Round($timeSince, 1))h ago"
        $safetyChecks.Passed++
    }
    else {
        Write-Warning-Custom "No recent successful testing deployment"
        $safetyChecks.Failed++
    }
}
else {
    Write-Warning-Custom "No testing history found"
    $safetyChecks.Failed++
}

# Check 2: Docker health
Write-Info "Check 2/5: Docker Health"
$safetyChecks.Total++

if (Test-DockerRunning) {
    $health = Test-ContainerHealth -ContainerName $ContainerName
    
    if ($health.IsRunning -and -not $health.HasErrors) {
        Write-Success "Docker healthy"
        $safetyChecks.Passed++
    }
    else {
        Write-Error-Custom "Docker has issues"
        $safetyChecks.Failed++
    }
}
else {
    Write-Error-Custom "Docker not running"
    $safetyChecks.Failed++
}

# Check 3: Disk space
Write-Info "Check 3/5: Disk Space"
$safetyChecks.Total++

$drive = Get-PSDrive -Name (Split-Path -Qualifier $PWD)
$freeGB = [Math]::Round($drive.Free / 1GB, 2)

if ($freeGB -gt 5) {
    Write-Success "Disk space: ${freeGB}GB free"
    $safetyChecks.Passed++
}
else {
    Write-Warning-Custom "Low disk space: ${freeGB}GB"
    $safetyChecks.Failed++
}

# Check 4: Active connections (simulated)
Write-Info "Check 4/5: Active Connections Check"
$safetyChecks.Total++

# In real production, check actual user connections
# For now, just verify service is accessible
try {
    $response = Test-NetConnection -ComputerName "localhost" -Port 8082 -WarningAction SilentlyContinue -ErrorAction Stop
    
    if ($response.TcpTestSucceeded) {
        Write-Success "Service accessible"
        $safetyChecks.Passed++
    }
    else {
        Write-Warning-Custom "Service not accessible"
        $safetyChecks.Failed++
    }
}
catch {
    Write-Warning-Custom "Cannot check service"
    $safetyChecks.Failed++
}

# Check 5: File changes review
Write-Info "Check 5/5: File Changes Review"
$safetyChecks.Total++

Initialize-ChangeTracker
$changes = Get-ChangedFiles

if ($changes.Count -eq 0) {
    Write-Success "No pending changes"
    $safetyChecks.Passed++
}
else {
    Write-Warning-Custom "$($changes.Count) changes detected"
    Show-ChangesReport -Changes $changes -Actions @()
    $safetyChecks.Passed++  # Not a failure, just information
}

# Safety Summary
Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Red
Write-Host "Safety Checks:" -ForegroundColor White
Write-Host "  ✓ Passed: $($safetyChecks.Passed)/$($safetyChecks.Total)" -ForegroundColor Green
Write-Host "  ✗ Failed: $($safetyChecks.Failed)/$($safetyChecks.Total)" -ForegroundColor Red
Write-Host "═══════════════════════════════════════" -ForegroundColor Red

if ($safetyChecks.Failed -gt 0 -and -not $Force) {
    Write-Box -Lines @("❌ Safety checks failed", "Fix issues or use -Force") -Color Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════
# Step 2: Backup
# ═══════════════════════════════════════════════════════════════════════════

if ($Backup) {
    Write-Header "Step 2: Creating Backup"
    
    try {
        # Create backup directory
        if (-not (Test-Path "backups")) {
            New-Item -Path "backups" -ItemType Directory | Out-Null
        }
        New-Item -Path $BackupPath -ItemType Directory -Force | Out-Null
        
        # Backup critical files
        $backupItems = @(
            "eScriptorium_CLEAN\front\dist",
            "docker-compose.yml",
            "tracking-deployment.json"
        )
        
        $backedUp = 0
        foreach ($item in $backupItems) {
            if (Test-Path $item) {
                $dest = Join-Path $BackupPath (Split-Path -Leaf $item)
                Copy-Item -Path $item -Destination $dest -Recurse -Force
                $backedUp++
            }
        }
        
        Write-Success "Backup created: $BackupPath ($backedUp items)"
    }
    catch {
        Write-Error-Custom "Backup failed: $_"
        Write-Host "   Continue without backup? (Y/N): " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        if ($response -ne "Y" -and $response -ne "y") {
            exit 1
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# Step 3: Deployment
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Step 3: Executing Production Deployment"

# Call dev-deploy with appropriate flags
Write-Info "Deploying to production..."

$deployArgs = @("-Force")
$null = & "SCRIPTS\deploy-dev.ps1" @deployArgs

$deploySuccess = $LASTEXITCODE -eq 0

if ($deploySuccess) {
    Write-Success "Production deployment completed"
}
else {
    Write-Error-Custom "Production deployment failed"
    
    if ($Backup) {
        Write-Host ""
        Write-Host "⚠️  Deployment failed! Backup available at:" -ForegroundColor Red
        Write-Host "   $BackupPath" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   Restore backup? (Y/N): " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        
        if ($response -eq "Y" -or $response -eq "y") {
            Write-Info "Restoring backup..."
            # Restore logic here
            Write-Warning-Custom "Manual restore required - see backup at $BackupPath"
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# Step 4: Post-Deployment Monitoring
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Step 4: Post-Deployment Monitoring"

Write-Info "Monitoring for 30 seconds..."

$monitorStart = Get-Date
$issues = @()

for ($i = 0; $i -lt 6; $i++) {
    Start-Sleep -Seconds 5
    
    # Check container status
    $status = Get-ContainerStatus -ContainerName $ContainerName
    
    if ($status -notmatch "Up") {
        $issues += "Container stopped at +$($i*5)s"
        Write-Warning-Custom "Container issue detected"
    }
    
    # Check for errors in logs
    $logs = Get-ContainerLogs -ContainerName $ContainerName -Lines 20
    $errors = $logs | Select-String -Pattern "ERROR|CRITICAL"
    
    if ($errors.Count -gt 0) {
        $issues += "$($errors.Count) errors at +$($i*5)s"
    }
    
    # Progress indicator
    $percent = (($i + 1) / 6) * 100
    Write-Host "`r  Monitoring: $($i*5)s / 30s [$percent%]" -NoNewline
}

Write-Host ""

if ($issues.Count -eq 0) {
    Write-Success "No issues detected during monitoring"
}
else {
    Write-Warning-Custom "$($issues.Count) issues detected:"
    $issues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}

# ═══════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════

$duration = ((Get-Date) - $StartTime).TotalSeconds
$durationStr = "$([Math]::Round($duration, 1))s"

$status = if ($deploySuccess -and $issues.Count -eq 0) { "Success" }
          elseif ($deploySuccess) { "Success with Warnings" }
          else { "Failed" }

# Save to tracking
Save-TrackingEntry `
    -Environment $Environment `
    -Actions @("safety_checks", "backup", "deployment", "monitoring") `
    -Status $status `
    -Duration $durationStr `
    -Changes $changes

# Display summary
Write-Host ""
Write-Box -Lines @(
    "📊 Production Deployment Summary",
    "Environment: $Environment",
    "Status: $status",
    "Duration: $durationStr",
    "Safety Checks: $($safetyChecks.Passed)/$($safetyChecks.Total)",
    "Backup: $(if ($Backup) { $BackupPath } else { 'Skipped' })",
    "Issues: $($issues.Count)"
) -Color $(if ($status -eq "Success") { "Green" } elseif ($status -eq "Success with Warnings") { "Yellow" } else { "Red" })

if ($status -eq "Success") {
    Write-Host ""
    Write-Host "✅ Production deployment successful!" -ForegroundColor Green
    Write-Host "   Monitor the system closely for the next hour" -ForegroundColor Cyan
}
elseif ($status -eq "Success with Warnings") {
    Write-Host ""
    Write-Host "⚠️  Deployment completed with warnings" -ForegroundColor Yellow
    Write-Host "   Review issues and monitor closely" -ForegroundColor Yellow
}
else {
    Write-Host ""
    Write-Host "❌ Production deployment failed" -ForegroundColor Red
    Write-Host "   Backup available: $BackupPath" -ForegroundColor Yellow
}

Write-Host ""

# Exit code
exit $(if ($status -eq "Success") { 0 } else { 1 })
