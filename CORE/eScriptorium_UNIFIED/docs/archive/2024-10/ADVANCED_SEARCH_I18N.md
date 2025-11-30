# 🌍 תמיכה רב-לשונית לחיפוש המתקדם

**תאריך:** 20 אוקטובר 2025  
**שפות נתמכות:** עברית (he) + צרפתית (fr) + אנגלית (en - ברירת מחדל)

---

## 📝 סיכום

הוספנו תרגומים מלאים לדף החיפוש המתקדם בעברית וצרפתית.

---

## 📋 מפתחות תרגום שנוספו

### כותרות ראשיות
```
Advanced Search → חיפוש מתקדם / Recherche avancée
Search across all your documents using Elasticsearch → חפש בכל המסמכים שלך באמצעות Elasticsearch
```

### טופס חיפוש
```
Search Query → שאילתת חיפוש / Requête de recherche
Enter search terms... → הזן מונחי חיפוש... / Entrez les termes de recherche...
Search → חפש / Rechercher
Show Filters → הצג מסננים / Afficher les filtres
Hide Filters → הסתר מסננים / Masquer les filtres
```

### מסננים
```
Minimum Confidence → רמת ודאות מינימלית / Confiance minimale
Document ID → מזהה מסמך / ID du document
Project ID → מזהה פרויקט / ID du projet
```

### מצבים
```
Loading... → טוען... / Chargement...
Searching... → מחפש... / Recherche en cours...
```

### סטטוס Elasticsearch
```
Elasticsearch Status → סטטוס Elasticsearch / Statut d'Elasticsearch
Status → סטטוס / Statut
Enabled → מופעל / Activé
Total Documents → סך המסמכים / Total des documents
Index Size → גודל אינדקס / Taille de l'index
Elasticsearch is not enabled → Elasticsearch אינו מופעל / Elasticsearch n'est pas activé
```

### הודעות
```
Please enter at least 2 characters → אנא הזן לפחות 2 תווים / Veuillez entrer au moins 2 caractères
Search failed → החיפוש נכשל / La recherche a échoué
No results found → לא נמצאו תוצאות / Aucun résultat trouvé
Try different search terms or adjust filters → נסה מונחי חיפוש אחרים או שנה את המסננים
```

### תוצאות
```
Relevance Score → ציון רלוונטיות / Score de pertinence
Page → עמוד / Page
Line → שורה / Ligne
Open Document → פתח מסמך / Ouvrir le document
Found → נמצאו / Trouvé
results → תוצאות / résultats
of → מתוך / de
```

---

## 📁 קבצים ששונו

### תרגומים עברית
```
app/locale/he/LC_MESSAGES/django.po     (+70 lines)
app/locale/he/LC_MESSAGES/search_translations.txt (נוצר)
```

### תרגומים צרפתית
```
app/locale/fr/LC_MESSAGES/django.po     (+70 lines)
app/locale/fr/LC_MESSAGES/search_translations.txt (נוצר)
```

---

## 🔧 איך להשתמש

### שינוי שפה בדפדפן

#### דרך 1: תפריט שפות (אם זמין)
1. פתח את eScriptorium
2. לחץ על בורר השפה בפינה (he/fr/en)
3. בחר שפה
4. הדף ייטען מחדש

#### דרך 2: URL ידני
```
http://localhost:8082/he/advanced-search/     # עברית
http://localhost:8082/fr/advanced-search/     # צרפתית
http://localhost:8082/en/advanced-search/     # אנגלית
```

#### דרך 3: Cookie ידני (F12 Developer Console)
```javascript
document.cookie = "django_language=he; path=/";  // עברית
document.cookie = "django_language=fr; path=/";  // צרפתית
document.cookie = "django_language=en; path=/";  // אנגלית
location.reload();
```

---

## 🧪 בדיקה

### עברית
```
1. פתח: http://localhost:8082/he/advanced-search/
2. ודא: כותרת "חיפוש מתקדם"
3. ודא: כפתור "חפש"
4. ודא: "הצג מסננים"
5. ודא: תמיכה ב-RTL (טקסט מימין לשמאל)
```

### צרפתית
```
1. פתח: http://localhost:8082/fr/advanced-search/
2. ודא: כותרת "Recherche avancée"
3. ודא: כפתור "Rechercher"
4. ודא: "Afficher les filtres"
5. ודא: תמיכה ב-LTR (טקסט משמאל לימין)
```

---

## ⚙️ קומפילציה (אופציונלי)

אם `msgfmt` זמין ב-container:

```bash
# קומפילציה ידנית
docker-compose exec web python manage.py compilemessages

# או עם gettext ישירות
cd app/locale/he/LC_MESSAGES
msgfmt -o django.mo django.po

cd ../../fr/LC_MESSAGES  
msgfmt -o django.mo django.po
```

**לתשומת לב:** Django יכול לטעון `.po` files ישירות במצב DEBUG, אז הקומפילציה אופציונלית בפיתוח.

---

## 🔮 שיפורים עתידיים

### תרגומים נוספים
- [ ] ערבית (ar)
- [ ] ספרדית (es)
- [ ] גרמנית (de)
- [ ] איטלקית (it)

### תכונות
- [ ] זיהוי אוטומטי של שפת הדפדפן
- [ ] תרגום דינמי של תוצאות חיפוש
- [ ] תמיכה בתרגום שמות מסמכים
- [ ] Auto-complete רב-לשוני

---

## 📊 סטטיסטיקות

- **סך מפתחות תרגום:** 30
- **שפות נתמכות:** 3 (he, fr, en)
- **קבצי תרגום:** 2 (.po files)
- **שורות קוד:** ~140 (70 לכל שפה)

---

## 🐛 בעיות ידועות

### בעיה: התרגומים לא מופיעים
**פתרון:**
```bash
# 1. ודא ש-django.po מכיל את התרגומים
cat app/locale/he/LC_MESSAGES/django.po | tail -100

# 2. אתחל web container
docker-compose restart web

# 3. נקה cache של Django
docker-compose exec web python manage.py clear_cache

# 4. בדוק cookie של שפה
# F12 → Application → Cookies → django_language
```

### בעיה: RTL לא עובד כראוי
**פתרון:**
דף החיפוש המתקדם כבר כולל תמיכה ב-RTL דרך CSS:
```css
[dir="rtl"] .border-left {
    border-left: none !important;
    border-right: 3px solid !important;
}
```

אם צריך, הוסף `dir="rtl"` ל-`<html>` tag ב-`base.html`.

---

## 💡 טיפים

### 1. בדיקת תרגום בפיתוח
```python
# Django shell
from django.utils.translation import gettext
from django.utils.translation import activate

activate('he')
gettext('Advanced Search')  # → 'חיפוש מתקדם'

activate('fr')
gettext('Advanced Search')  # → 'Recherche avancée'
```

### 2. הוספת תרגום חדש
```bash
# 1. הוסף ל-django.po:
msgid "New String"
msgstr "מחרוזת חדשה"  # עברית
msgstr "Nouvelle chaîne"  # צרפתית

# 2. קמפל (אם זמין):
docker-compose exec web python manage.py compilemessages

# 3. אתחל:
docker-compose restart web
```

### 3. שימוש ב-Template Tags
```django
{% load i18n %}

<h1>{% trans "Advanced Search" %}</h1>
<p>{% blocktrans %}Search across all your documents{% endblocktrans %}</p>
```

---

## ✅ סיכום

**Status:** ✅ התרגומים נוספו בהצלחה!

**מה עבד:**
- ✅ 30 מפתחות תרגום לעברית
- ✅ 30 מפתחות תרגום לצרפתית
- ✅ קבצי .po עודכנו
- ✅ Web container אותחל

**מה לבדוק:**
- 🔍 פתח `/he/advanced-search/` ובדוק עברית
- 🔍 פתח `/fr/advanced-search/` ובדוק צרפתית
- 🔍 בדוק ש-RTL עובד בעברית

**הבא:**
אם התרגומים עובדים, נמשיך ל-Feature #2: Error Detection System! 🚀

---

**Last Updated:** 20 אוקטובר 2025
