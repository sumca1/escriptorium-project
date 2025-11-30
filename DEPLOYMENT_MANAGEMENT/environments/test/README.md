# 🟡 TEST Environment - סביבת בדיקות

## 🎯 מטרה
סביבה לבדיקות לפני deploy - **snapshot קפוא** של הקוד

## ⚡ תכונות
- ✅ **Frozen Build** - קוד קפוא בזמן build
- ✅ **Production-like** - מתנהג כמו ייצור
- ✅ **Automated Tests** - pytest, coverage, CI/CD
- ✅ **Stable** - לא משתנה במהלך בדיקות
- ⚠️ **צריך rebuild** - לכל שינוי קוד

## 🚀 הפעלה מהירה

### Build + Up:
```powershell
cd DEPLOYMENT_MANAGEMENT\environments\test
docker-compose up -d --build
```

Build: **~2-3 דקות**

### Up בלבד (אם כבר בנוי):
```powershell
docker-compose up -d
```

### Down:
```powershell
docker-compose down
```

## 🔗 נקודות גישה

- **Application:** <http://localhost:8081>
- **PostgreSQL:** localhost:5433
- **Redis:** localhost:6380

## 🧪 הרצת טסטים

### כל הטסטים:
```powershell
docker-compose exec web pytest
```

### טסט ספציפי:
```powershell
docker-compose exec web pytest app/tests/test_views.py -v
```

### עם coverage:
```powershell
docker-compose exec web pytest --cov=app --cov-report=html
```

## 📊 תרחיש בדיקה טיפוסי

### 1. סיימת feature ב-dev
```powershell
# עבדת כל היום ב-dev, הכל עובד שם
```

### 2. Build ב-test
```powershell
cd DEPLOYMENT_MANAGEMENT\environments\test
docker-compose up -d --build
# Build: 2-3 דקות - יוצר snapshot של הקוד
```

### 3. הרץ טסטים
```powershell
docker-compose exec web pytest -v
# ✅ All tests passed!
```

### 4. בדיקה ידנית
```
http://localhost:8081
# בדוק את הfeature החדש
```

### 5. מצאת bug?
```powershell
# חזור ל-dev, תקן, חזור לשלב 2
```

### 6. הכל עובד? → Deploy!
```powershell
# עבור ל-prod
```

## ⏱️ זמני ביצוע

| פעולה | זמן |
|-------|-----|
| Build מלא | 2-3 דקות |
| Start | 20 שניות |
| Tests (כל הסוויטה) | 1-5 דקות |
| Stop | 10 שניות |

## 🔄 Workflow טיפוסי

### סוף יום עבודה:

```
17:00 → docker-compose up -d --build
17:03 → docker-compose exec web pytest
17:08 → בדיקה ידנית ב-http://localhost:8081
17:15 → ✅ הכל עובד → commit + push
17:16 → docker-compose down
```

### תיקון bug מהיר:

```
1. מצאתי bug ב-test
2. חזרתי ל-dev, תיקנתי (5 דקות)
3. Build מחדש ב-test (2 דקות)
4. Tests עברו ✅
5. Deploy!
```

## 🐛 פתרון בעיות

### טסטים נכשלים:
```powershell
# לוגים מפורטים:
docker-compose exec web pytest -vv --tb=long

# טסט ספציפי:
docker-compose exec web pytest app/tests/test_views.py::test_login -vv
```

### Build נכשל:
```powershell
# נקה הכל:
docker-compose down -v
docker system prune -f

# Build מחדש:
docker-compose up -d --build
```

### Database ריק:
```powershell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py loaddata fixtures/test_data.json
```

## 📁 מבנה קבצים

```
test/
├── docker-compose.yml    ← הגדרות containers
├── .env.test            ← משתני סביבה
├── pytest.ini           ← הגדרות pytest
└── README.md            ← המדריך הזה
```

## 🎓 טיפים

1. **הרץ טסטים לפני כל commit:**
   ```powershell
   docker-compose exec web pytest
   ```

2. **השתמש ב-fixtures:**
   ```python
   @pytest.fixture
   def test_user():
       return User.objects.create(username='test')
   ```

3. **בדוק coverage:**
   ```powershell
   docker-compose exec web pytest --cov=app --cov-report=term-missing
   ```

4. **CI/CD Integration:**
   - GitHub Actions יכול להריץ את test אוטומטית
   - הוסף `.github/workflows/test.yml`

## ⚠️ חשוב!

**סביבה זו לבדיקות בלבד!**

- ✅ הרץ לפני כל deploy
- ✅ הרץ ב-CI/CD pipeline
- ✅ מייצג ייצור
- ❌ לא לייצור אמיתי

## 🔄 מעבר בין סביבות

**מ-dev ל-test:**
```powershell
# סיימת ב-dev? בדוק ב-test:
cd ..\test
docker-compose up -d --build
```

**מ-test ל-prod:**
```powershell
# טסטים עברו? Deploy לייצור:
cd ..\prod
docker-compose up -d --build
```

---

**רוצה לחזור לפיתוח?** → עבור ל-`../dev/`  
**מוכן לייצור?** → עבור ל-`../prod/`
