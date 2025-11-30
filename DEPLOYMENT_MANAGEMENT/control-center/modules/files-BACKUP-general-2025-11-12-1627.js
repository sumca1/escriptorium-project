// ========================================
// מודול מעקב קבצים (File Tracker Module)
// ========================================

import dataLoader from './data-loader.js';
import terminalConfig from './terminal-config.js';

let viewMode = 'table'; // 'table' or 'tree'

export async function init() {
    console.log('מאתחל מודול מעקב קבצים (Initializing File Tracker Module)');
    await renderFileTracker();
}

async function renderFileTracker() {
    const container = document.getElementById('files-content');
    
    // טעינת נתונים אמיתיים
    const projectFiles = await dataLoader.getProjectFiles();
    const gitStatus = await getGitStatus();
    
    container.innerHTML = `
        <!-- כרטיסי סיכום -->
        <div class="stats-grid" style="margin-bottom: 2rem;">
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">קבצים ששונו (Modified Files)</span>
                    <div class="stat-icon" style="background: rgba(217, 119, 6, 0.1); color: var(--warning-orange);">
                        📝
                    </div>
                </div>
                <div class="stat-value">${gitStatus.modified.length}</div>
                <div class="stat-change">
                    <span>לא סונכרנו</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">קבצים חדשים (New Files)</span>
                    <div class="stat-icon" style="background: rgba(5, 150, 105, 0.1); color: var(--success-green);">
                        ➕
                    </div>
                </div>
                <div class="stat-value">${gitStatus.untracked.length}</div>
                <div class="stat-change positive">
                    <span>↑</span>
                    <span>טרם נוספו</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">סטטוס סנכרון (Sync Status)</span>
                    <div class="stat-icon" style="background: rgba(59, 130, 246, 0.1); color: var(--primary-blue-light);">
                        🔄
                    </div>
                </div>
                <div class="stat-value">${gitStatus.modified.length === 0 ? 'מסונכרן' : 'ממתין'}</div>
                <div class="stat-change">
                    <span>${gitStatus.modified.length} שינויים</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">מצב Git</span>
                    <div class="stat-icon" style="background: rgba(139, 92, 246, 0.1); color: #8b5cf6;">
                        🌳
                    </div>
                </div>
                <div class="stat-value">${gitStatus.branch || 'main'}</div>
                <div class="stat-change">
                    <span>Branch נוכחי</span>
                </div>
            </div>
        </div>

        <!-- פילטרים ותצוגה -->
        <div class="card" style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding: 0 0.5rem 0.5rem;">
                <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="window.filterFiles('all')">
                        הכל (All)
                    </button>
                    <button class="btn btn-warning" onclick="window.filterFiles('modified')">
                        שונו (Modified)
                    </button>
                    <button class="btn btn-success" onclick="window.filterFiles('new')">
                        חדשים (New)
                    </button>
                    <button class="btn btn-secondary" onclick="window.filterFiles('python')">
                        Python
                    </button>
                    <button class="btn btn-secondary" onclick="window.filterFiles('javascript')">
                        JavaScript
                    </button>
                </div>
                
                <div style="display: flex; gap: 0.5rem;">
                    <button class="btn ${viewMode === 'table' ? 'btn-primary' : 'btn-secondary'}" onclick="window.switchView('table')">
                        📋 טבלה
                    </button>
                    <button class="btn ${viewMode === 'tree' ? 'btn-primary' : 'btn-secondary'}" onclick="window.switchView('tree')">
                        🌳 עץ
                    </button>
                </div>
            </div>
        </div>

        <!-- אזור תצוגה -->
        <div id="files-view-area">
            ${viewMode === 'table' ? renderTableView(gitStatus) : renderTreeView(gitStatus)}
        </div>
    `;
    
    // רישום פונקציות גלובליות
    window.filterFiles = filterFiles;
    window.switchView = switchView;
    window.syncFile = syncFile;
    window.viewFile = viewFile;
}

// ========================================
// תצוגת טבלה (Table View)
// ========================================
function renderTableView(gitStatus) {
        <!-- כרטיסי סיכום -->
        <div class="stats-grid" style="margin-bottom: 2rem;">
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">קבצים ששונו (Modified Files)</span>
                    <div class="stat-icon" style="background: rgba(217, 119, 6, 0.1); color: var(--warning-orange);">
                        📝
                    </div>
                </div>
                <div class="stat-value">7</div>
                <div class="stat-change">
                    <span>2 שעות אחרונות</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">קבצים חדשים (New Files)</span>
                    <div class="stat-icon" style="background: rgba(5, 150, 105, 0.1); color: var(--success-green);">
                        ➕
                    </div>
                </div>
                <div class="stat-value">3</div>
                <div class="stat-change positive">
                    <span>↑</span>
                    <span>היום</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">קבצים שנמחקו (Deleted Files)</span>
                    <div class="stat-icon" style="background: rgba(220, 38, 38, 0.1); color: var(--danger-red);">
                        🗑️
                    </div>
                </div>
                <div class="stat-value">1</div>
                <div class="stat-change">
                    <span>היום</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">סטטוס סנכרון (Sync Status)</span>
                    <div class="stat-icon" style="background: rgba(59, 130, 246, 0.1); color: var(--primary-blue-light);">
                        🔄
                    </div>
                </div>
                <div class="stat-value">מסונכרן</div>
                <div class="stat-change">
                    <span>לפני 10 דקות</span>
                </div>
            </div>
        </div>

        <!-- פילטרים -->
        <div class="card" style="margin-bottom: 1.5rem;">
            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                <button class="btn btn-primary" onclick="filterFiles('all')">
                    הכל (All)
                </button>
                <button class="btn btn-secondary" onclick="filterFiles('modified')">
                    שונו (Modified)
                </button>
                <button class="btn btn-secondary" onclick="filterFiles('new')">
                    חדשים (New)
                </button>
                <button class="btn btn-secondary" onclick="filterFiles('deleted')">
                    נמחקו (Deleted)
                </button>
                <button class="btn btn-secondary" onclick="filterFiles('python')">
                    Python
                </button>
                <button class="btn btn-secondary" onclick="filterFiles('javascript')">
                    JavaScript
                </button>
            </div>
        </div>

        <!-- טבלת קבצים -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">שינויים אחרונים (Recent Changes)</h3>
                <button class="btn btn-success" onclick="commitChanges()">
                    💾 שמור שינויים (Commit Changes)
                </button>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>קובץ (File)</th>
                            <th>סוג (Type)</th>
                            <th>פעולה (Action)</th>
                            <th>גודל (Size)</th>
                            <th>זמן (Time)</th>
                            <th>פעולות (Actions)</th>
                        </tr>
                    </thead>
                    <tbody id="files-table-body">
                        <tr>
                            <td><strong>SESSION_LOG.md</strong></td>
                            <td><span class="status-badge status-success">Markdown</span></td>
                            <td><span class="status-badge status-warning">שונה (Modified)</span></td>
                            <td>45.2 KB</td>
                            <td>לפני שעה</td>
                            <td>
                                <button class="btn btn-primary" style="padding: 0.375rem 0.75rem;" onclick="window.open('../../../SESSION_LOG.md', '_blank')">
                                    👁️ צפה (View)
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>CURRENT_STATE.md</strong></td>
                            <td><span class="status-badge status-success">Markdown</span></td>
                            <td><span class="status-badge status-warning">שונה (Modified)</span></td>
                            <td>28.7 KB</td>
                            <td>לפני 30 דקות</td>
                            <td>
                                <button class="btn btn-primary" style="padding: 0.375rem 0.75rem;" onclick="window.open('../../../CURRENT_STATE.md', '_blank')">
                                    👁️ צפה (View)
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>escriptorium/ui/control-center/dashboard.html</strong></td>
                            <td><span class="status-badge status-info">HTML</span></td>
                            <td><span class="status-badge status-success">חדש (New)</span></td>
                            <td>65.2 KB</td>
                            <td>עכשיו</td>
                            <td>
                                <button class="btn btn-primary" style="padding: 0.375rem 0.75rem;" onclick="window.open('dashboard.html', '_blank')">
                                    👁️ צפה (View)
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>escriptorium/scripts/deploy/deploy-dev.ps1</strong></td>
                            <td><span class="status-badge status-warning">PowerShell</span></td>
                            <td><span class="status-badge status-warning">שונה (Modified)</span></td>
                            <td>12.4 KB</td>
                            <td>לפני 2 שעות</td>
                            <td>
                                <button class="btn btn-primary" style="padding: 0.375rem 0.75rem;" onclick="alert('נתיב: ../../../escriptorium/scripts/deploy/deploy-dev.ps1')">
                                    👁️ צפה (View)
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>temp_old_backup.py</strong></td>
                            <td><span class="status-badge status-warning">Python</span></td>
                            <td><span class="status-badge status-danger">נמחק (Deleted)</span></td>
                            <td>--</td>
                            <td>לפני 4 שעות</td>
                            <td>
                                <button class="btn btn-secondary" style="padding: 0.375rem 0.75rem;" onclick="restoreFile('temp_old_backup.py')">
                                    ↩️ שחזר (Restore)
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- גרף שינויים לאורך זמן -->
        <div class="card" style="margin-top: 2rem;">
            <div class="card-header">
                <h3 class="card-title">פעילות קבצים - 7 ימים (File Activity - 7 Days)</h3>
            </div>
            <div style="padding: 1rem; background: var(--bg-main); border-radius: 8px;">
                <canvas id="files-chart" style="max-height: 250px;"></canvas>
            </div>
        </div>
    `;
}

// פונקציות עזר
window.filterFiles = function(type) {
    console.log(`מסנן קבצים לפי: ${type}`);
    alert(`מציג קבצים מסוג: ${type} (Filtering files by: ${type})`);
};

window.viewFile = function(filename) {
    console.log(`צופה בקובץ: ${filename}`);
    alert(`פותח קובץ: ${filename} (Opening file: ${filename})`);
};

window.restoreFile = function(filename) {
    console.log(`משחזר קובץ: ${filename}`);
    alert(`משחזר קובץ: ${filename} (Restoring file: ${filename})`);
};

window.commitChanges = function() {
    console.log('שומר שינויים...');
    alert('שומר שינויים למערכת (Committing changes to system)');
};
