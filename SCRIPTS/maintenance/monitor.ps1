# ========================================
# 🔥 ניטור חכם - Smart Monitor
# ========================================
# פשוט! ישן → מתעורר כשיש שינוי → מעדכן → חזרה לשינה
# ========================================

param(
    [string]$ProjectRoot = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset"
)

$ErrorActionPreference = "Continue"

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║   🔥 מוניטור חכם - Smart Monitor                             ║
║                                                                ║
║   💤 ישן כשאין שינויים                                        ║
║   ⚡ מתעורר רק כשקובץ נשמר                                    ║
║   📊 מעדכן Dashboard מיידית                                   ║
║   💾 אפס CPU כשאין פעילות                                     ║
║                                                                ║
║   🛑 לחץ Ctrl+C לעצירה                                        ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# פונקציה לעדכון Dashboard
function Update-Dashboard {
    param([string]$ChangedFile, [string]$ChangeType)
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
    Write-Host "🔄 שינוי זוהה: " -NoNewline -ForegroundColor Yellow
    Write-Host "$ChangedFile " -NoNewline -ForegroundColor White
    Write-Host "($ChangeType)" -ForegroundColor DarkGray
    
    # קרא מצב נוכחי
    $status = @{
        lastUpdate = Get-Date -Format "dd/MM/yyyy HH:mm:ss"
        lastChange = @{
            file = $ChangedFile
            type = $ChangeType
            time = $timestamp
        }
        environments = @{
            dev = Get-EnvironmentStatus "dev"
            test = Get-EnvironmentStatus "test"
            prod = Get-EnvironmentStatus "prod"
        }
        containers = Get-DockerContainers
        activity = @(
            @{
                time = $timestamp
                action = "שינוי קובץ: $ChangedFile"
                status = "הצלחה"
            }
        )
    }
    
    # שמור ל-JSON
    $statusFile = Join-Path $ProjectRoot "PROJECT_STATUS.json"
    $status | ConvertTo-Json -Depth 10 | Set-Content $statusFile -Encoding UTF8
    
    Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
    Write-Host "✅ Dashboard עודכן!" -ForegroundColor Green
    Write-Host ""
}

# פונקציה לקבלת מצב סביבה
function Get-EnvironmentStatus {
    param([string]$EnvName)
    
    $envPath = Join-Path $ProjectRoot "ENVIRONMENTS\$EnvName"
    $composePath = Join-Path $envPath "docker-compose.yml"
    
    if (Test-Path $composePath) {
        # בדוק אם Containers רצים
        Push-Location $envPath
        $containers = docker-compose ps -q 2>$null
        Pop-Location
        
        if ($containers) {
            return @{
                status = "active"
                uptime = (Get-Random -Minimum 100 -Maximum 5000)  # זמני - צריך חישוב אמיתי
                containers = ($containers | Measure-Object).Count
            }
        }
    }
    
    return @{
        status = "inactive"
        uptime = 0
        containers = 0
    }
}

# פונקציה לקבלת Docker Containers
function Get-DockerContainers {
    $containers = @()
    
    try {
        $running = docker ps --format "{{.Names}}|{{.Status}}" 2>$null
        
        foreach ($line in $running) {
            if ($line) {
                $parts = $line -split '\|'
                $containers += @{
                    name = $parts[0]
                    status = $parts[1]
                }
            }
        }
    } catch {
        # אין Docker או שגיאה
    }
    
    return $containers
}

# ========================================
# 🔥 FileSystemWatcher - הלב הפועם
# ========================================

Write-Host "🔧 מגדיר FileSystemWatcher..." -ForegroundColor Cyan

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $ProjectRoot
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

# מסננים - עקוב רק אחרי קבצים חשובים
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor 
                       [System.IO.NotifyFilters]::FileName -bor
                       [System.IO.NotifyFilters]::DirectoryName

# ========================================
# 🎯 Action - מה לעשות כשיש שינוי
# ========================================

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    $name = $Event.SourceEventArgs.Name
    
    # התעלם מקבצים זמניים
    $ignorePatterns = @(
        '\.tmp$', '\.swp$', '~$', '^\.', 
        'PROJECT_STATUS\.json',  # התעלם מהקובץ שאנחנו יוצרים!
        'PROJECT_CONTROL_CENTER\.html',
        '\.git\\', 'node_modules\\', '__pycache__\\',
        '\.pyc$', '\.pyo$', '\.log$'
    )
    
    $shouldIgnore = $false
    foreach ($pattern in $ignorePatterns) {
        if ($name -match $pattern) {
            $shouldIgnore = $true
            break
        }
    }
    
    if ($shouldIgnore) {
        return  # התעלם משינוי זה
    }
    
    # עקוב רק אחרי קבצים רלוונטיים
    $relevantExtensions = @('.py', '.js', '.vue', '.html', '.css', '.yml', '.yaml', '.json', '.env', '.md')
    $extension = [System.IO.Path]::GetExtension($name)
    
    if ($extension -in $relevantExtensions -or $name -eq 'docker-compose.yml' -or $name -eq '.env') {
        # Debounce - המתן 500ms למקרה של שינויים מרובים
        Start-Sleep -Milliseconds 500
        
        # עדכן Dashboard
        Update-Dashboard -ChangedFile $name -ChangeType $changeType
    }
}

# רישום Events
$handlers = @()
$handlers += Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action
$handlers += Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action
$handlers += Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action $action
$handlers += Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $action

Write-Host "✅ FileSystemWatcher פעיל!" -ForegroundColor Green
Write-Host ""
Write-Host "💤 ישן... מחכה לשינויים..." -ForegroundColor DarkGray
Write-Host ""

# עדכון ראשוני
Update-Dashboard -ChangedFile "Initialization" -ChangeType "Started"

# ========================================
# 💤 לולאת המתנה אינסופית
# ========================================
try {
    while ($true) {
        Start-Sleep -Seconds 1
        # פשוט ישן... FileSystemWatcher יעיר אותנו!
    }
} finally {
    # ניקוי ביציאה
    Write-Host ""
    Write-Host "🛑 עוצר מוניטור..." -ForegroundColor Yellow
    
    foreach ($handler in $handlers) {
        Unregister-Event -SourceIdentifier $handler.Name -ErrorAction SilentlyContinue
    }
    
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    
    Write-Host "✅ מוניטור נעצר בהצלחה" -ForegroundColor Green
}
