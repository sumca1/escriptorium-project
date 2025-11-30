#!/usr/bin/env node
/**
 * Docker Status Monitor - מעדכן את הדשבורד עם נתוני Docker בזמן אמת
 * מריץ בואריוצה בשעה קובעת סטטוס Docker ומייצר JSON עבור הדשבורד
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const OUTPUT_FILE = path.join(__dirname, '../app/docker-status.json');
const UPDATE_INTERVAL = 5000; // 5 שניות

console.log('🐳 Docker Status Monitor - מתחיל...');
console.log(`📁 קובץ פלט: ${OUTPUT_FILE}`);
console.log(`⏱️  מרווח עדכון: ${UPDATE_INTERVAL}ms`);

// פונקציה להרצת פקודת Docker
function runDockerCommand(command) {
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                // Docker לא פועל או שגיאה אחרת
                resolve({ error: error.message, stderr });
                return;
            }
            resolve({ stdout, stderr });
        });
    });
}

// פונקציה לקבלת סטטוס Docker
async function getDockerStatus() {
    const status = {
        timestamp: new Date().toISOString(),
        dockerRunning: false,
        containers: [],
        summary: {
            total: 0,
            running: 0,
            stopped: 0,
            paused: 0
        }
    };

    try {
        // בדוק אם Docker פועל
        const psResult = await runDockerCommand('docker ps -a --format "{{json .}}"');
        
        if (psResult.error) {
            status.error = 'Docker Desktop לא פועל';
            return status;
        }

        status.dockerRunning = true;

        // פרוס את התוצאות
        const lines = psResult.stdout.trim().split('\n').filter(line => line);
        
        for (const line of lines) {
            try {
                const container = JSON.parse(line);
                
                const containerInfo = {
                    id: container.ID,
                    name: container.Names,
                    image: container.Image,
                    status: container.Status,
                    state: container.State,
                    ports: container.Ports || '',
                    created: container.CreatedAt,
                    isRunning: container.State === 'running',
                    isPaused: container.State === 'paused',
                    isExited: container.State === 'exited'
                };

                status.containers.push(containerInfo);
                status.summary.total++;
                
                if (containerInfo.isRunning) {
                    status.summary.running++;
                } else if (containerInfo.isPaused) {
                    status.summary.paused++;
                } else {
                    status.summary.stopped++;
                }
            } catch (parseError) {
                console.error('שגיאה בפירוש JSON:', parseError.message);
            }
        }

        // מידע נוסף - docker-compose
        const composeResult = await runDockerCommand('docker-compose ps --format json');
        if (!composeResult.error && composeResult.stdout) {
            status.composeAvailable = true;
        }

    } catch (error) {
        status.error = error.message;
    }

    return status;
}

// פונקציה לשמירת הסטטוס לקובץ
async function saveStatus() {
    try {
        const status = await getDockerStatus();
        
        // יצירת תיקייה אם לא קיימת
        const dir = path.dirname(OUTPUT_FILE);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        // שמירה לקובץ
        fs.writeFileSync(OUTPUT_FILE, JSON.stringify(status, null, 2), 'utf8');
        
        const emoji = status.dockerRunning ? '✅' : '❌';
        const msg = status.dockerRunning 
            ? `${status.summary.running}/${status.summary.total} פועלים` 
            : 'Docker כבוי';
        
        console.log(`${emoji} [${new Date().toLocaleTimeString('he-IL')}] ${msg}`);
        
    } catch (error) {
        console.error('❌ שגיאה בשמירה:', error.message);
    }
}

// הרצה ראשונה מיידית
saveStatus();

// עדכון תקופתי
setInterval(saveStatus, UPDATE_INTERVAL);

// טיפול בעצירה נקייה
process.on('SIGINT', () => {
    console.log('\n👋 עוצר Docker Status Monitor...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n👋 עוצר Docker Status Monitor...');
    process.exit(0);
});

console.log('🚀 Docker Status Monitor פעיל!');
console.log('💡 לחץ Ctrl+C לעצירה\n');
