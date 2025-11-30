/**
 * Logs Module - מציג יומנים (Logs Viewer)
 * צפייה ב-logs של build, deploy, system
 */

/**
 * Initialize Logs Module
 */
export function init() {
    console.log('📋 Logs Module initialized');
    loadLogsView();
    loadLogs('all');
}

/**
 * Load Logs View HTML
 */
function loadLogsView() {
    const container = document.getElementById('logs-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="logs-viewer">
            <div class="logs-header">
                <h2>מציג יומנים (Logs Viewer)</h2>
                <p class="subtitle">צפייה ב-logs מהמערכת</p>
            </div>
            
            <!-- Log Type Filters -->
            <div class="log-filters">
                <button class="filter-btn active" onclick="window.logsModule.filterLogs('all')">
                    📋 הכל (All)
                </button>
                <button class="filter-btn" onclick="window.logsModule.filterLogs('build')">
                    🔨 Build
                </button>
                <button class="filter-btn" onclick="window.logsModule.filterLogs('deploy')">
                    🚀 Deploy
                </button>
                <button class="filter-btn" onclick="window.logsModule.filterLogs('error')">
                    ❌ Errors
                </button>
                <button class="filter-btn" onclick="window.logsModule.filterLogs('system')">
                    ⚙️ System
                </button>
            </div>
            
            <!-- Search Box -->
            <div class="log-search">
                <input type="text" id="log-search-input" placeholder="חיפוש ב-logs..." 
                       oninput="window.logsModule.searchLogs()">
                <button class="btn btn-secondary" onclick="window.logsModule.clearLogs()">
                    🗑️ נקה (Clear)
                </button>
                <button class="btn btn-info" onclick="window.logsModule.downloadLogs()">
                    💾 הורד (Download)
                </button>
            </div>
            
            <!-- Logs Display -->
            <div class="logs-container" id="logs-container">
                <div class="loading">טוען יומנים...</div>
            </div>
        </div>
        
        <style>
            .logs-viewer { padding: 20px; }
            .logs-header { margin-bottom: 30px; }
            .logs-header h2 { color: #2c3e50; margin-bottom: 10px; }
            
            .log-filters {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            
            .filter-btn {
                padding: 10px 20px;
                border: 2px solid #ecf0f1;
                background: white;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: bold;
            }
            
            .filter-btn:hover {
                background: #f8f9fa;
            }
            
            .filter-btn.active {
                background: #3498db;
                color: white;
                border-color: #3498db;
            }
            
            .log-search {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            
            .log-search input {
                flex: 1;
                padding: 12px;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                font-size: 14px;
            }
            
            .logs-container {
                background: #2c3e50;
                color: #ecf0f1;
                padding: 20px;
                border-radius: 12px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                max-height: 600px;
                overflow-y: auto;
                direction: ltr;
                text-align: left;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .log-entry {
                padding: 8px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                line-height: 1.6;
            }
            
            .log-entry.build { border-right: 4px solid #3498db; }
            .log-entry.deploy { border-right: 4px solid #2ecc71; }
            .log-entry.error { border-right: 4px solid #e74c3c; }
            .log-entry.system { border-right: 4px solid #f39c12; }
            
            .log-timestamp {
                color: #95a5a6;
                margin-left: 10px;
            }
            
            .log-type {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                margin-left: 10px;
            }
            
            .log-type.build { background: #3498db; }
            .log-type.deploy { background: #2ecc71; }
            .log-type.error { background: #e74c3c; }
            .log-type.system { background: #f39c12; }
            
            .log-message {
                margin-top: 5px;
                color: #ecf0f1;
            }
        </style>
    `;
}

/**
 * Load Logs
 */
function loadLogs(type = 'all') {
    const container = document.getElementById('logs-container');
    if (!container) return;
    
    // Sample log data
    const sampleLogs = [
        {
            timestamp: new Date(Date.now() - 60000).toISOString(),
            type: 'build',
            message: 'Frontend build completed successfully in 3m 45s'
        },
        {
            timestamp: new Date(Date.now() - 120000).toISOString(),
            type: 'deploy',
            message: 'Deployed to dev environment - 247 files updated'
        },
        {
            timestamp: new Date(Date.now() - 180000).toISOString(),
            type: 'error',
            message: 'Build failed: webpack compilation error on line 342'
        },
        {
            timestamp: new Date(Date.now() - 240000).toISOString(),
            type: 'system',
            message: 'Docker container "web-1" restarted - uptime 2h 15m'
        },
        {
            timestamp: new Date(Date.now() - 300000).toISOString(),
            type: 'build',
            message: 'npm install completed - 1,234 packages installed'
        }
    ];
    
    const filteredLogs = type === 'all' ? sampleLogs : sampleLogs.filter(log => log.type === type);
    
    renderLogs(filteredLogs);
}

/**
 * Render Logs
 */
function renderLogs(logs) {
    const container = document.getElementById('logs-container');
    if (!container) return;
    
    if (logs.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: #95a5a6;">אין logs להצגה</div>';
        return;
    }
    
    let html = '';
    logs.forEach(log => {
        const time = new Date(log.timestamp).toLocaleString('he-IL');
        html += `
            <div class="log-entry ${log.type}">
                <span class="log-type ${log.type}">${log.type.toUpperCase()}</span>
                <span class="log-timestamp">${time}</span>
                <div class="log-message">${log.message}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Filter Logs by Type
 */
function filterLogs(type) {
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Load filtered logs
    loadLogs(type);
}

/**
 * Search Logs
 */
function searchLogs() {
    const searchTerm = document.getElementById('log-search-input').value.toLowerCase();
    const logEntries = document.querySelectorAll('.log-entry');
    
    logEntries.forEach(entry => {
        const message = entry.textContent.toLowerCase();
        if (message.includes(searchTerm)) {
            entry.style.display = 'block';
        } else {
            entry.style.display = 'none';
        }
    });
}

/**
 * Clear Logs
 */
function clearLogs() {
    if (confirm('האם למחוק את כל ה-logs?')) {
        const container = document.getElementById('logs-container');
        container.innerHTML = '<div style="text-align: center; color: #95a5a6;">Logs נמחקו</div>';
    }
}

/**
 * Download Logs
 */
function downloadLogs() {
    const container = document.getElementById('logs-container');
    const logsText = container.textContent;
    
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs_${new Date().toISOString()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Export
 */
window.logsModule = {
    filterLogs,
    searchLogs,
    clearLogs,
    downloadLogs
};
