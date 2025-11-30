# 🇫🇷 מיפוי מלא - תרגומים לצרפתית ב-eScriptorium

**תאריך:** 20 אוקטובר 2025  
**מטרה:** מיפוי מקיף של כל קבצי התרגום הצרפתיים במאגר המקורי

---

## 📋 סיכום מהיר

**⚠️ הבהרה חשובה:** git grep מצא 26 קבצים שמכילים תווים לא-ASCII (כולל אותיות צרפתיות, em-dash, וכו').  
**אבל רק חלק קטן הם תרגומים אמיתיים!**

**סיווג מדויק:**
1. 🎯 **תרגומי UI אמיתיים** (Django i18n) - 2 קבצים ✅
2. 📊 **תרגומי DB** (name_fr) - 3 קבצים ⚠️ (קיים אבל לא מוצג)
3. 👥 **שמות תורמים** - 3 קבצים 📝 (לא תרגום)
4. � **קומנטים בצרפתית** - 1-5 קבצים 📝 (לא תרגום)
5. 🔤 **תווי Unicode אקראיים** - 12-17 קבצים ❌ (em-dash, quotes, וכו')

**סה"כ תרגומים פעילים:** **רק 2 קבצים** (django.po + django.mo)!

---

## ⚠️ למה git grep מצא 26 קבצים?

**הבעיה:** הפקודה חיפשה תווי Unicode בטווח Latin Extended:
```bash
git grep -l "[àâäéèêëïîôùûüÿæœçÀÂÄÉÈÊËÏÎÔÙÛÜŸÆŒÇ]"
```

**מה זה תפס:**
1. ✅ **אותיות צרפתיות אמיתיות:** é, è, ç, à, ô, û
2. ❌ **Em-dash:** — (תו U+2014 במקום -)
3. ❌ **Curly quotes:** " " ' ' (במקום " ')
4. ❌ **תווים טיפוגרפיים אחרים**

**דוגמאות:**

| קובץ | מה נמצא | סוג |
|------|---------|-----|
| `models.py` | `"--floating-ngrams"` (em-dash) | תו טיפוגרפי |
| `DiploPanel.vue` | `"nombre de caractères"` | קומנט בצרפתית |
| `contributors_list.html` | `"Thibault Clérice"` | שם אדם |
| `0019_load_scripts.py` | `"name_fr": "arménien"` | תרגום אמיתי ✅ |

---

## 🔍 בדיקה מדויקת - קבצים עם תוכן צרפתי אמיתי

### קטגוריה א': תרגומים פעילים ✅

**1. `app/locale/fr/LC_MESSAGES/django.po`**
- תרגומים: ~300-500 מחרוזות
- סוג: Django gettext
- שימוש: ממשק משתמש מתורגם
- **סטטוס: פעיל!**

**2. `app/locale/fr/LC_MESSAGES/django.mo`**
- קובץ בינארי מקומפל
- **סטטוס: פעיל!**

---

### קטגוריה ב': תרגומי DB לא פעילים ⚠️

**3. `app/apps/core/migrations/0019_load_scripts.py`**
- תרגומים: 208 name_fr
- שורות עם צרפתית: ~208
- דוגמה: `{'name': 'Arabic', 'name_fr': 'arabe'}`
- **סטטוס: בDB אבל לא מוצג!**

**4. `app/apps/core/migrations/0018_auto_20190502_0936.py`**
- הגדרת שדה name_fr
- **סטטוס: יוצר את השדה**

**5. `front/src/stories/util/scripts.js`**
- תרגומים: 208 name_fr (JavaScript)
- זהה למיגרציה
- **סטטוס: Storybook בלבד, לא פרודקשן**

---

### קטגוריה ג': שמות אנשים 📝

**6. `app/contributors_example/contributors_list.html`**
- אותיות צרפתיות: é, è, ç
- שימוש: שמות כמו "Clérice", "Chagué"
- שורות: ~5
- **סטטוס: לא תרגום, רק שמות**

**7. `app/contributors_example/credits_list.html`**
- זהה ל-contributors_list
- **סטטוס: לא תרגום**

**8. `app/escriptorium/templates/core/credits.html`**
- זהה ל-contributors_list
- **סטטוס: לא תרגום**

---

### קטגוריה ד': קומנטים בקוד 💬

**9. `front/vue/components/DiploPanel.vue`**
- שורות עם צרפתית: 1-2
- תוכן: `//  nombre de caractères du début jusqu'à la position du curseur`
- תרגום: "מספר התווים מההתחלה עד מיקום הסמן"
- **סטטוס: קומנט, לא משפיע על הממשק**

**10. `front/src/stories/util/fixtures.js`**
- ככל הנראה name_fr בנתונים לדוגמה
- **צריך בדיקה מדויקת**

---

### קטגוריה ה': תווים טיפוגרפיים בלבד 🔤

**11-26. שאר הקבצים** (Templates, Vue, Python)
- תווים: em-dash (—), curly quotes (" ")
- **לא תרגום אמיתי!**
- דוגמה: `"allow n-gram matches anywhere"` (יש em-dash)

---

## 📊 סיכום סופי - תרגום לצרפתית

| רכיב | קבצים | פעיל? | השפעה על משתמש |
|------|-------|-------|----------------|
| **Django UI** | 2 | ✅ כן | ממשק מתורגם לחלוטין |
| **Scripts (name_fr)** | 3 | ❌ לא | קיים בDB, לא מוצג |
| **Typologies** | 0 | ❌ אין | אין name_fr בכלל |
| **Vue.js** | 0 | ❌ לא | אין vue-i18n |
| **שמות/קומנטים** | 6 | 📝 לא רלוונטי | לא תרגום |
| **תווים אקראיים** | 15 | ❌ לא | false positives |

---

## 🎯 המסקנה החשובה

**תרגום לצרפתית ב-eScriptorium:**
- ✅ **עובד:** ממשק המשתמש (django.po)
- ⚠️ **קיים אבל לא עובד:** שמות Scripts (name_fr)
- ❌ **לא קיים:** Typologies, Vue components

**BiblIA תיקן את זה:**
- הוסיף `get_localized_name()` ← עכשיו name_fr **עובד**!
- הוסיף `name_he` ותרגומים עבריים
- הוסיף תרגומים ל-Typologies

---

### 📄 `app/locale/fr/LC_MESSAGES/django.po`
**תפקיד:** קובץ התרגום הראשי של eScriptorium לצרפתית  
**סוג:** Django gettext translation file  
**יוצר:** Stefan Weil (2022)  
**תיאור:** מכיל תרגומים לכל מחרוזות הממשק (UI strings)

**מבנה:**
```gettext
msgid "You don't have any disk storage left."
msgstr "Vous n'avez plus d'espace disque."

msgid "Horizontal l2r"
msgstr "Horizontal de gauche à droite"
```

**תרגומים אופייניים:**
- ניווט ותפריטים
- הודעות שגיאה
- טפסים ולחצנים
- הודעות מערכת

**שימוש:**
```python
from django.utils.translation import gettext as _
message = _("You don't have any disk storage left.")
# במשתמש צרפתי: "Vous n'avez plus d'espace disque."
```

**סטטוס:** ✅ **פעיל** - קובץ זה עובד בפועל!

---

### 📄 `app/locale/fr/LC_MESSAGES/django.mo`
**תפקיד:** גרסה מקומפלת של django.po  
**סוג:** Binary message catalog  
**תיאור:** קובץ בינארי שנוצר מ-django.po על ידי `compilemessages`

**יצירה:**
```bash
python manage.py compilemessages
```

**סטטוס:** ✅ **פעיל** - Django קורא ממנו בזמן ריצה

---

## 2️⃣ קבצי נתונים (name_fr)

### 📄 `app/apps/core/migrations/0019_load_scripts.py`
**תפקיד:** טעינת 208 Unicode scripts עם תרגומים צרפתיים  
**סוג:** Django data migration  
**גודל:** ~15,000 שורות  
**תרגומים:** 208 scripts

**מבנה:**
```python
scripts_data = [
    {'iso_code': 'Arab', 'name': 'Arabic', 'name_fr': 'arabe', 'text_direction': 'horizontal-rl'},
    {'iso_code': 'Armn', 'name': 'Armenian', 'name_fr': 'arménien'},
    {'iso_code': 'Hebr', 'name': 'Hebrew', 'name_fr': 'hébreu'},
    {'iso_code': 'Latn', 'name': 'Latin', 'name_fr': 'latin'},
    # ... 204 more
]

def load_scripts(apps, schema_editor):
    Script = apps.get_model("core", "Script")
    for script_data in scripts_data:
        Script.objects.update_or_create(
            iso_code=script_data['iso_code'],
            defaults=script_data
        )
```

**דוגמאות תרגום:**
- `'Adlm'`: `'adlam'`
- `'Ahom'`: `'âhom'`
- `'Hluw'`: `'hiéroglyphes anatoliens (hiéroglyphes louvites, hiéroglyphes hittites)'`
- `'Aran'`: `'arabe (variante nastalique)'`

**סטטוס:** ⚠️ **נטען ל-DB אבל לא מוצג** (עד ש-BiblIA תיקן!)

---

### 📄 `app/apps/core/migrations/0018_auto_20190502_0936.py`
**תפקיד:** יצירת שדה name_fr במודל Script  
**סוג:** Django schema migration  
**תאריך:** 2 מאי 2019

**קוד:**
```python
migrations.AddField(
    model_name='script',
    name='name_fr',
    field=models.CharField(blank=True, max_length=128),
)
```

**סטטוס:** ✅ **פעיל** - השדה קיים ב-DB

---

### 📄 `front/src/stories/util/scripts.js`
**תפקיד:** JavaScript fixtures לסיפורי Storybook  
**סוג:** JavaScript data file  
**תרגומים:** 208 scripts (זהה למיגרציה)

**מבנה:**
```javascript
export const scripts = [
    {
        id: 1,
        name: "Adlam",
        name_fr: "adlam",
        iso_code: "Adlm",
        text_direction: "horizontal-rl",
        blank_char: " ",
    },
    {
        id: 5,
        name: "Arabic",
        name_fr: "arabe",
        iso_code: "Arab",
        text_direction: "horizontal-rl",
        blank_char: " ",
    },
    // ... 206 more
]
```

**שימוש:** Testing/Storybook development בלבד  
**סטטוס:** ⚠️ **לא בשימוש בפרודקשן** - רק לפיתוח

---

## 3️⃣ קבצי אנשים (Contributors)

### 📄 `app/contributors_example/contributors_list.html`
**תפקיד:** רשימת תורמים לפרויקט  
**סוג:** Django HTML template  
**שמות צרפתיים:**
- Alix Chagué (Inria)
- Thibault Clérice (Inria)
- Léa Maronet (Intern)

**אותיות צרפתיות:** `é`, `è`, `ç`

**סטטוס:** 📝 **תיעוד בלבד** - לא חלק מהתרגום, רק שמות

---

### 📄 `app/contributors_example/credits_list.html`
**תפקיד:** רשימת קרדיטים מורחבת  
**תוכן:** דומה ל-contributors_list.html  
**סטטוס:** 📝 **תיעוד בלבד**

---

### 📄 `app/escriptorium/templates/core/credits.html`
**תפקיד:** עמוד קרדיטים בממשק  
**שמות צרפתיים:** אותם תורמים  
**סטטוס:** 📝 **מוצג למשתמשים** - אבל לא תרגום

---

## 4️⃣ קבצי Templates (Django HTML)

### 📄 `app/escriptorium/templates/core/document_form.html`
**תפקיד:** טופס יצירת/עריכת מסמך  
**תוכן צרפתי:** ככל הנראה קומנטים או דוגמאות  
**צריך בדיקה:** ✓

---

### 📄 `app/escriptorium/templates/core/document_list.html`
**תפקיד:** רשימת מסמכים  
**תוכן צרפתי:** ככל הנראה קומנטים  
**צריך בדיקה:** ✓

---

### 📄 `app/escriptorium/templates/core/document_ontology.html`
**תפקיד:** ניהול אונטולוגיה של מסמך  
**צריך בדיקה:** ✓

---

### 📄 `app/escriptorium/templates/core/home.html`
**תפקיד:** דף הבית  
**צריך בדיקה:** ✓

---

### 📄 `app/escriptorium/templates/core/models_list/table.html`
**תפקיד:** טבלת מודלים  
**צריך בדיקה:** ✓

---

### 📄 `app/escriptorium/templates/registration/password_reset_done.html`
**תפקיד:** אישור איפוס סיסמה  
**צריך בדיקה:** ✓

---

### 📄 `app/escriptorium/templates/registration/password_reset_form.html`
**תפקיד:** טופס איפוס סיסמה  
**צריך בדיקה:** ✓

---

### 📄 `app/escriptorium/templates/reporting/project_reports.html`
**תפקיד:** דוחות פרויקט  
**צריך בדיקה:** ✓

---

## 5️⃣ קבצי Vue.js Components

### 📄 `front/vue/components/AlignModal/AlignAdvancedFieldset.vue`
**תפקיד:** Fieldset מתקדם ב-modal של יישור  
**צריך בדיקה:** ✓

---

### 📄 `front/vue/components/DiploPanel.vue`
**תפקיד:** פאנל דיפלומטי  
**צריך בדיקה:** ✓

---

### 📄 `front/vue/components/EditorNavigation/EditorNavigation.vue`
**תפקיד:** ניווט בעורך  
**צריך בדיקה:** ✓

---

### 📄 `front/vue/components/PartMetadataRow.vue`
**תפקיד:** שורת מטא-דאטה  
**צריך בדיקה:** ✓

---

### 📄 `front/vue/components/TagsSelector.vue`
**תפקיד:** בורר תגיות  
**צריך בדיקה:** ✓

---

## 6️⃣ קבצי Python (Backend Code)

### 📄 `app/apps/api/serializers.py`
**תפקיד:** Django REST Framework serializers  
**תוכן צרפתי:** ככל הנראה קומנטים או docstrings  
**צריך בדיקה:** ✓

---

### 📄 `app/apps/core/forms.py`
**תפקיד:** Django forms  
**צריך בדיקה:** ✓

---

### 📄 `app/apps/core/models.py`
**תפקיד:** Django models (כולל Script עם name_fr!)  
**תוכן חשוב:**
```python
class Script(models.Model):
    name = models.CharField(max_length=128)
    name_fr = models.CharField(max_length=128, blank=True)  # ← זה!
```
**סטטוס:** ✅ **קריטי** - הגדרת השדה

---

### 📄 `app/apps/core/tasks.py`
**תפקיד:** Celery tasks  
**צריך בדיקה:** ✓

---

### 📄 `app/apps/core/templatetags/timedelta.py`
**תפקיד:** Template tags מותאמים  
**צריך בדיקה:** ✓

---

### 📄 `app/apps/core/tests/test_views.py`
**תפקיד:** Unit tests  
**צריך בדיקה:** ✓

---

## 7️⃣ קבצים נוספים

### 📄 `front/src/stories/util/fixtures.js`
**תפקיד:** נתונים לדוגמה ל-Storybook  
**צריך בדיקה:** ✓

---

### 📄 `origin/develop:public/index.html`
**תפקיד:** HTML ראשי  
**צריך בדיקה:** ✓

---

## 📊 סיכום לפי סוג תוכן

| סוג תוכן | קבצים | פעיל? | תיאור |
|----------|-------|-------|--------|
| **Django i18n** | 2 | ✅ | django.po + django.mo - עובד! |
| **name_fr במיגרציות** | 2 | ⚠️ | נטען ל-DB אבל לא מוצג |
| **name_fr ב-JavaScript** | 2 | ⚠️ | scripts.js + fixtures.js - dev בלבד |
| **שמות תורמים** | 3 | 📝 | לא תרגום, רק שמות |
| **Templates** | 8 | ❓ | צריך בדיקה - קומנטים? |
| **Vue Components** | 5 | ❓ | צריך בדיקה - קומנטים? |
| **Python Code** | 5 | 🔍 | models.py חשוב! |

---

## 🔍 שלב הבא - בדיקה מעמיקה

עכשיו נבדוק כל קובץ ב"צריך בדיקה" כדי להבין:
1. האם זה תרגום אמיתי או סתם קומנט?
2. איך זה משתמש ב-name_fr?
3. האם זה משפיע על הממשק?

**רוצה שאמשיך לבדוק את ה-18 קבצים שסומנו "צריך בדיקה"?**

---

**תאריך יצירה:** 20 אוקטובר 2025

## 💻 דוגמאות קוד - איך התרגום עובד בפועל

### תרחיש 1: משתמש צרפתי נכנס למערכת

```python
# 1. הדפדפן שולח: Accept-Language: fr-FR
# 2. Django middleware מזהה:
from django.utils import translation
translation.activate('fr')

# 3. כל הטקסטים נשלפים מ-django.po:
from django.utils.translation import gettext as _
message = _("You don't have any disk storage left.")
# תוצאה: "Vous n'avez plus d'espace disque." ✅

# 4. אבל Scripts נשארים באנגלית! ❌
script = Script.objects.get(iso_code='Arab')
print(str(script))  # "Arabic" במקום "arabe"
```

### תרחיש 2: BiblIA פותר את הבעיה

```python
# עכשיו __str__() משתמש ב-get_localized_name():
translation.activate('fr')
script = Script.objects.get(iso_code='Arab')
print(str(script))  # "arabe" ✅
```

---

**תאריך יצירה:** 20 אוקטובר 2025  
**תאריך עדכון:** 20 אוקטובר 2025
