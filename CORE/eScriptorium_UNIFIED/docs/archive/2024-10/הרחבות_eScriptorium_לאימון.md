# 🔌 הרחבות ותוספים ל-eScriptorium עבור אימון מודלים
**תאריך:** 22 אוקטובר 2025  
**מקור:** חיפוש ב-GitHub + תיעוד קיים בפרויקט

---

## 📊 סיכום מהיר

### ✅ מה קיים ב-eScriptorium המקורי (scripta-psl/escriptorium)
1. ✅ **Kraken Integration** - מנוע OCR/HTR עם augmentation מובנה
2. ✅ **Training System** - אימון מודלים דרך ממשק אינטרנט
3. ✅ **Model Management** - ניהול מודלים ושיתוף
4. ✅ **Ground Truth Export** - ייצוא נתונים לאימון

### 🎯 הרחבות קהילתיות (community extensions)
**16 repositories ב-GitHub topics/escriptorium:**

1. **Tesseract Extension** (UB-Mannheim)
2. **CERberus** (WHaverals) - הערכת דיוק
3. **Virtual Keyboards** - מקלדות וירטואליות
4. **Ground Truth Tools** - כלי ניהול GT
5. **Pipeline Tools** - כלי אוטומציה

---

## 🔥 הרחבות חשובות לאימון מודלים

### 1️⃣ Tesseract Extension (UB-Mannheim)

#### 📌 מה זה?
פיתוח של **UB-Mannheim** שמוסיף תמיכה ב-Tesseract OCR ל-eScriptorium:
- אימון מודלי Tesseract דרך ממשק eScriptorium
- העלאה ושימוש במודלי Tesseract קיימים
- המרה של מודלים משפות שונות

#### 🔗 מידע טכני
```yaml
Repository: https://github.com/JKamlah/eScriptorium
Branch: extension-tesseract
Status: Experimental (לא רשמי)
Installation: Fork של eScriptorium המקורי
```

#### ⚖️ יתרונות וחסרונות

**יתרונות:**
- ✅ מודלים עבריים מוכנים (`heb`, `heb_best`)
- ✅ מצוין לטקסט **מודפס** (printed text)
- ✅ מאגר גדול של מודלים (130+ שפות)
- ✅ אפשרות להשוות Kraken vs Tesseract

**חסרונות:**
- ❌ **לא חלק רשמי** של eScriptorium
- ❌ דורש fork מיוחד (אחזקה מורכבת)
- ❌ Tesseract פחות טוב ל-HTR (**כתב יד**)
- ❌ BiblIA מתמחה בכתב יד → Kraken עדיף

#### 💡 המלצה ל-BiblIA
```
❌ לא מומלץ כרגע
סיבה: BiblIA מתמחה בכתבי יד עתיקים (HTR).
       Tesseract מתמחה בטקסט מודפס (OCR).
       Kraken 5.2.9 עם augmentation מספיק לנו.
```

---

### 2️⃣ CERberus - Character Error Rate Guardian 🐶

#### 📌 מה זה?
**WHaverals/CERberus** - כלי להערכת דיוק OCR/HTR:
- חישוב CER (Character Error Rate)
- חישוב WER (Word Error Rate)
- השוואה בין מודלים
- ויזואליזציה של שגיאות

#### 🔗 מידע טכני
```yaml
Repository: https://github.com/WHaverals/CERberus
Language: HTML + JavaScript
Integration: Standalone tool (לא plugin)
Use Case: Evaluation & Testing
```

#### ⚖️ יתרונות

**מה זה נותן:**
- ✅ הערכת דיוק מדויקת
- ✅ השוואה בין מודלים שונים
- ✅ זיהוי סוגי שגיאות
- ✅ תמיכה ב-eScriptorium/Transkribus

#### 💡 המלצה ל-BiblIA
```
✅ מומלץ לשקול
סיבה: כלי מצוין להערכת ביצועי המודלים שאנחנו מאמנים.
       יכול לעזור להשוות augmentation levels.
       לא דורש שינוי ב-eScriptorium (standalone).
```

---

### 3️⃣ aspyre-gt - Ground Truth Pipeline (alix-tz)

#### 📌 מה זה?
**Pipeline להעברת Ground Truth** מ-Transkribus ל-eScriptorium:
- המרה אוטומטית של ALTO-XML
- שמירת מבנה וסגמנטציה
- העברת transcriptions

#### 🔗 מידע טכני
```yaml
Repository: https://github.com/alix-tz/aspyre-gt
Language: Python
Type: Pipeline Script
Use Case: Data Migration
```

#### 💡 המלצה ל-BiblIA
```
⚠️ רלוונטי אם...
אם יש לך GT ב-Transkribus שרצית להעביר.
אחרת - לא צריך.
```

---

### 4️⃣ Virtual Keyboards (alix-tz, tsmdt)

#### 📌 מה זה?
מקלדות וירטואליות מותאמות לתמלול:
- **virtual-kabbage** (alix-tz) - מחולל מקלדות CSV→JSON
- **keyboardBuilder4eScriptorium** (tsmdt) - בונה מקלדות בקלות

#### 🔗 מידע טכני
```yaml
virtual-kabbage: https://github.com/alix-tz/virtual-kabbage
keyboardBuilder: https://github.com/tsmdt/keyboardBuilder4eScriptorium
Language: Python / HTML
Use Case: Transcription UI Enhancement
```

#### 💡 המלצה ל-BiblIA
```
✅ שימושי אם...
המשתמשים צריכים תווים מיוחדים (ניקוד, סימני פיסוק עתיקים).
יכול לשפר מהירות תמלול.
```

---

### 5️⃣ OCR-D keyboardGT - Keyboards Collection

#### 📌 מה זה?
אוסף **מקלדות ל-5 כלי transcription** כולל eScriptorium:
- Aletheia
- Transkribus
- LAREX
- QURATOR-neat
- **eScriptorium** ✅

#### 🔗 מידע טכני
```yaml
Repository: https://github.com/OCR-D/keyboardGT
Language: XSLT + JSON
Keyboards: German, Latin, Special chars
Use Case: Multi-tool Support
```

---

## 🔍 תוספות מובנות ב-eScriptorium (טרם שילבנו)

### 📊 סיכום: מה חסר ב-BiblIA

#### 1. Elasticsearch - חיפוש מתקדם
```yaml
✅ מותקן: כן (port 9200)
✅ פועל: כן
⚠️ מנוצל: לא!
```

**מה חסר:**
- אינדוקס אוטומטי של תמלולים
- ממשק חיפוש בכל המסמכים
- סינונים מתקדמים

**קוד דוגמה (eScriptorium מקורי):**
```python
# app/apps/core/tasks.py
from elasticsearch import Elasticsearch

def index_transcription(transcription_id):
    """מוסיף תמלול ל-Elasticsearch"""
    es = Elasticsearch([settings.ELASTICSEARCH_URL])
    transcription = LineTranscription.objects.get(pk=transcription_id)
    
    doc = {
        'content': transcription.content,
        'document_id': transcription.line.document_part.document.id,
        'document_name': transcription.line.document_part.document.name,
        'line_order': transcription.line.order,
        'created': transcription.created,
        'confidence': transcription.confidence
    }
    
    es.index(
        index='biblia-transcriptions',
        id=transcription_id,
        body=doc
    )
```

#### 2. Passim - Text Alignment
```yaml
✅ מותקן: כן (Docker container)
✅ פועל: כן (port 8080)
⚠️ מנוצל: לא!
```

**מה זה:**
- ממצא קטעי טקסט זהים/דומים
- Text reuse detection
- Alignment בין גרסאות

**שימוש פוטנציאלי:**
- השוואת תרגומים
- מציאת מקבילות במקורות
- זיהוי שגיאות העתקה

#### 3. Analytics Dashboard - לוח בקרה
```yaml
❌ לא קיים ב-BiblIA
✅ קיים ב-eScriptorium מקורי (חלקי)
```

**מה חסר:**
- סטטיסטיקות אימון מודלים
- גרפים של CER/WER לאורך זמן
- ניתוח ביצועים
- Dashboard אינטראקטיבי

#### 4. Error Detection System - זיהוי שגיאות
```yaml
❌ לא קיים ב-BiblIA
⚠️ לא קיים ב-eScriptorium מקורי (רעיון)
```

**מה זה יכול להיות:**
- זיהוי תווים משונים
- Spell-checking בזמן אמת
- הצעות תיקונים
- Confidence threshold alerts

---

## 🎯 המלצות לפי עדיפות

### 🥇 עדיפות גבוהה (לשקול עכשיו)

#### 1. **CERberus** - Evaluation Tool
```yaml
מאמץ: נמוך (standalone)
תועלת: גבוהה (הערכת מודלים)
זמן: 2-3 שעות להגדרה
```

**למה:**
- נעזור לך להעריך את הצלחת ה-augmentation
- השוואה בין levels (light/medium/heavy)
- זיהוי בעיות ספציפיות

**איך:**
```bash
# התקנה
git clone https://github.com/WHaverals/CERberus.git
cd CERberus

# ייצוא GT מ-eScriptorium
# (כבר יש לך TEXT export)

# הרצת הערכה
python cerberus.py --gt ground_truth.txt --ocr predictions.txt
```

#### 2. **Elasticsearch Integration** - חיפוש מתקדם
```yaml
מאמץ: בינוני (כבר מותקן, צריך integration)
תועלת: גבוהה (חיפוש בכל המסמכים)
זמן: 8-12 שעות
```

**למה:**
- Elasticsearch כבר רץ אצלך!
- רק צריך לחבר אותו
- שיפור משמעותי בשימושיות

**מה צריך:**
1. הוסיף indexing ל-`tasks.py`
2. ליצור search view
3. לעדכן UI עם חיפוש

---

### 🥈 עדיפות בינונית (לעתיד)

#### 3. **Virtual Keyboard** - מקלדת עברית מורחבת
```yaml
מאמץ: נמוך
תועלת: בינונית (תלוי במשתמשים)
זמן: 4-6 שעות
```

**למה:**
- אם משתמשים צריכים ניקוד עתיק
- סימני פיסוק מיוחדים
- תווים ארמיים

#### 4. **Analytics Dashboard** - לוח בקרה
```yaml
מאמץ: גבוה
תועלת: בינונית-גבוהה
זמן: 20-30 שעות
```

**למה:**
- מעקב אחר התקדמות אימון
- גרפים של CER לאורך זמן
- ניתוח ביצועים

---

### 🥉 עדיפות נמוכה (אופציונלי)

#### 5. **Passim Integration** - Text Alignment
```yaml
מאמץ: בינוני
תועלת: נמוכה (specific use case)
זמן: 10-15 שעות
```

**רלוונטי אם:**
- משווים תרגומים
- מחפשים text reuse
- חוקרים מקבילות

#### 6. **Tesseract Extension**
```yaml
מאמץ: גבוה מאוד (fork maintenance)
תועלת: נמוכה ל-BiblIA
זמן: 40+ שעות
```

**לא מומלץ כי:**
- BiblIA מתמחה ב-HTR (כתב יד)
- Tesseract מתמחה ב-OCR (מודפס)
- Kraken כבר מספיק טוב

---

## 📚 משאבים נוספים

### GitHub Repositories - eScriptorium Ecosystem

#### 🔧 Tools & Utilities
1. **CERberus** (WHaverals)
   - https://github.com/WHaverals/CERberus
   - Evaluation metrics (CER/WER)

2. **virtual-kabbage** (alix-tz)
   - https://github.com/alix-tz/virtual-kabbage
   - Virtual keyboard generator

3. **keyboardBuilder4eScriptorium** (tsmdt)
   - https://github.com/tsmdt/keyboardBuilder4eScriptorium
   - Keyboard builder tool

4. **OCR-D keyboardGT**
   - https://github.com/OCR-D/keyboardGT
   - Multi-tool keyboards collection

#### 📖 Documentation & Tutorials
5. **escriptorium-documentation** (alix-tz)
   - https://github.com/alix-tz/escriptorium-documentation
   - Official documentation site (MkDocs)

6. **eScriptorium_Dokumentation** (UB-Mannheim)
   - https://github.com/UB-Mannheim/eScriptorium_Dokumentation
   - German documentation (OCR-BW project)

7. **escriptorium_tutorial** (pjaskulski)
   - https://github.com/pjaskulski/escriptorium_tutorial
   - Polish tutorial (Kraken + eScriptorium)

#### 🔄 Pipelines & Integration
8. **aspyre-gt** (alix-tz)
   - https://github.com/alix-tz/aspyre-gt
   - Transkribus → eScriptorium pipeline

9. **lepidemo** (lectaurep)
   - https://github.com/lectaurep/lepidemo
   - LECTAUREP → TEI Publisher pipeline

10. **PAPYRSER** (oli-do)
    - https://github.com/oli-do/PAPYRSER
    - Ancient Greek TEI-XML parser

#### 📊 Ground Truth Collections
11. **GreekHTR** (PatristicTextArchive)
    - https://github.com/PatristicTextArchive/GreekHTR
    - Greek HTR ground truth

12. **OICEN-HTR** (NKCZ)
    - https://github.com/NKCZ/OICEN-HTR
    - Old Icelandic/Norse HTR

13. **digitue-gt** (UB-Mannheim)
    - https://github.com/UB-Mannheim/digitue-gt
    - UB Tübingen publications GT

14. **dach-gt** (UB-Mannheim)
    - https://github.com/UB-Mannheim/dach-gt
    - German libraries prints GT (Fraktur)

#### 🎓 Academic Projects
15. **TNAH-2021-Projet-Notre-Dame** (PSL-Chartes-HTR-Students)
    - https://github.com/PSL-Chartes-HTR-Students/TNAH-2021-Projet-Notre-Dame
    - Notre-Dame restoration journals (1860)

#### 🔍 Discovery Tools
16. **escriptorium-doc-finder** (alix-tz)
    - https://github.com/alix-tz/escriptorium-doc-finder
    - Listing of eScriptorium resources

---

## 💡 תכנית פעולה מומלצת

### שלב 1: הערכה (השבוע)
```bash
# 1. התקן CERberus להערכת מודלים
git clone https://github.com/WHaverals/CERberus.git

# 2. ייצא GT לבדיקה
# (משתמש ב-export קיים של eScriptorium)

# 3. הרץ הערכה על המודלים הנוכחיים
python cerberus.py --gt gt.txt --ocr model_output.txt
```

### שלב 2: Integration (שבועיים הבאים)
```bash
# 4. חבר Elasticsearch (כבר רץ!)
# עדכן: app/apps/core/tasks.py
# הוסף: indexing functions

# 5. צור search view
# עדכן: app/apps/core/views.py
# הוסף: SearchView class

# 6. עדכן UI
# עדכן: app/apps/core/templates
# הוסף: search box בניווט
```

### שלב 3: Enhancements (חודש הבא)
```bash
# 7. בנה virtual keyboard (אם נדרש)
# השתמש ב-virtual-kabbage או keyboardBuilder

# 8. התחל לבנות Analytics Dashboard
# צור endpoint ל-training statistics
# צור Vue component לגרפים
```

---

## ❓ שאלות נפוצות

### Q1: למה eScriptorium לא מגיע עם כל התוספים האלה?
**A:** eScriptorium הוא פרויקט **modular** - הליבה מספקת פונקציונליות בסיסית, והקהילה מוסיפה extensions לפי צרכים ספציפיים.

### Q2: האם צריך להתקין את כל התוספים?
**A:** **לא!** בחר רק מה שרלוונטי לשימוש שלך. ל-BiblIA מומלץ:
- ✅ CERberus (evaluation)
- ✅ Elasticsearch (כבר רץ)
- ⚠️ Virtual Keyboard (אם נדרש)

### Q3: Tesseract Extension - כדאי?
**A:** **לא ל-BiblIA** כי:
- BiblIA = כתב יד (HTR)
- Tesseract = מודפס (OCR)
- Kraken עדיף ל-HTR

### Q4: איך לבדוק אם Elasticsearch עובד?
```bash
# בדיקה:
curl http://localhost:9200

# צריך לראות:
{
  "name" : "elasticsearch",
  "cluster_name" : "docker-cluster",
  "version" : { ... }
}
```

### Q5: מה ההבדל בין CERberus לבין ketos?
```yaml
ketos:
  - CLI של Kraken
  - אימון מודלים
  - עבודה עם datasets
  
CERberus:
  - Evaluation tool
  - חישוב CER/WER
  - ויזואליזציה של שגיאות
```

---

## 📝 סיכום

### ✅ מה למדנו?
1. יש **16 repositories** בקהילת eScriptorium
2. **4 תוספות** עיקריות שימושיות לאימון:
   - CERberus (evaluation)
   - Elasticsearch (search)
   - Virtual Keyboards (transcription)
   - Analytics Dashboard (monitoring)
3. Tesseract Extension **לא מומלץ** ל-BiblIA

### 🎯 מה הלאה?
1. **השבוע:** התקן CERberus להערכת המודלים
2. **שבועיים:** חבר Elasticsearch (כבר רץ!)
3. **חודש:** בנה Analytics Dashboard

### 📚 קריאה נוספת
- [תוספות_eScriptorium_שטרם_שולבו.md](./תוספות_eScriptorium_שטרם_שולבו.md) - 980 שורות מפורט
- [TESSERACT_INTEGRATION_ANALYSIS.md](./TESSERACT_INTEGRATION_ANALYSIS.md) - ניתוח Tesseract
- [TRAINING_IMPROVEMENTS_PLAN.md](./TRAINING_IMPROVEMENTS_PLAN.md) - תכנית שיפורי אימון

---

**🎉 זיהינו 16 כלים בקהילה + 4 תוספות מובנות שלא שילבנו!**
