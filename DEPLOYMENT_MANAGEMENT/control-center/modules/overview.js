// ========================================
// מודול מבט כללי (Overview Module)
// ========================================

import dataLoader from './data-loader.js';

export async function init() {
    console.log('מאתחל מודול מבט כללי (Initializing Overview Module)');
    await renderOverview();
}

async function renderOverview() {
    const container = document.getElementById('overview-content');
    
    // טעינת נתונים אמיתיים
    const [sessionLog, currentState, dockerStatus] = await Promise.all([
        dataLoader.getSessionLog(),
        dataLoader.getCurrentState(),
        dataLoader.getDockerStatus()
    ]);
    
    const totalFiles = sessionLog.sessions.reduce((sum, s) => sum + s.files.length, 0);
    const dockerRunning = dockerStatus.containers.filter(c => c.isRunning).length;
    const componentsOk = currentState.components.filter(c => c.status === 'success').length;
    const componentsTotal = currentState.components.length;
    
    container.innerHTML = `
        <!-- סטטיסטיקות מפורטות -->
        <div class="stats-grid" style="margin-bottom: 2rem;">
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">קבצים ששונו (Modified Files)</span>
                    <div class="stat-icon" style="background: rgba(59, 130, 246, 0.1); color: var(--primary-blue-light);">
                        📁
                    </div>
                </div>
                <div class="stat-value">${totalFiles}</div>
                <div class="stat-change">
                    <span>מ-${sessionLog.sessions.length} סשנים</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">קונטיינרים פעילים (Docker Containers)</span>
                    <div class="stat-icon" style="background: rgba(5, 150, 105, 0.1); color: var(--success-green);">
                        �
                    </div>
                </div>
                <div class="stat-value">${dockerRunning}</div>
                <div class="stat-change ${dockerRunning === dockerStatus.containers.length ? 'positive' : ''}">
                    <span>${dockerRunning === dockerStatus.containers.length ? 'הכל פועל' : `${dockerStatus.containers.length - dockerRunning} לא פעילים`}</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">רכיבים תקינים (Healthy Components)</span>
                    <div class="stat-icon" style="background: rgba(217, 119, 6, 0.1); color: var(--warning-orange);">
                        ✅
                    </div>
                </div>
                <div class="stat-value">${componentsOk}/${componentsTotal}</div>
                <div class="stat-change">
                    <span>${Math.round((componentsOk / componentsTotal) * 100)}% תקינות</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">עדכון אחרון (Last Update)</span>
                    <div class="stat-icon" style="background: rgba(139, 92, 246, 0.1); color: #8b5cf6;">
                        �
                    </div>
                </div>
                <div class="stat-value">עכשיו</div>
                <div class="stat-change">
                    <span>${currentState.lastUpdate || 'לא ידוע'}</span>
                </div>
            </div>
        </div>

        <!-- לינקים מהירים לקבצי תיעוד -->
        <div class="card" style="margin-bottom: 2rem;">
            <div class="card-header">
                <h3 class="card-title">קבצי תיעוד מרכזיים (Main Documentation)</h3>
            </div>
            <div style="padding: 1rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                <button class="btn btn-primary" onclick="window.viewDocumentation('SESSION_LOG')" style="justify-content: flex-start; padding: 1rem;">
                    <div style="display: flex; flex-direction: column; align-items: flex-start;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.5rem;">📜</span>
                            <strong>SESSION_LOG.md</strong>
                        </div>
                        <span style="font-size: 0.875rem; opacity: 0.8;">היסטוריה מלאה של כל הסשנים</span>
                        <span style="font-size: 0.75rem; color: #059669; margin-top: 0.25rem;">✨ מעוצב בעברית</span>
                    </div>
                </button>
                
                <button class="btn btn-success" onclick="window.viewDocumentation('CURRENT_STATE')" style="justify-content: flex-start; padding: 1rem;">
                    <div style="display: flex; flex-direction: column; align-items: flex-start;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.5rem;">📊</span>
                            <strong>CURRENT_STATE.md</strong>
                        </div>
                        <span style="font-size: 0.875rem; opacity: 0.8;">מצב נוכחי של הפרויקט</span>
                        <span style="font-size: 0.75rem; color: #059669; margin-top: 0.25rem;">✨ מעוצב בעברית</span>
                    </div>
                </button>
            </div>
        </div>

        <!-- טבלת רכיבים -->
        <div class="card" style="margin-top: 2rem;">
            <div class="card-header">
                <h3 class="card-title">מצב רכיבי מערכת (System Components Status)</h3>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>רכיב (Component)</th>
                            <th>גרסה (Version)</th>
                            <th>מצב (Status)</th>
                            <th>זמן עדכון (Last Update)</th>
                            <th>פעולות (Actions)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Django Backend</strong></td>
                            <td>4.2.7</td>
                            <td><span class="status-badge status-success">פעיל</span></td>
                            <td>לפני 2 שעות</td>
                            <td>
                                <button class="btn btn-primary" style="padding: 0.375rem 0.75rem;">
                                    בדוק (Check)
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>Vue.js Frontend</strong></td>
                            <td>3.3.4</td>
                            <td><span class="status-badge status-success">פעיל</span></td>
                            <td>לפני 5 שעות</td>
                            <td>
                                <button class="btn btn-primary" style="padding: 0.375rem 0.75rem;">
                                    בדוק (Check)
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>PostgreSQL Database</strong></td>
                            <td>14.9</td>
                            <td><span class="status-badge status-success">פעיל</span></td>
                            <td>לפני 1 יום</td>
                            <td>
                                <button class="btn btn-primary" style="padding: 0.375rem 0.75rem;">
                                    בדוק (Check)
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>Redis Cache</strong></td>
                            <td>7.2.1</td>
                            <td><span class="status-badge status-warning">איטי</span></td>
                            <td>לפני 3 ימים</td>
                            <td>
                                <button class="btn btn-secondary" style="padding: 0.375rem 0.75rem;">
                                    אתחל (Restart)
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>Nginx Server</strong></td>
                            <td>1.24.0</td>
                            <td><span class="status-badge status-success">פעיל</span></td>
                            <td>לפני שבוע</td>
                            <td>
                                <button class="btn btn-primary" style="padding: 0.375rem 0.75rem;">
                                    בדוק (Check)
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// פונקציה לייצוא דוח
window.exportReport = function() {
    alert('מייצא דוח פעילות שבועי (Exporting weekly activity report)');
    console.log('מייצא דוח...');
};
