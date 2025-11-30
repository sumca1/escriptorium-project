// ═══════════════════════════════════════════════════════════
// 🐳 Docker Real-Time Status Integration
// קובץ זה מוסיף אינטגרציה בזמן אמת למצב Docker
// ═══════════════════════════════════════════════════════════

(function() {
    'use strict';
    
    let dockerStatusData = null;
    let dockerUpdateInterval = null;
    
    // טען סטטוס Docker
    async function loadDockerStatus() {
        try {
            const response = await fetch('docker-status.json?' + Date.now());
            dockerStatusData = await response.json();
            
            if (dockerStatusData) {
                updateDockerStatusUI();
                updateDockerDashboard();
            }
        } catch (error) {
            console.log('⚠️  Docker status file not found - monitor may not be running');
        }
    }
    
    // עדכן UI בהדר
    function updateDockerStatusUI() {
        if (!dockerStatusData) return;
        
        const syncText = document.getElementById('sync-text');
        const syncIndicator = document.getElementById('sync-indicator');
        
        if (!syncText || !syncIndicator) return;
        
        if (dockerStatusData.dockerRunning) {
            const running = dockerStatusData.summary.running;
            const total = dockerStatusData.summary.total;
            syncText.textContent = `🐳 Docker: ${running}/${total} פועלים`;
            syncIndicator.classList.remove('disconnected');
        } else {
            syncText.textContent = '❌ Docker כבוי';
            syncIndicator.classList.add('disconnected');
        }
    }
    
    // עדכן דשבורד Docker (אם קיים טאב)
    function updateDockerDashboard() {
        if (!dockerStatusData) return;
        
        const dashboardTab = document.getElementById('dashboard');
        if (!dashboardTab) return;
        
        // בדוק אם יש div מיוחד לסטטוס Docker
        let dockerStatusDiv = document.getElementById('docker-live-status');
        
        if (!dockerStatusDiv) {
            // צור div חדש בראש הדשבורד
            dockerStatusDiv = document.createElement('div');
            dockerStatusDiv.id = 'docker-live-status';
            dockerStatusDiv.style.cssText = `
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            `;
            
            // הוסף בתחילת הדשבורד
            const firstElement = dashboardTab.firstElementChild;
            if (firstElement) {
                dashboardTab.insertBefore(dockerStatusDiv, firstElement);
            } else {
                dashboardTab.appendChild(dockerStatusDiv);
            }
        }
        
        // בנה תוכן
        let html = '<h2 style="margin-bottom: 15px;">🐳 סטטוס Docker בזמן אמת</h2>';
        
        if (dockerStatusData.dockerRunning) {
            const { running, stopped, total } = dockerStatusData.summary;
            const percent = Math.round((running / total) * 100);
            
            html += `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px;">
                    <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 2em; font-weight: bold;">${running}</div>
                        <div>פועלים</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 2em; font-weight: bold;">${stopped}</div>
                        <div>כבויים</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 2em; font-weight: bold;">${total}</div>
                        <div>סה"כ</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 2em; font-weight: bold;">${percent}%</div>
                        <div>זמינות</div>
                    </div>
                </div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                    <h3 style="margin-bottom: 10px;">קונטיינרים:</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
            `;
            
            dockerStatusData.containers.forEach(container => {
                const status = container.isRunning ? '✅' : '⏹️';
                const bgColor = container.isRunning ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)';
                
                html += `
                    <div style="background: ${bgColor}; padding: 8px 15px; border-radius: 8px; font-size: 0.9em;">
                        ${status} ${container.name}
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
            
        } else {
            html += `
                <div style="background: rgba(239, 68, 68, 0.2); padding: 20px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 3em; margin-bottom: 10px;">❌</div>
                    <div style="font-size: 1.2em; font-weight: bold;">Docker Desktop לא פועל</div>
                    <div style="margin-top: 10px; opacity: 0.9;">
                        נא להפעיל את Docker Desktop כדי לראות את הקונטיינרים
                    </div>
                </div>
            `;
        }
        
        html += `
            <div style="margin-top: 15px; font-size: 0.85em; opacity: 0.8; text-align: center;">
                עדכון אחרון: ${new Date(dockerStatusData.timestamp).toLocaleTimeString('he-IL')}
            </div>
        `;
        
        dockerStatusDiv.innerHTML = html;
    }
    
    // התחל מוניטור
    function startDockerMonitoring() {
        console.log('🐳 מתחיל מוניטור Docker...');
        
        // טעינה ראשונה
        loadDockerStatus();
        
        // עדכון כל 5 שניות
        dockerUpdateInterval = setInterval(loadDockerStatus, 5000);
    }
    
    // עצור מוניטור
    function stopDockerMonitoring() {
        if (dockerUpdateInterval) {
            clearInterval(dockerUpdateInterval);
            dockerUpdateInterval = null;
            console.log('🛑 מוניטור Docker נעצר');
        }
    }
    
    // התחל אוטומטית כשהדף נטען
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startDockerMonitoring);
    } else {
        startDockerMonitoring();
    }
    
    // נקה כשעוזבים
    window.addEventListener('beforeunload', stopDockerMonitoring);
    
    // חשוף פונקציות גלובליות
    window.dockerMonitor = {
        load: loadDockerStatus,
        start: startDockerMonitoring,
        stop: stopDockerMonitoring,
        getData: () => dockerStatusData
    };
    
    console.log('✅ Docker Real-Time Integration טעון!');
})();
