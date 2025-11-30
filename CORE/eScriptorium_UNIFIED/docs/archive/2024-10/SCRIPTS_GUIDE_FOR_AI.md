# 🤖 מדריך סקריפטים לצ'אטבוטים AI

## 📋 תקציר מהיר

הפרויקט כולל סקריפטים חכמים שעוזרים לזהות ולתרגם מחרוזות. **אבל הם לא מושלמים!**

---

## 🎯 הכלל החשוב ביותר

> **הסקריפטים באו להקל עליך, לא להחליף את השיפוט שלך!**
>
> אם אתה רואה שגיאה, סתירה, או משהו שנראה לא נכון:
> 
> ✅ **תקן את הסקריפט**  
> ✅ **עדכן את SESSION_LOG.md**  
> ✅ **סמוך על עצמך**

---

## 📚 הסקריפטים הזמינים

### 1️⃣ `extract_missing_translations.py`
**מה הוא עושה:**
- סורק את כל קבצי Vue
- מחלץ מחרוזות שחסרות תרגום
- **מסווג אוטומטית ל-Frontend או Backend**
- מזהה hardcoded strings

**תוצאות:**
- `FRONTEND_strings_to_translate.txt` - להוסיף ל-`he.json`
- `BACKEND_strings_to_translate.txt` - להוסיף ל-`django.po`
- `hardcoded_strings_to_fix.txt` - צריך להמיר ל-`$t()`

**אם הסיווג שגוי:**
```python
# תתקן את הפונקציה classify_string_layer()
# הוסף patterns ל:
frontend_patterns = [...]  # בשורה ~40
backend_patterns = [...]   # בשורה ~60
```

---

### 2️⃣ `check_translation_status.py`
**מה הוא עושה:**
- בודק קבצי Vue אם יש hardcoded strings
- מזהה מחרוזות שלא תורגמו
- מסנן generic components (false positives)

**תוצאות:**
- דוח מפורט עם בעיות קריטיות ואזהרות
- `translation_check_report.txt`
- `fix_remaining_strings.py` (אם יש בעיות)

**אם יש false positives:**
```python
# בראש הקובץ, תוסיף ל:
EXCLUDE_PATTERNS = [...]   # שורה ~50
# או שפר:
def is_generic_component()  # שורה ~70
```

---

## 🔧 איך לתקן סקריפט?

### דוגמה: הסקריפט סיווג "Loading..." כ-Backend, אבל זה Frontend

**1. פתח את `extract_missing_translations.py`**

**2. מצא את `classify_string_layer()`** (בערך שורה 15)

**3. הוסף pattern:**
```python
frontend_patterns = [
    'cer.',
    'SegmOnto',
    'Select ',
    'Loading',      # ← הוסף כאן
    'tag',
    ...
]
```

**4. הרץ מחדש:**
```bash
python extract_missing_translations.py
```

**5. עדכן `SESSION_LOG.md`:**
```markdown
### Session - 26/10/2025 17:30 - Chatbot GPT-4

**תיקון סקריפט:**
- ✅ הוספתי "Loading" ל-frontend_patterns
- ✅ עכשיו כל Loading... מסווג נכון ל-Frontend
```

---

## ⚠️ מתי לסמוך על הסקריפט? מתי לא?

### ✅ סמוך על הסקריפט:
- זיהוי `$t()` - מאוד מדויק
- זיהוי hardcoded strings - טוב
- ספירת מחרוזות - מדויק

### ⚠️ בדוק ידנית:
- סיווג Frontend/Backend - **יכול לטעות!**
- זיהוי generic components - **false positives אפשריים**
- מחרוזות עם משתנים - **צריך הקשר**

---

## 🎓 דוגמאות מהחיים

### דוגמה 1: "No matching tags. ${...}"
**הסקריפט אומר:** Hardcoded string  
**נכון?** ✅ כן! צריך להמיר ל-`this.$t('No matching tags...', {total: ...})`

### דוגמה 2: "Failed to run SegmOnto check"
**הסקריפט אומר:** Backend  
**נכון?** ✅ כן! זה server error message

### דוגמה 3: "cer.accuracy"
**הסקריפט אומר:** Frontend  
**נכון?** ✅ כן! זה CER UI component

### דוגמה 4: "alert-${...}"
**הסקריפט אומר:** Hardcoded  
**נכון?** ❌ לא! זה CSS class, לא טקסט למשתמש

**מה לעשות?** תקן את `code_patterns` בסקריפט:
```python
code_patterns = [
    'alert-',   # ← כבר קיים
    'bg-',
    ...
]
```

---

## 📊 תרשים החלטה מהיר

```
האם הסקריפט זיהה מחרוזת?
│
├─ YES → האם הסיווג נכון?
│         ├─ YES → ✅ השתמש בו
│         └─ NO → ⚠️ תקן את classify_string_layer()
│
└─ NO → האם צריך לזהות?
          ├─ YES → ⚠️ תקן את PATTERNS
          └─ NO → ✅ הכל בסדר
```

---

## 🚀 Best Practices

### DO ✅
- **הרץ את הסקריפטים** לפני שאתה מתרגם
- **בדוק את התוצאות** - אל תסמוך עיוור
- **עדכן SESSION_LOG.md** אחרי תיקונים
- **שפר את הסקריפטים** אם מצאת שגיאה
- **הוסף הערות** לקוד שתיקנת

### DON'T ❌
- **אל תסמוך עיוור** על הסיווג Frontend/Backend
- **אל תתעלם מ-false positives** - תקן את הסקריפט
- **אל תשכח לעדכן** SESSION_LOG.md
- **אל תשאיר** סקריפטים שבורים לצ'אטבוט הבא

---

## 💡 טיפים

### טיפ 1: בדוק תמיד ב-grep
```bash
# בדוק איפה המחרוזת בשימוש:
grep -r "No matching tags" front/vue/
```

### טיפ 2: השתמש ב-TRANSLATION_LAYER_MAP.md
```markdown
# קובץ מפורט עם כל החלוקה Frontend/Backend
```

### טיפ 3: הרץ check_translation_status תכוף
```bash
python check_translation_status.py
# בודק שלא פספסת משהו
```

---

## 🤝 תרומה לפרויקט

כל פעם שאתה מתקן סקריפט:

1. **תעדכן את `SESSION_LOG.md`** עם מה ששינית
2. **תוסיף הערה** בקוד למה שינית
3. **תריץ מחדש** לוודא שהתיקון עובד
4. **תעדכן את `CURRENT_STATE.md`** אם רלוונטי

זה עוזר לצ'אטבוט הבא להבין מה עשית ולמה!

---

## 📞 שאלות נפוצות

### ש: הסקריפט אומר שיש 88 שורות חסרות, אבל בתרגום יש רק 74?
**ת:** חלק מהשורות הן Backend (django.po), לא Frontend (he.json). בדוק את `BACKEND_strings_to_translate.txt`.

### ש: הסקריפט מזהה CSS classes כ-hardcoded strings
**ת:** הוסף את הדפוס ל-`code_patterns` בסקריפט.

### ש: איך אני יודע אם סיווג Frontend/Backend נכון?
**ת:** 
- Frontend = UI components, buttons, labels, CER, SegmOnto
- Backend = Server errors, database messages, Django validation

### ש: מה אם אני לא בטוח?
**ת:** חפש את המחרוזת בקוד:
```bash
grep -r "Your string" front/vue/    # Frontend
grep -r "Your string" app/escriptorium/  # Backend
```

---

## 🎁 לסיום

הסקריפטים האלה נכתבו על ידי AI (כמוך!) והם משתפרים כל הזמן.

**זכור:**
- הם כלי עזר, לא אורקל אלוהי 😊
- אם משהו נראה לא נכון - **סמוך על עצמך**
- תקן, שפר, תרום - הפרויקט שלך גם!

---

**Good luck! 🚀**

*Last updated: 26 October 2025*  
*Maintained by: AI Chatbots Community 🤖*
