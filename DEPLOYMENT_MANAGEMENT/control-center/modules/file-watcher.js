// ========================================
// File Watcher - עדכון חכם רק כשיש שינוי (Smart Updates Only on Change)
// ========================================

class FileWatcher {
    constructor() {
        this.listeners = new Map();
        this.lastModified = new Map();
        this.checkInterval = 2000; // בדיקה כל 2 שניות
        this.isRunning = false;
    }

    // ========================================
    // התחל מעקב (Start Watching)
    // ========================================
    startWatching(files, callback) {
        if (this.isRunning) {
            console.log('⚠️ File Watcher כבר פועל');
            return;
        }

        console.log('👁️ מתחיל File Watcher חכם...');
        this.isRunning = true;
        this.files = files;
        this.callback = callback;

        // בדיקה ראשונית
        this.checkFiles();

        // בדיקה מחזורית
        this.intervalId = setInterval(() => {
            this.checkFiles();
        }, this.checkInterval);
    }

    // ========================================
    // בדוק שינויים בקבצים (Check for Changes)
    // ========================================
    async checkFiles() {
        let hasChanges = false;
        const changedFiles = [];

        for (const file of this.files) {
            try {
                const response = await fetch(file, { method: 'HEAD' });
                if (!response.ok) continue;

                const lastModified = response.headers.get('Last-Modified');
                const previousModified = this.lastModified.get(file);

                if (previousModified && lastModified !== previousModified) {
                    hasChanges = true;
                    changedFiles.push(file);
                    console.log(`📝 קובץ השתנה: ${file}`);
                }

                this.lastModified.set(file, lastModified);
            } catch (error) {
                console.warn(`⚠️ שגיאה בבדיקת ${file}:`, error.message);
            }
        }

        // אם יש שינויים - קרא ל-callback
        if (hasChanges) {
            console.log(`🔄 זוהו ${changedFiles.length} שינויים - מעדכן תצוגה...`);
            if (this.callback) {
                this.callback(changedFiles);
            }
        }
    }

    // ========================================
    // עצור מעקב (Stop Watching)
    // ========================================
    stopWatching() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
            this.isRunning = false;
            console.log('🛑 File Watcher נעצר');
        }
    }

    // ========================================
    // שנה מרווח בדיקה (Change Check Interval)
    // ========================================
    setCheckInterval(ms) {
        this.checkInterval = ms;
        if (this.isRunning) {
            this.stopWatching();
            this.startWatching(this.files, this.callback);
        }
    }

    // ========================================
    // קבל סטטוס (Get Status)
    // ========================================
    getStatus() {
        return {
            isRunning: this.isRunning,
            checkInterval: this.checkInterval,
            trackedFiles: this.files ? this.files.length : 0,
            lastChecked: new Date().toLocaleTimeString('he-IL')
        };
    }
}

// ייצא instance יחיד
const fileWatcher = new FileWatcher();
export default fileWatcher;
