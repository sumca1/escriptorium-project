# 🎉 המערכת מוכנה!

יצרתי לך מערכת כלים מקיפה למציאת הגרסה העובדת של eScriptorium ולהשוואה בינה לגרסה הנוכחית.

---

## 📦 מה יש לך כרגע?

### גרסאות זמינות:
```
✅ sept18   - 18/09/2025 17:56  (הכי ישנה)
✅ sept21   - 21/09/2025 18:36  (ביניים)
✅ sept25   - 25/09/2025 12:37  (GitLab מקורי)
🔵 current  - 05/10/2025 20:23  (נוכחי - עם עברית) ← פעיל כעת
```

---

## 🛠️ כלים שנוצרו עבורך:

### 1️⃣ **version_switcher.ps1** (10.84 KB)
   המחליף הראשי - מאפשר לך לעבור בין גרסאות בקלות
   
### 2️⃣ **compare_versions.ps1** (10.22 KB)
   משווה בין גרסאות - הגדרות, קבצים, logs
   
### 3️⃣ **automated_tester.ps1** (12.13 KB)
   בודק אוטומטי - בודק את כל הגרסאות ומייצר דוח
   
### 4️⃣ **README_VERSION_TOOLS.md** (8.76 KB)
   מדריך מקיף לכל הכלים
   
### 5️⃣ **QUICK_VERSION_TESTING_GUIDE.md** (8.51 KB)
   מדריך מהיר צעד אחר צעד
   
### 6️⃣ **VERSION_TESTING_REPORT_TEMPLATE.md** (8.79 KB)
   תבנית לתיעוד ממצאים
   
### 7️⃣ **RESTORE_OLD_VERSION.md** (7.24 KB)
   הסבר מפורט על שחזור גרסאות

---

## 🚀 איך להתחיל? (3 דקות)

### אופציה א': בדיקה אוטומטית (מומלץ!) 🤖

```powershell
cd "g:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN"

# הרץ בדיקה אוטומטית של כל הגרסאות
.\automated_tester.ps1 -AutoTest
```

**מה זה יעשה?**
- ✅ יבדוק את sept18, sept21, sept25
- ✅ יבדוק גישה לאתר
- ✅ יבדוק בריאות containers
- ✅ יחפש שגיאות
- ✅ יציג דוח עם המלצה איזו גרסה הכי טובה
- ⏱️ זמן: ~3-5 דקות

---

### אופציה ב': בדיקה ידנית צעד אחר צעד 👨‍💻

```powershell
cd "g:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN"

# 1. צפה בגרסאות
.\version_switcher.ps1 -Action list

# 2. נסה את הגרסה הכי ישנה
.\version_switcher.ps1 -Action sept18 -BackupData

# 3. המתן למערכת
Start-Sleep -Seconds 45

# 4. פתח בדפדפן
Start-Process "http://localhost:8082"

# 5. בדוק logs
.\compare_versions.ps1 -CompareType logs
```

**אם sept18 עובד:**
```powershell
# תייג אותו כגרסה עובדת
docker tag escriptorium_clean-web:latest escriptorium:working-version

# השווה לגרסה הנוכחית
.\compare_versions.ps1 `
    -Version1 "escriptorium:latest" `
    -Version2 "escriptorium:working-version" `
    -CompareType full
```

**אם sept18 לא עובד:**
```powershell
# נסה גרסה אחרת
.\version_switcher.ps1 -Action sept21 -BackupData
Start-Sleep -Seconds 45
Start-Process "http://localhost:8082"
```

---

## 📊 מה לבדוק בכל גרסה?

כשאתה פותח את http://localhost:8082, וודא:

```
✅ דף הבית נטען
✅ אין שגיאות 500/404
✅ הממשק מוצג כראוי
✅ תוכן בעברית (אם רלוונטי)
✅ אפשר להתחבר (אם יש לך משתמש)
✅ אפשר ליצור פרויקט חדש
```

---

## 🔍 אחרי שמצאת גרסה עובדת

### שלב 1: תייג אותה
```powershell
docker tag <working-image> escriptorium:working-version
```

### שלב 2: השווה לגרסה הנוכחית
```powershell
# השוואה מלאה
.\compare_versions.ps1 `
    -Version1 "escriptorium:latest" `
    -Version2 "escriptorium:working-version" `
    -CompareType full
```

### שלב 3: זהה הבדלים בקבצים חשובים
```powershell
# צור containers זמניים
$c1 = docker create escriptorium:latest
$c2 = docker create escriptorium:working-version

# השווה settings
docker cp ${c1}:/usr/src/app/escriptorium/settings.py ./new_settings.py
docker cp ${c2}:/usr/src/app/escriptorium/settings.py ./old_settings.py
code --diff old_settings.py new_settings.py

# השווה requirements
docker cp ${c1}:/usr/src/app/requirements.txt ./new_requirements.txt
docker cp ${c2}:/usr/src/app/requirements.txt ./old_requirements.txt
code --diff old_requirements.txt new_requirements.txt

# נקה
docker rm $c1 $c2
```

---

## 💾 גיבוי חשוב!

כל פעם שאתה משנה גרסה עם `-BackupData`, נוצר גיבוי אוטומטי ב:
```
.\backups\backup_YYYYMMDD_HHMMSS\
```

לגיבוי ידני:
```powershell
$backupDir = ".\backups\manual_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force

docker run --rm `
    -v escriptorium_clean_postgres:/data `
    -v ${PWD}:/backup `
    ubuntu tar czf /backup/$backupDir/postgres.tar.gz -C /data .
```

---

## 📚 מסמכים למידע נוסף

1. **README_VERSION_TOOLS.md** - מדריך מקיף לכל הכלים
2. **QUICK_VERSION_TESTING_GUIDE.md** - מדריך מהיר צעד אחר צעד
3. **VERSION_TESTING_REPORT_TEMPLATE.md** - תבנית לתיעוד ממצאים
4. **RESTORE_OLD_VERSION.md** - הסבר על שחזור גרסאות

---

## 🎯 התהליך המומלץ שלי בשבילך:

```powershell
# 1. עבור לתיקייה
cd "g:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN"

# 2. פתח את המדריך המהיר לעיון
code QUICK_VERSION_TESTING_GUIDE.md

# 3. הרץ בדיקה אוטומטית
.\automated_tester.ps1 -AutoTest

# 4. לך לשתות קפה ☕ (3-5 דקות)

# 5. קרא את הדוח שנוצר
code version_test_report_*.md

# 6. החלף לגרסה העובדת שהכלי מצא
.\version_switcher.ps1 -Action <best-version>

# 7. השווה לגרסה הנוכחית
.\compare_versions.ps1 `
    -Version1 "escriptorium:latest" `
    -Version2 "escriptorium_clean-web:latest" `
    -CompareType full

# 8. תקן את הבעיות בגרסה הנוכחית
# 9. Build מחדש
# 10. בדוק שהכל עובד!
```

---

## ⚠️ טיפים חשובים

1. **תמיד גבה נתונים** - השתמש ב-`-BackupData`
2. **התאזר בסבלנות** - כל החלפת גרסה לוקחת 30-60 שניות
3. **תעד ממצאים** - השתמש בתבנית הדוח
4. **שמור logs** - `docker-compose logs > logs.txt`
5. **בדוק לפני וכבר** - וודא שאתה מבין מה השתנה

---

## 🆘 אם משהו לא עובד

```powershell
# צפה בלוגים חיים
docker-compose logs -f

# בדוק סטטוס
docker ps -a

# אתחל
docker-compose restart

# חזור לגרסה הנוכחית
.\version_switcher.ps1 -Action current
```

---

## 🎓 למידע נוסף

פתח את:
```powershell
code README_VERSION_TOOLS.md
```

---

**בהצלחה! 🚀**

אם תתקל בבעיות או תצטרך עזרה, פשוט הפעל:
```powershell
.\version_switcher.ps1 -Action list
```
כדי לראות את הסטטוס הנוכחי.
