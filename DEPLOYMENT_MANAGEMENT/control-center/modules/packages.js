/**
 * 📦 Packages & Mappings Module
 * 
 * מציג:
 * - רישום חבילות (Packages Registry)
 * - מבנה תיקיות (Directory Structure)
 * - נקודות אינטגרציה (Integration Points)
 * - מפת תלויות (Dependencies Map)
 * 
 * @version 1.0
 * @date 2025-11-14
 */

export function init() {
    console.log('📦 Packages & Mappings module initialized');
    
    // טען נתונים ראשוניים
    loadMappingsData();
}

export async function render(container) {
    console.log('📦 Rendering Packages & Mappings...');
    
    container.innerHTML = `
        <div class="packages-container">
            <header class="packages-header">
                <h1>📦 מערכת ניהול חבילות ומיפויים</h1>
                <p class="subtitle">ניהול, מעקב ותכנון של כל רכיבי הפרויקט</p>
            </header>

            <!-- Navigation Tabs -->
            <nav class="mappings-tabs">
                <button class="tab-btn active" data-tab="packages">
                    📦 רישום חבילות
                </button>
                <button class="tab-btn" data-tab="structure">
                    🗂️ מבנה תיקיות
                </button>
                <button class="tab-btn" data-tab="integration">
                    🔗 נקודות אינטגרציה
                </button>
                <button class="tab-btn" data-tab="dependencies">
                    🕸️ מפת תלויות
                </button>
            </nav>

            <!-- Tab Contents -->
            <div class="tab-content active" id="packages-tab">
                <div class="loading">טוען נתונים...</div>
            </div>

            <div class="tab-content" id="structure-tab">
                <div class="loading">טוען נתונים...</div>
            </div>

            <div class="tab-content" id="integration-tab">
                <div class="loading">טוען נתונים...</div>
            </div>

            <div class="tab-content" id="dependencies-tab">
                <div class="loading">טוען נתונים...</div>
            </div>
        </div>
    `;

    // הוסף סגנונות
    injectStyles();
    
    // הפעל tabs
    setupTabs();
    
    // טען תוכן של tab הראשון
    await loadPackagesTab();
}

function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .packages-container {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .packages-header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }

        .packages-header h1 {
            margin: 0 0 10px 0;
            font-size: 2em;
        }

        .packages-header .subtitle {
            margin: 0;
            opacity: 0.9;
            font-size: 1.1em;
        }

        .mappings-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }

        .tab-btn {
            padding: 12px 24px;
            border: none;
            background: #f5f5f5;
            color: #333;
            cursor: pointer;
            border-radius: 8px 8px 0 0;
            font-size: 1em;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .tab-btn:hover {
            background: #e0e0e0;
            transform: translateY(-2px);
        }

        .tab-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.3s ease;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.1em;
        }

        .packages-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .package-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }

        .package-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }

        .package-card h3 {
            margin: 0 0 10px 0;
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .package-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .status-active {
            background: #4caf50;
            color: white;
        }

        .status-dev {
            background: #ff9800;
            color: white;
        }

        .status-planned {
            background: #2196f3;
            color: white;
        }

        .package-info {
            margin-top: 15px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .info-row:last-child {
            border-bottom: none;
        }

        .info-label {
            font-weight: 600;
            color: #666;
        }

        .info-value {
            color: #333;
        }

        .directory-tree {
            background: #f9f9f9;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.6;
            overflow-x: auto;
        }

        .directory-tree .folder {
            color: #2196f3;
            font-weight: 600;
        }

        .directory-tree .file {
            color: #666;
        }

        .integration-diagram {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 30px;
            margin: 20px 0;
        }

        .integration-flow {
            display: flex;
            flex-direction: column;
            gap: 20px;
            align-items: center;
        }

        .flow-item {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            min-width: 250px;
        }

        .flow-arrow {
            font-size: 2em;
            color: #667eea;
        }

        .dependencies-graph {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 30px;
            min-height: 400px;
        }

        .stats-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }

        .stats-number {
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }

        .stats-label {
            color: #666;
            font-size: 1.1em;
        }

        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transform: translateY(-2px);
        }

        .btn-secondary {
            background: #f5f5f5;
            color: #333;
        }

        .btn-secondary:hover {
            background: #e0e0e0;
        }
    `;
    document.head.appendChild(style);
}

function setupTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // הסר active מכולם
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            // הוסף active לנלחץ
            tab.classList.add('active');
            const tabName = tab.dataset.tab;
            const content = document.getElementById(`${tabName}-tab`);
            if (content) {
                content.classList.add('active');
                
                // טען תוכן אם עוד לא נטען
                loadTabContent(tabName);
            }
        });
    });
}

async function loadMappingsData() {
    console.log('📦 Loading mappings data...');
    // TODO: טען נתונים מקבצי MD או מ-API
}

async function loadPackagesTab() {
    const container = document.getElementById('packages-tab');
    
    try {
        // כרגע נתונים מוקשחים - בעתיד נטען מ-API
        const packages = [
            {
                name: 'eScriptorium Base',
                version: '0.13.x',
                domain: 'CORE',
                status: 'active',
                purpose: 'מערכת ליבת eScriptorium המקורית',
                dependencies: ['Django 4.2+', 'PostgreSQL 13+', 'Redis 7+']
            },
            {
                name: 'BiblIA Extensions',
                version: 'TBD',
                domain: 'CORE',
                status: 'planned',
                purpose: 'הרחבות עבריות ל-eScriptorium',
                dependencies: ['eScriptorium Base', 'Hebrew NLP']
            },
            {
                name: 'Docker Compose Setup',
                version: '3.8',
                domain: 'DEPLOYMENT',
                status: 'active',
                purpose: 'תצורת Docker containers',
                dependencies: ['Docker Engine 20+', 'Docker Compose 2+']
            }
        ];

        const packagesHTML = `
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="window.packagesModule.addPackage()">
                    ➕ הוסף חבילה חדשה
                </button>
                <button class="btn btn-secondary" onclick="window.packagesModule.exportData()">
                    📥 ייצא נתונים
                </button>
                <button class="btn btn-secondary" onclick="window.packagesModule.refreshData()">
                    🔄 רענן
                </button>
            </div>

            <div class="stats-row" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
                <div class="stats-card">
                    <div class="stats-number">${packages.length}</div>
                    <div class="stats-label">סה"כ חבילות</div>
                </div>
                <div class="stats-card">
                    <div class="stats-number">${packages.filter(p => p.status === 'active').length}</div>
                    <div class="stats-label">פעילות</div>
                </div>
                <div class="stats-card">
                    <div class="stats-number">${packages.filter(p => p.status === 'planned').length}</div>
                    <div class="stats-label">מתוכננות</div>
                </div>
            </div>

            <div class="packages-grid">
                ${packages.map(pkg => `
                    <div class="package-card">
                        <h3>
                            ${pkg.name}
                            <span class="package-status status-${pkg.status}">
                                ${getStatusText(pkg.status)}
                            </span>
                        </h3>
                        <div class="package-info">
                            <div class="info-row">
                                <span class="info-label">גרסה:</span>
                                <span class="info-value">${pkg.version}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">דומיין:</span>
                                <span class="info-value">${pkg.domain}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">מטרה:</span>
                                <span class="info-value">${pkg.purpose}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">תלויות:</span>
                                <span class="info-value">${pkg.dependencies.length} חבילות</span>
                            </div>
                        </div>
                        <div class="action-buttons" style="margin-top: 15px;">
                            <button class="btn btn-secondary" style="flex: 1; font-size: 0.9em;" onclick="window.packagesModule.viewDetails('${pkg.name}')">
                                📋 פרטים
                            </button>
                            <button class="btn btn-secondary" style="flex: 1; font-size: 0.9em;" onclick="window.packagesModule.editPackage('${pkg.name}')">
                                ✏️ ערוך
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        container.innerHTML = packagesHTML;

    } catch (error) {
        console.error('Error loading packages:', error);
        container.innerHTML = `<div class="error">❌ שגיאה בטעינת נתונים: ${error.message}</div>`;
    }
}

async function loadTabContent(tabName) {
    const container = document.getElementById(`${tabName}-tab`);
    
    // אם כבר טענו, אל תטען שוב
    if (container.innerHTML !== '<div class="loading">טוען נתונים...</div>') {
        return;
    }

    switch(tabName) {
        case 'packages':
            await loadPackagesTab();
            break;
        case 'structure':
            await loadStructureTab(container);
            break;
        case 'integration':
            await loadIntegrationTab(container);
            break;
        case 'dependencies':
            await loadDependenciesTab(container);
            break;
    }
}

async function loadStructureTab(container) {
    container.innerHTML = `
        <div class="directory-tree">
            <div style="margin-bottom: 20px;">
                <h3>🗂️ מבנה תיקיות הפרויקט</h3>
            </div>
            <pre>
escriptorium/
│
├── <span class="folder">📦 CORE/</span>
│   ├── <span class="folder">eScriptorium_UNIFIED/</span>     ← גרסת עבודה ראשית
│   ├── <span class="folder">eScriptorium_CLEAN/</span>       ← גרסת reference
│   └── <span class="file">README.md</span>
│
├── <span class="folder">🏗️ BUILD_MANAGEMENT/</span>
│   ├── <span class="folder">ci-cd/</span>                    ← GitHub Actions
│   ├── <span class="folder">testing/</span>                  ← Test suites
│   ├── <span class="folder">quality/</span>                  ← Code quality
│   ├── <span class="folder">versioning/</span>               ← Releases
│   ├── <span class="folder">documentation/</span>            ← Dev guides
│   └── <span class="folder">tools/</span>                    ← Build utilities
│
└── <span class="folder">🚢 DEPLOYMENT_MANAGEMENT/</span>
    ├── <span class="folder">docker/</span>                   ← Docker configs
    ├── <span class="folder">control-center/</span>           ← ⭐ אתה כאן!
    │   ├── <span class="folder">.instructions/</span>        ← AI chatbot instructions
    │   ├── <span class="folder">mappings/</span>             ← 📦 מיפויים
    │   ├── <span class="folder">modules/</span>              ← Dashboard modules
    │   ├── <span class="folder">servers/</span>              ← HTTP/Terminal servers
    │   ├── <span class="folder">scripts/</span>              ← Automation scripts
    │   └── <span class="folder">docs/</span>                 ← Documentation
    ├── <span class="folder">monitoring/</span>               ← Health checks
    ├── <span class="folder">scripts/</span>                  ← Deploy scripts
    └── <span class="folder">environments/</span>             ← Dev/test/prod
            </pre>
        </div>

        <div class="action-buttons">
            <button class="btn btn-primary" onclick="window.packagesModule.viewFullStructure()">
                📂 צפה במבנה מלא
            </button>
            <button class="btn btn-secondary" onclick="window.packagesModule.exportStructure()">
                📥 ייצא מבנה
            </button>
        </div>
    `;
}

async function loadIntegrationTab(container) {
    container.innerHTML = `
        <div class="integration-diagram">
            <h3 style="text-align: center; margin-bottom: 30px;">🔗 מפת אינטגרציה</h3>
            <div class="integration-flow">
                <div class="flow-item">👤 User / Developer</div>
                <div class="flow-arrow">↓</div>
                <div class="flow-item">🚢 DEPLOYMENT_MANAGEMENT<br>(Control Center)</div>
                <div class="flow-arrow">↓</div>
                <div class="flow-item">🏗️ BUILD_MANAGEMENT<br>(CI/CD, Testing)</div>
                <div class="flow-arrow">↓</div>
                <div class="flow-item">📦 CORE<br>(eScriptorium Application)</div>
                <div class="flow-arrow">↓</div>
                <div style="display: flex; gap: 20px;">
                    <div class="flow-item" style="min-width: 150px;">Django Backend</div>
                    <div class="flow-item" style="min-width: 150px;">Vue.js Frontend</div>
                    <div class="flow-item" style="min-width: 150px;">PostgreSQL DB</div>
                </div>
            </div>
        </div>

        <div class="action-buttons">
            <button class="btn btn-primary" onclick="window.packagesModule.viewIntegrationDetails()">
                📋 פרטי אינטגרציה מלאים
            </button>
            <button class="btn btn-secondary" onclick="window.packagesModule.testIntegrations()">
                🧪 בדוק אינטגרציות
            </button>
        </div>
    `;
}

async function loadDependenciesTab(container) {
    container.innerHTML = `
        <div class="dependencies-graph">
            <h3 style="text-align: center; margin-bottom: 30px;">🕸️ גרף תלויות</h3>
            <p style="text-align: center; color: #666;">
                גרף אינטראקטיבי יוצג כאן בקרוב...<br>
                (נדרש D3.js לויזואליזציה)
            </p>
            
            <div style="margin-top: 30px;">
                <h4>תלויות קריטיות:</h4>
                <ul style="list-style-position: inside;">
                    <li>CORE → Django 4.2+</li>
                    <li>CORE → PostgreSQL 13+</li>
                    <li>CORE → Redis 7+</li>
                    <li>BUILD → CORE (read-only)</li>
                    <li>DEPLOYMENT → BUILD (artifacts)</li>
                    <li>Control Center → Node.js 18+</li>
                </ul>
            </div>
        </div>

        <div class="action-buttons">
            <button class="btn btn-primary" onclick="window.packagesModule.analyzeDependencies()">
                🔍 נתח תלויות
            </button>
            <button class="btn btn-secondary" onclick="window.packagesModule.checkCircular()">
                🔄 בדוק תלויות מעגליות
            </button>
        </div>
    `;
}

function getStatusText(status) {
    const statusMap = {
        'active': '✅ פעיל',
        'dev': '🚧 בפיתוח',
        'planned': '🔄 מתוכנן'
    };
    return statusMap[status] || status;
}

// פונקציות ציבוריות (API)
window.packagesModule = {
    addPackage: () => alert('📦 הוספת חבילה חדשה - בפיתוח'),
    editPackage: (name) => alert(`✏️ עריכת חבילה: ${name} - בפיתוח`),
    viewDetails: (name) => alert(`📋 פרטי חבילה: ${name} - בפיתוח`),
    exportData: () => alert('📥 ייצוא נתונים - בפיתוח'),
    refreshData: async () => {
        await loadPackagesTab();
        alert('🔄 הנתונים רוענו');
    },
    viewFullStructure: () => alert('📂 מבנה מלא - יוצג בחלון נפרד'),
    exportStructure: () => alert('📥 ייצוא מבנה - בפיתוח'),
    viewIntegrationDetails: () => alert('📋 פרטי אינטגרציה - בפיתוח'),
    testIntegrations: () => alert('🧪 בדיקת אינטגרציות - בפיתוח'),
    analyzeDependencies: () => alert('🔍 ניתוח תלויות - בפיתוח'),
    checkCircular: () => alert('🔄 בדיקת תלויות מעגליות - בפיתוח')
};

export function cleanup() {
    console.log('📦 Packages & Mappings module cleaned up');
    delete window.packagesModule;
}
