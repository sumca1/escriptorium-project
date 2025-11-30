# 🔍 סיכום מהיר: ocrd_kraken ו-ketos

**תאריך:** 22 אוקטובר 2025

---

## 📌 TL;DR

| תוכנה | מותקן? | צריך? | למה? |
|-------|--------|-------|------|
| **ocrd_kraken** | ❌ לא | ❌ לא | wrapper מיותר ל-OCR-D |
| **ketos** | ✅ כן | 🤔 אופציונלי | CLI לאימון (לדיבאג) |

---

## 1️⃣ ocrd_kraken

### מה זה?
**OCR-D wrapper** עבור Kraken - ממשק קו פקודה תואם תקן גרמני OCR-D.

### פקודות
```bash
ocrd-kraken-binarize    # בינריזציה
ocrd-kraken-segment     # סגמנטציה
ocrd-kraken-recognize   # זיהוי טקסט
```

### למה לא צריך?
- eScriptorium משתמש **ישירות** ב-`kraken.lib` (Python API)
- ocrd_kraken זה רק wrapper לפורמט OCR-D
- אין לנו צורך בפורמטים של OCR-D (PAGE-XML, METS, ALTO)
- תוספת מיותרת של תלויות

**המלצה:** ❌ אל תתקין!

---

## 2️⃣ ketos

### מה זה?
**כלי CLI** לאימון מודלים של Kraken (חלק מחבילת `kraken`).

### פקודות עיקריות

```bash
# אימון recognition
ketos train -o model.mlmodel -t data/*.xml --augment --device cuda:0

# אימון segmentation  
ketos segtrain -o seg.mlmodel -t data/*.xml --augment

# בדיקת מודל
ketos test -m model.mlmodel test/*.xml

# הכנת dataset
ketos compile -o dataset.arrow data/*.xml
```

### סטטוס במערכת
```bash
✅ מותקן: kraken 5.2.9
✅ זמין: /usr/local/bin/ketos
✅ Module: /usr/local/lib/python3.8/site-packages/kraken/ketos/
```

### למה צריך? (אופציונלי)
- **debugging** מהיר של מודלים
- **ניסויים** ללא ממשק רשת
- **testing** של hyper-parameters

---

## 🎯 איך משתמשים?

### eScriptorium (שיטה רגילה) ✅
```python
# app/apps/core/tasks.py
from kraken.lib.train import RecognitionModel, KrakenTrainer

model = RecognitionModel(
    hyper_params={'augment': True},
    training_data=files,
    format_type='xml'
)
trainer = KrakenTrainer(max_epochs=50)
trainer.fit(model)
```

### ketos CLI (לדיבאג מהיר) 🔧
```bash
docker exec -it escriptorium_clean-celery-main-1 bash
ketos train -t data/*.xml -o test.mlmodel --epochs 10 --device cuda:0
```

---

## 📊 השוואה

| תכונה | eScriptorium | ketos CLI |
|-------|--------------|-----------|
| ממשק | Web UI | Terminal |
| נתונים | PostgreSQL + XML | XML files |
| ניהול | Django admin | Manual |
| אוגמנטציה | ✅ (שלב 1+2) | ✅ `--augment` |
| GPU | ✅ Celery worker | ✅ `--device` |
| Monitoring | Logs + Admin | TensorBoard |

---

## 💡 רעיונות לשיפור

### מה אפשר ללמוד מ-ketos?

1. **TensorBoard** (שלב 3 שלנו):
```python
from lightning.pytorch.loggers import TensorBoardLogger
trainer = KrakenTrainer(pl_logger=TensorBoardLogger('logs/'))
```

2. **Learning Rate Schedulers**:
```python
hyper_params = {
    'schedule': 'cosine',
    'cos_t_max': 50,
    'cos_min_lr': 1e-5
}
```

3. **Arrow Datasets** (מהיר יותר):
```bash
ketos compile -o dataset.arrow training/*.xml
```

---

## ✅ המלצות סופיות

### כן לעשות
- ✅ המשך עם eScriptorium (Web UI)
- ✅ השתמש ב-Python API של Kraken
- ✅ השתמש בשלבים 1+2 (augmentation)
- ✅ הוסף TensorBoard בעתיד

### לא לעשות
- ❌ אל תתקין ocrd_kraken (מיותר)
- ❌ אל תעבור ל-ketos בלבד (תאבד UI)
- ❌ אל תשנה ארכיטקטורה (עובדת מצוין)

### שימוש אופציונלי
- 🔧 ketos לדיבאג מהיר
- 🔧 ketos לניסויים
- 🔧 ketos לבדיקות מודלים

---

## 🏗️ ארכיטקטורה נוכחית

```
User (Web Browser)
    ↓
eScriptorium Django
    ↓
Celery Tasks (tasks.py)
    ↓
kraken.lib.train (Python API) ← זה מה שאנחנו משתמשים!
    ↓
PyTorch Lightning
    ↓
GPU/CPU Training
```

**לא צריך:**
```
ocrd_kraken (OCR-D wrapper) ✗
```

**יש אבל אופציונלי:**
```
ketos CLI (לדיבאג מהיר) ✓ (אם רוצים)
```

---

## 📚 קישורים

- **Kraken Training:** https://kraken.re/main/training.html
- **ketos Docs:** https://kraken.re/main/ketos.html
- **ocrd_kraken GitHub:** https://github.com/OCR-D/ocrd_kraken
- **המסמך המלא:** [הסבר_OCRD_KRAKEN_ו_KETOS.md](./הסבר_OCRD_KRAKEN_ו_KETOS.md)

---

## 🎊 סיכום אחרון

```
🔍 ocrd_kraken:  ❌ לא צריך (wrapper מיותר)
🔧 ketos:        ✅ יש לנו (אופציונלי לדיבאג)
✨ eScriptorium: ✅ המשך כרגיל (אופטימלי!)
```

**Bottom Line:**  
המערכת שלנו כבר משתמשת ב-Kraken בצורה הנכונה! 🚀

---

*נוצר: 22 אוקטובר 2025*  
*Kraken 5.2.9 | eScriptorium | BiblIA Project*
