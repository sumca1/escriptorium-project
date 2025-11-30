# 📚 מערכת התרגום העברית - תיעוד מפורט

## סקירה כללית

המערכת משתמשת ב-**4 שכבות תרגום** שונות, כל אחת אחראית על סוג אחר של תוכן:

---

## 🎯 שכבה 1: Django i18n (קבצי .po/.mo)

### 📁 קובץ: `app/locale/he/LC_MESSAGES/django.po`

**אחראי על:**
- ✅ מחרוזות שעוברות דרך `{% trans %}` או `gettext()` בקוד Django
- ✅ טקסטים סטטיים בתבניות (templates)
- ✅ הודעות מערכת
- ✅ כותרות דפים
- ✅ תיאורי שדות בטפסים
- ✅ הודעות שגיאה

**דוגמאות למה שמתורגם:**
```python
# בקוד Python:
_("Export your document")  # מתורגם מ-.po

# בתבנית HTML:
{% trans "Delete" %}  # מתורגם מ-.po
```

**כיצד לעדכן:**
1. ערוך את הקובץ `django.po`
2. הרץ: `python manage.py compilemessages -l he`
3. העתק את `django.mo` החדש לקונטיינר
4. אתחל את שרת web

**⚠️ לא משפיע על:**
- ❌ שמות תמלולים ממסד הנתונים (manual, ALTO)
- ❌ סוגי אזורים דינמיים (Title, Main, header)
- ❌ JavaScript דינמי
- ❌ ערכים שנשמרו במסד נתונים

---

## 🎯 שכבה 2: Typology Translations (מסד נתונים)

### 📁 קובץ: `app/apps/core/typology_translations_he.py`

**אחראי על:**
- ✅ **שמות סוגי אזורים** (BlockType) - Title, Main, Commentary, header, other, paragraph, page-number
- ✅ **סוגי שורות** (LineType) - Correction, Numbering, Signature
- ✅ **סוגי מסמכים** (DocumentType)
- ✅ **סוגי חלקים** (PartType)

**⚠️ חשוב מאוד:** קובץ זה משפיע **רק על מודלים במסד הנתונים**! אם תוסיף כאן "Documents", "Save", "Edit" - זה **לא יעבוד** כי אלה לא שמות טיפולוגיות!

**איך זה עובד:**
1. המילון `TYPOLOGY_TRANSLATIONS_HE` מכיל תרגומים
2. Migration `0078_populate_typology_hebrew.py` טוען את התרגומים למסד נתונים
3. כל טיפולוגיה נשמרת עם `name` (אנגלית) ו-`name_he` (עברית)
4. המערכת מציגה `name_he` כשהשפה היא עברית

**דוגמה:**
```python
TYPOLOGY_TRANSLATIONS_HE = {
    "Title": "כותרת",
    "Main": "עיקרי",
    "header": "כותרת עליונה",
    "paragraph": "פסקה",
}
```

**כיצד לעדכן:**
1. הוסף תרגום ל-`typology_translations_he.py`
2. העתק הקובץ לקונטיינר
3. הרץ סקריפט עדכון במסד נתונים:
```python
from core.models import BlockType
BlockType.objects.filter(name='header').update(name_he='כותרת עליונה')
```

**⚠️ לא משפיע על:**
- ❌ כפתורים סטטיים (Save, Delete, Cancel)
- ❌ תפריטי ניווט
- ❌ שמות תמלולים (manual, ALTO)
- ❌ פורמטי ייצוא

---

## 🎯 שכבה 3: Clean BiblIA Middleware (HTML דינמי)

### 📁 קובץ: `app/clean_biblia_middleware_v2.py`

**אחראי על:**
- ✅ **תרגום HTML לאחר רינדור** - מחליף טקסט אנגלי בעברי
- ✅ מחרוזות שלא עוברות דרך Django i18n
- ✅ תוכן JavaScript שמוצג ב-HTML
- ✅ טקסטים דינמיים שמגיעים מ-API
- ✅ הוספת תמיכה RTL (right-to-left)

**איך זה עובד:**
1. Django מייצר HTML בסיסי (באנגלית)
2. ה-Middleware מפרסר את ה-HTML עם BeautifulSoup
3. מחפש מחרוזות מהמילון `translation_map`
4. מחליף אותן בתרגום העברי
5. מוסיף CSS ל-RTL
6. מחזיר HTML מתורגם

**דוגמה:**
```python
self.translation_map = {
    'Documents': 'מסמכים',
    'Projects': 'פרוייקטים',
    'manual': 'ידני',
    'ALTO': 'ALTO',
    'Title': 'כותרת',
}
```

**✅ משפיע על:**
- ✅ טקסט גלוי ב-HTML
- ✅ כפתורים דינמיים
- ✅ תפריטים
- ✅ ערכים שמגיעים מ-JavaScript

**⚠️ לא משפיע על:**
- ❌ תוכן `<script>` ו-`<style>` (מדלג עליהם)
- ❌ JSON attributes
- ❌ data-* attributes
- ❌ קוד JavaScript עצמו

**כיצד לעדכן:**
1. ערוך את `clean_biblia_middleware_v2.py`
2. הוסף תרגומים ל-`translation_map`
3. העתק לקונטיינר
4. אתחל את שרת web

---

## 🎯 שכבה 4: Vue i18n (front/vue/locales/he.json)

### 📁 קובץ: `front/vue/locales/he.json`

**אחראי על:**
- ✅ **ממשק Vue.js** - 388 קומפוננטות Vue
- ✅ אפליקציית העריכה (Editor) - UnifiedEditor, TranscriptionModal, SegPanel
- ✅ כפתורים וכלים בממשק - "צבע רקע", "מלבן", "File", "Edit", "Tools"
- ✅ טקסטים דינמיים ב-frontend - 465 תרגומים מוגדרים
- ✅ הודעות UI בצד לקוח
- ⚠️ **116 תרגומים חסרים** - נמצאים בקוד אבל לא ב-he.json!

**סטטוס כיסוי:**
- 178 תרגומים בשימוש בקוד Vue
- 465 תרגומים מוגדרים ב-he.json
- 38 תרגומים נוספים מ-`window.EDITOR_TRANSLATIONS` (Django)
- **חסרים: 116** (כולל: "Auto Correct", "Classic", "Clear All", "Detect Errors")

**דוגמאות למה שמתורגם:**
```json
{
  "Background Color": "צבע רקע",
  "Rectangle": "מלבן",
  "Delete": "מחק",
  "Cancel": "בטל"
}
```

**איך זה עובד:**
1. Vue.js משתמש ב-`vue-i18n` library
2. קובץ `he.json` טוען אוטומטית כשהשפה עברית
3. בקומפוננטות: `{{ $t('Background Color') }}` → "צבע רקע"
4. תמיכה מלאה ב-RTL

**כיצד לעדכן:**
1. ערוך את `front/vue/locales/he.json`
2. הוסף תרגומים במבנה JSON
3. בנה את Vue: `npm run build` (או הקומפילציה אוטומטית בפיתוח)
4. רענן דפדפן

**⚠️ לא משפיע על:**
- ❌ תבניות Django (.html)
- ❌ טיפולוגיות במסד נתונים
- ❌ Backend/Python

---

## 📊 טבלת השוואה - מה מתרגם מה?

| סוג תוכן | django.po | typology_translations_he.py | clean_biblia_middleware_v2.py | he.json (Vue) |
|----------|-----------|----------------------------|------------------------------|---------------|
| **כפתורי ממשק Django** (Save, Delete) | ✅ | ❌ | ✅ (גיבוי) | ❌ |
| **כפתורי ממשק Vue** (צבע רקע, מלבן) | ❌ | ❌ | ❌ | ✅ |
| **תפריטי ניווט** | ✅ | ❌ | ✅ (גיבוי) | ❌ |
| **שמות סוגי אזורים** (Title, Main, header) | ❌ | ✅ | ✅ (גיבוי) | ❌ |
| **שמות תמלולים** (manual) | ❌ | ❌ | ✅ | ❌ |
| **פורמטי ייצוא** (ALTO, OpenITI) | ❌ | ❌ | ✅ | ❌ |
| **הודעות שגיאה Django** | ✅ | ❌ | ❌ | ❌ |
| **הודעות UI בעריכה** | ❌ | ❌ | ❌ | ✅ |
| **תיאורי טפסים** | ✅ | ❌ | ❌ | ❌ |
| **טקסט דינמי מ-JavaScript** | ❌ | ❌ | ✅ | ❌ |
| **קומפוננטות Vue.js** | ❌ | ❌ | ❌ | ✅ |
| **תמיכה RTL** | ❌ | ❌ | ✅ | ✅ (Vue) |

---

## 🔄 זרימת עבודה: איך לתרגם טקסט חדש?

### תרחיש 1: הוספת כפתור חדש בתבנית Django
```django
<button>{% trans "My New Button" %}</button>
```
**פתרון:** הוסף ל-`django.po`:
```
msgid "My New Button"
msgstr "הכפתור החדש שלי"
```

### תרחיש 2: הוספת סוג אזור חדש
```python
BlockType.objects.create(name='footer')
```
**פתרון:** 
1. הוסף ל-`typology_translations_he.py`:
```python
"footer": "כותרת תחתונה",
```
2. עדכן במסד נתונים:
```python
BlockType.objects.filter(name='footer').update(name_he='כותרת תחתונה')
```

### תרחיש 3: כפתור בעורך Vue
```vue
<button>{{ $t('Background Color') }}</button>
```
**פתרון:** הוסף ל-`front/vue/locales/he.json`:
```json
{
  "Background Color": "צבע רקע"
}
```

### תרחיש 4: טקסט שמופיע רק ב-HTML דינמי
```html
<span>Processing complete</span>
```
**פתרון:** הוסף ל-`clean_biblia_middleware_v2.py`:
```python
'Processing complete': 'העיבוד הושלם',
```

---

## 🐛 פתרון בעיות נפוצות

### בעיה: "הטקסט לא מתורגם"

**שאלות לבדיקה:**
1. ❓ **מאיפה הטקסט מגיע?**
   - תבנית Django → בדוק `django.po`
   - שם טיפולוגיה → בדוק `typology_translations_he.py`
   - JavaScript/דינמי → בדוק `clean_biblia_middleware_v2.py`

2. ❓ **האם עדכנת את הקובץ הנכון בקונטיינר?**
   ```bash
   docker cp file.py escriptorium_clean-web-1:/path/to/file.py
   ```

3. ❓ **האם אתחלת את השרת?**
   ```bash
   docker-compose restart web
   ```

4. ❓ **האם השפה מוגדרת לעברית?**
   - בדוק בהגדרות משתמש
   - URL צריך להכיל `/he/`

### בעיה: "התרגום מופיע רק באנגלית"

**אבחון:**
```python
# בדוק אם התרגום קיים במסד נתונים:
from core.models import BlockType
BlockType.objects.filter(name='header').values('name', 'name_he')

# בדוק אם ה-.mo קומפל:
ls -lh app/locale/he/LC_MESSAGES/django.mo

# בדוק logs של middleware:
docker logs escriptorium_clean-web-1 | grep "BibliaMiddleware"
```

---

## 📝 רשימת קבצים חשובים

### קבצי תרגום:
- `app/locale/he/LC_MESSAGES/django.po` - תרגומי Django (Backend)
- `app/locale/he/LC_MESSAGES/django.mo` - קומפילציה של .po
- `app/apps/core/typology_translations_he.py` - תרגומי טיפולוגיות (מסד נתונים)
- `app/clean_biblia_middleware_v2.py` - Middleware דינמי (HTML)
- `front/vue/locales/he.json` - תרגומי Vue.js (Frontend) - **~400+ תרגומים**

### קבצי הגדרה:
- `app/escriptorium/settings.py` - הגדרות MIDDLEWARE
- `app/apps/core/migrations/0078_populate_typology_hebrew.py` - טעינת תרגומים למסד נתונים

### קבצי Context Processors:
- `app/biblia_translation_processor.py` - Context processor פשוט (לא בשימוש)
- `app/biblia_translation_middleware.py` - Middleware ישן (לא בשימוש)
- `app/enhanced_biblia_middleware.py` - גרסה משופרת (לא בשימוש)

---

## 🎯 סיכום

**4 שכבות, 4 אחריות - אחרי ניקוי:**

1. **Django i18n (django.po)** → טקסטים סטטיים מתבניות Django וקוד Python [1100+ תרגומים]
2. **Typology Translations (typology_translations_he.py)** → שמות טיפולוגיות ממסד נתונים [19 תרגומים - 100% מכוסה]
3. **Clean BiblIA Middleware (clean_biblia_middleware_v2.py)** → **RTL support + 4 תרגומי fallback** (מנוקה!)
4. **Vue i18n (he.json)** → ממשק Vue.js (Editor, כפתורים, כלים) [465 תרגומים, חסרים 116]

**כלל אצבע - מתי להשתמש באיזה קובץ:**
- 🎨 כפתור/טקסט בתבנית Django → `django.po`
- 📦 שם טיפולוגיה (Title, Main, paragraph) → `typology_translations_he.py`
- 🖼️ כפתור/טקסט בקומפוננטת Vue → `front/vue/locales/he.json`
- 🔄 RTL support או fallback ייחודי → `clean_biblia_middleware_v2.py` (רק במקרים מיוחדים!)

**⚠️ אזהרה:** רוב התרגומים צריכים להיות ב-`django.po` או `he.json`, **לא** ב-middleware!

---

תיעוד זה עודכן לאחרונה: 23 באוקטובר 2025
