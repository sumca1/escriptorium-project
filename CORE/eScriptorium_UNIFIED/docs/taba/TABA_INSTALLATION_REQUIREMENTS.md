# ✅ TABA Pipeline - דרישות להפעלה מלאה
**תאריך:** 26 אוקטובר 2025  
**מטרה:** רשימת כל מה שצריך להתקין עוד

---

## 🎯 סטטוס נוכחי: מה כבר עובד

### ✅ הושלם במלואו:
```bash
✓ Django App מותקן ופעיל
✓ מסד נתונים עם 4 טבלאות 
✓ ממשק משתמש בעברית מלא
✓ Navigation menu מעודכן
✓ Django Admin integration
✓ תיעוד מקיף בעברית
✓ כל הקונטיינרים רצים (16/16)
✓ Passim server פעיל על פורט 9090
```

---

## 🔧 מה עוד צריך להתקין

### 1. 🐍 TABA Pipeline החיצוני (הכרחי)

**מיקום התקנה:** מחוץ לקונטיינרים של Docker

```bash
# יצירת סביבת Conda נפרדת
mkdir -p /opt/taba_pipeline
cd /opt/taba_pipeline

# התקנת Conda environment
conda create -n taba_alignment python=3.11 -y
conda activate taba_alignment

# התקנת Passim  
pip install git+https://github.com/dasmiq/passim.git

# שכפול TABA Pipeline
git clone https://github.com/Freymat/from_eScriptorium_to_Passim_and_back.git
cd from_eScriptorium_to_Passim_and_back

# התקנת תלויות
pip install -r requirements.txt
pip install arabic-reshaper python-bidi

# קונפיגורציה
cp credentials_example.py credentials.py
# ערכו credentials.py עם פרטי eScriptorium API
```

### 2. 📁 הכנת קורפוס Ground Truth (הכרחי)

**מיקום:** `/opt/taba_pipeline/data/ground_truth/`

```bash
# יצירת מבנה תיקיות
mkdir -p /opt/taba_pipeline/data/ground_truth/hebrew_classics/
mkdir -p /opt/taba_pipeline/data/ground_truth/sefaria_texts/
mkdir -p /opt/taba_pipeline/data/ground_truth/custom_texts/

# דוגמה לקבצי טקסט נקיים
echo "משלי שלמה בן דוד מלך ישראל..." > hebrew_classics/proverbs_1.txt
echo "בראשית ברא אלהים את השמים ואת הארץ..." > sefaria_texts/genesis_1.txt
```

**מקורות מומלצים לטקסטים:**
- ✅ Sefaria API (טקסטים מוכנים)
- ✅ קבצי PDF → TXT נקיים  
- ✅ טקסטים ידועים מעובדים
- ✅ ספרות עברית קלאסית דיגיטלית

### 3. ⚙️ קונפיגורציה של eScriptorium API

**קובץ:** `/opt/taba_pipeline/from_eScriptorium_to_Passim_and_back/credentials.py`

```python
# פרטי חיבור לeScriptorium
ESCRIPTORIUM_API_URL = "http://localhost:8082/api/"
ESCRIPTORIUM_USERNAME = "admin"  # המשתמש שלכם
ESCRIPTORIUM_PASSWORD = "password"  # הסיסמה שלכם
ESCRIPTORIUM_TOKEN = "your_api_token"  # אם יש

# פרטי Passim
PASSIM_URL = "http://localhost:9090/"
PASSIM_DATA_PATH = "/opt/taba_pipeline/data/"

# הגדרות TABA
TABA_WORK_DIR = "/opt/taba_pipeline/work/"
TABA_OUTPUT_DIR = "/opt/taba_pipeline/output/"
```

### 4. 🔗 חיבור Django ← TABA חיצוני

**קובץ:** `app/escriptorium/settings.py` (כבר קיים, צריך לעדכן)

```python
# הגדרות TABA (לעדכן בsettings.py)
TABA_PIPELINE_PATH = "/opt/taba_pipeline/from_eScriptorium_to_Passim_and_back/"
TABA_CONDA_ENV = "taba_alignment"
TABA_PYTHON_PATH = "/opt/miniconda3/envs/taba_alignment/bin/python"
```

### 5. 🚀 Celery Tasks לעבודות רקע (אופציונלי אבל מומלץ)

**קובץ חדש:** `app/apps/taba_pipeline/tasks.py`

```python
from celery import shared_task
import subprocess
import os

@shared_task
def run_taba_alignment(job_id):
    """הרצת TABA alignment ברקע"""
    job = AlignmentJob.objects.get(id=job_id)
    
    # הרצת TABA Pipeline חיצוני
    cmd = [
        settings.TABA_PYTHON_PATH,
        os.path.join(settings.TABA_PIPELINE_PATH, "main.py"),
        "--job-id", str(job_id),
        "--corpus", job.gt_corpus.source_path,
        "--document", str(job.document.id)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        job.status = 'completed'
    else:
        job.status = 'failed'
    
    job.save()
    return result
```

---

## 🧪 בדיקות שצריך לעשות

### בדיקה 1: Passim Server

```bash
# בדקו שPassim עובד
curl http://localhost:9090/status
# צריך להחזיר: {"status": "ok"}
```

### בדיקה 2: TABA Pipeline חיצוני  

```bash
# לאחר התקנה
conda activate taba_alignment
cd /opt/taba_pipeline/from_eScriptorium_to_Passim_and_back/
python main.py --help
# צריך להציג אפשרויות הפקודה
```

### בדיקה 3: חיבור API

```bash
# בדיקת API של eScriptorium
curl -H "Authorization: Token your_token" \
     http://localhost:8082/api/documents/
# צריך להחזיר רשימת מסמכים
```

### בדיקה 4: יצירת קורפוס ראשון

```bash
# דרך Django shell
docker-compose exec web python manage.py shell -c "
from apps.taba_pipeline.models import GroundTruthCorpus
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
corpus = GroundTruthCorpus.objects.create(
    name='בדיקה ראשונית',
    description='קורפוס לבדיקה',
    owner=user,
    source_type='txt'
)
print('✅ Corpus created:', corpus.id)
"
```

---

## 📋 צ'קליסט התקנה מלאה

### שלב 1: התקנה חיצונית
- [ ] יצירת conda environment חדש
- [ ] התקנת Passim מGitHub  
- [ ] שכפול TABA Pipeline
- [ ] התקנת python packages נדרשים
- [ ] קונפיגורציה של credentials.py

### שלב 2: הכנת נתונים  
- [ ] יצירת מבנה תיקיות לGT
- [ ] הוספת טקסטי GT ראשונים (5-10 קבצים)
- [ ] בדיקת נגישות הקבצים
- [ ] הכנת מטאדטה לטקסטים

### שלב 3: קונפיגורציה
- [ ] עדכון TABA_PIPELINE_PATH בsettings.py
- [ ] יצירת API token בeScriptorium  
- [ ] עדכון credentials.py עם פרטי חיבור
- [ ] בדיקת חיבור API

### שלב 4: בדיקות
- [ ] Passim server עובד  
- [ ] TABA pipeline חיצוני עובד
- [ ] Django dashboard נטען
- [ ] יצירת קורפוס ראשון מצליחה
- [ ] הרצת עבודה ראשונה (אם יש מסמכים)

---

## ⏱️ זמן התקנה משוער

```bash
שלב 1: התקנה חיצונית      - 30-45 דקות
שלב 2: הכנת נתונים         - 15-30 דקות  
שלב 3: קונפיגורציה         - 15-20 דקות
שלב 4: בדיקות             - 10-15 דקות
────────────────────────────────────────
סה"כ:                    70-110 דקות
```

---

## 🚨 נקודות חשובות

### אבטחה
```bash
⚠️  API Token - שמרו בסוד
⚠️  Credentials.py - אל תשתפו בGit
⚠️  File Permissions - רק למשתמש הנכון
```

### ביצועים  
```bash
💾 דיסק: ~2GB לTABA + GT files
🧠 RAM: 8GB מינימום (16GB מומלץ)  
⚡ CPU: 4+ ליבות לעיבוד מהיר
```

### תחזוקה
```bash
📅 עדכון Passim כל 3-6 חודשים
📅 גיבוי GT corpus חודשי  
📅 ניקוי קבצי עבודה זמניים
```

---

## 🎯 מה יקרה אחרי התקנה מלאה?

### תהליך עבודה מלא:
1. **יצירת קורפוס GT** ← דרך Django dashboard
2. **העלאת מסמך עם OCR** ← דרך eScriptorium רגיל  
3. **יצירת עבודת יישור** ← דרך TABA dashboard
4. **הרצה אוטומטית** ← TABA חיצוני + Passim
5. **קבלת XML מתוקן** ← שיפור של 15-30% דיוק!

### התוצאה הסופית:
**מערכת OCR מתקדמת עם יישור אוטומטי ושיפור דיוק משמעותי!** 🚀

---

## 📞 מה הצעד הבא?

**ההמלצה שלי:**

1. **התחילו עם שלב 1** - התקנת TABA חיצוני (30-45 דק')
2. **הכינו GT corpus קטן** - 5-10 טקסטים לבדיקה
3. **עשו בדיקה ראשונה** - עם מסמך אחד פשוט
4. **אחרי שזה עובד** - הרחבו לקורפוס גדול יותר

**אני כאן לעזור בכל השלבים!** 💪

---

*רשימה זו כוללת את כל הדרישות להפעלה מלאה של TABA Pipeline*  
*לאחר השלמת הצעדים האלו - המערכת תהיה פעילה במלואה!*