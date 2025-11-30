# מדריך מעשי ליישום תרגום עברי במערכת eScriptorium
## על בסיס ניתוח התרגום הצרפתי

**תאריך:** 5 באוקטובר 2025  
**מטרה:** מדריך צעד אחר צעד ליישום מלא של תרגום עברי

---

## תוכן עניינים
1. [התחלה מהירה](#התחלה-מהירה)
2. [תרחישים מעשיים](#תרחישים-מעשיים)
3. [אוטומציה וכלים](#אוטומציה-וכלים)
4. [בדיקות איכות](#בדיקות-איכות)
5. [פתרון בעיות](#פתרון-בעיות)

---

## 1. התחלה מהירה

### Setup בסיסי (10 דקות)

```bash
# 1. נווט לספריית הפרויקט
cd g:/OCR_Arabic_Testing/BiblIA_dataset-project/BiblIA_dataset/escriptorium

# 2. ודא שיש סביבת Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# או
.\venv\Scripts\activate   # Windows

# 3. התקן תלויות
pip install django gettext

# 4. נווט לספריית האפליקציה
cd app

# 5. צור תרגום עברי חדש
python manage.py makemessages -l he --all

# 6. ערוך את הקובץ
code locale/he/LC_MESSAGES/django.po

# 7. קמפל
python manage.py compilemessages -l he

# 8. הפעל את השרת
python manage.py runserver
```

### בדיקה מהירה

```python
# בדיקה ב-Django shell
python manage.py shell

>>> from django.utils.translation import activate, gettext as _
>>> activate('he')
>>> _('Save')
'שמור'
```

---

## 2. תרחישים מעשיים

### תרחיש 1: הוספת תרגום לפיצ'ר חדש

**סיטואציה:** פיתחת פיצ'ר חדש לייצוא מסמכים ל-PDF

#### שלב 1: כתיבת הקוד עם תמיכה בתרגום

```python
# apps/exports/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

def export_to_pdf(request, document_id):
    """ייצוא מסמך ל-PDF"""
    try:
        document = Document.objects.get(id=document_id)
        
        # ביצוע הייצוא
        pdf_file = generate_pdf(document)
        
        # הודעת הצלחה
        messages.success(
            request,
            _('Document "%(title)s" was exported successfully') % {
                'title': document.title
            }
        )
        
        return redirect('document_list')
        
    except Document.DoesNotExist:
        messages.error(
            request,
            _('Document not found')
        )
        return redirect('document_list')
    
    except Exception as e:
        messages.error(
            request,
            _('Error exporting document: %(error)s') % {
                'error': str(e)
            }
        )
        return redirect('document_list')


def export_multiple(request):
    """ייצוא מספר מסמכים"""
    document_ids = request.POST.getlist('documents')
    count = len(document_ids)
    
    # שימוש בריבוי
    message = ngettext(
        'One document was exported',
        '%(count)d documents were exported',
        count
    ) % {'count': count}
    
    messages.success(request, message)
    return redirect('document_list')
```

#### שלב 2: הוספה לטמפלייט

```django
{# templates/exports/export_form.html #}
{% load i18n %}

<div class="export-panel">
    <h2>{% trans "Export Documents" %}</h2>
    
    <form method="post" action="{% url 'export_pdf' %}">
        {% csrf_token %}
        
        <div class="form-group">
            <label>{% trans "Select documents to export" %}</label>
            {{ form.documents }}
        </div>
        
        <div class="form-group">
            <label>{% trans "Format" %}</label>
            <select name="format">
                <option value="pdf">{% trans "PDF Document" %}</option>
                <option value="alto">{% trans "ALTO XML" %}</option>
                <option value="text">{% trans "Plain Text" %}</option>
            </select>
        </div>
        
        <button type="submit" class="btn btn-primary">
            {% trans "Export" %}
        </button>
    </form>
    
    {% blocktrans count counter=documents.count %}
    You have selected {{ counter }} document.
    {% plural %}
    You have selected {{ counter }} documents.
    {% endblocktrans %}
</div>
```

#### שלב 3: חילוץ מחרוזות לתרגום

```bash
# חילוץ המחרוזות החדשות
cd app
python manage.py makemessages -l he --all

# הקובץ django.po יעודכן אוטומטית עם:
```

```po
#: apps/exports/views.py:15
#, python-format
msgid "Document \"%(title)s\" was exported successfully"
msgstr ""

#: apps/exports/views.py:25
msgid "Document not found"
msgstr ""

#: apps/exports/views.py:32
#, python-format
msgid "Error exporting document: %(error)s"
msgstr ""

#: apps/exports/views.py:45
msgid "One document was exported"
msgid_plural "%(count)d documents were exported"
msgstr[0] ""
msgstr[1] ""

#: templates/exports/export_form.html:5
msgid "Export Documents"
msgstr ""

#: templates/exports/export_form.html:11
msgid "Select documents to export"
msgstr ""

#: templates/exports/export_form.html:16
msgid "Format"
msgstr ""

#: templates/exports/export_form.html:18
msgid "PDF Document"
msgstr ""

#: templates/exports/export_form.html:19
msgid "ALTO XML"
msgstr ""

#: templates/exports/export_form.html:20
msgid "Plain Text"
msgstr ""

#: templates/exports/export_form.html:25
msgid "Export"
msgstr ""
```

#### שלב 4: תרגום לעברית

```po
#: apps/exports/views.py:15
#, python-format
msgid "Document \"%(title)s\" was exported successfully"
msgstr "המסמך \"%(title)s\" יוצא בהצלחה"

#: apps/exports/views.py:25
msgid "Document not found"
msgstr "המסמך לא נמצא"

#: apps/exports/views.py:32
#, python-format
msgid "Error exporting document: %(error)s"
msgstr "שגיאה בייצוא המסמך: %(error)s"

#: apps/exports/views.py:45
msgid "One document was exported"
msgid_plural "%(count)d documents were exported"
msgstr[0] "מסמך אחד יוצא"
msgstr[1] "%(count)d מסמכים יוצאו"

#: templates/exports/export_form.html:5
msgid "Export Documents"
msgstr "ייצוא מסמכים"

#: templates/exports/export_form.html:11
msgid "Select documents to export"
msgstr "בחר מסמכים לייצוא"

#: templates/exports/export_form.html:16
msgid "Format"
msgstr "פורמט"

#: templates/exports/export_form.html:18
msgid "PDF Document"
msgstr "מסמך PDF"

#: templates/exports/export_form.html:19
msgid "ALTO XML"
msgstr "ALTO XML"

#: templates/exports/export_form.html:20
msgid "Plain Text"
msgstr "טקסט רגיל"

#: templates/exports/export_form.html:25
msgid "Export"
msgstr "ייצוא"
```

#### שלב 5: קומפילציה ובדיקה

```bash
# קומפילציה
python manage.py compilemessages -l he

# הפעלת השרת
python manage.py runserver

# בדיקה בדפדפן
# נווט ל: http://localhost:8000/exports/
# שנה שפה לעברית (תפריט למעלה)
# ודא שכל הטקסטים בעברית
```

---

### תרחיש 2: תיקון תרגום קיים

**סיטואציה:** גילית שתרגום הכפתור "Delete" מופיע כ"מחק" אבל צריך להיות "מחיקה"

```bash
# 1. פתח את קובץ התרגום
code locale/he/LC_MESSAGES/django.po

# 2. חפש את הערך (Ctrl+F)
# חפש: msgid "Delete"

# 3. מצא את הבלוק:
#: apps/core/views.py:234
msgid "Delete"
msgstr "מחק"

# 4. תקן:
msgstr "מחיקה"

# 5. שמור וקמפל
python manage.py compilemessages -l he

# 6. רענן את הדפדפן (Ctrl+F5)
```

---

### תרחיש 3: הוספת תרגום Frontend (Vue.js)

**סיטואציה:** רוצה להוסיף כפתור חדש בעורך Vue

#### שלב 1: הוספה לקובץ JSON

```bash
# ערוך את קובץ התרגום
code front/vue/locales/he.json
```

```json
{
  "editor": {
    "toolbar": {
      "export": {
        "button": "ייצוא",
        "tooltip": "ייצא את המסמך הנוכחי",
        "formats": {
          "pdf": "PDF",
          "alto": "ALTO XML",
          "text": "טקסט רגיל"
        }
      }
    }
  }
}
```

#### שלב 2: שימוש ב-Vue Component

```vue
<!-- front/vue/src/components/EditorToolbar.vue -->
<template>
  <div class="toolbar">
    <button 
      @click="exportDocument" 
      :title="$t('editor.toolbar.export.tooltip')"
      class="btn btn-export">
      {{ $t('editor.toolbar.export.button') }}
    </button>
    
    <select v-model="exportFormat" class="format-select">
      <option value="pdf">
        {{ $t('editor.toolbar.export.formats.pdf') }}
      </option>
      <option value="alto">
        {{ $t('editor.toolbar.export.formats.alto') }}
      </option>
      <option value="text">
        {{ $t('editor.toolbar.export.formats.text') }}
      </option>
    </select>
  </div>
</template>

<script>
export default {
  name: 'EditorToolbar',
  data() {
    return {
      exportFormat: 'pdf'
    }
  },
  methods: {
    exportDocument() {
      const message = this.$t('editor.toolbar.export.tooltip');
      this.$notify.success(message);
      // ... קוד ייצוא
    }
  }
}
</script>
```

#### שלב 3: בנייה ובדיקה

```bash
# בנייה
cd front/vue
npm run build

# או במצב פיתוח
npm run serve

# בדיקה בדפדפן
```

---

### תרחיש 4: תרגום הודעות שגיאה

```python
# apps/core/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'language']
        labels = {
            'title': _('Title'),
            'description': _('Description'),
            'language': _('Language'),
        }
        help_texts = {
            'title': _('Enter a descriptive title for your document'),
            'description': _('Optional description'),
        }
        error_messages = {
            'title': {
                'required': _('Please enter a title'),
                'max_length': _('Title is too long (maximum 255 characters)'),
            }
        }
    
    def clean_title(self):
        title = self.cleaned_data['title']
        
        # בדיקות מותאמות אישית
        if len(title) < 3:
            raise forms.ValidationError(
                _('Title must be at least %(min)d characters long'),
                params={'min': 3}
            )
        
        if Document.objects.filter(title=title).exists():
            raise forms.ValidationError(
                _('A document with this title already exists')
            )
        
        return title
```

התרגום:
```po
msgid "Title"
msgstr "כותרת"

msgid "Description"
msgstr "תיאור"

msgid "Language"
msgstr "שפה"

msgid "Enter a descriptive title for your document"
msgstr "הזן כותרת תיאורית למסמך שלך"

msgid "Optional description"
msgstr "תיאור אופציונלי"

msgid "Please enter a title"
msgstr "אנא הזן כותרת"

msgid "Title is too long (maximum 255 characters)"
msgstr "הכותרת ארוכה מדי (מקסימום 255 תווים)"

#, python-format
msgid "Title must be at least %(min)d characters long"
msgstr "הכותרת חייבת להכיל לפחות %(min)d תווים"

msgid "A document with this title already exists"
msgstr "מסמך עם כותרת זו כבר קיים"
```

---

## 3. אוטומציה וכלים

### 3.1 סקריפט לחילוץ תרגומים חסרים

```python
#!/usr/bin/env python3
"""
extract_missing_translations.py
מוצא מחרוזות שחסר להן תרגום
"""

import re
import sys
from pathlib import Path

def find_untranslated(po_file):
    """מוצא ערכים לא מתורגמים"""
    untranslated = []
    
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # פיצול לבלוקים
    blocks = re.split(r'\n\n+', content)
    
    for block in blocks:
        # חיפוש msgid
        msgid_match = re.search(r'^msgid "([^"]+)"', block, re.MULTILINE)
        if not msgid_match:
            continue
            
        msgid = msgid_match.group(1)
        if not msgid.strip():
            continue
        
        # בדיקה אם יש msgstr
        msgstr_match = re.search(r'^msgstr "([^"]*)"', block, re.MULTILINE)
        if msgstr_match:
            msgstr = msgstr_match.group(1)
            if not msgstr.strip():
                # מציאת מיקום בקוד
                location_match = re.search(r'^#: (.+)$', block, re.MULTILINE)
                location = location_match.group(1) if location_match else 'Unknown'
                
                untranslated.append({
                    'msgid': msgid,
                    'location': location,
                    'block': block
                })
    
    return untranslated

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_missing_translations.py <po_file>")
        sys.exit(1)
    
    po_file = Path(sys.argv[1])
    
    if not po_file.exists():
        print(f"Error: File not found: {po_file}")
        sys.exit(1)
    
    print(f"🔍 בודק תרגומים חסרים ב: {po_file}")
    print("=" * 60)
    
    untranslated = find_untranslated(po_file)
    
    print(f"\n📊 נמצאו {len(untranslated)} מחרוזות לא מתורגמות:\n")
    
    for i, item in enumerate(untranslated[:20], 1):  # הצג רק 20 ראשונות
        print(f"{i}. {item['msgid']}")
        print(f"   מיקום: {item['location']}")
        print()
    
    if len(untranslated) > 20:
        print(f"... ועוד {len(untranslated) - 20} מחרוזות נוספות")
    
    # שמירה לקובץ
    output_file = po_file.parent / 'missing_translations.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("מחרוזות חסרות תרגום:\n")
        f.write("=" * 60 + "\n\n")
        for i, item in enumerate(untranslated, 1):
            f.write(f"{i}. {item['msgid']}\n")
            f.write(f"   מיקום: {item['location']}\n\n")
    
    print(f"\n💾 הדוח המלא נשמר ב: {output_file}")

if __name__ == '__main__':
    main()
```

שימוש:
```bash
python extract_missing_translations.py locale/he/LC_MESSAGES/django.po
```

### 3.2 סקריפט לאימות פורמט

```python
#!/usr/bin/env python3
"""
validate_translations.py
בודק תקינות של קבצי תרגום
"""

import re
import sys
from pathlib import Path

def validate_po_file(po_file):
    """בודק תקינות של קובץ .po"""
    errors = []
    warnings = []
    
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # בדיקה 1: קידוד UTF-8
    if 'charset=UTF-8' not in content:
        errors.append("❌ Missing UTF-8 charset declaration")
    
    # בדיקה 2: Plural-Forms
    if 'Plural-Forms' not in content:
        warnings.append("⚠️  Missing Plural-Forms declaration")
    
    # בדיקה 3: בדיקת פורמט placeholders
    blocks = re.split(r'\n\n+', content)
    
    for block in blocks:
        msgid_match = re.search(r'^msgid "([^"]+)"', block, re.MULTILINE)
        msgstr_match = re.search(r'^msgstr "([^"]*)"', block, re.MULTILINE)
        
        if msgid_match and msgstr_match:
            msgid = msgid_match.group(1)
            msgstr = msgstr_match.group(1)
            
            if not msgstr:
                continue  # ריק - זה OK
            
            # חיפוש placeholders
            msgid_placeholders = set(re.findall(r'%\((\w+)\)[sd]', msgid))
            msgstr_placeholders = set(re.findall(r'%\((\w+)\)[sd]', msgstr))
            
            # בדיקה שכל הplaceholders קיימים
            missing = msgid_placeholders - msgstr_placeholders
            if missing:
                location_match = re.search(r'^#: (.+)$', block, re.MULTILINE)
                location = location_match.group(1) if location_match else 'Unknown'
                errors.append(
                    f"❌ Missing placeholders in translation:\n"
                    f"   Location: {location}\n"
                    f"   msgid: {msgid}\n"
                    f"   msgstr: {msgstr}\n"
                    f"   Missing: {missing}"
                )
    
    return errors, warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_translations.py <po_file>")
        sys.exit(1)
    
    po_file = Path(sys.argv[1])
    
    if not po_file.exists():
        print(f"Error: File not found: {po_file}")
        sys.exit(1)
    
    print(f"🔍 מאמת קובץ תרגום: {po_file}")
    print("=" * 60)
    
    errors, warnings = validate_po_file(po_file)
    
    if not errors and not warnings:
        print("\n✅ הקובץ תקין!")
    else:
        if errors:
            print(f"\n❌ נמצאו {len(errors)} שגיאות:\n")
            for error in errors:
                print(error)
                print()
        
        if warnings:
            print(f"\n⚠️  {len(warnings)} אזהרות:\n")
            for warning in warnings:
                print(warning)
                print()
    
    sys.exit(len(errors))

if __name__ == '__main__':
    main()
```

### 3.3 Makefile לאוטומציה

```makefile
# Makefile
.PHONY: help translate extract compile validate clean

help:
	@echo "פקודות זמינות:"
	@echo "  make extract    - חילוץ מחרוזות לתרגום"
	@echo "  make compile    - קומפילציה של תרגומים"
	@echo "  make validate   - אימות תקינות"
	@echo "  make missing    - רשימת תרגומים חסרים"
	@echo "  make clean      - מחיקת קבצים זמניים"

extract:
	@echo "📝 מחלץ מחרוזות לתרגום..."
	cd app && python manage.py makemessages -l he --all --add-location file
	@echo "✅ הושלם!"

compile:
	@echo "🔨 מקמפל תרגומים..."
	cd app && python manage.py compilemessages -l he
	@echo "✅ הושלם!"

validate:
	@echo "🔍 מאמת תקינות..."
	python scripts/validate_translations.py app/locale/he/LC_MESSAGES/django.po

missing:
	@echo "📋 מחפש תרגומים חסרים..."
	python scripts/extract_missing_translations.py app/locale/he/LC_MESSAGES/django.po

clean:
	@echo "🧹 מנקה קבצים זמניים..."
	find app/locale -name "*.mo" -delete
	find app/locale -name "*~" -delete
	@echo "✅ הושלם!"

translate: extract compile
	@echo "✅ תהליך תרגום הושלם!"
```

שימוש:
```bash
make extract   # חילוץ
make compile   # קומפילציה
make validate  # אימות
make missing   # חיפוש חסרים
```

---

## 4. בדיקות איכות

### 4.1 בדיקות אוטומטיות

```python
# tests/test_translations.py
from django.test import TestCase
from django.utils.translation import activate, gettext as _

class TranslationTests(TestCase):
    def test_hebrew_translations_exist(self):
        """בודק שתרגומים עבריים קיימים"""
        activate('he')
        
        # בדיקות בסיסיות
        self.assertNotEqual(_('Save'), 'Save')
        self.assertNotEqual(_('Cancel'), 'Cancel')
        self.assertNotEqual(_('Delete'), 'Delete')
    
    def test_placeholders_work(self):
        """בודק ש-placeholders עובדים"""
        activate('he')
        
        text = _('You have %(count)d documents') % {'count': 5}
        self.assertIn('5', text)
        self.assertNotIn('%(count)d', text)
    
    def test_plural_forms(self):
        """בודק צורות ריבוי"""
        from django.utils.translation import ngettext
        activate('he')
        
        # יחיד
        text = ngettext('one document', '%d documents', 1) % 1
        self.assertIn('אחד', text)  # צריך להכיל "אחד"
        
        # רבים
        text = ngettext('one document', '%d documents', 5) % 5
        self.assertIn('5', text)
```

הרצה:
```bash
python manage.py test tests.test_translations
```

### 4.2 בדיקות ידניות - Checklist

```markdown
## Checklist לבדיקת תרגומים

### Backend (Django)
- [ ] כל הטפסים מתורגמים
- [ ] הודעות שגיאה מתורגמות
- [ ] תפריטים וכפתורים מתורגמים
- [ ] Email templates מתורגמים
- [ ] הודעות flash מתורגמות

### Frontend (Vue.js)
- [ ] UI components מתורגמים
- [ ] Tooltips מתורגמים
- [ ] Notifications מתורגמות
- [ ] Modals מתורגמות
- [ ] Error messages מתורגמות

### כיוון (RTL)
- [ ] טקסט מיושר ימינה
- [ ] תפריטים נפתחים בכיוון נכון
- [ ] Modals ממורכזות
- [ ] Forms מיושרות ימינה
- [ ] Icons בצד הנכון

### Placeholders
- [ ] כל הplaceholders פועלים
- [ ] אין %(var)s בטקסט מוצג
- [ ] מספרים מוצגים נכון
- [ ] תאריכים מוצגים בפורמט נכון

### צורות ריבוי
- [ ] יחיד/רבים עובד
- [ ] אפס מטופל נכון
- [ ] מספרים גדולים מטופלים נכון
```

---

## 5. פתרון בעיות

### בעיה 1: תרגום לא מוצג

**תסמינים:**
- הטקסט באנגלית למרות שבחרת עברית
- השפה מתחלפת חזרה לאנגלית

**פתרון:**

```bash
# 1. בדוק שהקומפילציה הצליחה
python manage.py compilemessages -l he
# אמור להראות: processing file django.po in locale/he/LC_MESSAGES

# 2. בדוק שקובץ .mo קיים
ls -la app/locale/he/LC_MESSAGES/django.mo

# 3. אתחל את Django
docker-compose restart web

# 4. נקה cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# 5. בדוק בדפדפן
# נקה cookies
# רענן עמוד (Ctrl+Shift+R)
```

### בעיה 2: תווים מקולקלים (���)

**תסמינים:**
- תווים עבריים מוצגים כ-???? או ���
- בעיות קידוד

**פתרון:**

```bash
# 1. בדוק קידוד הקובץ
file locale/he/LC_MESSAGES/django.po
# צריך להראות: UTF-8 Unicode text

# 2. אם לא UTF-8, המר:
iconv -f ISO-8859-8 -t UTF-8 django.po > django_utf8.po
mv django_utf8.po django.po

# 3. ודא בheader:
"Content-Type: text/plain; charset=UTF-8\n"

# 4. קמפל מחדש
python manage.py compilemessages -l he
```

### בעיה 3: Placeholder לא עובד

**תסמינים:**
- רואה `%(count)d` בטקסט המוצג
- שגיאה: KeyError: 'count'

**פתרון:**

```python
# ❌ שגוי
text = _('You have %(count)d documents')

# ✅ נכון
text = _('You have %(count)d documents') % {'count': 5}

# ✅ בtemplate
{% blocktrans count counter=documents.count %}
You have {{ counter }} documents.
{% endblocktrans %}
```

### בעיה 4: RTL לא עובד

**תסמינים:**
- טקסט עברי מיושר שמאלה
- UI נראה הפוך

**פתרון:**

```python
# הוסף ל-settings.py
LANGUAGES_BIDI = ["he", "ar", "fa"]
```

```html
<!-- בtemplate בסיסי -->
{% load i18n %}
<!DOCTYPE html>
<html dir="{% if LANGUAGE_BIDI %}rtl{% else %}ltr{% endif %}" 
      lang="{{ LANGUAGE_CODE }}">
<head>
    {% if LANGUAGE_BIDI %}
    <link rel="stylesheet" href="{% static 'css/rtl.css' %}">
    {% endif %}
</head>
```

```css
/* rtl.css */
[dir="rtl"] {
    text-align: right;
}

[dir="rtl"] .navbar {
    flex-direction: row-reverse;
}

[dir="rtl"] .sidebar {
    right: 0;
    left: auto;
}
```

### בעיה 5: פורמט תאריכים לא נכון

**תסמינים:**
- תאריכים בפורמט אמריקאי (MM/DD/YYYY)
- שעות לא בזמן ישראל

**פתרון:**

```python
# settings.py
LANGUAGE_CODE = 'he'
TIME_ZONE = 'Asia/Jerusalem'
USE_I18N = True
USE_L10N = True  # חשוב!
USE_TZ = True

# בtemplate
{% load l10n %}
{{ document.created_at|localize }}
```

---

## סיכום

### Workflow מומלץ לפיתוח יומיומי:

1. **כתוב קוד עם תרגום:**
   ```python
   from django.utils.translation import gettext as _
   message = _("Your text here")
   ```

2. **חלץ מחרוזות:**
   ```bash
   make extract
   ```

3. **תרגם:**
   ```bash
   code locale/he/LC_MESSAGES/django.po
   ```

4. **קמפל:**
   ```bash
   make compile
   ```

5. **בדוק:**
   ```bash
   make validate
   docker-compose restart web
   ```

### Tips לתרגום טוב:

✅ **DO:**
- השתמש תמיד ב-`gettext_lazy` ב-models ו-forms
- הוסף הערות למתרגמים: `#. Translators: ...`
- בדוק placeholders
- בדוק צורות ריבוי
- תרגם error messages

❌ **DON'T:**
- אל תשרשר מחרוזות: `_("Hello") + name`
- אל תחלק משפטים: `_("You have") + count + _("documents")`
- אל תשכח לקמפל
- אל תתרגם קוד או HTML
- אל תשתמש ב-hardcoded strings

---

**סוף המדריך המעשי**

*נוצר ב-5 באוקטובר 2025*  
*GitHub Copilot - AI Assistant*
