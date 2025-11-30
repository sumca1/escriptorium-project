# 📚 OCR-D/ocrd_kraken וכלי האימון של Kraken

**תאריך:** 22 אוקטובר 2025

---

## 🔍 סיכום הממצאים

### 1️⃣ OCR-D/ocrd_kraken

**מה זה?**  
- **Wrapper של OCR-D** עבור מנוע Kraken
- מספק ממשקי קו פקודה תואמי תקן OCR-D
- תומך בתהליך OCR המלא: binarization → segmentation → recognition

**מטרה:**  
אינטגרציה של Kraken עם **OCR-D workflow** - פרוימקט גרמני לסטנדרטיזציה של OCR על חומרים היסטוריים.

**רכיבים עיקריים:**
```
ocrd-kraken-binarize    # בינריזציה של תמונות
ocrd-kraken-segment     # סגמנטציה (זיהוי שורות ואזורים)
ocrd-kraken-recognize   # זיהוי טקסט
```

**פורמטים:**
- קלט/פלט: **PAGE-XML**, **ALTO**, **METS**
- עובד עם **Docker containers**
- תואם ל-**OCR-D ecosystem**

**סטטוס במערכת שלנו:**  
❌ **לא מותקן** - ואין צורך בו!

**למה לא צריך אותו?**
- eScriptorium כבר משתמש **ישירות** בספריית Kraken Python
- ocrd_kraken הוא רק wrapper לתקן OCR-D (פורמט עבודה גרמני)
- אין לנו צורך בתקני OCR-D (אנחנו משתמשים ב-Django + PostgreSQL)
- ההתקנה שלו תוסיף תלויות מיותרות

---

### 2️⃣ ketos (כלי אימון Kraken)

**מה זה?**  
- **כלי CLI** לאימון מודלים של Kraken
- חלק מחבילת `kraken` הרגילה
- פקודה: `ketos`

**פקודות עיקריות:**

#### אימון Recognition (זיהוי טקסט)
```bash
ketos train \
  -f page \                    # פורמט: page/alto/xml
  -o model.mlmodel \            # קובץ פלט
  -t training_data/*.xml \      # נתוני אימון
  -e evaluation_data/*.xml \    # נתוני בדיקה
  --device cuda:0 \             # GPU
  --augment                     # אוגמנטציה
```

#### אימון Segmentation (זיהוי שורות)
```bash
ketos segtrain \
  -o seg_model.mlmodel \
  -t training_data/*.xml \
  --augment \
  --device cuda:0
```

#### פקודות נוספות
```bash
ketos compile         # הכנת datasets
ketos pretrain        # pre-training
ketos test            # בדיקת מודל
ketos publish         # פרסום למאגר
```

**סטטוס במערכת שלנו:**  
✅ **מותקן ופעיל!**

```
Package: kraken 5.2.9
Location: /usr/local/lib/python3.8/site-packages
CLI tool: /usr/local/bin/ketos
Module: /usr/local/lib/python3.8/site-packages/kraken/ketos/
```

---

## 📊 השוואה: eScriptorium vs ketos

| היבט | eScriptorium (שלנו) | ketos CLI |
|------|---------------------|-----------|
| **ממשק** | Web UI + Django | Command line |
| **אימון** | Django tasks + Celery | פקודות ישירות |
| **נתונים** | PostgreSQL + XML files | XML files בלבד |
| **ניהול** | Web interface | Manual scripts |
| **אוגמנטציה** | ✅ מובנה (שלב 1+2) | ✅ דגל `--augment` |
| **GPU** | ✅ דרך Celery worker | ✅ דגל `--device` |
| **Monitoring** | Django admin + logs | CLI output + TensorBoard |

---

## 🔧 איך eScriptorium משתמש ב-Kraken?

### ארכיטקטורה נוכחית

```
eScriptorium (Django)
    ↓
app/apps/core/tasks.py
    ↓ קורא ל-
kraken.lib.train (Python API)
    ↓
RecognitionModel.fit()
SegmentationModel.fit()
    ↓
PyTorch Lightning Trainer
```

**קוד אמיתי מ-tasks.py:**
```python
from kraken.lib.train import RecognitionModel
from kraken.lib.default_specs import RECOGNITION_HYPER_PARAMS

# הגדרות אימון
RECOGNITION_HYPER_PARAMS['augment'] = True  # שלב 1 שלנו!

# אימון
model = RecognitionModel(
    training_data=ground_truth,
    model=existing_model,
    hyper_params=RECOGNITION_HYPER_PARAMS
)
trainer = KrakenTrainer(max_epochs=50)
trainer.fit(model)
```

---

## 💡 מה אפשר ללמוד מ-ketos?

### רעיונות לשיפור eScriptorium

#### 1. TensorBoard Integration (שלב 3 שלנו)
ketos תומך ב-TensorBoard:
```bash
ketos train --logger tensorboard --log-dir ./logs
```

**אפשר להוסיף ל-eScriptorium:**
```python
from lightning.pytorch.loggers import TensorBoardLogger

pl_logger = TensorBoardLogger('logs/', name='training')
trainer = KrakenTrainer(pl_logger=pl_logger)
```

#### 2. Learning Rate Schedulers
ketos תומך ב-schedulers מתקדמים:
```bash
ketos train --schedule cosine --cos-t-max 50 --cos-min-lr 1e-5
```

**קיים ב-kraken.lib.train** - אפשר להשתמש!

#### 3. Dataset Compilation
```bash
ketos compile -o dataset.arrow training_data/*.xml
```
יוצר Arrow datasets מהירים → רעיון לעתיד

---

## 🎯 המלצות

### ✅ מה כדאי לעשות

1. **להמשיך עם eScriptorium** - הממשק הקיים עובד מצוין
2. **להשתמש ב-Python API** של Kraken (כמו עכשיו)
3. **להוסיף TensorBoard** דרך Python (שלב 3)
4. **להפעיל schedulers** דרך hyper_params

### ❌ מה לא כדאי לעשות

1. **להתקין ocrd_kraken** - מיותר לחלוטין
2. **לעבור ל-ketos CLI** - נאבד את ממשק הרשת
3. **לשנות את הארכיטקטורה** - עובדת מצוין

### 🔄 שימוש היברידי אפשרי

אם רוצים **debugging מהיר**:

```bash
# בתוך container
docker exec -it escriptorium_clean-celery-main-1 bash

# אימון ניסיוני מהיר עם ketos
ketos train \
  -f page \
  -o test_model.mlmodel \
  -t /path/to/xml \
  --augment \
  --epochs 10 \
  --device cuda:0
```

**אבל:** לאימון רגיל - eScriptorium עדיף!

---

## 📖 קישורים לתיעוד

### Kraken Official Docs
- **Training Guide:** https://kraken.re/main/training.html
- **ketos Reference:** https://kraken.re/main/ketos.html
- **API Documentation:** https://kraken.re/main/api.html

### OCR-D Project
- **ocrd_kraken GitHub:** https://github.com/OCR-D/ocrd_kraken
- **OCR-D Specs:** https://ocr-d.de/en/spec

### eScriptorium
- **Our Implementation:** `app/apps/core/tasks.py`
- **Training Docs:** `TRAINING_GUIDE_INDEX.md`

---

## 🔬 דוגמאות קוד

### Using ketos CLI (לניסויים)

```bash
# 1. הכנת dataset
ketos compile -o dataset.arrow data/*.xml

# 2. אימון recognition
ketos train \
  -o hebrew_model.mlmodel \
  -s '[1,120,0,1 Lbx200 Do0.1,2 Lbx200 Do]' \
  -t data/*.xml \
  --augment \
  --device cuda:0 \
  --epochs 50 \
  --freq 1.0

# 3. בדיקת מודל
ketos test -m hebrew_model.mlmodel -f page test/*.xml

# 4. אימון segmentation
ketos segtrain \
  -o seg_model.mlmodel \
  -t data/*.xml \
  --augment
```

### Using Python API (בeScriptorium)

```python
# כמו שעושים עכשיו!
from kraken.lib.train import RecognitionModel, KrakenTrainer

model = RecognitionModel(
    hyper_params={'augment': True},  # שלב 1 שלנו
    training_data=training_files,
    evaluation_data=eval_files,
    format_type='xml',
    output='model.mlmodel'
)

trainer = KrakenTrainer(
    max_epochs=50,
    enable_progress_bar=True,
    pl_logger=tensorboard_logger  # שלב 3 עתידי
)

trainer.fit(model)
```

---

## 🎊 סיכום סופי

### ocrd_kraken
```
מה זה:       OCR-D wrapper לKraken
סטטוס:       ❌ לא מותקן
צריך אותו:   ❌ לא!
סיבה:        אנחנו משתמשים ישירות בKraken API
```

### ketos (kraken training)
```
מה זה:       כלי CLI לאימון מודלים
סטטוס:       ✅ מותקן (kraken 5.2.9)
צריך אותו:   🤔 אופציונלי
שימוש:       debugging, ניסויים מהירים
```

### המלצה
```
✅ המשך עם eScriptorium + Python API
✅ השתמש בשלבים 1+2 שיישמנו
✅ הוסף TensorBoard בעתיד (שלב 3)
❌ אל תתקין ocrd_kraken
🔄 ketos יכול לשמש לדיבאג מהיר
```

---

**מסקנה:**  
אין צורך בשינויים! המערכת שלנו משתמשת ב-Kraken בצורה האופטימלית דרך Python API. ketos זמין לניסויים אבל eScriptorium עדיף לשימוש רגיל.

---

*נוצר: 22 אוקטובר 2025*  
*מבוסס על: Kraken 5.2.9, eScriptorium, OCR-D documentation*
