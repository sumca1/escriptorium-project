# 📚 משאבים חיצוניים ופרויקטים קשורים

> **תאריך יצירה:** 5 באוקטובר 2025

---

## 🇩🇪 UB-Mannheim/eScriptorium_Dokumentation

### סקירה כללית
פרויקט תיעוד רשמי של eScriptorium בשפה הגרמנית (ואנגלית), שנוצר על ידי ספריית אוניברסיטת מנהיים במסגרת פרויקט OCR-BW וOCR-D.

### קישורים
- **GitHub**: https://github.com/UB-Mannheim/eScriptorium_Dokumentation
- **תיעוד מקוון**: https://ub-mannheim.github.io/eScriptorium_Dokumentation/
- **רישיון**: CC0-1.0 (נחלת הכלל)

### תוכן עיקרי
1. **מדריך שימוש כללי** (`Nutzungsanleitung_eScriptorium.md`)
2. **התקנה מקומית** (`Lokale_Installation_eScriptorium.md`)
3. **אימון מודלים** (גרמנית + אנגלית):
   - `Training-with-eScriptorium-DE.md`
   - `Training-with-eScriptorium-EN.md`
4. **שילוב Tesseract** (`eScriptorium-with-tesseract-extension.md`)
5. **העברה מ-Transkribus** (`Modellübertragung_Transkribus_nach_eScriptorium.md`)

### נקודות חשובות
- ✅ **Ground Truth Best Practices** - המלצות מקצועיות
- ✅ **Training Workflows** - תהליכי עבודה מומלצים
- ✅ **Fine-tuning vs Training from Scratch** - הסברים מפורטים
- ✅ **Virtual Keyboards** - תמיכה בשפות שונות
- ✅ **Tesseract Support** - OCR engine נוסף

### תורמים ראשיים
- **Stefan Weil** - מפתח ראשי
- **Thomas Schmidt** - תיעוד
- **Jan Kamlah** - פיתוח
- **Larissa Will** - תרומות

### למה זה רלוונטי לפרויקט BiblIA?

#### 1. **תיעוד דומה**
המבנה שלהם יכול לשמש השראה למדריכים שלנו:
```
המבנה שלהם:                    המבנה שלנו:
├── Installation Guide          ├── INSTALL-ubuntu.md
├── User Guide                  ├── README_BiblIA.md
├── Training Guide              ├── (יכול להיות שלב הבא)
└── Best Practices              └── TROUBLESHOOTING_GUIDE.md
```

#### 2. **Ground Truth Guidelines**
הם מספקים המלצות מפורטות ליצירת נתוני אימון איכותיים - רלוונטי גם לטקסטים עבריים.

#### 3. **Multi-Engine Support**
תמיכה בשני OCR engines (Kraken + Tesseract) - רעיון שיכול להיות שימושי בעתיד.

#### 4. **קהילה אקטיבית**
- 13 stars
- 3 forks
- עדכונים שוטפים
- תמיכת OCR-D project

---

## 🇫🇷 פרויקטים צרפתיים קשורים

### scripta PSL
- **תיאור**: הפרויקט המקורי שפיתח את eScriptorium
- **מוסד**: École Pratique des Hautes Études (EPHE)
- **קישור**: https://gitlab.inria.fr/scripta/escriptorium
- **רלוונטיות**: הפרויקט האב של eScriptorium

### Kraken OCR
- **תיאור**: מנוע ה-OCR שבבסיס eScriptorium
- **קישור**: https://kraken.re/
- **רלוונטיות**: הטכנולוגיה הליבה שעליה מבוסס הכל

---

## 🌍 מיזמים נוספים

### OCR-D
- **תיאור**: יוזמה גרמנית לסטנדרטיזציה של OCR
- **קישור**: https://ocr-d.de/
- **רלוונטיות**: Best practices ותקנים

### HTR-United
- **תיאור**: קהילה בינלאומית לשיתוף Ground Truth
- **קישור**: https://htr-united.github.io/
- **רלוונטיות**: משאבי אימון ונתונים

### Transkribus
- **תיאור**: פלטפורמה מסחרית (חלקית) ל-HTR
- **קישור**: https://readcoop.eu/transkribus/
- **רלוונטיות**: אלטרנטיבה מסחרית, שיטות עבודה

---

## 📖 משאבי למידה

### תיעוד רשמי
1. **eScriptorium Official Docs**: https://escriptorium.readthedocs.io/
2. **Kraken Documentation**: https://kraken.re/master/index.html
3. **Django Documentation**: https://docs.djangoproject.com/

### וידאו טיוטוריאלים
1. **eScriptorium Quick Start**: https://www.youtube.com/watch?v=aQuwh3OaKqg
2. **Training Models**: (קישורים במדריך UB-Mannheim)

### פייתון וספריות
1. **PyTorch**: https://pytorch.org/
2. **Vue.js**: https://vuejs.org/
3. **PostgreSQL**: https://www.postgresql.org/

---

## 🔗 קשרים עם פרויקט BiblIA

### משתמשים גדולים של eScriptorium
כפי שמופיע ב-`public/index.html` שלנו:
- ✅ **manuscriptologIA (msIA)** - Paris Observatory
- ✅ **Cremma** - INRIA, Paris
- ✅ **University Library of Mannheim** - גרמניה
- ✅ **National Library of Israel** - ירושלים (!) 🇮🇱
- ✅ **University of Maryland** - simorgh

### מדוע זה חשוב?
**הספרייה הלאומית בירושלים משתמשת ב-eScriptorium!** 
- זה אומר שהטכנולוגיה כבר בשימוש בישראל
- יש קהילה מקומית שיכולה לתמוך
- הניסיון שלנו ב-BiblIA יכול לתרום בחזרה

---

## 🎯 המלצות לפעולה

### 1. **למידה מUB-Mannheim**
- [ ] קרא את מדריך האימון הגרמני/אנגלי
- [ ] למד מהמבנה של התיעוד שלהם
- [ ] הבן את Ground Truth best practices

### 2. **שיתוף עם הקהילה**
- [ ] שקול לפרסם את התיעוד העברי ב-GitHub
- [ ] צור קשר עם הספרייה הלאומית בירושלים
- [ ] שתף ניסיון עם קהילת eScriptorium

### 3. **הרחבות עתידיות**
- [ ] שקול תמיכה ב-Tesseract (בנוסף ל-Kraken)
- [ ] צור קשר עם פרויקט OCR-D
- [ ] הוסף BiblIA ל-HTR-United

---

## 📝 הערות נוספות

### ציטוט מומלץ
אם תשתמש ברעיונות מהפרויקטים האלו, כדאי לציין:

```
Kamlah, J., Schmidt, T., & Weil, S. (2024). 
Training with eScriptorium: A step-by-step guide. 
Universitätsbibliothek Mannheim. 
https://github.com/UB-Mannheim/eScriptorium_Dokumentation
```

### רישיונות
- **UB-Mannheim Dokumentation**: CC0-1.0 (חופשי לחלוטין)
- **eScriptorium**: GPL-3.0
- **Kraken**: Apache 2.0

---

**עודכן לאחרונה:** 5 באוקטובר 2025  
**מתוחזק על ידי:** צוות BiblIA
