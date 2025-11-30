# שילוב TABA Pipeline ב-BiblIA

## סיכום מהיר

**TABA** = פייפליין חיצוני שיוצר Ground Truth אוטומטית על ידי יישור טקסטים דיגיטליים ידועים עם תוצאות OCR.

## מבנה השילוב

### ✅ מה עשינו:

1. **יצרנו Django App חדש**: `apps/taba_pipeline/`
   - Models: ניהול corpus של GT, ניהול jobs של alignment
   - Views: ממשק ניהול דרך BiblIA
   - Admin: אינטגרציה עם Django admin

2. **הוספנו ל-INSTALLED_APPS**: 
   ```python
   'apps.taba_pipeline',  # TABA: Auto Ground Truth generation
   ```

3. **הוספנו URLs**:
   ```python
   path('taba/', include('apps.taba_pipeline.urls')),
   ```

4. **הגדרות ב-settings.py**:
   ```python
   TABA_PIPELINE_PATH = os.getenv('TABA_PIPELINE_PATH', 'taba_external/')
   TABA_CONDA_ENV = 'alignment_pipeline'
   ```

### ✅ מה TABA עושה (לפי התיעוד הרשמי):

```
1. ייצוא XML מ-BiblIA (תוצאות OCR של Kraken)
   ↓
2. הכנת נתונים: חילוץ שורות OCR + טעינת טקסטים דיגיטליים (GT)
   ↓
3. הרצת Passim: זיהוי יישורים בין OCR ל-GT
   ↓
4. סינון לפי Levenshtein distance (איכות הה��אמה)
   ↓
5. יצירת XML מעודכן: שורות מיושרות מוחלפות ב-GT
   ↓
6. ייבוא חזרה ל-BiblIA: שכבת transcription חדשה לכל GT
```

## התקנה (לפי התיעוד הרשמי)

### שלב 1: יצירת Conda Environment

```bash
cd BiblIA_dataset/eScriptorium_CLEAN
mkdir taba_external
cd taba_external

conda create -n alignment_pipeline python=3.11
conda activate alignment_pipeline
pip install git+https://github.com/dasmiq/passim.git
git clone https://github.com/Freymat/from_eScriptorium_to_Passim_and_back.git .
pip install -r requirements.txt
```

### שלב 2: הגדרת credentials

צור קובץ `credentials.py`:
```python
root_url = "http://localhost:8082"
headers = {"Authorization": "Token YOUR_TOKEN"}
headersbrief = headers
```

### שלב 3: הכנת קורפוס GT

```bash
mkdir -p data/raw/digital_editions

# העתק טקסטים עבריים (TXT files):
# - ספרי תנ"ך
# - תלמוד
# - ספרות רבנית
# וכו'
```

### שלב 4: הגדרת BiblIA

ב-`.env` או `docker-compose.yml`:
```bash
TABA_PIPELINE_PATH=/path/to/taba_external
TABA_CONDA_ENV=alignment_pipeline
```

### שלב 5: Migrations

```bash
python manage.py makemigrations taba_pipeline
python manage.py migrate taba_pipeline
```

## שימוש

### 1. גש ל-Dashboard
```
http://localhost:8082/taba/
```

### 2. צור Corpus
- שם: "טקסטים עבריים - Sefaria"
- סוג: TXT Files
- נתיב: `/path/to/taba_external/data/raw/digital_editions/`

### 3. צור Alignment Job
- **מסמך**: בחר מסמך מ-BiblIA
- **OCR Transcription**: בחר שכבת Kraken
- **GT Corpus**: בחר corpus שיצרת
- **פרמטרים**:
  - Passim n-grams: 7
  - Cores: 6
  - Memory: 8 GB
  - Levenshtein threshold: 0.8

### 4. הרץ Pipeline

לחץ "Start Job" - הפייפליין יריץ את כל השלבים אוטומטית.

### 5. צפה בתוצאות

- **Job Details**: סטטיסטיקות של יישור
- **Document**: שכבות transcription חדשות (אחת לכל GT שנמצא)

## דוגמה

**OCR מקורי:**
```
הגדול הגבור ודנורא אל עליון קונה ברחמיו
```

**GT מיושר (Levenshtein: 0.861):**
```
הגדול הגבור והנורא. אל עליון קונה
```

�? שכבת Transcription חדשה נוצרת עם הטקסט המיושר!

## יתרונות

✅ **אוטומטי לחלוטין**: אין צורך בתעתיק ידני
✅ **קנה מידה**: אלפי עמודים בבת אחת
✅ **איכות מובטחת**: סינון Levenshtein
✅ **משולב ב-BiblIA**: ממשק נוח
✅ **חיצוני**: לא משנה את הקוד המרכזי

## קבצים שנוצרו

```
app/apps/taba_pipeline/
├── __init__.py           # App initialization
├── apps.py               # Django app config
├── models.py             # DB models (Corpus, Jobs, Results)
├── views.py              # Management UI
├── admin.py              # Django admin integration
├── urls.py               # URL routing
└── README.md             # תיעוד מלא באנגלית
```

## הוספה ל-Navigation

בשלב הבא נוסיף קישור ב-Navigation Bar:
```html
<a href="{% url 'taba-dashboard' %}">
  <i class="fas fa-robot"></i> {% trans "Auto GT" %}
</a>
```

---

**תאריך שילוב:** 26 אוקטובר 2025
**פרויקט מקור:** https://github.com/Freymat/from_eScriptorium_to_Passim_and_back
**מחבר מקורי:** Freymat (MiDRASH Project)
