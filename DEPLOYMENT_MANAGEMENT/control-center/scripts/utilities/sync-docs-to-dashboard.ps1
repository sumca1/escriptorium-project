# ========================================
# סנכרון מסמכי תיעוד לדשבורד
# Sync Documentation Files to Dashboard
# ========================================

param(
    [switch]$Watch,      # מצב מעקב רציף (watch mode)
    [switch]$Force,      # כפה העתקה גם אם אין שינויים
    [switch]$Verbose     # מידע מפורט
)

$ErrorActionPreference = "Stop"

# ========================================
# הגדרות נתיבים
# ========================================

$ProjectRoot = Split-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent) -Parent
$ProjectRoot = Split-Path $ProjectRoot -Parent  # עוד רמה למעלה ל-BiblIA_dataset

$ControlCenterDocs = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) "docs"

# קבצים לסנכרון
$FilesToSync = @(
    @{
        Name = "SESSION_LOG.md"
        Source = Join-Path $ProjectRoot "SESSION_LOG.md"
        Target = Join-Path $ControlCenterDocs "SESSION_LOG.md"
    },
    @{
        Name = "CURRENT_STATE.md"
        Source = Join-Path $ProjectRoot "CURRENT_STATE.md"
        Target = Join-Path $ControlCenterDocs "CURRENT_STATE.md"
    }
)

# ========================================
# פונקציות עזר
# ========================================

function Write-ColorHost {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Green" = "Green"
        "Yellow" = "Yellow"
        "Red" = "Red"
        "Cyan" = "Cyan"
        "Blue" = "Blue"
        "Magenta" = "Magenta"
        "Gray" = "Gray"
        "White" = "White"
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

function Get-FileHashQuick {
    param([string]$Path)
    
    if (!(Test-Path $Path)) {
        return $null
    }
    
    # hash מהיר - גודל + תאריך שינוי
    $file = Get-Item $Path
    return "$($file.Length)-$($file.LastWriteTime.Ticks)"
}

function Sync-SingleFile {
    param(
        [hashtable]$FileInfo,
        [bool]$ForceSync = $false
    )
    
    $name = $FileInfo.Name
    $source = $FileInfo.Source
    $target = $FileInfo.Target
    
    # בדיקת קיום מקור
    if (!(Test-Path $source)) {
        Write-ColorHost "  ⚠️  $name - קובץ מקור לא קיים!" "Yellow"
        return $false
    }
    
    # יצירת תיקיית יעד אם לא קיימת
    $targetDir = Split-Path $target -Parent
    if (!(Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }
    
    # בדיקת צורך בסנכרון
    $needsSync = $ForceSync
    
    if (!$needsSync) {
        if (!(Test-Path $target)) {
            $needsSync = $true
        } else {
            $sourceHash = Get-FileHashQuick $source
            $targetHash = Get-FileHashQuick $target
            $needsSync = ($sourceHash -ne $targetHash)
        }
    }
    
    if ($needsSync) {
        try {
            Copy-Item $source $target -Force
            $size = [math]::Round((Get-Item $source).Length / 1KB, 2)
            Write-ColorHost "  ✅ $name סונכרן ($size KB)" "Green"
            return $true
        } catch {
            Write-ColorHost "  ❌ שגיאה בסנכרון $name : $_" "Red"
            return $false
        }
    } else {
        if ($Verbose) {
            Write-ColorHost "  ⏭️  $name - ללא שינויים" "Gray"
        }
        return $false
    }
}

# ========================================
# פונקציה ראשית - סנכרון חד פעמי
# ========================================

function Invoke-SyncOnce {
    Write-ColorHost "`n📚 מסנכרן מסמכי תיעוד לדשבורד..." "Cyan"
    Write-ColorHost "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "Cyan"
    
    if ($Verbose) {
        Write-ColorHost "`n📂 נתיבים:" "Blue"
        Write-ColorHost "  מקור:  $ProjectRoot" "Gray"
        Write-ColorHost "  יעד:   $ControlCenterDocs" "Gray"
    }
    
    Write-ColorHost "`n🔄 מעבד קבצים..." "Blue"
    
    $syncedCount = 0
    $skippedCount = 0
    $errorCount = 0
    
    foreach ($file in $FilesToSync) {
        $synced = Sync-SingleFile -FileInfo $file -ForceSync $Force
        
        if ($synced) {
            $syncedCount++
        } elseif (Test-Path $file.Source) {
            $skippedCount++
        } else {
            $errorCount++
        }
    }
    
    Write-ColorHost "`n📊 סיכום:" "Blue"
    Write-ColorHost "  ✅ סונכרנו:    $syncedCount" "Green"
    Write-ColorHost "  ⏭️  דולגו:      $skippedCount" "Gray"
    
    if ($errorCount -gt 0) {
        Write-ColorHost "  ❌ שגיאות:     $errorCount" "Red"
    }
    
    Write-ColorHost "`n✨ סיום!" "Cyan"
    
    return $syncedCount
}

# ========================================
# פונקציה - מצב watch (מעקב רציף)
# ========================================

function Invoke-WatchMode {
    Write-ColorHost "`n👁️  מצב מעקב פעיל - עוקב אחר שינויים בקבצים..." "Cyan"
    Write-ColorHost "   (לחץ Ctrl+C לעצירה)" "Yellow"
    Write-ColorHost "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "Cyan"
    
    # שמירת hash files נוכחי
    $lastHashes = @{}
    foreach ($file in $FilesToSync) {
        $lastHashes[$file.Name] = Get-FileHashQuick $file.Source
    }
    
    # סנכרון ראשוני
    Invoke-SyncOnce | Out-Null
    
    Write-ColorHost "`n⏳ ממתין לשינויים..." "Gray"
    
    $iteration = 0
    while ($true) {
        Start-Sleep -Seconds 2
        $iteration++
        
        $changedFiles = @()
        
        foreach ($file in $FilesToSync) {
            $currentHash = Get-FileHashQuick $file.Source
            
            if ($currentHash -ne $lastHashes[$file.Name]) {
                $changedFiles += $file
                $lastHashes[$file.Name] = $currentHash
            }
        }
        
        if ($changedFiles.Count -gt 0) {
            Write-ColorHost "`n🔔 זוהו שינויים ב-$($changedFiles.Count) קבצים!" "Yellow"
            
            foreach ($file in $changedFiles) {
                Sync-SingleFile -FileInfo $file -ForceSync $true | Out-Null
            }
            
            Write-ColorHost "⏳ ממתין לשינויים..." "Gray"
        }
        
        # עדכון מחזורי כל 30 שניות
        if ($iteration % 15 -eq 0) {
            Write-Host "." -NoNewline -ForegroundColor Gray
        }
    }
}

# ========================================
# הרצה ראשית
# ========================================

try {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   סנכרון מסמכים לדשבורד BiblIA      ║" -ForegroundColor Cyan
    Write-Host "║   Dashboard Documentation Sync        ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
    
    if ($Watch) {
        Invoke-WatchMode
    } else {
        $syncCount = Invoke-SyncOnce
        
        if ($syncCount -eq 0) {
            Write-ColorHost "`n💡 טיפ: כדי לעקוב אחר שינויים באופן אוטומטי, הרץ:" "Yellow"
            Write-ColorHost "   .\sync-docs-to-dashboard.ps1 -Watch" "Gray"
        }
    }
    
    exit 0
    
} catch {
    Write-ColorHost "`n❌ שגיאה קריטית: $_" "Red"
    Write-ColorHost "Stack trace: $($_.ScriptStackTrace)" "Gray"
    exit 1
}
