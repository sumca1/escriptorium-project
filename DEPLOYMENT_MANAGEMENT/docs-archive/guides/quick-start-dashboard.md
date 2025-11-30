# 🚀 Quick Start - Smart Deploy V2 + Dashboard

## 🎯 הפעלה מהירה (3 דקות)

### שלב 1: הפעל Dashboard Integration (טרמינל 1)

```powershell
cd I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset
.\SCRIPTS\dashboard-integration.ps1
```

**פלט:**
```
╔═══════════════════════════════�?═══════╗
║   🔗 Dashboard Integration           ║
╚══════════════════════════════════════════╝

🔍 מתחיל FileSystemWatcher...
📊 Dashboard data יעודכן ב-dashboard-data.json
✅ Watcher פעיל - ממתין לשינויים...
⏱️  מעדכן כל 2 שניות
🛑 לחץ Ctrl+C לעצור
════════════════════════════════════

[13:45:00] ✅ Dashboard data מעודכן
```

**השאר את הטרמינל הזה רץ!**

---

### שלב 2: פתח את מרכז הבקרה

```powershell
# בדפדפן
start I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\PROJECT_CONTROL_CENTER.html
```

---

### שלב 3: הרץ Deployment (טרמינל 2)

```powershell
# בטרמינל חדש
cd I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset

# Build + Start dev
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Build -Up
```

**מה קורה:**

1. הסקריפט מתחיל לרוץ
2. `.deployment_state.json` מתעדכן בכל שלב
3. `dashboard-integration.ps1` מזהה שינוי
4. `dashboard-data.json` מתעדכן
5. הדשבורד מציג התקדמות בזמן אמת!

---

## 📊 הוספת Live Refresh לדשבורד

### עדכן PROJECT_CONTROL_CENTER.html

הוסף בסוף הקובץ, לפני `</body>`:

```html
<!-- Live Dashboard Updates -->
<script>
// קרא dashboard-data.json בזמן אמת
async function loadDashboardData() {
    try {
        const response = await fetch('dashboard-data.json?' + Date.now()); // cache bust
        const data = await response.json();
        
        updateDeploymentStatus(data);
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

// עדכן UI
function updateDeploymentStatus(data) {
    if (!data || !data.summary) return;
    
    const summary = data.summary;
    
    // עדכן Status Badge
    const statusBadge = document.getElementById('deployment-status');
    if (statusBadge) {
        const statusIcon = summary.status === 'running' ? '🔄' :
                          summary.status === 'completed' ? '✅' :
                          summary.status === 'failed' ? '❌' : '⏳';
        
        const statusText = summary.status === 'running' ? 'פועל' :
                          summary.status === 'completed' ? 'הושלם' :
                          summary.status === 'failed' ? 'נכשל' : 'סרק';
        
        statusBadge.innerHTML = `${statusIcon} ${statusText}`;
        statusBadge.className = `badge badge-${summary.status}`;
    }
    
    // עדכן Progress Bar
    const progressBar = document.getElementById('deployment-progress');
    if (progressBar) {
        progressBar.style.width = summary.percent + '%';
        progressBar.setAttribute('aria-valuenow', summary.percent);
        progressBar.innerHTML = `${summary.percent}%`;
        
        // צבע לפי סטטוס
        progressBar.className = 'progress-bar';
        if (summary.status === 'running') {
            progressBar.classList.add('bg-warning');
        } else if (summary.status === 'completed') {
            progressBar.classList.add('bg-success');
        } else if (summary.status === 'failed') {
            progressBar.classList.add('bg-danger');
        }
    }
    
    // עדכן Steps List
    if (data.deployment && data.deployment.steps) {
        updateStepsList(data.deployment.steps);
    }
    
    // עדכן Errors
    if (summary.errors && summary.errors.length > 0) {
        showErrors(summary.errors);
    }
}

// עדכן רשימת שלבים
function updateStepsList(steps) {
    const stepsList = document.getElementById('deployment-steps');
    if (!stepsList) return;
    
    stepsList.innerHTML = steps.map((step, i) => {
        const icon = step.status === 'completed' ? '✅' :
                    step.status === 'running' ? '🔄' :
                    step.status === 'failed' ? '❌' :
                    step.status === 'skipped' ? '⏭️' : '⏳';
        
        const statusClass = step.status || 'pending';
        const duration = step.duration ? ` (${step.duration.toFixed(1)}s)` : '';
        
        return `
            <li class="list-group-item list-group-item-${statusClass}">
                <span class="step-icon">${icon}</span>
                <span class="step-name">${step.name}</span>
                <span class="step-duration">${duration}</span>
            </li>
        `;
    }).join('');
}

// הצג שגיאות
function showErrors(errors) {
    const errorContainer = document.getElementById('deployment-errors');
    if (!errorContainer) return;
    
    errorContainer.innerHTML = `
        <div class="alert alert-danger">
            <strong>⚠️ שגיאות:</strong>
            <ul>
                ${errors.map(err => `<li>${err}</li>`).join('')}
            </ul>
        </div>
    `;
}

// רענן כל 2 שניות
setInterval(loadDashboardData, 2000);

// טעינה ראשונית
loadDashboardData();

console.log('📊 Live dashboard updates פעיל');
</script>

<style>
/* Deployment Status Styles */
.badge-running { background-color: #ffc107; }
.badge-completed { background-color: #28a745; }
.badge-failed { background-color: #dc3545; }
.badge-idle { background-color: #6c757d; }

.list-group-item-completed { background-color: #d4edda; }
.list-group-item-running { 
    background-color: #fff3cd; 
    animation: pulse 1.5s infinite;
}
.list-group-item-failed { background-color: #f8d7da; }
.list-group-item-skipped { background-color: #e2e3e5; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.step-duration {
    float: right;
    color: #6c757d;
    font-size: 0.9em;
}
</style>
```

---

### הוסף UI Elements לדשבורד

```html
<!-- הוסף אחרי ה-header -->
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>📊 מצב Deployment</h2>
            <span id="deployment-status" class="badge badge-idle">⏳ סרק</span>
        </div>
        <div class="card-body">
            <!-- Progress Bar -->
            <div class="progress mb-3" style="height: 30px;">
                <div id="deployment-progress" 
                     class="progress-bar" 
                     role="progressbar" 
                     style="width: 0%" 
                     aria-valuenow="0" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    0%
                </div>
            </div>
            
            <!-- Steps List -->
            <ul id="deployment-steps" class="list-group">
                <!-- יעודכן דינמית -->
            </ul>
            
            <!-- Errors -->
            <div id="deployment-errors" class="mt-3">
                <!-- יעודכן אם יש שגיאות -->
            </div>
        </div>
    </div>
</div>
```

---

## 🎮 כפתורים (אופציונלי - עדיין manual)

```html
<!-- כפתורים להרצה -->
<div class="deployment-controls mt-3">
    <h3>🎮 פקודות</h3>
    
    <div class="btn-group" role="group">
        <button class="btn btn-primary" onclick="copyCommand('build-up-dev')">
            🔨 Build + Start Dev
        </button>
        <button class="btn btn-success" onclick="copyCommand('up-dev')">
            🚀 Start Dev
        </button>
        <button class="btn btn-danger" onclick="copyCommand('down-dev')">
            🛑 Stop Dev
        </button>
        <button class="btn btn-info" onclick="copyCommand('show-state')">
            📊 Show State
        </button>
        <button class="btn btn-warning" onclick="copyCommand('resume')">
            🔄 Resume
        </button>
    </div>
    
    <div class="alert alert-info mt-3">
        <strong>💡 טיפ:</strong> לחץ על כפתור כדי להעתיק את הפקודה, ואז הדבק בטרמינל
    </div>
</div>

<script>
const commands = {
    'build-up-dev': '.\\SCRIPTS\\smart-deploy-v2.ps1 -Environment dev -Build -Up',
    'up-dev': '.\\SCRIPTS\\smart-deploy-v2.ps1 -Environment dev -Up',
    'down-dev': '.\\SCRIPTS\\smart-deploy-v2.ps1 -Environment dev -Down',
    'show-state': '.\\SCRIPTS\\smart-deploy-v2.ps1 -ShowState',
    'resume': '.\\SCRIPTS\\smart-deploy-v2.ps1 -Environment dev -Resume'
};

function copyCommand(cmd) {
    const command = commands[cmd];
    
    // העתק ל-clipboard
    navigator.clipboard.writeText(command).then(() => {
        alert(`✅ הועתק!\n\n${command}\n\nהדבק בטרמינל 2`);
    }).catch(err => {
        prompt('העתק ידנית:', command);
    });
}
</script>
```

---

## ✅ סיכום - מה יש לך עכשיו?

### טרמינל 1 (רץ תמיד):
```powershell
.\SCRIPTS\dashboard-integration.ps1
```
→ עוקב אחר `.deployment_state.json`  
→ מעדכן `dashboard-data.json`  
→ מספק מידע לדשבורד

### טרמינל 2 (הרצות):
```powershell
.\SCRIPTS\smart-deploy-v2.ps1 -Environment dev -Build -Up
```
→ מריץ deployments  
→ שומר state ב-`.deployment_state.json`  
→ פס התקדמות צבעוני

### הדפדפן:
```
PROJECT_CONTROL_CENTER.html
```
→ קורא `dashboard-data.json` כל 2 שניות  
→ מציג progress bar חי  
→ מראה steps בצבעים  
→ מתריע על שגיאות

---

## 🚀 Next Steps

1. ✅ הוסף את ה-HTML למעלה ל-`PROJECT_CONTROL_CENTER.html`
2. ✅ הפעל `dashboard-integration.ps1`
3. ✅ הרץ deployment
4. ✅ צפה בקסם!

5. 🔮 בעתיד: Web API (ראה `DASHBOARD_INTEGRATION.md`)

---

**גרסה:** 1.0  
**תאריך:** 12 נובמבר 2025  
**סטטוס:** 🟢 READY TO USE
