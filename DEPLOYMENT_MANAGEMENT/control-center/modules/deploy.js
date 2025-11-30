/**
 * Deploy Module - מנהל פריסה (Deployment Manager)
 * מריץ scripts ישירות בטרמינל הפנימי במקום העתקה
 */

// Import Terminal Configuration
import terminalConfig from './terminal-config.js';

/**
 * Initialize Deploy Module
 */
export function init() {
    console.log('📦 Deploy Module initialized');
    loadDeployView();
    loadDeploymentHistory();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadDeploymentHistory();
    }, 30000);
}

/**
 * Load Deploy View HTML
 */
function loadDeployView() {
    const container = document.getElementById('deploy-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="deploy-manager">
            <div class="deploy-header">
                <h2>מנהל פריסה (Deployment Manager)</h2>
                <p class="subtitle">הרצת פריסה לסביבות שונות - מופעל ישירות בטרמינל</p>
            </div>
            
            <!-- Environment Cards -->
            <div class="environment-cards">
                <div class="env-card dev">
                    <div class="env-icon">🔧</div>
                    <h3>פיתוח (Development)</h3>
                    <div class="env-status">
                        <span class="status-badge dev">dev</span>
                        <span class="last-deploy" id="dev-last-deploy">לא פורס</span>
                    </div>
                    <button class="btn btn-primary" onclick="window.deployModule.runDeployment('dev')">
                        🚀 הרץ פריסה (Deploy)
                    </button>
                </div>
                
                <div class="env-card test">
                    <div class="env-icon">🧪</div>
                    <h3>בדיקות (Testing)</h3>
                    <div class="env-status">
                        <span class="status-badge test">test</span>
                        <span class="last-deploy" id="test-last-deploy">לא פורס</span>
                    </div>
                    <button class="btn btn-primary" onclick="window.deployModule.runDeployment('test')">
                        🚀 הרץ פריסה (Deploy)
                    </button>
                </div>
                
                <div class="env-card prod">
                    <div class="env-icon">🎯</div>
                    <h3>ייצור (Production)</h3>
                    <div class="env-status">
                        <span class="status-badge prod">prod</span>
                        <span class="last-deploy" id="prod-last-deploy">לא פורס</span>
                    </div>
                    <button class="btn btn-danger" onclick="window.deployModule.runDeployment('prod')">
                        ⚠️ הרץ פריסה (Deploy)
                    </button>
                </div>
            </div>
            
            <!-- Deployment Progress -->
            <div class="deployment-progress" id="deployment-progress" style="display: none;">
                <h3>🔄 פריסה מתבצעת...</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
                <div class="progress-log" id="progress-log"></div>
            </div>
            
            <!-- Deployment History -->
            <div class="deployment-history">
                <h3>היסטוריית פריסות (Deployment History)</h3>
                <div class="history-table" id="deployment-history-table">
                    <div class="loading">טוען היסטוריה...</div>
                </div>
            </div>
        </div>
        
        <style>
            .deploy-manager {
                padding: 20px;
            }
            
            .deploy-header {
                margin-bottom: 30px;
            }
            
            .deploy-header h2 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            
            .subtitle {
                color: #7f8c8d;
                font-size: 14px;
            }
            
            .environment-cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            
            .env-card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border: 2px solid #ecf0f1;
                transition: all 0.3s ease;
            }
            
            .env-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .env-card.dev { border-top: 4px solid #3498db; }
            .env-card.test { border-top: 4px solid #f39c12; }
            .env-card.prod { border-top: 4px solid #e74c3c; }
            
            .env-icon {
                font-size: 48px;
                text-align: center;
                margin-bottom: 15px;
            }
            
            .env-card h3 {
                text-align: center;
                margin-bottom: 15px;
                color: #2c3e50;
            }
            
            .env-status {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 6px;
            }
            
            .status-badge {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }
            
            .status-badge.dev { background: #3498db; color: white; }
            .status-badge.test { background: #f39c12; color: white; }
            .status-badge.prod { background: #e74c3c; color: white; }
            
            .last-deploy {
                font-size: 12px;
                color: #7f8c8d;
            }
            
            .deployment-progress {
                background: white;
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
                background: linear-gradient(90deg, #3498db, #2ecc71);
                transition: width 0.3s ease;
                width: 0%;
            }
            
            .progress-log {
                max-height: 300px;
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
            
            .deployment-history {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .deployment-history h3 {
                margin-bottom: 20px;
                color: #2c3e50;
            }
            
            .history-table {
                overflow-x: auto;
            }
            
            .history-table table {
                width: 100%;
                border-collapse: collapse;
            }
            
            .history-table th,
            .history-table td {
                padding: 12px;
                text-align: right;
                border-bottom: 1px solid #ecf0f1;
            }
            
            .history-table th {
                background: #f8f9fa;
                font-weight: bold;
                color: #2c3e50;
            }
            
            .history-table tr:hover {
                background: #f8f9fa;
            }
            
            .status-success { color: #2ecc71; font-weight: bold; }
            .status-failed { color: #e74c3c; font-weight: bold; }
            .status-running { color: #f39c12; font-weight: bold; }
        </style>
    `;
}

/**
 * Run Deployment to Specified Environment
 * הרצה ישירה בטרמינל במקום העתקה!
 */
async function runDeployment(environment) {
    console.log(`🚀 Starting deployment to ${environment}`);
    
    // Show progress section
    const progressSection = document.getElementById('deployment-progress');
    progressSection.style.display = 'block';
    
    const progressFill = document.getElementById('progress-fill');
    const progressLog = document.getElementById('progress-log');
    
    // Clear previous logs
    progressLog.innerHTML = '';
    progressFill.style.width = '0%';
    
    // Log start
    addLog('🚀 מתחיל פריסה ל-' + environment.toUpperCase());
    progressFill.style.width = '10%';
    
    // Build script path (NEW correct paths!)
    const scriptPaths = {
        'dev': '.\\escriptorium\\scripts\\deploy\\deploy-dev.ps1',
        'test': '.\\escriptorium\\scripts\\deploy\\deploy-test.ps1',
        'prod': '.\\escriptorium\\scripts\\deploy\\deploy-prod.ps1'
    };
    
    const scriptPath = scriptPaths[environment];
    
    if (!scriptPath) {
        addLog('❌ שגיאה: סביבה לא מוכרת - ' + environment, 'error');
        return;
    }
    
    addLog('📝 סקריפט: ' + scriptPath);
    progressFill.style.width = '20%';
    
    try {
        // Execute command via Terminal Server with auto-port detection
        addLog('🔌 מתחבר לטרמינל...');
        progressFill.style.width = '30%';
        
        const result = await terminalConfig.executeCommand(scriptPath);
        
        progressFill.style.width = '50%';
        addLog('✅ הפקודה נשלחה לטרמינל');
        
        progressFill.style.width = '80%';
        
        // Display output
        if (result.output) {
            addLog('📤 פלט מהטרמינל:');
            addLog(result.output, 'output');
        }
        
        if (result.error) {
            addLog('⚠️ שגיאות:');
            addLog(result.error, 'error');
        }
        
        progressFill.style.width = '100%';
        addLog('✅ פריסה הושלמה!', 'success');
        
        // Update last deploy time
        const lastDeployElement = document.getElementById(`${environment}-last-deploy`);
        if (lastDeployElement) {
            lastDeployElement.textContent = new Date().toLocaleString('he-IL');
        }
        
        // Save to tracking
        await saveDeploymentTracking(environment, 'success', result.output);
        
        // Reload history
        setTimeout(() => {
            loadDeploymentHistory();
        }, 2000);
        
    } catch (error) {
        console.error('Deployment error:', error);
        addLog('❌ שגיאה בפריסה: ' + error.message, 'error');
        progressFill.style.width = '100%';
        progressFill.style.background = '#e74c3c';
        
        await saveDeploymentTracking(environment, 'failed', error.message);
    }
}

/**
 * Add Log Entry to Progress Log
 */
function addLog(message, type = 'info') {
    const progressLog = document.getElementById('progress-log');
    if (!progressLog) return;
    
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
    progressLog.appendChild(logEntry);
    
    // Auto-scroll to bottom
    progressLog.scrollTop = progressLog.scrollHeight;
}

/**
 * Save Deployment to Tracking JSON
 */
async function saveDeploymentTracking(environment, status, output) {
    try {
        const tracking = {
            timestamp: new Date().toISOString(),
            environment: environment,
            status: status,
            user: 'Control Center',
            output: output || '',
            scriptPath: `.\\escriptorium\\scripts\\deploy\\deploy-${environment}.ps1`
        };
        
        // In real implementation, save to JSON file via backend API
        console.log('Tracking saved:', tracking);
        
    } catch (error) {
        console.error('Error saving tracking:', error);
    }
}

/**
 * Load Deployment History from Tracking
 */
async function loadDeploymentHistory() {
    const historyTable = document.getElementById('deployment-history-table');
    if (!historyTable) return;
    
    try {
        // In real implementation, load from tracking-deployment.json
        // For now, show sample data
        
        const sampleHistory = [
            {
                timestamp: new Date(Date.now() - 3600000).toISOString(),
                environment: 'dev',
                status: 'success',
                user: 'Admin',
                duration: '2m 34s'
            },
            {
                timestamp: new Date(Date.now() - 7200000).toISOString(),
                environment: 'test',
                status: 'success',
                user: 'Admin',
                duration: '3m 12s'
            },
            {
                timestamp: new Date(Date.now() - 86400000).toISOString(),
                environment: 'prod',
                status: 'failed',
                user: 'Admin',
                duration: '1m 05s'
            }
        ];
        
        renderHistoryTable(sampleHistory);
        
    } catch (error) {
        console.error('Error loading history:', error);
        historyTable.innerHTML = '<div class="error">שגיאה בטעינת היסטוריה</div>';
    }
}

/**
 * Render History Table
 */
function renderHistoryTable(entries) {
    const historyTable = document.getElementById('deployment-history-table');
    if (!historyTable) return;
    
    if (!entries || entries.length === 0) {
        historyTable.innerHTML = '<div class="no-data">אין היסטוריית פריסות</div>';
        return;
    }
    
    let tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>זמן (Time)</th>
                    <th>סביבה (Environment)</th>
                    <th>סטטוס (Status)</th>
                    <th>משתמש (User)</th>
                    <th>משך (Duration)</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    entries.forEach(entry => {
        const statusClass = entry.status === 'success' ? 'status-success' : 
                           entry.status === 'failed' ? 'status-failed' : 'status-running';
        
        const statusText = entry.status === 'success' ? '✅ הצלחה' :
                          entry.status === 'failed' ? '❌ נכשל' : '🔄 פועל';
        
        const time = new Date(entry.timestamp).toLocaleString('he-IL');
        
        tableHTML += `
            <tr>
                <td>${time}</td>
                <td><span class="status-badge ${entry.environment}">${entry.environment.toUpperCase()}</span></td>
                <td class="${statusClass}">${statusText}</td>
                <td>${entry.user}</td>
                <td>${entry.duration}</td>
            </tr>
        `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    historyTable.innerHTML = tableHTML;
}

/**
 * Export functions for global access
 */
window.deployModule = {
    runDeployment: runDeployment
};
