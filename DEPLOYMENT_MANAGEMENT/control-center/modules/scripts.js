/**
 * Scripts Module - ספריית תסריטים (Scripts Library)
 * הרצת scripts ישירות מהממשק
 */

// Import Terminal Configuration
import terminalConfig from './terminal-config.js';

/**
 * Initialize Scripts Module
 */
export function init() {
    console.log('📜 Scripts Module initialized');
    loadScriptsView();
    loadScripts();
}

/**
 * Load Scripts View HTML
 */
function loadScriptsView() {
    const container = document.getElementById('scripts-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="scripts-library">
            <div class="scripts-header">
                <h2>ספריית תסריטים (Scripts Library)</h2>
                <p class="subtitle">הרצת scripts ישירות מהממשק</p>
            </div>
            
            <!-- Script Categories -->
            <div class="script-categories">
                <button class="category-btn active" onclick="window.scriptsModule.filterCategory('all')">
                    📋 הכל (All)
                </button>
                <button class="category-btn" onclick="window.scriptsModule.filterCategory('setup')">
                    🔧 Setup
                </button>
                <button class="category-btn" onclick="window.scriptsModule.filterCategory('build')">
                    🔨 Build
                </button>
                <button class="category-btn" onclick="window.scriptsModule.filterCategory('deploy')">
                    🚀 Deploy
                </button>
                <button class="category-btn" onclick="window.scriptsModule.filterCategory('maintenance')">
                    ⚙️ Maintenance
                </button>
            </div>
            
            <!-- Scripts Grid -->
            <div class="scripts-grid" id="scripts-grid">
                <div class="loading">טוען תסריטים...</div>
            </div>
            
            <!-- Execution Output -->
            <div class="script-output" id="script-output" style="display: none;">
                <div class="output-header">
                    <h3>פלט תסריט (Script Output)</h3>
                    <button class="btn btn-sm btn-secondary" onclick="window.scriptsModule.closeOutput()">
                        ✖️ סגור
                    </button>
                </div>
                <div class="output-log" id="output-log"></div>
            </div>
        </div>
        
        <style>
            .scripts-library { padding: 20px; }
            .scripts-header { margin-bottom: 30px; }
            .scripts-header h2 { color: #2c3e50; margin-bottom: 10px; }
            
            .script-categories {
                display: flex;
                gap: 10px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }
            
            .category-btn {
                padding: 10px 20px;
                border: 2px solid #ecf0f1;
                background: white;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: bold;
            }
            
            .category-btn:hover {
                background: #f8f9fa;
            }
            
            .category-btn.active {
                background: #3498db;
                color: white;
                border-color: #3498db;
            }
            
            .scripts-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: 20px;
            }
            
            .script-card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border-top: 4px solid #3498db;
            }
            
            .script-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .script-card.setup { border-top-color: #2ecc71; }
            .script-card.build { border-top-color: #f39c12; }
            .script-card.deploy { border-top-color: #e74c3c; }
            .script-card.maintenance { border-top-color: #9b59b6; }
            
            .script-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 10px;
            }
            
            .script-icon {
                font-size: 24px;
            }
            
            .script-name {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                font-family: 'Courier New', monospace;
            }
            
            .script-description {
                color: #2c3e50;
                font-size: 14px;
                margin-bottom: 10px;
                line-height: 1.6;
                font-weight: 600;
            }
            
            .script-details {
                color: #7f8c8d;
                font-size: 13px;
                margin-bottom: 10px;
                line-height: 1.5;
                font-style: italic;
            }
            
            .script-path {
                font-size: 12px;
                color: #95a5a6;
                font-family: 'Courier New', monospace;
                margin-bottom: 15px;
                word-break: break-all;
            }
            
            .script-params {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                border: 1px solid #e9ecef;
            }
            
            .params-form {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .param-row {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            
            .param-row label {
                font-weight: 600;
                color: #495057;
                font-size: 13px;
            }
            
            .param-input {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 13px;
            }
            
            .param-input:focus {
                outline: none;
                border-color: #3498db;
            }
            
            .param-desc {
                font-size: 12px;
                color: #6c757d;
                margin-right: 8px;
            }
            
            .script-actions {
                display: flex;
                gap: 10px;
            }
            
            .script-output {
                background: white;
                border-radius: 12px;
                padding: 25px;
                margin-top: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .output-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            
            .output-header h3 {
                color: #2c3e50;
                margin: 0;
            }
            
            .output-log {
                background: #2c3e50;
                color: #ecf0f1;
                padding: 20px;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                max-height: 400px;
                overflow-y: auto;
                direction: ltr;
                text-align: left;
                white-space: pre-wrap;
            }
        </style>
    `;
}

/**
 * Load Scripts
 */
function loadScripts() {
    const scriptsData = [
        // ═══════════════════════════════════════════════════════════
        // 🏥 Health & Pre-Flight Checks
        // ═══════════════════════════════════════════════════════════
        {
            name: 'health_check.ps1',
            category: 'setup',
            icon: '🏥',
            description: 'בדיקת בריאות מוקדמת - לפני העלאה לדוקר',
            details: 'בודק: כלים חיצוניים, קבצים חיוניים, תצורת Docker, מבנה תיקיות, משאבי מערכת',
            path: '.\\SCRIPTS\\health_check.ps1',
            params: [
                { name: 'Environment', type: 'select', options: ['dev', 'test', 'prod'], default: 'dev' },
                { name: 'Detailed', type: 'checkbox', description: 'פירוט מלא' },
                { name: 'ExportJson', type: 'checkbox', description: 'ייצוא לJSON' }
            ]
        },
        {
            name: 'validate_files.ps1',
            category: 'setup',
            icon: '🔍',
            description: 'בדיקת קבצים ותיקון אוטומטי',
            details: 'בודק שכל הקבצים קיימים (requirements.txt, package.json, etc.) ומעתיק מקוד מקור אם חסרים!',
            path: '.\\SCRIPTS\\validate_files.ps1',
            params: [
                { name: 'Environment', type: 'select', options: ['dev', 'test', 'prod', 'all'], default: 'dev' },
                { name: 'AutoFix', type: 'checkbox', description: '🔧 תקן אוטומטית (העתק קבצים חסרים)' },
                { name: 'Detailed', type: 'checkbox', description: 'פירוט מלא + גודל קבצים' }
            ]
        },
        
        // ═══════════════════════════════════════════════════════════
        // 🔄 Sync & Watch
        // ═══════════════════════════════════════════════════════════
        {
            name: 'sync_environments.ps1',
            category: 'setup',
            icon: '🔄',
            description: 'סנכרון SOURCE/ → ENVIRONMENTS/',
            details: 'מעתיק קבצים ששונו מ-SOURCE/ לסביבות (dev/test/prod) עם MD5 hash comparison',
            path: '.\\SCRIPTS\\sync_environments.ps1',
            params: [
                { name: 'Target', type: 'select', options: ['dev', 'test', 'prod', 'all'], default: 'dev' },
                { name: 'Force', type: 'checkbox', description: 'אלץ העתקה (התעלם מ-hash)' },
                { name: 'DryRun', type: 'checkbox', description: 'תצוגה מקדימה (לא מעתיק)' },
                { name: 'Verbose', type: 'checkbox', description: 'פירוט מלא' }
            ]
        },
        {
            name: 'watch_source_files.ps1',
            category: 'setup',
            icon: '👀',
            description: 'מעקב אוטומטי אחר שינויים ב-SOURCE/',
            details: 'רץ ברקע ומסנכרן אוטומטית כשקובץ משתנה - hot-reload לקונטיינרים!',
            path: '.\\SCRIPTS\\watch_source_files.ps1',
            params: [
                { name: 'IntervalSeconds', type: 'number', default: 2, description: 'מרווח בדיקה (שניות)' },
                { name: 'Once', type: 'checkbox', description: 'בדיקה חד-פעמית (לא מעקב רציף)' },
                { name: 'Verbose', type: 'checkbox', description: 'פירוט מלא' }
            ]
        },
        
        // ═══════════════════════════════════════════════════════════
        // 🐳 Docker Operations
        // ═══════════════════════════════════════════════════════════
        {
            name: 'rebuild_container.ps1',
            category: 'build',
            icon: '🔨',
            description: 'Rebuild מהיר של קונטיינר',
            details: 'Stop → Build (--no-cache optional) → Up -d → Health Check',
            path: '.\\SCRIPTS\\rebuild_container.ps1',
            params: [
                { name: 'Container', type: 'select', options: ['web', 'nginx', 'postgres', 'redis', 'all'], default: 'web' },
                { name: 'Environment', type: 'select', options: ['dev', 'test', 'prod'], default: 'dev' },
                { name: 'NoCache', type: 'checkbox', description: 'Build ללא cache (איטי אבל נקי)' },
                { name: 'PullImages', type: 'checkbox', description: 'Pull images עדכניים' }
            ]
        },
        {
            name: 'view_logs.ps1',
            category: 'maintenance',
            icon: '📋',
            description: 'צפייה בלוגי קונטיינרים',
            details: 'לוגים מרוכזים עם סינון לפי רמת חומרה (error/warning/info) וצבעים',
            path: '.\\SCRIPTS\\view_logs.ps1',
            params: [
                { name: 'Container', type: 'select', options: ['web', 'nginx', 'postgres', 'redis', 'all'], default: 'web' },
                { name: 'Tail', type: 'number', default: 100, description: 'מספר שורות אחרונות' },
                { name: 'Follow', type: 'checkbox', description: 'מעקב חי (tail -f)' },
                { name: 'Level', type: 'select', options: ['all', 'error', 'warning', 'info'], default: 'all', description: 'סינון לפי רמה' },
                { name: 'Search', type: 'text', description: 'חיפוש טקסט ספציפי' }
            ]
        },
        
        // ═══════════════════════════════════════════════════════════
        // 🚀 Deploy Scripts (הסקריפטים הקיימים)
        // ═══════════════════════════════════════════════════════════
        {
            name: 'build-and-deploy.ps1',
            category: 'build',
            icon: '🏗️',
            description: 'בנייה ופריסה מלאה של המערכת',
            details: 'Quick/Full modes - build frontend + deploy to Docker',
            path: '.\\escriptorium\\scripts\\build\\build-and-deploy.ps1 -Quick'
        },
        {
            name: 'deploy-dev.ps1',
            category: 'deploy',
            icon: '🚀',
            description: 'פריסה לסביבת Development',
            path: '.\\escriptorium\\scripts\\deploy\\deploy-dev.ps1'
        },
        {
            name: 'deploy-test.ps1',
            category: 'deploy',
            icon: '🧪',
            description: 'פריסה לסביבת Testing',
            path: '.\\escriptorium\\scripts\\deploy\\deploy-test.ps1'
        },
        {
            name: 'deploy-prod.ps1',
            category: 'deploy',
            icon: '⚠️',
            description: 'פריסה לסביבת Production (זהירות!)',
            path: '.\\escriptorium\\scripts\\deploy\\deploy-prod.ps1'
        },
        {
            name: 'restart-services.ps1',
            category: 'maintenance',
            icon: '🔄',
            description: 'אתחול שירותי Docker (web + nginx)',
            path: '.\\escriptorium\\scripts\\maintenance\\restart-services.ps1'
        },
        {
            name: 'verify-deployment.ps1',
            category: 'maintenance',
            icon: '✅',
            description: 'בדיקת תקינות הפריסה',
            path: '.\\escriptorium\\scripts\\maintenance\\verify-deployment.ps1'
        },
        {
            name: 'compile-translations.ps1',
            category: 'build',
            icon: '🌐',
            description: 'קומפילציה של תרגומים עבריים',
            path: '.\\escriptorium\\scripts\\build\\compile-translations.ps1 -Language he'
        },
        {
            name: 'run-all.ps1',
            category: 'setup',
            icon: '⚡',
            description: 'הרצה מלאה - diagnostics + build + test',
            path: '.\\escriptorium\\scripts\\run-all.ps1'
        }
    ];
    
    renderScriptsGrid(scriptsData);
}

/**
 * Render Scripts Grid
 */
function renderScriptsGrid(scripts) {
    const grid = document.getElementById('scripts-grid');
    if (!grid) return;
    
    let html = '';
    scripts.forEach((script, index) => {
        const icon = script.icon || '📜';
        const details = script.details || '';
        const hasParams = script.params && script.params.length > 0;
        
        html += `
            <div class="script-card ${script.category}" data-category="${script.category}" data-index="${index}">
                <div class="script-header">
                    <span class="script-icon">${icon}</span>
                    <div class="script-name">${script.name}</div>
                </div>
                <div class="script-description">${script.description}</div>
                ${details ? `<div class="script-details">${details}</div>` : ''}
                <div class="script-path">${script.path}</div>
                
                ${hasParams ? `
                    <div class="script-params" id="params-${index}" style="display: none;">
                        ${renderParams(script.params, index)}
                    </div>
                ` : ''}
                
                <div class="script-actions">
                    ${hasParams ? `
                        <button class="btn btn-info btn-sm" onclick="window.scriptsModule.toggleParams(${index})">
                            ⚙️ פרמטרים
                        </button>
                    ` : ''}
                    <button class="btn btn-primary btn-sm" onclick="window.scriptsModule.runScriptWithIndex(${index})">
                        ▶️ הרץ
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="window.scriptsModule.copyCommand('${script.path}')">
                        📋 העתק
                    </button>
                </div>
            </div>
        `;
    });
    
    grid.innerHTML = html;
    
    // Store scripts data globally
    window._scriptsData = scripts;
}

/**
 * Render Parameters Form
 */
function renderParams(params, scriptIndex) {
    let html = '<div class="params-form">';
    
    params.forEach((param, paramIndex) => {
        const inputId = `param-${scriptIndex}-${paramIndex}`;
        
        html += `<div class="param-row">`;
        html += `<label for="${inputId}">${param.name}:</label>`;
        
        switch (param.type) {
            case 'select':
                html += `<select id="${inputId}" class="param-input">`;
                param.options.forEach(opt => {
                    const selected = opt === param.default ? 'selected' : '';
                    html += `<option value="${opt}" ${selected}>${opt}</option>`;
                });
                html += `</select>`;
                break;
                
            case 'checkbox':
                const desc = param.description ? `<span class="param-desc">${param.description}</span>` : '';
                html += `<input type="checkbox" id="${inputId}" class="param-input">`;
                html += desc;
                break;
                
            case 'number':
                html += `<input type="number" id="${inputId}" class="param-input" value="${param.default || ''}" placeholder="${param.description || ''}">`;
                break;
                
            case 'text':
                html += `<input type="text" id="${inputId}" class="param-input" placeholder="${param.description || ''}">`;
                break;
        }
        
        html += `</div>`;
    });
    
    html += '</div>';
    return html;
}


/**
 * Toggle Parameters Visibility
 */
function toggleParams(scriptIndex) {
    const paramsDiv = document.getElementById(`params-${scriptIndex}`);
    if (paramsDiv) {
        paramsDiv.style.display = paramsDiv.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Run Script with Parameters
 */
function runScriptWithIndex(scriptIndex) {
    const script = window._scriptsData[scriptIndex];
    if (!script) return;
    
    let command = script.path;
    
    // Collect parameters
    if (script.params && script.params.length > 0) {
        const params = [];
        script.params.forEach((param, paramIndex) => {
            const inputId = `param-${scriptIndex}-${paramIndex}`;
            const input = document.getElementById(inputId);
            
            if (!input) return;
            
            if (param.type === 'checkbox') {
                if (input.checked) {
                    params.push(`-${param.name}`);
                }
            } else if (param.type === 'select' || param.type === 'text' || param.type === 'number') {
                const value = input.value;
                if (value) {
                    params.push(`-${param.name} ${value}`);
                }
            }
        });
        
        if (params.length > 0) {
            command += ' ' + params.join(' ');
        }
    }
    
    runScript(command, script.name);
}

/**
 * Filter by Category
 */
function filterCategory(category) {
    // Update active button
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Filter scripts
    const scriptCards = document.querySelectorAll('.script-card');
    scriptCards.forEach(card => {
        if (category === 'all' || card.dataset.category === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/**
 * Run Script via Terminal
 */
async function runScript(scriptPath, scriptName) {
    console.log(`▶️ Running script: ${scriptPath}`);
    
    const outputSection = document.getElementById('script-output');
    const outputLog = document.getElementById('output-log');
    
    outputSection.style.display = 'block';
    outputLog.textContent = `[${new Date().toLocaleTimeString('he-IL')}] מריץ: ${scriptName}\n\n`;
    
    try {
        const result = await terminalConfig.executeCommand(scriptPath);
        
        if (result.output) {
            outputLog.textContent += result.output;
        }
        
        if (result.error) {
            outputLog.textContent += '\n\n⚠️ Errors:\n' + result.error;
        }
        
        outputLog.textContent += '\n\n✅ הושלם!';
        
    } catch (error) {
        console.error('Script execution error:', error);
        outputLog.textContent += `\n\n❌ שגיאה: ${error.message}`;
    }
}

/**
 * Copy Command to Clipboard
 */
function copyCommand(command) {
    navigator.clipboard.writeText(command).then(() => {
        alert(`✅ הועתק ללוח:\n${command}`);
    }).catch(err => {
        console.error('Copy failed:', err);
        alert('❌ שגיאה בהעתקה');
    });
}

/**
 * Close Output Section
 */
function closeOutput() {
    const outputSection = document.getElementById('script-output');
    outputSection.style.display = 'none';
}

/**
 * Export
 */
window.scriptsModule = {
    filterCategory,
    runScript,
    runScriptWithIndex,
    toggleParams,
    copyCommand,
    closeOutput
};
