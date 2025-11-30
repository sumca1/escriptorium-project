# 🚀 הוראות להעלאת תמונות Docker ל-GitHub

## מטרה
לבנות את תמונות ה-Docker ב-GitHub Actions ולהוריד אותן דרך GitHub Container Registry (ghcr.io) - **לא חסום ב-NetFree!**

---

## שלב 1: הכנת הפרויקט

### 1.1 צור repository ב-GitHub
```bash
# אם עדיין אין repository:
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### 1.2 העלה את הקוד
```bash
git add .
git commit -m "Initial commit with eScriptorium"
git push -u origin main
```

---

## שלב 2: הפעלת GitHub Actions

### 2.1 ב-GitHub Repository:
1. לך ל-**Settings** → **Actions** → **General**
2. תחת **Workflow permissions**, בחר:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**
3. שמור

### 2.2 הרץ את ה-Workflow:
1. לך ל-**Actions** tab
2. בחר **Build and Push Docker Images**
3. לחץ **Run workflow** → **Run workflow**
4. המתן 10-15 דקות לבנייה

---

## שלב 3: שימוש בתמונות

### 3.1 התמונה תהיה זמינה ב:
```
ghcr.io/YOUR_USERNAME/YOUR_REPO:latest
```

### 3.2 עדכן את docker-compose.yml:
במקום:
```yaml
build:
  context: ../../../CORE/eScriptorium_UNIFIED
  dockerfile: Dockerfile
```

השתמש ב:
```yaml
image: ghcr.io/YOUR_USERNAME/YOUR_REPO:latest
```

### 3.3 הורד את התמונה:
```powershell
# התמונה ציבורית - לא צריך authentication
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO:latest
```

---

## שלב 4: הרצת הסביבה

```powershell
cd DEPLOYMENT_MANAGEMENT\environments\dev
docker-compose up -d
```

**זהו! 🎉**

---

## Troubleshooting

### אם התמונה private:
```powershell
# צור Personal Access Token ב-GitHub
# Settings → Developer settings → Personal access tokens → Tokens (classic)
# סמן: read:packages

docker login ghcr.io -u YOUR_USERNAME
# Password: הדבק את ה-token
```

### בדיקת תמונות זמינות:
https://github.com/YOUR_USERNAME/YOUR_REPO/pkgs/container/YOUR_REPO

---

## עדכון אוטומטי

כל push ל-branch `main` יבנה תמונה חדשה עם:
- ✅ Tag `latest`
- ✅ Tag עם שם ה-branch
- ✅ Tag עם commit SHA

דוגמה:
```
ghcr.io/username/repo:latest
ghcr.io/username/repo:main-abc1234
ghcr.io/username/repo:main
```
