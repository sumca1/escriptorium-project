# שגיאות Vue i18n - אל תחזרו עליהן!

## ❌ שגיאה #1: מרכאות מוקפאות מסקריפט Python

### מה קרה:
```python
# סקריפט Python
replacements = [
    (r'label="Text"', r':label="$t(\'Text\')"'),
]
```

### מה זה יצר:
```vue
:label="$t(\'Text\')"  <!-- ❌ מרכאות מוקפאות -->
```

### למה זה בעיה:
Vue template parser רואה את `\'` כ-escape sequence ולא כמרכאה רגילה.

### ✅ פתרון:
```python
# אופציה 1: מרכאות כפולות
replacements = [
    (r'label="Text"', r':label="$t(\"Text\")"'),
]

# אופציה 2: שרשור מחרוזות
replacements = [
    (r'label="Text"', r':label="$t(' + "'" + r'Text' + "'" + r')"'),
]
```

---

## ❌ שגיאה #2: מרכאות כפולות בתוך $t()

### מה קרה:
```vue
:label="$t(\"Import\")"  <!-- ❌ -->
```

### שגיאת Webpack:
```
ERROR: <template v-slot> can only appear at the root level
```

(שגיאה מטעה - הבעיה האמיתית היא במרכאות!)

### למה זה בעיה:
Vue 2 template parser מצפה למרכאות **יחידות** בתוך expressions.

### ✅ פתרון:
```vue
:label="$t('Import')"  <!-- ✅ מרכאות יחידות -->
```

---

## ❌ שגיאה #3: שכחנו binding דינמי (:)

### מה קרה:
```vue
label="$t('Text')"  <!-- ❌ חסר : -->
```

### למה זה בעיה:
בלי `:` Vue רואה את זה כ-string literal `"$t('Text')"` ולא כ-expression!

### ✅ פתרון:
```vue
:label="$t('Text')"  <!-- ✅ עם : לפני -->
```

---

## 📋 Checklist למניעת שגיאות

בודקים לפני commit:

- [ ] כל ה-`$t()` עם **מרכאות יחידות** `'`
- [ ] כל attribute עם `$t()` מתחיל ב-**`:`**
- [ ] אין escape sequences (`\'` או `\"`)
- [ ] Build הצליח: `npm run build`
- [ ] ESLint עבר בלי שגיאות
- [ ] Test בדפדפן עם Ctrl+F5

---

## 🔍 איך לזהות שגיאות מוקדם

### 1. בדוק בעורך קוד:
- מרכאות צריכות להיות בצבע **ירוק/כחול**
- אם הן באדום = בעיה!

### 2. הרץ ESLint:
```bash
cd front
npm run lint
```

### 3. בנה לפני push:
```bash
npm run build
# צריך להגיד: "compiled successfully"
```

---

## 💡 Regex הנכון לעתיד

### למצוא hardcoded strings:
```python
# מוצא label="Text" (ללא : או $t)
pattern = r'label="([^"]+)"(?!\s*:)'
```

### להחליף בצורה נכונה:
```python
# אופציה 1: עם double quotes
pattern = r'label="([^"]+)"'
replacement = r':label="$t(\"\1\")"'

# אחרי זה להפוך double ל-single:
pattern2 = r'\$t\(\"([^"]+)\"\)'
replacement2 = r"$t('\1')"
```

### או ישר עם single quotes:
```python
pattern = r'label="([^"]+)"'
replacement = r":label=\"$t('\1')\""
```

---

## 🧪 Test Case לוודא שהכל עובד

```vue
<!-- ✅ נכון -->
<Button :label="$t('Click me')" />
<h1>{{ $t('Title') }}</h1>
<input :placeholder="$t('Enter text')" />

<!-- ❌ שגוי -->
<Button label="$t('Click me')" />  <!-- חסר : -->
<Button :label="$t(\"Click me\")" />  <!-- double quotes -->
<Button :label="$t(\'Click me\')" />  <!-- escaped quotes -->
<h1>$t('Title')</h1>  <!-- חסר {{ }} -->
```

---

**זכרו**: Vue 2 קפדני מאוד על syntax. בדקו כל שינוי!
