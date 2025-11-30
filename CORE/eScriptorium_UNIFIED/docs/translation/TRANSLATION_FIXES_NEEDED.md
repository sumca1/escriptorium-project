# Translation Fixes Report - דוח תיקוני תרגום
# Generated: 2025-10-19

## 🔴 CRITICAL: 11 Strings Exist in .po but Not Displayed

These translations EXIST but are not being used by the templates!
This is a **code issue**, not a translation issue.

### Problem: JavaScript or Missing {% trans %} Tags

**Affected String:**
- "Overwrite existing model file" → "דרוס קובץ מודל קיים" ✅ (IN .PO)

**Locations to Check:**
1. `app/apps/imports/templates/` - Import forms
2. `app/apps/core/templates/` - Base templates  
3. JavaScript files in `front/` - Dynamic content

### Action Items:

#### 1. Check Templates for {% trans %} Usage
Search for these files and verify they use translation tags:

```bash
# Find templates with "Overwrite existing model file"
grep -r "Overwrite existing model file" app/apps/*/templates/

# Check if they use {% trans %}
grep -B2 -A2 "Overwrite existing model" app/apps/*/templates/*.html
```

#### 2. Fix Template Examples

**WRONG:**
```django
<label>Overwrite existing model file</label>
```

**CORRECT:**
```django
{% load i18n %}
<label>{% trans "Overwrite existing model file" %}</label>
```

#### 3. Check JavaScript Files

If content is added via JavaScript, it won't use Django translations.

**Files to check:**
- `front/src/` - All .js files
- Look for: `innerHTML = "Overwrite existing model file"`

**Fix:** Use Django's JavaScript catalog:
```javascript
// In template:
{% load i18n %}
<script src="{% url 'javascript-catalog' %}"></script>

// In JavaScript:
const text = gettext("Overwrite existing model file");
```

---

## 🟡 MEDIUM: 29 Strings with Partial Matches

These are compound sentences that need to be added as complete strings.

### Examples:

**1. "Override existing segmentation"**
- Currently only "Segment" is translated
- Need to add full string to .po:

```po
msgid "Override existing segmentation"
msgstr "דרוס פילוח קיים"
```

**2. "Auto Process (Recommended)"**
```po
msgid "Auto Process (Recommended)"
msgstr "עיבוד אוטומטי (מומלץ)"
```

**3. "Denoise - Remove noise from image"**
```po
msgid "Denoise - Remove noise from image"
msgstr "הסרת רעש - הסר רעש מהתמונה"
```

**4. "Deskew - Auto-rotate to correct orientation"**
```po
msgid "Deskew - Auto-rotate to correct orientation"
msgstr "יישור - סיבוב אוטומטי לכיוון נכון"
```

**5. "Enhance Contrast - CLAHE enhancement"**
```po
msgid "Enhance Contrast - CLAHE enhancement"
msgstr "שיפור ניגודיות - שיפור CLAHE"
```

**6. "Binarize - Convert to black and white"**
```po
msgid "Binarize - Convert to black and white"
msgstr "בינריזציה - המרה לשחור-לבן"
```

### Action:

```bash
# Add these to django.po manually, then compile:
cd app
python manage.py compilemessages
docker-compose restart web
```

---

## ❌ LOW: 5 Missing Strings

These don't exist in .po at all:

```po
# Add to app/locale/he/LC_MESSAGES/django.po:

msgid "Kraken OCR Engine"
msgstr "מנוע Kraken OCR"

msgid "IIIF manifest URI"
msgstr "כתובת IIIF Manifest"

msgid "Users mailing list"
msgstr "רשימת תפוצה למשתמשים"

msgid "Advanced Hebrew OCR & HTR Platform for Historical Manuscripts"
msgstr "פלטפורמה מתקדמת ל-OCR ו-HTR עברי לכתבי יד היסטוריים"
```

---

## 🔧 Implementation Steps

### Step 1: Find Problem Templates
```bash
cd app
grep -r "Overwrite existing model file" apps/*/templates/
```

### Step 2: Check for {% load i18n %}
```bash
grep -L "{% load i18n %}" apps/*/templates/*.html
```

### Step 3: Add Missing Translations
Edit: `app/locale/he/LC_MESSAGES/django.po`

Add all the translations from the sections above.

### Step 4: Recompile
```bash
cd app
python manage.py compilemessages
```

### Step 5: Restart Django
```bash
docker-compose restart web
```

### Step 6: Clear Browser Cache
The translations are cached! Clear cache or hard refresh (Ctrl+F5)

---

## 📋 Priority Order

1. **🔴 CRITICAL:** Fix the 11 strings that exist but don't show
   - Check templates for {% trans %} tags
   - Check JavaScript for dynamic content
   
2. **🟡 MEDIUM:** Add 29 compound sentences to .po
   - Edit django.po
   - Add complete sentences with translations
   
3. **❌ LOW:** Add 5 completely missing strings
   - Simple additions to .po file

---

## 🎯 Expected Results After Fixes

- **Before:** 69.8% Hebrew content, 82.4% UI Hebrew
- **After:** 85%+ Hebrew content, 95%+ UI Hebrew

The main issue is NOT missing translations, but rather:
1. Templates not using {% trans %} (11 strings)
2. Complete sentences not marked for translation (29 strings)
