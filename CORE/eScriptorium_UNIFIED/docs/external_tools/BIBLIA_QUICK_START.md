# התחלה מהירה - 3 שלבים פשוטים

## 🎯 מה נעשה?
בדיקה עם 5 עמודים → אימון מודל קטן → בדיקה שהתהליך עובד

---

## ⚡ שלב 1: ייבוא (10-15 דקות)

### פתח eScriptorium:
```
http://localhost:8082
User: koperberg
```

### צור פרויקט ומסמך:
1. **פרויקטים (Projects)** → **יצירת פרויקט (Create Project)** → `BiblIA Test - Ashkenazy`
2. בתוך הפרויקט: **יצירת מסמך (Create Document)** → `Ashkenazy Test Set`
   - **תסריט עיקרי (Main Script):** `Hebrew` (עברית)
   - **כיוון קריאה (Read Direction):** `Right to Left` (מימין לשמאל)
   - **היסט שורה (Line Offset):** `Baseline` (קו בסיס)

### העלה 5 תמונות:
**תמונות (Images)** → **ייבוא (Import)** → בחר את 5 הקבצים האלה:

```
G:\OCR_Arabic_Testing\BiblIA_dataset\BiblIA_dataset\Ashkenazy\btv1b10539358v.jpg
G:\OCR_Arabic_Testing\BiblIA_dataset\BiblIA_dataset\Ashkenazy\btv1b10539463d.jpg
G:\OCR_Arabic_Testing\BiblIA_dataset\BiblIA_dataset\Ashkenazy\btv1b10539464v.jpg
G:\OCR_Arabic_Testing\BiblIA_dataset\BiblIA_dataset\Ashkenazy\btv1b10539470g.jpg
G:\OCR_Arabic_Testing\BiblIA_dataset\BiblIA_dataset\Ashkenazy\btv1b10539499b.jpg
```

### ייבא XML לכל דף (5 פעמים):

**עבור כל דף:**
1. לחץ על התמונה (בתצוגת המסמך)
2. **עריכה (Edit)** - כפתור עפרון למעלה
3. **ייבוא (Import)** - בתפריט העליון
4. בחר את קובץ ה-XML המתאים (אותו שם, סיומת .xml)
5. **פורמט (Format):** בחר **ALTO**
6. **ייבוא (Import)** - אישור
7. ✅ **וודא שאת רואה:**
   - ריבועים/מלבנים (אזורי טקסט)
   - קווים אדומים (קווי בסיס)
   - טקסט עברי (תמלול)
8. **שמירה (Save)** - Ctrl+S או כפתור למעלה

---

## 🎓 שלב 2: אימון (30-60 דקות CPU)

### התחל אימון:
1. חזור לתצוגת המסמך (לחץ על שם המסמך למעלה)
2. **סמן את כל 5 הדפים** - checkbox ליד כל תמונה
3. בתפריט למעלה: **פילוח (Segmentation)** → **אימון מודל (Train Model)**
4. מלא את הטופס:
   ```
   שם המודל (Model Name): Hebrew_Ashkenazy_Test_v1
   מודל בסיס (Base Model): (השאר ריק - אימון מאפס)
   דריסה (Override): לא מסומן
   ```
5. **התחל אימון (Start Training)**

### עקוב אחרי התקדמות:

**בטרמינל (מומלץ!):**
```powershell
docker-compose logs -f celery-main
```

**תראה:**
```
Starting segmentation training...
Epoch 1/100: loss=0.523
Epoch 2/100: loss=0.487
...
Best model saved with accuracy: 82.3%
Training completed!
```

### ⏱️ זמן צפוי:
- **CPU:** 30-60 דקות
- **GPU:** 10-20 דקות

---

## ✅ שלב 3: בדיקה (5 דקות)

### בדוק שהמודל נוצר:
1. **מודלים (Models)** בתפריט העליון → תמצאי `Hebrew_Ashkenazy_Test_v1`
2. לחצי על שם המודל
3. תראי:
   - **דיוק אימון (Training Accuracy):** למשל 82.5%
   - **גודל קובץ (File Size):** בערך 15-25 MB
   - **נוצר (Created):** תאריך ושעה

### נסי את המודל על דף חדש:
1. העלי עוד דף מ-Ashkenazy (רק JPG, **ללא XML הפעם**)
2. לחצי על הדף → **עריכה (Edit)**
3. **פילוח (Segment)** - כפתור בתפריט העליון
4. בחרי:
   - **מודל (Model):** `Hebrew_Ashkenazy_Test_v1`
   - **שלבים (Steps):** **Both** (גם אזורים וגם קווים)
5. **הרץ (Run)**
6. המתני 10-30 שניות
7. ✅ **תראי סגמנטציה אוטומטית!**
   - אזורים מזוהים (לא מושלם עם 5 דפים בלבד)
   - קווי בסיס מזוהים
   - זה הוכחה שהתהליך עובד!

---

## 🚀 הצעד הבא

**אם הכל עבד**, עכשיו תעשה אימון אמיתי:
- **30 דפים** במקום 5
- **זמן אימון:** 3-5 שעות (CPU)
- **Accuracy צפוי:** 88-95%
- **תוצאה:** מודל production-ready!

---

## 🔧 אם משהו לא עובד

```powershell
# בדוק containers
docker-compose ps

# ראה שגיאות
docker-compose logs celery-main --tail 50

# אתחל
docker-compose restart celery-main
```

---

## 📝 רשימת בדיקה מהירה

- [ ] פתחתי http://localhost:8082
- [ ] יצרתי פרויקט
- [ ] יצרתי מסמך
- [ ] העליתי 5 תמונות
- [ ] ייבאתי 5 XML (כל דף בנפרד!)
- [ ] כל דף מציג סגמנטציה ✅
- [ ] התחלתי אימון
- [ ] רץ `docker-compose logs -f celery-main`
- [ ] האימון הסתיים (30-60 דק')
- [ ] המודל קיים ב-Models
- [ ] המודל עובד על דף חדש

---

**זהו! התחל כאן ↑**

פרטים נוספים ב-`QUICK_START_GUIDE.md`
