// ========================================
// מודול תיעוד משופר - DEPLOYMENT_MANAGEMENT
// Documentation Module Enhanced
// ========================================

import { marked } from 'https://cdn.jsdelivr.net/npm/marked@11/+esm';

// הגדרות marked לתצוגה משופרת
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: true,
    mangle: false
});

// Cache למסמכים שנטענו
const docsCache = new Map();
// Cache לתוכן חיפוש
const searchCache = new Map();
// Cache למיפוי קבצים (שם → נתיב מלא)
const filePathCache = new Map();

export async function init() {
    console.log('🚀 מאתחל מודול תיעוד DEPLOYMENT משופר (Initializing Enhanced Deployment Documentation Module)');
    await scanAvailableFiles(); // סרוק קבצים זמינים
    await renderDocs();
    initializeSearch();
}

// פונקציה לסריקת כל הקבצים הזמינים בשרת
async function scanAvailableFiles() {
    console.log('🔍 סורק קבצים זמינים...');
    
    // רשימת נתיבים לסריקה (יחסית לשרת Dashboard - control-center/)
    const pathsToScan = [
        '',  // root של control-center
        'docs/',  // control-center/docs/
        'project-docs/',  // ../../../project-docs/
        '../../../',  // תיקיית root של הפרויקט
        '../../../docs/',
        '../../../project-docs/',
        '../../../SCRIPTS/',
        '../../../escriptorium/',
        '../../../escriptorium/management/',
        '../../../escriptorium/ui/',
        '../../../escriptorium/scripts/',
        '../../../DEPLOYMENT_MANAGEMENT/',
        'DEPLOYMENT_MANAGEMENT/docs-archive/',
        'DEPLOYMENT_MANAGEMENT/docs-archive/guides/',
        'DEPLOYMENT_MANAGEMENT/docs-archive/architecture/'
    ];
    
    // בנה רשימה דינמית של קבצי .md מכל המסמכים הרשומים
    const filesToFind = new Set();
    
    // הוסף קבצים מהקטלוג
    if (window.docsModule && window.docsModule.allDocs) {
        window.docsModule.allDocs.forEach(doc => {
            const fileName = doc.file.split('/').pop();
            if (fileName.endsWith('.md') || fileName.endsWith('.ps1')) {
                filesToFind.add(fileName);
            }
        });
    }
    
    // הוסף גם קבצים נפוצים שאולי לא רשומים
    const commonFiles = [
        'README.md',
        'QUICK_START.md',
        'ORGANIZATION_COMPLETE.md',
        'UNIFIED_MAPPING_REPORT.md',
        'UNIFIED_QUICK_STATUS.md',
        'CONFUSION_SOLVED.md',
        'UNIFIED_CONFUSION_REPORT.md',
        'ESCRIPTORIUM_STRUCTURE_COMPLETE.md',
        'DOCUMENTATION_CENTER_UPGRADE_REPORT.md',
        'create-escriptorium-structure.ps1'
    ];
    
    commonFiles.forEach(file => filesToFind.add(file));
    
    console.log(`📋 מחפש ${filesToFind.size} קבצים...`);
    
    // רשימת קבצים שאנחנו יודעים שזמינים (למנוע 404s)
    const knownAvailablePaths = [
        'docs/',
        'project-docs/',
        'DEPLOYMENT_MANAGEMENT/docs-archive/',
        'DEPLOYMENT_MANAGEMENT/docs-archive/guides/',
        'DEPLOYMENT_MANAGEMENT/docs-archive/architecture/'
    ];
    
    // נסה למצוא כל קובץ - אך רק בנתיבים שיש להם סיכוי
    for (const fileName of filesToFind) {
        const fileNameLower = fileName.toLowerCase();
        
        // אם כבר מצאנו, דלג
        if (filePathCache.has(fileNameLower)) continue;
        
        // חפש רק בנתיבים שסביר שהקובץ נמצא בהם
        const isMarkdown = fileName.endsWith('.md');
        const isPowerShell = fileName.endsWith('.ps1');
        
        // קבצי .ps1 בדרך כלל לא זמינים דרך השרת - דלג עליהם
        if (isPowerShell) continue;
        
        // חפש רק בנתיבים הידועים
        for (const basePath of knownAvailablePaths) {
            const fullPath = basePath + fileName;
            
            try {
                const response = await fetch(`/${fullPath}`, { method: 'HEAD' });
                if (response.ok) {
                    filePathCache.set(fileNameLower, fullPath);
                    console.log(`✅ מצאתי: ${fileName} ב-${fullPath}`);
                    break; // מצאנו, עבור לקובץ הבא
                }
            } catch (error) {
                // קובץ לא קיים בנתיב הזה, המשך בשקט
            }
        }
    }
    
    console.log(`📁 סיימתי סריקה: ${filePathCache.size} קבצים נמצאו`);
}

async function renderDocs() {
    const container = document.getElementById('docs-content');
    
    // רשימת מדריכים ממוקדת ב-DEPLOYMENT_MANAGEMENT + תיעוד Docker
    const guides = [
        {
            category: '🚀 התחלה מהירה - Quick Start',
            icon: '🚀',
            items: [
                { title: 'START HERE', file: 'docs/START_HERE.md', desc: 'התחילו כאן - מדריך הפעלת מרכז הבקרה', tags: ['start', 'setup', 'הפעלה', 'התחלה'] },
                { title: 'HOW TO START', file: 'docs/HOW_TO_START.md', desc: 'מדריך התחלה מפורט - שרתים וממשק', tags: ['start', 'servers', 'שרתים', 'התחלה'] },
                { title: 'Dashboard Guide', file: 'docs/DASHBOARD_GUIDE.md', desc: 'מדריך שימוש בלוח הבקרה', tags: ['dashboard', 'ui', 'ממשק', 'לוח', 'בקרה'] }
            ]
        },
        {
            category: '🎛️ מרכז הבקרה - Control Center',
            icon: '🎛️',
            items: [
                { title: 'README - Control Center', file: 'docs/README_CONTROL_CENTER.md', desc: 'תיעוד מלא של מרכז הבקרה', tags: ['control', 'overview', 'כללי', 'בקרה'] },
                { title: 'Dashboard Integration', file: 'docs/DASHBOARD_INTEGRATION.md', desc: 'שילוב הדשבורד במערכת', tags: ['dashboard', 'integration', 'שילוב', 'לוח'] },
                { title: 'Integration Plan', file: 'docs/INTEGRATION_PLAN.md', desc: 'תוכנית שילוב מערכות', tags: ['plan', 'integration', 'תכנון', 'שילוב'] },
                { title: 'Control Center Summary', file: 'docs/CONTROL_CENTER_SUMMARY.md', desc: 'סיכום יכולות המערכת', tags: ['summary', 'סיכום', 'בקרה'] },
                { title: 'Control Center Audit', file: 'docs/CONTROL_CENTER_AUDIT.md', desc: 'ביקורת ובדיקות מערכת', tags: ['audit', 'ביקורת', 'בדיקות'] },
                { title: 'Documentation Viewer', file: 'docs/README_DOCUMENTATION_VIEWER.md', desc: 'מערכת צפייה במסמכים', tags: ['viewer', 'docs', 'תיעוד', 'מסמכים'] }
            ]
        },
        {
            category: '📊 מצב נוכחי - Status & Logs',
            icon: '📊',
            items: [
                { title: 'Current State', file: 'docs/CURRENT_STATE.md', desc: 'מצב נוכחי של המערכת', tags: ['status', 'current', 'מצב', 'נוכחי'] },
                { title: 'Session Log', file: 'docs/SESSION_LOG.md', desc: 'יומן פעילות מפורט', tags: ['log', 'history', 'היסטוריה', 'יומן'] }
            ]
        },
        {
            category: '🐳 Docker & Deployment',
            icon: '🐳',
            items: [
                { title: 'Smart Deployment System', file: 'DEPLOYMENT_MANAGEMENT/docs-archive/smart-deployment-system.md', desc: 'מערכת פריסה חכמה ואוטומטית', tags: ['docker', 'deploy', 'automation', 'פריסה', 'אוטומציה'] },
                { title: 'Deployment Strategy', file: 'DEPLOYMENT_MANAGEMENT/docs-archive/guides/deployment-strategy.md', desc: 'אסטרטגיית פריסה מומלצת', tags: ['docker', 'strategy', 'אסטרטגיה', 'פריסה'] },
                { title: 'How It Works', file: 'DEPLOYMENT_MANAGEMENT/docs-archive/guides/how-it-works.md', desc: 'איך מערכת הפריסה עובדת', tags: ['docker', 'how-to', 'הסבר', 'פריסה'] },
                { title: 'Environments Guide', file: 'DEPLOYMENT_MANAGEMENT/docs-archive/guides/environments-real-world-guide.md', desc: 'מדריך סביבות (dev/test/prod)', tags: ['environments', 'docker', 'סביבות', 'dev', 'test', 'prod'] }
            ]
        },
        {
            category: '🏗️ ארכיטקטורה - Architecture',
            icon: '🏗️',
            items: [
                { title: 'Scripts Architecture', file: 'DEPLOYMENT_MANAGEMENT/docs-archive/architecture/scripts-architecture.md', desc: 'ארכיטקטורת סקריפטי Deployment', tags: ['architecture', 'scripts', 'ארכיטקטורה', 'סקריפטים'] },
                { title: 'System Summary', file: 'DEPLOYMENT_MANAGEMENT/docs-archive/system-summary.md', desc: 'סיכום ארכיטקטורת המערכת', tags: ['architecture', 'summary', 'סיכום', 'מערכת'] },
                { title: 'System Summary V2', file: 'DEPLOYMENT_MANAGEMENT/docs-archive/system-summary-v2.md', desc: 'סיכום ארכיטקטורה מעודכן', tags: ['architecture', 'summary', 'עדכון', 'v2'] },
                { title: 'Structure Complete', file: 'DEPLOYMENT_MANAGEMENT/docs-archive/escriptorium-structure-complete.md', desc: 'מבנה מלא של eScriptorium', tags: ['structure', 'מבנה', 'escriptorium'] }
            ]
        },
        {
            category: '📚 מדריכים מתקדמים - Advanced Guides',
            icon: '📚',
            items: [
                { title: 'Control Center Guide', file: 'DEPLOYMENT_MANAGEMENT/docs-archive/guides/control-center-guide.md', desc: 'מדריך מתקדם למרכז בקרה', tags: ['advanced', 'control', 'מתקדם', 'בקרה'] },
                { title: 'Learnings from Scripts', file: 'DEPLOYMENT_MANAGEMENT/docs-archive/learnings-from-existing-script.md', desc: 'לקחים מסקריפטים קיימים', tags: ['lessons', 'best-practices', 'לקחים', 'סקריפטים'] }
            ]
        },
        {
            category: '🔗 תיעוד פרויקט כללי - General Project',
            icon: '🔗',
            items: [
                { title: 'README - eScriptorium', file: 'README.md', desc: 'מבוא כללי לפרויקט eScriptorium', tags: ['readme', 'intro', 'מבוא', 'פרויקט'] },
                { title: 'Quick Start', file: 'QUICK_START.md', desc: 'התחלה מהירה בפרויקט', tags: ['start', 'quick', 'מהיר', 'התחלה'] },
                { title: 'Organization Complete', file: 'project-docs/ORGANIZATION_COMPLETE.md', desc: 'ארגון תיקיות הפרויקט', tags: ['organization', 'structure', 'ארגון', 'תיקיות'] }
            ]
        },
        {
            category: '📝 דוחות וניתוחים - Reports & Analysis',
            icon: '📝',
            items: [
                { title: 'UNIFIED Mapping Report', file: 'UNIFIED_MAPPING_REPORT.md', desc: 'מיפוי מפורט של מערכת UNIFIED', tags: ['unified', 'mapping', 'מיפוי', 'דוח'] },
                { title: 'UNIFIED Quick Status', file: 'UNIFIED_QUICK_STATUS.md', desc: 'סיכום מהיר של מצב UNIFIED', tags: ['unified', 'status', 'מצב', 'סיכום'] },
                { title: 'Confusion Solved', file: 'CONFUSION_SOLVED.md', desc: 'הסבר על 2 UNIFIED שונים במערכת', tags: ['unified', 'confusion', 'הסבר', 'בעיות'] },
                { title: 'UNIFIED Confusion Report', file: 'UNIFIED_CONFUSION_REPORT.md', desc: 'ניתוח מעמיק של בעיית UNIFIED', tags: ['unified', 'analysis', 'ניתוח', 'דוח'] },
                { title: 'eScriptorium Structure Complete', file: 'ESCRIPTORIUM_STRUCTURE_COMPLETE.md', desc: 'סיכום סופי מקיף של מבנה המערכת', tags: ['structure', 'complete', 'מבנה', 'סיכום'] },
                { title: 'Documentation Center Upgrade', file: 'DOCUMENTATION_CENTER_UPGRADE_REPORT.md', desc: 'דוח שיפורים במרכז התיעוד', tags: ['docs', 'upgrade', 'שיפורים', 'תיעוד'] }
            ]
        },
        {
            category: '📂 מבנה תיקיות - Directory Structure',
            icon: '📂',
            items: [
                { title: 'eScriptorium README', file: 'README.md', desc: 'מדריך ראשי (יחפש אוטומטית)', tags: ['escriptorium', 'readme', 'תיקייה', 'מבנה'] }
            ]
        },
        {
            category: '🛠️ סקריפטים וכלים - Scripts & Tools',
            icon: '🛠️',
            items: [
                { title: 'Create eScriptorium Structure', file: 'create-escriptorium-structure.ps1', desc: 'סקריפט יצירת מבנה תיקיות מלא', tags: ['script', 'powershell', 'structure', 'סקריפט', 'כלי'] }
            ]
        }
    ];
    
    let html = `
        <div class="docs-container">
            <div class="docs-header">
                <div class="docs-header-content">
                    <h2>📚 מרכז התיעוד - DEPLOYMENT_MANAGEMENT</h2>
                    <p class="docs-subtitle">תיעוד מרכז הבקרה, Docker, פריסה וניהול של פרויקט eScriptorium</p>
                    <div class="docs-breadcrumb">
                        <span>3️⃣ 🚢 DEPLOY - ניהול Docker</span>
                        <span class="separator">→</span>
                        <span>Control Center</span>
                        <span class="separator">→</span>
                        <span>Documentation</span>
                    </div>
                </div>
            </div>
            
            <div class="docs-search-section">
                <div class="search-box">
                    <input type="text" id="docs-search-input" class="search-input" placeholder="🔍 חפש במדריכים... (תמיכה בחיפוש בתוכן הקבצים)">
                    <div class="search-options">
                        <label>
                            <input type="checkbox" id="search-in-content" checked>
                            <span>חפש גם בתוכן המסמכים</span>
                        </label>
                    </div>
                </div>
                <div id="search-results" class="search-results" style="display: none;"></div>
            </div>
    `;
    
    guides.forEach(category => {
        html += `
            <div class="docs-category" data-category="${category.category}">
                <h3 class="docs-category-title">
                    <span class="category-icon">${category.icon}</span>
                    ${category.category}
                    <span class="category-count">(${category.items.length} מדריכים)</span>
                </h3>
                <div class="docs-grid">
        `;
        
        category.items.forEach(item => {
            const tagsStr = item.tags.join(',');
            html += `
                <div class="doc-card" data-title="${item.title.toLowerCase()}" data-desc="${item.desc.toLowerCase()}" data-tags="${tagsStr}" data-file="${item.file}">
                    <div class="doc-card-header">
                        <h4 class="doc-title">${item.title}</h4>
                    </div>
                    <p class="doc-desc">${item.desc}</p>
                    <div class="doc-tags">
                        ${item.tags.slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                    <div class="doc-card-footer">
                        <button class="btn btn-primary btn-sm" onclick="window.docsModule.loadDoc('${item.file}', '${item.title}')">
                            📖 קרא
                        </button>
                        <span class="doc-file" title="${item.file}">${item.file.split('/').pop()}</span>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        
        <div id="docs-viewer" class="docs-viewer" style="display: none;">
            <aside id="docs-toc" class="docs-toc" style="display: none;">
                <div class="docs-toc-top-bar">
                    <button class="docs-toc-close-btn" onclick="window.docsModule.closeViewer()">
                        ✕ סגור
                    </button>
                    <div class="docs-toc-doc-title" id="docs-toc-doc-title"></div>
                    <div class="docs-toc-navigation">
                        <button class="docs-toc-nav-btn" id="docs-toc-prev-btn" onclick="window.docsModule.navigateToPrevDoc()" title="מסמך קודם">
                            ← הקודם
                        </button>
                        <button class="docs-toc-nav-btn" id="docs-toc-next-btn" onclick="window.docsModule.navigateToNextDoc()" title="מסמך הבא">
                            הבא →
                        </button>
                    </div>
                </div>
                
                <div class="docs-toc-header">
                    <div class="docs-toc-controls">
                        <span class="docs-toc-level-label">הצג רמות:</span>
                        <select id="docs-toc-level-filter" class="docs-toc-level-select" onchange="window.docsModule.filterTocByLevel(this.value)">
                            <option value="all">כל הרמות (1-6)</option>
                            <option value="1">רק כותרות ראשיות (1)</option>
                            <option value="2" selected>רמות 1-2</option>
                            <option value="3">רמות 1-3</option>
                            <option value="4">רמות 1-4</option>
                            <option value="5">רמות 1-5</option>
                        </select>
                    </div>
                    
                    <div class="docs-toc-tabs">
                        <button class="docs-toc-tab active" data-tab="nav" onclick="window.docsModule.switchTocTab('nav')">
                            📑 ניווט
                        </button>
                        <button class="docs-toc-tab" data-tab="search" onclick="window.docsModule.switchTocTab('search')">
                            🔍 חיפוש
                        </button>
                    </div>
                    
                    <div class="docs-toc-search-box" id="docs-toc-search-box">
                        <button class="docs-toc-search-clear" id="docs-toc-search-clear" onclick="window.docsModule.clearTocSearch()">✕</button>
                        <input 
                            type="text" 
                            id="docs-toc-search-input" 
                            class="docs-toc-search-input" 
                            placeholder="חפש במסמך..."
                            oninput="window.docsModule.searchInDoc(this.value)"
                        />
                    </div>
                </div>
                
                <ul id="docs-toc-list" class="docs-toc-list"></ul>
                <div id="docs-toc-results" class="docs-toc-results"></div>
            </aside>
            
            <div class="docs-viewer-main">
                <div class="docs-viewer-header">
                    <button class="btn btn-secondary" onclick="window.docsModule.closeViewer()">
                        ← חזור לרשימה
                    </button>
                    <h3 id="docs-viewer-title"></h3>
                    <button class="btn btn-outline" onclick="window.docsModule.printDoc()">
                        🖨️ הדפס
                    </button>
                </div>
                <div id="docs-viewer-content" class="docs-viewer-content markdown-body"></div>
            </div>
        </div>
        
        ${getEnhancedStyles()}
    `;
    
    container.innerHTML = html;
    initializeSearch();
    
    // אתחל את רשימת כל המסמכים לניווט
    window.docsModule.allDocs = [];
    guides.forEach(category => {
        category.items.forEach(item => {
            window.docsModule.allDocs.push(item);
        });
    });
    
    console.log(`📚 נטענו ${window.docsModule.allDocs.length} מסמכים`);
}

function getEnhancedStyles() {
    return `
        <style>
            .docs-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 1rem;
            }
            
            .docs-header {
                text-align: center;
                margin-bottom: 2rem;
                padding: 2.5rem 2rem;
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            
            .docs-header-content h2 {
                margin: 0 0 0.5rem 0;
                font-size: 2.2rem;
                font-weight: 700;
            }
            
            .docs-subtitle {
                margin: 0 0 1rem 0;
                opacity: 0.95;
                font-size: 1.15rem;
                line-height: 1.6;
            }
            
            .docs-breadcrumb {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                margin-top: 1rem;
                font-size: 0.9rem;
                opacity: 0.9;
            }
            
            .docs-breadcrumb .separator {
                opacity: 0.5;
            }
            
            .docs-search-section {
                margin-bottom: 2.5rem;
            }
            
            .search-box {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            }
            
            .search-input {
                width: 100%;
                padding: 14px 20px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 15px;
                transition: all 0.3s ease;
            }
            
            .search-input:focus {
                outline: none;
                border-color: #3498db;
                box-shadow: 0 0 0 4px rgba(52, 152, 219, 0.1);
            }
            
            .search-options {
                margin-top: 1rem;
                display: flex;
                gap: 1rem;
            }
            
            .search-options label {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                cursor: pointer;
                color: #555;
                font-size: 0.95rem;
            }
            
            .search-results {
                margin-top: 1rem;
                background: #f8f9fa;
                border-radius: 8px;
                padding: 1rem;
            }
            
            .search-result-item {
                background: white;
                padding: 1rem;
                margin-bottom: 0.75rem;
                border-radius: 8px;
                border-left: 4px solid #3498db;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .search-result-item:hover {
                transform: translateX(-4px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .search-result-title {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 0.25rem;
            }
            
            .search-result-snippet {
                font-size: 0.85rem;
                color: #666;
                line-height: 1.5;
            }
            
            .search-highlight {
                background: #fff3cd;
                padding: 1px 3px;
                border-radius: 2px;
                font-weight: 600;
            }
            
            .docs-category {
                margin-bottom: 3rem;
            }
            
            .docs-category-title {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                font-size: 1.6rem;
                margin-bottom: 1.25rem;
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 0.75rem;
            }
            
            .category-icon {
                font-size: 1.8rem;
            }
            
            .category-count {
                font-size: 0.9rem;
                color: #7f8c8d;
                font-weight: 400;
            }
            
            .docs-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
                gap: 1.5rem;
            }
            
            .doc-card {
                background: white;
                border-radius: 14px;
                padding: 1.75rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                border-top: 4px solid #3498db;
                display: flex;
                flex-direction: column;
            }
            
            .doc-card:hover {
                transform: translateY(-6px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.12);
                border-top-color: #2980b9;
            }
            
            .doc-card-header {
                margin-bottom: 0.75rem;
            }
            
            .doc-title {
                margin: 0;
                color: #2c3e50;
                font-size: 1.15rem;
                font-weight: 700;
                line-height: 1.4;
            }
            
            .doc-desc {
                color: #555;
                font-size: 0.95rem;
                margin-bottom: 1rem;
                line-height: 1.6;
                flex: 1;
            }
            
            .doc-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-bottom: 1rem;
            }
            
            .tag {
                background: #e8f4f8;
                color: #2980b9;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 500;
            }
            
            .doc-card-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                margin-top: auto;
            }
            
            .doc-file {
                font-size: 0.75rem;
                color: #95a5a6;
                font-family: 'Courier New', monospace;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                flex: 1;
            }
            
            .docs-viewer {
                background: white;
                border-radius: 14px;
                padding: 2.5rem;
                box-shadow: 0 2px 12px rgba(0,0,0,0.08);
                max-width: 1400px;
                margin: 0 auto;
                display: block;
                position: relative;
            }
            
            .docs-viewer-main {
                width: 100%;
                max-width: 100%;
                margin: 0;
                padding: 0;
            }
            
            .docs-viewer-header {
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 2rem;
                padding-bottom: 1.5rem;
                border-bottom: 3px solid #e9ecef;
            }
            
            .docs-viewer-header h3 {
                margin: 0;
                color: #2c3e50;
                flex: 1;
                font-size: 1.8rem;
            }
            
            /* Table of Contents Sidebar */
            .docs-toc {
                position: fixed;
                right: 0;
                top: 0;
                bottom: 0;
                width: 340px;
                background: #f8f9fa;
                padding: 1.5rem;
                overflow-y: auto;
                z-index: 9999;
                box-shadow: -2px 0 12px rgba(0,0,0,0.15);
                border-left: 2px solid #dee2e6;
            }
            
            .docs-toc-top-bar {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 1rem;
                margin: -1.5rem -1.5rem 1rem -1.5rem;
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                border-bottom: 2px solid #2471a3;
            }
            
            .docs-toc-close-btn {
                background: rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9rem;
                font-weight: 600;
                transition: all 0.2s ease;
                flex-shrink: 0;
            }
            
            .docs-toc-close-btn:hover {
                background: rgba(255,255,255,0.3);
                transform: translateX(-2px);
            }
            
            .docs-toc-doc-title {
                flex: 1;
                font-size: 1rem;
                font-weight: 700;
                text-overflow: ellipsis;
                overflow: hidden;
                white-space: nowrap;
            }
            
            .docs-toc-navigation {
                display: flex;
                gap: 0.5rem;
                flex-shrink: 0;
            }
            
            .docs-toc-nav-btn {
                background: rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: 0.4rem 0.8rem;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.85rem;
                transition: all 0.2s ease;
                white-space: nowrap;
            }
            
            .docs-toc-nav-btn:hover:not(:disabled) {
                background: rgba(255,255,255,0.3);
                transform: scale(1.05);
            }
            
            .docs-toc-nav-btn:disabled {
                opacity: 0.3;
                cursor: not-allowed;
            }
            
            .docs-toc-header {
                margin-bottom: 1rem;
            }
            
            .docs-toc-controls {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 1rem;
                padding: 0.75rem;
                background: white;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
            
            .docs-toc-level-label {
                font-size: 0.85rem;
                color: #6c757d;
                font-weight: 600;
                white-space: nowrap;
            }
            
            .docs-toc-level-select {
                flex: 1;
                padding: 0.4rem 0.6rem;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 0.85rem;
                background: white;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .docs-toc-level-select:hover {
                border-color: #3498db;
            }
            
            .docs-toc-level-select:focus {
                outline: none;
                border-color: #3498db;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
            }
            
            .docs-toc-tabs {
                display: flex;
                gap: 0.5rem;
                margin-bottom: 1rem;
                border-bottom: 2px solid #dee2e6;
            }
            
            .docs-toc-tab {
                flex: 1;
                padding: 0.5rem 1rem;
                background: transparent;
                border: none;
                border-bottom: 3px solid transparent;
                cursor: pointer;
                font-size: 0.9rem;
                font-weight: 600;
                color: #6c757d;
                transition: all 0.2s ease;
                margin-bottom: -2px;
            }
            
            .docs-toc-tab:hover {
                color: #2c3e50;
                background: rgba(52, 152, 219, 0.05);
            }
            
            .docs-toc-tab.active {
                color: #3498db;
                border-bottom-color: #3498db;
            }
            
            .docs-toc-search-box {
                position: relative;
                margin-bottom: 1rem;
                display: none;
            }
            
            .docs-toc-search-box.active {
                display: block;
            }
            
            .docs-toc-search-input {
                width: 100%;
                padding: 0.6rem 2.5rem 0.6rem 1rem;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                font-size: 0.9rem;
                transition: all 0.2s ease;
            }
            
            .docs-toc-search-input:focus {
                outline: none;
                border-color: #3498db;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
            }
            
            .docs-toc-search-clear {
                position: absolute;
                left: 0.75rem;
                top: 50%;
                transform: translateY(-50%);
                background: none;
                border: none;
                color: #6c757d;
                cursor: pointer;
                padding: 0.25rem;
                font-size: 1.1rem;
                display: none;
            }
            
            .docs-toc-search-clear.visible {
                display: block;
            }
            
            .docs-toc-title {
                font-size: 1.1rem;
                font-weight: 700;
                color: #2c3e50;
                margin: 0 0 1rem 0;
                padding-bottom: 0.75rem;
                border-bottom: 2px solid #dee2e6;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .docs-toc-list {
                list-style: none;
                padding: 0;
                margin: 0;
                display: block;
            }
            
            .docs-toc-list.hidden {
                display: none;
            }
            
            .docs-toc-item {
                margin: 0;
                transition: all 0.2s ease;
                position: relative;
            }
            
            .docs-toc-item.filtered-out {
                display: none;
            }
            
            .docs-toc-item.has-children {
                /* פריט עם ילדים */
            }
            
            .docs-toc-item.collapsed > .docs-toc-list {
                display: none;
            }
            
            .docs-toc-item {
                position: relative;
            }
            
            .docs-toc-item.has-children .docs-toc-link {
                padding-left: 2rem;
            }
            
            .docs-toc-link {
                display: block;
                padding: 0.5rem 0.75rem;
                color: #495057;
                text-decoration: none;
                border-radius: 6px;
                transition: all 0.2s ease;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .docs-toc-expand-btn {
                position: absolute;
                right: 0.5rem;
                top: 50%;
                transform: translateY(-50%);
                background: transparent;
                border: none;
                color: #6c757d;
                cursor: pointer;
                padding: 0.25rem 0.5rem;
                font-size: 0.9rem;
                transition: all 0.2s ease;
                z-index: 1;
            }
            
            .docs-toc-expand-btn:hover {
                color: #3498db;
                transform: translateY(-50%) scale(1.2);
            }
            
            .docs-toc-item.collapsed .docs-toc-expand-btn::before {
                content: '◀';
            }
            
            .docs-toc-item.has-children:not(.collapsed) .docs-toc-expand-btn::before {
                content: '▼';
            }
            
            .docs-toc-results {
                display: none;
            }
            
            .docs-toc-results.active {
                display: block;
            }
            
            .docs-toc-result-item {
                padding: 0.75rem;
                margin-bottom: 0.5rem;
                background: white;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
                border: 1px solid #e9ecef;
            }
            
            .docs-toc-result-item:hover {
                border-color: #3498db;
                box-shadow: 0 2px 8px rgba(52, 152, 219, 0.15);
            }
            
            .docs-toc-result-text {
                font-size: 0.85rem;
                color: #495057;
                line-height: 1.5;
            }
            
            .docs-toc-result-highlight {
                background: #fff3cd;
                color: #856404;
                font-weight: 600;
                padding: 0 0.2rem;
            }
            
            .docs-toc-no-results {
                text-align: center;
                padding: 2rem 1rem;
                color: #6c757d;
                font-size: 0.9rem;
            }
            
            .docs-toc-item {
                margin: 0;
            }
            
            .docs-toc-link {
                display: block;
                padding: 0.5rem 0.75rem;
                color: #495057;
                text-decoration: none;
                border-radius: 6px;
                transition: all 0.2s ease;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .docs-toc-link:hover {
                background: #e9ecef;
                color: #2c3e50;
                transform: translateX(-3px);
            }
            
            .docs-toc-link.active {
                background: #3498db;
                color: white;
                font-weight: 600;
            }
            
            /* Indentation for heading levels */
            .docs-toc-item.level-1 .docs-toc-link {
                font-weight: 700;
                font-size: 1.05rem;
                color: #2c3e50;
                padding: 0.6rem 0.75rem;
                background: rgba(52, 152, 219, 0.05);
                margin-bottom: 0.25rem;
            }
            
            .docs-toc-item.level-1 .docs-toc-link:hover {
                background: rgba(52, 152, 219, 0.15);
            }
            
            .docs-toc-item.level-2 .docs-toc-link {
                padding-right: 1.5rem;
                font-size: 0.95rem;
                font-weight: 600;
                color: #34495e;
            }
            
            .docs-toc-item.level-3 .docs-toc-link {
                padding-right: 2.5rem;
                font-size: 0.88rem;
                font-weight: 500;
                color: #5a6c7d;
            }
            
            .docs-toc-item.level-4 .docs-toc-link {
                padding-right: 3.5rem;
                font-size: 0.82rem;
                font-weight: 400;
                color: #7f8c8d;
            }
            
            .docs-toc-item.level-5 .docs-toc-link,
            .docs-toc-item.level-6 .docs-toc-link {
                padding-right: 4.5rem;
                font-size: 0.76rem;
                font-weight: 400;
                color: #95a5a6;
            }
            
            .docs-toc::-webkit-scrollbar {
                width: 6px;
            }
            
            .docs-toc::-webkit-scrollbar-track {
                background: #e9ecef;
                border-radius: 3px;
            }
            
            .docs-toc::-webkit-scrollbar-thumb {
                background: #adb5bd;
                border-radius: 3px;
            }
            
            .docs-toc::-webkit-scrollbar-thumb:hover {
                background: #868e96;
            }
            
            /* Enhanced Markdown Styles */
            .markdown-body {
                line-height: 1.8;
                color: #2c3e50;
                font-size: 16px;
                padding-left: 1rem;
            }
            
            .markdown-body h1 {
                font-size: 2.5rem;
                color: #2c3e50;
                margin: 2.5rem 0 1.5rem;
                padding-bottom: 0.5rem;
                border-bottom: 3px solid #3498db;
                font-weight: 700;
                scroll-margin-top: 6rem;
            }
            
            .markdown-body h2 {
                font-size: 2rem;
                color: #34495e;
                margin: 2rem 0 1rem;
                padding-bottom: 0.3rem;
                border-bottom: 2px solid #95a5a6;
                scroll-margin-top: 6rem;
            }
            
            .markdown-body h3 {
                font-size: 1.6rem;
                color: #34495e;
                margin: 1.8rem 0 1rem;
                scroll-margin-top: 6rem;
            }
            
            .markdown-body h4 {
                font-size: 1.3rem;
                color: #5a6c7d;
                margin: 1.5rem 0 0.8rem;
                scroll-margin-top: 6rem;
            }
            
            .markdown-body h5 {
                font-size: 1.1rem;
                color: #5a6c7d;
                margin: 1.3rem 0 0.7rem;
                scroll-margin-top: 6rem;
            }
            
            .markdown-body h6 {
                font-size: 1rem;
                color: #7f8c8d;
                margin: 1.2rem 0 0.6rem;
                scroll-margin-top: 6rem;
            }
                font-weight: 600;
            }
            
            .markdown-body h3 {
                font-size: 1.6rem;
                color: #34495e;
                margin: 1.75rem 0 0.75rem;
                font-weight: 600;
            }
            
            .markdown-body h4 {
                font-size: 1.3rem;
                color: #555;
                margin: 1.5rem 0 0.5rem;
            }
            
            .markdown-body p {
                margin: 1rem 0;
                line-height: 1.8;
            }
            
            .markdown-body ul,
            .markdown-body ol {
                margin: 1rem 0;
                padding-right: 2rem;
            }
            
            .markdown-body li {
                margin: 0.5rem 0;
                line-height: 1.7;
            }
            
            .markdown-body code {
                background: #f1f3f5;
                padding: 3px 8px;
                border-radius: 4px;
                font-family: 'Courier New', Consolas, monospace;
                font-size: 0.9em;
                color: #c7254e;
                border: 1px solid #e1e4e8;
            }
            
            .markdown-body pre {
                background: #2c3e50;
                color: #ecf0f1;
                padding: 1.5rem;
                border-radius: 10px;
                overflow-x: auto;
                margin: 1.5rem 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .markdown-body pre code {
                background: transparent;
                padding: 0;
                color: inherit;
                border: none;
            }
            
            .markdown-body blockquote {
                border-right: 4px solid #3498db;
                padding: 1rem 1.5rem;
                margin: 1.5rem 0;
                background: #f8f9fa;
                border-radius: 4px;
                color: #555;
            }
            
            .markdown-body table {
                border-collapse: collapse;
                width: 100%;
                margin: 1.5rem 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            .markdown-body th,
            .markdown-body td {
                border: 1px solid #ddd;
                padding: 0.75rem;
                text-align: right;
            }
            
            .markdown-body th {
                background: #f1f3f5;
                font-weight: 600;
                color: #2c3e50;
            }
            
            .markdown-body tr:hover {
                background: #f8f9fa;
            }
            
            .markdown-body a {
                color: #3498db;
                text-decoration: none;
                border-bottom: 1px solid transparent;
                transition: all 0.2s ease;
            }
            
            .markdown-body a:hover {
                color: #2980b9;
                border-bottom-color: #2980b9;
            }
            
            .markdown-body img {
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                margin: 1.5rem 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .markdown-body hr {
                border: none;
                border-top: 2px solid #e9ecef;
                margin: 2rem 0;
            }
            
            @media print {
                .docs-viewer-header,
                .docs-toc,
                .btn {
                    display: none !important;
                }
                
                .docs-viewer {
                    box-shadow: none;
                    padding: 0;
                    display: block;
                }
                
                .docs-viewer-main {
                    max-width: 100%;
                }
            }
            
            @media (max-width: 1024px) {
                .docs-toc {
                    display: none;
                }
                
                .docs-viewer {
                    display: block;
                }
            }
            
            @media (max-width: 768px) {
                .docs-grid {
                    grid-template-columns: 1fr;
                }
                
                .docs-viewer {
                    padding: 1.5rem;
                }
                
                .markdown-body h1 {
                    font-size: 2rem;
                }
                
                .markdown-body h2 {
                    font-size: 1.6rem;
                }
            }
        </style>
    `;
}

// חיפוש מתקדם עם תמיכה בחיפוש בתוכן
function initializeSearch() {
    const searchInput = document.getElementById('docs-search-input');
    const searchInContent = document.getElementById('search-in-content');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.toLowerCase().trim();
        
        if (query.length < 2) {
            // חיפוש רגיל בכרטיסים
            filterCards(query);
            searchResults.style.display = 'none';
            return;
        }
        
        // חיפוש עם השהייה
        searchTimeout = setTimeout(async () => {
            if (searchInContent.checked) {
                await searchInDocuments(query);
            } else {
                filterCards(query);
                searchResults.style.display = 'none';
            }
        }, 300);
    });
}

function filterCards(query) {
    const cards = document.querySelectorAll('.doc-card');
    const categories = document.querySelectorAll('.docs-category');
    
    categories.forEach(category => {
        let hasVisibleCards = false;
        const categoryCards = category.querySelectorAll('.doc-card');
        
        categoryCards.forEach(card => {
            const title = card.dataset.title;
            const desc = card.dataset.desc;
            const tags = card.dataset.tags;
            const matches = !query || title.includes(query) || desc.includes(query) || tags.includes(query);
            
            card.style.display = matches ? 'block' : 'none';
            if (matches) hasVisibleCards = true;
        });
        
        category.style.display = hasVisibleCards ? 'block' : 'none';
    });
}

async function searchInDocuments(query) {
    const searchResults = document.getElementById('search-results');
    const cards = document.querySelectorAll('.doc-card');
    
    searchResults.innerHTML = '<div style="text-align: center; padding: 1rem;">🔍 מחפש בתוכן המסמכים...</div>';
    searchResults.style.display = 'block';
    
    const results = [];
    
    // חפש בכל המסמכים
    for (const card of cards) {
        const file = card.dataset.file;
        const title = card.querySelector('.doc-title').textContent;
        
        try {
            let content;
            if (searchCache.has(file)) {
                content = searchCache.get(file);
            } else {
                const response = await fetch(`/${file}`);
                if (!response.ok) continue;
                content = await response.text();
                searchCache.set(file, content);
            }
            
            // חפש בתוכן
            const lowerContent = content.toLowerCase();
            if (lowerContent.includes(query)) {
                // מצא את ההקשר
                const index = lowerContent.indexOf(query);
                const start = Math.max(0, index - 100);
                const end = Math.min(content.length, index + query.length + 100);
                let snippet = content.substring(start, end);
                
                // הדגש את התוצאה
                snippet = snippet.replace(new RegExp(query, 'gi'), match => 
                    `<span class="search-highlight">${match}</span>`
                );
                
                results.push({ title, file, snippet });
            }
        } catch (error) {
            console.warn(`לא הצלחנו לחפש ב-${file}:`, error);
        }
    }
    
    // הצג תוצאות
    if (results.length === 0) {
        searchResults.innerHTML = '<div style="text-align: center; padding: 1rem; color: #999;">😕 לא נמצאו תוצאות</div>';
    } else {
        let html = `<div style="margin-bottom: 1rem; font-weight: 600;">נמצאו ${results.length} תוצאות:</div>`;
        results.forEach(result => {
            html += `
                <div class="search-result-item" onclick="window.docsModule.loadDoc('${result.file}', '${result.title}')">
                    <div class="search-result-title">${result.title}</div>
                    <div class="search-result-snippet">...${result.snippet}...</div>
                </div>
            `;
        });
        searchResults.innerHTML = html;
    }
}

// פונקציות ציבוריות
window.docsModule = {
    currentDocIndex: -1,
    allDocs: [],
    
    async loadDoc(filename, title) {
        console.log(`📖 טוען מדריך: ${filename}`);
        
        const viewer = document.getElementById('docs-viewer');
        const container = document.querySelector('.docs-container');
        const viewerTitle = document.getElementById('docs-viewer-title');
        const viewerContent = document.getElementById('docs-viewer-content');
        const tocTitle = document.getElementById('docs-toc-doc-title');
        
        // חפש את הנתיב האמיתי של הקובץ
        let actualFilePath = filename;
        const fileNameOnly = filename.split('/').pop().toLowerCase();
        
        if (filePathCache.has(fileNameOnly)) {
            actualFilePath = filePathCache.get(fileNameOnly);
            console.log(`🔍 מצאתי קובץ: ${filename} → ${actualFilePath}`);
        } else {
            console.log(`⚠️ משתמש בנתיב מקורי: ${filename}`);
        }
        
        // שמור את המסמך הנוכחי
        this.currentDocIndex = this.allDocs.findIndex(doc => doc.file === filename);
        
        // עדכן כפתורי ניווט
        this.updateNavigationButtons();
        
        // הצג loading
        viewerTitle.textContent = title;
        tocTitle.textContent = title;
        viewerContent.innerHTML = '<div style="text-align: center; padding: 3rem;"><div class="spinner"></div><p>טוען מדריך...</p></div>';
        
        container.style.display = 'none';
        viewer.style.display = 'block';
        
        try {
            // בדוק cache
            let markdown;
            if (docsCache.has(actualFilePath)) {
                markdown = docsCache.get(actualFilePath);
            } else {
                const response = await fetch(`/${actualFilePath}`);
                if (!response.ok) {
                    // נסה חיפוש אלטרנטיבי
                    console.log(`❌ לא נמצא ב-${actualFilePath}, מנסה חיפוש...`);
                    const foundPath = await this.searchForFile(fileNameOnly);
                    if (foundPath) {
                        console.log(`✅ נמצא ב-${foundPath}`);
                        const retryResponse = await fetch(`/${foundPath}`);
                        if (retryResponse.ok) {
                            markdown = await retryResponse.text();
                            filePathCache.set(fileNameOnly, foundPath);
                        } else {
                            throw new Error(`HTTP ${response.status}: ${actualFilePath}`);
                        }
                    } else {
                        throw new Error(`HTTP ${response.status}: ${actualFilePath}`);
                    }
                } else {
                    markdown = await response.text();
                }
                docsCache.set(actualFilePath, markdown);
            }
            
            // המר ל-HTML עם marked
            const html = marked.parse(markdown);
            viewerContent.innerHTML = html;
            
            // הפוך קישורי מסמכים ללחיצים
            this.linkifyDocReferences(viewerContent);
            
            // צור תוכן עניינים (TOC)
            generateTableOfContents();
            
            // החל סינון ברירת מחדל (רמות 1-2) אבל אל תקפל אוטומטית
            setTimeout(() => {
                const levelSelect = document.getElementById('docs-toc-level-filter');
                if (levelSelect) {
                    window.docsModule.filterTocByLevel(levelSelect.value);
                }
                
                // אל תקפל כלום - השאר הכל פתוח (ברירת מחדל)
                // המשתמש יקפל בעצמו אם הוא רוצה
            }, 100);
            
            // גלול למעלה
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
        } catch (error) {
            console.error('❌ שגיאה בטעינת מדריך:', error);
            viewerContent.innerHTML = `
                <div class="error-message" style="background: #fee; border: 2px solid #fcc; padding: 2rem; border-radius: 12px; text-align: center;">
                    <h3 style="color: #c33; margin-top: 0;">❌ שגיאה בטעינת מדריך</h3>
                    <p style="color: #666; font-size: 1.1rem;">לא הצלחנו לטעון את הקובץ:</p>
                    <code style="display: block; background: #f8f9fa; padding: 1rem; border-radius: 6px; margin: 1rem 0;">${filename}</code>
                    <p style="color: #999; font-size: 0.95rem; margin: 1rem 0;">${error.message}</p>
                    <button class="btn btn-primary" onclick="window.docsModule.closeViewer()">← חזור לרשימה</button>
                </div>
            `;
        }
    },
    
    closeViewer() {
        const viewer = document.getElementById('docs-viewer');
        const container = document.querySelector('.docs-container');
        const toc = document.getElementById('docs-toc');
        
        // הסתר את תוכן העניינים
        toc.style.display = 'none';
        
        viewer.style.display = 'none';
        container.style.display = 'block';
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    
    async searchForFile(fileName) {
        console.log(`🔍 מחפש קובץ: ${fileName}`);
        
        // רשימת נתיבים לסריקה (יחסית ל-control-center/)
        const pathsToTry = [
            '',  // control-center/ (root של השרת)
            'docs/',  // control-center/docs/
            'DEPLOYMENT_MANAGEMENT/docs-archive/',
            'DEPLOYMENT_MANAGEMENT/docs-archive/guides/',
            'DEPLOYMENT_MANAGEMENT/docs-archive/architecture/',
            '../../../',  // BiblIA_dataset/ (root כללי)
            '../../../docs/',
            '../../../project-docs/',
            '../../../SCRIPTS/',
            '../../../escriptorium/',
            '../../../escriptorium/management/',
            '../../../escriptorium/ui/',
            '../../../escriptorium/scripts/',
            '../../../eScriptorium_CLEAN/',
            '../../../app/',
            'modules/',
            'scripts/'
        ];
        
        // נסה כל נתיב
        for (const basePath of pathsToTry) {
            const fullPath = basePath + fileName;
            
            try {
                const response = await fetch(`/${fullPath}`, { method: 'HEAD' });
                if (response.ok) {
                    console.log(`✅ מצאתי ב-${fullPath}`);
                    return fullPath;
                }
            } catch (error) {
                // המשך לנתיב הבא
            }
        }
        
        console.log(`❌ לא מצאתי את ${fileName}`);
        return null;
    },
    
    linkifyDocReferences(contentElement) {
        // מצא את כל המסמכים הזמינים מה-allDocs
        const availableDocsMap = new Map();
        this.allDocs.forEach(doc => {
            // נרמול: שם הקובץ בלי נתיב ובלי סיומת
            const fileName = doc.file.split('/').pop().replace(/\.(md|ps1)$/i, '');
            availableDocsMap.set(fileName.toLowerCase(), doc);
            
            // גם עם הסיומת
            const fileNameWithExt = doc.file.split('/').pop();
            availableDocsMap.set(fileNameWithExt.toLowerCase(), doc);
            
            // גם את הנתיב המלא (עם תיקייה)
            availableDocsMap.set(doc.file.toLowerCase(), doc);
            availableDocsMap.set(doc.file.toLowerCase().replace(/\.(md|ps1)$/i, ''), doc);
        });
        
        // רגקס לזיהוי הפניות למסמכים
        // תומך ב:
        // - CONTROL_CENTER_PLAN.md
        // - SESSION_LOG.md
        // - project-docs/DOCUMENTATION_CENTER_UPGRADE_REPORT.md
        // - docs/API_GUIDE.md
        // - SCRIPTS/create-escriptorium-structure.ps1
        // - escriptorium/management/README.md
        const docRefRegex = /\b([a-zA-Z0-9_-]+(?:\/[a-zA-Z0-9_-]+)*\/[A-Z][A-Z0-9_]+\.(?:md|ps1))\b|\b([A-Z][A-Z0-9_]+(?:\.(?:md|ps1))?)\b/g;
        
        // עבור על כל אלמנטי הטקסט
        const walker = document.createTreeWalker(
            contentElement,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: (node) => {
                    // דלג על קישורים קיימים, קוד, וכו'
                    const parent = node.parentElement;
                    if (!parent) return NodeFilter.FILTER_REJECT;
                    const tagName = parent.tagName.toLowerCase();
                    if (['a', 'code', 'pre', 'script', 'style'].includes(tagName)) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );
        
        const nodesToProcess = [];
        let node;
        while (node = walker.nextNode()) {
            nodesToProcess.push(node);
        }
        
        nodesToProcess.forEach(textNode => {
            const text = textNode.textContent;
            const matches = [...text.matchAll(docRefRegex)];
            
            if (matches.length === 0) return;
            
            const fragment = document.createDocumentFragment();
            let lastIndex = 0;
            
            matches.forEach(match => {
                // הרגקס מחזיר 2 קבוצות: נתיב מלא או שם פשוט
                const docRef = match[1] || match[2];
                if (!docRef) return;
                
                const startIndex = match.index;
                
                // בדוק אם המסמך קיים
                const docRefLower = docRef.toLowerCase();
                const matchedDoc = availableDocsMap.get(docRefLower) || 
                                   availableDocsMap.get(docRefLower.replace(/\.(md|ps1)$/i, ''));
                
                if (matchedDoc) {
                    // הוסף טקסט לפני
                    if (startIndex > lastIndex) {
                        fragment.appendChild(document.createTextNode(text.substring(lastIndex, startIndex)));
                    }
                    
                    // צור קישור
                    const link = document.createElement('a');
                    link.href = '#';
                    link.textContent = docRef;
                    link.className = 'doc-internal-link';
                    link.title = `📄 ${matchedDoc.title}`;
                    link.style.cssText = 'color: #3498db; text-decoration: none; border-bottom: 1px dotted #3498db; font-weight: 500; cursor: pointer;';
                    link.addEventListener('mouseenter', (e) => {
                        e.target.style.color = '#2980b9';
                        e.target.style.borderBottom = '1px solid #2980b9';
                    });
                    link.addEventListener('mouseleave', (e) => {
                        e.target.style.color = '#3498db';
                        e.target.style.borderBottom = '1px dotted #3498db';
                    });
                    link.onclick = (e) => {
                        e.preventDefault();
                        this.loadDoc(matchedDoc.file, matchedDoc.title);
                    };
                    
                    fragment.appendChild(link);
                    lastIndex = startIndex + docRef.length;
                }
            });
            
            // הוסף טקסט אחרון
            if (lastIndex < text.length) {
                fragment.appendChild(document.createTextNode(text.substring(lastIndex)));
            }
            
            // החלף את הטקסט המקורי
            if (fragment.childNodes.length > 0) {
                textNode.parentNode.replaceChild(fragment, textNode);
            }
        });
        
        console.log(`🔗 קישרתי הפניות למסמכים (${availableDocsMap.size} מסמכים זמינים)`);
    },
    
    printDoc() {
        window.print();
    },
    
    switchTocTab(tab) {
        const navTab = document.querySelector('.docs-toc-tab[data-tab="nav"]');
        const searchTab = document.querySelector('.docs-toc-tab[data-tab="search"]');
        const searchBox = document.getElementById('docs-toc-search-box');
        const tocList = document.getElementById('docs-toc-list');
        const tocResults = document.getElementById('docs-toc-results');
        
        if (tab === 'nav') {
            navTab.classList.add('active');
            searchTab.classList.remove('active');
            searchBox.classList.remove('active');
            tocList.classList.remove('hidden');
            tocResults.classList.remove('active');
        } else if (tab === 'search') {
            navTab.classList.remove('active');
            searchTab.classList.add('active');
            searchBox.classList.add('active');
            tocList.classList.add('hidden');
            tocResults.classList.add('active');
            
            // פוקוס על שדה החיפוש
            setTimeout(() => {
                document.getElementById('docs-toc-search-input').focus();
            }, 100);
        }
    },
    
    searchInDoc(query) {
        const content = document.getElementById('docs-viewer-content');
        const results = document.getElementById('docs-toc-results');
        const clearBtn = document.getElementById('docs-toc-search-clear');
        
        // הצג/הסתר כפתור ניקוי
        if (query.trim()) {
            clearBtn.classList.add('visible');
        } else {
            clearBtn.classList.remove('visible');
            results.innerHTML = '<div class="docs-toc-no-results">הקלד מילה לחיפוש...</div>';
            return;
        }
        
        if (query.length < 2) {
            results.innerHTML = '<div class="docs-toc-no-results">הקלד לפחות 2 תווים...</div>';
            return;
        }
        
        // חפש בתוכן
        const textContent = content.textContent;
        const lowerQuery = query.toLowerCase();
        const lowerContent = textContent.toLowerCase();
        
        const matches = [];
        let index = 0;
        
        while ((index = lowerContent.indexOf(lowerQuery, index)) !== -1) {
            const start = Math.max(0, index - 60);
            const end = Math.min(textContent.length, index + query.length + 60);
            let snippet = textContent.substring(start, end);
            
            // הדגש את התוצאה
            const highlightedSnippet = snippet.replace(
                new RegExp(query, 'gi'),
                match => `<span class="docs-toc-result-highlight">${match}</span>`
            );
            
            matches.push({
                snippet: highlightedSnippet,
                position: index
            });
            
            index += query.length;
            
            // הגבל ל-50 תוצאות
            if (matches.length >= 50) break;
        }
        
        // הצג תוצאות
        if (matches.length === 0) {
            results.innerHTML = '<div class="docs-toc-no-results">😕 לא נמצאו תוצאות</div>';
        } else {
            let html = `<div style="margin-bottom: 0.75rem; font-weight: 600; color: #2c3e50;">🔍 נמצאו ${matches.length} תוצאות</div>`;
            
            matches.forEach((match, i) => {
                html += `
                    <div class="docs-toc-result-item" onclick="window.docsModule.highlightResult('${query}', ${i})">
                        <div class="docs-toc-result-text">...${match.snippet}...</div>
                    </div>
                `;
            });
            
            results.innerHTML = html;
        }
    },
    
    highlightResult(query, resultIndex) {
        const content = document.getElementById('docs-viewer-content');
        
        // הסר הדגשות קודמות
        content.querySelectorAll('.search-highlight-active').forEach(el => {
            el.classList.remove('search-highlight-active');
        });
        
        // מצא את כל המופעים
        const textNodes = [];
        const walker = document.createTreeWalker(
            content,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.toLowerCase().includes(query.toLowerCase())) {
                textNodes.push(node);
            }
        }
        
        // הדגש את התוצאה הספציפית
        if (textNodes[resultIndex]) {
            const targetNode = textNodes[resultIndex];
            const parent = targetNode.parentElement;
            
            // צור span להדגשה
            const text = targetNode.textContent;
            const lowerText = text.toLowerCase();
            const lowerQuery = query.toLowerCase();
            const index = lowerText.indexOf(lowerQuery);
            
            if (index !== -1) {
                const before = text.substring(0, index);
                const match = text.substring(index, index + query.length);
                const after = text.substring(index + query.length);
                
                const span = document.createElement('span');
                span.className = 'search-highlight-active';
                span.textContent = match;
                span.style.cssText = 'background: #ffeb3b; color: #000; padding: 0.2rem 0.3rem; border-radius: 3px; font-weight: 600;';
                
                const fragment = document.createDocumentFragment();
                fragment.appendChild(document.createTextNode(before));
                fragment.appendChild(span);
                fragment.appendChild(document.createTextNode(after));
                
                parent.replaceChild(fragment, targetNode);
                
                // גלול לתוצאה
                span.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    },
    
    clearTocSearch() {
        const input = document.getElementById('docs-toc-search-input');
        const clearBtn = document.getElementById('docs-toc-search-clear');
        const results = document.getElementById('docs-toc-results');
        
        input.value = '';
        clearBtn.classList.remove('visible');
        results.innerHTML = '<div class="docs-toc-no-results">הקלד מילה לחיפוש...</div>';
        
        // הסר הדגשות
        document.querySelectorAll('.search-highlight-active').forEach(el => {
            const text = el.textContent;
            el.replaceWith(document.createTextNode(text));
        });
    },
    
    filterTocByLevel(maxLevel) {
        const tocItems = Array.from(document.querySelectorAll('.docs-toc-item'));
        const maxLevelNum = maxLevel === 'all' ? 6 : parseInt(maxLevel);

        // עזר: מוצא אם לאייטם יש אב שקולפסד
        const hasCollapsedAncestor = (idx) => {
            const item = tocItems[idx];
            const levelMatch = item.className.match(/level-(\d+)/);
            if (!levelMatch) return false;
            const level = parseInt(levelMatch[1]);
            // חפש אחורה עד שמוצאים אב (רמה נמוכה יותר)
            for (let i = idx - 1; i >= 0; i--) {
                const other = tocItems[i];
                const m = other.className.match(/level-(\d+)/);
                if (!m) continue;
                const otherLevel = parseInt(m[1]);
                if (otherLevel < level) {
                    return other.classList.contains('collapsed');
                }
            }
            return false;
        };

        // שלב 1: סמן פריטים מחוץ לטווח הרמות והסתר אותם
        tocItems.forEach(item => {
            const levelMatch = item.className.match(/level-(\d+)/);
            if (!levelMatch) return;
            const level = parseInt(levelMatch[1]);
            if (level <= maxLevelNum) {
                item.classList.remove('filtered-out');
            } else {
                item.classList.add('filtered-out');
                item.style.display = 'none';
            }
        });

        // שלב 2: עבור כל פריט בתוך הטווח – קבע תצוגה לפי מצב האבות (קולפסד או לא)
        tocItems.forEach((item, idx) => {
            if (!item.classList.contains('filtered-out')) {
                // ברירת מחדל: נראה
                item.style.display = '';
                // אם יש אב שקולפסד → הסתר
                if (hasCollapsedAncestor(idx)) {
                    item.style.display = 'none';
                }
            }
        });

        // שלב 3: עדכן את כפתורי ההרחבה לכל פריט
        const headingsArray = Array.from(document.querySelectorAll('#docs-viewer-content h1, h2, h3, h4, h5, h6'));
        tocItems.forEach(item => {
            const itemIndex = parseInt(item.dataset.index);
            if (!Number.isNaN(itemIndex) && !item.classList.contains('filtered-out')) {
                updateExpandButtonState(item, itemIndex, headingsArray, maxLevelNum);
            }
        });

        // שלב 4: קפל פריטים שהילדים הישירים שלהם אינם נראים במסנן
        tocItems.forEach(item => {
            if (item.classList.contains('has-children') && !item.classList.contains('filtered-out')) {
                const expandBtn = item.querySelector('.docs-toc-expand-btn');
                if (expandBtn && expandBtn.style.display === 'none') {
                    item.classList.add('collapsed');
                }
            }
        });

        console.log(`🔍 סינון תוכן עניינים: מציג רמות 1-${maxLevel === 'all' ? '6' : maxLevel}`);
    },
    
    updateNavigationButtons() {
        const prevBtn = document.getElementById('docs-toc-prev-btn');
        const nextBtn = document.getElementById('docs-toc-next-btn');
        
        if (!prevBtn || !nextBtn) return;
        
        // בדוק אם יש מסמך קודם
        if (this.currentDocIndex <= 0) {
            prevBtn.disabled = true;
            prevBtn.title = 'אין מסמך קודם';
        } else {
            prevBtn.disabled = false;
            const prevDoc = this.allDocs[this.currentDocIndex - 1];
            prevBtn.title = `← ${prevDoc.title}`;
        }
        
        // בדוק אם יש מסמך הבא
        if (this.currentDocIndex >= this.allDocs.length - 1) {
            nextBtn.disabled = true;
            nextBtn.title = 'אין מסמך הבא';
        } else {
            nextBtn.disabled = false;
            const nextDoc = this.allDocs[this.currentDocIndex + 1];
            nextBtn.title = `${nextDoc.title} →`;
        }
    },
    
    navigateToPrevDoc() {
        if (this.currentDocIndex > 0) {
            const prevDoc = this.allDocs[this.currentDocIndex - 1];
            this.loadDoc(prevDoc.file, prevDoc.title);
        }
    },
    
    navigateToNextDoc() {
        if (this.currentDocIndex < this.allDocs.length - 1) {
            const nextDoc = this.allDocs[this.currentDocIndex + 1];
            this.loadDoc(nextDoc.file, nextDoc.title);
        }
    },
    
    toggleTocItem(itemElement) {
        itemElement.classList.toggle('collapsed');
    },
    
    toggleTocChildren(itemElement, headingsArray) {
        const isCollapsed = itemElement.classList.contains('collapsed');
        const itemIndex = parseInt(itemElement.dataset.index);
        const itemLevel = parseInt(itemElement.className.match(/level-(\d+)/)[1]);
        
        // קבל את מקסימום הרמה המותרת כרגע
        const levelSelect = document.getElementById('docs-toc-level-filter');
        const maxAllowedLevel = levelSelect && levelSelect.value !== 'all' ? parseInt(levelSelect.value) : 6;
        
        if (isCollapsed) {
            // פתיחה - הצג רק את הילדים הישירים (רמה אחת למטה)
            itemElement.classList.remove('collapsed');
            
            let nextIndex = itemIndex + 1;
            
            while (nextIndex < headingsArray.length) {
                const nextLevel = parseInt(headingsArray[nextIndex].tagName.substring(1));
                
                // אם הגענו לכותרת באותה רמה או נמוכה יותר, עצור
                if (nextLevel <= itemLevel) break;
                
                const nextItem = document.querySelector(`.docs-toc-item[data-index="${nextIndex}"]`);
                if (nextItem) {
                    // הצג רק ילדים ישירים (רמה מיידית למטה) שמותרים בפילטר
                    if (nextLevel === itemLevel + 1 && nextLevel <= maxAllowedLevel) {
                        nextItem.style.display = '';
                        // עדכן את מצב החץ של הפריט הזה
                        updateExpandButtonState(nextItem, nextIndex, headingsArray, maxAllowedLevel);
                    }
                    // ילדים עמוקים יותר יישארו מוסתרים (יפתחו בנפרד)
                }
                
                nextIndex++;
            }
            
        } else {
            // קיפול - הסתר את כל הילדים (כולל נכדים)
            itemElement.classList.add('collapsed');
            
            let nextIndex = itemIndex + 1;
            while (nextIndex < headingsArray.length) {
                const nextLevel = parseInt(headingsArray[nextIndex].tagName.substring(1));
                
                // אם הגענו לכותרת באותה רמה או נמוכה יותר, עצור
                if (nextLevel <= itemLevel) break;
                
                const nextItem = document.querySelector(`.docs-toc-item[data-index="${nextIndex}"]`);
                if (nextItem) {
                    nextItem.style.display = 'none';
                    // קפל גם את הפריט עצמו אם היה פתוח
                    nextItem.classList.add('collapsed');
                }
                
                nextIndex++;
            }
        }
    }
}

// פונקציה לעדכון מצב כפתור ההרחבה
function updateExpandButtonState(itemElement, itemIndex, headingsArray, maxAllowedLevel) {
    const itemLevel = parseInt(itemElement.className.match(/level-(\d+)/)[1]);
    const expandBtn = itemElement.querySelector('.docs-toc-expand-btn');

    if (!expandBtn) return;

    // בדיקה אך ורק לילדים ישירים (level+1) ובהתאם למסנן
    let hasDirectChildrenInFilter = false;
    let firstDirectChildIndex = -1;
    let idx = itemIndex + 1;
    while (idx < headingsArray.length) {
        const nextLevel = parseInt(headingsArray[idx].tagName.substring(1));
        if (nextLevel <= itemLevel) break; // יציאה מהתחום של ילדים
        if (nextLevel === itemLevel + 1) {
            // זהו ילד ישיר
            if (nextLevel <= maxAllowedLevel) {
                hasDirectChildrenInFilter = true;
                firstDirectChildIndex = idx;
            }
            break; // אין צורך לבדוק נכדים בשלב זה
        }
        idx++;
    }

    // הצג או הסתר את הכפתור בהתאם
    if (hasDirectChildrenInFilter) {
        expandBtn.style.display = '';

        // קבע מצב פתוח/סגור לפי תצוגת הילד הישיר הראשון
        if (firstDirectChildIndex >= 0) {
            const childItem = document.querySelector(`.docs-toc-item[data-index="${firstDirectChildIndex}"]`);
            if (childItem) {
                if (childItem.style.display !== 'none') {
                    itemElement.classList.remove('collapsed'); // פתוח → חץ ▼
                } else {
                    itemElement.classList.add('collapsed'); // סגור → חץ ◀
                }
            }
        }
    } else {
        expandBtn.style.display = 'none';
    }
}

// פונקציה ליצירת תוכן עניינים אוטומטי - רשימה שטוחה עם כפתורי הרחבה
function generateTableOfContents() {
    const content = document.getElementById('docs-viewer-content');
    const toc = document.getElementById('docs-toc');
    const tocList = document.getElementById('docs-toc-list');
    const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
    
    // אם יש פחות מ-3 כותרות, הסתר את תוכן העניינים
    if (headings.length < 3) {
        toc.style.display = 'none';
        return;
    }
    
    // נקה את הרשימה
    tocList.innerHTML = '';
    
    // המר headings למערך כדי לבדוק יחסים
    const headingsArray = Array.from(headings);
    
    // צור פריט בתוכן עניינים לכל כותרת (רשימה שטוחה כמו קודם)
    headings.forEach((heading, index) => {
        const level = parseInt(heading.tagName.substring(1)); // h1 -> 1, h2 -> 2, etc.
        const id = heading.id || `heading-${index}`;
        heading.id = id; // וודא שיש ID לכותרת
        
        const li = document.createElement('li');
        li.className = `docs-toc-item level-${level}`;
        li.dataset.index = index;
        
        // בדוק אם יש כותרת ברמה נמוכה יותר אחרי זו (ברמה הבאה ישירות)
        let hasChildren = false;
        if (index < headingsArray.length - 1) {
            // חפש את הכותרת הבאה שהיא ברמה גבוהה יותר (מספר גדול יותר)
            for (let i = index + 1; i < headingsArray.length; i++) {
                const nextLevel = parseInt(headingsArray[i].tagName.substring(1));
                
                // אם הגענו לכותרת באותה רמה או נמוכה יותר, עצור
                if (nextLevel <= level) break;
                
                // מצאנו כותרת ברמה גבוהה יותר - יש ילדים!
                hasChildren = true;
                break;
            }
        }
        
        // אם יש "ילדים", הוסף כפתור הרחבה
        if (hasChildren) {
            li.classList.add('has-children');
            
            const expandBtn = document.createElement('button');
            expandBtn.className = 'docs-toc-expand-btn';
            expandBtn.onclick = (e) => {
                e.stopPropagation();
                window.docsModule.toggleTocChildren(li, headingsArray);
            };
            li.appendChild(expandBtn);
        }
        
        const link = document.createElement('a');
        link.href = `#${id}`;
        link.className = 'docs-toc-link';
        link.textContent = heading.textContent;
        
        // טיפול בקליק - גלילה חלקה
        link.addEventListener('click', (e) => {
            e.preventDefault();
            heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
            updateActiveTocItem(link);
        });
        
        li.appendChild(link);
        tocList.appendChild(li);
    });
    
    // הצג את תוכן העניינים
    toc.style.display = 'block';
    
    // הפעל scroll spy
    setupScrollSpy();
}

// מעקב אחר מיקום הגלילה והדגשת הכותרת הפעילה
function setupScrollSpy() {
    const content = document.getElementById('docs-viewer-content');
    const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
    const tocLinks = document.querySelectorAll('.docs-toc-link');
    
    if (headings.length === 0 || tocLinks.length === 0) return;
    
    // בדוק אילו כותרות נמצאות ב-viewport
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                tocLinks.forEach(link => {
                    if (link.getAttribute('href') === `#${id}`) {
                        updateActiveTocItem(link);
                    }
                });
            }
        });
    }, { 
        rootMargin: '-100px 0px -66%', // הדגש כותרת רק כשהיא באזור העליון של המסך
        threshold: 0.5
    });
    
    // עקוב אחרי כל הכותרות
    headings.forEach(heading => observer.observe(heading));
}

// עדכון הכותרת הפעילה בתוכן עניינים
function updateActiveTocItem(activeLink) {
    document.querySelectorAll('.docs-toc-link').forEach(link => {
        link.classList.remove('active');
    });
    activeLink.classList.add('active');
}

