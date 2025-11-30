# ========================================
# 🚀 Smart Deploy V2 - מערכת מודולרית חכמה
# ========================================
# קורא את הקובץ הזה להסבר: SMART_DEPLOY_GUIDE.md
# ========================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment,
    
    [switch]$Build,
    [switch]$Up,
    [switch]$Down,
    [switch]$Resume,    # המשך מכשלון
    [switch]$ShowState, # הצג מצב
    [switch]$Reset      # איפוס
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset"
$EnvPath = Join-Path $ProjectRoot "ENVIRONMENTS\$Environment"

# טעינת מודולים
$libs = @(
    "progress-bar.ps1",
    "state-manager.ps1",
    "check-docker.ps1",
    "check-source.ps1",
    "check-environment.ps1",
    "build-image.ps1"
)

foreach ($lib in $libs) {
    $libPath = Join-Path $PSScriptRoot "lib\$lib"
    if (Test-Path $libPath) {
        . $libPath
    } else {
        Write-Warning "⚠️  Missing: $lib"
    }
}

# ========================================
# פונקציות עזר
# ========================================

function Write-StepHeader {
    param([string]$Title, [int]$Step, [int]$Total)
    Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  שלב $Step/$Total : $Title" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

function Invoke-Step {
    param(
        [int]$StepIndex,
        [string]$StepName,
        [scriptblock]$Action,
        [datetime]$StartTime,
        [int]$TotalSteps
    )
    
    Write-StepHeader -Title $StepName -Step ($StepIndex + 1) -Total $TotalSteps
    Update-StepState -StepIndex $StepIndex -Status "running"
    
    Show-ProgressWithTimer -Current $StepIndex -Total $TotalSteps `
        -Status "מריץ: $StepName" -StartTime $StartTime -Color "Yellow"
    
    try {
        $result = & $Action
        Update-StepState -StepIndex $StepIndex -Status "completed"
        
        Clear-Progress
        Show-ProgressWithTimer -Current ($StepIndex + 1) -Total $TotalSteps `
            -Status "✅ $StepName" -StartTime $StartTime -Color "Green"
        
        Start-Sleep -Milliseconds 300
        return @{ success = $true; result = $result }
        
    } catch {
        Update-StepState -StepIndex $StepIndex -Status "failed" -ErrorMessage $_.Exception.Message
        
        Clear-Progress
        Show-ProgressWithTimer -Current $StepIndex -Total $TotalSteps `
            -Status "❌ $StepName" -StartTime $StartTime -Color "Red"
        
        Write-Host "`n💥 $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "💡 הרץ עם -Resume להמשיך" -ForegroundColor Yellow
        
        return @{ success = $false; error = $_.Exception.Message }
    }
}

# ========================================
# טיפול בפרמטרים
# ========================================

if ($ShowState) {
    Show-DeploymentState
    exit 0
}

if ($Reset) {
    Reset-DeploymentState
    exit 0
}

# הגדרת שלבים
$steps = @()

if ($Down) { $steps += "עצירת containers" }

if ($Build) {
    $steps += @(
        "בדיקת Docker",
        "בדיקת SOURCE",
        "בדיקת סביבה",
        "בניית image"
    )
}

if ($Up) {
    $steps += @(
        "הפעלת containers",
        "אימות"
    )
}

if ($steps.Count -eq 0) {
    Write-Host "❌ חובה: -Build או -Up או -Down" -ForegroundColor Red
    exit 1
}

# אתחול/המשך
$state = Get-DeploymentState

if ($Resume -and $state) {
    Write-Host "🔄 ממשיך..." -ForegroundColor Cyan
    Show-DeploymentState
    $startStep = Get-NextPendingStep
    if ($startStep -eq -1) {
        Write-Host "✅ הכל הושלם!" -ForegroundColor Green
        exit 0
    }
} else {
    Reset-DeploymentState
    $state = Initialize-DeploymentState -Environment $Environment -Steps $steps
    $startStep = 0
}

$startTime = Get-Date
$totalSteps = $steps.Count

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║         🚀 Smart Deploy V2 - $Environment                         ║
║         📊 $totalSteps שלבים | ⏱️  $(Get-Date -Format "HH:mm:ss")                    ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ביצוע
for ($i = $startStep; $i -lt $totalSteps; $i++) {
    $stepName = $steps[$i]
    
    $result = Invoke-Step -StepIndex $i -StepName $stepName -StartTime $startTime -TotalSteps $totalSteps -Action {
        switch ($stepName) {
            "בדיקת Docker" { Assert-DockerReady }
            "בדיקת SOURCE" { Assert-SourceReady -ProjectRoot $ProjectRoot }
            "בדיקת סביבה" { Assert-EnvironmentReady -ProjectRoot $ProjectRoot -Environment $Environment }
            "בניית image" {
                $r = Build-DockerImageSmart -Environment $Environment -EnvPath $EnvPath
                if (-not $r.success) { throw $r.error }
            }
            "הפעלת containers" {
                Push-Location $EnvPath
                $out = docker-compose up -d 2>&1
                Pop-Location
                if ($LASTEXITCODE -ne 0) { throw "up נכשל" }
            }
            "אימות" {
                Start-Sleep -Seconds 5
                Push-Location $EnvPath
                $ps = docker-compose ps
                Pop-Location
                Write-Host $ps
            }
            "עצירת containers" {
                Push-Location $EnvPath
                docker-compose down 2>&1 | Out-Null
                Pop-Location
            }
        }
    }
    
    if (-not $result.success) {
        Write-Host "`n❌ נכשל בשלב $($i+1): $stepName" -ForegroundColor Red
        Write-Host "💡 הרץ: .\smart-deploy-v2.ps1 -Environment $Environment -Resume" -ForegroundColor Yellow
        Complete-DeploymentState -Success $false
        exit 1
    }
}

# סיכום
Complete-DeploymentState -Success $true
$elapsed = (Get-Date) - $startTime

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║              ✅ הושלם! ⏱️  $([math]::Round($elapsed.TotalSeconds,1))s                ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

if ($Up) {
    $port = @{ dev=8000; test=8001; prod=8082 }[$Environment]
    Write-Host "🌐 http://localhost:$port" -ForegroundColor Cyan
}
