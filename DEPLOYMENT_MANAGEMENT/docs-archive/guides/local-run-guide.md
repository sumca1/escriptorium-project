# 🏠 מדריך הרצה מקומית (ללא Docker)

## למה ללא Docker?
NetFree חוסם את כל תמונות Docker Hub, כולל Python, Node, Postgres וכו'.

## פתרון: הרצה מקומית עם Python

### שלב 1: התקנת Python (אם אין)
1. הורד Python 3.10+ מ: https://www.python.org/downloads/
2. במהלך ההתקנה סמן: "Add Python to PATH"

### שלב 2: התקנת PostgreSQL (אם אין)
1. הורד PostgreSQL מ: https://www.postgresql.org/download/windows/
2. התקן עם הגדרות ברירת מחדל
3. שמור את הסיסמה!

### שלב 3: התקנת Redis (אופציונלי)
```powershell
# דרך Chocolatey
choco install redis-64
```

### שלב 4: הרצת eScriptorium
```powershell
cd I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\CORE\eScriptorium_UNIFIED

# יצירת סביבה וירטואלית
python -m venv venv
.\venv\Scripts\Activate.ps1

# התקנת dependencies
pip install -r requirements.txt

# הגדרת DB
$env:DATABASE_URL="postgresql://user:password@localhost:5432/escriptorium"

# הרצת migrations
python manage.py migrate

# יצירת superuser
python manage.py createsuperuser

# הרצת שרת
python manage.py runserver
```

### שלב 5: גישה
פתח דפדפן: http://localhost:8000

---

## חלופה: שימוש ב-GitHub Actions

אם אתה רוצה Docker, השתמש ב-GitHub Actions:

1. העלה קוד ל-GitHub (כבר עשינו!)
2. הרץ workflow ב-Actions tab
3. הורד תמונה מוכנה:
   ```powershell
   docker pull ghcr.io/sumca1/escriptorium-project:latest
   docker run -p 8000:8000 ghcr.io/sumca1/escriptorium-project:latest
   ```

---

## מה להמליץ?

**לפיתוח יומיומי:** הרצה מקומית (מהר ופשוט)
**לפריסה/שיתוף:** GitHub Actions (תמונות מוכנות)
