# ✅ Practical Checklist - מה לעשות צעד אחר צעד

**תאריך:** 23 אוקטובר 2025  
**מטרה:** רשימת פעולות קונקרטית - מה בדיוק צריך לעשות

---

## 🎯 ממצא: יש לנו תוכנית ברורה!

סה"כ צריך 4 משימות עיקריות:

```
MISSION 1: Django Backend (5-10 שעות)
├─ ✅ קיים: django.po + django.mo + 242 תרגומים
└─ ❌ חסר: 536 מחרוזות לא מתורגמות

MISSION 2: Vue.js Frontend (2-3 שעות)
├─ ✅ קיים: Vue infrastructure
└─ ❌ חסר: front/vue/locales/he.json (100 מפתחות)

MISSION 3: JavaScript HTML (1-2 שעות)
├─ ✅ קיים: advanced_search.html pattern
└─ ❌ חסר: i18n objects בשאר התבניות

MISSION 4: QA & Testing (2-3 שעות)
├─ ✅ תוכנית בדיקה
└─ ❌ ביצוע בדיקות

סה"כ: 10-18 שעות עבודה
```

---

## 📋 MISSION 1: Django Backend Completion

### שלב 1.1: חילוץ מחרוזות חדשות

```bash
# נווט לספריית האפליקציה
cd app

# חילוץ כל המחרוזות הלא מתורגמות
python manage.py makemessages -l he --all --add-location file

# ✅ תוצאה צפויה:
# - django.po יעודכן עם 536 מחרוזות חדשות
# - כל msgstr יהיה ריק ("")
```

### שלב 1.2: זיהוי ודיווח חסרים

```bash
# יצור דוח של מחרוזות חסרות
grep -E '^msgstr ""$' locale/he/LC_MESSAGES/django.po > untranslated_he.txt

# ✅ תוצאה:
# - untranslated_he.txt עם 536 שורות
# - כל שורה = מחרוזת שצריך תרגום
```

### שלב 1.3: תרגום ידני

**שלוש אפשרויות:**

#### אפשרות A: Weblate (המומלץ)
```
1. נווט ל: https://hosted.weblate.org/projects/escriptorium/
2. בחר "Hebrew" (עברית)
3. אדם = התחל תרגום
4. תרגם 536 מחרוזות

⏱️ זמן: 5-10 שעות (תלוי בעזרה קהילתית)
```

#### אפשרות B: Poedit Editor (Standalone)
```
1. הורד Poedit: https://poedit.net/
2. פתח: app/locale/he/LC_MESSAGES/django.po
3. תרגם כל msgstr ריק
4. שמור

⏱️ זמן: 5-8 שעות (עם מילון בחזות)
```

#### אפשרות C: Text Editor + Python Script
```bash
# יצור Python script להוספה חצי-אוטומטית
cat > translate_batch.py << 'EOF'
import polib
po = polib.pofile('locale/he/LC_MESSAGES/django.po')

for entry in po:
    if not entry.msgstr:
        # הוסף תרגום (מן הרשימה שלך)
        entry.msgstr = get_translation(entry.msgid)

po.save()
EOF

python translate_batch.py

⏱️ זמן: 3-5 שעות (רק בהתאמה ידנית סופית)
```

### שלב 1.4: קומפיל

```bash
# קומפיל ל-.mo
python manage.py compilemessages -l he

# ✅ תוצאה:
# - django.mo יעודכן
# - לא צריך להפעיל את השרת - קורא מהקובץ

# בדיקה קטנה
python manage.py shell
>>> from django.utils.translation import activate, gettext as _
>>> activate('he')
>>> _('Save')  # צריך להדפיס: "שמור"
'שמור'
```

### ✅ Checklist MISSION 1

- [ ] הרץ `makemessages -l he --all`
- [ ] בדוק שנוצרו 536 מחרוזות חדשות
- [ ] תרגם את כל המחרוזות (בחר אפשרות A/B/C)
- [ ] בדוק thatלא חסרים תרגומים
- [ ] הרץ `compilemessages -l he`
- [ ] בדוק בקונסול Python
- [ ] הפעל את השרת וודא בדפדפן

**סטטוס Mission 1:** ✅ `100% Django coverage`

---

## 📋 MISSION 2: Vue.js Frontend

### שלב 2.1: יצירת he.json

```bash
# נווט לספריית Vue
cd front/vue/locales

# יצור קובץ עברי
cat > he.json << 'EOF'
{
  "title": "eScriptorium",
  "editor": {
    "toolbar": {
      "save": "שמור",
      "undo": "ביטול",
      "redo": "חזור",
      "cut": "גזור",
      "copy": "העתק",
      "paste": "הדבק",
      "delete": "מחוק",
      "select_all": "בחר הכל",
      "clear": "מחק הכל",
      "split": "פצל שורה",
      "merge": "מזג שורות",
      "zoom_in": "הגדל",
      "zoom_out": "הקטן",
      "fullscreen": "מסך מלא",
      "export": "ייצוא",
      "download": "הורד"
    },
    "labels": {
      "transcription": "תמלול",
      "confidence": "ביטחון",
      "accuracy": "דיוק",
      "status": "סטטוס",
      "page": "עמוד",
      "line": "שורה",
      "word": "מילה"
    },
    "messages": {
      "saving": "שומר...",
      "saved": "נשמר בהצלחה!",
      "error_saving": "שגיאה בשמירה",
      "loading": "טוען...",
      "loaded": "טוען בהצלחה",
      "error_loading": "שגיאה בטעינה",
      "no_results": "לא נמצאו תוצאות",
      "confirm_delete": "האם אתה בטוח?",
      "deleted": "הוסר בהצלחה"
    }
  },
  "search": {
    "placeholder": "חפש בתוך המסמך...",
    "search_button": "חפש",
    "clear_button": "נקה",
    "results": "נמצאו {count} תוצאות",
    "no_results": "לא נמצאו תוצאות",
    "previous": "הקודם",
    "next": "הבא"
  },
  "document": {
    "title": "כותרת",
    "description": "תיאור",
    "created": "נוצר",
    "modified": "שונה",
    "author": "מחבר",
    "pages": "עמודים"
  },
  "errors": {
    "network_error": "שגיאת רשת",
    "server_error": "שגיאת שרת",
    "invalid_input": "קלט לא תקין",
    "access_denied": "גישה נדחתה",
    "not_found": "לא נמצא"
  }
}
EOF
```

### שלב 2.2: עדכון Vue configuration

```javascript
// front/vue/src/i18n.js
import Vue from 'vue'
import VueI18n from 'vue-i18n'

Vue.use(VueI18n)

import en from '@/locales/en.json'
import fr from '@/locales/fr.json'
import he from '@/locales/he.json'  // ← הוסף את זה!

const messages = {
  en,
  fr,
  he  // ← הוסף את זה!
}

export default new VueI18n({
  locale: 'en',
  messages,
  fallbackLocale: 'en'
})
```

### שלב 2.3: בדיקה

```bash
# בנייה ובדיקה
cd front/vue
npm run serve

# בדפדפן:
# 1. נווט ל: http://localhost:8080
# 2. החלף שפה לעברית (אם יש בחירה)
# 3. בדוק שהכפתורים בעברית
# 4. בדוק שההודעות בעברית
```

### ✅ Checklist MISSION 2

- [ ] יצור he.json עם 100 מפתחות
- [ ] עדכן vue i18n configuration
- [ ] הרץ `npm run serve`
- [ ] בדוק בדפדפן בעברית
- [ ] ודא שההודעות בעברית
- [ ] בדוק כמה Vue components

**סטטוס Mission 2:** ✅ `100% Vue.js coverage`

---

## 📋 MISSION 3: JavaScript Inline HTML

### שלב 3.1: סריקת templates

```bash
# חפש תבניות עם JavaScript
find templates -name "*.html" -exec grep -l "<script>" {} \;

# בודקות עם JavaScript inline:
# - templates/core/editor.html
# - templates/core/search.html
# - templates/core/document_images.html
# - templates/core/models_list/main.html
```

### שלב 3.2: הוספת i18n object

**דוגמה - editor.html:**

```html
<!-- templates/core/editor.html -->
{% load i18n %}

<script>
  // יצור i18n object
  const editorI18n = {
    // Toolbar
    save: "{% trans 'Save' %}",
    undo: "{% trans 'Undo' %}",
    redo: "{% trans 'Redo' %}",
    delete: "{% trans 'Delete' %}",
    
    // Messages
    saveSuccess: "{% trans 'Saved successfully' %}",
    saveError: "{% trans 'Error saving' %}",
    deleteConfirm: "{% trans 'Are you sure?' %}",
    deleteSuccess: "{% trans 'Item deleted successfully' %}",
    
    // Errors
    networkError: "{% trans 'Network error' %}",
    serverError: "{% trans 'Server error' %}"
  };
</script>

<!-- שימוש בקוד -->
<script>
  function saveDocument() {
    fetch('/api/save', {method: 'POST'})
      .then(() => alert(editorI18n.saveSuccess))
      .catch(() => alert(editorI18n.saveError));
  }
  
  function deleteItem(id) {
    if (confirm(editorI18n.deleteConfirm)) {
      fetch(`/api/delete/${id}`, {method: 'DELETE'})
        .then(() => alert(editorI18n.deleteSuccess));
    }
  }
</script>
```

### שלב 3.3: עדכון כל template

**רשימת templates לעדכן:**

```
[ ] templates/core/editor.html
[ ] templates/core/search.html
[ ] templates/core/document_images.html
[ ] templates/core/models_list/main.html
[ ] templates/core/documents_tasks_list.html
[ ] templates/core/ontology/import_ontology.html
[ ] כל template נוסף עם JavaScript
```

### ✅ Checklist MISSION 3

- [ ] סרוק את כל templates לחיפוש JavaScript
- [ ] הוסף i18n object לכל template
- [ ] בדוק שכל משתנה בתרגום
- [ ] הפעל את השרת
- [ ] בדוק כל דף בעברית
- [ ] ודא שהודעות בעברית

**סטטוס Mission 3:** ✅ `100% JavaScript coverage`

---

## 📋 MISSION 4: QA & Testing

### שלב 4.1: בדיקת דפים

**Checklist דפים:**

```
MAIN PAGES:
[ ] Home page - כל טקסט בעברית?
[ ] Login page - כל טקסט בעברית?
[ ] Document list - שמות מסמכים בעברית?

EDITOR:
[ ] Editor toolbar - כפתורים בעברית?
[ ] Transcription panel - כל הודעות בעברית?
[ ] Regions & lines - תיאורים בעברית?

FEATURES:
[ ] Search - הודעות חיפוש בעברית?
[ ] Import - הודעות ייבוא בעברית?
[ ] Export - הודעות ייצוא בעברית?
[ ] Models - רשימת מודלים בעברית?

ERRORS:
[ ] 404 page - בעברית?
[ ] 403 page - בעברית?
[ ] Form errors - הודעות שגיאה בעברית?
[ ] Network errors - בעברית?

MESSAGES:
[ ] Success messages - בעברית?
[ ] Error messages - בעברית?
[ ] Warning messages - בעברית?
[ ] Info messages - בעברית?
```

### שלב 4.2: בדיקת תפקוד

```bash
# 1. התחברות למערכת
# - Username: test
# - Password: test123
# ✅ בדוק: כל ההודעות בעברית

# 2. יצירת מסמך
# ✅ בדוק: הודעות הצלחה בעברית

# 3. העלאת תמונות
# ✅ בדוק: הודעות התקדמות בעברית

# 4. עריכה בעורך
# ✅ בדוק: כל הממשק בעברית

# 5. שגיאות בכוונה
# - חסר מינימום תווים בשדה
# - ניסיון מחיקה עם ביטול
# ✅ בדוק: כל ההודעות בעברית
```

### שלב 4.3: דוח סופי

```markdown
# דוח בדיקה - תרגום עברי
תאריך: [DATE]

סה"כ דפים בדוקים: X
דפים שכל הממשק בעברית: Y
דפים עם בעיות: Z

בעיות שנמצאו:
1. [דוגמה]
2. [דוגמה]

מסקנה: ✅ מוכן ל-Production
או: ⚠️ צריך תיקונים
```

### ✅ Checklist MISSION 4

- [ ] בדוק home page
- [ ] בדוק login/logout
- [ ] בדוק document list
- [ ] בדוק editor
- [ ] בדוק search
- [ ] בדוק import/export
- [ ] בדוק error messages
- [ ] בדוק form validation
- [ ] בדוק success messages
- [ ] כתוב דוח סופי

**סטטוס Mission 4:** ✅ `100% QA completion`

---

## 🎉 FINAL CHECKLIST - תרגום 100%

```
MISSION 1: Django Backend
✅ 242 + 536 = 778 מחרוזות מתורגמות
✅ django.po מקומפל ל-django.mo
✅ כל המחרוזות בעברית

MISSION 2: Vue.js Frontend
✅ he.json יוצר עם 100 מפתחות
✅ Vue i18n עדכן
✅ כל הממשק בעברית

MISSION 3: JavaScript
✅ כל template עם i18n object
✅ כל הודעה בעברית
✅ כל confirmation בעברית

MISSION 4: QA
✅ כל דף בדוק בעברית
✅ כל הודעה שגיאה בעברית
✅ כל טופס בעברית

סה"כ: 100% תרגום ממשק eScriptorium לעברית! 🎉
```

---

## ⏱️ Timeline מעשי

| שלב | מטלה | זמן | ימים |
|-----|--------|------|------|
| 1 | Django extraction | 30 דק | יום 1 |
| 2 | Django translation | 7 שעות | יום 2-3 |
| 3 | Django compilation | 30 דק | יום 4 |
| 4 | Django QA | 1 שעה | יום 4 |
| 5 | Vue.js he.json | 2 שעות | יום 5 |
| 6 | Vue.js config | 1 שעה | יום 5 |
| 7 | Vue.js QA | 1 שעה | יום 5 |
| 8 | JavaScript templates | 2 שעות | יום 6 |
| 9 | JavaScript QA | 1 שעה | יום 6 |
| 10 | Overall QA | 2 שעות | יום 7 |

**סה"כ: ~2 שבועות או 10-18 שעות בעבודה חלקית**

---

**מוכן להתחיל? בואי נלך! 🚀**

