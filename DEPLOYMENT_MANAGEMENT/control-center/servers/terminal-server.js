#!/usr/bin/env node
/**
 * PowerShell Terminal Server - Enhanced Version
 * שרת Node.js מתקדם שמריץ פקודות PowerShell בשביל הדשבורד
 * 
 * תכונות:
 * - תמיכה ב-PowerShell 5.1 ו-PowerShell 7 (pwsh)
 * - בחירת working directory
 * - environment variables מותאמים אישית
 * - הרצה ברקע (background jobs)
 * - timeout וbuffer מותאמים
 * 
 * הרצה: node terminal-server.js [port]
 * פורט ברירת מחדל: 3000
 */

const express = require('express');
const cors = require('cors');
const { exec, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const app = express();

// קריאת הפורט מה-arguments, environment או ברירת מחדל 3000
const PORT = process.argv[2] || process.env.TERMINAL_SERVER_PORT || process.env.PORT || 3000;

// Background jobs tracking
const backgroundJobs = new Map();
let jobIdCounter = 0;

// Detect PowerShell versions
const POWERSHELL_VERSIONS = {
    pwsh7: 'pwsh.exe',      // PowerShell 7+
    powershell: 'powershell.exe'  // PowerShell 5.1
};

// Check which PowerShell versions are available
function detectPowerShellVersions() {
    const available = {};
    
    // Check PowerShell 7
    try {
        require('child_process').execSync('pwsh.exe -v', { stdio: 'ignore' });
        available.pwsh7 = true;
    } catch {
        available.pwsh7 = false;
    }
    
    // Check PowerShell 5.1
    try {
        require('child_process').execSync('powershell.exe -v', { stdio: 'ignore' });
        available.powershell = true;
    } catch {
        available.powershell = false;
    }
    
    return available;
}

const availablePowerShell = detectPowerShellVersions();

// Middleware
app.use(cors());
app.use(express.json());

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        status: 'running',
        message: '💻 PowerShell Terminal Server Enhanced - מוכן לפעולה!',
        version: '2.0',
        powershell: availablePowerShell,
        endpoints: {
            '/exec': 'POST - הרץ פקודת PowerShell',
            '/exec-background': 'POST - הרץ פקודה ברקע',
            '/job/:id': 'GET - סטטוס job ברקע',
            '/jobs': 'GET - כל ה-jobs הפעילים',
            '/status': 'GET - סטטוס השרת',
            '/shells': 'GET - רשימת shells זמינים'
        }
    });
});

// Status endpoint
app.get('/status', (req, res) => {
    res.json({
        status: 'ok',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        platform: process.platform,
        nodeVersion: process.version,
        powershell: availablePowerShell,
        activeJobs: backgroundJobs.size,
        totalJobsRun: jobIdCounter
    });
});

// Get available shells
app.get('/shells', (req, res) => {
    res.json({
        available: availablePowerShell,
        default: availablePowerShell.pwsh7 ? 'pwsh7' : 'powershell',
        versions: POWERSHELL_VERSIONS
    });
});

// Get all background jobs
app.get('/jobs', (req, res) => {
    const jobs = Array.from(backgroundJobs.entries()).map(([id, job]) => ({
        id,
        command: job.command,
        status: job.status,
        startTime: job.startTime,
        pid: job.process?.pid || null
    }));
    
    res.json({
        count: jobs.length,
        jobs
    });
});

// Get specific job status
app.get('/job/:id', (req, res) => {
    const jobId = parseInt(req.params.id);
    const job = backgroundJobs.get(jobId);
    
    if (!job) {
        return res.status(404).json({
            success: false,
            error: `Job ${jobId} לא נמצא`
        });
    }
    
    res.json({
        id: jobId,
        command: job.command,
        status: job.status,
        startTime: job.startTime,
        endTime: job.endTime,
        duration: job.endTime ? (job.endTime - job.startTime) / 1000 : null,
        exitCode: job.exitCode,
        stdout: job.stdout,
        stderr: job.stderr,
        pid: job.process?.pid || null
    });
});

// Execute PowerShell command (synchronous - waits for completion)
app.post('/exec', (req, res) => {
    const { 
        command, 
        shell = availablePowerShell.pwsh7 ? 'pwsh7' : 'powershell',
        cwd = path.resolve(__dirname),
        timeout = 5 * 60 * 1000, // 5 minutes default
        maxBuffer = 10 * 1024 * 1024, // 10MB default
        env = {}
    } = req.body;
    
    if (!command) {
        return res.status(400).json({
            success: false,
            error: 'חסרה פקודה להרצה'
        });
    }
    
    // Validate shell
    const shellExe = POWERSHELL_VERSIONS[shell];
    if (!shellExe || !availablePowerShell[shell]) {
        return res.status(400).json({
            success: false,
            error: `Shell '${shell}' לא זמין. השתמש ב: ${Object.keys(availablePowerShell).filter(k => availablePowerShell[k]).join(', ')}`
        });
    }
    
    // Validate working directory
    if (!fs.existsSync(cwd)) {
        return res.status(400).json({
            success: false,
            error: `תיקייה לא קיימת: ${cwd}`
        });
    }
    
    console.log(`\n🚀 מריץ פקודה: ${command}`);
    console.log(`   Shell: ${shell} (${shellExe})`);
    console.log(`   CWD: ${cwd}`);
    console.log(`   ⏰ זמן: ${new Date().toLocaleString('he-IL')}`);
    
    const startTime = Date.now();
    
    // Build exec command
    const execCommand = `${shellExe} -NoProfile -ExecutionPolicy Bypass -Command "${command.replace(/"/g, '`"')}"`;
    
    // Merge environment variables
    const execEnv = { ...process.env, ...env };
    
    exec(execCommand, {
        cwd: cwd,
        maxBuffer: maxBuffer,
        timeout: timeout,
        encoding: 'utf8',
        env: execEnv
    }, (error, stdout, stderr) => {
        const duration = ((Date.now() - startTime) / 1000).toFixed(2);
        
        console.log(`   ✅ הושלם ב-${duration} שניות`);
        
        if (error) {
            console.error(`   ❌ שגיאה: ${error.message}`);
            
            return res.json({
                success: false,
                error: error.message,
                exitCode: error.code || 1,
                stdout: stdout || '',
                stderr: stderr || error.message,
                duration: parseFloat(duration),
                shell: shell,
                cwd: cwd
            });
        }
        
        // Success
        res.json({
            success: true,
            stdout: stdout || '',
            stderr: stderr || '',
            exitCode: 0,
            duration: parseFloat(duration),
            command: command,
            shell: shell,
            cwd: cwd
        });
    });
});

// Execute PowerShell command in background (non-blocking)
app.post('/exec-background', (req, res) => {
    const { 
        command, 
        shell = availablePowerShell.pwsh7 ? 'pwsh7' : 'powershell',
        cwd = path.resolve(__dirname),
        env = {}
    } = req.body;
    
    if (!command) {
        return res.status(400).json({
            success: false,
            error: 'חסרה פקודה להרצה'
        });
    }
    
    // Validate shell
    const shellExe = POWERSHELL_VERSIONS[shell];
    if (!shellExe || !availablePowerShell[shell]) {
        return res.status(400).json({
            success: false,
            error: `Shell '${shell}' לא זמין`
        });
    }
    
    // Validate working directory
    if (!fs.existsSync(cwd)) {
        return res.status(400).json({
            success: false,
            error: `תיקייה לא קיימת: ${cwd}`
        });
    }
    
    // Create job
    const jobId = ++jobIdCounter;
    const job = {
        id: jobId,
        command: command,
        shell: shell,
        cwd: cwd,
        status: 'running',
        startTime: Date.now(),
        endTime: null,
        exitCode: null,
        stdout: '',
        stderr: '',
        process: null
    };
    
    console.log(`\n🔄 מריץ פקודה ברקע (Job #${jobId}): ${command}`);
    console.log(`   Shell: ${shell} (${shellExe})`);
    console.log(`   CWD: ${cwd}`);
    
    // Spawn process
    const execEnv = { ...process.env, ...env };
    const childProcess = spawn(shellExe, [
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-Command', command
    ], {
        cwd: cwd,
        env: execEnv,
        windowsHide: true
    });
    
    job.process = childProcess;
    backgroundJobs.set(jobId, job);
    
    // Capture output
    childProcess.stdout.on('data', (data) => {
        job.stdout += data.toString();
    });
    
    childProcess.stderr.on('data', (data) => {
        job.stderr += data.toString();
    });
    
    // Handle completion
    childProcess.on('close', (code) => {
        job.status = code === 0 ? 'completed' : 'failed';
        job.exitCode = code;
        job.endTime = Date.now();
        const duration = ((job.endTime - job.startTime) / 1000).toFixed(2);
        
        console.log(`   ✅ Job #${jobId} הושלם ב-${duration} שניות (Exit: ${code})`);
        
        // Clean up after 10 minutes
        setTimeout(() => {
            backgroundJobs.delete(jobId);
            console.log(`   🧹 Job #${jobId} נמחק מהזיכרון`);
        }, 10 * 60 * 1000);
    });
    
    childProcess.on('error', (err) => {
        job.status = 'error';
        job.stderr += err.message;
        job.endTime = Date.now();
        console.error(`   ❌ Job #${jobId} נכשל: ${err.message}`);
    });
    
    // Return job ID immediately
    res.json({
        success: true,
        jobId: jobId,
        message: 'פקודה רצה ברקע',
        checkStatus: `/job/${jobId}`,
        pid: childProcess.pid
    });
});

// Error handling
app.use((err, req, res, next) => {
    console.error('❌ שגיאת שרת:', err);
    res.status(500).json({
        success: false,
        error: 'שגיאת שרת פנימית',
        details: err.message
    });
});

// Start server
app.listen(PORT, () => {
    console.log('\n╔════════════════════════════════════════════════════════════════╗');
    console.log('║  💻 PowerShell Terminal Server Enhanced v2.0                  ║');
    console.log('╚════════════════════════════════════════════════════════════════╝');
    console.log('');
    console.log(`✅ שרת רץ על http://localhost:${PORT}`);
    console.log(`📁 תיקייה: ${__dirname}`);
    console.log(`🎯 מוכן לקבל פקודות PowerShell!`);
    console.log('');
    console.log('🐚 PowerShell Versions:');
    console.log(`   ${availablePowerShell.pwsh7 ? '✅' : '❌'} PowerShell 7+ (pwsh.exe)`);
    console.log(`   ${availablePowerShell.powershell ? '✅' : '❌'} PowerShell 5.1 (powershell.exe)`);
    console.log('');
    console.log('📊 Endpoints:');
    console.log(`   GET  http://localhost:${PORT}/              - מידע על השרת`);
    console.log(`   GET  http://localhost:${PORT}/status        - סטטוס השרת`);
    console.log(`   GET  http://localhost:${PORT}/shells        - shells זמינים`);
    console.log(`   POST http://localhost:${PORT}/exec          - הרץ פקודה (blocking)`);
    console.log(`   POST http://localhost:${PORT}/exec-background - הרץ פקודה ברקע`);
    console.log(`   GET  http://localhost:${PORT}/jobs          - כל ה-jobs`);
    console.log(`   GET  http://localhost:${PORT}/job/:id       - סטטוס job`);
    console.log('');
    console.log('💡 תכונות חדשות:');
    console.log('   ✨ בחירת PowerShell version (5.1 או 7)');
    console.log('   ✨ Working directory מותאם אישית');
    console.log('   ✨ Environment variables');
    console.log('   ✨ הרצה ברקע (background jobs)');
    console.log('   ✨ Timeout ו-buffer מותאמים');
    console.log('');
    console.log('💡 לעצירת השרת: Ctrl+C');
    console.log('═══════════════════════════════════════════════════════════════════\n');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n\n👋 עוצר את השרת...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n\n👋 עוצר את השרת...');
    process.exit(0);
});
