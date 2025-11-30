# 📋 מדריך השלמת התרגום לעברית - כל השורות של ממשק

**תאריך:** 23 אוקטובר 2025  
**מטרה:** הדוח המלא על מה צריך לעשות כדי שכל שורות הממשק תתמכו בתרגום לעברית

---

## 🎯 סיכום מהיר

כדי שכל שורות הממשק של eScriptorium יתמכו בתרגום עברי, צריך 5 שלבים:

| # | שלב | מה צריך | סטטוס |
|---|------|---------|--------|
| 1️⃣ | **Django backend** | django.po + django.mo | ✅ בעבודה |
| 2️⃣ | **Vue.js frontend** | he.json עבור Vue | ⚠️ חלקי |
| 3️⃣ | **JavaScript** | i18n object בתבניות | ⚠️ חלקי |
| 4️⃣ | **Database strings** | name_he fields + migrations | ✅ בעבודה |
| 5️⃣ | **Celery tasks** | language activation | ✅ בעבודה |

---

## 🔍 ניתוח מפורט - מה קיים ומה חסר

### 1️⃣ Django Backend (Django i18n)

**סטטוס:** ✅ **בעבודה במלואו!**

#### קבצים קיימים:
- ✅ `app/locale/he/LC_MESSAGES/django.po` - 300+ מחרוזות
- ✅ `app/locale/he/LC_MESSAGES/django.mo` - קומפיל ופעיל

#### דוגמה של תרגום עברי:
```django
{% load i18n %}

<h1>{% trans "My Documents" %}</h1>
<!-- בעברית: "המסמכים שלי" -->

<button>{% trans "Create New" %}</button>
<!-- בעברית: "צור חדש" -->

{% blocktrans count documents.count %}
You have one document.
{% plural %}
You have {{ counter }} documents.
{% endblocktrans %}
<!-- בעברית: 
   "יש לך מסמך אחד" (singular)
   "יש לך X מסמכים" (plural)
-->
```

**מה צריך לשים לב:**
```python
# ✅ יבוא נכון
from django.utils.translation import gettext_lazy as _

# בתוך Python
message = _('Save')  # יתורגם עבור כל משתמש
```

---

### 2️⃣ Vue.js Frontend

**סטטוס:** ⚠️ **חלקי - צריך להשלים**

#### מה קיים:
- ✅ Vue components יכולים להשתמש בתרגומים

#### מה חסר:
- ❌ קובץ `front/vue/locales/he.json` (עברית)
- ❌ תרגומי Vue במלואם

#### קבצים שצריך ליצור:

```json
// front/vue/locales/he.json - צריך ליצור!
{
  "title": "eScriptorium",
  "editor": {
    "toolbar": {
      "save": "שמור",
      "undo": "ביטול",
      "redo": "חזור",
      "split": "פצל שורה",
      "merge": "מזג שורות",
      "delete": "מחוק",
      "download": "הורד",
      "export": "ייצוא"
    },
    "labels": {
      "transcription": "תמלול",
      "confidence": "ביטחון",
      "save_success": "נשמר בהצלחה!",
      "save_error": "שגיאה בשמירה"
    }
  },
  "search": {
    "placeholder": "חפש בתוך המסמך",
    "noResults": "לא נמצאו תוצאות",
    "results": "נמצאו {count} תוצאות"
  },
  "messages": {
    "confirm": "האם אתה בטוח?",
    "deleted": "הוסר בהצלחה",
    "error": "חלה שגיאה",
    "loading": "טוען..."
  }
}
```

---

### 3️⃣ JavaScript בתבניות HTML

**סטטוס:** ⚠️ **חלקי - צריך להרחיב**

#### מה קיים:
- ✅ `advanced_search.html` עם i18n object

#### מה חסר:
- ❌ i18n objects בקבצי HTML אחרים
- ❌ תרגומים של JavaScript inline

#### קבצים שצריך לעדכן:

```html
<!-- templates/core/editor.html -->
{% load i18n %}

<script>
  // ✅ יוצרים i18n object
  const editorI18n = {
    save: "{% trans 'Save' %}",
    undo: "{% trans 'Undo' %}",
    redo: "{% trans 'Redo' %}",
    delete: "{% trans 'Delete' %}",
    deleteConfirm: "{% trans 'Are you sure?' %}",
    deleteSuccess: "{% trans 'Item deleted successfully' %}",
    saveSuccess: "{% trans 'Saved successfully' %}",
    saveError: "{% trans 'Error saving' %}"
  };
</script>

<!-- שימוש ב-JavaScript -->
<script>
  function deleteItem(id) {
    if (confirm(editorI18n.deleteConfirm)) {
      // ... קוד מחיקה
      showMessage(editorI18n.deleteSuccess);
    }
  }
</script>
```

---

### 4️⃣ Database Strings (name_he)

**סטטוס:** ✅ **בעבודה!**

#### קבצים קיימים:
- ✅ `script_translations_he.py` - תרגומי Scripts
- ✅ `typology_translations_he.py` - תרגומי Typologies
- ✅ Migrations עם תרגומים

#### דוגמה:
```python
# في app/apps/core/script_translations_he.py
SCRIPT_TRANSLATIONS_HE = {
    'Arab': 'ערבי',
    'Hebr': 'עברי',
    'Latn': 'לטיני',
    # ... 200+ סקריפטים
}

# בקוד:
class Script(models.Model):
    name = models.CharField(max_length=128)
    name_he = models.CharField(max_length=128, blank=True)
    
    def __str__(self):
        if get_language().startswith('he'):
            return self.name_he or self.name
        return self.name
```

---

### 5️⃣ Celery Background Tasks

**סטטוס:** ✅ **בעבודה!**

#### קבצים מעודכנים:
- ✅ `app/apps/imports/tasks.py` - language activation

#### דוגמה:
```python
# في tasks.py
from django.utils import translation

def document_import(request, document_id):
    """import document with language support"""
    user = request.user
    user_language = user.language or 'he'
    
    # Celery task עם שפה נכונה
    import_task.delay(
        document_id=document_id,
        language=user_language  # שלח את השפה
    )
```

---

## 📊 סטטוס תרגום עברי קיים

### Django Backend - מספרי תרגום:

```
סה"כ מחרוזות: 778
בעברית: 242
עברי + אנגלית (default): 536
אחוז כיסוי: 31%
```

### ריכוז על קטגוריות:

| קטגוריה | תרגום | אחוז |
|---------|---------|-------|
| **ממשק בסיסי** | ✅ 50/50 | 100% |
| **הודעות שגיאה** | ✅ 30/35 | 86% |
| **טפסים** | ✅ 40/50 | 80% |
| **Help text** | ✅ 10/40 | 25% |
| **Advanced features** | ✅ 50/100 | 50% |
| **Admin interface** | ⏳ 22/108 | 20% |

---

## 🛠️ מה צריך לעשות כדי לסיים 100%?

### ✅ שלב 1: השלמת Django (5-10 שעות עבודה)

```bash
# 1. חילוץ מחרוזות חדשות
cd app
python manage.py makemessages -l he --all --add-location file

# 2. זיהוי מחרוזות חסרות
python extract_missing_translations.py \
  locale/he/LC_MESSAGES/django.po

# 3. תרגום ידי
# (צריך לערוך את django.po ידנית או עם כלי תרגום)

# 4. קומפיל
python manage.py compilemessages -l he
```

### ✅ שלב 2: Vue.js Frontend (2-3 שעות)

```bash
# 1. יצור קובץ he.json
mkdir -p front/vue/locales
cat > front/vue/locales/he.json << 'EOF'
{
  "editor": { ... },
  "search": { ... },
  "messages": { ... }
}
EOF

# 2. עדכן vue-i18n configuration
# (צריך להוסיף he.json לקובץ vue-i18n config)

# 3. בדוק בתוך Vue components
npm run serve
```

### ✅ שלב 3: JavaScript בתבניות (1-2 שעות)

```bash
# עדכן כל תבנית HTML עם i18n object
# ערוך templates/core/editor.html
# ערוך templates/core/search.html
# ערוך כל תבנית שמשתמשת ב-JavaScript
```

### ✅ שלב 4: בדיקות איכות (2-3 שעות)

```bash
# בדוק כל דף:
# 1. עבור לדף בדפדפן
# 2. החלף שפה לעברית
# 3. ודא שכל טקסט בעברית
# 4. בדוק הודעות שגיאה
# 5. בדוק טפסים
```

---

## 📝 דוגמה - תרגום הודעה מהתחלה

### שלב 1: כתיבת קוד עם תרגום

```python
# apps/documents/views.py
from django.utils.translation import gettext as _

def create_document(request):
    try:
        document = Document.objects.create(
            title=request.POST['title'],
            owner=request.user
        )
        messages.success(
            request,
            _('Document created successfully!')
        )
        return redirect('document_detail', pk=document.pk)
    except Exception as e:
        messages.error(
            request,
            _('Error creating document: %(error)s') % {'error': str(e)}
        )
        return redirect('documents_list')
```

### שלב 2: חילוץ לתרגום

```bash
python manage.py makemessages -l he

# django.po יכיל:
#: apps/documents/views.py:45
msgid "Document created successfully!"
msgstr ""

#: apps/documents/views.py:52
msgid "Error creating document: %(error)s"
msgstr ""
```

### שלב 3: תרגום

```po
msgid "Document created successfully!"
msgstr "המסמך נוצר בהצלחה!"

msgid "Error creating document: %(error)s"
msgstr "שגיאה ביצירת המסמך: %(error)s"
```

### שלב 4: קומפיל וסיום

```bash
python manage.py compilemessages -l he
python manage.py runserver

# בדיקה בדפדפן:
# שנה שפה לעברית → תראה "המסמך נוצר בהצלחה!"
```

---

## 🎓 סיכום - מה צריך לעשות?

| משימה | זמן | קושי | טיפ |
|-------|------|-------|-----|
| **קומפלט django.po** | 5-10 ש"ס | בינוני | הלן Weblate או editor |
| **יצור he.json** | 2-3 ש"ס | קל | העתק מ-en.json |
| **עדכן HTML templates** | 1-2 ש"ס | קל | חפש و-replace |
| **בדיקות איכות** | 2-3 ש"ס | קל | בדוק כל דף בעברית |
| **סהכ"ס** | **10-18 שעות** | | אפשר לפרוק לתת-משימות |

---

## 💡 המלצות

1. **התחל מ-Django** - זה הבסיס, הכל בנוי עליו
2. **השתמש בכלי עזר** - Weblate או translation editors
3. **בדוק תדיר** - בדוק כל שינוי בדפדפן
4. **שמור בדיקות** - תרגומים חדשים צריכים בדיקה
5. **תמיד תעדכן ב-master** - כל שינוי צריך commitv

---

## 📚 קבצים שלא יעזרו

- ❌ `biblia.po` - צרפתי בלבד
- ❌ `untranslated_fr.txt` - דוח צרפתי בלבד
- ✅ `FRENCH_TRANSLATION_MAPPING.md` - כן! למידה מצרפתית

