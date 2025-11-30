<#
.SYNOPSIS
    Testing Deployment - סקריפט ראשי לסביבת בדיקות
    
.DESCRIPTION
    מתחבר ל-PROJECT_CONTROL_CENTER
    מריץ בדיקות מקיפות לפני פריסה
    
.PARAMETER SkipTests
    דלג על בדיקות והרץ רק פריסה

.NOTES
    Version: 1.0
    Date: 12 November 2025
    Integration: PROJECT_CONTROL_CENTER - Testing Button
#>

param(
    [switch]$SkipTests,
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
$Environment = "Testing"
$ContainerName = "escriptorium_clean-web-1"

# ═══════════════════════════════════════════════════════════════════════════
# Header
# ═══════════════════════════════════════════════════════════════════════════

Write-Box -Lines @(
    "🧪 Testing Deployment",
    "Environment: $Environment",
    "Mode: $(if ($SkipTests) { 'Deploy Only' } else { 'Full Testing' })",
    "Time: $(Get-Date -Format 'HH:mm:ss')"
) -Color Magenta

# ═══════════════════════════════════════════════════════════════════════════
# Step 1: Pre-Deployment Tests
# ═══════════════════════════════════════════════════════════════════════════

$testResults = @{
    Total = 0
    Passed = 0
    Failed = 0
    Warnings = 0
}

if (-not $SkipTests) {
    Write-Header "Step 1: Running Pre-Deployment Tests"
    
    # Test 1: Requirements Check
    Write-Info "Test 1/5: Requirements Check"
    $testResults.Total++
    
    if (Test-Path "SCRIPTS\check-requirements.ps1") {
        $checkResult = & "SCRIPTS\check-requirements.ps1"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Requirements check passed"
            $testResults.Passed++
        }
        else {
            Write-Warning-Custom "Requirements check has warnings"
            $testResults.Warnings++
        }
    }
    else {
        Write-Warning-Custom "Requirements checker not found"
        $testResults.Warnings++
    }
    
    # Test 2: Docker Health
    Write-Info "Test 2/5: Docker Health Check"
    $testResults.Total++
    
    if (Test-DockerRunning) {
        $health = Test-ContainerHealth -ContainerName $ContainerName
        
        if ($health.IsRunning -and -not $health.HasErrors) {
            Write-Success "Docker healthy"
            $testResults.Passed++
        }
        else {
            Write-Warning-Custom "Docker has issues"
            $testResults.Warnings++
        }
    }
    else {
        Write-Error-Custom "Docker not running"
        $testResults.Failed++
    }
    
    # Test 3: Build Output Verification
    Write-Info "Test 3/5: Build Output Check"
    $testResults.Total++
    
    $frontendPath = "eScriptorium_CLEAN\front"
    $distPath = Join-Path $frontendPath "dist"
    
    if (Test-BuildOutput -FrontendPath $frontendPath) {
        $stats = Get-BuildStatistics -FrontendPath $frontendPath
        Write-Success "Build output valid ($($stats.TotalFiles) files)"
        $testResults.Passed++
    }
    else {
        Write-Warning-Custom "Build output incomplete"
        $testResults.Warnings++
    }
    
    # Test 4: Container Connectivity
    Write-Info "Test 4/5: Container Connectivity"
    $testResults.Total++
    
    try {
        $response = Invoke-ContainerCommand -ContainerName $ContainerName -Command "echo 'test'"
        
        if ($response) {
            Write-Success "Container accessible"
            $testResults.Passed++
        }
        else {
            Write-Warning-Custom "Container not responding"
            $testResults.Warnings++
        }
    }
    catch {
        Write-Error-Custom "Cannot connect to container"
        $testResults.Failed++
    }
    
    # Test 5: File Changes Analysis
    Write-Info "Test 5/5: File Changes Analysis"
    $testResults.Total++
    
    Initialize-ChangeTracker
    $changes = Get-ChangedFiles
    
    Write-Success "Detected $($changes.Count) changes"
    $testResults.Passed++
    
    # Test Summary
    Write-Host ""
    Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "Test Results:" -ForegroundColor White
    Write-Host "  ✓ Passed:   $($testResults.Passed)/$($testResults.Total)" -ForegroundColor Green
    Write-Host "  ✗ Failed:   $($testResults.Failed)/$($testResults.Total)" -ForegroundColor Red
    Write-Host "  ⚠ Warnings: $($testResults.Warnings)/$($testResults.Total)" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
    
    # Decision
    if ($testResults.Failed -gt 0 -and -not $Force) {
        Write-Box -Lines @("❌ Tests failed", "Fix issues or use -Force") -Color Red
        exit 1
    }
    
    if ($testResults.Warnings -gt 0) {
        Write-Host "`n⚠️  Tests passed with warnings" -ForegroundColor Yellow
        Write-Host "   Continue with deployment? (Y/N): " -NoNewline -ForegroundColor Cyan
        $response = Read-Host
        if ($response -ne "Y" -and $response -ne "y") {
            Write-Warning-Custom "Deployment cancelled"
            exit 0
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# Step 2: Deployment
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Step 2: Executing Deployment"

# Call dev-deploy for actual deployment
$deployArgs = @()
if ($Force) { $deployArgs += "-Force" }

Write-Info "Calling deploy-dev.ps1..."

$deployResult = & "SCRIPTS\deploy-dev.ps1" @deployArgs

$deploySuccess = $LASTEXITCODE -eq 0

if ($deploySuccess) {
    Write-Success "Deployment completed"
}
else {
    Write-Error-Custom "Deployment failed"
}

# ═══════════════════════════════════════════════════════════════════════════
# Step 3: Post-Deployment Verification
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Step 3: Post-Deployment Verification"

$verifyResults = @{
    Total = 0
    Passed = 0
    Failed = 0
}

# Verify 1: Container Status
Write-Info "Verify 1/3: Container Status"
$verifyResults.Total++

$status = Get-ContainerStatus -ContainerName $ContainerName

if ($status -match "Up") {
    Write-Success "Container running"
    $verifyResults.Passed++
}
else {
    Write-Error-Custom "Container not running"
    $verifyResults.Failed++
}

# Verify 2: Logs Check
Write-Info "Verify 2/3: Error Logs"
$verifyResults.Total++

$logs = Get-ContainerLogs -ContainerName $ContainerName -Lines 50

$errorCount = ($logs | Select-String -Pattern "ERROR|CRITICAL" | Measure-Object).Count

if ($errorCount -eq 0) {
    Write-Success "No errors in logs"
    $verifyResults.Passed++
}
else {
    Write-Warning-Custom "$errorCount errors found in logs"
    $verifyResults.Failed++
}

# Verify 3: Service Response
Write-Info "Verify 3/3: Service Response Test"
$verifyResults.Total++

try {
    $response = Test-NetConnection -ComputerName "localhost" -Port 8082 -WarningAction SilentlyContinue -ErrorAction Stop
    
    if ($response.TcpTestSucceeded) {
        Write-Success "Service responding on port 8082"
        $verifyResults.Passed++
    }
    else {
        Write-Warning-Custom "Service not responding"
        $verifyResults.Failed++
    }
}
catch {
    Write-Warning-Custom "Cannot test service response"
    $verifyResults.Failed++
}

# ═══════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════

$duration = ((Get-Date) - $StartTime).TotalSeconds
$durationStr = "$([Math]::Round($duration, 1))s"

$overallPassed = $testResults.Passed + $verifyResults.Passed
$overallTotal = $testResults.Total + $verifyResults.Total
$overallFailed = $testResults.Failed + $verifyResults.Failed

$status = if ($overallFailed -eq 0 -and $deploySuccess) { "Success" }
          elseif ($deploySuccess) { "Success with Warnings" }
          else { "Failed" }

# Save to tracking
Save-TrackingEntry `
    -Environment $Environment `
    -Actions @("pre_tests", "deployment", "post_verify") `
    -Status $status `
    -Duration $durationStr `
    -Changes @()

# Display summary
Write-Host ""
Write-Box -Lines @(
    "📊 Testing Summary",
    "Environment: $Environment",
    "Status: $status",
    "Duration: $durationStr",
    "Tests Passed: $overallPassed/$overallTotal",
    "Deployment: $(if ($deploySuccess) { 'Success' } else { 'Failed' })"
) -Color $(if ($status -eq "Success") { "Green" } else { "Yellow" })

Write-Host ""

# Exit code
exit $(if ($status -eq "Success") { 0 } else { 1 })
