# 🇫🇷 ארכיטקטורת התרגום הצרפתי - eScriptorium המקורי

**תאריך:** 20 אוקטובר 2025  
**מטרה:** להבין את **הכוונה המקורית** - איך eScriptorium תכנן שהתרגום יעבוד

---

## 🎯 השאלות שנחקור

1. ✅ איך eScriptorium חשב לתרגם **Templates (.html)**?
2. ✅ איך eScriptorium חשב לתרגם **Vue Components (.vue)**?
3. ✅ איך eScriptorium חשב לתרגם **JavaScript (.js)**?
4. ✅ איך eScriptorium חשב לתרגם **Python Backend (.py)**?
5. ✅ איך eScriptorium חשב לתרגם **נתוני DB** (Scripts, Typologies)?
6. ⚠️ **למה זה לא הושלם?**

---

## 📋 המתודולוגיה

נעקוב אחרי **ראיות קוד** שמראות כוונת תכנון:

```
1. חיפוש קבצי תצורה (settings.py, webpack.config.js)
2. ניתוח הגדרות i18n
3. בדיקת imports של ספריות תרגום
4. מעקב אחר קונבנציות Django/Vue
5. השוואה לפרויקטים דומים
```

---

## 🔍 שלב 1: Django Templates - הגישה המקורית

### א. חיפוש הגדרות i18n

<function_calls>
<invoke name="run_in_terminal">
<parameter name="command">git show origin/develop:app/escriptorium/settings.py | Select-String "LANGUAGE|LOCALE|I18N" -Context 2,2 | Select-Object -First 50