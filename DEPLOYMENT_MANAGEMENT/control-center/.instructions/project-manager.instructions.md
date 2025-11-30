---
description: CRITICAL - Project Manager system for coordinating all AI chatbot workers
applyTo: '**'
---

# 🏗️ מערכת מפקח הבניה האוטומטי
**CRITICAL: כל צ'אטבוט חייב לקרוא קובץ זה לפני תחילת עבודה**

---

## 🚨 **חובה לקריאה ראשונה!**

**לפני שמתחיל לקרוא את המסמך הזה:**
- ✅ **קרא תחילה:** `eScriptorium_CLEAN/.github/instructions/MANDATORY_FIRST_ACTION.md`
- 🔧 **נושאים קריטיים:** SSL/pip issues, MCP tools availability
- ⚡ **עדיפות:** HIGHEST - חובה בכל סשן חדש!

---

## 🎯 מטרת המערכת

**אתה צ'אטבוט-עובד בפרויקט eScriptorium.**

המשתמש = מנהל הבניה הראשי  
אתה = קבלן/עובד שמבצע משימות  
המערכת הזו = המפקח שמתאם הכל

---

## ⚠️ חובה! לפני שמתחילים עבודה

### שלב 1: קרא את תיק הפרויקט
```markdown
📂 קבצים שחובה לקרוא (בסדר הזה):

1. `CHATBOT_ONBOARDING.md` - הכרת הפרויקט (5 דק')
2. `CURRENT_STATE.md` - מצב נוכחי של הפרויקט (3 דק')
3. `SESSION_LOG.md` - מה עשו צ'אטבוטים אחרים (2 דק')
4. `.github/instructions/automation-scripts.instructions.md` - חוקי אוטומציה (3 דק')
5. `BUILD_MANAGER_DASHBOARD.html` - לוח בקרה של המנהל (צפייה בלבד - אל תערוך!)
```

**סה"כ זמן קריאה: ~15 דקות**  
**זה חוסך לך שעות של טעויות!**

---

### 🎯 **חשוב מאוד!** לוח הבקרה

**`BUILD_MANAGER_DASHBOARD.html`** הוא הממשק של המנהל (המשתמש).

#### ✅ מה אתה צריך לעשות:
1. **אל תערוך את הקובץ ידנית** - זה ממשק ויזואלי בלבד
2. **עדכן את קבצי המצב** שהדשבורד קורא מהם:
   - `CURRENT_STATE.md` → הדשבורד מציג את הנתונים משם
   - `SESSION_LOG.md` → הדשבורד מציג פעילות משם
   - `logs/build-*.log` → הדשבורד מציג לוגים משם

#### 🔄 איך זה עובד (אוטומטי):
```
אתה (צ'אטבוט) עושה שינויים
         ↓
עדכון CURRENT_STATE.md + SESSION_LOG.md
         ↓
המנהל פותח BUILD_MANAGER_DASHBOARD.html
         ↓
הדשבורד קורא את הקבצים המעודכנים
         ↓
המנהל רואה את מה שעשית! ✅
```

**לכן:** תמיד עדכן את `CURRENT_STATE.md` ו-`SESSION_LOG.md` - זה מספיק!

---

### שלב 2: בדוק אם המשימה כבר נעשתה

```powershell
# חפש ב-SESSION_LOG.md אם מישהו כבר עשה את זה
Get-Content SESSION_LOG.md | Select-String "המשימה שלך"
```

**דוגמה:**
```markdown
משימה: "תקן את תרגום ה-CER strings"

✅ לפני שמתחיל - חפש:
- "CER" ב-SESSION_LOG.md
- "translation" ב-CURRENT_STATE.md
- "translate_cer_strings.py" בלוגים

אם מצאת → קרא מה נעשה ומה הבעיות
אם לא מצאת → המשימה חדשה, תתחיל
```

---

### שלב 3: קבל את רשימת המשימות שלך

```markdown
📋 מקורות למשימות:

1. **CURRENT_STATE.md → "Next Steps"**
   - משימות מאושרות ומתועדפות
   
2. **SESSION_LOG.md → "Next Chatbot Should Know"**
   - המלצות מצ'אטבוטים קודמים
   
3. **בקשת המשתמש הישירה**
   - מה שהמשתמש ביקש ממך עכשיו
```

---

## 📚 מאגר דפוסים ידועים (Knowledge Base)

### דפוס #1: npm install נכשל

**תסמינים:**
```
MODULE_NOT_FOUND: caniuse-lite
node_modules corrupted
```

**פתרון מוכח:**
```powershell
# אל תריץ npm ידנית!
# השתמש בסקריפט:
.\scripts\build-and-deploy.ps1 -Full

# או ידנית (רק אם הסקריפט לא עובד):
cd front
npm cache clean --force
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json -Force
npm install
```

**מתועד ב:** `SESSION_LOG.md` - Session 2025-10-26  
**זמן פתרון:** 5-8 דקות

---

### דפוס #2: תרגומים לא מופיעים בדפדפן

**תסמינים:**
```
- שיניתי he.json
- הרצתי build
- פתחתי בדפדפן - עדיין באנגלית
```

**פתרון מוכח:**
```powershell
# 1. ודא שהתרגום נפרס ל-Docker
.\scripts\build-and-deploy.ps1 -Smart

# 2. נקה cache של Django
docker-compose exec web python manage.py collectstatic --noinput

# 3. אתחל שירותים
.\scripts\restart-services.ps1

# 4. נקה cache דפדפן (Ctrl+Shift+Delete)
```

**מתועד ב:** `SESSION_LOG.md` - Session 2025-10-25  
**זמן פתרון:** 3-5 דקות

---

### דפוס #3: Docker containers לא עולים

**תסמינים:**
```
docker-compose up -d
Container "web-1" is unhealthy
```

**פתרון מוכח:**
```powershell
# 1. בדוק לוגים
docker-compose logs web --tail 50

# 2. בעיות נפוצות:
#    - Port 8082 תפוס → סגור תהליכים ישנים
#    - בעיות הרשאות → הרץ כ-Administrator
#    - קבצים חסרים → בדוק CURRENT_STATE.md

# 3. אתחול מלא
docker-compose down
docker-compose up -d
.\scripts\verify-deployment.ps1
```

**מתועד ב:** `DOCKER_COMMANDS_REFERENCE.md`  
**זמן פתרון:** 2-5 דקות

---

### דפוס #4: Build אורך יותר מדי

**תסמינים:**
```
npm install תקוע
45,263 קבצים נמחקים
זה לוקח 10-15 דקות
```

**פתרון מוכח:**
```powershell
# השתמש במצב Quick
.\scripts\build-and-deploy.ps1 -Quick

# זה מדלג על:
# - מחיקת node_modules
# - npm cache clean
# - npm install (אם כבר קיים)

# זמן: 3-5 דקות במקום 10-15
```

**מתועד ב:** `IMPROVEMENT_SUGGESTIONS.md` - Issue #001a  
**זמן חיסכון:** 7-10 דקות

---

### דפוס #5: עריכת קובץ Python במקום ב-Docker

**תסמינים:**
```
- ערכתי views.py מקומית
- הרצתי את Docker
- השינויים לא עובדים
```

**פתרון מוכח:**
```powershell
# אל תערוך קבצים ב-Docker ישירות!
# תמיד ערוך מקומית ואז פרוס:

# 1. ערוך קובץ מקומית
code app/escriptorium/core/views.py

# 2. פרוס ל-Docker
.\scripts\build-and-deploy.ps1 -Smart

# 3. אימות
.\scripts\verify-deployment.ps1
```

**מתועד ב:** `README_ENFORCED_BUILD.md`  
**זמן פתרון:** מיידי

---

### דפוס #6: duplicated entries ב-.po files

**תסמينים:**
```
django.core.management.base.CommandError: 
duplicate message definition
```

**פתרון מוכח:**
```powershell
# הכלי remove_po_duplicates.py פותר את זה אוטומטית!

# אופציה 1 - דרך סקריפט (מומלץ):
.\scripts\compile-translations.ps1 -Language he
# הסקריפט מריץ את remove_po_duplicates.py אוטומטית

# אופציה 2 - ידני:
python remove_po_duplicates.py
docker-compose exec web python manage.py compilemessages -l he
```

**מתועד ב:** `DEDUPLICATION_HEBREW_GUIDE.md`  
**זמן פתרון:** 1-2 דקות

---

## 🔄 תהליך עבודה סטנדרטי

### כשאתה מקבל משימה חדשה:

```
┌─────────────────────────────────────────┐
│ 1. קרא CURRENT_STATE.md                │
│    ↓                                    │
│    מה המצב הנוכחי?                     │
│    יש בעיות ידועות?                    │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 2. חפש ב-SESSION_LOG.md                │
│    ↓                                    │
│    מישהו עשה משימה דומה?               │
│    מה הבעיות שהיו?                     │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 3. בדוק במאגר דפוסים (למעלה)          │
│    ↓                                    │
│    יש פתרון מוכן?                      │
│    איזה סקריפט להשתמש?                 │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 4. בצע את המשימה                       │
│    ↓                                    │
│    תעד כל צעד                          │
│    שמור לוגים                          │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 5. דווח חזרה                           │
│    ↓                                    │
│    עדכן SESSION_LOG.md                 │
│    עדכן CURRENT_STATE.md               │
└─────────────────────────────────────────┘
```

---

## 📝 תבנית דיווח סטנדרטית

### בסיום כל משימה - עדכן את SESSION_LOG.md:

```markdown
### Session - [תאריך] [שעה] - Chatbot [שם/מזהה]

**משימה שהתבקשתי לבצע:**
[תיאור המשימה כמו שהמשתמש ביקש]

**קבצים ששינתי:**
- `נתיב/קובץ1.py` - [מה שינתי בדיוק - שורות X-Y]
- `נתיב/קובץ2.js` - [מה שינתי בדיוק - שורות A-B]

**פעולות שביצעתי:**
1. ✅ [פעולה 1 - כולל פקודה מדויקת]
2. ✅ [פעולה 2 - כולל פקודה מדויקת]
3. ⚠️ [פעולה 3 - נתקלתי בבעיה]

**בעיות שנתקלתי בהן:**
- **בעיה:** [תיאור הבעיה]
  - **פתרון:** [איך פתרתי]
  - **זמן פתרון:** X דקות
  - **האם זה דפוס חדש?** כן/לא

**דפוסים שזיהיתי (למאגר):**
- [אם זיהית דפוס חדש שצריך לתעד]

**זמן ביצוע כולל:** X דקות

**המלצות לצ'אטבוט הבא:**
- [מה הוא צריך לדעת]
- [על מה לשים לב]
- [מה עדיין צריך לעשות]

**סטטוס סיום:**
- [ ] משימה הושלמה 100%
- [ ] משימה הושלמה חלקית - נותר: [...]
- [ ] משימה נכשלה - סיבה: [...]

---
```

---

## 🎓 חוקי זהב לצ'אטבוט

### ✅ תמיד תעשה:

1. **קרא לפני שמתחיל**
   - CURRENT_STATE.md
   - SESSION_LOG.md (10 הסשנים האחרונים)
   - automation-scripts.instructions.md

2. **השתמש בסקריפטים**
   - ❌ לא: `npm install`
   - ✅ כן: `.\scripts\build-and-deploy.ps1`

3. **תעד הכל במקום אחד**
   - ✅ עדכן `SESSION_LOG.md` - תיעוד מרכזי
   - ✅ עדכן `CURRENT_STATE.md` - מצב נוכחי
   - ❌ אל תיצור קבצי תיעוד משלך!
   - ❌ אל תיצור `SUMMARY.md` או `REPORT.md`

4. **חפש דפוסים**
   - אם נתקלת בבעיה - חפש פתרון קיים
   - אם פתרת בעיה חדשה - תעד אותה במאגר הדפוסים (בקובץ הזה)

5. **דווח חזרה**
   - עדכן SESSION_LOG.md
   - עדכן CURRENT_STATE.md
   - השאר המלצות לצ'אטבוט הבא

---

### ❌ לעולם אל תעשה:

1. **לא להריץ פקודות ידניות**
   - npm, docker, compilemessages
   - יש סקריפטים לכל דבר!

2. **לא לערוך קבצים ב-Docker ישירות**
   - תמיד ערוך מקומית ופרוס

3. **לא למחוק SESSION_LOG.md**
   - זה הזיכרון הקולקטיבי שלנו!

4. **לא לדלג על תיעוד**
   - אם לא תעדת - זה כאילו לא קרה

5. **לא להמציא פתרונות**
   - אם יש פתרון מתועד - השתמש בו!

6. **🚨 לא להשאיר קבצים זמניים! (חשוב מאוד)**
   - אל תיצור קבצים כמו: `temp.txt`, `test.py`, `backup.old`
   - אם יצרת קובץ זמני - **מחק אותו בסיום!**
   - אם זה חשוב - העבר ל-`archive/` או ל-`logs/`

7. **🚨 לא ליצור קבצי תיעוד נפרדים!**
   - אין `CHATBOT_SESSION_X.md`
   - אין `MY_WORK_SUMMARY.md`
   - אין `FIXES_I_MADE.md`
   - **הכל ב-`SESSION_LOG.md` בלבד!**

---

## 🗑️ ניהול קבצים זמניים - חובה!

### כללים:

#### ✅ קבצים מותרים:
- קבצי קוד: `.py`, `.js`, `.html`, `.css`, `.vue`
- קבצי הגדרות: `package.json`, `docker-compose.yml`
- קבצי תיעוד: `SESSION_LOG.md`, `CURRENT_STATE.md`
- לוגים: `logs/build-*.log`, `logs/history.log`

#### ❌ קבצים אסורים (למחוק בסיום!):
- `temp*.py`, `test*.js`, `backup*.*`
- `old_*`, `new_*`, `copy_*`
- `~*`, `*.tmp`, `*.bak`
- `TODO.txt`, `NOTES.md` (אלא אם כן חלק רשמי מהפרויקט)

#### 📦 אם הקובץ חשוב - העבר לארכיון:
```powershell
# אם יצרת קובץ חשוב אבל זמני:
Move-Item "my_analysis.py" "archive/my_analysis_2025-10-27.py"

# אם יצרת לוג חשוב:
Move-Item "debug_output.txt" "logs/debug_2025-10-27.txt"
```

### תהליך סיום סשן:

```
┌─────────────────────────────────────┐
│ 1. סיימתי את המשימה                │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 2. בדיקה: יצרתי קבצים זמניים?      │
│    → כן? מחק או העבר לארכיון        │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 3. עדכון SESSION_LOG.md             │
│    (תיעוד מרכזי - כל מה שעשיתי)     │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 4. עדכון CURRENT_STATE.md           │
│    (מצב נוכחי - מה עובד/לא עובד)   │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 5. סיימתי! ✅                       │
│    הפרויקט נקי וממושמע               │
└─────────────────────────────────────┘
```

---

## 📝 תיעוד מרכזי - האחריות של המפקח

### עקרון: **כל התיעוד במקום אחד!**

#### קבצי התיעוד הרשמיים:

| קובץ | מטרה | מי מעדכן |
|------|------|----------|
| `SESSION_LOG.md` | היסטוריה מלאה של כל הסשנים | כל צ'אטבוט בסיום |
| `CURRENT_STATE.md` | מצב נוכחי של הפרויקט | כל צ'אטבוט בסיום |
| `logs/build-*.log` | לוגי build אוטומטיים | סקריפטים |
| `logs/history.log` | היסטוריית build | סקריפטים |
| `BUILD_MANAGER_DASHBOARD.html` | ממשק ויזואלי למנהל | קריאה אוטומטית מהקבצים למעלה |

#### 🚫 קבצים שאסור ליצור:

- `CHATBOT_SESSION_12.md` ❌
- `MY_WORK_TODAY.md` ❌
- `FIXES_SUMMARY.md` ❌
- `TRANSLATION_WORK.md` ❌
- `BUILD_NOTES.txt` ❌

**למה?** כי זה יוצר בלאגן! כל התיעוד חייב להיות ב-`SESSION_LOG.md` אחד מרכזי.

---

## 📊 איך המנהל רואה את העבודה שלך?

### תרשים זרימת מידע:

```
┌─────────────────────────────────────┐
│  אתה (צ'אטבוט) עובד                │
│  ↓                                  │
│  1. משנה קבצי קוד                   │
│  2. מריץ סקריפטים                   │
│  3. פותר בעיות                      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  מעדכן קבצי מצב:                    │
│  • SESSION_LOG.md (מה עשיתי)        │
│  • CURRENT_STATE.md (מה המצב)       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  המנהל פותח:                        │
│  BUILD_MANAGER_DASHBOARD.html       │
│  ↓                                  │
│  רואה בממשק ויזואלי:                │
│  ✅ 6 משימות הושלמו                 │
│  📊 67% התקדמות                     │
│  🤖 פעילות שלך בטיימליין            │
│  ⚠️ בעיות שזיהית                   │
└─────────────────────────────────────┘
```

**המסקנה:** עדכן `SESSION_LOG.md` + `CURRENT_STATE.md` והמנהל יראה הכל אוטומטית! 🎯

---

## 🗂️ מבנה הפרויקט (מפה)

```
BiblIA_dataset/
│
├── 📁 .github/instructions/        ← חוקים וקבצי הדרכה
│   ├── automation-scripts.instructions.md
│   ├── session-tracking.instructions.md
│   └── project-manager.instructions.md (הקובץ הזה!)
│
├── 📄 CHATBOT_ONBOARDING.md         ← הכרת הפרויקט
├── 📄 CURRENT_STATE.md              ← מצב נוכחי
├── 📄 SESSION_LOG.md                ← היסטוריה של כל הסשנים
│
├── 📁 eScriptorium_CLEAN/
│   ├── 📁 scripts/                  ← סקריפטי אוטומציה
│   │   ├── build-and-deploy.ps1    ← בנייה ופריסה
│   │   ├── compile-translations.ps1
│   │   ├── restart-services.ps1
│   │   └── verify-deployment.ps1
│   │
│   ├── 📁 front/                    ← פרונטאנד Vue.js
│   │   ├── vue/locales/he.json     ← תרגומים עבריים
│   │   ├── dist/                   ← קבצים מבולדים
│   │   └── package.json
│   │
│   ├── 📁 app/escriptorium/         ← Backend Django
│   │   ├── core/
│   │   └── locale/he/LC_MESSAGES/
│   │
│   └── 📁 logs/                     ← לוגים אוטומטיים
│       ├── build-*.log
│       ├── repair-*.log
│       └── history.log
│
└── 📄 remove_po_duplicates.py       ← כלי לתיקון .po files
```

---

## 🚀 דוגמאות מעשיות

### דוגמה 1: צ'אטבוט חדש מקבל משימה

**המשתמש אומר:**  
> "תבנה את הפרונטאנד ותפרוס אותו"

**הצ'אטבוט צריך:**

```markdown
1. ✅ לקרוא CURRENT_STATE.md
   → לראות שיש npm install issue

2. ✅ לחפש "build" ב-SESSION_LOG.md
   → למצוא שהצ'אטבוט הקודם השתמש ב-Quick mode

3. ✅ לבדוק במאגר דפוסים
   → דפוס #1: npm install נכשל
   → דפוס #4: Build אורך יותר מדי

4. ✅ להריץ את הפקודה הנכונה:
   .\scripts\build-and-deploy.ps1 -Full
   (לא Quick! כי יש בעיית npm)

5. ✅ לתעד ב-SESSION_LOG.md:
   - מה הרצתי
   - כמה זמן זה לקח
   - מה התוצאה

6. ✅ לעדכן CURRENT_STATE.md:
   - npm issue → Fixed
   - Build status → Success
```

---

### דוגמה 2: זיהוי דפוס חדש

**צ'אטבוט נתקל בבעיה:**
```
Error: webpack compilation failed
Module not found: 'vue-router'
```

**מה הצ'אטבוט צריך לעשות:**

```markdown
1. ✅ חפש בעיה דומה ב-SESSION_LOG.md
   → לא מצא

2. ✅ חפש במאגר דפוסים
   → לא מצא

3. ✅ פתור את הבעיה:
   npm install vue-router --save

4. ✅ **תעד דפוס חדש:**

   ### דפוס #7: webpack compilation failed - missing vue-router
   
   **תסמינים:**
   ```
   Module not found: 'vue-router'
   webpack compilation failed
   ```
   
   **פתרון:**
   ```powershell
   cd front
   npm install vue-router --save
   npm run build
   ```
   
   **זמן פתרון:** 2 דקות

5. ✅ דווח למשתמש:
   "מצאתי בעיה חדשה ופתרתי - תיעדתי במאגר הדפוסים"
```

---

### דוגמה 3: ניהול נכון של קבצים זמניים

**תרחיש:** צ'אטבוט מנתח קובץ תרגום ויוצר קובץ זמני

**❌ דרך שגויה:**
```powershell
# יצירת קובץ זמני
python analyze_translation.py > temp_results.txt

# עבודה עם הקובץ
Get-Content temp_results.txt

# עזיבת הקובץ במקום! ❌❌❌
```

**✅ דרך נכונה:**
```powershell
# יצירת קובץ זמני
python analyze_translation.py > temp_results.txt

# עבודה עם הקובץ
Get-Content temp_results.txt

# אופציה 1: מחיקה אם לא חשוב
Remove-Item temp_results.txt
Write-Host "✅ קובץ זמני נמחק"

# אופציה 2: העברה לארכיון אם חשוב
Move-Item temp_results.txt "logs/translation_analysis_2025-10-27.txt"
Write-Host "✅ קובץ הועבר לארכיון"

# תיעוד ב-SESSION_LOG.md:
"יצרתי קובץ זמני temp_results.txt והעברתי אותו ל-logs/"
```

---

### דוגמה 4: תיעוד מרכזי נכון

**תרחיש:** צ'אטבוט תיקן 5 בעיות שונות

**❌ דרך שגויה:**
```markdown
# הצ'אטבוט יוצר:
CHATBOT_SESSION_14_SUMMARY.md
TRANSLATION_FIXES.md
BUILD_IMPROVEMENTS.md
DOCKER_CHANGES.md
```
**תוצאה:** 4 קבצים חדשים! בלאגן! ❌

**✅ דרך נכונה:**
```markdown
# הצ'אטבוט מעדכן רק:
SESSION_LOG.md  ← כל התיעוד כאן!

### Session - 27/10/2025 14:45 - Chatbot #14

**משימה:** תיקון 5 בעיות build + תרגום

**קבצים ששינתי:**
- he.json - תיקון 12 מחרוזות תרגום
- build-and-deploy.ps1 - תיקון bug בפס התקדמות
- docker-compose.yml - עדכון ports

**פעולות:**
1. ✅ תיקון תרגומים
2. ✅ תיקון סקריפט build
3. ✅ עדכון Docker config
4. ✅ בדיקה ואימות
5. ✅ מחיקת קבצים זמניים (temp_*.py)

**זמן כולל:** 25 דקות
```
**תוצאה:** קובץ 1 מרכזי! מסודר! ✅

---

## 📊 מעקב התקדמות

### מדדי הצלחה:

| מדד | יעד | כיצד לבדוק |
|-----|-----|------------|
| זמן onboarding לצ'אטבוט חדש | < 15 דק' | קריאת 4 הקבצים הראשיים |
| שיעור שימוש בסקריפטים | 100% | אין פקודות npm/docker ידניות ב-SESSION_LOG |
| זמן ממוצע לפתרון בעיה | < 10 דק' | בדיקה במאגר דפוסים |
| שיעור תיעוד | 100% | כל משימה מתועדת ב-SESSION_LOG |

---

## 🆘 מה לעשות אם תקוע?

### רמה 1 - חפש בתיעוד:
```markdown
1. SESSION_LOG.md → בעיות דומות?
2. מאגר דפוסים → פתרון מוכן?
3. CURRENT_STATE.md → Known Issues?
```

### רמה 2 - נסה פתרונות כלליים:
```powershell
# בעיות npm/build:
.\scripts\build-and-deploy.ps1 -Full

# בעיות Docker:
docker-compose down && docker-compose up -d

# בעיות תרגום:
.\scripts\compile-translations.ps1 -Language he
```

### רמה 3 - דווח למשתמש:
```markdown
"נתקלתי בבעיה שלא מתועדת:
[תיאור הבעיה]

חיפשתי ב:
- SESSION_LOG.md ❌
- מאגר דפוסים ❌
- CURRENT_STATE.md ❌

ניסיתי:
1. [פתרון 1] - לא עבד
2. [פתרון 2] - לא עבד

צריך הכוונה איך להמשיך."
```

---

## 🎯 סיכום - הנקודות החשובות ביותר

### 🔴 3 דברים שחייבים לעשות תמיד:

1. **📖 קרא לפני שמתחיל**
   - CURRENT_STATE.md
   - SESSION_LOG.md (אחרונים)

2. **🤖 השתמש בסקריפטים**
   - לא npm/docker ידני
   - יש סקריפט לכל דבר

3. **📝 תעד הכל**
   - SESSION_LOG.md
   - CURRENT_STATE.md
   - דפוסים חדשים

### 🔴 3 דברים שאסור לעשות לעולם:

1. **🚫 קבצים זמניים**
   - אל תשאיר temp_*, backup_*, test_*
   - מחק או העבר לארכיון!

2. **🚫 תיעוד נפרד**
   - אל תיצור קבצי MD משלך
   - הכל ב-SESSION_LOG.md בלבד!

3. **🚫 פקודות ידניות**
   - אל תריץ npm/docker ישירות
   - השתמש ב-build-and-deploy.ps1!

---

**גרסה:** 1.0  
**תאריך יצירה:** 27 אוקטובר 2025  
**סטטוס:** 🔴 ENFORCED - חובה לכל צ'אטבוט

---

## 📞 קבלת עזרה

**אם אתה צ'אטבוט וקראת את זה:**
- ✅ אתה מוכן להתחיל לעבוד
- ✅ אתה יודע איפה לחפש מידע
- ✅ אתה יודע איך לדווח חזרה

**אם אתה המשתמש:**
- ✅ הצ'אטבוטים שלך עכשיו עובדים בצורה מתואמת
- ✅ יש להם מדריך ברור
- ✅ הם לא ישכפלו עבודה

---

**הצלחה! 🚀**
