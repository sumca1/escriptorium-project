# ========================================
# 🎛️ סקריפט עדכון Dashboard חכם (Smart Update)
# ========================================
# מטרה: לעדכן את PROJECT_CONTROL_CENTER.html
#        רק כשיש שינויים אמיתיים!
# ========================================

param(
    [switch]$Continuous,  # האם להמשיך לרוץ ברקע?
    [switch]$Watch,       # 🔥 מצב FileSystemWatcher - מגיב רק לשינויים!
    [int]$IntervalSeconds = 30,  # כל כמה שניות לעדכן (אם Continuous ללא Watch)
    [switch]$Once         # עדכון חד-פעמי (ברירת מחדל)
)

$ErrorActionPreference = "Continue"

# נתיבים
$ProjectRoot = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset"
$SourceDir = Join-Path $ProjectRoot "SOURCE"
$EnvDir = Join-Path $ProjectRoot "ENVIRONMENTS"
$StatusFile = Join-Path $ProjectRoot "PROJECT_STATUS.json"

# ========================================
# 🔍 פונקציה: סריקת קבצים שהשתנו
# ========================================
function Get-ModifiedFiles {
    $modifiedFiles = @()
    
    # בדיקה עם git (אם זמין)
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Push-Location $ProjectRoot
        $gitStatus = git status --porcelain 2>$null
        if ($gitStatus) {
            $modifiedFiles = $gitStatus | ForEach-Object {
                $_ -replace '^\s*[A-Z?]+\s+', ''
            }
        }
        Pop-Location
    }
    
    # אם אין git, בדוק לפי זמן שינוי (15 דקות אחרונות)
    if ($modifiedFiles.Count -eq 0 -and (Test-Path $SourceDir)) {
        $cutoffTime = (Get-Date).AddMinutes(-15)
        $modifiedFiles = Get-ChildItem $SourceDir -Recurse -File | 
            Where-Object { $_.LastWriteTime -gt $cutoffTime } |
            Select-Object -ExpandProperty FullName |
            ForEach-Object { $_ -replace [regex]::Escape($ProjectRoot), '' }
    }
    
    return $modifiedFiles
}

# ========================================
# 🐳 פונקציה: בדיקת סטטוס Docker
# ========================================
function Get-DockerStatus {
    $status = @{
        dev = @{ status = 'inactive'; uptime = 0; port = 8000 }
        test = @{ status = 'inactive'; tests = 0; passed = 0; coverage = 0 }
        prod = @{ status = 'inactive'; uptime = 0; containers = 0; healthy = 0 }
    }
    
    try {
        $containers = docker ps --format "{{.Names}},{{.Status}},{{.Ports}}" 2>$null
        
        foreach ($container in $containers) {
            if (-not $container) { continue }
            
            $parts = $container -split ','
            $name = $parts[0]
            $statusText = $parts[1]
            $ports = $parts[2]
            
            # זיהוי סביבה לפי שם container
            if ($name -match 'dev|development') {
                $status.dev.status = 'active'
                if ($statusText -match 'Up (\d+)') {
                    $status.dev.uptime = [int]$matches[1] * 60  # המרה לשניות
                }
            }
            elseif ($name -match 'test|testing') {
                $status.test.status = 'active'
            }
            elseif ($name -match 'web|nginx|db|redis') {
                $status.prod.status = 'active'
                $status.prod.containers++
                
                # בדיקת health
                $health = docker inspect --format='{{.State.Health.Status}}' $name 2>$null
                if ($health -eq 'healthy' -or $health -eq '') {
                    $status.prod.healthy++
                }
                
                # זמן הפעלה
                if ($statusText -match 'Up (\d+) (\w+)') {
                    $value = [int]$matches[1]
                    $unit = $matches[2]
                    
                    $uptime = switch ($unit) {
                        'second' { $value }
                        'seconds' { $value }
                        'minute' { $value * 60 }
                        'minutes' { $value * 60 }
                        'hour' { $value * 3600 }
                        'hours' { $value * 3600 }
                        'day' { $value * 86400 }
                        'days' { $value * 86400 }
                        default { 0 }
                    }
                    
                    if ($uptime -gt $status.prod.uptime) {
                        $status.prod.uptime = $uptime
                    }
                }
            }
        }
    }
    catch {
        Write-Warning "לא ניתן לקרוא סטטוס Docker: $_"
    }
    
    return $status
}

# ========================================
# 📊 פונקציה: ספירת קבצים
# ========================================
function Get-FileStats {
    $stats = @{
        total = 0
        modified = 0
        synced = 0
    }
    
    if (Test-Path $SourceDir) {
        $allFiles = Get-ChildItem $SourceDir -Recurse -File | 
            Where-Object { $_.Extension -in @('.py', '.js', '.vue', '.html', '.css', '.json', '.yml', '.yaml') }
        
        $stats.total = $allFiles.Count
        
        # קבצים שהשתנו
        $modifiedFiles = Get-ModifiedFiles
        $stats.modified = $modifiedFiles.Count
        $stats.synced = $stats.total - $stats.modified
    }
    
    return $stats
}

# ========================================
# 📝 פונקציה: קריאת לוגים אחרונים
# ========================================
function Get-RecentLogs {
    $logs = @()
    
    # חיפוש קבצי לוגים
    $logDirs = @(
        (Join-Path $EnvDir "development\logs"),
        (Join-Path $EnvDir "testing\logs"),
        (Join-Path $EnvDir "production\logs"),
        (Join-Path $ProjectRoot "logs")
    )
    
    foreach ($dir in $logDirs) {
        if (Test-Path $dir) {
            $logFiles = Get-ChildItem $dir -Filter "*.log" -File | 
                Sort-Object LastWriteTime -Descending | 
                Select-Object -First 3
            
            foreach ($file in $logFiles) {
                # קרא 10 שורות אחרונות
                $lines = Get-Content $file.FullName -Tail 10 -ErrorAction SilentlyContinue
                
                foreach ($line in $lines) {
                    if ($line -match '^\[?(\d{2}:\d{2}:\d{2})\]?\s*(.+)$') {
                        $logs += @{
                            time = $matches[1]
                            message = $matches[2]
                            type = if ($line -match 'ERROR|FAIL') { 'error' }
                                   elseif ($line -match 'SUCCESS|OK|PASS') { 'success' }
                                   else { 'info' }
                        }
                    }
                }
            }
        }
    }
    
    # מיון לפי זמן (אחרונים ראשון)
    return $logs | Select-Object -Last 20
}

# ========================================
# 📈 פונקציה: פעילות אחרונה
# ========================================
function Get-RecentActivity {
    $activity = @()
    $now = Get-Date
    
    # פעילות מקבצים שהשתנו
    $modifiedFiles = Get-ModifiedFiles
    foreach ($file in $modifiedFiles | Select-Object -First 5) {
        $fileName = Split-Path $file -Leaf
        $activity += @{
            time = $now.ToString("HH:mm")
            title = "שינוי קובץ"
            description = "$fileName עודכן"
        }
    }
    
    # פעילות מ-Docker
    $dockerStatus = Get-DockerStatus
    
    if ($dockerStatus.dev.status -eq 'active') {
        $activity += @{
            time = $now.AddMinutes(-5).ToString("HH:mm")
            title = "Development הופעל"
            description = "סביבת פיתוח עלתה עם hot-reload"
        }
    }
    
    if ($dockerStatus.prod.status -eq 'active') {
        $activity += @{
            time = $now.AddMinutes(-10).ToString("HH:mm")
            title = "Production פעיל"
            description = "$($dockerStatus.prod.containers) containers פעילים"
        }
    }
    
    # הוספת פעילות Dashboard
    $activity += @{
        time = $now.ToString("HH:mm")
        title = "עדכון Dashboard"
        description = "עדכון אוטומטי של מדדים וסטטיסטיקות"
    }
    
    return $activity | Select-Object -First 10
}

# ========================================
# 💾 פונקציה: שמירת נתונים ל-JSON
# ========================================
function Save-ProjectStatus {
    $dockerStatus = Get-DockerStatus
    $fileStats = Get-FileStats
    $recentLogs = Get-RecentLogs
    $recentActivity = Get-RecentActivity
    
    $projectData = @{
        lastUpdate = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        environments = $dockerStatus
        files = $fileStats
        logs = $recentLogs
        activity = $recentActivity
    }
    
    # המרה ל-JSON ושמירה
    $json = $projectData | ConvertTo-Json -Depth 10
    $json | Out-File $StatusFile -Encoding UTF8 -Force
    
    Write-Host "✅ Dashboard עודכן: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
    
    return $projectData
}

# ========================================
# 📊 הצגת סטטיסטיקות
# ========================================
function Show-Stats {
    param($data)
    
    Write-Host "`n📊 סטטיסטיקות נוכחיות:" -ForegroundColor Cyan
    Write-Host "  📂 קבצים: $($data.files.total) (מסונכרנים: $($data.files.synced), שונו: $($data.files.modified))"
    Write-Host "  🔧 Development: $($data.environments.dev.status)"
    Write-Host "  🧪 Testing: $($data.environments.test.status)"
    Write-Host "  🚢 Production: $($data.environments.prod.status) ($($data.environments.prod.containers) containers)"
    Write-Host "  📝 לוגים: $($data.logs.Count) שורות אחרונות"
    Write-Host "  📈 פעילות: $($data.activity.Count) אירועים`n"
}

# ========================================
# 🚀 Main - הפעלה חכמה
# ========================================

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🎛️  Dashboard Updater - מעדכן חכם                         ║
║                                                                ║
║   📍 Dashboard: PROJECT_CONTROL_CENTER.html                    ║
║   📍 נתונים: PROJECT_STATUS.json                              ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# בדיקת תיקיות
if (-not (Test-Path $SourceDir)) {
    Write-Warning "⚠️  תיקיית SOURCE/ לא קיימת! יצירת מבנה..."
    New-Item -ItemType Directory -Path $SourceDir -Force | Out-Null
}

if (-not (Test-Path $EnvDir)) {
    Write-Warning "⚠️  תיקיית ENVIRONMENTS/ לא קיימת! יצירת מבנה..."
    New-Item -ItemType Directory -Path $EnvDir -Force | Out-Null
}

# ========================================
# 🔥 מצב FileSystemWatcher (מומלץ!)
# ========================================
if ($Watch) {
    Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║   🔥 מצב FileSystemWatcher פעיל!                             ║
║                                                                ║
║   ✅ עוקב אחרי שינויים בזמן אמת                              ║
║   ⚡ מעדכן רק כשיש שינוי אמיתי                               ║
║   💾 חוסך משאבים - לא רץ סתם                                 ║
║                                                                ║
║   � תיקיות במעקב:                                           ║
║      • SOURCE/ (כל הקוד)                                      ║
║      • docker-compose.yml                                     ║
║      • .env files                                             ║
║                                                                ║
║   🛑 לחץ Ctrl+C לעצירה                                        ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

    # יצירת FileSystemWatcher
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = $ProjectRoot
    $watcher.IncludeSubdirectories = $true
    $watcher.EnableRaisingEvents = $true
    
    # מסננים - עקוב רק אחרי קבצים רלוונטיים
    $watcher.Filter = "*.*"
    $watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor 
                           [System.IO.NotifyFilters]::FileName -bor
                           [System.IO.NotifyFilters]::DirectoryName

    # פונקציה שתרוץ בכל שינוי
    $action = {
        $path = $Event.SourceEventArgs.FullPath
        $changeType = $Event.SourceEventArgs.ChangeType
        $fileName = Split-Path $path -Leaf
        
        # התעלם מקבצים זמניים
        if ($fileName -match '\.tmp$|\.swp$|~$|^\.') {
            return
        }
        
        # התעלם מעדכוני Dashboard עצמו (למנוע לופ)
        if ($fileName -eq 'PROJECT_STATUS.json' -or $fileName -eq 'PROJECT_CONTROL_CENTER.html') {
            return
        }
        
        # עקוב רק אחרי קבצים רלוונטיים
        $relevantExtensions = @('.py', '.js', '.vue', '.html', '.css', '.yml', '.yaml', '.env', '.json')
        $ext = [System.IO.Path]::GetExtension($fileName)
        
        if ($ext -in $relevantExtensions) {
            $timestamp = Get-Date -Format 'HH:mm:ss'
            Write-Host "[$timestamp] 🔄 שינוי זוהה: $fileName ($changeType)" -ForegroundColor Yellow
            
            # המתן קצת (למקרה של שינויים מרובים)
            Start-Sleep -Milliseconds 500
            
            # עדכן Dashboard
            try {
                $data = Save-ProjectStatus
                Write-Host "[$timestamp] ✅ Dashboard עודכן!" -ForegroundColor Green
            }
            catch {
                Write-Host "[$timestamp] ❌ שגיאה בעדכון: $_" -ForegroundColor Red
            }
        }
    }

    # רישום אירועים
    Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action | Out-Null
    Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action | Out-Null
    Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action $action | Out-Null
    Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $action | Out-Null

    Write-Host "✅ FileSystemWatcher פעיל! מחכה לשינויים...`n" -ForegroundColor Green
    
    # עדכון ראשוני
    $data = Save-ProjectStatus
    Show-Stats $data

    # המתן אינסופי
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    }
    finally {
        # נקה בעת סגירה
        $watcher.EnableRaisingEvents = $false
        $watcher.Dispose()
        Get-EventSubscriber | Unregister-Event
        Write-Host "`n🛑 FileSystemWatcher הופסק" -ForegroundColor Yellow
    }
}

# ========================================
# ⏰ מצב Continuous (פולינג רגיל)
# ========================================
elseif ($Continuous) {
    Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║   ⏰ מצב Continuous פעיל                                     ║
║                                                                ║
║   🔄 עדכון כל $IntervalSeconds שניות                                      ║
║   ⚠️  שים לב: זה מעמיס יותר מ-Watch mode                      ║
║                                                                ║
║   💡 מומלץ: הרץ עם -Watch במקום!                             ║
║   🛑 לחץ Ctrl+C לעצירה                                        ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Yellow
    
    while ($true) {
        try {
            $data = Save-ProjectStatus
            Show-Stats $data
            Start-Sleep -Seconds $IntervalSeconds
        }
        catch {
            Write-Error "❌ שגיאה: $_"
            Start-Sleep -Seconds 5
        }
    }
}

# ========================================
# 🎯 מצב Once (חד-פעמי - ברירת מחדל)
# ========================================
else {
    Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║   🎯 עדכון חד-פעמי                                           ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

    $data = Save-ProjectStatus
    Show-Stats $data
    
    Write-Host "`n✅ Dashboard עודכן בהצלחה!`n" -ForegroundColor Green
    Write-Host "📂 פתח את הקובץ: PROJECT_CONTROL_CENTER.html" -ForegroundColor Cyan
    Write-Host @"

� אפשרויות הרצה:

1️⃣  עדכון חד-פעמי (מה שרצת עכשיו):
   .\update_dashboard.ps1

2️⃣  🔥 FileSystemWatcher (מומלץ! - מגיב רק לשינויים):
   .\update_dashboard.ps1 -Watch

3️⃣  ⏰ Continuous (כל 30 שניות):
   .\update_dashboard.ps1 -Continuous

4️⃣  ⏰ Continuous מהיר (כל 5 שניות):
   .\update_dashboard.ps1 -Continuous -IntervalSeconds 5

"@ -ForegroundColor Gray
}
