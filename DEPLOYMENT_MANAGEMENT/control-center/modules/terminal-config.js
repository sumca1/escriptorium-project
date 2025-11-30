/**
 * Terminal Configuration - חיפוש פורט זמין אוטומטי
 * מוצא פורט פנוי עבור Terminal Server
 */

class TerminalConfig {
    constructor() {
        this.baseUrl = null;
        this.ports = [3001, 3002, 3003, 3004, 3005, 8080, 8081, 8082]; // רשימת פורטים לנסות
        this.currentPort = null;
        this.isConnected = false;
    }

    /**
     * מצא פורט זמין ובדוק חיבור
     */
    async findAvailablePort() {
        console.log('🔍 מחפש Terminal Server זמין...');

        for (const port of this.ports) {
            try {
                const url = `http://localhost:${port}`;
                console.log(`   נסיון חיבור לפורט ${port}...`);

                // נסה לבצע status check
                const response = await fetch(`${url}/status`, {
                    method: 'GET',
                    signal: AbortSignal.timeout(1000) // timeout של שנייה
                });

                if (response.ok) {
                    this.baseUrl = url;
                    this.currentPort = port;
                    this.isConnected = true;
                    console.log(`✅ Terminal Server נמצא על פורט ${port}`);
                    return url;
                }
            } catch (error) {
                // נסיון חיבור נכשל, נמשיך לפורט הבא
                console.log(`   ❌ פורט ${port} לא זמין`);
                continue;
            }
        }

        // לא נמצא שרת פעיל
        console.warn('⚠️ לא נמצא Terminal Server פעיל');
        this.isConnected = false;
        return null;
    }

    /**
     * קבל URL של Terminal Server
     */
    async getServerUrl() {
        if (this.baseUrl && this.isConnected) {
            return this.baseUrl;
        }

        return await this.findAvailablePort();
    }

    /**
     * בדוק אם מחובר
     */
    async checkConnection() {
        if (!this.baseUrl) {
            return false;
        }

        try {
            const response = await fetch(`${this.baseUrl}/status`, {
                method: 'GET',
                signal: AbortSignal.timeout(1000)
            });
            
            this.isConnected = response.ok;
            return response.ok;
        } catch (error) {
            this.isConnected = false;
            return false;
        }
    }

    /**
     * הרץ פקודה דרך Terminal Server
     */
    async executeCommand(command, cwd = null) {
        // וודא שיש חיבור
        const serverUrl = await this.getServerUrl();
        
        if (!serverUrl) {
            throw new Error('Terminal Server לא זמין. אנא הפעל את השרת תחילה.');
        }

        try {
            const response = await fetch(`${serverUrl}/exec`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    command: command,
                    cwd: cwd || 'I:\\OCR_Arabic_Testing\\BiblIA_dataset-project\\BiblIA_dataset'
                })
            });

            if (!response.ok) {
                throw new Error(`Terminal Server error: ${response.status}`);
            }

            const result = await response.json();
            return result;

        } catch (error) {
            // נסה למצוא פורט אחר במקרה שהשרת נפל
            console.error('שגיאה בהרצת פקודה, מנסה למצוא שרת אחר...');
            this.baseUrl = null;
            this.isConnected = false;
            
            // נסה שוב עם חיפוש חדש
            const newUrl = await this.findAvailablePort();
            if (newUrl) {
                return await this.executeCommand(command, cwd);
            }
            
            throw error;
        }
    }

    /**
     * הצג הודעת חיבור למשתמש
     */
    getConnectionStatus() {
        if (this.isConnected) {
            return {
                status: 'connected',
                message: `✅ מחובר ל-Terminal Server (Port ${this.currentPort})`,
                color: '#2ecc71'
            };
        } else {
            return {
                status: 'disconnected',
                message: '⚠️ Terminal Server לא זמין - אנא הפעל את השרת',
                color: '#e74c3c'
            };
        }
    }
}

// יצירת instance גלובלי
const terminalConfig = new TerminalConfig();

// ייצוא
export default terminalConfig;
