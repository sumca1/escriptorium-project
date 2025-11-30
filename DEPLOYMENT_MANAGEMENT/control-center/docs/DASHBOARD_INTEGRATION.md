# 🎮 חיבור מרכז הבקרה ל-Smart Deploy V2

## 🎯 מטרה

חבר את `PROJECT_CONTROL_CENTER.html` ל-`smart-deploy-v2.ps1` כך שהמנהל יוכל:

1. ✅ להפעיל deployment בלחיצת כפתור
2. ✅ לראות התקדמות חיה
3. ✅ לקבל התראות על הצלחה/כשלון
4. ✅ לעקוב אחר מצב (state) בזמן אמת

---

## 📋 אסטרטגיות אינטגרציה

### אופציה 1: PowerShell Web API (מומלץ!)

**רעיון:** הדשבורד קורא ל-REST API שמריץ את הסקריפטים

#### שלב 1: צור PowerShell Web Server

```powershell
# SCRIPTS/api-server.ps1
param([int]$Port = 8080)

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Start()

Write-Host "🚀 API Server רץ על http://localhost:$Port"

while ($true) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response
    
    # CORS
    $response.Headers.Add("Access-Control-Allow-Origin", "*")
    
    # Routing
    $path = $request.Url.AbsolutePath
    $method = $request.HttpMethod
    
    switch ($path) {
        "/api/deploy" {
            # POST /api/deploy
            # Body: { "environment": "dev", "build": true, "up": true }
            
            $reader = New-Object System.IO.StreamReader($request.InputStream)
            $body = $reader.ReadToEnd() | ConvertFrom-Json
            
            $env = $body.environment
            $buildFlag = if ($body.build) { "-Build" } else { "" }
            $upFlag = if ($body.up) { "-Up" } else { "" }
            
            # הרץ ב-background
            $job = Start-Job -ScriptBlock {
                param($env, $build, $up)
                & ".\SCRIPTS\smart-deploy-v2.ps1" -Environment $env $build $up
            } -ArgumentList $env, $buildFlag, $upFlag
            
            $result = @{
                success = $true
                jobId = $job.Id
                message = "Deployment התחיל"
            } | ConvertTo-Json
            
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($result)
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        }
        
        "/api/state" {
            # GET /api/state
            if (Test-Path ".deployment_state.json") {
                $state = Get-Content ".deployment_state.json" -Raw
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($state)
            } else {
                $error = @{ error = "אין state" } | ConvertTo-Json
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($error)
            }
            
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        }
        
        "/api/logs" {
            # GET /api/logs
            # TODO: החזר לוגים
        }
        
        default {
            $error = @{ error = "Not Found" } | ConvertTo-Json
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($error)
            $response.StatusCode = 404
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        }
    }
    
    $response.Close()
}
```

#### שלב 2: עדכן את הדשבורד

```html
<!-- הוסף ב-PROJECT_CONTROL_CENTER.html -->
<script>
// API Base URL
const API_URL = 'http://localhost:8080/api';

// הפעל deployment
async function runDeploy(environment, options = {}) {
    const body = {
        environment: environment,
        build: options.build || false,
        up: options.up || false
    };
    
    try {
        const response = await fetch(`${API_URL}/deploy`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('success', `Deployment התחיל - Job ${result.jobId}`);
            startStatePolling(); // התחל polling למצב
        }
    } catch (error) {
        showNotification('error', `שגיאה: ${error.message}`);
    }
}

// קרא מצב בזמן אמת
async function fetchDeployState() {
    try {
        const response = await fetch(`${API_URL}/state`);
        const state = await response.json();
        
        if (!state.error) {
            updateDashboardState(state);
        }
    } catch (error) {
        console.error('Failed to fetch state:', error);
    }
}

// עדכן דשבורד
function updateDashboardState(state) {
    // עדכן פס התקדמות
    const percent = Math.round((state.currentStep / state.totalSteps) * 100);
    document.getElementById('progress-bar').style.width = `${percent}%`;
    document.getElementById('progress-text').textContent = `${percent}%`;
    
    // עדכן רשימת שלבים
    const stepsHtml = state.steps.map((step, i) => {
        const icon = step.status === 'completed' ? '✅' :
                     step.status === 'running' ? '🔄' :
                     step.status === 'failed' ? '❌' : '⏳';
        
        return `<li class="${step.status}">${icon} ${step.name}</li>`;
    }).join('');
    
    document.getElementById('steps-list').innerHTML = stepsHtml;
    
    // התראה אם הושלם/נכשל
    if (state.status === 'completed') {
        showNotification('success', '✅ Deployment הושלם בהצלחה!');
        stopStatePolling();
    } else if (state.status === 'failed') {
        showNotification('error', `❌ Deployment נכשל: ${state.errors.join(', ')}`);
        stopStatePolling();
    }
}

// Polling למצב
let pollingInterval = null;

function startStatePolling() {
    if (pollingInterval) return; // כבר רץ
    
    pollingInterval = setInterval(fetchDeployState, 2000); // כל 2 שניות
}

function stopStatePolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

// כפתורים
document.getElementById('btn-build-dev').addEventListener('click', () => {
    runDeploy('dev', { build: true, up: true });
});

document.getElementById('btn-start-dev').addEventListener('click', () => {
    runDeploy('dev', { up: true });
});

document.getElementById('btn-stop-dev').addEventListener('click', () => {
    runDeploy('dev', { down: true });
});

// טעינה ראשונית
fetchDeployState();
</script>
```

#### שלב 3: הרץ את ה-API Server

```powershell
# בטרמינל נפרד
.\SCRIPTS\api-server.ps1 -Port 8080
```

---

### אופציה 2: FileSystemWatcher (פשוט יותר)

**רעיון:** הדשבורד עוקב אחר `.deployment_state.json` בזמן אמת

#### שלב 1: עדכן monitor.ps1

```powershell
# monitor.ps1 (הוסף)

# עקוב אחר .deployment_state.json
$stateWatcher = New-Object System.IO.FileSystemWatcher
$stateWatcher.Path = $projectRoot
$stateWatcher.Filter = ".deployment_state.json"
$stateWatcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite

$stateWatcher.Changed += {
    Write-Host "📊 State השתנה - מעדכן דשבורד..."
    
    # קרא state
    $state = Get-Content ".deployment_state.json" | ConvertFrom-Json
    
    # עדכן dashboard-data.json
    $dashboardData = @{
        lastUpdate = Get-Date -Format "o"
        deployment = $state
    } | ConvertTo-Json -Depth 10
    
    Set-Content "dashboard-data.json" $dashboardData
}

$stateWatcher.EnableRaisingEvents = $true
```

#### שלב 2: עדכן הדשבורד

```html
<!-- הוסף ב-PROJECT_CONTROL_CENTER.html -->
<script>
// קרא dashboard-data.json
async function loadDashboardData() {
    try {
        const response = await fetch('dashboard-data.json?' + Date.now()); // cache bust
        const data = await response.json();
        
        if (data.deployment) {
            updateDashboardState(data.deployment);
        }
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

// רענן כל 2 שניות
setInterval(loadDashboardData, 2000);

// טעינה ראשונית
loadDashboardData();
</script>
```

#### שלב 3: כפתורים להרצה

```html
<!-- הוסף כפתורים -->
<button onclick="runDeployCommand('dev', 'build-up')">
    🔨 Build + Start Dev
</button>

<script>
function runDeployCommand(env, action) {
    // צור .bat קובץ זמני
    const command = action === 'build-up' 
        ? `.\\SCRIPTS\\smart-deploy-v2.ps1 -Environment ${env} -Build -Up`
        : `.\\SCRIPTS\\smart-deploy-v2.ps1 -Environment ${env} -Down`;
    
    // הרץ דרך exec או תצוגה
    alert(`הרץ בטרמינל:\n${command}`);
    
    // אופציה: צור .bat ופתח
    const batContent = `@echo off\npowershell.exe -NoProfile -ExecutionPolicy Bypass -Command "${command}"`;
    // שמור ל-temp.bat והרץ
}
</script>
```

---

### אופציה 3: WebSocket (מתקדם)

**רעיון:** חיבור דו-כיווני בזמן אמת

```powershell
# SCRIPTS/websocket-server.ps1
# דורש: Install-Module -Name Fleck

using module Fleck

$server = New-Object Fleck.WebSocketServer("ws://localhost:8081")

$server.Start({
    param($socket)
    
    $socket.OnOpen = {
        Write-Host "🔗 Client מחובר"
    }
    
    $socket.OnMessage = {
        param($message)
        
        # Client שלח פקודה
        $cmd = $message | ConvertFrom-Json
        
        if ($cmd.action -eq 'deploy') {
            # הרץ deployment
            Start-Job -ScriptBlock {
                param($env, $build, $up, $socket)
                
                & ".\SCRIPTS\smart-deploy-v2.ps1" -Environment $env -Build:$build -Up:$up
                
                # שלח עדכונים חזרה
                while ($true) {
                    Start-Sleep -Seconds 2
                    
                    if (Test-Path ".deployment_state.json") {
                        $state = Get-Content ".deployment_state.json" | ConvertFrom-Json
                        $socket.Send(($state | ConvertTo-Json))
                        
                        if ($state.status -in @('completed', 'failed')) {
                            break
                        }
                    }
                }
            } -ArgumentList $cmd.environment, $cmd.build, $cmd.up, $socket
        }
    }
})

Write-Host "🚀 WebSocket Server רץ על ws://localhost:8081"
```

---

## 🎨 UI Component - פס התקדמות חי

```html
<!-- הוסף ב-PROJECT_CONTROL_CENTER.html -->
<style>
.deployment-progress {
    margin: 20px 0;
    padding: 15px;
    border: 2px solid #555;
    border-radius: 8px;
    background: #1e1e1e;
}

.progress-container {
    width: 100%;
    height: 30px;
    background: #2d2d2d;
    border: 1px solid #555;
    border-radius: 4px;
    overflow: hidden;
    position: relative;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #4caf50, #8bc34a);
    transition: width 0.5s ease;
    position: relative;
}

.progress-bar.running {
    background: linear-gradient(90deg, #ffc107, #ffeb3b);
}

.progress-bar.failed {
    background: linear-gradient(90deg, #f44336, #e57373);
}

.progress-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-weight: bold;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}

.steps-list {
    list-style: none;
    padding: 0;
    margin-top: 15px;
}

.steps-list li {
    padding: 8px;
    margin: 5px 0;
    border-radius: 4px;
    background: #2d2d2d;
}

.steps-list li.completed {
    background: #1b5e20;
}

.steps-list li.running {
    background: #f57f17;
    animation: pulse 1.5s infinite;
}

.steps-list li.failed {
    background: #b71c1c;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}
</style>

<div class="deployment-progress">
    <h3>📊 מצב Deployment</h3>
    
    <div class="progress-container">
        <div id="progress-bar" class="progress-bar" style="width: 0%">
            <span id="progress-text" class="progress-text">0%</span>
        </div>
    </div>
    
    <ul id="steps-list" class="steps-list">
        <!-- יעודכן דינמית -->
    </ul>
    
    <div class="deployment-controls">
        <button id="btn-build-dev" class="btn-primary">
            🔨 Build + Start Dev
        </button>
        <button id="btn-start-dev" class="btn-success">
            🚀 Start Dev
        </button>
        <button id="btn-stop-dev" class="btn-danger">
            🛑 Stop Dev
        </button>
        <button id="btn-show-state" class="btn-info">
            📊 Show State
        </button>
    </div>
</div>
```

---

## 🚀 קבצים לדוגמה

### 1. PowerShell Web API

צור: `SCRIPTS/api-server.ps1` (ראה למעלה)

### 2. Dashboard Integration Script

```powershell
# SCRIPTS/dashboard-integration.ps1

# טען state
function Get-CurrentDeploymentState {
    if (Test-Path ".deployment_state.json") {
        return Get-Content ".deployment_state.json" | ConvertFrom-Json
    }
    return $null
}

# המר ל-HTML
function ConvertTo-DashboardHtml {
    param($state)
    
    $html = "<div class='state-summary'>"
    
    if ($state) {
        $percent = [math]::Round(($state.currentStep / $state.totalSteps) * 100)
        
        $html += "<div class='progress-bar' style='width: ${percent}%'>"
        $html += "$percent%"
        $html += "</div>"
        
        foreach ($step in $state.steps) {
            $icon = switch ($step.status) {
                "completed" { "✅" }
                "running" { "🔄" }
                "failed" { "❌" }
                default { "⏳" }
            }
            
            $html += "<p class='$($step.status)'>$icon $($step.name)</p>"
        }
    } else {
        $html += "<p>אין deployment פעיל</p>"
    }
    
    $html += "</div>"
    
    return $html
}

# ייצוא JSON לדשבורד
function Export-DashboardData {
    $state = Get-CurrentDeploymentState
    
    $data = @{
        timestamp = Get-Date -Format "o"
        deployment = $state
    }
    
    $data | ConvertTo-Json -Depth 10 | Set-Content "dashboard-data.json"
    Write-Host "✅ Dashboard data מעודכן"
}

# הרץ
Export-DashboardData
```

---

## 🎯 המלצה

**התחל עם אופציה 2 (FileSystemWatcher)** - הכי פשוט:

1. עדכן `monitor.ps1` לעקוב אחר `.deployment_state.json`
2. הוסף `dashboard-data.json` export
3. עדכן `PROJECT_CONTROL_CENTER.html` לקרוא את הקובץ
4. פולינג כל 2 שניות

**אח"כ שדרג לאופציה 1 (Web API)** אם צריך:
- הפעלת deployments מהדשבורד
- ניהול jobs
- לוגים בזמן אמת

---

**גרסה:** 1.0  
**תאריך:** 12 נובמבר 2025
