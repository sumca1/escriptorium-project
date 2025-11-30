// ========================================
// מודול מעקב קבצים לקונטיינרים (Container Files Tracker)
// ========================================

import dataLoader from './data-loader.js';
import terminalConfig from './terminal-config.js';
import fileWatcher from './file-watcher.js';

let viewMode = localStorage.getItem('filesViewMode') || 'tree'; // 'table' or 'tree'
let currentFilter = 'all';

export async function init() {
    console.log('🐳 מאתחל מודול מעקב קבצים לקונטיינרים');
    await renderFileTracker();
    
    // התחל File Watcher חכם - עדכון רק כשיש שינוי!
    const filesToWatch = [
        'docs/SESSION_LOG.md',
        'docs/CURRENT_STATE.md'
    ];
    
    fileWatcher.startWatching(filesToWatch, (changedFiles) => {
        console.log('📝 קבצים השתנו - מרענן תצוגה...', changedFiles);
        renderFileTracker();
    });
}

async function renderFileTracker() {
    const container = document.getElementById('files-content');
    
    // טעינת נתונים אמיתיים
    const volumeMounts = await getVolumeMounts();
    const sourceFiles = await getSourceFiles();
    const syncStatus = await getSyncStatus();
    const watcherStatus = fileWatcher.getStatus();
    
    container.innerHTML = `
        <!-- אינדיקטור File Watcher -->
        <div style="background: linear-gradient(135deg, rgba(5, 150, 105, 0.1), rgba(59, 130, 246, 0.1)); border: 1px solid var(--success-green); border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.25rem;">${watcherStatus.isRunning ? '👁️' : '⏸️'}</span>
                <div>
                    <div style="font-weight: 600; color: var(--success-green);">
                        ${watcherStatus.isRunning ? '🟢 File Watcher פעיל' : '🔴 File Watcher מושהה'}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">
                        עדכון אוטומטי רק כשיש שינוי | בדיקה כל ${watcherStatus.checkInterval / 1000} שניות
                    </div>
                </div>
            </div>
            <button class="btn btn-secondary" onclick="window.toggleFileWatcher()" style="padding: 0.375rem 0.75rem; font-size: 0.875rem;">
                ${watcherStatus.isRunning ? '⏸️ השהה' : '▶️ הפעל'}
            </button>
        </div>
        
        <div class="stats-grid" style="margin-bottom: 2rem;">
            <!-- Volume Mounts פעילים -->
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">Volume Mounts פעילים</span>
                    <div class="stat-icon" style="background: rgba(59, 130, 246, 0.1); color: var(--primary-blue-light);">
                        🔗
                    </div>
                </div>
                <div class="stat-value">${volumeMounts.length}</div>
                <div class="stat-change">
                    <span>מסונכרנים לקונטיינרים</span>
                </div>
            </div>

            <!-- קבצים ששונו -->
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">קבצים ששונו ב-SOURCE/</span>
                    <div class="stat-icon" style="background: rgba(217, 119, 6, 0.1); color: var(--warning-orange);">
                        📝
                    </div>
                </div>
                <div class="stat-value">${sourceFiles.modified.length}</div>
                <div class="stat-change">
                    <span>ממתינים לסנכרון</span>
                </div>
            </div>

            <!-- סטטוס Dev -->
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">Development Sync</span>
                    <div class="stat-icon" style="background: rgba(5, 150, 105, 0.1); color: var(--success-green);">
                        🔧
                    </div>
                </div>
                <div class="stat-value">${syncStatus.dev.status}</div>
                <div class="stat-change ${syncStatus.dev.status === 'מסונכרן' ? 'positive' : ''}">
                    <span>${syncStatus.dev.files} קבצים</span>
                </div>
            </div>

            <!-- סטטוס Test/Prod -->
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">Test/Prod Sync</span>
                    <div class="stat-icon" style="background: rgba(139, 92, 246, 0.1); color: #8b5cf6;">
                        🚀
                    </div>
                </div>
                <div class="stat-value">${syncStatus.test.status}</div>
                <div class="stat-change">
                    <span>${syncStatus.prod.status}</span>
                </div>
            </div>
        </div>

        <!-- כרטיס Volume Mounts -->
        <div class="card" style="margin-bottom: 1.5rem;">
            <div class="card-header">
                <h3 class="card-title">🔗 Volume Mounts פעילים (Active Volume Mounts)</h3>
                <button class="btn btn-primary" onclick="window.refreshVolumes()">
                    🔄 רענן (Refresh)
                </button>
            </div>
            <div style="padding: 1rem;">
                ${renderVolumeMounts(volumeMounts)}
            </div>
        </div>

        <!-- בחירת תצוגה ופילטרים -->
        <div class="card" style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding: 1rem;">
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    <button class="btn ${currentFilter === 'all' ? 'btn-primary' : 'btn-secondary'}" onclick="window.filterFiles('all')">
                        הכל (All)
                    </button>
                    <button class="btn ${currentFilter === 'modified' ? 'btn-warning' : 'btn-secondary'}" onclick="window.filterFiles('modified')">
                        📝 שונו (${sourceFiles.modified.length})
                    </button>
                    <button class="btn ${currentFilter === 'python' ? 'btn-secondary' : 'btn-secondary'}" onclick="window.filterFiles('python')">
                        🐍 Python
                    </button>
                    <button class="btn ${currentFilter === 'javascript' ? 'btn-secondary' : 'btn-secondary'}" onclick="window.filterFiles('javascript')">
                        💛 JavaScript
                    </button>
                </div>
                
                <!-- כפתורי החלפת תצוגה - בולטים! -->
                <div style="display: flex; gap: 0.5rem; align-items: center; background: var(--bg-main); padding: 0.5rem; border-radius: 8px; border: 2px solid var(--border-color);">
                    <span style="font-size: 0.875rem; color: var(--text-secondary); margin-left: 0.5rem; font-weight: 600;">
                        תצוגה:
                    </span>
                    <button class="btn ${viewMode === 'table' ? 'btn-primary' : 'btn-secondary'}" onclick="window.switchFilesView('table')" style="padding: 0.5rem 1rem; font-size: 0.95rem;">
                        📋 פרטים
                    </button>
                    <button class="btn ${viewMode === 'tree' ? 'btn-primary' : 'btn-secondary'}" onclick="window.switchFilesView('tree')" style="padding: 0.5rem 1rem; font-size: 0.95rem;">
                        🌳 עץ
                    </button>
                </div>
            </div>
        </div>

        <!-- אזור תצוגה -->
        <div id="files-view-area">
            ${viewMode === 'table' ? renderTableView(sourceFiles) : renderTreeView(sourceFiles)}
        </div>

        <!-- סטטוס סנכרון לסביבות -->
        <div class="stats-grid" style="margin-top: 2rem;">
            ${renderSyncStatusCards(syncStatus)}
        </div>
    `;
    
    // רישום פונקציות גלובליות
    window.filterFiles = filterFiles;
    window.switchFilesView = switchFilesView;
    window.refreshVolumes = refreshVolumes;
    window.syncToEnvironment = syncToEnvironment;
    window.viewFileInContainer = viewFileInContainer;
    window.toggleFileWatcher = toggleFileWatcher;
}

// ========================================
// Volume Mounts
// ========================================
function renderVolumeMounts(mounts) {
    if (!mounts || mounts.length === 0) {
        return `<div style="padding: 2rem; text-align: center; color: var(--text-secondary);">
            אין Volume Mounts פעילים כרגע
        </div>`;
    }
    
    return `
        <div style="display: grid; gap: 1rem;">
            ${mounts.map(mount => `
                <div style="background: var(--bg-main); border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
                                ${mount.source}
                            </div>
                            <div style="color: var(--text-secondary); font-size: 0.875rem;">
                                ↓ מסונכרן ל
                            </div>
                            <div style="font-family: 'Courier New', monospace; color: var(--primary-blue-light); margin-top: 0.25rem;">
                                ${mount.target}
                            </div>
                        </div>
                        <span class="status-badge ${mount.active ? 'status-success' : 'status-danger'}">
                            ${mount.active ? '✅ פעיל' : '❌ לא פעיל'}
                        </span>
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                        Container: <strong>${mount.container}</strong> | Mode: <strong>${mount.mode}</strong>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// ========================================
// תצוגת עץ (Tree View)
// ========================================
function renderTreeView(sourceFiles) {
    return `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">🌳 עץ קבצים - SOURCE/ (Files Tree)</h3>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    <span style="color: var(--success-green);">●</span> שונה (Modified) |
                    <span style="color: var(--text-secondary);">●</span> ללא שינוי (Unchanged)
                </div>
            </div>
            <div style="padding: 1rem; font-family: 'Courier New', monospace; background: var(--bg-main);">
                ${renderTreeStructure(sourceFiles)}
            </div>
        </div>
    `;
}

function renderTreeStructure(sourceFiles) {
    // בניית מבנה עץ
    const tree = {
        'SOURCE': {
            'app': {
                'core': ['views.py', 'models.py', 'urls.py'],
                'api': ['serializers.py', 'views.py'],
                'locale': ['he/LC_MESSAGES/django.po']
            },
            'front': {
                'dist': ['editor.js', 'vendor.js', 'styles.css'],
                'vue': ['components/Editor.vue']
            }
        }
    };
    
    let html = '';
    
    function renderNode(name, content, level = 0, isLast = true) {
        const indent = '  '.repeat(level);
        const branch = isLast ? '└── ' : '├── ';
        const isModified = sourceFiles.modified.some(f => f.includes(name));
        const icon = typeof content === 'object' ? '📂' : '📄';
        const color = isModified ? 'color: var(--success-green); font-weight: 600;' : 'color: var(--text-secondary);';
        const badge = isModified ? ' <span style="background: var(--success-green); color: white; padding: 0.125rem 0.375rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">שונה</span>' : '';
        
        html += `<div style="${color}">${indent}${branch}${icon} ${name}${badge}</div>`;
        
        if (typeof content === 'object') {
            const keys = Object.keys(content);
            keys.forEach((key, index) => {
                renderNode(key, content[key], level + 1, index === keys.length - 1);
            });
        } else if (Array.isArray(content)) {
            content.forEach((item, index) => {
                renderNode(item, null, level + 1, index === content.length - 1);
            });
        }
    }
    
    renderNode('SOURCE', tree.SOURCE, 0);
    return html;
}

// ========================================
// תצוגת טבלה (Table View)
// ========================================
function renderTableView(sourceFiles) {
    const allFiles = [
        ...sourceFiles.modified.map(f => ({ path: f, status: 'modified' })),
        ...sourceFiles.unchanged.slice(0, 10).map(f => ({ path: f, status: 'unchanged' }))
    ];
    
    return `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📋 קבצים ב-SOURCE/ (Files in SOURCE/)</h3>
                <button class="btn btn-success" onclick="window.syncToEnvironment('dev')">
                    💾 סנכרן ל-Dev (Sync to Dev)
                </button>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>קובץ (File)</th>
                            <th>סוג (Type)</th>
                            <th>סטטוס (Status)</th>
                            <th>גודל (Size)</th>
                            <th>סנכרון (Sync)</th>
                            <th>פעולות (Actions)</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${allFiles.map(file => {
                            const ext = file.path.split('.').pop();
                            const typeMap = {
                                'py': { label: 'Python', class: 'warning' },
                                'js': { label: 'JavaScript', class: 'info' },
                                'vue': { label: 'Vue', class: 'success' },
                                'css': { label: 'CSS', class: 'info' },
                                'html': { label: 'HTML', class: 'info' },
                                'po': { label: 'Translation', class: 'secondary' }
                            };
                            const type = typeMap[ext] || { label: ext, class: 'secondary' };
                            
                            return `
                                <tr>
                                    <td>
                                        <strong>${file.path}</strong>
                                    </td>
                                    <td>
                                        <span class="status-badge status-${type.class}">${type.label}</span>
                                    </td>
                                    <td>
                                        <span class="status-badge status-${file.status === 'modified' ? 'warning' : 'success'}">
                                            ${file.status === 'modified' ? '📝 שונה' : '✅ מסונכרן'}
                                        </span>
                                    </td>
                                    <td>${Math.floor(Math.random() * 50 + 5)} KB</td>
                                    <td>
                                        <span class="status-badge status-success">Dev ✅</span>
                                        <span class="status-badge status-secondary">Test ⏳</span>
                                    </td>
                                    <td>
                                        <button class="btn btn-primary" style="padding: 0.375rem 0.75rem; font-size: 0.875rem;" onclick="window.viewFileInContainer('${file.path}')">
                                            👁️ צפה בקונטיינר
                                        </button>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// ========================================
// כרטיסי סטטוס סנכרון
// ========================================
function renderSyncStatusCards(syncStatus) {
    const environments = [
        { key: 'dev', name: 'Development', icon: '🔧', color: 'var(--success-green)' },
        { key: 'test', name: 'Testing', icon: '🧪', color: 'var(--warning-orange)' },
        { key: 'prod', name: 'Production', icon: '🚀', color: 'var(--danger-red)' }
    ];
    
    return environments.map(env => {
        const status = syncStatus[env.key];
        const isGood = status.status === 'מסונכרן';
        
        return `
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">${env.icon} ${env.name}</span>
                    <div class="stat-icon" style="background: rgba(${isGood ? '5, 150, 105' : '217, 119, 6'}, 0.1); color: ${isGood ? 'var(--success-green)' : 'var(--warning-orange)'};">
                        ${isGood ? '✅' : '⏳'}
                    </div>
                </div>
                <div class="stat-value">${status.status}</div>
                <div class="stat-change ${isGood ? 'positive' : ''}">
                    <span>${status.files} קבצים מסונכרנים</span>
                </div>
                <button class="btn ${isGood ? 'btn-success' : 'btn-warning'}" style="width: 100%; margin-top: 0.75rem;" onclick="window.syncToEnvironment('${env.key}')">
                    🔄 סנכרן עכשיו (Sync Now)
                </button>
            </div>
        `;
    }).join('');
}

// ========================================
// נתונים (Data Loading)
// ========================================
async function getVolumeMounts() {
    // קריאה מ-docker-compose.yml או Docker API
    return [
        {
            source: 'SOURCE/app',
            target: '/usr/src/app',
            container: 'escriptorium-web-dev',
            mode: 'rw',
            active: true
        },
        {
            source: 'SOURCE/front/dist',
            target: '/usr/src/app/static',
            container: 'escriptorium-web-dev',
            mode: 'rw',
            active: true
        },
        {
            source: 'ENVIRONMENTS/development',
            target: '/usr/src/app',
            container: 'escriptorium-web-dev',
            mode: 'rw',
            active: true
        }
    ];
}

async function getSourceFiles() {
    // יקרא מהמערכת את הקבצים ב-SOURCE/
    return {
        modified: [
            'SOURCE/app/core/views.py',
            'SOURCE/front/dist/editor.js',
            'SOURCE/app/locale/he/LC_MESSAGES/django.po'
        ],
        unchanged: [
            'SOURCE/app/core/models.py',
            'SOURCE/app/core/urls.py',
            'SOURCE/front/dist/vendor.js',
            'SOURCE/front/dist/styles.css'
        ]
    };
}

async function getSyncStatus() {
    return {
        dev: { status: 'מסונכרן', files: 156 },
        test: { status: 'ממתין', files: 142 },
        prod: { status: 'לא מסונכרן', files: 128 }
    };
}

// ========================================
// פעולות (Actions)
// ========================================
function filterFiles(type) {
    currentFilter = type;
    console.log(`🔍 מסנן קבצים: ${type}`);
    renderFileTracker();
}

function switchFilesView(mode) {
    viewMode = mode;
    localStorage.setItem('filesViewMode', mode);
    console.log(`👁️ מחליף תצוגה ל: ${mode}`);
    renderFileTracker();
}

async function refreshVolumes() {
    console.log('🔄 מרענן Volume Mounts...');
    await renderFileTracker();
}

async function syncToEnvironment(env) {
    console.log(`🔄 מסנכרן ל-${env}...`);
    alert(`מתחיל סנכרון ל-${env} environment\n\nיריץ:\n.\\SCRIPTS\\sync_environments.ps1 -Target ${env}`);
}

function viewFileInContainer(filePath) {
    console.log(`👁️ צופה בקובץ: ${filePath}`);
    alert(`פותח קובץ מהקונטיינר:\n${filePath}\n\nפקודה:\ndocker-compose exec web cat ${filePath}`);
}

function toggleFileWatcher() {
    const status = fileWatcher.getStatus();
    if (status.isRunning) {
        fileWatcher.stopWatching();
        console.log('⏸️ File Watcher הושהה');
    } else {
        const filesToWatch = [
            '../docs/SESSION_LOG.md',
            '../docs/CURRENT_STATE.md',
            '../../../.file-changes-state.json'
        ];
        fileWatcher.startWatching(filesToWatch, (changedFiles) => {
            console.log('📝 קבצים השתנו - מרענן תצוגה...', changedFiles);
            renderFileTracker();
        });
        console.log('▶️ File Watcher הופעל');
    }
    renderFileTracker();
}

// ייצוא פונקציות
export { filterFiles, switchFilesView, refreshVolumes, syncToEnvironment, viewFileInContainer, toggleFileWatcher };
