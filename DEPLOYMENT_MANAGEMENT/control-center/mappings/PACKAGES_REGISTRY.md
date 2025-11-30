# 📦 רישום חבילות - Packages Registry

**תאריך עדכון אחרון:** 14 בנובמבר 2025  
**גרסה:** 1.0  
**אחראי:** Control Center Management System

---

## 🎯 מטרת המסמך

מסמך זה מרכז את כל החבילות החיצוניות והפנימיות המשולבות בפרויקט eScriptorium.  
כל חבילה מתועדת עם: מטרה, גרסה, תלויות, סטטוס שילוב, ונקודות אינטגרציה.

---

## 📊 סיכום מהיר

| קטגוריה | כמות | סטטוס |
|---------|------|-------|
| חבילות ליבה (Core) | 0 | 🔄 בתכנון |
| חבילות BiblIA | 0 | 🔄 בתכנון |
| חבילות עזר (Utilities) | 0 | 🔄 בתכנון |
| חבילות Docker | 0 | 🔄 בתכנון |
| **סה"כ** | **0** | 🔄 **בתכנון** |

---

## 🏗️ חבילות ליבה (Core Packages)

### 1. eScriptorium Base
```yaml
שם: eScriptorium
גרסה: 0.13.x
דומיין: CORE
מטרה: מערכת ליבת eScriptorium המקורית
תיקייה: escriptorium/CORE/eScriptorium_UNIFIED/
סטטוס: ✅ פעיל
תלויות:
  - Django 4.2+
  - PostgreSQL 13+
  - Redis 7+
  - Celery 5+
נקודות אינטגרציה:
  - API endpoints: /api/v1/
  - Database: PostgreSQL
  - Cache: Redis
  - Queue: Celery
מתעד: user@system
תאריך: 2025-11-14
```

---

## 🎨 חבילות BiblIA

### 1. BiblIA Extensions (לתכנון)
```yaml
שם: BiblIA Extensions
גרסה: TBD
דומיין: CORE
מטרה: הרחבות עבריות ל-eScriptorium
תיקייה: (טרם הוקצה)
סטטוס: 🔄 בתכנון
תלויות:
  - eScriptorium Base
  - Hebrew NLP libraries
  - Custom OCR models
נקודות אינטגרציה:
  - (טרם הוגדרו)
מתעד: Control Center
תאריך: 2025-11-14
```

---

## 🛠️ חבילות עזר (Utility Packages)

*(טרם נוספו חבילות)*

---

## 🐳 חבילות Docker

### 1. Docker Compose Configuration
```yaml
שם: Docker Compose Setup
גרסה: 3.8
דומיין: DEPLOYMENT_MANAGEMENT
מטרה: תצורת Docker containers למערכת
תיקייה: escriptorium/DEPLOYMENT_MANAGEMENT/docker/
סטטוס: ✅ פעיל
תלויות:
  - Docker Engine 20+
  - Docker Compose 2+
נקודות אינטגרציה:
  - Control Center dashboard
  - Health checks
  - Monitoring
מתעד: Control Center
תאריך: 2025-11-14
```

---

## 📋 תבנית הוספת חבילה חדשה

```yaml
שם: [שם החבילה]
גרסה: [x.y.z]
דומיין: [CORE / BUILD_MANAGEMENT / DEPLOYMENT_MANAGEMENT]
מטרה: [תיאור מטרת החבילה]
תיקייה: [נתיב מלא]
סטטוס: [🔄 בתכנון / 🚧 בפיתוח / ✅ פעיל / ⚠️ deprecated]
תלויות:
  - [חבילה 1]
  - [חבילה 2]
נקודות אינטגרציה:
  - [נקודה 1]
  - [נקודה 2]
בעיות ידועות:
  - [בעיה 1 אם יש]
מתעד: [שם המתעד]
תאריך: [YYYY-MM-DD]
```

---

## 🔗 קישורים נוספים

- [מבנה תיקיות](./DIRECTORY_STRUCTURE.md)
- [נקודות אינטגרציה](./INTEGRATION_POINTS.md)
- [מפת תלויות](./DEPENDENCIES_MAP.md)
- [Control Center Dashboard](../BUILD_MANAGER_DASHBOARD.html)

---

## 📝 היסטוריית שינויים

| תאריך | גרסה | שינוי | מבצע |
|-------|------|-------|------|
| 2025-11-14 | 1.0 | יצירה ראשונית | Control Center |

---

**הערה:** מסמך זה מתעדכן אוטומטית על ידי Control Center ומשתלב עם הדשבורד הויזואלי.
