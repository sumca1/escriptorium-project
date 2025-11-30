// ========================================
// Service Worker - Auto-Start Terminal Server
// ========================================

const TERMINAL_SERVER_PORT = 3001;
const CHECK_INTERVAL = 5000; // 5 seconds

let serverCheckInterval = null;

// התקנה
self.addEventListener('install', (event) => {
    console.log('🔧 Service Worker מותקן...');
    self.skipWaiting();
});

// הפעלה
self.addEventListener('activate', (event) => {
    console.log('�? Service Worker מופעל!');
    event.waitUntil(clients.claim());
    
    // התחל לבדוק את השרת
    startServerCheck();
});

// בדיקת חיבור לשרת
async function checkServerConnection() {
    try {
        const response = await fetch(`http://localhost:${TERMINAL_SERVER_PORT}/status`, {
            method: 'GET',
            mode: 'cors'
        });
        
        if (response.ok) {
            console.log('�? Terminal Server פעיל');
            return true;
        }
    } catch (error) {
        console.log('�? Terminal Server לא זמין - מנסה להפעיל...');
        return false;
    }
    return false;
}

// הפעלת השרת באמצעות PowerShell
async function startTerminalServer() {
    try {
        // שלח הודעה לכל הלקוחות להפעיל את השרת
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'START_TERMINAL_SERVER',
                command: 'node terminal-server.js'
            });
        });
        
        console.log('📡 שלח בקשה להפעלת Terminal Server');
    } catch (error) {
        console.error('�? שגיאה בהפעלת Terminal Server:', error);
    }
}

// מעקב אחר מצב השרת
function startServerCheck() {
    if (serverCheckInterval) {
        clearInterval(serverCheckInterval);
    }
    
    serverCheckInterval = setInterval(async () => {
        const isConnected = await checkServerConnection();
        
        if (!isConnected) {
            await startTerminalServer();
        }
    }, CHECK_INTERVAL);
    
    // בדיקה ראשונית מיידית
    checkServerConnection().then(isConnected => {
        if (!isConnected) {
            startTerminalServer();
        }
    });
}

// טיפול בהודעות מהלקוח
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'CHECK_SERVER') {
        checkServerConnection().then(isConnected => {
            event.source.postMessage({
                type: 'SERVER_STATUS',
                connected: isConnected
            });
        });
    }
});
