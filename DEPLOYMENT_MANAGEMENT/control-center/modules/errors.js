/**
 * Errors Module - רישום שגיאות (Error Registry)
 * ניהול error codes עם auto-fix
 */

// Import Terminal Configuration
import terminalConfig from './terminal-config.js';

/**
 * Initialize Errors Module
 */
export function init() {
    console.log('⚠️ Errors Module initialized');
    loadErrorsView();
    loadErrorCodes();
}

/**
 * Load Errors View HTML
 */
function loadErrorsView() {
    const container = document.getElementById('errors-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="errors-manager">
            <div class="errors-header">
                <h2>רישום שגיאות (Error Registry)</h2>
                <p class="subtitle">מעקב ותיקון שגיאות ידועות</p>
            </div>
            
            <!-- Error Categories -->
            <div class="error-categories">
                <button class="category-btn active" onclick="window.errorsModule.filterByCategory('all')">
                    📋 הכל (All)
                </button>
                <button class="category-btn" onclick="window.errorsModule.filterByCategory('docker')">
                    🐳 Docker
                </button>
                <button class="category-btn" onclick="window.errorsModule.filterByCategory('build')">
                    🔨 Build
                </button>
                <button class="category-btn" onclick="window.errorsModule.filterByCategory('deploy')">
                    🚀 Deploy
                </button>
                <button class="category-btn" onclick="window.errorsModule.filterByCategory('database')">
                    🗄️ Database
                </button>
                <button class="category-btn" onclick="window.errorsModule.filterByCategory('network')">
                    🌐 Network
                </button>
                <button class="category-btn" onclick="window.errorsModule.filterByCategory('config')">
                    ⚙️ Config
                </button>
                <button class="category-btn" onclick="window.errorsModule.filterByCategory('system')">
                    💻 System
                </button>
            </div>
            
            <!-- Search Box -->
            <div class="error-search">
                <input type="text" id="error-search-input" placeholder="חיפוש שגיאה..." 
                       oninput="window.errorsModule.searchErrors()">
            </div>
            
            <!-- Errors Table -->
            <div class="errors-table" id="errors-table">
                <div class="loading">טוען שגיאות...</div>
            </div>
        </div>
        
        <style>
            .errors-manager { padding: 20px; }
            .errors-header { margin-bottom: 30px; }
            .errors-header h2 { color: #2c3e50; margin-bottom: 10px; }
            
            .error-categories {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
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
                background: #e74c3c;
                color: white;
                border-color: #e74c3c;
            }
            
            .error-search {
                margin-bottom: 20px;
            }
            
            .error-search input {
                width: 100%;
                padding: 12px;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                font-size: 14px;
            }
            
            .errors-table {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .error-item {
                padding: 20px;
                border-right: 4px solid #e74c3c;
                background: #f8f9fa;
                margin-bottom: 15px;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .error-item:hover {
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transform: translateX(-5px);
            }
            
            .error-header-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .error-code {
                font-size: 16px;
                font-weight: bold;
                color: #e74c3c;
                font-family: 'Courier New', monospace;
            }
            
            .error-category {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
                background: #3498db;
                color: white;
            }
            
            .error-description {
                color: #2c3e50;
                margin-bottom: 15px;
                line-height: 1.6;
            }
            
            .error-actions {
                display: flex;
                gap: 10px;
            }
            
            .error-item.docker { border-right-color: #3498db; }
            .error-item.build { border-right-color: #f39c12; }
            .error-item.deploy { border-right-color: #e74c3c; }
            .error-item.database { border-right-color: #9b59b6; }
            .error-item.network { border-right-color: #16a085; }
            .error-item.config { border-right-color: #d35400; }
            .error-item.system { border-right-color: #7f8c8d; }
            
            .has-autofix::after {
                content: "🔧 Auto-Fix";
                display: inline-block;
                margin-right: 10px;
                padding: 2px 8px;
                background: #2ecc71;
                color: white;
                border-radius: 4px;
                font-size: 11px;
            }
        </style>
    `;
}

/**
 * Load Error Codes from JSON
 */
async function loadErrorCodes() {
    try {
        const response = await fetch('../data/error-codes-registry.json?' + Date.now());
        const data = await response.json();
        
        // Convert JSON format to display format
        const errorCodes = data.errors.map(error => ({
            code: error.code,
            category: error.category,
            title: error.title,
            description: error.description,
            solution: error.solution,
            autoFix: error.autoFixAvailable || false,
            autoFixCommand: error.autoFixCommand || '',
            severity: error.severity,
            symptoms: error.symptoms || [],
            documentation: error.documentation || ''
        }));
        
        renderErrorTable(errorCodes);
        
    } catch (error) {
        console.error('Failed to load error codes:', error);
        document.getElementById('errors-table').innerHTML = `
            <div style="text-align: center; color: #e74c3c; padding: 40px;">
                ❌ שגיאה בטעינת error codes<br>
                <small>${error.message}</small>
            </div>
        `;
    }
}

/**
 * Render Error Table
 */
function renderErrorTable(errors) {
    const table = document.getElementById('errors-table');
    if (!table) return;
    
    if (errors.length === 0) {
        table.innerHTML = '<div style="text-align: center; color: #95a5a6; padding: 40px;">אין שגיאות להצגה ✅</div>';
        return;
    }
    
    let html = '';
    errors.forEach(error => {
        const autofixClass = error.autoFix ? 'has-autofix' : '';
        const severityColor = error.severity === 'critical' ? '#c0392b' : 
                             error.severity === 'high' ? '#e74c3c' : 
                             error.severity === 'medium' ? '#f39c12' : '#3498db';
        
        html += `
            <div class="error-item ${error.category} ${autofixClass}">
                <div class="error-header-row">
                    <div>
                        <span class="error-code">${error.code}</span>
                        <span class="error-title" style="color: #2c3e50; margin-right: 10px;">${error.title}</span>
                    </div>
                    <div>
                        <span class="error-severity" style="background: ${severityColor}; padding: 3px 8px; border-radius: 4px; color: white; font-size: 11px; margin-left: 5px;">
                            ${error.severity.toUpperCase()}
                        </span>
                        <span class="error-category">${error.category}</span>
                    </div>
                </div>
                <div class="error-description">${error.description}</div>
                ${error.symptoms && error.symptoms.length > 0 ? `
                    <div class="error-symptoms" style="margin: 10px 0; padding: 10px; background: #fff3cd; border-radius: 6px; font-size: 13px;">
                        <strong>תסמינים:</strong>
                        <ul style="margin: 5px 0 0 20px; padding: 0;">
                            ${error.symptoms.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                <div class="error-solution">
                    <strong>פתרון:</strong> ${error.solution}
                </div>
                <div class="error-actions">
                    <button class="btn btn-sm btn-info" onclick="window.errorsModule.showDetails('${error.code}')">
                        📖 פרטים (Details)
                    </button>
                    ${error.autoFix ? `
                        <button class="btn btn-sm btn-success" onclick="window.errorsModule.runAutoFix('${error.code}')">
                            🔧 תקן אוטומטית (Auto-Fix)
                        </button>
                    ` : ''}
                    ${error.documentation ? `
                        <button class="btn btn-sm btn-secondary" onclick="window.open('${error.documentation}', '_blank')">
                            📚 תיעוד (Docs)
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    table.innerHTML = html;
}

/**
 * Filter by Category
 */
function filterByCategory(category) {
    // Update active button
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Filter errors
    const errorItems = document.querySelectorAll('.error-item');
    errorItems.forEach(item => {
        if (category === 'all' || item.classList.contains(category)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Search Errors
 */
function searchErrors() {
    const searchTerm = document.getElementById('error-search-input').value.toLowerCase();
    const errorItems = document.querySelectorAll('.error-item');
    
    errorItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Show Error Details
 */
async function showDetails(errorCode) {
    try {
        const response = await fetch('../data/error-codes-registry.json?' + Date.now());
        const data = await response.json();
        const error = data.errors.find(e => e.code === errorCode);
        
        if (!error) {
            alert('❌ שגיאה לא נמצאה');
            return;
        }
        
        const symptoms = error.symptoms ? error.symptoms.join('\n  • ') : 'לא זמין';
        const autoFix = error.autoFixAvailable ? '✅ זמין' : '❌ לא זמין';
        const autoFixCmd = error.autoFixCommand || 'לא זמין';
        const docs = error.documentation || 'אין תיעוד זמין';
        
        alert(`
╔════════════════════════════════════════════════════════╗
║  📖 פרטי שגיאה מלאים                                  ║
╚════════════════════════════════════════════════════════╝

🔖 קוד: ${error.code}
📂 קטגוריה: ${error.category}
🎯 כותרת: ${error.title}
⚠️ חומרה: ${error.severity}

📝 תיאור:
${error.description}

🔍 תסמינים:
  • ${symptoms}

💡 פתרון:
${error.solution}

🔧 תיקון אוטומטי: ${autoFix}
${error.autoFixAvailable ? `\n📜 פקודה:\n${autoFixCmd}` : ''}

📚 תיעוד:
${docs}
        `.trim());
        
    } catch (error) {
        alert('❌ שגיאה בטעינת פרטים: ' + error.message);
    }
}

/**
 * Run Auto-Fix for Error
 */
async function runAutoFix(errorCode) {
    if (!confirm(`האם להריץ Auto-Fix עבור ${errorCode}?`)) {
        return;
    }
    
    console.log(`🔧 Running auto-fix for ${errorCode}`);
    
    try {
        // Load error data from JSON
        const response = await fetch('../data/error-codes-registry.json?' + Date.now());
        const data = await response.json();
        const error = data.errors.find(e => e.code === errorCode);
        
        if (!error || !error.autoFixAvailable || !error.autoFixCommand) {
            alert('❌ אין Auto-Fix זמין לשגיאה זו');
            return;
        }
        
        // Execute auto-fix command
        alert(`🔧 מריץ: ${error.autoFixCommand}\n\nאנא המתן...`);
        
        const result = await terminalConfig.executeCommand(error.autoFixCommand);
        
        if (result.output) {
            alert(`✅ Auto-Fix הושלם!\n\n📤 פלט:\n${result.output}`);
        } else {
            alert('✅ Auto-Fix הושלם בהצלחה!');
        }
        
        // Reload error codes to refresh display
        setTimeout(() => {
            loadErrorCodes();
        }, 1000);
        
    } catch (error) {
        alert(`❌ שגיאה בהרצת Auto-Fix: ${error.message}`);
        console.error('Auto-fix error:', error);
    }
}

/**
 * Export
 */
window.errorsModule = {
    filterByCategory,
    searchErrors,
    showDetails,
    runAutoFix
};
