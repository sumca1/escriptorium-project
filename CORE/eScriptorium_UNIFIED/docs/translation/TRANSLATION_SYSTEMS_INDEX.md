# 🌍 מדריך מרכזי - מערכות התרגום ב-eScriptorium

**תאריך:** 20 אוקטובר 2025  
**פרויקט:** BiblIA Dataset - eScriptorium Hebrew Translation

---

## 📚 רשימת המסמכים

### 🎯 קריאה מומלצת לפי נושא:

| אם אתה רוצה... | קרא את... |
|----------------|-----------|
| **להבין איך תרגום Vue.js עובד** | [VUE_TRANSLATION_SUMMARY.md](./VUE_TRANSLATION_SUMMARY.md) |
| **להשוות Vue vs Django templates** | [VUE_TRANSLATION_COMPARISON.md](./VUE_TRANSLATION_COMPARISON.md) |
| **להבין מה BiblIA הוסיף** | [SPECIAL_TRANSLATION_FILES.md](./SPECIAL_TRANSLATION_FILES.md) |
| **לראות מיפוי של כל הקבצים הצרפתיים** | [FRENCH_TRANSLATION_MAPPING.md](./FRENCH_TRANSLATION_MAPPING.md) |
| **להשוות צרפתית לעברית** | [FRENCH_VS_HEBREW_TRANSLATION.md](./FRENCH_VS_HEBREW_TRANSLATION.md) |
| **להתחיל מהבסיס** | המסמך הזה ⬇️ |

---

## 🎓 סקירה כללית

### מה זה eScriptorium?
- פלטפורמת OCR/HTR לכתבי יד היסטוריים
- פותח ב-EPHE-PSL, פריז
- Open Source (Django + Vue.js)

### מה זה BiblIA?
- פרויקט ישראלי להעתקת כתבי יד עבריים
- מבוסס על eScriptorium
- הוסיף תמיכה מלאה בעברית

---

## 🌐 שפות נתמכות

### eScriptorium המקורי:

| שפה | ממשק (UI) | נתוני DB | Vue.js | סטטוס |
|-----|----------|---------|--------|-------|
| 🇬🇧 English | ✅ | ✅ | ✅ | ברירת מחדל |
| 🇫🇷 French | ✅ | ⚠️ | ❌ | חלקי |
| 🇩🇪 German | ✅ | ❌ | ❌ | חלקי |
| 🇳🇴 Norwegian | ✅ | ❌ | ❌ | חלקי |

**הסבר:**
- ✅ ממשק (UI): תרגום דרך django.po
- ⚠️ נתוני DB: name_fr קיים אבל לא מוצג
- ❌ Vue.js: טקסט hard-coded באנגלית

---

### BiblIA:

| שפה | ממשק (UI) | נתוני DB | Vue.js | סטטוס |
|-----|----------|---------|--------|-------|
| 🇬🇧 English | ✅ | ✅ | ✅ | ברירת מחדל |
| 🇫🇷 French | ✅ | ✅ | ❌ | **עובד!*** |
| 🇮🇱 Hebrew | ✅ | ✅ | ✅ | מלא |

***תובנה:** BiblIA תיקן את name_fr, אז צרפתית עובדת טוב יותר!

---

## 📂 ארכיטקטורת התרגום

### שכבה 1: ממשק משתמש (Django Templates)

```
Django Templates
    ↓
{% trans "Text" %}
    ↓
django.po (fr/he/de/nb)
    ↓
תרגום מוצג
```

**קבצים:**
- `app/locale/fr/LC_MESSAGES/django.po` (צרפתית)
- `app/locale/he/LC_MESSAGES/django.po` (עברית)
- `app/locale/de/LC_MESSAGES/django.po` (גרמנית)

**סטטוס:** ✅ עובד מצוין בכל השפות

---

### שכבה 2: נתוני מסד נתונים (Scripts, Typologies)

```
Database Models
    ↓
Script.name / Script.name_fr / Script.name_he
    ↓
get_localized_name() ← BiblIA הוסיף!
    ↓
תרגום דינמי
```

**קבצים:**
- `app/apps/core/models.py` (הגדרות)
- `app/apps/core/script_translations_he.py` (תרגומים עבריים)
- `app/apps/core/migrations/0019_load_scripts.py` (תרגומים צרפתיים)

**סטטוס:**
- eScriptorium: ⚠️ name_fr קיים אבל לא עובד
- BiblIA: ✅ name_fr + name_he עובדים

---

### שכבה 3: Vue.js Components

```
Vue Components
    ↓
$t('key')
    ↓
window.EDITOR_TRANSLATIONS ← BiblIA הוסיף!
    ↓
תרגום מוצג
```

**קבצים:**
- `app/escriptorium/templates/core/document_part_edit.html`
- `front/vue/components/*.vue`

**סטטוס:**
- eScriptorium: ❌ אין תרגום
- BiblIA: ✅ 20 מפתחות תרגום לעברית

---

## 🔄 תהליך התרגום

### 1. הוספת תרגום לממשק (UI)

```bash
# 1. חלץ מחרוזות חדשות
cd app
python manage.py makemessages -l he

# 2. ערוך את django.po
nano locale/he/LC_MESSAGES/django.po

# 3. קמפל
python manage.py compilemessages -l he

# 4. רענן דפדפן
# התרגום אמור להופיע!
```

---

### 2. הוספת תרגום ל-Scripts (BiblIA)

```python
# 1. ערוך script_translations_he.py
SCRIPT_TRANSLATIONS_HE = {
    'Neww': 'כתב חדש',  # הוסף שורה
}

# 2. צור migration
python manage.py makemigrations --empty core --name add_new_script_translation

# 3. ערוך את ה-migration
from ..script_translations_he import SCRIPT_TRANSLATIONS_HE

def add_translation(apps, schema_editor):
    Script = apps.get_model("core", "Script")
    script = Script.objects.get(iso_code='Neww')
    script.name_he = SCRIPT_TRANSLATIONS_HE['Neww']
    script.save()

# 4. הרץ
python manage.py migrate
```

---

### 3. הוספת תרגום ל-Vue.js (BiblIA)

```javascript
// 1. ערוך document_part_edit.html
window.EDITOR_TRANSLATIONS = {
    'existing_key': 'תרגום קיים',
    'new_key': 'תרגום חדש',  // הוסף
};

// 2. ב-Vue component:
<template>
  <p>{{ $t('new_key') }}</p>
</template>

// 3. npm run build
// 4. רענן דפדפן
```

---

## 🎯 התרומה של BiblIA

### מה היה ב-eScriptorium:
1. ✅ django.po לצרפתית, גרמנית, נורווגית
2. ⚠️ name_fr ב-DB אבל לא מוצג
3. ❌ אין תרגום ל-Vue.js
4. ❌ אין name_fr ל-Typologies

### מה BiblIA הוסיף:
1. ✅ django.po לעברית
2. ✅ **get_localized_name()** - עכשיו name_fr עובד!
3. ✅ name_he ל-Scripts
4. ✅ name_he ל-Typologies (חדש לגמרי!)
5. ✅ window.EDITOR_TRANSLATIONS ל-Vue.js
6. ✅ $t() method ב-Vue components

### התוצאה:
- 🇮🇱 עברית: תרגום מלא 100%
- 🇫🇷 צרפתית: השתפר מ-70% ל-95% (בזכות get_localized_name)
- 🇩🇪 גרמנית: נשאר 70% (רק UI)

---

## 📊 השוואת גישות

### eScriptorium - גישה "embedded":

```python
# הכל בתוך המיגרציה
scripts_data = [
    {'name': 'Arabic', 'name_fr': 'arabe'},
    {'name': 'Armenian', 'name_fr': 'arménien'},
    # ... 208 שורות
]
```

**יתרונות:**
- הכל במקום אחד
- פשוט לטעינה ראשונית

**חסרונות:**
- קשה לתחזק
- קשה לעדכן
- לא ניתן לשימוש חוזר

---

### BiblIA - גישה "modular":

```python
# קובץ נפרד
# script_translations_he.py
SCRIPT_TRANSLATIONS_HE = {
    'Arab': 'ערבי',
    'Armn': 'ארמני',
}

# במיגרציה - import בלבד
from ..script_translations_he import SCRIPT_TRANSLATIONS_HE
```

**יתרונות:**
- ✅ קל לתחזק
- ✅ ניתן לשימוש חוזר
- ✅ ניתן לבדיקות unit tests
- ✅ קריא יותר

**חסרונות:**
- צריך שני קבצים (translations + migration)

---

## 🔍 דוגמאות מעשיות

### דוגמה 1: Script מוצג לפי שפה

```python
>>> from core.models import Script
>>> from django.utils import translation

>>> script = Script.objects.get(iso_code='Arab')

# אנגלית
>>> translation.activate('en')
>>> str(script)
'Arabic'

# צרפתית (עובד בזכות BiblIA!)
>>> translation.activate('fr')
>>> str(script)
'arabe'

# עברית
>>> translation.activate('he')
>>> str(script)
'ערבי'
```

---

### דוגמה 2: Typology (רק ב-BiblIA)

```python
>>> from core.models import BlockType
>>> from django.utils import translation

>>> block = BlockType.objects.get(name='Title')

# עברית
>>> translation.activate('he')
>>> str(block)
'כותרת'

# אנגלית
>>> translation.activate('en')
>>> str(block)
'Title'

# צרפתית - לא קיים!
>>> translation.activate('fr')
>>> str(block)
'Title'  # נשאר באנגלית
```

---

### דוגמה 3: Vue.js (רק ב-BiblIA)

```vue
<!-- Document Part Editor -->
<template>
  <button>{{ $t('save_transcription') }}</button>
</template>

<!-- עברית: "שמור תמלול" -->
<!-- אנגלית: "Save Transcription" -->
```

---

## 📈 סטטיסטיקות

### eScriptorium:
- שפות: 4 (en, fr, de, nb)
- קבצי תרגום: ~6
- תרגומי UI: ~300-500 מחרוזות
- תרגומי DB: 208 Scripts (name_fr) - לא פעיל
- תרגומי Vue: 0

### BiblIA:
- שפות: 5 (en, fr, de, nb, he) - **צרפתית משופרת!**
- קבצי תרגום: ~10
- תרגומי UI: ~300-500 מחרוזות
- תרגומי DB: 208 Scripts + 12 Typologies - **פעיל!**
- תרגומי Vue: 20 מפתחות

---

## 🚀 מה הלאה?

### תרגום מלא לצרפתית ב-BiblIA:
- [ ] typology_translations_fr.py
- [ ] Vue translations צרפתיים
- [ ] migration חדש

### תרגום לגרמנית:
- [ ] script_translations_de.py
- [ ] typology_translations_de.py
- [ ] Vue translations גרמניים
- [ ] 2 migrations

### תרגום לערבית:
- [ ] django.po
- [ ] script_translations_ar.py
- [ ] typology_translations_ar.py
- [ ] Vue translations ערביים
- [ ] 2 migrations

---

## 📚 קישורים למסמכים

1. [VUE_TRANSLATION_SUMMARY.md](./VUE_TRANSLATION_SUMMARY.md) - מדריך מלא לתרגום Vue.js
2. [VUE_TRANSLATION_COMPARISON.md](./VUE_TRANSLATION_COMPARISON.md) - השוואת גישות
3. [SPECIAL_TRANSLATION_FILES.md](./SPECIAL_TRANSLATION_FILES.md) - קבצי BiblIA הייחודיים
4. [FRENCH_TRANSLATION_MAPPING.md](./FRENCH_TRANSLATION_MAPPING.md) - 26 הקבצים הצרפתיים
5. [FRENCH_VS_HEBREW_TRANSLATION.md](./FRENCH_VS_HEBREW_TRANSLATION.md) - השוואה מפורטת

---

**תאריך יצירה:** 20 אוקטובר 2025  
**מחבר:** BiblIA Dataset Project  
**רישיון:** Documentation עבור פרויקט Open Source
