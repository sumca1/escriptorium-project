# Quick Start Guide - TABA Pipeline in BiblIA
## מדריך התחלה מהירה

### ✅ מה כבר מוכן:
- Django App: `apps/taba_pipeline/` ✅
- Models + Migrations: נוצרו ✅
- Views + URLs: מוכנים ✅
- Navigation: הוסף ל-menu ✅
- תרגום עברי: הוסף ✅

---

### 🚀 להפעלה ראשונית:

#### 1. הרץ Docker Containers
```bash
docker-compose up -d
```

#### 2. הרץ Migration (פעם אחת בלבד)
```bash
docker-compose exec web python manage.py migrate taba_pipeline
```

#### 3. גש ל-Dashboard
```
http://localhost:8082/taba/
```

**תראה**: "System Status" - TABA Not Installed (זה תקין!)

---

### 📥 להתקנת TABA External Pipeline:

#### שלב 1: צור Conda Environment

```bash
# במחשב המארח (לא Docker!)
cd BiblIA_dataset/eScriptorium_CLEAN
mkdir taba_external
cd taba_external

# יצירת environment
conda create -n alignment_pipeline python=3.11 -y
conda activate alignment_pipeline

# התקנת Passim
pip install git+https://github.com/dasmiq/passim.git

# שיבוט TABA
git clone https://github.com/Freymat/from_eScriptorium_to_Passim_and_back.git .

# התקנת dependencies
pip install -r requirements.txt
```

#### שלב 2: הגדרות

**יצור קובץ `credentials.py`:**
```python
root_url = "http://localhost:8082"
headers = {
    "Authorization": "Token YOUR_API_TOKEN_HERE"
}
headersbrief = headers
```

**קבל API Token:**
```bash
# בתוך Docker
docker-compose exec web python manage.py shell
```
```python
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='your_username')
token, created = Token.objects.get_or_create(user=user)
print(token.key)
```

#### שלב 3: הכן Ground Truth Corpus

```bash
# צור תיקייה
mkdir -p data/raw/digital_editions

# העתק קבצי TXT עבריים
# לדוגמה:
# data/raw/digital_editions/
#   ├── genesis.txt
#   ├── exodus.txt
#   └── ...
```

---

### 💻 שימוש דרך BiblIA UI:

#### 1. צור Corpus
1. גש ל: `http://localhost:8082/taba/corpus/`
2. לחץ "Add Corpus" (בadmin או דרך UI)
3. מלא:
   - **Name**: "ספרי תנ"ך"
   - **Source Type**: TXT Files
   - **Source Path**: `/path/to/taba_external/data/raw/digital_editions/`

#### 2. צור Alignment Job
1. גש ל: `http://localhost:8082/taba/jobs/create/`
2. בחר:
   - **Document**: המסמך שלך ב-eScriptorium
   - **OCR Transcription**: שכבת Kraken
   - **GT Corpus**: הcorpus שיצרת
3. הגדר פרמטרים:
   - **Passim n-grams**: 7
   - **Cores**: 6
   - **Memory**: 8 GB
   - **Levenshtein threshold**: 0.8

#### 3. הרץ Pipeline
1. גש לפרטי Job
2. לחץ "Start Job"
3. עקוב אחר Progress

---

### 🎬 הרצה ידנית (Advanced):

```bash
# הפעל TABA environment
conda activate alignment_pipeline
cd taba_external

# הרצת pipeline מלא
python main.py --run_all --no_import

# או שלב-שלב:
python main.py --prepare_data_for_passim
python main.py --compute_alignments_with_passim
python main.py --create_xmls_from_passim_results
python main.py --export_xmls_to_eSc
```

---

### 📊 תוצאות:

**בתוך eScriptorium:**
- שכבות transcription חדשות
- אחת לכל GT שנמצא יישור
- שורות מיושרות מוחלפות ב-GT

**קבצים:**
- `data/output/xmls_for_eSc/` - XMLs מעודכנים
- `data/output/alignment_register/` - סטטיסטיקות JSON
- `data/output/results_summary_tsv/` - טבלאות TSV

---

### 🔧 Troubleshooting:

**"TABA Not Installed"**
- זה תקין! TABA הוא external, לא חלק מ-Docker
- להתקנה: עקוב אחר "שלב 1" למעלה

**"Passim Not Installed"**
- במחשב המארח:
```bash
conda activate alignment_pipeline
pip install git+https://github.com/dasmiq/passim.git
```

**"No Alignments Found"**
- נסה להוריד Levenshtein threshold ל-0.7
- בדוק שה-GT texts בעברית
- ודא שיש OCR באיכות סבירה

**"Memory Error"**
- הפחת ב-`config.py`:
```python
mem = 4  # במקום 8
n_cores = 4  # במקום 6
```

---

### 📖 תיעוד מלא:

- **English**: `app/apps/taba_pipeline/README.md`
- **עברית**: `TABA_INTEGRATION_HEB.md`
- **Technical**: `TABA_INTEGRATION_SUMMARY.md`
- **Original TABA**: https://github.com/Freymat/from_eScriptorium_to_Passim_and_back

---

**הכל מוכן! רק להריץ docker-compose up ולהתחיל לעבוד!** 🚀
