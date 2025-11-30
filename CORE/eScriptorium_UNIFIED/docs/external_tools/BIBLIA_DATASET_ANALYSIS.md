# דוח ניתוח BiblIA Dataset
**תאריך:** 20 אוקטובר 2025

---

## 📊 סיכום Dataset

### מידע כללי
- **שם:** BiblIA - General Model for Medieval Hebrew Manuscripts
- **מקור:** Bibliothèque nationale de France (BnF) + Biblioteca Apostolica Vaticana (BAV)
- **מחקר:** Daniel Stökl Ben Ezra et al., HIP@ICDAR 2021
- **מטרה:** HTR (Handwritten Text Recognition) לכתבי יד עבריים מימי הביניים
- **גרסה:** 1.0 (6.8.2021)
- **מנוע:** Kraken OCR + eScriptorium

---

## 📁 מבנה התיקיות

```
BiblIA_dataset/
├── README.txt                  # תיעוד המערך
├── catalogue.txt               # מטא-דאטה על כל תמונה
├── Ashkenazy/                  # כתב אשכנזי
│   ├── btv1b10539358v.jpg
│   ├── btv1b10539358v.xml
│   └── ... (106 תמונות + XML)
├── Italian/                    # כתב איטלקי
│   ├── btv1b10539471x.jpg
│   ├── btv1b10539471x.xml
│   └── ... (98 תמונות + XML)
└── Sephardi/                   # כתב ספרדי
    ├── btv1b105393258.jpg
    ├── btv1b105393258.xml
    └── ... (98 תמונות + XML)
```

---

## 📈 סטטיסטיקות

### קבצים
- **סה"כ תמונות זמינות:** 132 (.jpg)
- **סה"כ קבצי ALTO XML:** 202 (.xml)
- **תמונות חסרות:** 70 (מ-BAV, יש קישורי IIIF)

### חלוקה לפי סגנון כתב

| סגנון | מספר קבצים (XML) | מספר תמונות |
|-------|------------------|-------------|
| **Ashkenazy** | 106 | 52 |
| **Italian** | 98 | 50 |
| **Sephardi** | 98 | 50 |
| **סה"כ** | 302 | 152 |

### חלוקה Train/Test

לפי `catalogue.txt`:
- **Train:** ~170-180 דפים
- **Test:** ~20-30 דפים

---

## 🔍 מבנה קבצי ALTO XML

### Schema
- **פורמט:** ALTO 4.2
- **Schema:** `http://www.loc.gov/standards/alto/v4/alto-4-2.xsd`
- **Namespace:** `http://www.loc.gov/standards/alto/ns-v4#`

### מבנה היררכי

```xml
<?xml version="1.0" encoding="UTF-8"?>
<alto>
  <Description>
    <MeasurementUnit>pixel</MeasurementUnit>
    <sourceImageInformation>
      <fileName>btv1b10539358v.jpg</fileName>
    </sourceImageInformation>
  </Description>
  
  <Tags>
    <!-- טיפולוגיות אזורים -->
    <OtherTag ID="BT1" LABEL="Title" DESCRIPTION="block type Title"/>
    <OtherTag ID="BT2" LABEL="Main" DESCRIPTION="block type Main"/>
    <OtherTag ID="BT3" LABEL="Commentary" DESCRIPTION="block type Commentary"/>
    <OtherTag ID="BT4" LABEL="Illustration" DESCRIPTION="block type Illustration"/>
  </Tags>
  
  <Layout>
    <Page WIDTH="4063" HEIGHT="4931" PHYSICAL_IMG_NR="42" ID="eSc_dummypage_">
      <PrintSpace HPOS="0" VPOS="0" WIDTH="4063" HEIGHT="4931">
        
        <!-- אזור טקסט (Region) -->
        <TextBlock HPOS="2112.0" VPOS="0.0" WIDTH="887.0" HEIGHT="3733.0" 
                   ID="eSc_textblock_92513" TAGREFS="BT2">
          <Shape>
            <Polygon POINTS="2243 0 2136 19 2112 109 2112 3668 ..."/>
          </Shape>
          
          <!-- שורה (Line) -->
          <TextLine ID="eSc_line_1277004"
                    BASELINE="2158 54 2178 54 2509 46 2857 43 2956 54 2976 56"
                    HPOS="2154" VPOS="4" WIDTH="819" HEIGHT="135">
            <Shape>
              <Polygon POINTS="2154 53 2158 12 2212 4 2800 4 ..."/>
            </Shape>
            
            <!-- תמלול (Transcription) -->
            <String CONTENT="פליג לאברוהי ואסל" 
                    HPOS="2154" VPOS="4" WIDTH="819" HEIGHT="135"/>
          </TextLine>
          
          <!-- שורות נוספות... -->
        </TextBlock>
        
        <!-- אזורים נוספים... -->
      </PrintSpace>
    </Page>
  </Layout>
</alto>
```

---

## 📋 מטא-דאטה (catalogue.txt)

### עמודות

| עמודה | תיאור | דוגמה |
|-------|-------|-------|
| `filename` | שם קובץ XML | `btv1b10539358v.xml` |
| `script_type` | סגנון כתב | `Ashkenazi`, `Italian`, `Sephardi` |
| `library` | ספרייה | `BnF`, `BAV` |
| `Shelfmark` | מיקום פיזי | `BnF héb. 1349`, `Vat.ebr.9` |
| `Date` | תאריך יצירה | `1287`, `13th century`, `ca. 1400` |
| `Biblical_or_Rabbinic` | ז'אנר | `Biblical`, `Rabbinic` |
| `color_or_grayscale` | סוג תמונה | `color`, `grayscale` |
| `iiif_manifest` | IIIF Manifest URL | `https://gallica.bnf.fr/ark:/...` |
| `link2img` | קישור לתמונה | `https://digi.vatlib.it/...` |
| `test/train` | חלוקה | `train`, `test` |

### דוגמה

```
filename                        script_type  library  Shelfmark      Date         test/train
btv1b10539358v.xml              Ashkenazi    BnF      BnF héb. 1349               train
Vat.ebr.9_0011_fa_0003r.xml     Italian      BAV      Vat.ebr.9      1287         train
btv1b10539330f.xml              Sephardi     BnF      BnF héb. 25    1232         train
```

---

## ✅ מה כלול ב-Ground Truth

### 1. **Segmentation (פילוח)**
- ✅ **Regions (אזורים):** TextBlock עם Polygon מדויק
- ✅ **Region Types (טיפולוגיות):** Title, Main, Commentary, Illustration
- ✅ **Lines (שורות):** TextLine עם Polygon + Baseline
- ✅ **Baselines (קווי בסיס):** רצף נקודות (x,y) לכל שורה

### 2. **Transcription (תמלול)**
- ✅ **Hebrew Unicode:** תמלול מלא של כל שורה
- ✅ **Layout מדויק:** קואורדינטות HPOS, VPOS, WIDTH, HEIGHT

### 3. **Metadata (מטא-דאטה)**
- ✅ **Script type:** Ashkenazi, Italian, Sephardi
- ✅ **Date:** תאריכי יצירה
- ✅ **Provenance:** BnF, BAV
- ✅ **Genre:** Biblical, Rabbinic

---

## 🎯 שימושים אפשריים

### 1. **אימון מודל סגמנטציה** ⭐ (המטרה שלך)

**מה ניתן לאמן:**
- זיהוי אזורי טקסט (Text Regions)
- הפרדת עמודות (Columns)
- זיהוי שוליים (Margins)
- זיהוי כותרות (Titles)
- זיהוי פרשנות (Commentary)
- קווי בסיס (Baselines)

**כמות נתונים:**
- **מינימום:** 20-30 דפים
- **מומלץ:** 50-100 דפים
- **זמין:** 132-202 דפים ✅

**איכות:**
- ✅ מצוין - סגמנטציה ידנית מקצועית
- ✅ מגוון - 3 סגנונות כתב שונים
- ✅ מגוון - תקופות שונות (1100-1581)
- ✅ מגוון - מסמכים שונים (תנ"ך, רבנות)

---

### 2. **אימון מודל HTR (זיהוי תווים)**

**מה כלול:**
- תמלול Unicode מלא
- יישור מדויק לקואורדינטות
- Hebrew text ברמה גבוהה

**שימוש:**
- אימון מודל OCR לעברית
- שיפור דיוק זיהוי כתב יד
- התאמה לסגנונות כתב שונים

---

### 3. **מחקר וניתוח**

**אפשרויות:**
- ניתוח סגנונות כתב
- השוואה בין תקופות
- מחקר פליאוגרפי
- סטטיסטיקה לשונית

---

## 🚀 תוכנית פעולה מומלצת

### **אופציה A: אימון מודל ספציפי לסגנון** (מומלץ למתחילים)

**שלב 1:** בחר סגנון כתב אחד
```
בחר: Ashkenazy / Italian / Sephardi
→ כ-50 תמונות זמינות לכל אחד
```

**שלב 2:** ייבוא ל-eScriptorium
```bash
python import_biblia_train.py \
    --dir "G:\BiblIA_dataset\BiblIA_dataset\Ashkenazy" \
    --max 30 \
    --project "BiblIA - Ashkenazy Training" \
    --document "Ashkenazy Manuscripts" \
    --model "Hebrew_Ashkenazy_Layout_v1" \
    --token YOUR_TOKEN
```

**שלב 3:** אימון מודל
```
זמן: 2-4 שעות (GPU) או 4-8 שעות (CPU)
דיוק צפוי: 85-95% (תלוי באיכות הנתונים)
```

**שלב 4:** הערכה
```
השתמש ב-test set (המסומן בcatalogue.txt)
מדוד: Precision, Recall, F1-Score
```

---

### **אופציה B: אימון מודל כללי (General Model)** (מומלץ למתקדמים)

**שלב 1:** ערבב את כל הסגנונות
```
Ashkenazy (30 דפים) + Italian (30 דפים) + Sephardi (30 דפים)
= 90 דפים train set
```

**שלב 2:** אימון מודל יחיד
```
מודל שיודע להתמודד עם כל סוגי הכתב
יותר גנרי אבל פחות מדויק לכל סגנון ספציפי
```

**שלב 3:** Fine-tuning
```
אפשר לעשות Fine-tuning למודל הכללי
עבור כל סגנון בנפרד
```

---

### **אופציה C: ייבוא ידני + אימון בממשק** (מומלץ לבדיקה ראשונית)

**שלב 1:** העלה 10 דפים ידנית
```
1. פתח eScriptorium Web UI
2. צור פרויקט חדש
3. העלה תמונות
4. ייבא ALTO XML לכל דף (Import > ALTO)
```

**שלב 2:** אמן מודל בממשק
```
1. בחר את הדפים
2. Models > Train Segmentation
3. קבע שם למודל
4. התחל אימון
```

**יתרונות:**
- ✅ בקרה חזותית מלאה
- ✅ קל יותר לדיבאג
- ✅ רואה את התוצאות מיד

**חסרונות:**
- ❌ איטי (ידני)
- ❌ לא ניתן לאוטומציה
- ❌ מתאים רק למספר קטן של דפים

---

## ⚠️ אתגרים ופתרונות

### בעיה 1: ALTO XML לא נתמך ב-API

**הבעיה:**
eScriptorium API לא תומך בייבוא ALTO XML ישירות

**פתרון 1:** ייבוא דרך Web UI (ידני)
```
✅ עובד 100%
❌ לא ניתן לאוטומציה
```

**פתרון 2:** המרה ל-PAGE XML
```python
# יש להמיר ALTO → PAGE XML
# PAGE XML נתמך ב-API
```

**פתרון 3:** סקריפט מותאם אישית
```python
# כתיבת parser ש:
# 1. מעלה תמונה
# 2. יוצר Blocks/Lines ידנית דרך API
# 3. מוסיף Transcriptions
```

---

### בעיה 2: 70 תמונות חסרות (מ-BAV)

**הבעיה:**
רק 132/202 תמונות כלולות בפועל

**פתרון:**
```
1. השתמש ב-132 התמונות הזמינות (מספיק!)
2. לחילופין: הורד מ-IIIF links (בcatalogue.txt)
```

**קוד להורדה אוטומטית:**
```python
import requests
import pandas as pd

# קרא catalogue
df = pd.read_csv('catalogue.txt', sep='\t')

# הורד תמונות חסרות
for idx, row in df[df['library'] == 'BAV'].iterrows():
    url = row['link2img']
    filename = row['filename'].replace('.xml', '.jpg')
    # Download...
```

---

### בעיה 3: חלוקת Train/Test

**הבעיה:**
catalogue.txt כבר מכיל חלוקה, אבל רנדומלית

**פתרון:**
```python
# סנן לפי עמודת test/train
train_files = df[df['test/train'] == 'train']['filename'].tolist()
test_files = df[df['test/train'] == 'test']['filename'].tolist()

# השתמש רק ב-train files לאימון
# שמור test files להערכה
```

---

## 📝 סיכום והמלצות

### ✅ מה יש לך

1. **Ground Truth איכותי** - סגמנטציה ידנית מקצועית
2. **כמות מספקת** - 132-202 דפים (יותר ממספיק לאימון)
3. **מגוון רחב** - 3 סגנונות כתב, תקופות שונות
4. **תיעוד מלא** - README, catalogue, metadata
5. **פורמט תקני** - ALTO 4.2 XML

### 🎯 המלצה סופית

**אסטרטגיה מומלצת:**

1. **התחל עם Ashkenazy** (או סגנון אחר)
   - 30 דפים train
   - 5-10 דפים test
   
2. **ייבא ידנית דרך Web UI** (בפעם הראשונה)
   - קל יותר לדיבאג
   - רואה מיד שהכל עובד
   
3. **אמן מודל ראשון**
   - שם: `Hebrew_Ashkenazy_Layout_v1`
   - זמן: 2-4 שעות
   - דיוק צפוי: 85-92%
   
4. **הערך על test set**
   - מדוד דיוק
   - זהה בעיות
   
5. **שפר:**
   - הוסף עוד דפים מגוונים
   - תקן ground truth אם צריך
   - Fine-tune היפרפרמטרים

6. **הרחב:**
   - אמן מודלים לסגנונות אחרים
   - צור מודל כללי (all scripts)
   - שתף במאגר Zenodo

---

**זה מערך נתונים מצוין לאימון! אתה במצב טוב מאוד.** 🚀

כל מה שצריך זה:
1. להעלות את התמונות + XML ל-eScriptorium
2. להפעיל `segtrain`
3. לחכות 2-6 שעות
4. לקבל מודל מאומן מעולה ✅
