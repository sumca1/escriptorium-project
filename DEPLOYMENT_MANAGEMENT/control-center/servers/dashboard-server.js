#!/usr/bin/env node

/**
 * ========================================
 * שרת HTTP פשוט למרכז הבקרה
 * Simple HTTP Server for Control Center
 * ========================================
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.PORT || 8080;

// MIME types
const mimeTypes = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.md': 'text/markdown; charset=utf-8'
};

// יצירת השרת
const server = http.createServer((req, res) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
    
    // פרסור URL
    const parsedUrl = url.parse(req.url);
    let pathname = parsedUrl.pathname;
    
    // ברירת מחדל - dashboard.html
    if (pathname === '/') {
        pathname = '/dashboard.html';
    }
    
    // בניית נתיב מלא
    // השרת נמצא ב-servers/, אבל הקבצים ב-app/
    // ניצור מבנה מדורג של חיפוש
    const controlCenterRoot = path.join(__dirname, '..');  // control-center/
    const appPath = path.join(controlCenterRoot, 'app', pathname);
    const controlCenterPath = path.join(controlCenterRoot, pathname);
    let filePath = appPath;  // נסה קודם ב-app/
    
    // אם הקובץ לא נמצא ב-control-center, נסה ב-escriptorium
    // זה מאפשר גישה לקבצי .md ואחרים מתיקיית escriptorium
    const tryAlternatePath = () => {
        // עלה רמות: servers/ -> control-center/ -> DEPLOYMENT_MANAGEMENT/ -> escriptorium/
        const escriptoriumRoot = path.join(__dirname, '..', '..', '..');
        return path.join(escriptoriumRoot, pathname.replace(/^\//, ''));
    };
    
    // בדיקת קיום קובץ - חיפוש מדורג
    fs.access(filePath, fs.constants.F_OK, (err) => {
        if (err) {
            // לא נמצא ב-app/, נסה ב-control-center/
            filePath = controlCenterPath;
            
            fs.access(filePath, fs.constants.F_OK, (err2) => {
                if (err2) {
                    // נסה נתיב חלופי (escriptorium root)
                    const alternatePath = tryAlternatePath();
                    
                    fs.access(alternatePath, fs.constants.F_OK, (err3) => {
                        if (err3) {
                            // גם בנתיב החלופי לא נמצא
                            res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
                            res.end(`
                                <!DOCTYPE html>
                                <html lang="he" dir="rtl">
                                <head>
                                    <meta charset="UTF-8">
                                    <title>404 - לא נמצא</title>
                                    <style>
                                        body { 
                                            font-family: Arial, sans-serif; 
                                            text-align: center; 
                                            padding: 50px;
                                            background: #f8fafc;
                                        }
                                        h1 { color: #dc2626; }
                                        code { background: #f1f5f9; padding: 0.2rem 0.5rem; border-radius: 4px; }
                                        .paths { font-size: 0.85rem; color: #64748b; margin-top: 1rem; }
                                    </style>
                                </head>
                                <body>
                                    <h1>❌ 404 - הקובץ לא נמצא</h1>
                                    <p>הנתיב המבוקש: <code>${pathname}</code></p>
                                    <div class="paths">
                                        <p>חיפשנו ב:</p>
                                        <p>• app/${pathname}</p>
                                        <p>• control-center/${pathname}</p>
                                        <p>• escriptorium/${pathname}</p>
                                    </div>
                                    <a href="/dashboard.html" style="display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px;">🏠 חזרה לדשבורד</a>
                                </body>
                                </html>
                            `);
                            return;
                        }
                        
                        // נמצא בנתיב החלופי - השתמש בו
                        filePath = alternatePath;
                        readAndSendFile(filePath, res);
                    });
                    return;
                }
                
                // נמצא ב-control-center/
                readAndSendFile(filePath, res);
            });
            return;
        }
        
        // נמצא ב-app/
        readAndSendFile(filePath, res);
    });
});

// פונקציה לקריאה ושליחת קובץ
function readAndSendFile(filePath, res) {
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(500, { 'Content-Type': 'text/html; charset=utf-8' });
            res.end(`
                <!DOCTYPE html>
                <html lang="he" dir="rtl">
                <head>
                    <meta charset="UTF-8">
                    <title>500 - שגיאת שרת</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f8fafc; }
                        h1 { color: #dc2626; }
                    </style>
                </head>
                <body>
                    <h1>❌ שגיאת שרת</h1>
                    <p>${err.message}</p>
                    <a href="/dashboard.html">🏠 חזרה לדשבורד</a>
                </body>
                </html>
            `);
            return;
        }
        
        // קביעת MIME type
        const ext = path.extname(filePath).toLowerCase();
        const contentType = mimeTypes[ext] || 'application/octet-stream';
        
        // שליחת התשובה
        res.writeHead(200, { 
            'Content-Type': contentType,
            'Access-Control-Allow-Origin': '*' // CORS
        });
        res.end(data);
    });
}

// הפעלת השרת
server.listen(PORT, () => {
    console.log('═══════════════════════════════════════════════════════════');
    console.log('🚀 מרכז הבקרה פועל! (Control Center Running!)');
    console.log('═══════════════════════════════════════════════════════════');
    console.log('');
    console.log(`🌐 פתח בדפדפן: http://localhost:${PORT}/dashboard.html`);
    console.log('');
    console.log('⚠️  לעצירה: לחץ Ctrl+C');
    console.log('═══════════════════════════════════════════════════════════');
    
    // פתיחה אוטומטית בדפדפן (Windows)
    if (process.platform === 'win32') {
        const { exec } = require('child_process');
        exec(`start http://localhost:${PORT}/dashboard.html`);
    }
});
