# 📱 התקנת SegmOnto ב-Firefox

## 🔧 שלבים:

### **שלב 1: פתח about:debugging**
```
כתובת בר: about:debugging
או: about:debugging#/runtime/this-firefox
```

### **שלב 2: בחר "This Firefox"**
- בצד **שמאל**
- לחץ על **"This Firefox"**

### **שלב 3: Load Temporary Add-on**
- כפתור: **"Load Temporary Add-on..."** (עליון)
- בחר קובץ:
  ```
  G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\segmonto-official\manifest.json
  ```
- לחץ **"Open"**

### **שלב 4: אישור + בדיקה**
✅ תוסף מופיע ברשימה  
✅ סמל: ✓ בעיגול  
✅ שם: "eScriptorium Segmonto Live Checker"  
✅ סטטוס: "Temporary extension"

---

## 🧪 בדיקה:

1. **כפתור בסרגל:**
   - זווית **ימנית עליונה** של Firefox
   - צריך להיות סמל **✓** מסומן
   - לחץ עליו → popup צריך להנפתח

2. **בדוק רישום:**
   - about:debugging → Temporary Extensions
   - צריך לראות את התוסף ברשימה

3. **חשוב:**
   - ⚠️ Temporary = יוסר כשתסגור Firefox
   - בפעם הבאה צריך לטעון שוב
   - אם רוצה קבוע: צריך Signed extension (מורכב יותר)

---

## 📝 Firefox: התקנה קבועה (Advanced)

אם רוצה שהתוסף יישמר אחרי סגירה:

### דרך 1: Web-Ext (NPM)
```bash
npm install -g web-ext
cd G:\...\segmonto-official
web-ext run  # תשמור זמנית בזמן פיתוח
```

### דרך 2: Signed Extension
צריך:
1. חשבון Mozilla Developer
2. לשלוח ל-AMO (Add-ons store)
3. כ-3-5 ימים לאישור

### דרך 3: Profile עם Temporary מקדמי
1. פתח Firefox
2. Load Temporary → סגור ופתח
3. בפעם הבאה: about:debugging → Temporary Extensions → Load again

---

## ✅ סיימת! Firefox מוכן! 🎉

**הערה:** זה Temporary. רוצה להשמיר? תגיד ואדווה דרך Web-Ext! 🚀
