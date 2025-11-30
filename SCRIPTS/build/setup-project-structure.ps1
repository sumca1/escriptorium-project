# ========================================
# 📁 ארגון מבנה הפרויקט
# ========================================
# יוצר מבנה SOURCE/ + ENVIRONMENTS/
# ========================================

param(
    [string]$ProjectRoot = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset",
    [switch]$DryRun  # הצגה בלבד, לא ביצוע
)

$ErrorActionPreference = "Stop"

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║   📁 ארגון מבנה הפרויקט                                       ║
║                                                                ║
║   🎯 מטרה:                                                     ║
║      1. SOURCE/ - קוד מקור אחד ויחיד                          ║
║      2. ENVIRONMENTS/ - סביבות נפרדות                         ║
║                                                                ║
║   ⚡ יתרונות:                                                  ║
║      • פיתוח מהיר ללא build Docker                            ║
║      • בדיקות ללא השפעה על production                         ║
║      • ייצור יציב ומבודד                                      ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ========================================
# שלב 1: יצירת מבנה תיקיות
# ========================================

Write-Host "`n📂 שלב 1: יצירת מבנה תיקיות" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$structure = @{
    "SOURCE" = @{
        "app" = @{}
        "front" = @{}
        "public" = @{}
        "config" = @{}
        "scripts" = @{}
    }
    "ENVIRONMENTS" = @{
        "dev" = @{
            "volumes" = @{}
            "logs" = @{}
        }
        "test" = @{
            "volumes" = @{}
            "logs" = @{}
        }
        "prod" = @{
            "volumes" = @{}
            "logs" = @{}
        }
    }
}

function New-DirectoryStructure {
    param(
        [string]$BasePath,
        [hashtable]$Structure
    )
    
    foreach ($key in $Structure.Keys) {
        $path = Join-Path $BasePath $key
        
        if ($DryRun) {
            Write-Host "  [DRY-RUN] 📁 $path" -ForegroundColor DarkGray
        } else {
            if (-not (Test-Path $path)) {
                New-Item -ItemType Directory -Path $path -Force | Out-Null
                Write-Host "  ✅ נוצר: $path" -ForegroundColor Green
            } else {
                Write-Host "  ℹ️  קיים: $path" -ForegroundColor DarkGray
            }
        }
        
        # רקורסיה לתת-תיקיות
        if ($Structure[$key] -is [hashtable] -and $Structure[$key].Count -gt 0) {
            New-DirectoryStructure -BasePath $path -Structure $Structure[$key]
        }
    }
}

New-DirectoryStructure -BasePath $ProjectRoot -Structure $structure

# ========================================
# שלב 2: זיהוי קוד מקור נוכחי
# ========================================

Write-Host "`n🔍 שלב 2: זיהוי קוד מקור נוכחי" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$possibleSources = @(
    "eScriptorium_CLEAN",
    "escriptorium\eScriptorium_UNIFIED",
    "escriptorium\eScriptorium_V2"
)

$currentSource = $null

foreach ($source in $possibleSources) {
    $sourcePath = Join-Path $ProjectRoot $source
    if (Test-Path $sourcePath) {
        Write-Host "  ✅ מצאתי: $source" -ForegroundColor Green
        
        # בדוק אם יש app/ ו-front/
        $hasApp = Test-Path (Join-Path $sourcePath "app")
        $hasFront = Test-Path (Join-Path $sourcePath "front")
        
        if ($hasApp -and $hasFront) {
            $currentSource = $sourcePath
            Write-Host "     → זה נראה כמו המקור הראשי!" -ForegroundColor Cyan
            break
        }
    }
}

if (-not $currentSource) {
    Write-Warning "⚠️  לא מצאתי קוד מקור ברור. אמשיך ליצור מבנה ריק."
}

# ========================================
# שלב 3: יצירת docker-compose לכל סביבה
# ========================================

Write-Host "`n🐳 שלב 3: יצירת docker-compose לכל סביבה" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$environments = @{
    "dev" = @{
        "ports" = "8000:8000"
        "volumes" = @(
            "../../SOURCE/app:/usr/src/app:cached"
            "../../SOURCE/front:/usr/src/front:cached"
            "./volumes/media:/usr/src/app/media"
        )
        "envFile" = ".env.dev"
        "description" = "פיתוח - Hot reload"
    }
    "test" = @{
        "ports" = "8001:8000"
        "volumes" = @(
            "./volumes/media:/usr/src/app/media"
        )
        "envFile" = ".env.test"
        "description" = "בדיקות - Build מלא"
    }
    "prod" = @{
        "ports" = "8082:8000"
        "volumes" = @(
            "./volumes/media:/usr/src/app/media"
        )
        "envFile" = ".env.prod"
        "description" = "ייצור - יציב"
    }
}

foreach ($envName in $environments.Keys) {
    $envPath = Join-Path $ProjectRoot "ENVIRONMENTS\$envName"
    $composePath = Join-Path $envPath "docker-compose.yml"
    $env = $environments[$envName]
    
    $volumesYaml = ($env.volumes | ForEach-Object { "      - $_" }) -join "`n"
    
    $composeContent = @"
# ========================================
# $($env.description)
# ========================================

version: '3.8'

services:
  web:
    build:
      context: ../../SOURCE
      dockerfile: ../ENVIRONMENTS/$envName/Dockerfile
    container_name: escriptorium_${envName}_web
    ports:
      - "$($env.ports)"
    volumes:
$volumesYaml
    env_file:
      - $($env.envFile)
    depends_on:
      - db
      - redis
    restart: unless-stopped
    command: >
      bash -c "
        python manage.py migrate &&
        python manage.py collectstatic --noinput &&
        gunicorn escriptorium.wsgi:application --bind 0.0.0.0:8000
      "

  db:
    image: postgres:15-alpine
    container_name: escriptorium_${envName}_db
    volumes:
      - ./volumes/postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=escriptorium_${envName}
      - POSTGRES_USER=escriptorium
      - POSTGRES_PASSWORD=escriptorium
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: escriptorium_${envName}_redis
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: escriptorium_${envName}_nginx
    ports:
      - "808$([int][char]$envName[0] - 100):80"
    volumes:
      - ../../SOURCE/public:/usr/share/nginx/html:ro
      - ./volumes/media:/usr/share/nginx/media:ro
    depends_on:
      - web
    restart: unless-stopped
"@

    if ($DryRun) {
        Write-Host "  [DRY-RUN] 📄 $composePath" -ForegroundColor DarkGray
    } else {
        $composeContent | Set-Content $composePath -Encoding UTF8
        Write-Host "  ✅ נוצר: docker-compose.yml ב-$envName" -ForegroundColor Green
    }
    
    # יצירת קובץ .env
    $envFilePath = Join-Path $envPath $env.envFile
    $envContent = @"
# ========================================
# $($env.description) - Environment
# ========================================

DEBUG=True
SECRET_KEY=change-me-in-production
DATABASE_URL=postgresql://escriptorium:escriptorium@db:5432/escriptorium_${envName}
REDIS_URL=redis://redis:6379/0

# Django
DJANGO_SETTINGS_MODULE=escriptorium.settings
ALLOWED_HOSTS=localhost,127.0.0.1

# Media
MEDIA_ROOT=/usr/src/app/media
STATIC_ROOT=/usr/src/app/static
"@

    if ($DryRun) {
        Write-Host "  [DRY-RUN] 📄 $envFilePath" -ForegroundColor DarkGray
    } else {
        $envContent | Set-Content $envFilePath -Encoding UTF8
        Write-Host "  ✅ נוצר: $($env.envFile) ב-$envName" -ForegroundColor Green
    }
}

# ========================================
# שלב 4: יצירת Dockerfile לכל סביבה
# ========================================

Write-Host "`n🐋 שלב 4: יצירת Dockerfile לכל סביבה" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$dockerfiles = @{
    "dev" = @"
FROM python:3.8-slim

WORKDIR /usr/src

# התקנה מהירה
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Hot reload
ENV PYTHONUNBUFFERED=1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
"@
    "test" = @"
FROM python:3.8-slim

WORKDIR /usr/src

# Copy source
COPY app/ /usr/src/app/
COPY front/ /usr/src/front/

# Install dependencies
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

# Build frontend
RUN cd /usr/src/front && npm install && npm run build

CMD ["gunicorn", "escriptorium.wsgi:application", "--bind", "0.0.0.0:8000"]
"@
    "prod" = @"
FROM python:3.8-slim

WORKDIR /usr/src

# Optimized build
COPY app/ /usr/src/app/
COPY front/ /usr/src/front/

RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt && \
    cd /usr/src/front && \
    npm ci --production && \
    npm run build && \
    rm -rf node_modules

# Security
RUN useradd -m -u 1000 escriptorium && \
    chown -R escriptorium:escriptorium /usr/src

USER escriptorium

CMD ["gunicorn", "escriptorium.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
"@
}

foreach ($envName in $dockerfiles.Keys) {
    $dockerfilePath = Join-Path $ProjectRoot "ENVIRONMENTS\$envName\Dockerfile"
    
    if ($DryRun) {
        Write-Host "  [DRY-RUN] 🐋 $dockerfilePath" -ForegroundColor DarkGray
    } else {
        $dockerfiles[$envName] | Set-Content $dockerfilePath -Encoding UTF8
        Write-Host "  ✅ נוצר: Dockerfile ב-$envName" -ForegroundColor Green
    }
}

# ========================================
# שלב 5: סקריפטי עזר
# ========================================

Write-Host "`n🛠️  שלב 5: יצירת סקריפטי עזר" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

# סקריפט החלפה בין סביבות
$switchScript = @'
# ========================================
# 🔄 החלפה בין סביבות
# ========================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment,
    
    [switch]$Build,
    [switch]$Up,
    [switch]$Down
)

$envPath = "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\ENVIRONMENTS\$Environment"

Write-Host "🔄 עובר לסביבה: $Environment" -ForegroundColor Cyan

Push-Location $envPath

if ($Down) {
    Write-Host "🛑 מוריד סביבה נוכחית..." -ForegroundColor Yellow
    docker-compose down
}

if ($Build) {
    Write-Host "🔨 בונה סביבה..." -ForegroundColor Yellow
    docker-compose build
}

if ($Up) {
    Write-Host "🚀 מעלה סביבה..." -ForegroundColor Green
    docker-compose up -d
    
    Start-Sleep -Seconds 5
    docker-compose ps
}

Pop-Location

Write-Host "`n✅ סביבה $Environment מוכנה!" -ForegroundColor Green
'@

$switchScriptPath = Join-Path $ProjectRoot "SCRIPTS\switch-environment.ps1"

if ($DryRun) {
    Write-Host "  [DRY-RUN] 🔄 $switchScriptPath" -ForegroundColor DarkGray
} else {
    $switchScript | Set-Content $switchScriptPath -Encoding UTF8
    Write-Host "  ✅ נוצר: switch-environment.ps1" -ForegroundColor Green
}

# ========================================
# סיכום
# ========================================

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║   ✅ מבנה הפרויקט הושלם!                                      ║
╚════════════════════════════════════════════════════════════════╝

📁 מבנה שנוצר:
   SOURCE/           ← קוד מקור יחיד
   ENVIRONMENTS/
     ├─ dev/         ← פיתוח מהיר
     ├─ test/        ← בדיקות
     └─ prod/        ← ייצור

🚀 שימוש:

   # פיתוח מהיר (ללא build!)
   .\SCRIPTS\switch-environment.ps1 -Environment dev -Up

   # בדיקות
   .\SCRIPTS\switch-environment.ps1 -Environment test -Build -Up

   # ייצור
   .\SCRIPTS\switch-environment.ps1 -Environment prod -Build -Up

📊 ניטור אוטומטי:
   .\SCRIPTS\monitor.ps1
   (יעקוב אחרי שינויים ויעדכן Dashboard!)

"@ -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n⚠️  זה היה DRY-RUN - שום דבר לא שונה!" -ForegroundColor Yellow
    Write-Host "הרץ שוב ללא -DryRun כדי ליישם." -ForegroundColor Yellow
}
