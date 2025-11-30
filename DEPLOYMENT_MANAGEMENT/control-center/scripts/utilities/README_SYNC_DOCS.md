# 📚 סנכרון מסמכי תיעוד לדשבורד
**Sync Documentation Files to Dashboard**

---

## 🎯 מטרה

סקריפט זה מסנכרן אוטומטית את קבצי התיעוד הראשיים מהפרויקט לדשבורד:
- `SESSION_LOG.md` - תיעוד סשנים
- `CURRENT_STATE.md` - מצב נוכחי של הפרויקט

---

## 🚀 שימוש

### סנכרון חד-פעמי
```powershell
.\sync-docs-to-dashboard.ps1
```

### סנכרון עם פלט מפורט
```powershell
.\sync-docs-to-dashboard.ps1 -Verbose
```

### כפה סנכרון (גם אם אין שינויים)
```powershell
.\sync-docs-to-dashboard.ps1 -Force
```

### מצב מעקב אוטומטי (Watch Mode)
```powershell
.\sync-docs-to-dashboard.ps1 -Watch
```
**במצב זה הסקריפט ימשיך לרוץ ויסנכרן אוטומטית כל שינוי!**

---

## ⚙️ אינטגרציה אוטומטית

הסקריפט רץ **אוטומטית** בכל פעם ש-`START_DASHBOARD.bat` מופעל!

זה אומר:
- ✅ כל פעם שאתה מפעיל את הדשבורד, המסמכים מסונכרנים
- ✅ אתה תמיד רואה את המידע העדכני ביותר
- ✅ אין צורך להריץ ידנית

---

## 📂 נתיבים

| קובץ | מקור | יעד |
|------|------|-----|
| `SESSION_LOG.md` | `BiblIA_dataset\SESSION_LOG.md` | `control-center\docs\SESSION_LOG.md` |
| `CURRENT_STATE.md` | `BiblIA_dataset\CURRENT_STATE.md` | `control-center\docs\CURRENT_STATE.md` |

---

## 🔍 איך זה עובד?

1. **בדיקת שינויים** - הסקריפט משווה hash (גודל + תאריך) של הקבצים
2. **סנכרון חכם** - מעתיק רק אם יש שינויים (חוסך זמן)
3. **יצירת תיקיות** - אם `docs/` לא קיימת, היא נוצרת אוטומטית
4. **דיווח מפורט** - מספר כמה קבצים סונכרנו ודולגו

---

## 🎨 דוגמאות פלט

### סנכרון מוצלח
```
📚 מסנכרן מסמכי תיעוד לדשבורד...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 מעבד קבצים...
  ✅ SESSION_LOG.md סונכרן (273.54 KB)
  ✅ CURRENT_STATE.md סונכרן (35.58 KB)

📊 סיכום:
  ✅ סונכרנו:    2
  ⏭️  דולגו:      0

✨ סיום!
```

### אין שינויים
```
📚 מסנכרן מסמכי תיעוד לדשבורד...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 מעבד קבצים...
  ⏭️  SESSION_LOG.md - ללא שינויים
  ⏭️  CURRENT_STATE.md - ללא שינויים

📊 סיכום:
  ✅ סונכרנו:    0
  ⏭️  דולגו:      2

✨ סיום!

💡 טיפ: כדי לעקוב אחר שינויים באופן אוטומטי, הרץ:
   .\sync-docs-to-dashboard.ps1 -Watch
```

---

## 🛠️ פרמטרים

| פרמטר | תיאור | דוגמה |
|-------|-------|-------|
| `-Watch` | מצב מעקב רציף - עוקב אחר שינויים בזמן אמת | `.\sync-docs-to-dashboard.ps1 -Watch` |
| `-Force` | כפה סנכרון גם אם אין שינויים | `.\sync-docs-to-dashboard.ps1 -Force` |
| `-Verbose` | הצג מידע מפורט (נתיבים, פרטים) | `.\sync-docs-to-dashboard.ps1 -Verbose` |

ניתן לשלב פרמטרים:
```powershell
.\sync-docs-to-dashboard.ps1 -Watch -Verbose
```

---

## 📝 הערות חשובות

### מתי צריך להריץ ידנית?

רק אם:
1. 🔄 ערכת `SESSION_LOG.md` או `CURRENT_STATE.md` **בזמן שהדשבורד פתוח**
2. 💾 רוצה לוודא שהשינויים מופיעים **מיד** בלי לסגור את הדשבורד

**פתרון:** הרץ `.\sync-docs-to-dashboard.ps1` ואז רענן את הדף (F5)

### מצב Watch - מתי להשתמש?

אם אתה **עובד על המסמכים** ורוצה לראות שינויים **בזמן אמת** בדשבורד:
```powershell
.\sync-docs-to-dashboard.ps1 -Watch
```

השאר את הטרמינל פתוח והוא יסנכרן אוטומטית כל שינוי!

---

## 🐛 פתרון בעיות

### שגיאה: "קובץ מקור לא קיים"
**בעיה:** `SESSION_LOG.md` או `CURRENT_STATE.md` לא נמצאים בשורש הפרויקט.

**פתרון:**
```powershell
# בדוק אם הקבצים קיימים
Test-Path "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\SESSION_LOG.md"
Test-Path "I:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\CURRENT_STATE.md"
```

### הסקריפט לא רץ אוטומטית
**בעיה:** `START_DASHBOARD.bat` לא מריץ את הסנכרון.

**פתרון:** ודא ש-Execution Policy מאפשרת הרצת סקריפטים:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

---

## 📊 לוגים

הסקריפט לא יוצר קבצי לוג, אבל אפשר להפנות פלט לקובץ:
```powershell
.\sync-docs-to-dashboard.ps1 -Verbose | Tee-Object -FilePath "sync-log.txt"
```

---

## 🔗 קבצים קשורים

- `START_DASHBOARD.bat` - מריץ את הסנכרון אוטומטית
- `dashboard-server.js` - שרת הדשבורד (מגיש מ-`docs/`)
- `data-loader.js` - טוען את המסמכים בדשבורד

---

**גרסה:** 1.0  
**תאריך:** 13 נובמבר 2025  
**מחבר:** BiblIA Dashboard Team
