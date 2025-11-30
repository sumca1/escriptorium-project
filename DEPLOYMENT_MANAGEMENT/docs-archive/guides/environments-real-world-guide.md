# 🌍 מדריך סביבות עבודה - איך זה באמת עובד?

## 🎯 העיקרון המרכזי

**SOURCE/ אחד → 3 סביבות שונות → כל אחת עם מטרה אחרת**

```
SOURCE/ (הקוד שלך - המקור האמיתי)
   ↓
   ├─→ dev/     (פיתוח מהיר - רואה שינויים מיידית)
   ├─→ test/    (בדיקות - build קפוא)
   └─→ prod/    (ייצור - אופטימלי ויציב)
```

---

## 📊 השוואה מפורטת: 3 הסביבות

| תכונה | 🟢 dev | 🟡 test | 🔴 prod |
|-------|--------|---------|---------|
| **מטרה** | לכתוב קוד מהר | לבדוק שהכל עובד | אתר חי לייצור |
| **קוד** | מחובר ישירות ל-SOURCE/ | עותק קפוא | עותק קפוא |
| **שינוי קובץ** | רואה מיד ללא build | צריך build מחדש | צריך build מחדש |
| **Build זמן** | **0 שניות** ⚡ | 2-3 דקות | 5-7 דקות |
| **npm** | `install` (מהיר) | `ci` (deterministic) | `ci --production` (קטן) |
| **Hot Reload** | ✅ כן | ❌ לא | ❌ לא |
| **Debug** | ✅ כן | בינוני | ❌ לא |
| **Optimization** | ❌ לא | בינוני | ✅ מלא |
| **Security** | ❌ לא | בינוני | ✅ כן |
| **גודל Image** | גדול | בינוני | קטן |
| **זיכרון** | הרבה | בינוני | מעט |
| **Port** | 8000 | 8001 | 8082 |

---

## 🟢 סביבה 1: dev (פיתוח)

### 🎯 מתי להשתמש?

**כל יום, כל הזמן, זה בית שלך!** 🏠

- כותב קוד חדש
- מתקן bugs
- מנסה features חדשים
- Debug
- ניסויים

### 🔧 איך זה עובד?

```yaml
# dev/docker-compose.yml
services:
  web:
    volumes:
      - ../../SOURCE/app:/usr/src/app:cached  # ← קישור ישר!
      - ../../SOURCE/front:/usr/src/front:cached
```

**המשמעות:**
- הקוד שלך ב-`SOURCE/` **מחובר ישירות** לcontainer
- כל שינוי שאתה שומר **נראה מיד** בcontainer
- **אין צורך ב-build!** ⚡

### 📝 דוגמה מעשית:

```powershell
# יום רגיל בעבודה:

# 1️⃣ הפעלה ראשונה (פעם ביום)
.\SCRIPTS\switch-environment.ps1 -Environment dev -Up
# Build: 2-3 דקות (רק פעם אחת!)

# 2️⃣ עבודה
code SOURCE/app/views.py

# מוסיף שורה:
def my_new_feature(request):
    return JsonResponse({"status": "working!"})

# Ctrl+S (שמירה)

# 3️⃣ רענון דפדפן
# http://localhost:8000/my-new-feature
# ✅ עובד מיד! ללא build!

# 4️⃣ מצאת bug? תקן
def my_new_feature(request):
    return JsonResponse({"status": "fixed!"})  # ← תיקון

# Ctrl+S

# 5️⃣ רענון דפדפן
# ✅ התיקון חי!

# זמן למחזור: 5 שניות
```

### ⚡ יתרונות:

- 🚀 **מהיר** - אין build!
- 🔄 **Hot Reload** - רואה שינויים מיד
- 🐛 **Debug קל** - לוגים ישירים
- 💻 **נוח לפיתוח** - כמו לעבוד מקומית

### ⚠️ חסרונות:

- 🐌 **איטי בריצה** - אין optimization
- 📦 **Image גדול** - כל dependencies
- 🔓 **לא מאובטח** - DEBUG=True
- ⚠️ **לא מייצג ייצור** - התנהגות שונה

---

## 🟡 סביבה 2: test (בדיקות)

### 🎯 מתי להשתמש?

**לפני deploy - לוודא שהכל עובד!** ✅

- סיימת feature → בדיקה
- לפני merge ל-main
- CI/CD pipeline
- בדיקות אינטגרציה

### 🔧 איך זה עובד?

```yaml
# test/docker-compose.yml
services:
  web:
    build:
      context: ../../SOURCE  # ← בונה מ-SOURCE
    # אין volumes של קוד! רק media/logs
```

**המשמעות:**
- הקוד **מועתק** פעם אחת ב-build
- השינויים שלך **לא נראים** עד build הבא
- כמו **snapshot** של הקוד

### 📝 דוגמה מעשית:

```powershell
# תרחיש: סיימתי feature חדשה

# 1️⃣ עבדתי ב-dev
# (כתבתי 100 שורות קוד ב-SOURCE/app/views.py)

# 2️⃣ לפני commit - בדיקה ב-test
.\SCRIPTS\switch-environment.ps1 -Environment test -Build -Up
# Build: 2-3 דקות
# יוצר image עם הקוד הנוכחי

# 3️⃣ הרצת בדיקות
cd ENVIRONMENTS/test
docker-compose exec web pytest
# ✅ כל הבדיקות עברו!

# 4️⃣ בדיקה ידנית
# http://localhost:8001
# ✅ הfeature עובד!

# 5️⃣ מצאתי bug קטן ב-test
code SOURCE/app/views.py
# תיקנתי את הבאג

# 6️⃣ צריך build מחדש כדי לראות תיקון!
.\SCRIPTS\switch-environment.ps1 -Environment test -Build -Up
# Build: 2-3 דקות
# עכשיו הimage כולל את התיקון

# 7️⃣ בדיקה שוב
# http://localhost:8001
# ✅ הבאג תוקן!

# 8️⃣ כל הבדיקות עברו → commit + push!
```

### ⚡ יתרונות:

- ✅ **מייצג ייצור** - התנהגות דומה
- 🧪 **טסטים מהימנים** - סביבה נקייה
- 📸 **Snapshot** - קוד קפוא
- 🔒 **יציב** - לא משתנה בזמן בדיקה

### ⚠️ חסרונות:

- ⏱️ **Build לוקח זמן** - 2-3 דקות
- 🔄 **צריך rebuild** - לכל שינוי
- 💾 **Image בינוני** - לא מינימלי

---

## 🔴 סביבה 3: prod (ייצור)

### 🎯 מתי להשתמש?

**האתר האמיתי! משתמשים אמיתיים!** 🌐

- deploy לייצור
- משתמשים ניגשים לאתר
- 24/7 uptime
- ביצועים מקסימליים

### 🔧 איך זה עובד?

```dockerfile
# prod/Dockerfile
FROM python:3.8-slim

# Optimized build
RUN pip install --no-cache-dir ...
RUN npm ci --production  # רק dependencies מינימליים
RUN npm run build && rm -rf node_modules  # מחק אחרי build!

# Security
USER escriptorium  # לא root!
```

**המשמעות:**
- Build **מאופטמל מלא**
- Image **קטן ומהיר**
- **אין debug tools**
- **מאובטח** - user לא-root

### 📝 דוגמה מעשית:

```powershell
# תרחיש: Deploy לייצור

# 1️⃣ עבדתי שבוע ב-dev
# 100 commits, 50 features חדשים

# 2️⃣ בדיקות ב-test
.\SCRIPTS\switch-environment.ps1 -Environment test -Build -Up
# ✅ כל הבדיקות עברו!

# 3️⃣ Deploy לייצור
.\SCRIPTS\switch-environment.ps1 -Environment prod -Build -Up
# Build: 5-7 דקות (אופטימיזציה מלאה!)

# זמן build:
# [1/10] Installing Python dependencies... (60s)
# [2/10] Installing Node dependencies... (90s)
# [3/10] Building frontend... (120s)
# [4/10] Optimizing assets... (45s)
# [5/10] Removing dev dependencies... (30s)
# [6/10] Setting up security... (15s)
# [7/10] Configuring user permissions... (10s)
# [8/10] Cleaning up... (20s)
# [9/10] Final optimization... (30s)
# [10/10] Done! (420s total = 7 minutes)

# 4️⃣ הרצת migrations
cd ENVIRONMENTS/prod
docker-compose exec web python manage.py migrate
# ✅ Database updated!

# 5️⃣ האתר חי!
# http://localhost:8082
# או: https://your-domain.com

# 6️⃣ מצאת bug קריטי בייצור?!
code SOURCE/app/views.py
# תיקנתי

# 7️⃣ בדיקה מהירה ב-dev
.\SCRIPTS\switch-environment.ps1 -Environment dev -Up
# http://localhost:8000
# ✅ התיקון עובד!

# 8️⃣ בדיקה ב-test
.\SCRIPTS\switch-environment.ps1 -Environment test -Build -Up
# ✅ עבר בדיקות!

# 9️⃣ Hotfix לייצור
.\SCRIPTS\switch-environment.ps1 -Environment prod -Build -Up
# Build: 7 דקות
# ✅ Bug תוקן בייצור!
```

### ⚡ יתרונות:

- 🚀 **מהיר** - optimization מלא
- 🔒 **מאובטח** - hardened
- 📦 **קטן** - image מינימלי
- 💪 **יציב** - לא משתנה
- ⚡ **ביצועים** - workers מרובים

### ⚠️ חסרונות:

- ⏱️ **Build ארוך** - 5-7 דקות
- 🔄 **Deploy איטי** - צריך rebuild
- 🐛 **Debug קשה** - אין כלים
- ⚠️ **שגיאה = downtime** - עד rebuild

---

## 🔗 הגשר בין הסביבות

### ❓ "האם כל מצב הוא לעצמו או יש גשר?"

**יש גשר! המקור הוא SOURCE/!** 🌉

```
אתה עובד ב:  SOURCE/app/views.py
                 ↓
              שומר (Ctrl+S)
                 ↓
     ┌───────────┴───────────┐
     ↓           ↓           ↓
   dev/       test/       prod/
(רואה מיד)  (צריך build) (צריך build)
```

### 📝 תרחיש מלא:

```powershell
# 🟢 בוקר - פיתוח ב-dev
.\SCRIPTS\switch-environment.ps1 -Environment dev -Up
code SOURCE/app/views.py

# כתבתי function חדשה:
def calculate_cer(text1, text2):
    # ... logic ...
    return cer_score

# שמרתי → רענון דפדפן → ✅ עובד!

# עשיתי 20 שינויים קטנים, כל אחד רואה מיד ב-dev
# זמן פיתוח: 2 שעות

# 🟡 צהריים - בדיקה ב-test
.\SCRIPTS\switch-environment.ps1 -Environment test -Build -Up
# Build: 3 דקות
# ✅ כל הטסטים עברו!

# 🔴 אחה"צ - Deploy לייצור
.\SCRIPTS\switch-environment.ps1 -Environment prod -Build -Up
# Build: 7 דקות
# ✅ Feature חיה בייצור!

# ערב - מצאתי bug קטן בייצור
code SOURCE/app/views.py
# תיקון: שורה 42

# 🟢 בדיקה מהירה ב-dev
# רענון → ✅ תוקן!

# 🟡 בדיקה ב-test
.\SCRIPTS\switch-environment.ps1 -Environment test -Build -Up
# ✅ עבר!

# 🔴 Hotfix לייצור
.\SCRIPTS\switch-environment.ps1 -Environment prod -Build -Up
# ✅ תוקן בייצור!
```

### 🎯 העיקרון:

1. **SOURCE/** = המקור האמיתי (single source of truth)
2. **dev/** = מראה מצביעה (mirror) - רואה שינויים מיד
3. **test/** = snapshot - צריך refresh (build)
4. **prod/** = snapshot מאובטח - צריך refresh (build)

---

## 🚀 תרחישים נפוצים

### תרחיש 1: יום עבודה רגיל

```powershell
# בוקר
.\SCRIPTS\switch-environment.ps1 -Environment dev -Up
.\SCRIPTS\monitor.ps1  # ברקע

# עבודה
code SOURCE/
# כל שינוי → Dashboard מתעדכן → רואה ב-dev מיד

# סוף יום
# אם סיימתי feature:
.\SCRIPTS\switch-environment.ps1 -Environment test -Build -Up
# בדיקה → commit → push
```

**זמן build:** 3 דקות ליום (רק test)  
**זמן פיתוח:** 8 שעות ללא builds! ⚡

---

### תרחיש 2: Bug בייצור! 🐛🔥

```powershell
# 1️⃣ משתמש דיווח bug
# "כפתור X לא עובד!"

# 2️⃣ שכפול ב-dev
.\SCRIPTS\switch-environment.ps1 -Environment dev -Up
# http://localhost:8000
# ✅ שיכפלתי את הבאג!

# 3️⃣ תיקון מהיר
code SOURCE/app/templates/button.html
# תיקנתי שורה 15

# רענון דפדפן → ✅ עובד!

# 4️⃣ בדיקה ב-test
.\SCRIPTS\switch-environment.ps1 -Environment test -Build -Up
# Build: 3 דקות
# ✅ עבר בדיקות!

# 5️⃣ Hotfix לייצור
.\SCRIPTS\switch-environment.ps1 -Environment prod -Build -Up
# Build: 7 דקות
# ✅ Bug תוקן!

# סה"כ זמן: 15 דקות (כולל builds)
```

---

### תרחיש 3: Feature גדול חדש

```powershell
# שבוע 1-2: פיתוח ב-dev
.\SCRIPTS\switch-environment.ps1 -Environment dev -Up
# עבודה 10 ימים, 200 commits
# כל שינוי רואה מיד!

# יום 11: בדיקות ב-test
.\SCRIPTS\switch-environment.ps1 -Environment test -Build -Up
docker-compose -f ENVIRONMENTS/test/docker-compose.yml exec web pytest
# ✅ 150 טסטים עברו!

# יום 12: Staging (test על שרת חיצוני)
# העלאה ל-staging server
# QA team בודקים
# ✅ אישור!

# יום 13: Production deploy
.\SCRIPTS\switch-environment.ps1 -Environment prod -Build -Up
# ✅ Feature חיה!
```

---

## 🎨 ויזואליזציה

### מבנה קבצים:

```
SOURCE/                          ← כאן אתה עובד!
├── app/
│   ├── views.py                 ← כאן אתה כותב קוד
│   ├── models.py
│   └── templates/
└── front/
    ├── src/
    └── package.json

ENVIRONMENTS/
├── dev/
│   ├── docker-compose.yml       ← volumes: מצביע ל-SOURCE/
│   └── Dockerfile               ← פשוט, ללא optimization
│
├── test/
│   ├── docker-compose.yml       ← build: עותק מ-SOURCE/
│   └── Dockerfile               ← optimization בינוני
│
└── prod/
    ├── docker-compose.yml       ← build: עותק מ-SOURCE/
    └── Dockerfile               ← optimization מלא + security
```

### זרימת עבודה:

```
אתה ← → SOURCE/ ← → dev/ (מראה חיה)
                    ↓
                 test/ (snapshot - build)
                    ↓
                 prod/ (snapshot - build)
```

---

## 📊 סיכום טבלה מפורט

### זמנים:

| פעולה | dev | test | prod |
|-------|-----|------|------|
| Build ראשוני | 2 דק' | 3 דק' | 7 דק' |
| רענון אחרי שינוי | **0 שניות** | 3 דק' | 7 דק' |
| Startup | 10 שניות | 15 שניות | 20 שניות |

### שימוש:

| תרחיש | איזו סביבה? |
|-------|-------------|
| כתיבת קוד יומיומי | 🟢 dev |
| ניסוי feature חדש | 🟢 dev |
| Debug bug | 🟢 dev |
| בדיקות לפני commit | 🟡 test |
| CI/CD pipeline | 🟡 test |
| בדיקות אינטגרציה | 🟡 test |
| Deploy לייצור | 🔴 prod |
| Hotfix קריטי | 🟢 dev → 🟡 test → 🔴 prod |

---

## 💡 טיפים חשובים

### 1. dev רץ כל הזמן

```powershell
# בוקר:
.\SCRIPTS\switch-environment.ps1 -Environment dev -Up
.\SCRIPTS\monitor.ps1

# יום שלם:
# עובד ב-SOURCE/ ← רואה שינויים מיד!

# ערב:
# אל תעצור! תשאיר אותו רץ למחר
```

### 2. test רק לבדיקות

```powershell
# לא משתמשים בו כל היום!
# רק לפני:
# - commit
# - merge
# - deploy
```

### 3. prod רק לייצור

```powershell
# אסור לנסות דברים ב-prod!
# רק deploy מאושר אחרי test
```

---

## ✅ מוכן ליישום?

עכשיו שהבנת איך זה עובד, בוא נריץ את זה בפועל! 🚀

```powershell
# צעד 1: צור מבנה
.\SCRIPTS\setup-project-structure.ps1

# צעד 2: הפעל dev
.\SCRIPTS\switch-environment.ps1 -Environment dev -Up

# צעד 3: הפעל מוניטור
.\SCRIPTS\monitor.ps1

# צעד 4: התחל לעבוד!
code SOURCE/
```

**אז מה אתה אומר? מוכן להתחיל?** 🎯
