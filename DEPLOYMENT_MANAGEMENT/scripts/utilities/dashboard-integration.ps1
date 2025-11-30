# 🔗 Dashboard Integration Script
# מחבר את smart-deploy-v2.ps1 למרכז הבקרה

param(
    [Parameter(Mandatory=$false)]
    [int]$UpdateIntervalSeconds = 2
)

$ErrorActionPreference = "Stop"

# נתיבים
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$StateFile = Join-Path $ProjectRoot ".deployment_state.json"
$DashboardDataFile = Join-Path $ProjectRoot "dashboard-data.json"

Write-Host "╔═════�?══════�?══════�?══════════�?══�?═════╗" -ForegroundColor DarkGray
Write-Host "�?   🔗 Dashboard Integration           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════�?═══════╝" -ForegroundColor DarkGray
Write-Host ""

# פונקציה: קרא state
function Get-DeploymentState {
    if (Test-Path $StateFile) {
        try {
            $content = Get-Content $StateFile -Raw
            return $content | ConvertFrom-Json
        } catch {
            Write-Warning "Failed to parse state file: $_"
            return $null
        }
    }
    return $null
}

# פונקציה: המר state ל-dashboard data
function ConvertTo-DashboardData {
    param($state)
    
    $data = @{
        timestamp = Get-Date -Format "o"
        deployment = $null
        summary = @{
            status = "idle"
            environment = ""
            currentStep = 0
            totalSteps = 0
            percent = 0
            errors = @()
        }
    }
    
    if ($state) {
        $data.deployment = $state
        
        $percent = if ($state.totalSteps -gt 0) {
            [math]::Round(($state.currentStep / $state.totalSteps) * 100)
        } else { 0 }
        
        $data.summary = @{
            status = $state.status
            environment = $state.environment
            currentStep = $state.currentStep
            totalSteps = $state.totalSteps
            percent = $percent
            errors = $state.errors
            startTime = $state.startTime
            endTime = $state.endTime
        }
    }
    
    return $data
}

# פונקציה: שמור dashboard data
function Export-DashboardData {
    param($data)
    
    try {
        $json = $data | ConvertTo-Json -Depth 10 -Compress
        Set-Content -Path $DashboardDataFile -Value $json -Force
        
        $timestamp = Get-Date -Format "HH:mm:ss"
        Write-Host "[$timestamp] �? Dashboard data מעודכן" -ForegroundColor Green
        
        # הצג סיכום
        if ($data.summary.status -ne "idle") {
            $status = $data.summary.status
            $env = $data.summary.environment
            $percent = $data.summary.percent
            
            $statusIcon = switch ($status) {
                "running" { "🔄" }
                "completed" { "�?" }
                "failed" { "❌" }
                default { "⏳" }
            }
            
            Write-Host "[$timestamp] $statusIcon $env - $percent% ($($data.summary.currentStep)/$($data.summary.totalSteps))" -ForegroundColor Cyan
            
            # אם יש שגיאות
            if ($data.summary.errors.Count -gt 0) {
                Write-Host "[$timestamp] ⚠️  שגיאות: $($data.summary.errors -join ', ')" -ForegroundColor Yellow
            }
        }
        
    } catch {
        Write-Warning "Failed to export dashboard data: $_"
    }
}

# פונקציה: FileSystemWatcher
function Start-StateWatcher {
    Write-Host "🔍 מתחיל FileSystemWatcher על $StateFile..." -ForegroundColor Cyan
    Write-Host "📊 Dashboard data יעודכן ב-$DashboardDataFile" -ForegroundColor Cyan
    Write-Host ""
    
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = $ProjectRoot
    $watcher.Filter = ".deployment_state.json"
    $watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName
    
    # Event handler
    $action = {
        Start-Sleep -Milliseconds 100 # המתן לכתיבה להסתיים
        
        $state = Get-DeploymentState
        $data = ConvertTo-DashboardData -state $state
        Export-DashboardData -data $data
    }
    
    # רשום events
    $handlers = @()
    $handlers += Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action $action
    $handlers += Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action $action
    
    $watcher.EnableRaisingEvents = $true
    
    Write-Host "�? Watcher פעיל - ממתין לשינויים..." -ForegroundColor Green
    Write-Host "⏱️  מעדכן כל $UpdateIntervalSeconds שניות (polling נוסף)" -ForegroundColor Gray
    Write-Host "🛑 לחץ Ctrl+C לעצור" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "════�?═══════════════════════════════════" -ForegroundColor DarkGray
    Write-Host ""
    
    # טעינה ראשונית
    $state = Get-DeploymentState
    $data = ConvertTo-DashboardData -state $state
    Export-DashboardData -data $data
    
    try {
        # Loop ראשי - polling נוסף
        while ($true) {
            Start-Sleep -Seconds $UpdateIntervalSeconds
            
            # פולינג (במקרה ש-FileSystemWatcher החמיץ)
            $state = Get-DeploymentState
            $data = ConvertTo-DashboardData -state $state
            Export-DashboardData -data $data
        }
    } finally {
        # ניקוי
        $watcher.EnableRaisingEvents = $false
        $handlers | ForEach-Object { Unregister-Event -SourceIdentifier $_.Name }
        $watcher.Dispose()
        
        Write-Host ""
        Write-Host "🛑 Watcher נעצר" -ForegroundColor Yellow
    }
}

# הרץ
Start-StateWatcher
