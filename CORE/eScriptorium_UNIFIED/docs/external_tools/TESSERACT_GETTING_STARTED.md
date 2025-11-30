# Tesseract Integration - Getting Started
**תאריך התחלה:** 5 באוקטובר 2025

## ✅ שלב 1: גיבוי (להתחיל עכשיו!)

```powershell
# הפעל את הסקריפט הזה מתיקיית הפרויקט:
cd "G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN"

# 1. יצירת תיקיית גיבויים
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupPath = "G:\OCR_Arabic_Testing\BiblIA_Backups\pre-tesseract_$timestamp"
New-Item -ItemType Directory -Force -Path $backupPath

# 2. גיבוי קבצי קונפיגורציה
Write-Host "Backing up configuration files..." -ForegroundColor Cyan
Copy-Item -Path ".\docker-compose.yml" -Destination "$backupPath\docker-compose.yml.backup"
Copy-Item -Path ".\Dockerfile" -Destination "$backupPath\Dockerfile.backup"
Copy-Item -Path ".\app\requirements.txt" -Destination "$backupPath\requirements.txt.backup"
Copy-Item -Path ".\variables.env" -Destination "$backupPath\variables.env.backup" -ErrorAction SilentlyContinue

# 3. גיבוי בסיס נתונים (אם רץ)
Write-Host "Backing up database..." -ForegroundColor Cyan
docker ps --filter "name=db" --format "{{.Names}}" | ForEach-Object {
    $dbContainer = $_
    docker exec $dbContainer pg_dump -U escriptorium escriptorium > "$backupPath\db_backup_$timestamp.sql"
    Write-Host "Database backed up to: $backupPath\db_backup_$timestamp.sql" -ForegroundColor Green
}

# 4. גיבוי מדיה ומודלים
Write-Host "Backing up media and models..." -ForegroundColor Cyan
if (Test-Path ".\media") {
    Copy-Item -Path ".\media" -Destination "$backupPath\media" -Recurse
    Write-Host "Media backed up" -ForegroundColor Green
}

# 5. תיעוד גרסאות
Write-Host "Documenting current versions..." -ForegroundColor Cyan
@"
# BiblIA System State Before Tesseract Integration
Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Docker Images
$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" | Out-String)

## Running Containers
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Out-String)

## Python Packages (from requirements.txt)
$(Get-Content ".\app\requirements.txt" | Out-String)

## Git Status
$(git status | Out-String)

## Git Log (last 5 commits)
$(git log --oneline -n 5 | Out-String)
"@ | Out-File -FilePath "$backupPath\system_state.txt"

Write-Host "`n✅ Backup completed successfully!" -ForegroundColor Green
Write-Host "Backup location: $backupPath" -ForegroundColor Yellow
Write-Host "`nNext step: Review TESSERACT_INTEGRATION_IMPLEMENTATION_PLAN.md - Step 2" -ForegroundColor Cyan
```

**הרץ את זה עכשיו ושמור את נתיב הגיבוי!**

---

## 📋 Checklist התחלתי

לפני שמתחילים, ודא:

### דרישות מערכת:
- [ ] Windows 10/11 עם PowerShell 5.1+
- [ ] Docker Desktop מותקן ורץ
- [ ] Git מותקן
- [ ] VS Code מותקן (מומלץ)
- [ ] 20GB+ מקום פנוי בדיסק
- [ ] 16GB+ RAM (מומלץ)

### ידע נדרש:
- [ ] הבנה בסיסית של Docker
- [ ] הבנה בסיסית של Git
- [ ] יכולת קריאת Python (בסיסי)
- [ ] ניסיון עם PowerShell / Command Line

### זמן זמין:
- [ ] יום עבודה מלא (~9 שעות) או
- [ ] 2-3 ימים בחלקים קטנים

### גיבוי בוצע:
- [ ] docker-compose.yml
- [ ] Dockerfile
- [ ] requirements.txt
- [ ] בסיס נתונים
- [ ] תיקיית media/models
- [ ] תיעוד מצב נוכחי

---

## 🚦 מצב התקדמות

| שלב | משימה | סטטוס | הערות |
|-----|-------|-------|-------|
| 1 | גיבוי | ⏳ בתהליך | הרץ סקריפט למעלה |
| 2 | Clone fork | ⏸️ ממתין | |
| 3 | השוואה | ⏸️ ממתין | |
| 4 | Dockerfile | ⏸️ ממתין | |
| 5 | Requirements | ⏸️ ממתין | |
| 6 | Python Code | ⏸️ ממתין | |
| 7 | Docker-compose | ⏸️ ממתין | |
| 8 | Build & Test | ⏸️ ממתין | |
| 9 | Download Models | ⏸️ ממתין | |
| 10 | Upload Models | ⏸️ ממתין | |
| 11 | Integration Tests | ⏸️ ממתין | |
| 12 | Optimization | ⏸️ ממתין | |

---

## 📞 נקודות החלטה קריטיות

### לפני שמתחיל:
**שאלה:** האם עשיתי גיבוי מלא?  
**תשובה נדרשת:** ✅ כן, הגיבוי ב-[נתיב]

### אחרי Clone:
**שאלה:** האם ראיתי את הקבצים שהשתנו?  
**תשובה נדרשת:** ✅ כן, סקרתי את ההבדלים

### לפני Build:
**שאלה:** האם בדקתי כל שינוי בקוד?  
**תשובה נדרשת:** ✅ כן, הכל מובן ותיעדתי

### לפני Production:
**שאלה:** האם הבדיקות עברו בהצלחה?  
**תשובה נדרשת:** ✅ כן, כל הטסטים ירוקים

---

## 🆘 במקרה חירום - Rollback

אם משהו משתבש **בכל שלב**, חזרה מהירה:

```powershell
# עצירת כל הקונטיינרים
docker-compose down

# שחזור קבצים מגיבוי
$backupPath = "G:\OCR_Arabic_Testing\BiblIA_Backups\pre-tesseract_[TIMESTAMP]"
Copy-Item -Path "$backupPath\docker-compose.yml.backup" -Destination ".\docker-compose.yml" -Force
Copy-Item -Path "$backupPath\Dockerfile.backup" -Destination ".\Dockerfile" -Force
Copy-Item -Path "$backupPath\requirements.txt.backup" -Destination ".\app\requirements.txt" -Force

# שחזור בסיס נתונים
# (אם נדרש - פרטים מלאים בתוכנית)

# בנייה מחדש
docker-compose build --no-cache
docker-compose up -d

Write-Host "✅ Rollback completed - system restored to previous state" -ForegroundColor Green
```

---

## 📊 Progress Tracking

**התחלה:** __________ (תאריך ושעה)  
**גיבוי הושלם:** __________ (תאריך ושעה)  
**Clone הושלם:** __________ (תאריך ושעה)  
**Build הצליח:** __________ (תאריך ושעה)  
**בדיקות עברו:** __________ (תאריך ושעה)  
**סיום:** __________ (תאריך ושעה)

**זמן ממשי שהושקע:** __________ שעות

---

## 💡 טיפים חשובים

1. **עבוד בשיטתיות** - אל תדלג על שלבים
2. **תעד הכל** - כתוב מה עשית בכל שלב
3. **בדוק פעמיים** - לפני build ולפני production
4. **קח הפסקות** - זה מרתון, לא ספרינט
5. **שמור גיבויים** - בכל נקודת ציון

---

## 📚 קבצים חשובים

1. **תוכנית מפורטת:**  
   `TESSERACT_INTEGRATION_IMPLEMENTATION_PLAN.md`

2. **ניתוח טכני:**  
   `TESSERACT_INTEGRATION_ANALYSIS.md`

3. **מעקב התקדמות (זה!):**  
   `TESSERACT_GETTING_STARTED.md`

4. **לוג שינויים:**  
   `TESSERACT_CHANGELOG.md` (ייווצר בתהליך)

---

## ✅ מוכן להתחיל?

1. **הרץ את סקריפט הגיבוי למעלה** ↑
2. **ודא שהגיבוי הצליח**
3. **עבור לשלב 2** בתוכנית המפורטת
4. **עדכן קובץ זה** עם התקדמותך

**בהצלחה! 🚀**

---

**שאלות?** תייג את המשימה הספציפית ואשמח לעזור בפרטים!
