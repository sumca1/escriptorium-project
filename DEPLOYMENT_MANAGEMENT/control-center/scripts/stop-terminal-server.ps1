<#
.SYNOPSIS
    עוצר את Terminal Server
    
.DESCRIPTION
    מוצא ועוצר את שרת הטרמינל (Job או Process)
    
.PARAMETER Port
    פורט של השרת (ברירת מחדל: 3000)
#>

param(
    [int]$Port = 3000
)

$ScriptRoot = Split-Path -Parent $PSCommandPath
$ControlCenterRoot = Split-Path -Parent $ScriptRoot

Write-Host "🔍 מחפש Terminal Server על פורט $Port..." -ForegroundColor Cyan

# בדוק אם יש Job ID שמור
$jobInfoFile = Join-Path $ControlCenterRoot "data\terminal-server-info.json"
if (Test-Path $jobInfoFile) {
    try {
        $jobInfo = Get-Content $jobInfoFile | ConvertFrom-Json
        $job = Get-Job -Id $jobInfo.JobId -ErrorAction SilentlyContinue
        
        if ($job) {
            Write-Host "✅ מצאתי Job: $($job.Id)" -ForegroundColor Green
            Stop-Job -Id $job.Id
            Remove-Job -Id $job.Id -Force
            Write-Host "✅ Job נעצר ונמחק" -ForegroundColor Green
            Remove-Item $jobInfoFile -Force
        }
    } catch {
        Write-Host "⚠️  לא הצלחתי לעצור דרך Job ID" -ForegroundColor Yellow
    }
}

# חפש לפי פורט
try {
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connection) {
        $processId = $connection.OwningProcess
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        
        if ($process) {
            Write-Host "✅ מצאתי תהליך: $($process.Name) (PID: $processId)" -ForegroundColor Green
            Stop-Process -Id $processId -Force
            Write-Host "✅ תהליך נעצר" -ForegroundColor Green
            
            # נקה את קובץ המידע
            if (Test-Path $jobInfoFile) {
                Remove-Item $jobInfoFile -Force
            }
            
            return
        }
    }
} catch {
    Write-Host "⚠️  שגיאה בחיפוש תהליך: $_" -ForegroundColor Yellow
}

# אם לא מצאנו כלום
Write-Host "ℹ️  לא נמצא שרת פעיל על פורט $Port" -ForegroundColor Gray
Write-Host "`n💡 טיפים:" -ForegroundColor Cyan
Write-Host "   - בדוק אם השרת באמת רץ: Get-NetTCPConnection -LocalPort $Port" -ForegroundColor White
Write-Host "   - רשימת כל ה-Jobs: Get-Job" -ForegroundColor White
Write-Host "   - רשימת תהליכי node: Get-Process node" -ForegroundColor White
