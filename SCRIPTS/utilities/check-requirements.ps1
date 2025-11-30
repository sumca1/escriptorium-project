<#
.SYNOPSIS
    Requirements Checker - בודק את כל הצרכים לפני הרצת סקריפטים

.DESCRIPTION
    סקריפט בדיקה מקיף שבודק:
    - Prerequisites (PowerShell, הרשאות)
    - External Tools (Docker, npm, node)
    - Files & Directories
    - Docker Configuration
    - Network connectivity

.PARAMETER SaveToFile
    שמירת תוצאות לקובץ

.PARAMETER Detailed
    הצגת פרטים מלאים

.EXAMPLE
    .\check-requirements.ps1
    
.EXAMPLE
    .\check-requirements.ps1 -SaveToFile -Detailed

.NOTES
    Version: 1.0
    Date: 12 November 2025
#>

param(
    [switch]$SaveToFile,
    [switch]$Detailed
)

# Load UI functions for beautiful output
$CorePath = Join-Path $PSScriptRoot "core"
if (Test-Path (Join-Path $CorePath "ui-functions.ps1")) {
    . (Join-Path $CorePath "ui-functions.ps1")
}
else {
    # Fallback if ui-functions not available
    function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
    function Write-Error-Custom { param($Message) Write-Host "✗ $Message" -ForegroundColor Red }
    function Write-Warning-Custom { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
    function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
    function Write-Header { param($Message) Write-Host "`n=== $Message ===" -ForegroundColor Cyan }
}

# Results tracking
$global:Results = @{
    Prerequisites = @()
    ExternalTools = @()
    Files = @()
    Docker = @()
    Network = @()
}

$global:TotalChecks = 0
$global:PassedChecks = 0
$global:FailedChecks = 0
$global:WarningChecks = 0

function Add-CheckResult {
    param(
        [string]$Category,
        [string]$Item,
        [ValidateSet("Pass", "Fail", "Warning")]
        [string]$Status,
        [string]$Details = ""
    )
    
    $global:TotalChecks++
    
    switch ($Status) {
        "Pass" { $global:PassedChecks++ }
        "Fail" { $global:FailedChecks++ }
        "Warning" { $global:WarningChecks++ }
    }
    
    $global:Results[$Category] += [PSCustomObject]@{
        Item = $Item
        Status = $Status
        Details = $Details
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 1: Prerequisites
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Test 1: Prerequisites"

# PowerShell Version
$psVersion = $PSVersionTable.PSVersion
if ($psVersion.Major -ge 5) {
    Write-Success "PowerShell: $psVersion"
    Add-CheckResult -Category "Prerequisites" -Item "PowerShell Version" -Status "Pass" -Details "$psVersion"
}
else {
    Write-Error-Custom "PowerShell: $psVersion (נדרש 5.1+)"
    Add-CheckResult -Category "Prerequisites" -Item "PowerShell Version" -Status "Fail" -Details "$psVersion (נדרש 5.1+)"
}

# Execution Policy
$policy = Get-ExecutionPolicy
if ($policy -ne "Restricted") {
    Write-Success "ExecutionPolicy: $policy"
    Add-CheckResult -Category "Prerequisites" -Item "ExecutionPolicy" -Status "Pass" -Details $policy
}
else {
    Write-Error-Custom "ExecutionPolicy: $policy (צריך לשנות)"
    Add-CheckResult -Category "Prerequisites" -Item "ExecutionPolicy" -Status "Fail" -Details "$policy (צריך: RemoteSigned או Unrestricted)"
}

# Administrator Privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Success "הרשאות: Administrator"
    Add-CheckResult -Category "Prerequisites" -Item "Admin Rights" -Status "Pass" -Details "Running as Administrator"
}
else {
    Write-Warning-Custom "הרשאות: User (לא Administrator)"
    Add-CheckResult -Category "Prerequisites" -Item "Admin Rights" -Status "Warning" -Details "Not running as Administrator (חלק מהפעולות עשויות להיכשל)"
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 2: External Tools
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Test 2: External Tools"

# Docker
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker: $dockerVersion"
        Add-CheckResult -Category "ExternalTools" -Item "Docker" -Status "Pass" -Details $dockerVersion
    }
    else {
        throw "Docker command failed"
    }
}
catch {
    Write-Error-Custom "Docker: לא מותקן או לא ב-PATH"
    Add-CheckResult -Category "ExternalTools" -Item "Docker" -Status "Fail" -Details "לא מותקן - התקן מ-https://www.docker.com/products/docker-desktop"
}

# docker-compose
try {
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "docker-compose: $composeVersion"
        Add-CheckResult -Category "ExternalTools" -Item "docker-compose" -Status "Pass" -Details $composeVersion
    }
    else {
        throw "docker-compose command failed"
    }
}
catch {
    Write-Error-Custom "docker-compose: לא זמין"
    Add-CheckResult -Category "ExternalTools" -Item "docker-compose" -Status "Fail" -Details "לא זמין - נכלל ב-Docker Desktop"
}

# Docker Daemon
try {
    docker ps 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker daemon: Running"
        Add-CheckResult -Category "ExternalTools" -Item "Docker Daemon" -Status "Pass" -Details "Running"
        
        # Container count
        $containers = docker ps -q 2>$null
        $count = ($containers | Measure-Object).Count
        if ($Detailed) {
            Write-Info "  Containers running: $count"
        }
    }
    else {
        throw "Docker daemon not responding"
    }
}
catch {
    Write-Error-Custom "Docker daemon: לא רץ"
    Add-CheckResult -Category "ExternalTools" -Item "Docker Daemon" -Status "Fail" -Details "לא רץ - הפעל Docker Desktop"
}

# npm
try {
    $npmVersion = npm --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "npm: v$npmVersion"
        Add-CheckResult -Category "ExternalTools" -Item "npm" -Status "Pass" -Details "v$npmVersion"
    }
    else {
        throw "npm command failed"
    }
}
catch {
    Write-Error-Custom "npm: לא מותקן"
    Add-CheckResult -Category "ExternalTools" -Item "npm" -Status "Fail" -Details "לא מותקן - התקן Node.js מ-https://nodejs.org"
}

# node
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "node: $nodeVersion"
        Add-CheckResult -Category "ExternalTools" -Item "node" -Status "Pass" -Details $nodeVersion
    }
    else {
        throw "node command failed"
    }
}
catch {
    Write-Error-Custom "node: לא מותקן"
    Add-CheckResult -Category "ExternalTools" -Item "node" -Status "Fail" -Details "לא מותקן - התקן Node.js מ-https://nodejs.org"
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 3: Files & Directories
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Test 3: Files & Directories"

$requiredFiles = @(
    @{Path = "SCRIPTS\core\ui-functions.ps1"; Description = "UI Functions Library"},
    @{Path = "SCRIPTS\core\docker-functions.ps1"; Description = "Docker Functions Library"},
    @{Path = "SCRIPTS\core\build-functions.ps1"; Description = "Build Functions Library"},
    @{Path = "SCRIPTS\dev-deploy.ps1"; Description = "Dev Deployment Script"},
    @{Path = "eScriptorium_CLEAN\front\package.json"; Description = "Frontend Package Config"}
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file.Path) {
        Write-Success "$($file.Path)"
        Add-CheckResult -Category "Files" -Item $file.Description -Status "Pass" -Details $file.Path
        
        if ($Detailed) {
            $size = [Math]::Round((Get-Item $file.Path).Length / 1KB, 1)
            Write-Info "  Size: $size KB"
        }
    }
    else {
        Write-Error-Custom "$($file.Path) - חסר!"
        Add-CheckResult -Category "Files" -Item $file.Description -Status "Fail" -Details "$($file.Path) - קובץ חסר"
    }
}

# docker-compose.yml (multiple possible locations)
$dockerComposePaths = @(
    @{Path = "docker-compose.yml"; Location = "Root"},
    @{Path = "eScriptorium_CLEAN\docker-compose.yml"; Location = "eScriptorium_CLEAN"}
)

$foundDockerCompose = $false
$dockerComposeLocation = ""

foreach ($dcPath in $dockerComposePaths) {
    if (Test-Path $dcPath.Path) {
        Write-Success "docker-compose.yml נמצא ב-$($dcPath.Location)"
        Add-CheckResult -Category "Files" -Item "docker-compose.yml" -Status "Pass" -Details "Location: $($dcPath.Location)"
        $foundDockerCompose = $true
        $dockerComposeLocation = $dcPath.Path
        break
    }
}

if (-not $foundDockerCompose) {
    Write-Error-Custom "docker-compose.yml לא נמצא!"
    Add-CheckResult -Category "Files" -Item "docker-compose.yml" -Status "Fail" -Details "לא נמצא באף מיקום"
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 4: Docker Configuration
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Test 4: Docker Configuration"

if ($foundDockerCompose) {
    try {
        $content = Get-Content $dockerComposeLocation -Raw
        
        # Service 'web'
        if ($content -match "^\s*web:" -or $content -match "services:\s+web:") {
            Write-Success "Service 'web' מוגדר"
            Add-CheckResult -Category "Docker" -Item "Service 'web'" -Status "Pass" -Details "מוגדר ב-docker-compose.yml"
        }
        else {
            Write-Warning-Custom "Service 'web' לא מוגדר"
            Add-CheckResult -Category "Docker" -Item "Service 'web'" -Status "Warning" -Details "לא נמצא ב-docker-compose.yml"
        }
        
        # Port 8082
        if ($content -match "8082") {
            Write-Success "Port 8082 מוגדר"
            Add-CheckResult -Category "Docker" -Item "Port 8082" -Status "Pass" -Details "מוגדר ב-docker-compose.yml"
        }
        else {
            Write-Warning-Custom "Port 8082 לא מוגדר (אולי port אחר?)"
            Add-CheckResult -Category "Docker" -Item "Port 8082" -Status "Warning" -Details "לא מוגדר - בדוק איזה port משמש"
        }
        
        # Static volume
        if ($content -match "/usr/src/app/static") {
            Write-Success "Static volume מוגדר"
            Add-CheckResult -Category "Docker" -Item "Static Volume" -Status "Pass" -Details "מוגדר ב-docker-compose.yml"
        }
        else {
            Write-Warning-Custom "Static volume לא מוגדר"
            Add-CheckResult -Category "Docker" -Item "Static Volume" -Status "Warning" -Details "ייתכן שצריך להגדיר"
        }
        
        if ($Detailed) {
            # List all services
            $services = $content | Select-String -Pattern "^\s*(\w+):" -AllMatches | ForEach-Object { $_.Matches.Groups[1].Value }
            Write-Info "  Services found: $($services -join ', ')"
        }
    }
    catch {
        Write-Error-Custom "שגיאה בקריאת docker-compose.yml: $_"
        Add-CheckResult -Category "Docker" -Item "docker-compose.yml parsing" -Status "Fail" -Details $_.Exception.Message
    }
}
else {
    Write-Warning-Custom "לא ניתן לבדוק הגדרות Docker - docker-compose.yml חסר"
    Add-CheckResult -Category "Docker" -Item "Docker Configuration" -Status "Fail" -Details "docker-compose.yml חסר"
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 5: Networxxxxxxxctivity
# ═══════════════════════════════════════════════════════════════════════════

Write-Header "Test 5: Network Connectivity"

# npm registry
try {
    $response = Test-NetConnection -ComputerName "registry.npmjs.org" -Port 443 -WarningAction SilentlyContinue -ErrorAction Stop
    if ($response.TcpTestSucceeded) {
        Write-Success "npm registry נגיש"
        Add-CheckResult -Category "Network" -Item "npm registry" -Status "Pass" -Details "registry.npmjs.org:443 נגיש"
    }
    else {
        Write-Warning-Custom "npm registry לא נגיש"
        Add-CheckResult -Category "Network" -Item "npm registry" -Status "Warning" -Details "בדוק חיבור אינטרנט"
    }
}
catch {
    Write-Warning-Custom "לא ניתן לבדוק גישה לnpm registry"
    Add-CheckResult -Category "Network" -Item "npm registry" -Status "Warning" -Details "בדיקה נכשלה - ייתכן שChrome או Firewall חוסמים"
}

# Docker Hub (if needed)
try {
    $response = Test-NetConnection -ComputerName "hub.docker.com" -Port 443 -WarningAction SilentlyContinue -ErrorAction Stop
    if ($response.TcpTestSucceeded) {
        Write-Success "Docker Hub נגיש"
        Add-CheckResult -Category "Network" -Item "Docker Hub" -Status "Pass" -Details "hub.docker.com:443 נגיש"
    }
    else {
        Write-Warning-Custom "Docker Hub לא נגיש"
        Add-CheckResult -Category "Network" -Item "Docker Hub" -Status "Warning" -Details "בדוק חיבור אינטרנט"
    }
}
catch {
    Write-Warning-Custom "לא ניתן לבדוק גישה לDocker Hub"
    Add-CheckResult -Category "Network" -Item "Docker Hub" -Status "Warning" -Details "בדיקה נכשלה"
}

# ═══════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Header "Summary"

Write-Host ""
Write-Host "Total Checks: $global:TotalChecks" -ForegroundColor White
Write-Host "  ✓ Passed:   $global:PassedChecks" -ForegroundColor Green
Write-Host "  ✗ Failed:   $global:FailedChecks" -ForegroundColor Red
Write-Host "  ⚠ Warnings: $global:WarningChecks" -ForegroundColor Yellow

$successRate = if ($global:TotalChecks -gt 0) { 
    [Math]::Round(($global:PassedChecks / $global:TotalChecks) * 100, 1) 
} else { 
    0 
}

Write-Host "`nSuccess Rate: $successRate%" -ForegroundColor $(
    if ($successRate -ge 90) { "Green" }
    elseif ($successRate -ge 70) { "Yellow" }
    else { "Red" }
)

# Recommendations
Write-Host ""
if ($global:FailedChecks -eq 0 -and $global:WarningChecks -eq 0) {
    Write-Host "✅ כל הבדיקות עברו בהצלחה!" -ForegroundColor Green
    Write-Host "   המערכת מוכנה להרצת סקריפטים." -ForegroundColor Green
}
elseif ($global:FailedChecks -eq 0) {
    Write-Host "⚠️  יש אזהרות, אבל המערכת צריכה לעבוד" -ForegroundColor Yellow
    Write-Host "   בדוק את האזהרות למעלה." -ForegroundColor Yellow
}
else {
    Write-Host "❌ יש בעיות שצריך לתקן!" -ForegroundColor Red
    Write-Host "   תקן את הבעיות המסומנות ב-✗ למעלה." -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 צעדים מומלצים:" -ForegroundColor Cyan
    
    # Specific recommendations
    $recommendations = @()
    
    foreach ($result in $global:Results["ExternalTools"]) {
        if ($result.Status -eq "Fail") {
            if ($result.Item -eq "Docker") {
                $recommendations += "  - התקן Docker Desktop: https://www.docker.com/products/docker-desktop"
            }
            if ($result.Item -eq "Docker Daemon") {
                $recommendations += "  - הפעל Docker Desktop"
            }
            if ($result.Item -in @("npm", "node")) {
                $recommendations += "  - התקן Node.js: https://nodejs.org"
            }
        }
    }
    
    foreach ($result in $global:Results["Files"]) {
        if ($result.Status -eq "Fail" -and $result.Item -eq "docker-compose.yml") {
            $recommendations += "  - צור docker-compose.yml או העתק אותו לפרויקט"
        }
    }
    
    if ($recommendations.Count -gt 0) {
        $recommendations | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
    }
}

# Save to file if requested
if ($SaveToFile) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $outputFile = "check-requirements-$timestamp.json"
    
    $output = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        TotalChecks = $global:TotalChecks
        PassedChecks = $global:PassedChecks
        FailedChecks = $global:FailedChecks
        WarningChecks = $global:WarningChecks
        SuccessRate = $successRate
        Results = $global:Results
    }
    
    $output | ConvertTo-Json -Depth 10 | Set-Content $outputFile
    Write-Host ""
    Write-Host "📄 תוצאות נשמרו ל-$outputFile" -ForegroundColor Cyan
}

Write-Host ""

# Exit code based on results
if ($global:FailedChecks -eq 0) {
    exit 0
}
else {
    exit 1
}
