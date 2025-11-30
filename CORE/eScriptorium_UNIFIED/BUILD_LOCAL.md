# 🔧 Local Build Guide - NetFree Bypass

מדריך לבנייה מקומית של Docker images עם עקיפת חסימות NetFree.

## 📋 הבעיה

NetFree חוסם:
- ❌ `docker.io` (Docker Hub) - תמונות base
- ❌ `pypi.org` - Python packages  
- ❌ `registry.npmjs.org` - NPM packages
- ❌ `github.com` - Git repositories

## ✅ הפתרון - 3 שלבים

### שלב 1: GitHub Actions מוריד ומעלה תמונות base

GitHub Actions **לא חסום** ע"י NetFree, אז הוא:

1. מושך תמונות מ-Docker Hub:
   - `node:18-alpine`
   - `registry:2`
   - `postgres:15-alpine`
   - `python:3.10-slim`

2. דוחף אותן ל-GitHub Container Registry:
   - `ghcr.io/sumca1/escriptorium-project/node:18-alpine`
   - `ghcr.io/sumca1/escriptorium-project/registry:latest`
   - וכו'

**זה כבר קורה אוטומטית בכל push!**

### שלב 2: משיכת התמונות למחשב המקומי

```powershell
# משוך את כל התמונות מ-GitHub
docker pull ghcr.io/sumca1/escriptorium-project/node:18-alpine
docker pull ghcr.io/sumca1/escriptorium-project/registry:latest
docker pull ghcr.io/sumca1/escriptorium-project/postgres:15-alpine
docker pull ghcr.io/sumca1/escriptorium-project/python:3.10-slim
```

### שלב 3: העברה ל-Registry המקומי

```powershell
# Tag לRegistry מקומי
docker tag ghcr.io/sumca1/escriptorium-project/node:18-alpine localhost:5001/node:18-alpine
docker tag ghcr.io/sumca1/escriptorium-project/postgres:15-alpine localhost:5001/postgres:15-alpine
docker tag ghcr.io/sumca1/escriptorium-project/python:3.10-slim localhost:5001/python:3.10-slim

# Push לRegistry מקומי
docker push localhost:5001/node:18-alpine
docker push localhost:5001/postgres:15-alpine
docker push localhost:5001/python:3.10-slim
```

## 🏗️ בנייה מקומית

עכשיו אפשר לבנות **מקומית** עם תמונות מה-Registry המקומי:

```powershell
cd CORE\eScriptorium_UNIFIED

# בניה עם Dockerfile שמשתמש ב-localhost:5001
docker build -t localhost:5001/escriptorium:mybuild -f Dockerfile.localregistry .
```

## 🔄 Workflow מלא

```powershell
# 1. וודא ש-Registry המקומי רץ
docker ps | Select-String "docker-registry"

# 2. משוך תמונות מ-GitHub
docker pull ghcr.io/sumca1/escriptorium-project/node:18-alpine

# 3. העבר ל-Registry מקומי
docker tag ghcr.io/sumca1/escriptorium-project/node:18-alpine localhost:5001/node:18-alpine
docker push localhost:5001/node:18-alpine

# 4. בנה מקומית
cd CORE\eScriptorium_UNIFIED
docker build -t localhost:5001/escriptorium:v2 -f Dockerfile.localregistry .

# 5. השתמש בתמונה החדשה
docker run -d localhost:5001/escriptorium:v2
```

## 📦 סקריפט אוטומציה

יצרנו סקריפט שעושה את כל זה אוטומטית:

```powershell
.\DEPLOYMENT_MANAGEMENT\scripts\utilities\pull-and-mirror-images.ps1
```

זה ימשוך את כל התמונות מ-GitHub ויעביר אותן ל-Registry המקומי.

## 🎯 יתרונות

✅ **עצמאות מלאה** - לא תלוי באינטרנט אחרי ההורדה הראשונה  
✅ **מהירות** - כל התמונות מקומיות  
✅ **גרסאות מרובות** - שמור כמה שרוצה builds  
✅ **ניפוי באגים** - בנה וטעה מקומית  
✅ **עקיפת NetFree** - 100% bypass

## ⚠️ שים לב

- Python packages עדיין יורדו מ-PyPI בזמן build
- אם גם זה חסום, תצטרך pip mirror מקומי
- npm packages יורדו מ-npmjs.org
- אם גם זה חסום, תצטרך npm mirror

## 🔧 פתרונות מתקדמים

### PyPI Mirror מקומי

אם PyPI חסום:
```powershell
# הורד packages במקום אחר והעתק
pip download -r requirements.txt -d ./packages
# העתק לקונטיינר ו:
pip install --no-index --find-links=./packages -r requirements.txt
```

### NPM Mirror מקומי

אם NPM חסום:
```powershell
# הורד node_modules במקום אחר והעתק
npm install
# העתק את node_modules/ לפרויקט
```

## 📞 תמיכה

אם משהו לא עובד:
1. בדוק ש-Registry המקומי רץ: `docker ps | grep registry`
2. בדוק ש-daemon.json מוגדר: `"insecure-registries": ["localhost:5001"]`
3. הפעל מחדש Docker Desktop
4. נסה pull ידני: `docker pull ghcr.io/sumca1/escriptorium-project/node:18-alpine`
