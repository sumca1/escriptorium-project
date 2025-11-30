// ========================================
// מודול דשבורד (Dashboard Module)
// ========================================

export async function init() {
    console.log('✅ מודול Dashboard הופעל');
    await renderDashboard();
}

async function renderDashboard() {
    const container = document.getElementById('dashboard');
    
    if (!container) {
        console.warn('⚠️ Dashboard container not found');
        return;
    }
    
    // Clear existing content
    container.innerHTML = '';
    
    container.innerHTML = `
        <div class="dashboard-overview">
            <h2>🎯 מרכז הבקרה - סקירה כללית</h2>
            
            <div class="dashboard-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
                <!-- System Status Card -->
                <div class="dashboard-card" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>🔧 סטטוס המערכת</h3>
                    <div class="status-item" style="margin: 10px 0;">
                        <span class="status-label">Terminal Server:</span>
                        <span class="status-value online" style="color: #28a745;">✅ פעיל - Port 3001</span>
                    </div>
                    <div class="status-item" style="margin: 10px 0;">
                        <span class="status-label">Docker Monitor:</span>
                        <span class="status-value online" style="color: #28a745;">✅ פועל</span>
                    </div>
                    <div class="status-item" style="margin: 10px 0;">
                        <span class="status-label">Dashboard:</span>
                        <span class="status-value online" style="color: #28a745;">✅ מחובר</span>
                    </div>
                </div>

                <!-- Docker Summary Card -->
                <div class="dashboard-card" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>🐋 סיכום Docker</h3>
                    <div id="docker-summary-dash">
                        <p>טוען נתונים...</p>
                    </div>
                </div>

                <!-- Quick Actions Card -->
                <div class="dashboard-card" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>⚡ פעולות מהירות</h3>
                    <div class="quick-actions" style="display: flex; flex-direction: column; gap: 10px;">
                        <button onclick="window.showView('terminal')" class="action-btn" style="padding: 10px; cursor: pointer;">
                            💻 פתח טרמינל
                        </button>
                        <button onclick="window.showView('docker')" class="action-btn" style="padding: 10px; cursor: pointer;">
                            🐋 צפה ב-Docker
                        </button>
                        <button onclick="window.showView('build')" class="action-btn" style="padding: 10px; cursor: pointer;">
                            🔨 בנה OCR
                        </button>
                    </div>
                </div>

                <!-- Recent Activity Card -->
                <div class="dashboard-card" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>📊 פעילות אחרונה</h3>
                    <div class="activity-log" id="activity-log">
                        <div class="activity-item" style="margin: 5px 0; font-size: 0.9em;">
                            <span class="activity-time" style="color: #666;">עכשיו</span>
                            <span class="activity-text"> - Dashboard נטען בהצלחה</span>
                        </div>
                    </div>
                </div>

                <!-- System Resources Card -->
                <div class="dashboard-card" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>📈 משאבים</h3>
                    <div class="resources-info">
                        <p>PowerShell: <strong>7.x</strong></p>
                        <p>Node.js: <strong>פעיל</strong></p>
                        <p>Docker Desktop: <strong>פעיל</strong></p>
                    </div>
                </div>

                <!-- Help Card -->
                <div class="dashboard-card" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>❓ עזרה מהירה</h3>
                    <div class="help-links" style="line-height: 1.8;">
                        <p>📘 מדריך התחלה מהירה</p>
                        <p>📋 רשימת בדיקות</p>
                        <p>📖 מדריך שימוש מלא</p>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Load Docker status for summary
    loadDockerSummary();
    
    // Auto-refresh every 10 seconds
    setInterval(loadDockerSummary, 10000);
    
    console.log('✅ Dashboard content rendered');
}

async function loadDockerSummary() {
    try {
        const response = await fetch('/app/docker-status.json');
        const data = await response.json();
        
        const summaryDiv = document.getElementById('docker-summary-dash');
        if (summaryDiv && data.summary) {
            const { running, stopped, total } = data.summary;
            const percentage = total > 0 ? Math.round((running / total) * 100) : 0;
            
            summaryDiv.innerHTML = `
                <div class="docker-stats" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                    <div class="stat-item" style="text-align: center;">
                        <div class="stat-value running" style="font-size: 2em; font-weight: bold; color: #28a745;">${running}</div>
                        <div class="stat-label" style="font-size: 0.9em; color: #666;">פועלים</div>
                    </div>
                    <div class="stat-item" style="text-align: center;">
                        <div class="stat-value stopped" style="font-size: 2em; font-weight: bold; color: #dc3545;">${stopped}</div>
                        <div class="stat-label" style="font-size: 0.9em; color: #666;">מושבתים</div>
                    </div>
                    <div class="stat-item" style="text-align: center;">
                        <div class="stat-value" style="font-size: 2em; font-weight: bold;">${total}</div>
                        <div class="stat-label" style="font-size: 0.9em; color: #666;">סה"כ</div>
                    </div>
                    <div class="stat-item" style="text-align: center;">
                        <div class="stat-value ${percentage > 70 ? 'running' : 'stopped'}" style="font-size: 2em; font-weight: bold; color: ${percentage > 70 ? '#28a745' : '#dc3545'};">${percentage}%</div>
                        <div class="stat-label" style="font-size: 0.9em; color: #666;">זמינות</div>
                    </div>
                </div>
                <p class="last-update" style="text-align: center; margin-top: 15px; font-size: 0.8em; color: #999;">
                    עדכון אחרון: ${new Date(data.timestamp).toLocaleTimeString('he-IL')}
                </p>
            `;
        }
    } catch (error) {
        console.log('Docker status will load when available');
    }
}
