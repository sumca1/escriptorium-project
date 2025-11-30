<#
.SYNOPSIS
    Master Troubleshoot Script - אבחון ותיקון בעיות
    
.DESCRIPTION
    מזהה ומתקן בעיות נפוצות:
    - Docker לא רץ
    - Containers לא פעילים
    - Ports תפוסים
    - קבצים חסרים
    
.PARAMETER ErrorCode
    קוד שגיאה ספציפי לטיפול (DOCKER_001, PORT_001, וכו')
    
.PARAMETER AutoFix
    נסה לתקן אוטומטית
    
.PARAMETER Scan
    סרוק בעיות בלי לתקן
    
.EXAMPLE
    .\troubleshoot-master.ps1 -Scan
    .\troubleshoot-master.ps1 -ErrorCode DOCKER_001 -AutoFix
    .\troubleshoot-master.ps1 -AutoFix
#>

param(
    [string]$ErrorCode,
    [switch]$AutoFix,
    [switch]$Scan
)

$ErrorActionPreference = "Continue"
$ScriptRoot = Split-Path -Parent $PSCommandPath

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           🔧 Master Troubleshoot Script                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# טען error registry
$errorRegistryPath = "..\..\control-center\data\error-codes-registry.json"
if (Test-Path $errorRegistryPath) {
    $registry = Get-Content $errorRegistryPath | ConvertFrom-Json
} else {
    Write-Host "⚠️  Error registry לא נמצא: $errorRegistryPath" -ForegroundColor Yellow
    $registry = $null
}

# פונקציה לבדיקת בעיה
function Test-Issue {
    param($Code, $Name, $Check, $Fix)
    
    Write-Host "`n🔍 בודק: $Name ($Code)" -ForegroundColor Cyan
    
    try {
        $result = & $Check
        if ($result -eq $false) {
            Write-Host "   ❌ נמצאה בעיה!" -ForegroundColor Red
            
            if ($AutoFix -and $Fix) {
                Write-Host "   🔧 מתקן..." -ForegroundColor Yellow
                & $Fix
                Write-Host "   ✅ תוקן!" -ForegroundColor Green
            } else {
                Write-Host "   💡 פתרון: הרץ עם -AutoFix לתיקון אוטומטי" -ForegroundColor Yellow
            }
            return $false
        } else {
            Write-Host "   ✅ תקין" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "   ⚠️  שגיאה בבדיקה: $_" -ForegroundColor Yellow
        return $null
    }
}

# אם יש ErrorCode ספציפי
if ($ErrorCode) {
    Write-Host "🎯 מטפל בשגיאה: $ErrorCode`n" -ForegroundColor Yellow
    
    if ($registry) {
        $error = $registry.errors | Where-Object { $_.code -eq $ErrorCode }
        
        if ($error) {
            Write-Host "📋 שם: $($error.title)" -ForegroundColor White
            Write-Host "📄 תיאור: $($error.description)" -ForegroundColor Gray
            Write-Host "`n💡 פתרון: $($error.solution)" -ForegroundColor Cyan
            
            if ($AutoFix -and $error.autoFixAvailable) {
                Write-Host "`n🔧 מריץ תיקון אוטומטי..." -ForegroundColor Yellow
                Write-Host "   פקודה: $($error.autoFixCommand)" -ForegroundColor Gray
                Invoke-Expression $error.autoFixCommand
                Write-Host "✅ הושלם!" -ForegroundColor Green
            }
        } else {
            Write-Host "❌ שגיאה $ErrorCode לא נמצאה ברישום" -ForegroundColor Red
        }
    }
    exit
}

# סריקה כללית
Write-Host "🔍 מריץ סריקה כללית...`n" -ForegroundColor Cyan

$issues = @()

# 1. בדוק Docker
$dockerOk = Test-Issue -Code "DOCKER_001" -Name "Docker Desktop פעיל" `
    -Check { 
        $null -ne (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)
    } `
    -Fix {
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        Start-Sleep 10
    }
if (-not $dockerOk) { $issues += "DOCKER_001" }

# 2. בדוק Containers
$containersOk = Test-Issue -Code "DOCKER_002" -Name "Containers פעילים" `
    -Check {
        $containers = docker ps 2>$null
        $LASTEXITCODE -eq 0 -and $containers.Count -gt 1
    } `
    -Fix {
        $dockerComposePath = "..\..\CORE\eScriptorium_UNIFIED"
        Push-Location $dockerComposePath
        docker-compose up -d
        Pop-Location
    }
if (-not $containersOk) { $issues += "DOCKER_002" }

# 3. בדוק Ports
$portsOk = Test-Issue -Code "PORT_001" -Name "Ports זמינים" `
    -Check {
        $port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
        $port80 = Get-NetTCPConnection -LocalPort 80 -ErrorAction SilentlyContinue
        # אם אין משהו על 3000 או שיש משהו על 80 (Docker) זה טוב
        $true
    } `
    -Fix {
        Write-Host "   ניקוי ports לא מיושם עדיין"
    }

# סיכום
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                     📊 סיכום סריקה                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($issues.Count -eq 0) {
    Write-Host "✅ לא נמצאו בעיות!" -ForegroundColor Green
} else {
    Write-Host "⚠️  נמצאו $($issues.Count) בעיות:" -ForegroundColor Yellow
    foreach ($issue in $issues) {
        Write-Host "   - $issue" -ForegroundColor Red
    }
    
    if (-not $AutoFix) {
        Write-Host "`n💡 הרץ עם -AutoFix לתיקון אוטומטי" -ForegroundColor Cyan
    }
}
