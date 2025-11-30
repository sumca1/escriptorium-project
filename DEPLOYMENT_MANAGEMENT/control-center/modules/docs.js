// ========================================
// מודול תיעוד (Documentation Module)
// ========================================

import { marked } from 'https://cdn.jsdelivr.net/npm/marked@11/+esm';

export async function init() {
    console.log('מאתחל מודול תיעוד (Initializing Documentation Module)');
    await renderDocs();
}

async function renderDocs() {
    const container = document.getElementById('docs-content');
    
    // רשימת מדריכים מתיקיית escriptorium/
    const guides = [
        {
            category: '🚀 התחלה מהירה',
            items: [
                { title: 'Quick Start - התחלה מהירה', file: '../../../QUICK_START.md', desc: 'מדריך התחלה מהירה', readTime: '3 דקות' },
                { title: 'README - eScriptorium', file: '../../../README.md', desc: 'מבוא לפרויקט', readTime: '5 דקות' }
            ]
        },
        {
            category: '📦 פריסה ובנייה (Deployment)',
            items: [
                { title: 'Smart Deploy V2 - מדריך שימוש', file: 'docs/smart-deployment-system.md', desc: 'מערכת פריסה חכמה', readTime: '5 דקות' },
                { title: 'Deployment Strategy', file: 'docs/guides/deployment-strategy.md', desc: 'אסטרטגיית פריסה', readTime: '8 דקות' },
                { title: 'Environments Guide', file: 'docs/guides/environments-real-world-guide.md', desc: 'מדריך סביבות', readTime: '10 דקות' }
            ]
        },
        {
            category: '🎛️ מרכז הבקרה',
            items: [
                { title: 'Dashboard Integration', file: 'ui/control-center/DASHBOARD_INTEGRATION.md', desc: 'שילוב דשבורד', readTime: '10 דקות' },
                { title: 'Control Center Guide', file: 'docs/guides/control-center-guide.md', desc: 'מדריך מרכז בקרה', readTime: '12 דקות' },
                { title: 'START HERE', file: 'ui/control-center/START_HERE.md', desc: 'מדריך הפעלה', readTime: '5 דקות' },
                { title: 'Dashboard Guide', file: 'ui/control-center/DASHBOARD_GUIDE.md', desc: 'מדריך הדשבורד', readTime: '8 דקות' }
            ]
        },
        {
            category: '🏗️ ארכיטקטורה',
            items: [
                { title: 'ארכיטקטורת סקריפטים', file: 'docs/architecture/scripts-architecture.md', desc: 'ארכיטקטורת סקריפטים מפורטת', readTime: '8 דקות' },
                { title: 'How It Works', file: 'docs/guides/how-it-works.md', desc: 'איך המערכת עובדת', readTime: '15 דקות' },
                { title: 'System Summary', file: 'docs/system-summary.md', desc: 'סיכום מערכת', readTime: '10 דקות' }
            ]
        },
        {
            category: '🌐 תרגום (Translation)',
            items: [
                { title: 'Translation Workflow', file: '.github/instructions/translation-workflow.instructions.md', desc: 'תהליך עבודה של תרגום', readTime: '7 דקות' }
            ]
        },
        {
            category: '📊 ניהול פרויקט',
            items: [
                { title: 'Organization Complete', file: 'project-docs/ORGANIZATION_COMPLETE.md', desc: 'ארגון הפרויקט', readTime: '5 דקות' },
                { title: 'Current Status & Plan', file: 'management/reports/current-status-and-plan.md', desc: 'מצב ותוכנית', readTime: '8 דקות' },
                { title: 'Completion Plan', file: 'management/reports/completion-plan.md', desc: 'תוכנית השלמה', readTime: '10 דקות' }
            ]
        }
    ];
    
    let html = `
        <div class="docs-container">
            <div class="docs-header">
                <h2>📚 מרכז התיעוד - eScriptorium</h2>
                <p class="docs-subtitle">כל המדריכים והתיעוד של תיקיית escriptorium במקום אחד</p>
            </div>
            
            <div class="docs-search" style="margin-bottom: 2rem;">
                <input type="text" id="docs-search-input" class="search-input" placeholder="🔍 חפש מדריך..." style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">
            </div>
    `;
    
    guides.forEach(category => {
        html += `
            <div class="docs-category" data-category="${category.category}">
                <h3 class="docs-category-title">${category.category}</h3>
                <div class="docs-grid">
        `;
        
        category.items.forEach(item => {
            html += `
                <div class="doc-card" data-title="${item.title.toLowerCase()}" data-desc="${item.desc.toLowerCase()}">
                    <div class="doc-card-header">
                        <h4 class="doc-title">${item.title}</h4>
                        ${item.readTime ? `<span class="doc-read-time">⏱️ ${item.readTime}</span>` : ''}
                    </div>
                    <p class="doc-desc">${item.desc}</p>
                    <div class="doc-card-footer">
                        <button class="btn btn-primary btn-sm" onclick="window.docsModule.loadDoc('${item.file}', '${item.title}')">
                            📖 קרא
                        </button>
                        <span class="doc-file">${item.file.split('/').pop()}</span>
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
            <div class="docs-viewer-header">
                <button class="btn btn-secondary" onclick="window.docsModule.closeViewer()">
                    ← חזור לרשימה
                </button>
                <h3 id="docs-viewer-title"></h3>
            </div>
            <div id="docs-viewer-content" class="docs-viewer-content"></div>
        </div>
        
        <style>
            .docs-container {
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .docs-header {
                text-align: center;
                margin-bottom: 2rem;
                padding: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 12px;
            }
            
            .docs-header h2 {
                margin: 0 0 0.5rem 0;
                font-size: 2rem;
            }
            
            .docs-subtitle {
                margin: 0;
                opacity: 0.9;
                font-size: 1.1rem;
            }
            
            .docs-category {
                margin-bottom: 3rem;
            }
            
            .docs-category-title {
                font-size: 1.5rem;
                margin-bottom: 1rem;
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 0.5rem;
            }
            
            .docs-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: 1.5rem;
            }
            
            .doc-card {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border-top: 4px solid #3498db;
            }
            
            .doc-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .doc-card-header {
                margin-bottom: 0.75rem;
            }
            
            .doc-title {
                margin: 0;
                color: #2c3e50;
                font-size: 1.1rem;
                font-weight: 600;
            }
            
            .doc-desc {
                color: #7f8c8d;
                font-size: 0.9rem;
                margin-bottom: 1rem;
                line-height: 1.5;
            }
            
            .doc-card-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
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
                border-radius: 12px;
                padding: 2rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .docs-viewer-header {
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 2px solid #e9ecef;
            }
            
            .docs-viewer-header h3 {
                margin: 0;
                color: #2c3e50;
                flex: 1;
            }
            
            .docs-viewer-content {
                line-height: 1.8;
                color: #2c3e50;
            }
            
            .docs-viewer-content h1,
            .docs-viewer-content h2,
            .docs-viewer-content h3 {
                color: #2c3e50;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            
            .docs-viewer-content code {
                background: #f8f9fa;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }
            
            .docs-viewer-content pre {
                background: #2c3e50;
                color: #ecf0f1;
                padding: 1.5rem;
                border-radius: 8px;
                overflow-x: auto;
            }
            
            .docs-viewer-content pre code {
                background: transparent;
                padding: 0;
                color: inherit;
            }
            
            .search-input:focus {
                outline: none;
                border-color: #3498db;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
            }
        </style>
    `;
    
    container.innerHTML = html;
    
    // חיפוש מדריכים
    const searchInput = document.getElementById('docs-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.doc-card');
            
            cards.forEach(card => {
                const title = card.dataset.title;
                const desc = card.dataset.desc;
                const matches = title.includes(query) || desc.includes(query);
                card.style.display = matches ? 'block' : 'none';
            });
        });
    }
}

// פונקציות ציבוריות
window.docsModule = {
    async loadDoc(filename, title) {
        console.log(`טוען מדריך: ${filename}`);
        
        const viewer = document.getElementById('docs-viewer');
        const container = document.querySelector('.docs-container');
        const viewerTitle = document.getElementById('docs-viewer-title');
        const viewerContent = document.getElementById('docs-viewer-content');
        
        // הצג loading
        viewerTitle.textContent = title;
        viewerContent.innerHTML = '<div style="text-align: center; padding: 3rem;"><div class="spinner"></div><p>טוען מדריך...</p></div>';
        
        container.style.display = 'none';
        viewer.style.display = 'block';
        
        try {
            // טען את הקובץ דרך השרת
            // השרת (dashboard-server.js) מחפש:
            // 1. control-center/${filename}
            // 2. escriptorium/${filename} (אם לא נמצא)
            const response = await fetch(`/${filename}`);
            if (!response.ok) throw new Error(`לא נמצא: ${filename}`);
            
            const markdown = await response.text();
            
            // המר ל-HTML
            const html = marked.parse(markdown);
            
            viewerContent.innerHTML = html;
            
            // גלול למעלה
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
        } catch (error) {
            console.error('שגיאה בטעינת מדריך:', error);
            viewerContent.innerHTML = `
                <div class="error-message" style="background: #fee; border: 1px solid #fcc; padding: 2rem; border-radius: 8px; text-align: center;">
                    <h3 style="color: #c33; margin-top: 0;">❌ שגיאה בטעינת מדריך</h3>
                    <p style="color: #666;">לא הצלחנו לטעון את הקובץ: <code>${filename}</code></p>
                    <p style="color: #999; font-size: 0.9rem;">${error.message}</p>
                    <button class="btn btn-primary" onclick="window.docsModule.closeViewer()">חזור לרשימה</button>
                </div>
            `;
        }
    },
    
    closeViewer() {
        const viewer = document.getElementById('docs-viewer');
        const container = document.querySelector('.docs-container');
        
        viewer.style.display = 'none';
        container.style.display = 'block';
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};
