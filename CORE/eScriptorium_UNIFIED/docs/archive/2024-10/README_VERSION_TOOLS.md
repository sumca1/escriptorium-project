# 🔄 כלי ניהול גרסאות eScriptorium

ברוך הבא למערכת ניהול גרסאות של eScriptorium! כלים אלו יעזרו לך למצוא את הגרסה האחרונה שעבדה טוב, ולהשוות בינה לגרסה הנוכחית.

---

## 📦 גרסאות זמינות

| מפתח | תאריך | תיאור | זמינות |
|------|-------|-------|---------|
| `sept18` | 18/09/2025 17:56 | הגרסה הכי ישנה | ✅ |
| `sept21` | 21/09/2025 18:36 | גרסת ביניים | ✅ |
| `sept25` | 25/09/2025 12:37 | גרסה מקורית מ-GitLab | ✅ |
| `current` | 05/10/2025 20:23 | גרסה נוכחית (עם עברית) | 🔵 פעיל |

---

## 🛠️ כלים זמינים

### 1. 📋 `version_switcher.ps1` - החלפת גרסאות
מחליף בין גרסאות שונות של eScriptorium בקלות.

**שימוש בסיסי**:
```powershell
# הצג רשימת גרסאות
.\version_switcher.ps1 -Action list

# החלף לגרסה ספציפית
.\version_switcher.ps1 -Action sept18

# החלף עם גיבוי אוטומטי של הנתונים
.\version_switcher.ps1 -Action sept18 -BackupData
```

**פרמטרים**:
- `-Action`: הפעולה לביצוע (`list`, `sept18`, `sept21`, `sept25`, `current`, `compare`)
- `-BackupData`: צור גיבוי נתונים לפני ההחלפה
- `-KeepData`: שמור את הנתונים הקיימים (ברירת מחדל)

---

### 2. 🔍 `compare_versions.ps1` - השוואת גרסאות
משווה בין שתי גרסאות שונות.

**שימוש**:
```powershell
# השווה הגדרות
.\compare_versions.ps1 `
    -Version1 "escriptorium:latest" `
    -Version2 "escriptorium_clean-web:latest" `
    -CompareType config

# השווה קבצים
.\compare_versions.ps1 `
    -Version1 "escriptorium:latest" `
    -Version2 "escriptorium_clean-web:latest" `
    -CompareType files

# הצג logs
.\compare_versions.ps1 -CompareType logs

# השוואה מלאה
.\compare_versions.ps1 `
    -Version1 "escriptorium:latest" `
    -Version2 "escriptorium_clean-web:latest" `
    -CompareType full
```

**סוגי השוואה**:
- `config`: משתני סביבה והגדרות
- `files`: קבצים בפועל
- `logs`: לוגים של containers
- `full`: כל מה שלמעלה

---

### 3. 🧪 `automated_tester.ps1` - בדיקה אוטומטית
בודק את כל הגרסאות באופן אוטומטי ומייצר דוח.

**שימוש**:
```powershell
# בדיקה אוטומטית של כל הגרסאות
.\automated_tester.ps1 -AutoTest

# התאם זמן המתנה (ברירת מחדל: 45 שניות)
.\automated_tester.ps1 -AutoTest -WaitSeconds 60
```

**מה הכלי בודק**:
- ✅ גישה לממשק Web
- ✅ בריאות Containers
- ✅ שגיאות ב-logs
- ✅ ציון כולל לכל גרסה

---

## 🚀 תהליך מומלץ למציאת הגרסה העובדת

### אופציה א': בדיקה ידנית (מומלץ למתחילים)

```powershell
# 1. צפה בגרסאות זמינות
.\version_switcher.ps1 -Action list

# 2. החלף לגרסה הכי ישנה
.\version_switcher.ps1 -Action sept18 -BackupData

# 3. המתן למערכת
Start-Sleep -Seconds 45

# 4. בדוק בדפדפן
Start-Process "http://localhost:8082"

# 5. בדוק logs
.\compare_versions.ps1 -CompareType logs

# 6. אם זה עובד - תייג את הגרסה
docker tag escriptorium_clean-web:latest escriptorium:working-version

# 7. אם לא - נסה גרסה אחרת
.\version_switcher.ps1 -Action sept21 -BackupData
```

### אופציה ב': בדיקה אוטומטית (מומלץ למתקדמים)

```powershell
# הרץ בדיקה אוטומטית
.\automated_tester.ps1 -AutoTest

# הכלי יבדוק את כל הגרסאות ויציג דוח מפורט
# זה ייקח בערך 3-5 דקות
```

---

## 📊 השוואה לאחר מציאת הגרסה העובדת

```powershell
# 1. השווה הגדרות
.\compare_versions.ps1 `
    -Version1 "escriptorium:latest" `
    -Version2 "escriptorium:working-version" `
    -CompareType config

# 2. השווה קבצים
.\compare_versions.ps1 `
    -Version1 "escriptorium:latest" `
    -Version2 "escriptorium:working-version" `
    -CompareType files

# 3. השווה ידנית קבצים ספציפיים
$c1 = docker create escriptorium:latest
$c2 = docker create escriptorium:working-version

docker cp ${c1}:/usr/src/app/escriptorium/settings.py ./new_settings.py
docker cp ${c2}:/usr/src/app/escriptorium/settings.py ./old_settings.py

code --diff old_settings.py new_settings.py

docker rm $c1
docker rm $c2
```

---

## 📝 תיעוד הממצאים

השתמש בתבנית הדוח:

```powershell
# פתח את תבנית הדוח
code VERSION_TESTING_REPORT_TEMPLATE.md

# או הרץ בדיקה אוטומטית שתיצור דוח
.\automated_tester.ps1 -AutoTest
```

---

## 🆘 פתרון בעיות נפוצות

### בעיה: המערכת לא עולה אחרי החלפת גרסה
```powershell
# בדוק סטטוס
docker-compose ps

# הצג logs חיים
docker-compose logs -f

# אתחל
docker-compose restart
```

### בעיה: שגיאה בגישה לדפדפן
```powershell
# בדוק שהפורט פתוח
docker ps | Select-String "8082"

# בדוק logs של nginx
docker logs escriptorium_clean-nginx-1 --tail 50
```

### בעיה: Celerybeat לא עובד
```powershell
# זו בעיה ידועה, תקן את docker-compose.yml
# שנה את השורה:
# command: celery -E -A escriptorium beat -l INFO
# ל:
# command: celery -A escriptorium beat -l INFO

# ואז:
docker-compose restart celerybeat
```

---

## 💾 גיבוי ושחזור נתונים

### גיבוי ידני
```powershell
$backupDir = ".\backups\manual_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force

# גבה volumes
docker run --rm `
    -v escriptorium_clean_postgres:/data `
    -v ${PWD}:/backup `
    ubuntu tar czf /backup/$backupDir/postgres.tar.gz -C /data .

docker run --rm `
    -v escriptorium_clean_media:/data `
    -v ${PWD}:/backup `
    ubuntu tar czf /backup/$backupDir/media.tar.gz -C /data .
```

### שחזור מגיבוי
```powershell
$backupDir = ".\backups\manual_20251005_123456"  # שנה לתיקייה הנכונה

docker run --rm `
    -v escriptorium_clean_postgres:/data `
    -v ${PWD}:/backup `
    ubuntu tar xzf /backup/$backupDir/postgres.tar.gz -C /data

docker run --rm `
    -v escriptorium_clean_media:/data `
    -v ${PWD}:/backup `
    ubuntu tar xzf /backup/$backupDir/media.tar.gz -C /data
```

---

## 📚 קבצי עזר נוספים

- `QUICK_VERSION_TESTING_GUIDE.md` - מדריך מהיר צעד אחר צעד
- `VERSION_TESTING_REPORT_TEMPLATE.md` - תבנית לדוח ממצאים
- `RESTORE_OLD_VERSION.md` - הסבר מפורט על שחזור גרסאות

---

## 🎯 דוגמה מלאה

```powershell
# 1. עבור לתיקייה
cd "g:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN"

# 2. צפה במצב הנוכחי
.\version_switcher.ps1 -Action list

# 3. הרץ בדיקה אוטומטית
.\automated_tester.ps1 -AutoTest

# הכלי יבדוק את sept18, sept21, sept25
# ויציג איזו גרסה עובדת הכי טוב

# 4. אחרי שהכלי סיים, תוצאות נשמרות ב:
#    - version_test_report_YYYYMMDD_HHMMSS.md
#    - test_logs_sept18_YYYYMMDD_HHMMSS.txt
#    - test_logs_sept21_YYYYMMDD_HHMMSS.txt
#    - test_logs_sept25_YYYYMMDD_HHMMSS.txt

# 5. פתח את הדוח
code version_test_report_*.md

# 6. החלף לגרסה העובדת (נניח sept18)
.\version_switcher.ps1 -Action sept18

# 7. השווה לגרסה הנוכחית
.\compare_versions.ps1 `
    -Version1 "escriptorium:latest" `
    -Version2 "escriptorium_clean-web:latest" `
    -CompareType full

# 8. תקן את הבעיות בגרסה הנוכחית
# 9. build מחדש
# 10. בדוק שהכל עובד
```

---

## ⚙️ הגדרות מתקדמות

### הרצת שתי גרסאות במקביל

ראה `RESTORE_OLD_VERSION.md` סעיף "אופציה 2" למדריך מפורט.

### שינוי פורטים

ערוך `docker-compose.override.yml`:
```yaml
services:
  nginx:
    ports:
      - 8083:80  # במקום 8082
```

---

## 📞 תמיכה

אם נתקעת:
1. בדוק את ה-logs: `.\compare_versions.ps1 -CompareType logs`
2. צפה בדוח האחרון שנוצר
3. השווה קבצי הגדרות בין גרסאות
4. וודא שיש לך גיבויים

---

**בהצלחה במציאת הגרסה העובדת! 🚀**
