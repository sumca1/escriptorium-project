<#
.SYNOPSIS
    סקריפט חכם להפעלת שרת הטרמינל עם זיהוי פורט זמין אוטומטי

.DESCRIPTION
    הסקריפט:
    1. בודק זמינות פורטים (3000-3010)
    2. מעלה את השרת על הפורט הראשון הזמין
    3. מעדכן את הדשבורד עם הפורט הנכון
    4. מפעיל את הדשבורד בדפדפן
    5. עוקב אחרי לוגי השרת

.PARAMETER Port
    פורט התחלתי (ברירת מחדל: 3000)

.PARAMETER MaxRetries
    מספר פורטים מקסימלי לנסות (ברירת מחדל: 10)

.PARAMETER NoBrowser
    לא לפתוח דפדפן אוטומטית

.EXAMPLE
    .\start-terminal-server.ps1
    מפעיל את השרת עם הגדרות ברירת מחדל

.EXAMPLE
    .\start-terminal-server.ps1 -Port 3005 -NoBrowser
    מפעיל מפורט 3005 בלי לפתוח דפדפן
#>

[CmdletBinding()]
param(
    [int]$Port = 3000,
    [int]$MaxRetries = 10,
    [switch]$NoBrowser
)

# ===============================
# פונקציות עזר
# ===============================

function Test-PortAvailable {
    param([int]$PortNumber)
    
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $PortNumber)
        $listener.Start()
        $listener.Stop()
        return $true
    }
    catch {
        return $false
    }
}

function Find-AvailablePort {
    param(
        [int]$StartPort,
        [int]$MaxAttempts
    )
    
    Write-Host "`n🔍 מחפש פורט זמין..." -ForegroundColor Cyan
    
    for ($i = 0; $i -lt $MaxAttempts; $i++) {
        $testPort = $StartPort + $i
        Write-Host "   בודק פורט $testPort... " -NoNewline
        
        if (Test-PortAvailable -PortNumber $testPort) {
            Write-Host "✅ זמין!" -ForegroundColor Green
            return $testPort
        }
        else {
            Write-Host "❌ תפוס" -ForegroundColor Red
        }
    }
    
    return $null
}

function Update-DashboardPort {
    param([int]$PortNumber)
    
    $dashboardPath = Join-Path $PSScriptRoot ".." "PROJECT_CONTROL_CENTER_V2.html"
    
    if (-not (Test-Path $dashboardPath)) {
        Write-Warning "⚠️ לא נמצא קובץ הדשבורד: $dashboardPath"
        return $false
    }
    
    Write-Host "`n📝 מעדכן את הדשבורד לפורט $PortNumber..." -ForegroundColor Cyan
    
    try {
        $content = Get-Content $dashboardPath -Raw -Encoding UTF8
        
        # עדכון כל המופעים של localhost:3000 לפורט החדש
        $pattern = 'http://localhost:\d+'
        $replacement = "http://localhost:$PortNumber"
        $newContent = $content -replace $pattern, $replacement
        
        Set-Content -Path $dashboardPath -Value $newContent -Encoding UTF8 -NoNewline
        
        Write-Host "   ✅ הדשבורד עודכן בהצלחה!" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "❌ שגיאה בעדכון הדשבורד: $_"
        return $false
    }
}

function Start-TerminalServerProcess {
    param(
        [int]$PortNumber,
        [string]$ServerScript
    )
    
    Write-Host "`n🚀 מפעיל את שרת הטרמינל..." -ForegroundColor Cyan
    Write-Host "   📂 תיקייה: $PSScriptRoot\.." -ForegroundColor Gray
    Write-Host "   📜 סקריפט: $ServerScript" -ForegroundColor Gray
    Write-Host "   🔌 פורט: $PortNumber" -ForegroundColor Gray
    
    # יצירת environment variable לפורט
    $env:TERMINAL_SERVER_PORT = $PortNumber
    
    # הפעלת השרת כ-background job
    $serverPath = Join-Path $PSScriptRoot ".." $ServerScript
    $workingDir = Join-Path $PSScriptRoot ".."
    
    $job = Start-Job -ScriptBlock {
        param($ServerPath, $WorkingDir, $Port)
        
        Set-Location $WorkingDir
        $env:TERMINAL_SERVER_PORT = $Port
        
        node $ServerPath
    } -ArgumentList $serverPath, $workingDir, $PortNumber
    
    # המתנה קצרה להפעלת השרת
    Start-Sleep -Seconds 2
    
    # בדיקה שהשרת רץ
    $jobState = Get-Job -Id $job.Id | Select-Object -ExpandProperty State
    
    if ($jobState -eq "Running") {
        Write-Host "`n✅ השרת עלה בהצלחה!" -ForegroundColor Green
        Write-Host "   🌐 כתובת: http://localhost:$PortNumber" -ForegroundColor Cyan
        Write-Host "   🆔 Job ID: $($job.Id)" -ForegroundColor Gray
        return $job
    }
    else {
        Write-Error "❌ השרת נכשל בהפעלה"
        Receive-Job -Job $job
        Remove-Job -Job $job -Force
        return $null
    }
}

function Test-ServerHealth {
    param([int]$PortNumber)
    
    Write-Host "`n🏥 בודק תקינות השרת..." -ForegroundColor Cyan
    
    $maxAttempts = 5
    $attemptDelay = 1
    
    for ($i = 1; $i -le $maxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$PortNumber/status" -TimeoutSec 3 -UseBasicParsing
            
            if ($response.StatusCode -eq 200) {
                Write-Host "   ✅ השרת מגיב תקין!" -ForegroundColor Green
                
                # הצגת מידע מהשרת
                $status = $response.Content | ConvertFrom-Json
                Write-Host "`n📊 סטטוס השרת:" -ForegroundColor Cyan
                Write-Host "   ⏱️  זמן פעילות: $($status.uptime)" -ForegroundColor Gray
                Write-Host "   💾 זיכרון: $([math]::Round($status.memory.heapUsed / 1MB, 2)) MB" -ForegroundColor Gray
                Write-Host "   🖥️  פלטפורמה: $($status.platform)" -ForegroundColor Gray
                
                return $true
            }
        }
        catch {
            Write-Host "   ⏳ ניסיון $i/$maxAttempts - ממתין..." -ForegroundColor Yellow
            Start-Sleep -Seconds $attemptDelay
        }
    }
    
    Write-Warning "⚠️ השרת לא מגיב לבדיקות תקינות"
    return $false
}

function Open-Dashboard {
    param(
        [int]$PortNumber,
        [string]$DashboardPath
    )
    
    if (-not (Test-Path $DashboardPath)) {
        Write-Warning "⚠️ לא נמצא קובץ הדשבורד"
        return
    }
    
    Write-Host "`n🌐 פותח את הדשבורד בדפדפן..." -ForegroundColor Cyan
    Write-Host "   📄 קובץ: $DashboardPath" -ForegroundColor Gray
    Write-Host "   🔗 שרת: http://localhost:$PortNumber" -ForegroundColor Gray
    
    Start-Process $DashboardPath
    
    Write-Host "   ✅ הדשבורד נפתח!" -ForegroundColor Green
}

function Show-ServerInstructions {
    param(
        [int]$JobId,
        [int]$PortNumber
    )
    
    Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║        🎉 שרת הטרמינל פעיל ומוכן לשימוש!                ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    Write-Host "`n📋 מידע חשוב:" -ForegroundColor Yellow
    Write-Host "   • השרת רץ כ-Background Job (ID: $JobId)" -ForegroundColor White
    Write-Host "   • הדשבורד מחובר לפורט: $PortNumber" -ForegroundColor White
    Write-Host "   • לחץ על כרטיסיית 'טרמינל' בדשבורד כדי להשתמש" -ForegroundColor White
    
    Write-Host "`n🔧 פקודות ניהול:" -ForegroundColor Yellow
    Write-Host "   • צפייה בלוגים:    " -NoNewline -ForegroundColor White
    Write-Host "Receive-Job -Id $JobId -Keep" -ForegroundColor Cyan
    Write-Host "   • עצירת השרת:      " -NoNewline -ForegroundColor White
    Write-Host "Stop-Job -Id $JobId; Remove-Job -Id $JobId" -ForegroundColor Cyan
    Write-Host "   • בדיקת סטטוס:     " -NoNewline -ForegroundColor White
    Write-Host "Invoke-WebRequest http://localhost:$PortNumber/status" -ForegroundColor Cyan
    Write-Host "   • הפעלה מחדש:      " -NoNewline -ForegroundColor White
    Write-Host ".\SCRIPTS\start-terminal-server.ps1" -ForegroundColor Cyan
    
    Write-Host "`n💡 טיפים:" -ForegroundColor Yellow
    Write-Host "   • כדי לראות את הפלט בזמן אמת, השתמש ב: Get-Job -Id $JobId | Receive-Job -Wait" -ForegroundColor Gray
    Write-Host "   • אם השרת לא מגיב, נסה לפתוח את PROJECT_CONTROL_CENTER_V2.html מחדש" -ForegroundColor Gray
    Write-Host "   • כל הפקודות בטרמינל הדשבורד מתבצעות בתיקייה: $(Join-Path $PSScriptRoot '..')" -ForegroundColor Gray
    
    Write-Host "`n🎯 נקודות מעבר בדשבורד:" -ForegroundColor Yellow
    Write-Host "   1️⃣  לחץ על כרטיסיה: 💻 טרמינל" -ForegroundColor White
    Write-Host "   2️⃣  נסה כפתור מהיר: ✅ בדיקת דרישות" -ForegroundColor White
    Write-Host "   3️⃣  או כתוב פקודה: .\SCRIPTS\deploy-dev.ps1" -ForegroundColor White
    Write-Host "   4️⃣  לחץ Enter או על כפתור 'הרץ'" -ForegroundColor White
    
    Write-Host "`n" -NoNewline
}

# ===============================
# תהליך ראשי
# ===============================

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║     🚀 הפעלת שרת טרמינל חכם - Smart Terminal Server     ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta

# שלב 1: מציאת פורט זמין
$availablePort = Find-AvailablePort -StartPort $Port -MaxAttempts $MaxRetries

if ($null -eq $availablePort) {
    Write-Error "❌ לא נמצא פורט זמין בטווח $Port-$($Port + $MaxRetries - 1)"
    Write-Host "`n💡 נסה:" -ForegroundColor Yellow
    Write-Host "   • סגור תהליכים שתופסים פורטים: Get-Process -Name node | Stop-Process" -ForegroundColor Gray
    Write-Host "   • נסה טווח פורטים אחר: .\start-terminal-server.ps1 -Port 4000" -ForegroundColor Gray
    exit 1
}

Write-Host "`n✅ פורט זמין נמצא: $availablePort" -ForegroundColor Green

# שלב 2: עדכון הדשבורד
$dashboardUpdated = Update-DashboardPort -PortNumber $availablePort

if (-not $dashboardUpdated) {
    Write-Warning "⚠️ המשך בלי עדכון דשבורד (עדכן ידנית אם נדרש)"
}

# שלב 3: הפעלת השרת
$serverJob = Start-TerminalServerProcess -PortNumber $availablePort -ServerScript "terminal-server.js"

if ($null -eq $serverJob) {
    Write-Error "❌ כשלון בהפעלת השרת"
    exit 1
}

# שלב 4: בדיקת תקינות
$isHealthy = Test-ServerHealth -PortNumber $availablePort

if (-not $isHealthy) {
    Write-Warning "⚠️ השרת עלה אך לא מגיב לבדיקות - המשך בזהירות"
}

# שלב 5: פתיחת הדשבורד
if (-not $NoBrowser) {
    $dashboardPath = Join-Path $PSScriptRoot ".." "PROJECT_CONTROL_CENTER_V2.html"
    Open-Dashboard -PortNumber $availablePort -DashboardPath $dashboardPath
}

# שלב 6: הצגת הוראות
Show-ServerInstructions -JobId $serverJob.Id -PortNumber $availablePort

# שמירת מידע למעקב
$trackingInfo = @{
    JobId = $serverJob.Id
    Port = $availablePort
    StartTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    DashboardPath = Join-Path $PSScriptRoot ".." "PROJECT_CONTROL_CENTER_V2.html"
} | ConvertTo-Json

$trackingPath = Join-Path $PSScriptRoot ".." ".terminal-server-info.json"
Set-Content -Path $trackingPath -Value $trackingInfo -Encoding UTF8

Write-Host "💾 מידע נשמר ב: .terminal-server-info.json" -ForegroundColor Gray
Write-Host "`n✨ בהצלחה! השרת מוכן לשימוש." -ForegroundColor Green
Write-Host ""
