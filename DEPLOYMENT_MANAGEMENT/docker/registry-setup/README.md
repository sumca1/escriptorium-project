# 🐳 Docker Registry Local Setup

התקנה מקומית של Docker Registry פרטי.

## 🚀 התקנה מהירה

```powershell
.\setup-registry.ps1
```

זהו! Registry יעלה על `localhost:5000`

## ⚙️ הגדרת Docker (חובה!)

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

## 📦 שימוש

### Push תמונה מ-GitHub ל-Registry מקומי:

```powershell
# 1. Pull מ-GitHub
docker pull ghcr.io/sumca1/escriptorium-project:latest

# 2. Tag לRegistry מקומי
docker tag ghcr.io/sumca1/escriptorium-project:latest localhost:5000/escriptorium:latest

# 3. Push לRegistry מקומי
docker push localhost:5000/escriptorium:latest
```

### שימוש ב-docker-compose:

```yaml
services:
  web:
    image: localhost:5000/escriptorium:latest
    # ...
```

## 🔧 פקודות מתקדמות

```powershell
# הפעלה עם פורט אחר
.\setup-registry.ps1 -Port 5001

# עצירה
.\setup-registry.ps1 -Stop

# הסרה מלאה
.\setup-registry.ps1 -Remove

# בדיקת סטטוס
docker ps | Select-String "registry"

# רשימת תמונות
curl http://localhost:5000/v2/_catalog
```

## 🎯 יתרונות

✅ **עקיפת NetFree** - כל ה-pulls מקומיים  
✅ **מהירות** - אין צורך ב-internet  
✅ **גרסאות מרובות** - שמור כמה שרוצה  
✅ **פרטיות** - התמונות לא עוזבות את המחשב

## ⚠️ שים לב

- Registry זה **לא מאובטח** - רק לשימוש **מקומי**
- **אל תחשוף** לאינטרנט
- התמונות נשמרות ב-Docker Volume: `docker_registry`

## 🔄 Workflow מומלץ

1. **Build ב-GitHub Actions** → תמונה ב-ghcr.io
2. **Pull מ-GitHub** → למחשב המקומי (פעם אחת)
3. **Push ל-Registry מקומי** → localhost:5000
4. **שימוש** → כל ה-builds ללא חסימות!
