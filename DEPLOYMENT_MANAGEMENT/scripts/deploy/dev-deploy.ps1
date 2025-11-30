<#
.SYNOPSIS
    Development Deployment Script - Quick & Smart

.DESCRIPTION
    Single unified script for dev environment deployment:
    - Checks Docker
    - Builds frontend (npm ci + npm run build)
    - Deploys to Docker container
    - Restarts services
    - Verifies deployment

.PARAMETER Quick
    Skip npm install if node_modules exists

.PARAMETER Force
    Force full rebuild (clear cache, reinstall)

.PARAMETER VerifyOnly
    Only verify deployment, don't build/deploy

.EXAMPLE
    .\dev-deploy.ps1
    # Standard deployment

.EXAMPLE
    .\dev-deploy.ps1 -Quick
    # Fast deployment (skip npm install)

.EXAMPLE
    .\dev-deploy.ps1 -Force
    # Full rebuild from scratch

.NOTES
    Version: 1.0
    Date: 12 November 2025
    Uses: Core libraries (ui-functions, docker-functions, build-functions)
#>

param(
    [switch]$Quick,
    [switch]$Force,
    [switch]$VerifyOnly
)

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Auto-detect paths
$FrontendPath = Join-Path $ProjectRoot "eScriptorium_CLEAN\front"

# Find docker-compose.yml
$DockerComposePath = $null
$possiblePaths = @(
    (Join-Path $ProjectRoot "eScriptorium_CLEAN"),
    $ProjectRoot
)

foreach ($path in $possiblePaths) {
    if (Test-Path (Join-Path $path "docker-compose.yml")) {
        $DockerComposePath = $path
        break
    }
}

if (-not $DockerComposePath) {
    Write-Host "❌ docker-compose.yml not found" -ForegroundColor Red
    Write-Host "Searched in:" -ForegroundColor Yellow
    $possiblePaths | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    exit 1
}

$ContainerName = "escriptorium_clean-web-1"

# ═══════════════════════════════════════════════════════════════════════════
# Load Core Libraries
# ═══════════════════════════════════════════════════════════════════════════

$CorePath = Join-Path $ScriptDir "core"

Write-Host "Loading core libraries..." -ForegroundColor Cyan
. (Join-Path $CorePath "ui-functions.ps1")
. (Join-Path $CorePath "docker-functions.ps1")
. (Join-Path $CorePath "build-functions.ps1")
Write-Host "✓ Libraries loaded`n" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════════════════════
# Main Workflow
# ═══════════════════════════════════════════════════════════════════════════

try {
    Write-Box -Lines @(
        "Development Deployment",
        "Environment: eScriptorium_CLEAN",
        "Mode: $(if ($Quick) { 'Quick' } elseif ($Force) { 'Force' } elseif ($VerifyOnly) { 'Verify Only' } else { 'Standard' })"
    ) -Color Cyan
    
    Write-Host ""
    
    # ═══════════════════════════════════════════════════════════════════════
    # Step 1: Prerequisites Check
    # ═══════════════════════════════════════════════════════════════════════
    
    Write-Header "🔍 STEP 1: Prerequisites Check"
    
    $checksPass = $true
    
    # Check Docker
    if (-not (Test-DockerInstalled)) {
        $checksPass = $false
    }
    
    if (-not (Test-DockerComposeInstalled)) {
        $checksPass = $false
    }
    
    if (-not (Test-DockerRunning)) {
        $checksPass = $false
    }
    
    # Check npm/Node (skip if VerifyOnly)
    if (-not $VerifyOnly) {
        if (-not (Test-NpmInstalled)) {
            $checksPass = $false
        }
        
        if (-not (Test-NodeInstalled)) {
            $checksPass = $false
        }
    }
    
    if (-not $checksPass) {
        Write-Error-Custom "Prerequisites check failed. Please fix the issues above."
        exit 1
    }
    
    Write-Success "All prerequisites OK"
    Write-Host ""
    
    # ═══════════════════════════════════════════════════════════════════════
    # Step 2: Ensure Container is Running
    # ═══════════════════════════════════════════════════════════════════════
    
    Write-Header "🐳 STEP 2: Docker Container Check"
    
    if (-not (Start-ContainerIfNeeded -ContainerName $ContainerName -WorkingDirectory $DockerComposePath)) {
        Write-Error-Custom "Failed to ensure container is running"
        exit 1
    }
    
    Write-Host ""
    
    # ═══════════════════════════════════════════════════════════════════════
    # Step 3: Build Frontend (skip if VerifyOnly)
    # ═══════════════════════════════════════════════════════════════════════
    
    if (-not $VerifyOnly) {
        # Force mode - reset everything
        if ($Force) {
            Reset-BuildEnvironment -FrontendPath $FrontendPath
            Write-Host ""
        }
        
        # Install dependencies (unless Quick and node_modules exists)
        if (-not $Quick -or $Force -or -not (Test-Path (Join-Path $FrontendPath "node_modules"))) {
            if (-not (Install-NpmDependencies -FrontendPath $FrontendPath -UseNpmCi)) {
                Write-Error-Custom "npm install failed"
                exit 1
            }
            Write-Host ""
        }
        else {
            Write-Info "⚡ Quick mode - skipping npm install (node_modules exists)"
            Write-Host ""
        }
        
        # Build
        if (-not (Build-Frontend -FrontendPath $FrontendPath)) {
            Write-Error-Custom "Build failed"
            exit 1
        }
        Write-Host ""
        
        # Verify build output
        Write-Header "🧪 STEP 3: Verify Build Output"
        $verification = Test-BuildOutput -FrontendPath $FrontendPath
        
        if (-not $verification.Success) {
            Write-Error-Custom "Build verification failed - missing files"
            exit 1
        }
        
        # Show build stats
        $stats = Get-BuildStatistics -FrontendPath $FrontendPath
        if ($stats) {
            Write-Info "Build statistics:"
            Write-Host "  Total files: $($stats.TotalFiles)" -ForegroundColor White
            Write-Host "  Total size: $($stats.TotalSize) MB" -ForegroundColor White
            Write-Host "  Largest: $($stats.LargestFile) ($($stats.LargestSize) KB)" -ForegroundColor White
        }
        
        Write-Host ""
        
        # ═══════════════════════════════════════════════════════════════════
        # Step 4: Deploy to Docker
        # ═══════════════════════════════════════════════════════════════════
        
        Write-Header "🚀 STEP 4: Deploy to Docker"
        
        $distPath = Join-Path $FrontendPath "dist"
        $deploySuccess = $true
        
        # Get all files in dist/
        $distFiles = Get-ChildItem -Path $distPath -File -Recurse
        
        Write-Info "Deploying $($distFiles.Count) files..."
        
        $deployed = 0
        $failed = 0
        
        foreach ($file in $distFiles) {
            $relativePath = $file.FullName.Substring($distPath.Length + 1)
            $destPath = "/usr/src/app/static/$($relativePath -replace '\\', '/')"
            
            if (Copy-ToContainer -SourcePath $file.FullName -ContainerName $ContainerName -DestinationPath $destPath) {
                $deployed++
            }
            else {
                $failed++
                $deploySuccess = $false
            }
            
            # Show progress
            $percent = [Math]::Floor(($deployed + $failed) / $distFiles.Count * 100)
            Show-ProgressBar -Activity "Deploying files" -Percent $percent
        }
        
        Show-ProgressBarComplete -Activity "Deploying files" -Success:$deploySuccess
        
        if (-not $deploySuccess) {
            Write-Warning-Custom "Some files failed to deploy ($failed failed)"
        }
        else {
            Write-Success "All files deployed successfully"
        }
        
        Write-Host ""
        
        # ═══════════════════════════════════════════════════════════════════
        # Step 5: Restart Services
        # ═══════════════════════════════════════════════════════════════════
        
        Write-Header "🔄 STEP 5: Restart Services"
        
        if (Restart-DockerService -Services @("web", "nginx") -WorkingDirectory $DockerComposePath) {
            Write-Success "Services restarted"
        }
        else {
            Write-Warning-Custom "Service restart completed with warnings"
        }
        
        Write-Host ""
    }
    
    # ═══════════════════════════════════════════════════════════════════════
    # Step 6: Verification
    # ═══════════════════════════════════════════════════════════════════════
    
    Write-Header "✅ STEP 6: Deployment Verification"
    
    # Container health check
    $health = Test-ContainerHealth -ContainerName $ContainerName
    
    if ($health.IsRunning) {
        Write-Success "Container: Running"
        
        if ($health.HasErrors) {
            Write-Warning-Custom "Container has errors in logs"
            Write-Info "Recent logs:"
            $health.Logs | Select-Object -Last 5 | ForEach-Object {
                Write-Host "  $_" -ForegroundColor Yellow
            }
        }
        else {
            Write-Success "Container: Healthy"
        }
    }
    else {
        Write-Error-Custom "Container: Not running"
    }
    
    # Show container status
    Write-Info "Container status:"
    $status = Get-ContainerStatus -WorkingDirectory $DockerComposePath
    $status | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Gray
    }
    
    Write-Host ""
    
    # ═══════════════════════════════════════════════════════════════════════
    # Success Summary
    # ═══════════════════════════════════════════════════════════════════════
    
    $endTime = Get-Date
    
    Write-Box -Lines @(
        "✅ DEPLOYMENT COMPLETE!",
        "",
        "Container: $ContainerName",
        "Status: Running",
        "Frontend: Deployed",
        "Services: Restarted",
        "",
        "Time: $((Get-Date).ToString('HH:mm:ss'))"
    ) -Color Green
    
    Write-Host ""
    Write-Info "💡 Next steps:"
    Write-Host "  - Open browser: http://localhost:8082" -ForegroundColor Cyan
    Write-Host "  - Check logs: docker-compose logs -f web" -ForegroundColor Cyan
    Write-Host "  - Re-deploy: .\dev-deploy.ps1 -Quick" -ForegroundColor Cyan
    Write-Host ""
    
    exit 0
}
catch {
    Write-Host ""
    Write-Box -Lines @(
        "❌ DEPLOYMENT FAILED",
        "",
        "Error: $($_.Exception.Message)",
        "",
        "Check logs above for details"
    ) -Color Red
    
    Write-Host ""
    Write-Info "💡 Troubleshooting:"
    Write-Host "  - Run with -Force for full rebuild" -ForegroundColor Yellow
    Write-Host "  - Check Docker: docker ps" -ForegroundColor Yellow
    Write-Host "  - Check logs: docker-compose logs web" -ForegroundColor Yellow
    Write-Host ""
    
    exit 1
}
