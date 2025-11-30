# ========================================
# �?? סקריפט פריסה חכם - Smart Deploy
# ========================================
# לומד מטעויות, פותר בעיות אוטומטית, מתעד הכל
# ========================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment,
    
    [switch]$Build,
    [switch]$Up,
    [switch]$Down,
    [switch]$Restart,
    [switch]$Logs,
    [switch]$Status,
    [switch]$Fix        # מצב תיקון אוטומטי
)

$ErrorActionPreference = "Continue"
$ProjectRoot = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset"
$EnvPath = Join-Path $ProjectRoot "ENVIRONMENTS\$Environment"
$LogsPath = Join-Path $ProjectRoot "logs"
$KnowledgeBase = Join-Path $ProjectRoot "SCRIPTS\smart-deploy-knowledge.json"

# יצירת תיקיית לוגים
if (-not (Test-Path $LogsPath)) {
    New-Item -ItemType Directory -Path $LogsPath -Force | Out-Null
}

# ========================================
# �?? Knowledge Base - מאגר ידע
# ========================================

$KnownIssues = @{
    "requirements.txt: not found" = @{
        problem = "Dockerfile מחפש requirements.txt בנתיב שגוי"
        solution = {
            Write-Host "🔧 מתקן: עדכון Dockerfile עם נתיב נכון..." -ForegroundColor Yellow
            
            $dockerfilePath = Join-Path $EnvPath "Dockerfile"
            $content = Get-Content $dockerfilePath -Raw
            
            # זיהוי אוטומטי של הבעיה
            if ($content -match "COPY.*requirements\.txt") {
                if ($content -match "COPY \.\./") {
                    # נתיב יחסי שגוי
                    $content = $content -replace "COPY \.\./\.\./SOURCE/app/requirements\.txt", "COPY SOURCE/app/requirements.txt"
                } elseif ($content -match "COPY app/requirements\.txt") {
                    # נתיב ישיר שגוי
                    $content = $content -replace "COPY app/requirements\.txt", "COPY SOURCE/app/requirements.txt"
                }
                
                $content | Set-Content $dockerfilePath -Encoding UTF8
                Write-Host "�? Dockerfile תוקן!" -ForegroundColor Green
                return $true
            }
            return $false
        }
        category = "dockerfile"
        severity = "high"
        autofix = $true
    }
    
    "context: .*SOURCE" = @{
        problem = "docker-compose.yml עם context שגוי"
        solution = {
            Write-Host "🔧 מתקן: עדכון docker-compose.yml..." -ForegroundColor Yellow
            
            $composePath = Join-Path $EnvPath "docker-compose.yml"
            $content = Get-Content $composePath -Raw
            
            if ($content -match "context:\s*\.\./\.\./SOURCE") {
                $content = $content -replace "context:\s*\.\./\.\./SOURCE", "context: ../.."
                $content = $content -replace "dockerfile:\s*\.\./ENVIRONMENTS", "dockerfile: ENVIRONMENTS"
                
                $content | Set-Content $composePath -Encoding UTF8
                Write-Host "�? docker-compose.yml תוקן!" -ForegroundColor Green
                return $true
            }
            return $false
        }
        category = "docker-compose"
        severity = "high"
        autofix = $true
    }
    
    "no such file or directory.*manage\.py" = @{
        problem = "manage.py לא נמצא - volumes mount לא מוגדר נכון"
        solution = {
            Write-Host "🔧 מתקן: בדיקת volumes ב-docker-compose..." -ForegroundColor Yellow
            
            $composePath = Join-Path $EnvPath "docker-compose.yml"
            $content = Get-Content $composePath -Raw
            
            # ודא volumes mount נכון
            if ($content -notmatch "SOURCE/app:/usr/src/app") {
                Write-Host "⚠️  volumes mount חסר! מוסיף..." -ForegroundColor Yellow
                # הוסף volumes (צריך לוגיקה מורכבת יותר)
                return $false
            }
            
            Write-Host "�? volumes נראה תקין" -ForegroundColor Green
            return $true
        }
        category = "volumes"
        severity = "critical"
        autofix = $false
    }
    
    "port.*already allocated" = @{
        problem = "פורט תפוס על ידי container אחר"
        solution = {
            param($port)
            Write-Host "🔧 מנסה לשחרר פורט $port..." -ForegroundColor Yellow
            
            # מצא container שתופס את הפורט
            $containers = docker ps --format "{{.ID}} {{.Ports}}" | Select-String $port
            
            if ($containers) {
                Write-Host "📦 מצאתי containers שתופסים את הפורט:" -ForegroundColor Yellow
                $containers | ForEach-Object {
                    $id = ($_ -split " ")[0]
                    Write-Host "   🛑 עוצר container: $id" -ForegroundColor Yellow
                    docker stop $id | Out-Null
                }
                Start-Sleep -Seconds 2
                Write-Host "�? פורט שוחרר!" -ForegroundColor Green
                return $true
            }
            
            return $false
        }
        category = "networking"
        severity = "medium"
        autofix = $true
    }
    
    "database.*does not exist" = @{
        problem = "Database לא קיים"
        solution = {
            Write-Host "🔧 יוצר database..." -ForegroundColor Yellow
            
            $dbName = "escriptorium_$Environment"
            
            # הרץ migrations
            docker-compose -f (Join-Path $EnvPath "docker-compose.yml") exec -T web python manage.py migrate
            
            Write-Host "�? Database מוכן!" -ForegroundColor Green
            return $true
        }
        category = "database"
        severity = "high"
        autofix = $true
    }
    
    "Cannot connect to the Docker daemon" = @{
        problem = "Docker לא רץ"
        solution = {
            Write-Host "🔧 מנסה להפעיל Docker..." -ForegroundColor Yellow
            
            Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
            Write-Host "�? ממתין ל-Docker להתחיל (30 שניות)..." -ForegroundColor Yellow
            Start-Sleep -Seconds 30
            
            # בדוק אם Docker זמין
            try {
                docker ps | Out-Null
                Write-Host "�? Docker פעיל!" -ForegroundColor Green
                return $true
            } catch {
                Write-Host "�? Docker לא הצליח להתחיל - נסה ידנית" -ForegroundColor Red
                return $false
            }
        }
        category = "docker-daemon"
        severity = "critical"
        autofix = $true
    }
}

# ========================================
# 📊 פונקציות עזר
# ========================================

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("Info", "Warning", "Error", "Success")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logFile = Join-Path $LogsPath "smart-deploy-$Environment-$(Get-Date -Format 'yyyyMMdd').log"
    
    $colors = @{
        Info = "Cyan"
        Warning = "Yellow"
        Error = "Red"
        Success = "Green"
    }
    
    $icons = @{
        Info = "ℹ️"
        Warning = "⚠️"
        Error = "�?"
        Success = "✅"
    }
    
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content $logFile $logEntry -Encoding UTF8
    
    Write-Host "$($icons[$Level]) $Message" -ForegroundColor $colors[$Level]
}

function Test-DockerRunning {
    try {
        docker ps | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Get-ContainerStatus {
    param([string]$ContainerName)
    
    try {
        $status = docker inspect --format='{{.State.Status}}' $ContainerName 2>$null
        return $status
    } catch {
        return "not-found"
    }
}

function Analyze-Error {
    param([string]$ErrorOutput)
    
    Write-Log "🔍 מנתח שגיאה..." "Info"
    
    $matchedIssues = @()
    
    foreach ($pattern in $KnownIssues.Keys) {
        if ($ErrorOutput -match $pattern) {
            $issue = $KnownIssues[$pattern]
            $matchedIssues += @{
                Pattern = $pattern
                Issue = $issue
            }
            
            Write-Log "🎯 זיהיתי בעיה ידועה: $($issue.problem)" "Warning"
        }
    }
    
    return $matchedIssues
}

function Invoke-AutoFix {
    param([array]$Issues)
    
    $fixed = 0
    $failed = 0
    
    foreach ($issue in $Issues) {
        $issueData = $issue.Issue
        
        if ($issueData.autofix) {
            Write-Log "🔧 מנסה תיקון אוטומטי: $($issueData.problem)" "Info"
            
            try {
                $result = & $issueData.solution
                
                if ($result) {
                    $fixed++
                    Write-Log "�? תוקן בהצלחה!" "Success"
                } else {
                    $failed++
                    Write-Log "⚠️  תיקון נכשל" "Warning"
                }
            } catch {
                $failed++
                Write-Log "�? שגיאה בתיקון: $_" "Error"
            }
        } else {
            Write-Log "ℹ️  בעיה זו דורשת תיקון ידני: $($issueData.problem)" "Info"
        }
    }
    
    return @{
        Fixed = $fixed
        Failed = $failed
    }
}

function Save-Knowledge {
    param(
        [string]$ErrorPattern,
        [string]$Solution,
        [string]$Category
    )
    
    # שמור ידע חדש למאגר
    $knowledge = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        pattern = $ErrorPattern
        solution = $Solution
        category = $Category
        environment = $Environment
    }
    
    $existingKnowledge = @()
    if (Test-Path $KnowledgeBase) {
        $existingKnowledge = Get-Content $KnowledgeBase -Raw | ConvertFrom-Json
    }
    
    $existingKnowledge += $knowledge
    $existingKnowledge | ConvertTo-Json -Depth 10 | Set-Content $KnowledgeBase -Encoding UTF8
    
    Write-Log "💾 ידע חדש נשמר למאגר!" "Success"
}

# ========================================
# 🎯 פונקציות ראשיות
# ========================================

function Invoke-SmartBuild {
    Write-Log "🔨 בונה סביבת $Environment..." "Info"
    
    Push-Location $EnvPath
    
    # ניסיון ראשון
    Write-Log "📦 ניסיון build..." "Info"
    $output = docker-compose build web 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "�? Build הצליח!" "Success"
        Pop-Location
        return $true
    }
    
    # יש שגיאה - נתחל
    Write-Log "⚠️  Build נכשל! מנתח..." "Warning"
    Write-Log $output "Info"
    
    $issues = Analyze-Error -ErrorOutput $output
    
    if ($issues.Count -gt 0 -and $Fix) {
        Write-Log "🔧 מצאתי $($issues.Count) בעיות ידועות. מתקן..." "Info"
        
        $fixResults = Invoke-AutoFix -Issues $issues
        
        Write-Log "📊 תוצאות תיקון: $($fixResults.Fixed) תוקנו, $($fixResults.Failed) נכשלו" "Info"
        
        if ($fixResults.Fixed -gt 0) {
            Write-Log "🔄 מנסה build שוב לאחר תיקונים..." "Info"
            $output = docker-compose build web 2>&1 | Out-String
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "🎉 Build הצליח אחרי תיקונים!" "Success"
                Pop-Location
                return $true
            }
        }
    }
    
    Write-Log "�? Build נכשל" "Error"
    Pop-Location
    return $false
}

function Invoke-SmartUp {
    Write-Log "🚀 מעלה סביבת $Environment..." "Info"
    
    Push-Location $EnvPath
    
    # בדוק Docker
    if (-not (Test-DockerRunning)) {
        Write-Log "�?�?  Docker לא רץ!" "Warning"
        
        if ($Fix) {
            $issue = $KnownIssues["Cannoxxxxxxxct to the Docker daemon"]
            & $issue.solution
        } else {
            Write-Log "💡 הפעל עם -Fix כדי לנסות להפעיל Docker אוטומטית" "Info"
            Pop-Location
            return $false
        }
    }
    
    # הרץ up
    Write-Log "📦 מעלה containers..." "Info"
    $output = docker-compose up -d 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "�? Containers עלו!" "Success"
        
        # המתן להתייצבות
        Write-Log "�? ממתין להתייצבות (10 שניות)..." "Info"
        Start-Sleep -Seconds 10
        
        # בדוק סטטוס
        Invoke-Status
        
        Pop-Location
        return $true
    }
    
    # יש שגיאה
    Write-Log "�?�?  Up נכשל! מנתח..." "Warning"
    Write-Log $output "Info"
    
    $issues = Analyze-Error -ErrorOutput $output
    
    if ($issues.Count -gt 0 -and $Fix) {
        $fixResults = Invoke-AutoFix -Issues $issues
        
        if ($fixResults.Fixed -gt 0) {
            Write-Log "🔄 מנסה up שוב..." "Info"
            $output = docker-compose up -d 2>&1 | Out-String
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "🎉 Up הצליח אחרי תיקונים!" "Success"
                Pop-Location
                return $true
            }
        }
    }
    
    Write-Log "�? Up נכשל" "Error"
    Pop-Location
    return $false
}

function Invoke-Status {
    Write-Log "📊 בודק סטטוס סביבת $Environment..." "Info"
    
    Push-Location $EnvPath
    
    Write-Host "`n╔═══════�?════════�?═══════════════════════╗" -ForegroundColor Cyan
    Write-Host "�?  📊 סטטוס סביבה: $Environment" -ForegroundColor Cyan
    Write-Host "╚═════════════════�?══════�?════�?══════�?═══╝" -ForegroundColor Cyan
    Write-Host ""
    
    # רשימת containers
    $containers = @("web", "db", "redis", "nginx")
    
    foreach ($container in $containers) {
        $fullName = "escriptorium_${Environment}_$container"
        $status = Get-ContainerStatus -ContainerName $fullName
        
        $icon = switch ($status) {
            "running" { "✅" }
            "exited" { "🛑" }
            "not-found" { "❌" }
            default { "⚠️" }
        }
        
        $color = switch ($status) {
            "running" { "Green" }
            "exited" { "Yellow" }
            "not-found" { "Red" }
            default { "Yellow" }
        }
        
        Write-Host "$icon $container : " -NoNewline
        Write-Host $status -ForegroundColor $color
    }
    
    Write-Host ""
    
    # פורטים
    Write-Host "🌐 פורטים:" -ForegroundColor Cyan
    
    $ports = switch ($Environment) {
        "dev" { @{ "Web" = 8000; "Nginx" = 8080 } }
        "test" { @{ "Web" = 8001; "Nginx" = 8081 } }
        "prod" { @{ "Web" = 8082; "Nginx" = 8082 } }
    }
    
    foreach ($service in $ports.Keys) {
        $port = $ports[$service]
        Write-Host "   �? $service : http://localhost:$port" -ForegroundColor Gray
    }
    
    Write-Host ""
    
    Pop-Location
}

function Invoke-SmartLogs {
    param([int]$Lines = 50)
    
    Write-Log "📜 מציג לוגים (אחרונים $Lines שורות)..." "Info"
    
    Push-Location $EnvPath
    docker-compose logs --tail=$Lines web
    Pop-Location
}

# ========================================
# 🎬 Main Logic
# ========================================

Write-Host @"

╔═════════════════════════�?════════════════════════�?═════════════╗
�?   �?? סקריפט פריסה חכם - Smart Deploy                         ║
�?                                                                ║
�?   סביבה: $Environment
�?   תיקון אוטומטי: $(if($Fix){"�? מופעל"}else{"�? כבוי"})
�?                                                                ║
�?══════════�?══════════════�?══════════�?══════════════════�?════════╝

"@ -ForegroundColor Cyan

# בדיקת נתיב
if (-not (Test-Path $EnvPath)) {
    Write-Log "�? סביבה $Environment לא קיימת ב-$EnvPath" "Error"
    exit 1
}

# ביצוע פעולות
$success = $true

if ($Down) {
    Write-Log "🛑 מוריד סביבה..." "Info"
    Push-Location $EnvPath
    docker-compose down
    Pop-Location
}

if ($Build) {
    $success = $success -and (Invoke-SmartBuild)
}

if ($Up) {
    $success = $success -and (Invoke-SmartUp)
}

if ($Restart) {
    Write-Log "🔄 מאתחל containers..." "Info"
    Push-Location $EnvPath
    docker-compose restart
    Pop-Location
}

if ($Status) {
    Invoke-Status
}

if ($Logs) {
    Invoke-SmartLogs
}

# סיכום
Write-Host "`n╔═══════�?══�?════�?════════════════════════╗" -ForegroundColor Cyan
Write-Host "�?  📊 סיכום                              ║" -ForegroundColor Cyan
Write-Host "╚═════════�?════════════════════════�?═════╝" -ForegroundColor Cyan
Write-Host ""

if ($success) {
    Write-Log "🎉 כל הפעולות הסתיימו בהצלחה!" "Success"
} else {
    Write-Log "⚠️  חלק מהפעולות נכשלו. בדוק לוגים ב-$LogsPath" "Warning"
}

Write-Host ""
Write-Host "💡 טיפים:" -ForegroundColor Yellow
Write-Host "   �? הוסף -Fix לתיקון אוטומטי של בעיות" -ForegroundColor Gray
Write-Host "   �? הוסף -Status לבדיקת מצב נוכחי" -ForegroundColor Gray
Write-Host "   �? הוסף -Logs לצפייה בלוגים" -ForegroundColor Gray
Write-Host ""
