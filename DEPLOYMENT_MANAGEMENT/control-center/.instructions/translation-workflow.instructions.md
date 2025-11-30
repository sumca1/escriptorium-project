---
description: CRITICAL - Complete translation workflow guide for AI chatbots
applyTo: '**'
---

# 🌐 מדריך תרגומים מלא - Translation Workflow Guide
**חובה לכל AI chatbot שעובד על תרגומים!**

---

## 🚨 **חובה לקריאה ראשונה!**

**לפני שמתחיל לקרוא את המסמך הזה:**
- ✅ **קרא תחילה:** `eScriptorium_CLEAN/.github/instructions/MANDATORY_FIRST_ACTION.md`
- 🔧 **נושאים קריטיים:** SSL/pip issues, MCP tools availability
- ⚡ **עדיפות:** HIGHEST - חובה בכל סשן חדש!

---

## 📍 CRITICAL: נתיבים נכונים (Correct Paths)

### ⚠️ שגיאה נפוצה #1: "The term is not recognized"

**❌ לא עובד:**
```powershell
# מנסה להריץ מתיקיית BiblIA_dataset (root)
PS G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset> .\scripts\compile-translations.ps1 -Language he
# שגיאה: The term '.\scripts\compile-translations.ps1' is not recognized
```

**✅ הפתרון הנכון:**

#### **אופציה 1: שנה תיקייה ל-eScriptorium_CLEAN תחילה**
```powershell
# מתיקיית BiblIA_dataset (root)
cd eScriptorium_CLEAN
.\scripts\compile-translations.ps1 -Language he
```

#### **אופציה 2: נתיב מלא מכל מקום**
```powershell
# מכל תיקייה
pwsh -File "G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\scripts\compile-translations.ps1" -Language he
```

#### **אופציה 3: נתיב יחסי נכון**
```powershell
# מתיקיית BiblIA_dataset (root)
.\eScriptorium_CLEAN\scripts\compile-translations.ps1 -Language he
```

---

## 📂 מבנה תיקיות (Directory Structure)

```
BiblIA_dataset/                                      ← ROOT
│
├── eScriptorium_CLEAN/                              ← תיקיית עבודה ראשית
│   │
│   ├── scripts/                                     ← סקריפטי אוטומציה
│   │   ├── compile-translations.ps1                 ← קומפילציה ⭐
│   │   ├── build-and-deploy.ps1
│   │   └── verify-deployment.ps1
│   │
│   └── app/                                         ← Django backend
│       └── locale/                                  ← תרגומי Django
│           └── he/
│               └── LC_MESSAGES/
│                   ├── django.po                    ← קובץ תרגום ⭐
│                   └── django.mo                    ← קובץ קומפילד
│
├── scripts/                                         ← סקריפטי Python כלליים
│   ├── find_empty_translations.py                   ← מציאת תרגומים ריקים ⭐
│   ├── auto_fill_7_translations.py                  ← הוספת תרגומים
│   └── auto_fill_he_multiline.py
│
├── check_missing_translations.py                    ← בדיקת תרגומים חסרים ⭐
└── remove_po_duplicates.py                          ← הסרת כפילויות ⭐
```

---

## 🔍 איך מוצאים תרגומים חסרים? (Find Missing Translations)

### **שיטה 1: סקריפט Python - `find_empty_translations.py` (מומלץ!)**

```powershell
# הרץ מתיקיית BiblIA_dataset (root)
python scripts\find_empty_translations.py
```

**מה הסקריפט עושה:**
- ✅ קורא את `eScriptorium_CLEAN\app\locale\he\LC_MESSAGES\django.po`
- ✅ מחפש שורות עם `msgstr ""`
- ✅ בודק שהשורה הבאה מתחילה ב-`#` (לא continuation)
- ✅ יוצר קובץ JSON עם כל התרגומים החסרים: `missing_translations.json`
- ✅ מדפיס רשימה מסודרת

**פלט לדוגמה:**
```
🔍 סריקת קובץ django.po לחיפוש msgstr ריקים...

נמצאו 7 msgstr ריקים:

1. Line 3456: "Create Corpus in Admin"
2. Line 3789: "Automatically generate training data..."
3. Line 4012: "TABA Pipeline Dashboard"
...

💾 שמירת רשימה ל-missing_translations.json
✅ סיום! נמצאו 7 תרגומים חסרים
```

---

### **שיטה 2: חיפוש ידני עם grep (מהיר)**

```powershell
# מתיקיית BiblIA_dataset (root)
Select-String -Path "eScriptorium_CLEAN\app\locale\he\LC_MESSAGES\django.po" -Pattern 'msgstr ""' -Context 1,0 | Select-Object -First 20
```

**הסבר:**
- `-Pattern 'msgstr ""'` - מחפש msgstr ריק
- `-Context 1,0` - מציג שורה אחת לפני (msgid) ואפס אחרי
- `-First 20` - מגביל ל-20 תוצאות ראשונות

---

### **שיטה 3: בדיקה מקיפה עם `check_missing_translations.py`**

```powershell
# הרץ מתיקיית BiblIA_dataset (root)
python check_missing_translations.py
```

**מה הסקריפט עושה:**
- ✅ קורא את כל קובץ `django.po`
- ✅ מחפש msgid/msgstr pairs
- ✅ מחשב כמה תרגומים חסרים
- ✅ מדפיס דוגמאות

**⚠️ הערה:** הסקריפט הזה **לא מטפל טוב ב-multi-line msgid**, לכן עדיף להשתמש ב-`find_empty_translations.py`!

---

## 🛠️ תהליך עבודה מלא (Complete Workflow)

### **תרחיש: צ'אטבוט מקבל משימה "תרגם הכל"**

```powershell
# שלב 1: מצא תרגומים חסרים
cd G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset
python scripts\find_empty_translations.py

# שלב 2: צור מיפוי תרגומים (ידני או אוטומטי)
# ערוך את missing_translations.json והוסף תרגומים

# שלב 3: הרץ סקריפט הוספה
python scripts\auto_fill_7_translations.py

# שלב 4: הסר duplicates
python remove_po_duplicates.py --locale-dir eScriptorium_CLEAN\app\locale --inplace --backup

# שלב 5: קומפל תרגומים
cd eScriptorium_CLEAN
.\scripts\compile-translations.ps1 -Language he

# שלב 6: אתחל web service
docker-compose restart web

# שלב 7: אמת (בדפדפן או בלוגים)
docker-compose logs web | Select-String -Pattern "locale"
```

---

## 📝 קובץ התרגום django.po - מבנה (PO File Structure)

### **דוגמה לתרגום חסר:**

```po
#: apps/taba_pipeline/templates/taba_pipeline/corpus_list.html:104
msgid ""
"You haven't created any Ground Truth corpora yet. Create one in the Django "
"admin to get started."
msgstr ""
                                ← שורה ריקה או # (זה הסימן!)

#: apps/taba_pipeline/templates/taba_pipeline/corpus_list.html:106
```

### **דוגמה לתרגום קיים:**

```po
#: apps/taba_pipeline/templates/taba_pipeline/dashboard.html:16
msgid ""
"Automatically generate training data by aligning OCR with known digital "
"texts using Passim"
msgstr ""
"ייצר נתוני אימון אוטומטית על ידי יישור OCR עם טקסטים דיגיטליים ידועים "
"באמצעות Passim"
                                ← יש msgstr! (לא ריק)

#: apps/taba_pipeline/templates/taba_pipeline/dashboard.html:26
```

---

## ⚙️ פקודות נפוצות - Quick Reference

### **1. מציאת תרגומים חסרים:**
```powershell
python scripts\find_empty_translations.py
```

### **2. הוספת תרגומים:**
```powershell
python scripts\auto_fill_7_translations.py
```

### **3. הסרת duplicates:**
```powershell
python remove_po_duplicates.py --locale-dir eScriptorium_CLEAN\app\locale --inplace --backup
```

### **4. קומפילציה:**
```powershell
cd eScriptorium_CLEAN
.\scripts\compile-translations.ps1 -Language he
```

### **5. אתחול שירות:**
```powershell
docker-compose restart web
```

### **6. בדיקת לוגים:**
```powershell
docker-compose logs web --tail 100 | Select-String -Pattern "locale\|translation\|compil"
```

---

## 🚨 שגיאות נפוצות ופתרונות (Common Errors)

### **שגיאה 1: "The term is not recognized"**

**סיבה:** רץ מתיקייה לא נכונה

**פתרון:**
```powershell
# וודא שאתה ב-eScriptorium_CLEAN
cd G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN
.\scripts\compile-translations.ps1 -Language he
```

---

### **שגיאה 2: "duplicate message definition"**

**סיבה:** יש duplicates בקובץ django.po

**פתרון:**
```powershell
python remove_po_duplicates.py --locale-dir eScriptorium_CLEAN\app\locale --inplace --backup
```

---

### **שגיאה 3: "No such file or directory: django.po"**

**סיבה:** נתיב לא נכון

**פתרון:**
```powershell
# וודא שאתה מריץ מ-BiblIA_dataset (root)
cd G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset
python scripts\find_empty_translations.py
```

---

### **שגיאה 4: "Messages compilation failed"**

**סיבה:** בעיה בתחביר של django.po

**פתרון:**
```powershell
# בדוק syntax errors
msgfmt --check eScriptorium_CLEAN\app\locale\he\LC_MESSAGES\django.po

# או הרץ את ה-compile עם verbose
cd eScriptorium_CLEAN
.\scripts\compile-translations.ps1 -Language he -Verbose
```

---

## 📊 טיפים למציאת תרגומים חסרים (Tips)

### **טיפ 1: ספירה מהירה**
```powershell
# כמה msgstr ריקים?
(Select-String -Path "eScriptorium_CLEAN\app\locale\he\LC_MESSAGES\django.po" -Pattern 'msgstr ""').Count
```

### **טיפ 2: ראה את ההקשר**
```powershell
# ראה 3 שורות לפני ואחרי כל msgstr ריק
Select-String -Path "eScriptorium_CLEAN\app\locale\he\LC_MESSAGES\django.po" -Pattern 'msgstr ""' -Context 3,3
```

### **טיפ 3: ייצוא לקובץ**
```powershell
# שמור את כל התרגומים החסרים לקובץ
Select-String -Path "eScriptorium_CLEAN\app\locale\he\LC_MESSAGES\django.po" -Pattern 'msgstr ""' -Context 2,0 > empty_translations.txt
```

---

## 🎯 מה צ'אטבוט הבא צריך לעשות?

### **כשמקבלים משימה: "תרגם הכל" או "השלם תרגומים"**

```markdown
✅ שלב 1: עבור לתיקייה הנכונה
cd G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset

✅ שלב 2: מצא תרגומים חסרים
python scripts\find_empty_translations.py

✅ שלב 3: אם יש תרגומים חסרים:
   - צור מיפוי תרגומים (MAPPING dict)
   - הרץ auto_fill script
   - הסר duplicates
   - קומפל
   - אתחל web
   - אמת

✅ שלב 4: אם אין תרגומים חסרים:
   - דווח למשתמש: "✅ כל התרגומים מלאים!"
```

---

## 🔗 קבצים רלוונטיים

| קובץ | מטרה | נתיב מלא |
|------|------|----------|
| **django.po** | קובץ תרגום | `eScriptorium_CLEAN\app\locale\he\LC_MESSAGES\django.po` |
| **find_empty_translations.py** | מציאת ריקים | `scripts\find_empty_translations.py` |
| **auto_fill_7_translations.py** | הוספת תרגומים | `scripts\auto_fill_7_translations.py` |
| **remove_po_duplicates.py** | הסרת duplicates | `remove_po_duplicates.py` |
| **compile-translations.ps1** | קומפילציה | `eScriptorium_CLEAN\scripts\compile-translations.ps1` |

---

## 📅 עדכון אחרון

- **תאריך:** 31 באוקטובר 2025
- **סטטוס:** ✅ כל 7 התרגומים הריקים מולאו והוקמפלו בהצלחה
- **נותרו:** 0 תרגומים ריקים ב-django.po

---

## 🎉 סיכום

**לצ'אטבוט הבא:**

1. ✅ **תמיד** השתמש בנתיבים המלאים מהמדריך
2. ✅ **תמיד** הרץ `find_empty_translations.py` לפני עבודה
3. ✅ **תמיד** הסר duplicates לפני קומפילציה
4. ✅ **תמיד** תעד את מה שעשית ב-SESSION_LOG.md

**זכור:** הקובץ הזה הוא **המדריך המלא** - אל תמציא מחדש! 🚀

---

**גרסה:** 1.0  
**תאריך יצירה:** 31 אוקטובר 2025  
**סטטוס:** 🟢 ACTIVE - מדריך רשמי לתרגומים
