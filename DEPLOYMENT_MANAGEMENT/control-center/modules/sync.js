/**
 * Sync Module - מנהל סנכרון (Sync Manager)
 * סנכרון קבצים בין סביבות שונות
 */

// Import Terminal Configuration
import terminalConfig from './terminal-config.js';

/**
 * Initialize Sync Module
 */
export function init() {
    console.log('🔄 Sync Module initialized');
    loadSyncView();
    loadSyncStatus();
}

/**
 * Load Sync View HTML
 */
function loadSyncView() {
    const container = document.getElementById('sync-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="sync-manager">
            <div class="sync-header">
                <h2>מנהל סנכרון (Sync Manager)</h2>
                <p class="subtitle">סנכרון קבצים בין Dev → Test → Production</p>
            </div>
            
            <!-- Sync Flow Diagram -->
            <div class="sync-flow">
                <div class="env-box dev">
                    <div class="env-name">🔧 Dev</div>
                    <div class="file-count" id="dev-files">0 קבצים</div>
                </div>
                <div class="arrow">→</div>
                <div class="env-box test">
                    <div class="env-name">🧪 Test</div>
                    <div class="file-count" id="test-files">0 קבצים</div>
                </div>
                <div class="arrow">→</div>
                <div class="env-box prod">
                    <div class="env-name">🎯 Prod</div>
                    <div class="file-count" id="prod-files">0 קבצים</div>
                </div>
            </div>
            
            <!-- Sync Actions -->
            <div class="sync-actions">
                <button class="btn btn-primary" onclick="window.syncModule.syncEnvironments('dev', 'test')">
                    🔄 סנכרן Dev → Test
                </button>
                <button class="btn btn-primary" onclick="window.syncModule.syncEnvironments('test', 'prod')">
                    🔄 סנכרן Test → Prod
                </button>
                <button class="btn btn-secondary" onclick="window.syncModule.checkDifferences()">
                    🔍 בדוק הבדלים (Check Diff)
                </button>
            </div>
            
            <!-- Auto Sync Toggle -->
            <div class="auto-sync">
                <label class="toggle-label">
                    <input type="checkbox" id="auto-sync-toggle" onchange="window.syncModule.toggleAutoSync()">
                    <span>סנכרון אוטומטי (Auto-Sync)</span>
                </label>
                <span class="auto-sync-info">מסנכרן כל 30 דקות</span>
            </div>
            
            <!-- Sync Progress -->
            <div class="sync-progress" id="sync-progress" style="display: none;">
                <h3>🔄 סנכרון מתבצע...</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="sync-progress-fill"></div>
                </div>
                <div class="sync-log" id="sync-log"></div>
            </div>
            
            <!-- Sync History -->
            <div class="sync-history">
                <h3>היסטוריית סנכרונים (Sync History)</h3>
                <div id="sync-history-list"></div>
            </div>
        </div>
        
        <style>
            .sync-manager { padding: 20px; }
            .sync-header { margin-bottom: 30px; }
            .sync-header h2 { color: #2c3e50; margin-bottom: 10px; }
            
            .sync-flow {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                margin: 40px 0;
                padding: 30px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .env-box {
                padding: 25px;
                border-radius: 12px;
                text-align: center;
                min-width: 150px;
                transition: all 0.3s ease;
            }
            
            .env-box:hover {
                transform: scale(1.05);
            }
            
            .env-box.dev { background: #3498db; color: white; }
            .env-box.test { background: #f39c12; color: white; }
            .env-box.prod { background: #e74c3c; color: white; }
            
            .env-name {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            
            .file-count {
                font-size: 14px;
                opacity: 0.9;
            }
            
            .arrow {
                font-size: 32px;
                color: #7f8c8d;
                font-weight: bold;
            }
            
            .sync-actions {
                display: flex;
                justify-content: center;
                gap: 15px;
                margin: 30px 0;
            }
            
            .auto-sync {
                text-align: center;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                margin: 20px 0;
            }
            
            .toggle-label {
                display: inline-flex;
                align-items: center;
                gap: 10px;
                cursor: pointer;
                font-weight: bold;
            }
            
            .toggle-label input[type="checkbox"] {
                width: 20px;
                height: 20px;
                cursor: pointer;
            }
            
            .auto-sync-info {
                display: block;
                margin-top: 10px;
                font-size: 13px;
                color: #7f8c8d;
            }
            
            .sync-progress {
                background: white;
                border-radius: 12px;
                padding: 25px;
                margin: 20px 0;
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
            
            .sync-log {
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
            
            .sync-history {
                background: white;
                border-radius: 12px;
                padding: 25px;
                margin-top: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .sync-history h3 {
                margin-bottom: 20px;
                color: #2c3e50;
            }
            
            .history-item {
                padding: 15px;
                border-right: 4px solid #3498db;
                background: #f8f9fa;
                margin-bottom: 10px;
                border-radius: 6px;
            }
            
            .history-item.success { border-right-color: #2ecc71; }
            .history-item.failed { border-right-color: #e74c3c; }
        </style>
    `;
}

/**
 * Sync Between Environments
 */
async function syncEnvironments(source, target) {
    console.log(`🔄 Syncing ${source} → ${target}`);
    
    const progressSection = document.getElementById('sync-progress');
    progressSection.style.display = 'block';
    
    const progressFill = document.getElementById('sync-progress-fill');
    const syncLog = document.getElementById('sync-log');
    
    syncLog.innerHTML = '';
    progressFill.style.width = '0%';
    
    addSyncLog(`🔄 מתחיל סנכרון ${source} → ${target}`);
    progressFill.style.width = '10%';
    
    const scriptPath = `.\\escriptorium\\scripts\\utilities\\sync_environments.ps1 -Source ${source} -Target ${target}`;
    
    try {
        addSyncLog('📝 מריץ: ' + scriptPath);
        progressFill.style.width = '30%';
        
        const result = await terminalConfig.executeCommand(scriptPath);
        
        progressFill.style.width = '70%';
        addSyncLog('✅ פקודה בוצעה');
        
        if (result.output) {
            addSyncLog('📤 פלט:');
            addSyncLog(result.output, 'output');
        }
        
        progressFill.style.width = '100%';
        addSyncLog('✅ סנכרון הושלם!', 'success');
        
        setTimeout(() => {
            loadSyncStatus();
        }, 2000);
        
    } catch (error) {
        console.error('Sync error:', error);
        addSyncLog('❌ שגיאה: ' + error.message, 'error');
        progressFill.style.width = '100%';
        progressFill.style.background = '#e74c3c';
    }
}

/**
 * Check Differences Between Environments
 */
async function checkDifferences() {
    addSyncLog('🔍 בודק הבדלים בין סביבות...');
    
    // Run diff check script
    const scriptPath = '.\\escriptorium\\scripts\\utilities\\check_env_diff.ps1';
    
    try {
        const result = await terminalConfig.executeCommand(scriptPath);
        
        if (result.output) {
            addSyncLog('📊 הבדלים נמצאו:');
            addSyncLog(result.output, 'output');
        } else {
            addSyncLog('✅ אין הבדלים!', 'success');
        }
        
    } catch (error) {
        addSyncLog('❌ שגיאה בבדיקת הבדלים: ' + error.message, 'error');
    }
}

/**
 * Toggle Auto Sync
 */
function toggleAutoSync() {
    const toggle = document.getElementById('auto-sync-toggle');
    if (toggle.checked) {
        addSyncLog('✅ סנכרון אוטומטי הופעל', 'success');
        // Start auto sync interval
    } else {
        addSyncLog('⏸️ סנכרון אוטומטי הושבת');
        // Stop auto sync interval
    }
}

/**
 * Load Sync Status
 */
function loadSyncStatus() {
    // Sample data
    document.getElementById('dev-files').textContent = '247 קבצים';
    document.getElementById('test-files').textContent = '245 קבצים';
    document.getElementById('prod-files').textContent = '243 קבצים';
    
    // Load history
    const historyList = document.getElementById('sync-history-list');
    if (historyList) {
        historyList.innerHTML = `
            <div class="history-item success">
                <strong>Dev → Test</strong> - לפני שעה - ✅ הצלחה
            </div>
            <div class="history-item success">
                <strong>Test → Prod</strong> - לפני 3 שעות - ✅ הצלחה
            </div>
        `;
    }
}

/**
 * Add Sync Log
 */
function addSyncLog(message, type = 'info') {
    const syncLog = document.getElementById('sync-log');
    if (!syncLog) return;
    
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
    syncLog.appendChild(logEntry);
    syncLog.scrollTop = syncLog.scrollHeight;
}

/**
 * Export
 */
window.syncModule = {
    syncEnvironments,
    checkDifferences,
    toggleAutoSync
};
