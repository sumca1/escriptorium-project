// ========================================
// טוען נתונים אמיתיים מהמערכת (Real Data Loader)
// ========================================

import terminalConfig from './terminal-config.js';

class DataLoader {
    constructor() {
        this.cache = {};
        this.cacheTTL = 30000; // 30 שניות
    }

    // ========================================
    // נתוני קבצים מ-SESSION_LOG.md
    // ========================================
    async getSessionLog() {
        if (this.isCached('sessionLog')) {
            return this.cache.sessionLog.data;
        }

        try {
            const response = await fetch('docs/SESSION_LOG.md');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const text = await response.text();
            
            const data = this.parseSessionLog(text);
            this.setCache('sessionLog', data);
            return data;
        } catch (error) {
            console.error('שגיאה בטעינת SESSION_LOG:', error);
            return this.getDefaultSessionLog();
        }
    }

    parseSessionLog(text) {
        const sessions = [];
        const lines = text.split('\n');
        let currentSession = null;

        for (const line of lines) {
            if (line.startsWith('### Session -')) {
                if (currentSession) sessions.push(currentSession);
                currentSession = {
                    date: this.extractDate(line),
                    files: [],
                    actions: []
                };
            } else if (currentSession && line.includes('Files Modified:')) {
                // נמשיך לאסוף קבצים
            } else if (currentSession && line.startsWith('- `')) {
                const file = line.match(/`([^`]+)`/)?.[1];
                if (file) currentSession.files.push(file);
            }
        }

        if (currentSession) sessions.push(currentSession);
        return { sessions, lastUpdate: new Date() };
    }

    // ========================================
    // נתוני מצב מ-CURRENT_STATE.md
    // ========================================
    async getCurrentState() {
        if (this.isCached('currentState')) {
            return this.cache.currentState.data;
        }

        try {
            const response = await fetch('docs/CURRENT_STATE.md');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const text = await response.text();
            
            const data = this.parseCurrentState(text);
            this.setCache('currentState', data);
            return data;
        } catch (error) {
            console.error('שגיאה בטעינת CURRENT_STATE:', error);
            return this.getDefaultCurrentState();
        }
    }

    parseCurrentState(text) {
        const lines = text.split('\n');
        const state = {
            components: [],
            issues: [],
            progress: 0,
            lastUpdate: null
        };

        for (const line of lines) {
            if (line.includes('Last Updated:')) {
                state.lastUpdate = line.split(':')[1]?.trim();
            }
            if (line.includes('✅') || line.includes('⚠️') || line.includes('❌')) {
                const component = {
                    name: line.replace(/[✅⚠️❌]/g, '').trim(),
                    status: line.includes('✅') ? 'success' : line.includes('⚠️') ? 'warning' : 'error'
                };
                state.components.push(component);
            }
        }

        return state;
    }

    // ========================================
    // נתוני Docker (זמני - נתונים סטטיים)
    // ========================================
    async getDockerStatus() {
        if (this.isCached('dockerStatus')) {
            return this.cache.dockerStatus.data;
        }

        // זמני: משתמש בנתונים סטטיים כי Terminal Server לא זמין
        // TODO: לתקן את Terminal Server להכיר /execute endpoint
        console.info('📦 טוען נתוני Docker סטטיים (Terminal Server לא זמין)');
        const data = this.getDefaultDockerStatus();
        this.setCache('dockerStatus', data);
        return data;

        /* // קוד מקורי - כשה-Terminal Server יעבוד:
        try {
            const result = await terminalConfig.executeCommand('docker ps --format "{{.Names}},{{.Status}},{{.State}}"');
            
            const containers = [];
            if (result.output) {
                const lines = result.output.split('\n').filter(l => l.trim());
                for (const line of lines) {
                    const [name, status, state] = line.split(',');
                    containers.push({
                        name: name?.trim() || 'unknown',
                        status: status?.trim() || 'unknown',
                        state: state?.trim() || 'unknown',
                        isRunning: state?.includes('running') || false
                    });
                }
            }

            const data = { containers, lastUpdate: new Date() };
            this.setCache('dockerStatus', data);
            return data;
        } catch (error) {
            console.warn('לא ניתן לקבל סטטוס Docker, משתמש בברירת מחדל:', error);
            return this.getDefaultDockerStatus();
        }
        */
    }

    // ========================================
    // נתוני קבצים בפרויקט
    // ========================================
    async getProjectFiles() {
        if (this.isCached('projectFiles')) {
            return this.cache.projectFiles.data;
        }

        try {
            // ננסה לקרוא מ-.file-changes-state.json אם קיים
            const response = await fetch('../../../.file-changes-state.json');
            const data = await response.json();
            
            this.setCache('projectFiles', data);
            return data;
        } catch (error) {
            console.warn('לא נמצא .file-changes-state.json, יוצר נתונים בסיסיים');
            return this.getDefaultProjectFiles();
        }
    }

    // ========================================
    // ספריית סקריפטים
    // ========================================
    async getAvailableScripts() {
        return {
            deploy: [
                { name: 'Deploy Dev', path: '.\\escriptorium\\scripts\\deploy\\deploy-dev.ps1', icon: '🚀' },
                { name: 'Deploy Test', path: '.\\escriptorium\\scripts\\deploy\\deploy-test.ps1', icon: '🧪' },
                { name: 'Deploy Prod', path: '.\\escriptorium\\scripts\\deploy\\deploy-prod.ps1', icon: '🏭' }
            ],
            build: [
                { name: 'Quick Build', path: '.\\escriptorium\\scripts\\build\\build-and-deploy.ps1 -Quick', icon: '⚡' },
                { name: 'Full Build', path: '.\\escriptorium\\scripts\\build\\build-and-deploy.ps1 -Full', icon: '🔨' },
                { name: 'Frontend Only', path: '.\\escriptorium\\scripts\\build\\build-frontend.ps1', icon: '🎨' }
            ],
            utilities: [
                { name: 'Sync Environments', path: '.\\escriptorium\\scripts\\utilities\\sync_environments.ps1', icon: '🔄' },
                { name: 'Verify Deployment', path: '.\\escriptorium\\scripts\\utilities\\verify-deployment.ps1', icon: '✅' },
                { name: 'Check Requirements', path: '.\\escriptorium\\scripts\\utilities\\check-requirements.ps1', icon: '📋' }
            ]
        };
    }

    // ========================================
    // Cache Management
    // ========================================
    isCached(key) {
        if (!this.cache[key]) return false;
        const age = Date.now() - this.cache[key].timestamp;
        return age < this.cacheTTL;
    }

    setCache(key, data) {
        this.cache[key] = {
            data,
            timestamp: Date.now()
        };
    }

    clearCache() {
        this.cache = {};
    }

    // ========================================
    // ברירות מחדל (Defaults)
    // ========================================
    getDefaultSessionLog() {
        return {
            sessions: [
                {
                    date: new Date().toISOString(),
                    files: ['SESSION_LOG.md', 'CURRENT_STATE.md'],
                    actions: ['עדכון תיעוד']
                }
            ],
            lastUpdate: new Date()
        };
    }

    getDefaultCurrentState() {
        return {
            components: [
                { name: 'Frontend', status: 'success' },
                { name: 'Backend', status: 'success' },
                { name: 'Docker', status: 'warning' }
            ],
            issues: [],
            progress: 85,
            lastUpdate: new Date().toISOString()
        };
    }

    getDefaultDockerStatus() {
        return {
            containers: [
                { name: 'escriptorium-web', status: 'Up', state: 'running', isRunning: true },
                { name: 'escriptorium-nginx', status: 'Up', state: 'running', isRunning: true },
                { name: 'escriptorium-postgres', status: 'Up', state: 'running', isRunning: true }
            ],
            lastUpdate: new Date()
        };
    }

    getDefaultProjectFiles() {
        return {
            modified: [
                { path: 'SESSION_LOG.md', size: '45.2 KB', time: 'לפני שעה' },
                { path: 'CURRENT_STATE.md', size: '28.7 KB', time: 'לפני 30 דקות' }
            ],
            new: [
                { path: 'escriptorium/ui/control-center/dashboard.html', size: '65.2 KB', time: 'עכשיו' }
            ],
            deleted: []
        };
    }

    extractDate(line) {
        const match = line.match(/Session - (.+?) -/);
        return match ? match[1] : new Date().toISOString();
    }
}

// ייצוא singleton
const dataLoader = new DataLoader();
export default dataLoader;
