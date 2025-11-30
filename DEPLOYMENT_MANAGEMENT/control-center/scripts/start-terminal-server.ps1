<#
.SYNOPSIS
    מפעיל את Terminal Server ברקע
    
.DESCRIPTION
    מריץ את שרת הטרמינל כ-background job ב-PowerShell
    כך שלא חוסם את הטרמינל הנוכחי
    
.PARAMETER Port
    פורט להאזנה (ברירת מחדל: 3000)
    
.EXAMPLE
    .\start-terminal-server.ps1
    .\start-terminal-server.ps1 -Port 3005
#>

param(
    [int]$Port = 3000,
    [switch]$Foreground
)

$ScriptRoot = Split-Path -Parent $PSCommandPath
$ControlCenterRoot = Split-Path -Parent $ScriptRoot
$ServersDir = Join-Path $ControlCenterRoot "servers"
$ServerPath = Join-Path $ServersDir "terminal-server.js"

# בדוק אם Node.js מותקן
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js לא מותקן! התקן מ-https://nodejs.org" -ForegroundColor Red
    exit 1
}

# בדוק אם השרת כבר רץ
$existingProcess = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($existingProcess) {
    Write-Host "⚠️  פורט $Port כבר בשימוש!" -ForegroundColor Yellow
    $processId = $existingProcess.OwningProcess
    $process = Get-Process -Id $processId
    Write-Host "   תהליך: $($process.Name) (PID: $processId)" -ForegroundColor Yellow
    
    $response = Read-Host "האם לעצור את התהליך הקיים? (y/n)"
    if ($response -eq 'y') {
        Stop-Process -Id $processId -Force
        Write-Host "✅ התהליך נעצר" -ForegroundColor Green
        Start-Sleep 2
    } else {
        Write-Host "❌ ביטול - בחר פורט אחר" -ForegroundColor Red
        exit 1
    }
}

# בדוק אם node_modules קיימים
$nodeModulesPath = Join-Path $ServersDir "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "📦 מתקין dependencies..." -ForegroundColor Cyan
    Push-Location $ServersDir
    npm install
    Pop-Location
}

Write-Host "`n🚀 מפעיל Terminal Server..." -ForegroundColor Cyan
Write-Host "   פורט: $Port" -ForegroundColor White
Write-Host "   נתיב: $ServerPath" -ForegroundColor White

if ($Foreground) {
    # הרצה רגילה (foreground)
    Write-Host "`n💡 רץ ב-foreground - לחץ Ctrl+C לעצירה`n" -ForegroundColor Yellow
    Push-Location $ServersDir
    node terminal-server.js $Port
    Pop-Location
} else {
    # הרצה ברקע (background job)
    $job = Start-Job -ScriptBlock {
        param($ServerPath, $Port, $ServersDir)
        Set-Location $ServersDir
        node $ServerPath $Port
    } -ArgumentList $ServerPath, $Port, $ServersDir
    
    Write-Host "✅ השרת רץ ברקע!" -ForegroundColor Green
    Write-Host "   Job ID: $($job.Id)" -ForegroundColor White
    Write-Host "   URL: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "`n📊 לבדיקת סטטוס:" -ForegroundColor Yellow
    Write-Host "   Get-Job -Id $($job.Id)" -ForegroundColor White
    Write-Host "   Receive-Job -Id $($job.Id) -Keep" -ForegroundColor White
    Write-Host "`n⏹️  לעצירה:" -ForegroundColor Yellow
    Write-Host "   Stop-Job -Id $($job.Id); Remove-Job -Id $($job.Id)" -ForegroundColor White
    
    # המתן שהשרת יעלה
    Write-Host "`n⏳ ממתין שהשרת יעלה..." -ForegroundColor Cyan
    $maxAttempts = 10
    $attempt = 0
    $serverUp = $false
    
    while ($attempt -lt $maxAttempts -and -not $serverUp) {
        Start-Sleep 1
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$Port/status" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                $serverUp = $true
                Write-Host "✅ השרת פעיל ומגיב!" -ForegroundColor Green
            }
        } catch {
            $attempt++
        }
    }
    
    if (-not $serverUp) {
        Write-Host "⚠️  השרת לא מגיב. בדוק את הלוגים:" -ForegroundColor Yellow
        Write-Host "   Receive-Job -Id $($job.Id)" -ForegroundColor White
    } else {
        # הצג מידע על השרת
        try {
            $info = Invoke-RestMethod -Uri "http://localhost:$Port/" -Method Get
            Write-Host "`n📋 מידע על השרת:" -ForegroundColor Cyan
            Write-Host "   גרסה: $($info.version)" -ForegroundColor White
            Write-Host "   PowerShell 7: $(if ($info.powershell.pwsh7) { '✅' } else { '❌' })" -ForegroundColor White
            Write-Host "   PowerShell 5.1: $(if ($info.powershell.powershell) { '✅' } else { '❌' })" -ForegroundColor White
        } catch {
            # No problem if this fails
        }
    }
    
    Write-Host "`n🎯 השרת מוכן לשימוש!" -ForegroundColor Green
    
    # שמור את ה-Job ID לקובץ
    $jobInfoFile = Join-Path $ControlCenterRoot "data\terminal-server-info.json"
    $jobInfo = @{
        JobId = $job.Id
        Port = $Port
        StartTime = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        Pid = $null
    }
    $jobInfo | ConvertTo-Json | Set-Content $jobInfoFile
    Write-Host "💾 מידע נשמר ב: $jobInfoFile" -ForegroundColor Gray
}
