# 📋 Change Log - eScriptorium BiblIA

## 🗓️ שינויים מיום 18 בספטמבר 2025

### ✅ שינויים מותרים ומוצדקים:

#### 1. **הוספת תמיכה בעברית** (`app/escriptorium/settings.py`)
- הוספת `'he'` ל-ESC_LANGUAGES
- הוספת Hebrew לרשימת LANGUAGES
- **הצדקה**: תמיכה רשמית בעברית למשתמשים ישראליים

#### 2. **הוספת API endpoints לניטור** (`app/apps/core/urls.py`)
- הוספת `system-maintenance/` route
- הוספת `api/system-status/` ו-`api/system-maintenance/`
- **הצדקה**: כלים לניטור ותחזוקת המערכת ללא פגיעה בפונקציונליות קיימת

#### 3. **הפעלת תכונות מתקדמות** (`docker-compose.yml`)
- הפעלת volume mapping: `- ./app/:/usr/src/app/`
- הוספת Elasticsearch service
- הפעלת CeleryBeat scheduler
- **הצדקה**: שיפור ביצועים ותכונות חדשות

#### 4. **הפעלת export modes** (`variables.env`)
- `EXPORT_OPENITI_MARKDOWN=true`
- `EXPORT_TEI_XML=true` 
- `DISABLE_ELASTICSEARCH=False`
- **הצדקה**: תכונות מתקדמות לחוקרים

### 🔒 עקרונות שנשמרו:
- ✅ לא שונתה פונקציונליות קיימת
- ✅ רק הוספות של תכונות חדשות
- ✅ שמירה על תאימות לאחור
- ✅ כל השינויים מתועדים כאן

### 📊 סיכום:
**סה"כ קבצים ששונו**: 5
**קבצי ליבה ששונו**: 2 (רק הוספות)
**קבצי הגדרות**: 3
**רמת סיכון**: 🟢 נמוכה

---

## 🗓️ שינויים מיום 5-17 באוקטובר 2025

### ✅ שינויים מותרים ומוצדקים:

#### 5. **תיקון בעיית CSS Build Process** (5 אוקטובר 2025 + 17 אוקטובר 2025)
- **קבצים מושפעים**: `Dockerfile`
- **בעיה מקורית** (5 אוק'): קבצי CSS (vendor.css, main.css וכו') לא הועתקו ל-`/usr/src/app/static/`
- **סיבה**: `COPY --from=frontend` העתיק ל-`/usr/src/app/front/` שלא היה ב-`STATICFILES_DIRS`
- **תיקון זמני** (5 אוק'): העתקה ידנית של *.css באמצעות `docker cp`
- **פתרון קבוע** (17 אוק'): ✅ **יושם**
  - שינוי `COPY --from=frontend /build/dist` מ-`/usr/src/app/front` ל-`/usr/src/app/escriptorium/static/dist/`
  - עדכון `ENV FRONTEND_DIR` מ-`/usr/src/app/front` ל-`/usr/src/app/escriptorium/static/dist`
  - הקבצים כעת מועתקים ישירות למקום הנכון ש-`collectstatic` מכיר
- **תיעוד**: `CSS_FIX_REPORT.md`, `CSS_BUILD_PROCESS_ANALYSIS.md`, `CSS_BUILD_SUMMARY.md`
- **הצדקה**: קבצי CSS חיוניים לממשק התקין (Bootstrap, responsive design)
- **יתרונות הפתרון**: 
  - ✅ אוטומטי בכל build
  - ✅ אין צורך בהעתקה ידנית
  - ✅ אין שינוי ב-settings.py (משתמש ב-`FRONTEND_DIR` environment variable קיים)
- **גיבוי**: `Dockerfile.backup.20251017`

#### 6. **אינטגרציה של Tesseract OCR** (`app/apps/core/models.py`)
- הוספת method חדש: `transcribe_tesseract()` (134 שורות קוד)
- שינוי שם: `transcribe()` → `transcribe_kraken()` + routing logic חדש
- הוספת `@cached_property engine` לזיהוי אוטומטי של סוג המנוע
- עדכון `clone_for_training()` לתמיכה בשתי סיומות קבצים
- עדכון validators להכרה ב-`.traineddata` files
- **הצדקה**: מתן אפשרות למשתמשים להשוות תוצאות OCR בין Kraken ו-Tesseract
- **יתרונות**: 
  - בחירת מנוע OCR מתאים לפי סוג הטקסט
  - אפשרות להשוואת דיוק בין מנועים
  - גמישות למחקר אקדמי
- **תאימות לאחור**: ✅ מלאה - Kraken ממשיך לעבוד כרגיל

#### 6. **תמיכה בהעלאת מודלי Tesseract** (`app/apps/core/forms.py`)
- עדכון `ModelUploadForm` validator לתמיכה ב-`.traineddata`
- שינוי logic ב-`clean_file()` לטיפול בשני סוגי מודלים:
  - Kraken (`.mlmodel`) - validation מלא כקודם
  - Tesseract (`.traineddata`) - validation מינימלי
- הוספת `GroupedModelChoiceIterator` לקיבוץ מודלים לפי מנוע
- **הצדקה**: הכרחי לתמיכה בהעלאת ושימוש במודלי Tesseract
- **שיפור UX**: קיבוץ מודלים בממשק לפי סוג (Kraken/Tesseract)

#### 7. **API ניטור ותחזוקה** (`app/apps/core/urls.py`)
- הוספת 3 routes חדשים:
  - `system-maintenance/` - ממשק תחזוקה (staff only)
  - `api/system-status/` - API לבדיקת בריאות המערכת
  - `api/system-maintenance/` - API לפעולות תחזוקה
- import של `SystemStatusAPI`, `SystemMaintenanceAPI` מ-`core.system_views`
- **הצדקה**: כלי DevOps לניטור ותחזוקה שוטפת
- **אבטחה**: הגישה מוגבלת ל-staff users בלבד

#### 8. **ארכיטקטורה מודולרית** (`app/escriptorium/settings.py`)
- הוספת Django apps נפרדים:
  - `apps.language_support` - ניתוח OCR לעברית
  - `biblia_templatetags` - template tags מותאמים
- הוספת middleware מבודד:
  - `CleanBibliaMiddlewareV2` (גרסה מתוקנת)
  - הערת גרסה ישנה שגרמה לבעיות JavaScript
- הוספת context processor:
  - `biblia_translation_processor.biblia_translations`
- **הצדקה**: הפרדה בין core של eScriptorium ל-customizations של BiblIA
- **עקרונות**: 
  - "One Purpose, One File"
  - אפס שינויים ב-core apps של eScriptorium
  - כל ה-customizations במודולים נפרדים

### 🔒 עקרונות שנשמרו (עדכון):
- ✅ לא שונתה פונקציונליות קיימת של Kraken
- ✅ רק הוספות של תכונות חדשות (Tesseract, APIs, Apps)
- ✅ שמירה על תאימות לאחור מלאה
- ✅ כל השינויים מתועדים כאן וב-Git
- ✅ ארכיטקטורה מודולרית - הפרדה בין core ל-custom
- ⚠️ חריגה מוצדקת: עריכת `models.py` לצורך Tesseract integration

### 📊 סיכום מעודכן:
**סה"כ קבצים ששונו**: 8
**קבצי ליבה ששונו**: 4 (models.py, forms.py, urls.py, settings.py)
**שורות קוד נוספו**: ~205
**קבצים חדשים**: 20+ (apps, middleware, tools, תיעוד)
**רמת סיכון**: 🟡 בינוני (ניתן לניהול)

### 📝 תיעוד נוסף:
- 📄 `CORE_FILES_AUDIT_REPORT.md` - ביקורת מפורטת של קבצי ליבה
- 📄 `TESSERACT_INTEGRATION_ANALYSIS.md` - ניתוח טכני מלא
- 📄 `COMPLETE_TRANSLATION_FIX_REPORT.md` - תיקון בעיות תרגום
- 📄 `MISTAKES_TO_AVOID.md` - קטלוג טעויות ללמידה

### ⚠️ פעולות נדרשות להשלמת התיעוד:
- [ ] יצירת `TESSERACT_INTEGRATION_TECHNICAL_DOCS.md`
- [ ] הוספת unit tests ל-Tesseract integration
- [ ] תיעוד upgrade path ל-eScriptorium עתידי
- [ ] בדיקות regression למנוע שבירת תכונות קיימות

---

## 🗓️ תיקונים מיום 17 באוקטובר 2025

### ✅ תיקון כפילות ב-settings.py

#### 9. **תיקון STATICFILES_DIRS** (`app/escriptorium/settings.py`)
- הסרת כפילות של `homepage` ו-`contributors` ב-STATICFILES_DIRS
- **בעיה**: אחרי merge מ-upstream, התיקיות הופיעו **גם** ברשימה הקבועה **וגם** ב-if blocks
- **תיקון**: הסרת 2 שורות מהרשימה הקבועה, שמירה על ה-if blocks בלבד
- **תוצאה**: 
  - ביצועים טובים יותר (פחות סריקות)
  - feature flags עובדים כראוי
  - קוד נקי יותר
- **הצדקה**: תיקון של redundancy שנוצרה ממיזוג branches
- **זמן תיקון**: 30 שניות
- **תיעוד**: ראה `STATICFILES_FIX_COMPLETED.md`

### 📊 סיכום ביקורת קבצי ליבה:
**תאריך ביקורת:** 17 באוקטובר 2025

- ✅ **ביקורת מלאה בוצעה** של כל קבצי הליבה
- ✅ **4 קבצים נבדקו**: models.py, forms.py, urls.py, settings.py
- ✅ **כל השינויים מתועדים** ב-`CORE_FILES_AUDIT_REPORT.md`
- ✅ **תיקון אחד בוצע**: כפילות STATICFILES_DIRS
- ✅ **המלצות תועדו** ב-`POST_AUDIT_TODO.md`

**קבצי תיעוד שנוצרו:**
- `CORE_FILES_AUDIT_REPORT.md` - דוח ביקורת מפורט (17KB)
- `CORE_AUDIT_SUMMARY.md` - סיכום מהיר (7KB)
- `SETTINGS_DEEP_AUDIT.md` - ביקורת מעמיקה של settings.py
- `SETTINGS_STATICFILES_ISSUE.md` - הסבר על בעיית הכפילות
- `STATICFILES_FIX_COMPLETED.md` - תיעוד התיקון
- `POST_AUDIT_TODO.md` - רשימת משימות המשך (13KB)
- `LANGUAGE_SETTINGS_EXPLAINED.md` - הסבר מעמיק על הגדרות שפה (14KB)
- `LANGUAGE_SETTINGS_DIAGRAM.md` - דיאגרמות ויזואליות של מערכת השפות
- `CSS_BUILD_PROCESS_ANALYSIS.md` - ניתוח תהליך בניית CSS (17 אוק' 2025)

---

**עדכון אחרון:** 22 אוקטובר 2025

---

## 🗓️ שינויים מיום 21-22 באוקטובר 2025

### ✅ שינויים מותרים ומוצדקים:

#### 10. **Analytics Dashboard - לוח בקרה אנליטי** (21-22 אוק' 2025)
- **קבצים חדשים שנוצרו**:
  - `app/escriptorium/templates/core/analytics_overview.html` (603 שורות)
  - `app/escriptorium/templates/core/analytics_dashboard.html`
  - `front/src/analytics-dashboard.js` - Vue.js component
  - `front/src/analytics-dashboard.css` - Responsive design
  
- **Backend API** (`app/apps/core/views.py`):
  - `AnalyticsDashboard` - View class חדש
  - Query optimization עם `select_related()` ו-`distinct()`
  - Support לסינון לפי user permissions
  
- **URL Routes** (`app/apps/core/urls.py`):
  - `/analytics/` - דף Overview
  - `/analytics/?model={ID}` - דף מודל ספציפי
  
- **תכונות שיושמו**:
  - 📊 גרפים אינטראקטיביים (Chart.js):
    - Accuracy Over Time (line chart)
    - Duration per Epoch (bar chart)
    - Data Split (doughnut chart)
  - 🔄 Real-time updates (auto-refresh 30 sec)
  - 📥 Export data ל-JSON
  - 📱 Responsive design (mobile-friendly)
  - 🌍 תרגום מלא לעברית
  
- **UI Integration**:
  - כפתור 📊 בטבלת המודלים (`/models/`)
  - Summary cards: Total Models, Active Training, Avg Accuracy, Total Epochs
  - Modal window עם גרפים מפורטים לכל מודל
  
- **הצדקה**: 
  - כלי מחקר לניתוח ביצועי מודלים
  - מעקב אחר תהליכי אימון
  - השוואת מודלים לפי מטריקות
  - תמיכה במחקר אקדמי
  
- **יתרונות**:
  - ✅ מידע ויזואלי ברור
  - ✅ עזרה בבחירת מודלים
  - ✅ מעקב התקדמות בזמן אמת
  - ✅ Export למחקר
  
- **תאימות לאחור**: ✅ מלאה - רק הוספת תכונות חדשות
- **תיעוד**: `ANALYTICS_DASHBOARD_COMPLETE.md`, `ANALYTICS_DASHBOARD_SUMMARY.md`
- **רמת סיכון**: 🟢 נמוכה (רק תכונות חדשות)

### 🔒 עקרונות שנשמרו:
- ✅ אפס שינויים בפונקציונליות קיימת
- ✅ רק הוספות של תכונות חדשות
- ✅ שמירה על תאימות לאחור
- ✅ תיעוד מלא

### 📊 סיכום מעודכן:
**סה"כ פרויקטים הושלמו**: 8 (↑ מ-7)
**התקדמות כללית**: 53% (↑ מ-46%)
**קבצים חדשים**: 4+ (templates, JS, CSS)
**שורות קוד נוספו**: ~700
**רמת סיכון**: 🟢 נמוכה

---

**עדכון אחרון:** 22 אוקטובר 2025, 11:30