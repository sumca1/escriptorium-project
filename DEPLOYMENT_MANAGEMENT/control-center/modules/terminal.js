// ========================================
// מודול טרמינל (Terminal Module)
// ========================================

export async function init() {
    console.log('💻 מאתחל מודול טרמינל (Initializing Terminal Module)');
    await renderTerminal();
}

async function renderTerminal() {
    const container = document.getElementById('terminal');
    
    if (!container) {
        console.warn('⚠️ Terminal container not found');
        return;
    }
    
    // Clear existing content  
    container.innerHTML = '';
    
    container.innerHTML = `
        <div class="card" style="margin-bottom: 1.5rem;">
            <div class="card-header">
                <h3 class="card-title">💻 PowerShell Terminal</h3>
            </div>
            <div style="padding: 1rem;">
                <div style="background: #1e1e1e; border-radius: 8px; padding: 1rem; font-family: 'Consolas', 'Courier New', monospace; color: #d4d4d4; min-height: 400px; max-height: 600px; overflow-y: auto;" id="terminal-output">
                    <div style="color: #4ec9b0;">מרכז הבקרה V2 - PowerShell Terminal</div>
                    <div style="color: #6a9955;">עדכן אחרון: ${new Date().toLocaleString('he-IL')}</div>
                    <div style="margin-top: 1rem; color: #ce9178;">PS > </div>
                </div>
                
                <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                    <input 
                        type="text" 
                        id="terminal-input" 
                        placeholder="הקלד פקודת PowerShell..."
                        style="flex: 1; padding: 0.75rem; border: 2px solid #3b82f6; border-radius: 8px; font-family: 'Consolas', monospace; font-size: 1rem;"
                        onkeypress="if(event.key === 'Enter') window.terminalModule.executeCommand()"
                    />
                    <button 
                        class="btn btn-success" 
                        onclick="window.terminalModule.executeCommand()"
                        style="padding: 0.75rem 1.5rem; white-space: nowrap;">
                        ▶ הרץ
                    </button>
                    <button 
                        class="btn btn-warning" 
                        onclick="window.terminalModule.clearTerminal()"
                        style="padding: 0.75rem 1.5rem;">
                        🗑️ נקה
                    </button>
                </div>
                
                <div style="margin-top: 1rem;">
                    <details style="background: #f8fafc; padding: 1rem; border-radius: 8px;">
                        <summary style="cursor: pointer; font-weight: 600; color: #475569;">
                            📚 פקודות מומלצות (לחץ להצגה)
                        </summary>
                        <div style="margin-top: 1rem; display: grid; gap: 0.5rem;" id="command-suggestions">
                            <button class="btn btn-sm btn-info" onclick="window.terminalModule.insertCommand('Get-Date')" style="text-align: right; justify-content: flex-end;">
                                📅 Get-Date - תאריך ושעה
                            </button>
                            <button class="btn btn-sm btn-info" onclick="window.terminalModule.insertCommand('docker ps')" style="text-align: right; justify-content: flex-end;">
                                🐳 docker ps - קונטיינרים פועלים
                            </button>
                            <button class="btn btn-sm btn-info" onclick="window.terminalModule.insertCommand('docker ps -a')" style="text-align: right; justify-content: flex-end;">
                                📦 docker ps -a - כל הקונטיינרים
                            </button>
                            <button class="btn btn-sm btn-info" onclick="window.terminalModule.insertCommand('Get-ChildItem')" style="text-align: right; justify-content: flex-end;">
                                📁 Get-ChildItem - רשימת קבצים
                            </button>
                            <button class="btn btn-sm btn-info" onclick="window.terminalModule.insertCommand('$PSVersionTable.PSVersion')" style="text-align: right; justify-content: flex-end;">
                                🔧 גרסת PowerShell
                            </button>
                        </div>
                    </details>
                </div>
                
                <div style="margin-top: 1rem; padding: 1rem; background: #fef3c7; border-radius: 8px; border-right: 4px solid #f59e0b;">
                    <strong style="color: #92400e;">💡 טיפ:</strong>
                    <span style="color: #78350f;">לחץ על אחת הפקודות המומלצות למעלה, או הקלד פקודה משלך.</span>
                </div>
            </div>
        </div>
    `;
    
    // Focus on input
    setTimeout(() => {
        const input = document.getElementById('terminal-input');
        if (input) input.focus();
    }, 100);
}

// Terminal functions
async function executeCommand() {
    const input = document.getElementById('terminal-input');
    const output = document.getElementById('terminal-output');
    
    if (!input || !output) return;
    
    const command = input.value.trim();
    if (!command) return;
    
    // Add command to output
    const commandLine = document.createElement('div');
    commandLine.innerHTML = `<div style="color: #ce9178; margin-top: 1rem;">PS > ${escapeHtml(command)}</div>`;
    output.appendChild(commandLine);
    
    // Clear input
    input.value = '';
    
    // Show loading
    const loadingLine = document.createElement('div');
    loadingLine.innerHTML = '<div style="color: #569cd6;">⏳ מריץ פקודה...</div>';
    loadingLine.id = 'loading-line';
    output.appendChild(loadingLine);
    
    // Scroll to bottom
    output.scrollTop = output.scrollHeight;
    
    try {
        // Execute via terminal server
        const response = await fetch('http://localhost:3001/exec', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                command: command,
                cwd: 'I:\\OCR_Arabic_Testing\\BiblIA_dataset-project\\BiblIA_dataset\\escriptorium'
            })
        });
        
        const data = await response.json();
        
        // Remove loading
        if (loadingLine && loadingLine.parentNode) {
            loadingLine.remove();
        }
        
        // Add result
        const resultLine = document.createElement('div');
        if (data.success) {
            const outputText = data.stdout || '(ללא פלט)';
            resultLine.innerHTML = `<div style="color: #d4d4d4; white-space: pre-wrap; margin-top: 0.5rem;">${escapeHtml(outputText)}</div>`;
            if (data.stderr) {
                resultLine.innerHTML += `<div style="color: #f48771; margin-top: 0.5rem;">⚠️ ${escapeHtml(data.stderr)}</div>`;
            }
        } else {
            resultLine.innerHTML = `<div style="color: #f48771; margin-top: 0.5rem;">❌ שגיאה: ${escapeHtml(data.error || data.stderr || 'Unknown error')}</div>`;
        }
        output.appendChild(resultLine);
        
    } catch (error) {
        // Remove loading
        if (loadingLine && loadingLine.parentNode) {
            loadingLine.remove();
        }
        
        const errorLine = document.createElement('div');
        errorLine.innerHTML = `
            <div style="color: #f48771; margin-top: 0.5rem;">
                ❌ שגיאה בחיבור לשרת<br>
                <span style="font-size: 0.9rem; opacity: 0.8;">וודא ש-Terminal Server רץ על http://localhost:3001</span>
            </div>
        `;
        output.appendChild(errorLine);
    }
    
    // Scroll to bottom
    output.scrollTop = output.scrollHeight;
}

function clearTerminal() {
    const output = document.getElementById('terminal-output');
    if (!output) return;
    
    output.innerHTML = `
        <div style="color: #4ec9b0;">מרכז הבקרה V2 - PowerShell Terminal</div>
        <div style="color: #6a9955;">עדכן אחרון: ${new Date().toLocaleString('he-IL')}</div>
        <div style="margin-top: 1rem; color: #ce9178;">PS > </div>
    `;
}

function insertCommand(command) {
    const input = document.getElementById('terminal-input');
    if (input) {
        input.value = command;
        input.focus();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export functions to window
if (typeof window !== 'undefined') {
    window.terminalModule = {
        executeCommand,
        clearTerminal,
        insertCommand
    };
}
