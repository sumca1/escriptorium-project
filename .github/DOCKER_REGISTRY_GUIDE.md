# 🐳 Docker Registry Setup - מדריך מלא

## 📋 סקירה כללית

ה-workflow הזה יוצר **קובץ התקנה** להקמת Docker Registry מקומי על המחשב שלך.

### מה זה עושה?

1. ✅ יוצר סקריפט PowerShell (Windows)
2. ✅ יוצר סקריפט Bash (Linux/Mac)  
3. ✅ יוצר README מפורט
4. ✅ מארז הכל ל-Artifact להורדה

## 🚀 איך להשתמש?

### שלב 1: הרץ את ה-Workflow

1. לך ל-[GitHub Actions](https://github.com/sumca1/escriptorium-project/actions)
2. בחר **"Setup Docker Registry"**
3. לחץ **"Run workflow"**
4. המתן ~30 שניות

### שלב 2: הורד את הקובץ

1. לחץ על הריצה שהסתיימה
2. גלול למטה ל-**Artifacts**
3. הורד **"docker-registry-setup.zip"**
4. חלץ את הקובץ

### שלב 3: הפעל את ההתקנה

**Windows:**
```powershell
cd docker-registry-setup
.\setup-registry.ps1
```

**Linux/Mac:**
```bash
cd docker-registry-setup
chmod +x setup-registry.sh
./setup-registry.sh
```

## ⚙️ הגדרות Docker (חובה!)

לאחר ההתקנה, **חובה** להגדיר את Docker:

### Windows:
1. פתח **Docker Desktop**
2. Settings → Docker Engine
3. הוסף:
```json
{
  "insecure-registries": ["localhost:5000"]
}
```
4. **Restart Docker Desktop**

### Linux:
```bash
sudo nano /etc/docker/daemon.json
```
הוסף:
```json
{
  "insecure-registries": ["localhost:5000"]
}
```
הפעל מחדש:
```bash
sudo systemctl restart docker
```

## 📦 שימוש בסיסי

### Push תמונה מ-GitHub ל-Registry מקומי:

```powershell
# 1. Pull מ-GitHub
docker pull ghcr.io/sumca1/escriptorium-project:latest

# 2. Tag לRegistry מקומי
docker tag ghcr.io/sumca1/escriptorium-project:latest localhost:5000/escriptorium:latest

# 3. Push לRegistry מקומי
docker push localhost:5000/escriptorium:latest
```

### עדכן docker-compose להשתמש ב-Registry מקומי:

```yaml
services:
  web:
    image: localhost:5000/escriptorium:latest  # במקום ghcr.io/...
    # ...
```

## 🎯 יתרונות

✅ **עקיפת NetFree** - כל ה-pulls יהיו מקומיים  
✅ **מהירות** - אין צורך ב-internet לכל build  
✅ **גרסאות מרובות** - שמור כמה שרוצה גרסאות  
✅ **פרטיות** - התמונות לא עוזבות את המחשב שלך

## 🔧 פקודות מתקדמות

### בדוק סטטוס:
```powershell
docker ps | Select-String "registry"
```

### רשימת תמונות ב-Registry:
```powershell
curl http://localhost:5000/v2/_catalog
```

### עצור Registry:
```powershell
.\setup-registry.ps1 -Stop
```

### הסר לגמרי:
```powershell
.\setup-registry.ps1 -Remove
```

## ⚠️ שים לב

- Registry זה **לא מאובטח** - רק לשימוש **מקומי**
- **אל תחשוף** לאינטרנט
- התמונות נשמרות ב-Docker Volume: `docker_registry`

## 🔄 Workflow להמשך עבודה

1. **Build ב-GitHub Actions** → תמונה חדשה ב-ghcr.io
2. **Pull מ-GitHub** → למחשב המקומי
3. **Push ל-Registry מקומי** → localhost:5000
4. **שימוש** → כל ה-builds מקומיים ללא חסימות!

## 📞 תמיכה

אם משהו לא עובד:
1. בדוק ש-Docker Desktop רץ
2. בדוק ש-`insecure-registries` מוגדר
3. הפעל מחדש את Docker Desktop
4. נסה לרוץ: `docker logs docker-registry`
