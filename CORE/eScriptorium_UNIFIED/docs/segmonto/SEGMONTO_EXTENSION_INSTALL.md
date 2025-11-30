# 🔧 התקנת SegmOnto Browser Extension v1.1

**גרסה:** 1.1 (רשמית מ-HTR-United)  
**תאריך:** 26 אוקטובר 2025  
**ממקום:** `segmonto-official/`

---

## 📋 שלבי התקנה

### ✅ דרך 1: Chrome / Edge / Brave (תומכים Manifest V3)

#### שלב 1: פתח Extensions Page
```
Chrome:  chrome://extensions/
Edge:    edge://extensions/
Brave:   brave://extensions/
```

#### שלב 2: הפעל Developer Mode
- פינה ימנית עליונה
- לחץ על המתג: **"Developer mode"** 
- צבע: כחול/כתום = מופעל ✅

#### שלב 3: Load Unpacked
- לחץ כפתור: **"Load unpacked"**
- בחר תיקייה: 
  ```
  G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\segmonto-official\
  ```

#### שלב 4: אישור
- התוסף יופיע ברשימה
- שם: "eScriptorium Segmonto Live Checker"
- סמל: ✓ בעיגול
- סטטוס: "Loaded unpacked"

---

## 🦊 דרך 2: Firefox (Temporary)

#### שלב 1: פתח about:debugging
```
סרגל כתובת: about:debugging
או: about:debugging#/runtime/this-firefox
```

#### שלב 2: לחץ "This Firefox"
בצד שמאל: **"This Firefox"**

#### שלב 3: Load Temporary Add-on
כפתור: **"Load Temporary Add-on..."**

#### שלב 4: בחר את manifest.json
```
G:\...\segmonto-official\manifest.json
```

#### שלב 5: אישור
- התוסף יופיע ברשימה
- סטטוס: "Temporary extension"

---

## 🔍 בדיקה שהתוסף נטען:

### Chrome/Edge:
- ✅ סמל ✓ בתפריט הימני (ליד שורת הכתובת)
- ✅ כתוב "eScriptorium Segmonto Live Checker"
- ✅ בחלון Extensions - סטטוס: "Enabled"

### Firefox:
- ✅ סמל ✓ בתפריט הימני
- ✅ כתוב "eScriptorium Segmonto Live Checker"
- ✅ בדף about:debugging - "Temporary extension"

---

## 🚀 איך להשתמש:

### שלב 1: גש ל-eScriptorium
```
http://localhost:8082/document/16/part/251/edit/
```

### שלב 2: לחץ על סמל SegmOnto
- בתפריט הימני (ליד שורת הכתובת)
- או בחלון פופ-אפ

### שלב 3: הזן Token (אם נדרש)
- Token: ניתן להשיג מ-eScriptorium Settings
- או: פשוט לחץ "Check" בלי token

### שלב 4: בדוק תוצאות
- Overall Status
- Regions validity
- Lines validity
- Errors list

---

## 📊 מה התוסף בודק?

### ✅ SegmOnto Valid Zones:
```
CustomZone, DamageZone, GraphicZone, DigitizationArtefactZone,
DropCapitalZone, MainZone, MarginTextZone, MusicZone,
NumberingZone, QuireMarksZone, RunningTitleZone, SealZone,
StampZone, TableZone, TitlePageZone
```

### ✅ SegmOnto Valid Lines:
```
CustomLine, DefaultLine, DropCapitalLine, HeadingLine,
InterlinearLine, MusicLine
```

### ❌ סוגים לא חוקיים:
```
RandomZone, FooLine, WeirdType  → ❌ Error
```

---

## 🎨 התוסף יראה כך:

```
Popup Window:
┌─────────────────────────────────────────┐
│ eScriptorium Segmonto Live Checker     │
├─────────────────────────────────────────┤
│                                         │
│ URL: http://localhost:8082/document... │
│ Auth Token: [____________]              │
│                                         │
│ [Check Document] [Check Current Page]  │
│                                         │
│ Results:                                │
│ ✅ 12/14 Regions are OK                 │
│ ✅ 8/9 Lines are OK                     │
│                                         │
│ ❌ Region 5: Invalid type "WeirdZone"  │
│ ⚠️  Line 3: No typology assigned        │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### ❌ "התוסף לא מופיע"
1. בדוק: Developer Mode **מופעל**?
2. בדוק: הנתיב נכון? 
   ```
   G:\...\segmonto-official\manifest.json צריך להיות שם
   ```
3. נסה: Reload (סמל ⟳ ב-Extensions)

### ❌ "Manifest error"
1. בדוק: קובץ `manifest.json` קיים?
2. בדוק: JSON תקין? (אין typos)
3. פתרון: הורד מחדש מ-Release

### ❌ "Permission denied"
1. בדוק: התוסף בצבע אפור?
2. פתרון: לחץ "Enable" (או סמל 🔘)

### ❌ "Chrome can't load"
1. סגור chrome לחלוטין
2. מחק folder: `C:\Users\...\AppData\Local\Google\Chrome\User Data\Extensions`
3. פתח chrome מחדש
4. נסה Load Unpacked שוב

---

## 📦 גרסה Signed (אם רוצה)

**עבור Firefox בצורה קבועה (לא temporary):**

התוסף צריך להיות חתום (signed) על ידי Mozilla.

**כרגע:** זה Temporary עד שתסגור את Firefox.

**חלופה:** השתמש בWebExt לpacking:
```bash
npm install -g web-ext
web-ext build --source-dir segmonto-official/
```

---

## ✅ Checklist:

```
☐ הורדתי Release 1.1 (✓ יש לנו)
☐ פתחתי Extensions Page
☐ הפעלתי Developer Mode
☐ לחצתי "Load unpacked"
☐ בחרתי segmonto-official/
☐ התוסף הופיע ברשימה
☐ סמל SegmOnto מופיע בתפריט
☐ נסיתי לחצות על הסמל
☐ Popup נפתח
```

---

## 🎯 הצעד הבא:

1. **בדוק שהתוסף עובד:**
   - לחץ על סמל SegmOnto
   - צריך להיפתח popup

2. **אם popup לא מופיע:**
   - בדוק console (F12)
   - חפש errors

3. **אם popup מופיע:**
   - הזן URL של eScriptorium
   - הזן token (אם יש)
   - לחץ "Check Document"
   - צריך לראות תוצאות

---

**סטטוס:** ✅ התוסף הרשמי 1.1 מוכן להתקנה!  
**צעד הבא:** בצע את ההתקנה בדפדפן שלך 🚀
