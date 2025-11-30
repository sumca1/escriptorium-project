# 🤖 TABA Pipeline - Auto Ground Truth Generation

**Integrated:** 26 October 2025  
**Status:** ✅ Ready for Use (after external setup)

---

## 📚 תיעוד / Documentation

### מדריכים מהירים / Quick Guides:
- **[מדריך התחלה מהירה](./TABA_QUICK_START.md)** 🇮🇱 - כל מה שצריך להתחיל
- **[Quick Start Guide](./app/apps/taba_pipeline/README.md)** 🇬🇧 - Full installation guide

### תיעוד טכני / Technical Docs:
- **[סיכום שילוב](./TABA_INTEGRATION_HEB.md)** 🇮🇱 - איך שילבנו את TABA
- **[Integration Summary](./TABA_INTEGRATION_SUMMARY.md)** 🇬🇧 - Technical architecture
- **[Completed Steps](./TABA_COMPLETED_STEPS.md)** ✅ - What's done, what's next

### מקור / Original:
- **[TABA GitHub](https://github.com/Freymat/from_eScriptorium_to_Passim_and_back)** - Original project

---

## 🎯 מה זה TABA?

**TABA (Text Alignment for Building Annotations)** יוצר Ground Truth אוטומטית על ידי:
1. ייצוא תוצאות OCR מ-BiblIA
2. יישור עם טקסטים דיגיטליים ידועים (Sefaria, ספרים, וכו')
3. שימוש ב-Passim לזיהוי התאמות
4. החלפת OCR ב-GT במקומות שיש יישור טוב
5. ייבוא חזרה כשכבות transcription חדשות

### דוגמה:

**OCR מקורי:**
```
הגדול הגבור ודנורא אל עליון קונה ברחמיו
```

**GT מיושר (Levenshtein: 0.861):**
```
הגדול הגבור והנורא. אל עליון קונה
```

→ **שכבת transcription חדשה נוצרת!**

---

## ⚡ Quick Access

### URLs:
- **Dashboard**: http://localhost:8082/taba/
- **Manage Corpora**: http://localhost:8082/taba/corpus/
- **Create Job**: http://localhost:8082/taba/jobs/create/
- **View Jobs**: http://localhost:8082/taba/jobs/

### Navigation:
```
Advanced Tools → יצירת אמת מידה אוטומטית (Auto Ground Truth)
```

---

## ✅ מה כבר מוכן / What's Ready:

- ✅ Django App (`apps/taba_pipeline/`)
- ✅ Database Models (4 models)
- ✅ Views + URLs (9 views, 11 routes)
- ✅ Templates (Dashboard UI)
- ✅ Navigation Menu integration
- ✅ Hebrew translations
- ✅ Full documentation (3 files)

---

## 📋 מה צריך להתקין / What Needs Setup:

### 1. Run Migration (once)
```bash
docker-compose exec web python manage.py migrate taba_pipeline
```

### 2. Install External TABA Pipeline
```bash
mkdir taba_external
cd taba_external
conda create -n alignment_pipeline python=3.11
conda activate alignment_pipeline
pip install git+https://github.com/dasmiq/passim.git
git clone https://github.com/Freymat/from_eScriptorium_to_Passim_and_back.git .
pip install -r requirements.txt
```

### 3. Configure
Create `taba_external/credentials.py`:
```python
root_url = "http://localhost:8082"
headers = {"Authorization": "Token YOUR_TOKEN"}
headersbrief = headers
```

### 4. Prepare GT Corpus
```bash
mkdir -p taba_external/data/raw/digital_editions
# Add TXT files with Hebrew texts
```

---

## 🚀 שימוש / Usage

### Via BiblIA UI:
1. Create GT Corpus → `/taba/corpus/`
2. Create Alignment Job → `/taba/jobs/create/`
3. Run Job → Click "Start"
4. View Results → New transcription layers in eScriptorium

### Manual (Advanced):
```bash
conda activate alignment_pipeline
cd taba_external
python main.py --run_all --no_import
```

---

## 🏗️ ארכיטקטורה / Architecture

```
┌──────────────────┐
│  BiblIA Django   │  ← Management UI
│  /taba/          │  ← Job monitoring
└────────┬─────────┘
         │ API
         ↓
┌──────────────────┐
│ TABA External    │  ← Standalone pipeline
│ (Passim + Spark) │  ← Conda environment
└──────────────────┘
```

**Key Design:**
- TABA = External standalone pipeline
- BiblIA = Management interface only
- Communication via eScriptorium API

---

## 📊 תכונות / Features

### Database Models:
1. **GroundTruthCorpus** - קולקציות טקסטים דיגיטליים
2. **GroundTruthText** - טקסטים בודדים
3. **AlignmentJob** - משימות יישור
4. **AlignmentResult** - תוצאות לכל עמוד

### Views:
- Dashboard - סקירה כללית
- Corpus Management - ניהול GT corpora
- Job Creation - יצירת משימות חדשות
- Job Monitoring - מעקב אחר ביצוע
- Results Viewing - צפייה בתוצאות

---

## 🎓 מתי להשתמש? / When to Use?

✅ **כדאי להשתמש כאשר:**
- יש לך טקסטים דיגיטליים ידועים (Sefaria, ספרים, וכו')
- OCR באיכות סבירה (לפחות 70% דיוק)
- צריך כמויות גדולות של GT
- רוצה לאמן מודל Kraken טוב יותר

❌ **לא מתאים כאשר:**
- אין טקסטים דיגיטליים מתאימים
- OCR באיכות נמוכה מאוד
- טקסט ייחודי ללא מקבילות ידועות

---

## 🔧 פרמטרים / Parameters

### Passim:
- `n`: N-gram size (default: 7)
- `cores`: CPU cores (default: 6)
- `memory`: RAM in GB (default: 8)

### Quality:
- `levenshtein_threshold`: 0.0-1.0 (default: 0.8)
  - גבוה יותר = פחות תוצאות, איכות גבוהה יותר
  - נמוך יותר = יותר תוצאות, עלול להיות noise

---

## 📞 תמיכה / Support

### תיקון בעיות / Troubleshooting:
ראה [TABA_QUICK_START.md](./TABA_QUICK_START.md#troubleshooting)

### קישורים / Links:
- **Original TABA**: https://github.com/Freymat/from_eScriptorium_to_Passim_and_back
- **Passim**: https://github.com/dasmiq/passim
- **Sefaria API**: https://www.sefaria.org/developers

---

**Created by:** BiblIA Development Team  
**Original TABA by:** Freymat (MiDRASH Project - EPHE)  
**License:** Follow original TABA license
