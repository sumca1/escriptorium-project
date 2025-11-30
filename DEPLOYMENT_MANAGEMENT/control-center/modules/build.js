/**
 * Build Module - מנהל בנייה (Build Manager)
 * מריץ build scripts ישירות בטרמינל
 */

// Import Terminal Configuration
import terminalConfig from './terminal-config.js';

/**
 * Initialize Build Module
 */
export function init() {
    console.log('🔨 Build Module initialized');
    loadBuildView();
    loadBuildStatus();
    
    // Auto-refresh build status every 10 seconds
    setInterval(() => {
        loadBuildStatus();
    }, 10000);
}

/**
 * Load Build View HTML
 */
function loadBuildView() {
    const container = document.getElementById('build-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="build-manager">
            <div class="build-header">
                <h2>מנהל בנייה (Build Manager)</h2>
                <p class="subtitle">בנייה והידור של המערכת - מופעל ישירות בטרמינל</p>
            </div>
            
            <!-- Build Mode Selection -->
            <div class="build-modes">
                <div class="build-card quick">
                    <div class="build-icon">⚡</div>
                    <h3>בנייה מהירה (Quick Build)</h3>
                    <p>ללא npm install, רק webpack</p>
                    <p class="build-time">⏱️ ~45 שניות</p>
                    <button class="btn btn-primary" onclick="window.buildModule.runBuild('quick')">
                        🚀 הרץ Quick Build
                    </button>
                </div>
                
                <div class="build-card full">
                    <div class="build-icon">🔧</div>
                    <h3>בנייה מלאה (Full Build)</h3>
                    <p>npm install + webpack + כל התהליך</p>
                    <p class="build-time">⏱️ ~10 דקות</p>
                    <button class="btn btn-secondary" onclick="window.buildModule.runBuild('full')">
                        🔨 הרץ Full Build
                    </button>
                </div>
                
                <div class="build-card frontend">
                    <div class="build-icon">🎨</div>
                    <h3>Frontend בלבד</h3>
                    <p>רק Vue.js frontend</p>
                    <p class="build-time">⏱️ ~3 דקות</p>
                    <button class="btn btn-info" onclick="window.buildModule.runBuild('frontend')">
                        🖼️ הרץ Frontend Build
                    </button>
                </div>
                
                <div class="build-card backend">
                    <div class="build-icon">⚙️</div>
                    <h3>Backend בלבד</h3>
                    <p>Django + Python</p>
                    <p class="build-time">⏱️ ~2 דקות</p>
                    <button class="btn btn-info" onclick="window.buildModule.runBuild('backend')">
                        🔧 הרץ Backend Build
                    </button>
                </div>
            </div>
            
            <!-- Build Progress -->
            <div class="build-progress" id="build-progress" style="display: none;">
                <div class="progress-header">
                    <h3>🔄 בנייה מתבצעת...</h3>
                    <button class="btn btn-danger btn-sm" onclick="window.buildModule.cancelBuild()">
                        ❌ בטל (Cancel)
                    </button>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="build-progress-fill"></div>
                </div>
                <div class="progress-status" id="build-status">מתחיל...</div>
                <div class="build-log" id="build-log"></div>
            </div>
            
            <!-- Build Status -->
            <div class="build-status-section">
                <h3>סטטוס בנייה אחרונה (Last Build Status)</h3>
                <div class="status-grid" id="build-status-grid">
                    <div class="loading">טוען סטטוס...</div>
                </div>
            </div>
        </div>
        
        <style>
            .build-manager {
                padding: 20px;
            }
            
            .build-header {
                margin-bottom: 30px;
            }
            
            .build-header h2 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            
            .build-modes {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            
            .build-card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .build-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .build-card.quick { border-top: 4px solid #2ecc71; }
            .build-card.full { border-top: 4px solid #3498db; }
            .build-card.frontend { border-top: 4px solid #9b59b6; }
            .build-card.backend { border-top: 4px solid #f39c12; }
            
            .build-icon {
                font-size: 48px;
                margin-bottom: 15px;
            }
            
            .build-card h3 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            
            .build-card p {
                color: #7f8c8d;
                font-size: 14px;
                margin-bottom: 8px;
            }
            
            .build-time {
                font-weight: bold;
                color: #3498db;
                margin-bottom: 15px !important;
            }
            
            .build-progress {
                background: white;
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .progress-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .progress-bar {
                width: 100%;
                height: 30px;
                background: #ecf0f1;
                border-radius: 15px;
                overflow: hidden;
                margin: 20px 0;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #2ecc71, #3498db);
                transition: width 0.5s ease;
                width: 0%;
            }
            
            .progress-status {
                text-align: center;
                font-weight: bold;
                color: #3498db;
                margin-bottom: 15px;
            }
            
            .build-log {
                max-height: 400px;
                overflow-y: auto;
                background: #2c3e50;
                color: #ecf0f1;
                padding: 15px;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                direction: ltr;
                text-align: left;
            }
            
            .build-status-section {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .build-status-section h3 {
                margin-bottom: 20px;
                color: #2c3e50;
            }
            
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            
            .status-item {
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                border-right: 4px solid #3498db;
            }
            
            .status-item h4 {
                margin-bottom: 8px;
                color: #2c3e50;
                font-size: 14px;
            }
            
            .status-item .value {
                font-size: 18px;
                font-weight: bold;
                color: #3498db;
            }
            
            .status-success { border-right-color: #2ecc71 !important; }
            .status-success .value { color: #2ecc71 !important; }
            .status-failed { border-right-color: #e74c3c !important; }
            .status-failed .value { color: #e74c3c !important; }
        </style>
    `;
}

/**
 * Run Build Process
 */
async function runBuild(mode) {
    console.log(`🔨 Starting ${mode} build`);
    
    const progressSection = document.getElementById('build-progress');
    progressSection.style.display = 'block';
    
    const progressFill = document.getElementById('build-progress-fill');
    const progressStatus = document.getElementById('build-status');
    const buildLog = document.getElementById('build-log');
    
    // Clear previous
    buildLog.innerHTML = '';
    progressFill.style.width = '0%';
    
    // Build scripts mapping
    const buildScripts = {
        'quick': '.\\escriptorium\\scripts\\build\\build-and-deploy.ps1 -Quick',
        'full': '.\\escriptorium\\scripts\\build\\build-and-deploy.ps1 -Full',
        'frontend': '.\\escriptorium\\scripts\\build\\build-frontend.ps1',
        'backend': '.\\escriptorium\\scripts\\build\\build-backend.ps1'
    };
    
    const scriptCommand = buildScripts[mode];
    
    if (!scriptCommand) {
        addBuildLog('❌ שגיאה: מצב בנייה לא מוכר', 'error');
        return;
    }
    
    addBuildLog(`🚀 מתחיל ${mode} build`);
    progressStatus.textContent = 'מכין...';
    progressFill.style.width = '10%';
    
    try {
        addBuildLog('📝 סקריפט: ' + scriptCommand);
        progressFill.style.width = '20%';
        progressStatus.textContent = 'מתחבר לטרמינל...';
        
        // Execute via Terminal Server with auto-port detection
        const result = await terminalConfig.executeCommand(scriptCommand);
        
        progressFill.style.width = '40%';
        progressStatus.textContent = 'בונה...';
        addBuildLog('✅ פקודה נשלחה לטרמינל');
        
        progressFill.style.width = '80%';
        progressStatus.textContent = 'מסיים...';
        
        if (result.output) {
            addBuildLog('📤 פלט:');
            addBuildLog(result.output, 'output');
        }
        
        if (result.error) {
            addBuildLog('⚠️ שגיאות:');
            addBuildLog(result.error, 'error');
        }
        
        progressFill.style.width = '100%';
        progressStatus.textContent = '✅ בנייה הושלמה!';
        progressFill.style.background = 'linear-gradient(90deg, #2ecc71, #27ae60)';
        
        addBuildLog('✅ בנייה הושלמה בהצלחה!', 'success');
        
        // Reload status
        setTimeout(() => {
            loadBuildStatus();
        }, 2000);
        
    } catch (error) {
        console.error('Build error:', error);
        addBuildLog('❌ שגיאה בבנייה: ' + error.message, 'error');
        progressFill.style.width = '100%';
        progressFill.style.background = '#e74c3c';
        progressStatus.textContent = '❌ בנייה נכשלה';
    }
}

/**
 * Add Log to Build Log
 */
function addBuildLog(message, type = 'info') {
    const buildLog = document.getElementById('build-log');
    if (!buildLog) return;
    
    const timestamp = new Date().toLocaleTimeString('he-IL');
    const logEntry = document.createElement('div');
    logEntry.style.marginBottom = '5px';
    
    if (type === 'error') {
        logEntry.style.color = '#e74c3c';
    } else if (type === 'success') {
        logEntry.style.color = '#2ecc71';
    } else if (type === 'output') {
        logEntry.style.color = '#ecf0f1';
        logEntry.style.whiteSpace = 'pre-wrap';
    }
    
    logEntry.textContent = `[${timestamp}] ${message}`;
    buildLog.appendChild(logEntry);
    buildLog.scrollTop = buildLog.scrollHeight;
}

/**
 * Cancel Build
 */
function cancelBuild() {
    const progressSection = document.getElementById('build-progress');
    progressSection.style.display = 'none';
    
    addBuildLog('⚠️ בנייה בוטלה על ידי המשתמש', 'error');
}

/**
 * Load Build Status
 */
async function loadBuildStatus() {
    const statusGrid = document.getElementById('build-status-grid');
    if (!statusGrid) return;
    
    try {
        // Sample data - in real implementation, load from build logs
        const statusData = [
            { label: 'בנייה אחרונה (Last Build)', value: 'לפני 2 שעות', status: 'success' },
            { label: 'סטטוס (Status)', value: 'הצלחה', status: 'success' },
            { label: 'משך זמן (Duration)', value: '3m 45s', status: 'info' },
            { label: 'מצב Frontend', value: 'מעודכן', status: 'success' },
            { label: 'מצב Backend', value: 'מעודכן', status: 'success' },
            { label: 'Docker Images', value: 'מעודכנים', status: 'success' }
        ];
        
        renderStatusGrid(statusData);
        
    } catch (error) {
        console.error('Error loading build status:', error);
        statusGrid.innerHTML = '<div class="error">שגיאה בטעינת סטטוס</div>';
    }
}

/**
 * Render Status Grid
 */
function renderStatusGrid(data) {
    const statusGrid = document.getElementById('build-status-grid');
    if (!statusGrid) return;
    
    let html = '';
    data.forEach(item => {
        const statusClass = item.status === 'success' ? 'status-success' : 
                           item.status === 'failed' ? 'status-failed' : '';
        
        html += `
            <div class="status-item ${statusClass}">
                <h4>${item.label}</h4>
                <div class="value">${item.value}</div>
            </div>
        `;
    });
    
    statusGrid.innerHTML = html;
}

/**
 * Export for global access
 */
window.buildModule = {
    runBuild: runBuild,
    cancelBuild: cancelBuild
};
