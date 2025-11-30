# CERberus Quick Start Guide

**מדריך התחלה מהירה לניתוח Character Error Rate ב-eScriptorium**

---

## 📋 מה זה CER (Character Error Rate)?

**CER** הוא מדד לאיכות OCR שמודד כמה טעויות יש בטקסט שזוהה בהשוואה לטקסט נכון (ground truth).

**נוסחה**:
```
CER = (Substitutions + Insertions + Deletions) / Total Characters × 100%
```

**דוגמה**:
- Ground Truth: "שלום עולם"
- Hypothesis: "שלוס עולם"
- טעויות: 1 תחליף ('ם' → 'ס')
- CER: 1/10 = **10%**

**מה זה אומר**:
- 🟢 **< 5%** - מצוין! OCR איכותי מאוד
- 🟠 **5-15%** - טוב, אבל אפשר לשפר
- 🔴 **> 15%** - דורש שיפור משמעותי

---

## 🚀 שימוש מהיר דרך Django Admin

### שלב 1: גש לממשק Admin

1. פתח דפדפן: http://localhost:8082/admin/
2. התחבר עם שם משתמש וסיסמה
3. נווט ל: **Cerberus Integration → CER analyses**

### שלב 2: צפה בניתוחים קיימים

תראה רשימה של ניתוחים עם:
- 🟢🟠🔴 **CER צבעוני** - זיהוי מהיר של בעיות
- **Accuracy** - אחוז הצלחה
- **Total Characters** - גודל הטקסט
- **Created at** - תאריך

### שלב 3: צפה בפרטים

לחץ על ניתוח כדי לראות:
- **Core Metrics**: CER, Accuracy, Total chars
- **Detailed Statistics**: תחליפים, הכנסות, מחיקות
- **Error Breakdown**: אחוזי שגיאות לפי סוג
- **Top Confusions**: 10 הטעויות הנפוצות ביותר

**דוגמה לטבלת Confusions**:
```
+----------+----------+-------+
| Correct  | Wrong    | Count |
+----------+----------+-------+
| ה        | ח        | 45    |
| כ        | ב        | 32    |
| ד        | ר        | 28    |
+----------+----------+-------+
```

---

## 🔧 שימוש דרך API (למתקדמים)

### הכנה: קבל Token

```bash
docker-compose exec web python manage.py drf_create_token YOUR_USERNAME
```

שמור את ה-Token שמתקבל!

### יצירת ניתוח חדש

```bash
curl -X POST http://localhost:8082/api/cerberus/analyses/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "ground_truth_transcription_id": 33,
    "hypothesis_transcription_id": 1,
    "ignore_case": false,
    "analyze_unicode_blocks": true
  }'
```

**תשובה**:
```json
{
  "id": 1,
  "cer_value": 18.75,
  "accuracy": 81.25,
  "num_correct": 13,
  "num_substitutions": 2,
  "num_insertions": 1,
  "num_deletions": 0
}
```

### קבל את ה-Confusions

```bash
curl -X GET "http://localhost:8082/api/cerberus/analyses/1/confusion_matrix/?limit=10" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### ייצא ל-CSV (לפתיחה ב-Excel)

```bash
curl -X GET "http://localhost:8082/api/cerberus/analyses/1/export/?format=csv&data_type=confusion" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -o confusions.csv
```

פתח את `confusions.csv` ב-Excel כדי לנתח טעויות!

---

## 🎯 תרחישים נפוצים

### תרחיש 1: השוואת מודלי OCR

**מטרה**: לבדוק איזה מודל OCR טוב יותר.

1. הרץ OCR עם **Kraken Model A** → שמור כ-Transcription 10
2. הרץ OCR עם **Kraken Model B** → שמור כ-Transcription 11
3. יש לך **Ground Truth ידני** → Transcription 5

**צור 2 ניתוחים**:
```bash
# Model A vs Ground Truth
curl -X POST .../analyses/ -d '{
  "ground_truth_transcription_id": 5,
  "hypothesis_transcription_id": 10
}'

# Model B vs Ground Truth  
curl -X POST .../analyses/ -d '{
  "ground_truth_transcription_id": 5,
  "hypothesis_transcription_id": 11
}'
```

**השווה CER**:
- Model A: CER = 8.5% ✅
- Model B: CER = 12.3%
- **תוצאה**: Model A טוב יותר!

---

### תרחיש 2: זיהוי תווים בעייתיים

**מטרה**: למצוא אילו תווים עבריים הכי קשים ל-OCR.

1. צור ניתוח
2. קבל תווים בעייתיים:

```bash
curl -X GET ".../analyses/1/problematic_characters/?threshold=0.7" \
  -H "Authorization: Token ..."
```

**תשובה**:
```json
{
  "problematic_characters": [
    {"character": "ץ", "correct_ratio": 0.45},
    {"character": "ף", "correct_ratio": 0.52},
    {"character": "ך", "correct_ratio": 0.68}
  ]
}
```

**מה לעשות**:
- אמן את המודל עם **יותר דוגמאות** של ץ, ף, ך
- או השתמש ב-**Post-correction rules**

---

### תרחיש 3: בדיקת השפעת אפשרויות

**מטרה**: האם להתעלם מרווחים משפר את ה-CER?

```bash
# ללא ignore
curl -X POST .../analyses/ -d '{
  "ground_truth_transcription_id": 5,
  "hypothesis_transcription_id": 10,
  "ignore_whitespace": false
}'
# → CER: 15.2%

# עם ignore
curl -X POST .../analyses/ -d '{
  "ground_truth_transcription_id": 5,
  "hypothesis_transcription_id": 10,
  "ignore_whitespace": true
}'
# → CER: 11.8%
```

**תוצאה**: התעלמות מרווחים הורידה CER ב-3.4%!

---

## 📊 ניתוח Unicode Blocks (עברית/ערבית)

CERberus מנתח בנפרד כל Unicode block:

**Hebrew Block** (0x0590-0x05FF):
- כולל: א-ת, ניקוד, טעמים
- CER: 8.2%
- Confusions: ה↔ח, כ↔ב, ד↔ר

**Arabic Block** (0x0600-0x06FF):
- כולל: ا-ي, דיאקריטיים
- CER: 12.5%
- Confusions: ب↔ت, ج↔ح

**Latin Block**:
- CER: 3.1% (קל יותר!)

**Punctuation**:
- CER: 25.8% (קשה!)

**שימוש**:
```bash
curl -X GET .../analyses/1/ | jq '.block_statistics'
```

---

## 🔍 פענוח Error Breakdown

**Error Breakdown** מראה התפלגות שגיאות:

```json
{
  "substitutions": 60.5,  // 60.5% מהשגיאות = תחליפים
  "insertions": 25.2,     // 25.2% = תווים מיותרים
  "deletions": 14.3       // 14.3% = תווים חסרים
}
```

**מה זה אומר**:
- **Substitutions גבוהות** → בעיית דמיון תווים (ה↔ח)
- **Insertions גבוהות** → OCR רואה תווים שלא קיימים
- **Deletions גבוהות** → OCR מפספס תווים

**פתרונות**:
- Substitutions → אמן עם תווים דומים
- Insertions → בדוק איכות תמונה (רעש)
- Deletions → בדוק contrast/binarization

---

## 💡 טיפים מתקדמים

### 1. השתמש ב-ignore_case לטקסטים עם אותיות גדולות/קטנות

```json
{
  "ignore_case": true
}
```

טוב עבור: לטינית, טורקית
לא רלוונטי עבור: עברית, ערבית

### 2. התעלם מניקוד אם לא חשוב

```json
{
  "ignore_chars": "ְֱֲֳִֵֶַָֹֺֻּֽׁׂ׃"
}
```

### 3. השתמש ב-batch_size גדול לביצועים

```bash
# ניתוח של 100 מסמכים
for id in {1..100}; do
  curl -X POST .../analyses/ -d "{ ... }"
done
```

### 4. ייצא ל-CSV לניתוח ב-Pandas

```python
import pandas as pd

df = pd.read_csv('confusions.csv')
top_10 = df.nlargest(10, 'count')
print(top_10)
```

---

## 🐛 פתרון בעיות נפוצות

### בעיה: "Authentication credentials were not provided"

**פתרון**:
```bash
# קבל token חדש
docker-compose exec web python manage.py drf_create_token YOUR_USERNAME

# השתמש בו בכל בקשה
-H "Authorization: Token YOUR_TOKEN_HERE"
```

### בעיה: "Transcription matching query does not exist"

**פתרון**:
```bash
# בדוק ID נכון
docker-compose exec web python manage.py shell -c \
  "from core.models import Transcription; print(list(Transcription.objects.values_list('id', 'name')))"
```

### בעיה: CER = 100%

**סיבה**: אחד מה-transcriptions ריק!

**בדיקה**:
```bash
curl .../transcriptions/1/ | jq '.content'
# אם מחזיר "" → ריק!
```

### בעיה: Confusions ריק

**סיבה**: אין תחליפים, רק insertions/deletions.

**זה תקין** אם:
- Ground truth ריק → רק deletions
- Hypothesis ריק → רק insertions
- התאמה מושלמת → אין confusions

---

## 📚 משאבים נוספים

- **API Reference**: `CERBERUS_API_REFERENCE.md`
- **Phase 2 Complete**: `CERBERUS_PHASE2_COMPLETE.md`
- **Django Admin**: http://localhost:8082/admin/cerberus_integration/ceranalysis/
- **Test Command**: `docker-compose exec web python manage.py test_cerberus_api`

---

## 🎓 לימוד נוסף

### מאמרים מומלצים:
- [Understanding Character Error Rate (CER)](https://en.wikipedia.org/wiki/Word_error_rate)
- [OCR Evaluation Metrics](https://www.sciencedirect.com/topics/computer-science/character-error-rate)
- [CERberus Original Tool](https://github.com/WHaverals/CERberus)

### וידאו tutorials (אופציונלי):
- eScriptorium Training: https://escriptorium.fr/tutorials/
- Kraken OCR: https://kraken.re/

---

## ✅ Checklist למשתמש חדש

- [ ] התקן token authentication
- [ ] צור ניתוח ראשון דרך API
- [ ] צפה בניתוח ב-Django Admin
- [ ] ייצא confusion matrix ל-CSV
- [ ] זיהה 3 תווים בעייתיים ביותר
- [ ] השווה 2 מודלי OCR
- [ ] הבן את ה-error breakdown
- [ ] נסה אפשרויות ignore

---

**סיימת? מצוין! עכשיו אתה יכול לנתח CER כמו מקצוען! 🎉**

**תאריך עדכון אחרון**: 26 באוקטובר 2024  
**גרסה**: 1.0
