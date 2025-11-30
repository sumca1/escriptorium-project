# 📚 קבצי תרגום מיוחדים - BiblIA Project

**תאריך:** 20 אוקטובר 2025  
**פרויקט:** BiblIA Dataset - eScriptorium Hebrew Translation

---

## 🎯 סקירה כללית

פרויקט BiblIA **השלים והרחיב** את מערכת התרגומים של eScriptorium המקורי:

### ✅ eScriptorium המקורי כלל:
- **Django i18n** - תרגומים סטנדרטיים דרך `django.po` (כולל צרפתית, גרמנית)
- **שדה `name_fr`** - במודל Script (208 כתבים) עם תרגומים צרפתיים
- ⚠️ **אבל:** לא הטמיע הצגה דינמית של `name_fr` בממשק!

### ✨ BiblIA הוסיף:
- **שדה `name_he`** - הוספה למודל Script
- **מתודה `get_localized_name()`** - מחזירה שם לפי שפת המשתמש
- **תרגומים ל-Typologies** - BlockType ו-LineType (לא היה ב-eScriptorium)
- **קבצי Python נפרדים** - לתחזוקה נוחה של תרגומים

---

## 📂 קבצי התרגום המיוחדים

### 1️⃣ **script_translations_he.py**

**מיקום:** `app/apps/core/script_translations_he.py`  
**גודל:** 7,674 bytes  
**תרגומים:** 208 שמות כתבים (Unicode scripts)

#### תוכן:
```python
SCRIPT_TRANSLATIONS_HE = {
    'Adlm': 'אדלם',
    'Afak': 'אפאקה',
    'Aghb': 'אלבני קווקזי',
    'Ahom': 'אהום, טאי אהום',
    'Arab': 'ערבי',
    'Aran': 'ערבי (וריאנט נסתעליק)',
    'Armi': 'ארמית אימפריאלית',
    'Armn': 'ארמני',
    # ... 200+ תרגומים נוספים
    'Hebr': 'עברי',
    'Latn': 'לטיני',
    'Grek': 'יווני',
    # ...
}
```

#### שימוש:
- תרגום שמות סקריפטים בממשק המשתמש
- מופיע ב-dropdowns של בחירת כתב
- נטען דרך migration 0076

---

### 2️⃣ **typology_translations_he.py**

**מיקום:** `app/apps/core/typology_translations_he.py`  
**גודל:** 558 bytes  
**תרגומים:** סוגי בלוקים ושורות

#### תוכן:
```python
TYPOLOGY_TRANSLATIONS_HE = {
    # Block types
    "Title": "כותרת",
    "Main": "עיקרי",
    "Commentary": "פירוש",
    "Illustration": "איור",
    "Decoration": "קישוט",
    "Cover": "כריכה",
    "Page": "עמוד",
    
    # Line types
    "Correction": "תיקון",
    "Numbering": "מספור",
    "Signature": "חתימה",
    "Default": "ברירת מחדל",
}
```

#### שימוש:
- תרגום סוגי בלוקים טקסט (BlockType)
- תרגום סוגי שורות (LineType)
- נטען דרך migration 0077

---

## 🔧 Migrations קשורות

### 1️⃣ **0076_add_hebrew_script_translations.py**

**מטרה:** הכנסת תרגומים עבריים לטבלת Scripts

```python
def add_hebrew_translations(apps, schema_editor):
    """Add Hebrew translations to all scripts"""
    Script = apps.get_model("core", "Script")
    
    translations = {
        'Adlm': 'אדלם',
        'Arab': 'ערבי',
        'Hebr': 'עברי',
        # ...
    }
    
    for code, name_he in translations.items():
        try:
            script = Script.objects.get(code=code)
            script.name_he = name_he
            script.save()
        except Script.DoesNotExist:
            pass
```

---

### 2️⃣ **0077_add_typology_name_he.py**

**מטרה:** הכנסת תרגומים עבריים לטבלת Typologies

```python
def add_hebrew_typology_names(apps, schema_editor):
    """Add Hebrew translations to typologies"""
    BlockType = apps.get_model("core", "BlockType")
    LineType = apps.get_model("core", "LineType")
    
    block_translations = {
        "Title": "כותרת",
        "Main": "עיקרי",
        # ...
    }
    
    for name_en, name_he in block_translations.items():
        BlockType.objects.filter(name=name_en).update(name_he=name_he)
```

---

## 🆚 השוואה: BiblIA vs eScriptorium המקורי

| היבט | eScriptorium המקורי | BiblIA |
|------|---------------------|---------|
| **תרגום UI סטטי** | django.po/mo (gettext) | ✅ django.po/mo |
| **תרגום Scripts** | ❌ רק אנגלית | ✅ script_translations_he.py |
| **תרגום Typologies** | ❌ רק אנגלית | ✅ typology_translations_he.py |
| **שדה name_he ב-DB** | ❌ לא קיים | ✅ נוסף למודלים |
| **Migrations מיוחדות** | ❌ לא | ✅ 0076, 0077 |
| **שפות אחרות** | fr, de, nb (UI בלבד) | he (UI + DB content) |

---

## 🌍 השוואת שפות

### במאגר המקורי (eScriptorium):

#### תרגומי UI (gettext):
```
locale/
├── de/LC_MESSAGES/django.po  (גרמנית - UI בלבד)
├── fr/LC_MESSAGES/django.po  (צרפתית - UI בלבד)  
├── nb/LC_MESSAGES/django.po  (נורווגית - UI בלבד)
└── en/LC_MESSAGES/django.pot (אנגלית - template)
```

#### תרגומי Scripts (בתוך קוד):
```
app/apps/core/migrations/0019_load_scripts.py:
    {'iso_code': 'Arab', 'name': 'Arabic', 'name_fr': 'arabe'}
    {'iso_code': 'Armn', 'name': 'Armenian', 'name_fr': 'arménien'}
    {'iso_code': 'Hebr', 'name': 'Hebrew', 'name_fr': 'hébreu'}
    # ... 208 scripts עם name_fr

front/src/stories/util/scripts.js:
    {name: "Arabic", name_fr: "arabe", iso_code: "Arab"}
    {name: "Armenian", name_fr: "arménien", iso_code: "Armn"}
    # ... תרגומים צרפתיים ב-JavaScript
```

#### ⚠️ אבל:
- ✅ השדה `name_fr` **קיים** ב-DB
- ✅ ה-migrations **ממלאים** את `name_fr`
- ✅ ה-JavaScript fixtures **מכילים** `name_fr`
- ❌ **אבל אין מנגנון הצגה!** Templates משתמשים רק ב-`script.name` (אנגלית)
- ❌ המודל Script **לא** היה לו `get_localized_name()` method
- ❌ הפונקציה `__str__()` מחזירה רק `self.name`

**אין:**
- ❌ script_translations_fr.py (קובץ נפרד)
- ❌ script_translations_de.py
- ❌ script_translations_nb.py  
- ❌ typology_translations_*.py (בכלל)

### ב-BiblIA:

#### תרגומי UI:
```
locale/
└── he/LC_MESSAGES/django.po  (עברית - UI)
```

#### תרגומי Scripts + Typologies:
```
apps/core/
├── script_translations_he.py      (208 כתבים - קובץ נפרד!)
├── typology_translations_he.py    (12 טיפולוגיות - חדש!)
└── migrations/
    ├── 0076_add_hebrew_script_translations.py  (טוען מ-script_translations_he)
    └── 0077_add_typology_name_he.py           (טוען מ-typology_translations_he)

models.py:
    class Script:
        name_he = models.CharField(...)  # שדה חדש!
        
        def get_localized_name(self, language=None):  # מתודה חדשה!
            if language.startswith('he') and self.name_he:
                return self.name_he
            elif language.startswith('fr') and self.name_fr:
                return self.name_fr
            return self.name
        
        def __str__(self):
            return self.get_localized_name()  # שינוי!
```

---

## 🔄 ההבדלים המרכזיים

| **אספקט** | **eScriptorium המקורי** | **BiblIA** |
|-----------|------------------------|-----------|
| **שדה name_fr** | ✅ קיים ב-DB | ✅ קיים ב-DB |
| **שדה name_he** | ❌ לא קיים | ✅ נוסף |
| **name_fr במיגרציה** | ✅ embedded בקוד המיגרציה | ✅ embedded בקוד המיגרציה |
| **name_he במיגרציה** | ❌ - | ✅ קובץ Python נפרד |
| **name_fr ב-JS** | ✅ front/src/stories/util/scripts.js | ✅ (ירש מ-eScriptorium) |
| **get_localized_name()** | ❌ לא קיים! | ✅ **נוסף ע"י BiblIA!** |
| **__str__() dynamic** | ❌ מחזיר `self.name` בלבד | ✅ מחזיר לפי שפה |
| **Templates** | מציגים `script.name` (EN בלבד) | מציגים `script` (מופיע לפי שפה) |
| **Typologies** | ❌ אין name_fr בכלל | ✅ BiblIA הוסיף name_he |

---

## 💡 למה BiblIA עשה את זה אחרת?

### 🔴 הבעיה ב-eScriptorium המקורי:

#### 1. name_fr קיים אבל לא פעיל:
```python
# app/apps/core/models.py (eScriptorium original)
class Script(models.Model):
    name = models.CharField(max_length=128)      # "Arabic"
    name_fr = models.CharField(max_length=128, blank=True)  # "arabe"
    # ...
    
    def __str__(self):
        return self.name  # ❌ תמיד מחזיר אנגלית!
```

#### 2. Templates לא משתמשים ב-name_fr:
```django
{# templates - eScriptorium original #}
<p>Script: {{ model.script.name }}</p>  
{# ❌ תמיד מציג "Arabic" גם למשתמש צרפתי #}
```

#### 3. API לא מחזיר name_fr:
```python
# serializers.py - eScriptorium original
class DocumentSerializer(serializers.ModelSerializer):
    script = serializers.ReadOnlyField(source='script.name')
    # ❌ תמיד "Arabic", לא "arabe"
```

### ✅ הפתרון של BiblIA:

#### 1. הוספת get_localized_name() method:
```python
# app/apps/core/models.py (BiblIA)
class Script(models.Model):
    name = models.CharField(max_length=128)
    name_fr = models.CharField(max_length=128, blank=True)
    name_he = models.CharField(max_length=128, blank=True)  # ← NEW!
    
    def get_localized_name(self, language=None):  # ← NEW!
        from django.utils import translation
        
        if language is None:
            language = translation.get_language()
        
        if language and language.startswith('he') and self.name_he:
            return self.name_he  # "עברי"
        elif language and language.startswith('fr') and self.name_fr:
            return self.name_fr  # "arabe"  
        return self.name  # "Arabic"
    
    def __str__(self):
        return self.get_localized_name()  # ✅ דינמי לפי שפה!
```

#### 2. עכשיו Templates עובדים אוטומטית:
```django
{# templates - BiblIA #}
<p>Script: {{ model.script }}</p>
{# ✅ "עברי" למשתמש עברי, "arabe" לצרפתי, "Arabic" לשאר #}
```

#### 3. קבצי Python נפרדים לתחזוקה:
```python
# app/apps/core/script_translations_he.py
SCRIPT_TRANSLATIONS_HE = {
    'Arab': 'ערבי',
    'Hebr': 'עברי',
    'Latn': 'לטיני',
    # ... 208 total
}

# app/apps/core/migrations/0076_add_hebrew_script_translations.py
from ..script_translations_he import SCRIPT_TRANSLATIONS_HE

def add_hebrew_translations(apps, schema_editor):
    Script = apps.get_model("core", "Script")
    for iso_code, name_he in SCRIPT_TRANSLATIONS_HE.items():
        script = Script.objects.filter(iso_code=iso_code).first()
        if script:
            script.name_he = name_he
            script.save(update_fields=['name_he'])
```

---

## 🎯 למה לא עשו זאת ב-eScriptorium?

**אפשרויות:**

1. **שכחו להשלים** - הוסיפו `name_fr` אבל לא הטמיעו הצגה
2. **לא היה צורך** - רוב המשתמשים דוברי אנגלית
3. **לא ידעו על הבעיה** - אף אחד לא השתמש בצרפתית ממש
4. **הותירו לעתיד** - תכננו אבל לא הספיקו

**BiblIA** מצא את הבעיה ופתר אותה כשניסה להוסיף עברית!

---

## 📊 סטטיסטיקה

| קובץ | שורות | תרגומים | גודל |
|------|-------|---------|------|
| script_translations_he.py | 208 | 208 כתבים | 7.6 KB |
| typology_translations_he.py | 23 | 12 טיפולוגיות | 558 B |
| 0076_add_hebrew_script_translations.py | 237 | - | - |
| 0077_add_typology_name_he.py | ~150 | - | - |
| **סה"כ** | ~618 | **220 תרגומים** | **~8.2 KB** |

---

## 🔍 איך למצוא שימוש בקבצים

### חיפוש ב-migration:
```bash
grep -r "script_translations_he" app/apps/core/migrations/
```

### חיפוש ב-views:
```bash
grep -r "name_he" app/apps/core/
```

### חיפוש ב-models:
```bash
grep -r "class Script" app/apps/core/models.py
```

---

## 🎓 לקחים

1. **gettext מתאים ל-UI בלבד**, לא לתוכן מבסיס נתונים
2. **eScriptorium הכין תשתית (name_fr)** אבל לא הטמיע הצגה דינמית
3. **BiblIA השלים את העבודה**:
   - הוסיף `get_localized_name()` שעובד גם ל-French
   - יצר `name_he` field חדש
   - הוסיף תרגומים ל-Typologies (שלא היו בכלל)
4. **קבצים נפרדים (script_translations_he.py)** נוחים יותר לתחזוקה מ-embedded dictionaries
5. **הפתרון של BiblIA עובד ל-3 שפות**: English, French (name_fr קיים), Hebrew (name_he חדש)

---

## 🔍 קבצים עם תרגומים צרפתיים ב-eScriptorium

### קבצי נתונים:
- `app/apps/core/migrations/0019_load_scripts.py` - 208 scripts עם name_fr
- `front/src/stories/util/scripts.js` - אותם 208 scripts (JavaScript fixtures)

### קבצי אנשים:
- `app/contributors_example/contributors_list.html` - שמות עם é, è (Clérice, Chagué וכו')
- `app/escriptorium/templates/core/credits.html` - אותו תוכן

### קבצי UI:
- `app/locale/fr/LC_MESSAGES/django.po` - תרגומי ממשק לצרפתית

**שים לב:** רק django.po עובד בפועל. name_fr קיים ב-DB אבל לא מוצג!

---

## 🔮 עתיד - הרחבה לשפות נוספות

### אופציה 1: המשך גישת BiblIA (קבצים נפרדים)

**לצרפתית (יש כבר name_fr!):**
```python
# צריך רק להפעיל את name_fr הקיים!
# אין צורך ב-migration חדש, הנתונים כבר ב-DB
# רק להוסיף תמיכה ב-get_localized_name() (כבר קיים!)
```

**לגרמנית (חדש):**
```
app/apps/core/script_translations_de.py
app/apps/core/typology_translations_de.py  
app/apps/core/migrations/0078_add_german_translations.py
```

**לערבית (חדש):**
```
app/apps/core/script_translations_ar.py
app/apps/core/typology_translations_ar.py
app/apps/core/migrations/0079_add_arabic_translations.py
```

### אופציה 2: פתרון Generic (JSONField)

```python
class Script(models.Model):
    name = models.CharField(max_length=128)  # English (default)
    translations = models.JSONField(default=dict, blank=True)
    # {"fr": "arabe", "he": "ערבי", "de": "Arabisch", "ar": "عربي"}
    
    def get_localized_name(self, language=None):
        if not language:
            language = translation.get_language()
        
        lang_code = language.split('-')[0]  # 'he-IL' -> 'he'
        return self.translations.get(lang_code, self.name)
```

**יתרונות:**
- ✅ אין צורך ב-migrations חדשות לכל שפה
- ✅ תמיכה ב-N שפות בלי שדות נוספים
- ✅ קל יותר לנהל

**חסרונות:**
- ❌ צריך migration גדול להעברת name_fr ו-name_he ל-JSON
- ❌ יותר מורכב לשאילתות (`translations__fr`)
- ❌ אין type safety

---

## 📚 קישורים וקבצים

### BiblIA - קבצי תרגום:
- [script_translations_he.py](./app/apps/core/script_translations_he.py) - 208 תרגומי כתבים
- [typology_translations_he.py](./app/apps/core/typology_translations_he.py) - 12 תרגומי טיפולוגיות
- [Migration 0076](./app/apps/core/migrations/0076_add_hebrew_script_translations.py) - טוען תרגומי Scripts
- [Migration 0077](./app/apps/core/migrations/0077_add_typology_name_he.py) - טוען תרגומי Typologies
- [models.py - Script class](./app/apps/core/models.py) - הגדרת המודל עם get_localized_name()

### eScriptorium המקורי - קבצים עם name_fr:
- `app/apps/core/migrations/0019_load_scripts.py` - 208 scripts עם name_fr embedded
- `app/apps/core/migrations/0018_auto_20190502_0936.py` - יצירת שדה name_fr
- `front/src/stories/util/scripts.js` - JavaScript fixtures עם name_fr
- `app/locale/fr/LC_MESSAGES/django.po` - תרגומי UI (לא scripts!)

### מסמכי תיעוד נוספים:
- [VUE_TRANSLATION_SUMMARY.md](./VUE_TRANSLATION_SUMMARY.md) - תרגום Vue.js components
- [VUE_TRANSLATION_COMPARISON.md](./VUE_TRANSLATION_COMPARISON.md) - השוואת גישות תרגום
- [VUE_TRANSLATION_INDEX.md](./VUE_TRANSLATION_INDEX.md) - מדריך מרכזי

---

## 🔬 ממצאי המחקר - סיכום

### מה מצאנו:

1. **eScriptorium התכוון לתמוך בצרפתית:**
   - יצר שדה `name_fr` ב-2019
   - מילא 208 scripts עם תרגומים צרפתיים
   - הכניס גם ל-JavaScript fixtures

2. **אבל לא הטמיע את זה:**
   - אין `get_localized_name()` method
   - `__str__()` מחזיר רק English
   - Templates קוראים ל-`script.name` (לא name_fr)
   - API מחזיר `source='script.name'`

3. **BiblIA גילה את הבעיה:**
   - כשניסה להוסיף עברית, ראה ש-name_fr לא עובד
   - הוסיף `get_localized_name()` שפותר גם ל-French!
   - יצר name_he field חדש
   - הוסיף תמיכה ב-Typologies (לא היה בכלל)

4. **התוצאה:**
   - BiblIA עכשיו תומך ב-**3 שפות** לתוכן DB: EN, FR, HE
   - eScriptorium המקורי בפועל תומך רק ב-**1 שפה**: EN
   - French locale (django.po) עובד רק ל-UI, לא לתוכן

---

**הערה חשובה:** אם תרצו להפעיל French ב-BiblIA, זה **כבר עובד!**  
הנתונים (name_fr) קיימים, והקוד (get_localized_name) תומך בהם.  
פשוט צריך להפעיל את השפה הצרפתית בהגדרות!

---

**תאריך יצירה:** 20 אוקטובר 2025  
**תאריך עדכון אחרון:** 20 אוקטובר 2025  
**מחבר:** BiblIA Dataset Project
