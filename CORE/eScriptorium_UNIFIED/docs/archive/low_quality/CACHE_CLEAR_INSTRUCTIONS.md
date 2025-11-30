# הוראות ניקוי Cache חזק בדפדפן

## Chrome / Edge / Brave:
1. **פתח DevTools**: לחץ F12
2. **לחץ לחיצה ארוכה** על כפתור הרענון (ליד שורת הכתובת)
3. בחר **"Empty Cache and Hard Reload"** (רק זמין כש-DevTools פתוח!)

## Firefox:
1. **פתח DevTools**: לחץ F12
2. לך ל-**Network** tab
3. סמן **"Disable Cache"** למעלה
4. לחץ Ctrl+Shift+R

## אלטרנטיבה (כל הדפדפנים):
1. **פתח DevTools**: F12
2. לך ל-**Application** tab (Chrome/Edge) או **Storage** (Firefox)
3. לחץ על **"Clear site data"** / **"Clear storage"**
4. סמן **הכל** (Cookies, Cache, Local Storage, Session Storage)
5. לחץ **"Clear data"**
6. סגור את הדפדפן לגמרי
7. פתח מחדש ולך ל-http://localhost:8082/document/16/part/251/edit/

## בדיקה שה-cache נוקה:
1. פתח DevTools (F12)
2. לך ל-**Network** tab
3. רענן את הדף
4. חפש את `editor.js` ברשימה
5. צריך לראות **"200"** ולא **"(disk cache)"** ליד הקובץ
6. גודל הקובץ צריך להיות **3.4 MB**
