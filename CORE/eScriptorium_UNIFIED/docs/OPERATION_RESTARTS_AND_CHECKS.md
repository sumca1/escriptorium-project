# Operation log: restarts, builds and checks

This document captures the manual operations we performed to recover and validate the eScriptorium CLEAN environment, plus recommended commands and troubleshooting notes so the steps can be repeated reliably.

Summary (high level)
- Ensured Docker Desktop is running after a host reboot.
- Confirmed no containers were running, started services with `docker-compose up -d`.
- Observed failing containers (exit codes 255 / 1) and inspected logs.
- Fixed missing `entrypoint.sh` issue by rebuilding images and ensuring `entrypoint.sh` is part of the build context.
- Performed a full no-cache build and restarted the stack.
- Validated services: web (nginx -> localhost:8082), Flower (localhost:5555), db, redis, channelserver, mail.

Exact commands executed (run from the `eScriptorium_CLEAN` directory):

- Check Docker Desktop / processes (PowerShell):
  - Get-Process | Where-Object {$_.Name -like "*docker*"}

- Check docker-compose status (may hang if Docker Desktop is not ready):
  - docker-compose ps

- Check raw docker containers:
  - docker ps
  - docker ps -a | findstr "escriptorium_clean"

- Inspect logs for a crashed container (example):
  - docker logs escriptorium_clean-channelserver-1

- If `entrypoint.sh: no such file or directory` or similar errors appear:
  - Confirm `app/entrypoint.sh` exists locally
  - Ensure Dockerfile copies it into the image (or that `docker-compose build` sees it in context)

- Bring the stack down (clean stop & remove containers):
  - docker-compose down

- Rebuild images from scratch (no cache):
  - docker-compose build --no-cache

- Start the stack:
  - docker-compose up -d

- Verify running containers and ports:
  - docker ps
  - curl -I http://localhost:8082
  - curl -I http://localhost:5555

Observed issues and how they were resolved
- Symptom: `docker-compose ps` hung or returned a pipe error after reboot.
  - Cause: Docker Desktop service hadn't fully started or Docker engine pipe not available.
  - Fix: Start Docker Desktop and wait (30s+), then retry. Use `Get-Process` to confirm Docker Desktop processes are present.

- Symptom: channelserver (and several celery workers) exited with code 255; nginx exited with code 1.
  - Investigation: `docker logs <container>` returned `exec /usr/src/app/entrypoint.sh: no such file or directory`.
  - Cause: Docker image was built without the `entrypoint.sh` copied into the final image (context/cache issue), or the container was created before the file was present.
  - Fix: `docker-compose down` then `docker-compose build --no-cache` and `docker-compose up -d`. Confirm `entrypoint.sh` is present in the `app/` folder in the repo and referenced by the Dockerfile.

Validation checklist
- [ ] Docker Desktop running on host
- [x] `docker-compose build --no-cache` completed successfully
- [x] `docker-compose up -d` started all services
- [x] `curl -I http://localhost:8082` -> HTTP 200 (site reachable)
- [x] Flower reachable at http://localhost:5555 (service returns 405 to HEAD, but web UI works in browser)

- Recommendations
- Automate the start and check sequence with a small local utility included in this repo under `ops-ui/`.

Ops UI (optional)
- A minimal Node/Express app is included at `ops-ui/` which exposes a small HTML page and a restricted backend to run safe docker/docker-compose commands from the repository root. It is intentionally minimal and should only be used on a trusted admin host.

To run the Ops UI (Windows / PowerShell):

```powershell
cd path\to\eScriptorium_CLEAN\ops-ui
npm install
npm start
# OR use the helper:
./run_ops_ui.ps1
```

Then open: http://localhost:3001

Security note: the web UI executes system commands. Do not expose this service beyond localhost. Consider adding HTTP auth or using system service account restrictions.

Next steps
- Move repeated troubleshooting/smoke checks into a script or CI job if you want automated health checks.
- Add brief unit tests for startup scripts that can run locally (e.g., check entrypoint file presence before build).

Appendix: quick troubleshooting commands

- Show recent logs for a service (tail + follow):
  - docker logs -f escriptorium_clean-web-1

- Recreate a single service and its image:
  - docker-compose build --no-cache web
  - docker-compose up -d web

---
Generated on: 2025-09-17

Recorded interactive sequence (Hebrew)

אחלה! הפעלה מחדש למחשב יכולה לפתור הרבה בעיות עם Docker. בוא ננסה שוב לבדוק את סטטוס הקונטיינרים:


cd "G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN" && docker-compose ps
נראה שDocker Desktop עוד לא התחיל אחרי הפעלת המחשב מחדש. בוא נבדוק אם Docker Desktop רץ ונתחיל אותו אם צריך:


Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
Docker Desktop לא רץ. בוא נתחיל אותו:


Start-Process "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"
עכשיו בוא נחכה כמה שניות לDocker Desktop להיטען ואז נבדוק שוב:


Start-Sleep -Seconds 30
עכשיו בוא ננסה שוב לבדוק את Docker:


docker --version
נראה שעדיין Docker לא מוכן. בוא ננסה גישה שונה - נבדוק אם יש תהליכי Docker ואז נבדוק את הסטטוס:


Get-Process | Where-Object {$_.Name -match "docker"}
מעולה! Docker Desktop רץ. עכשיו בוא ננסה לבדוק את הקונטיינרים שלנו:


cd "G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN" && docker-compose ps
הפקודה עדיין לא הגיבה. בוא ננסה בגישה שונה:


docker ps
אין קונטיינרים רצים כרגע. זה אומר שלאחר הפעלת המחשב מחדש, הקונטיינרים שלנו עצרו. בוא נתחיל אותם מחדש:


docker-compose up -d
מעולה! כל השירותים הופעלו בהצלחה! עכשיו בוא נבדוק את הסטטוס שלהם:


docker-compose ps
אני רואה שלא כל השירותים מופיעים ברשימה. בוא נבדוק עם docker ps רגיל לראות את כל הקונטיינרים:


docker ps
אני רואה שלא כל הקונטיינרים מופיעים. בוא נבדוק מה קורה עם הקונטיינרים שלא רצים:


docker ps -a | findstr "escriptorium_clean"
אני רואה שיש כמה קונטיינרים שהתרסקו עם exit code 255 וחלק עם exit code 1. בוא נבדוק את הלוגים של אחד מהקונטיינרים שהתרסק:


docker logs escriptorium_clean-channelserver-1
אהה! הבעיה היא שהקונטיינר לא מוצא את entrypoint.sh. בוא נבדוק מה יש בתיקיית app:

Read app

הקובץ entrypoint.sh קיים. אבל נראה שיש בעיה עם הרשאות או עם הדרך שהוא מועתק לקונטיינר. בוא נבדוק את הרשאות:


cd "G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\app" && Get-ChildItem entrypoint.sh | Select-Object Name, Length, LastWriteTime
הקובץ קיים ונראה בסדר. הבעיה היא כנראה שהקונטיינר נוצר לפני שהקובץ היה זמין או שיש בעיה עם הרשאות. בוא נעשה build מחדש של הקונטיינר:


cd "G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN" && docker-compose down
עכשיו בוא נעשה build מחדש של הקונטיינרים:


docker-compose build --no-cache
Continue waiting for docker-compose build --no-cache?
This will continue to poll for output to determine when the terminal becomes idle for up to 2 minutes.

מעולה! כל הקונטיינרים נבנו בהצלחה. עכשיו בוא נתחיל אותם:


docker-compose up -d
מצוין! כל השירותים הופעלו בהצלחה. עכשיו בוא נבדוק את הסטטוס שלהם:


docker-compose ps
יופי! כל השירותים רצים בהצלחה כולל הchannel server שהיה לנו בעיה איתו קודם. בוא נעדכן את רשימת המשימות:

Starting (20/21) בדיקת נגישות השירותים

עכשיו בוא נבדוק שהמערכת עובדת ונגישה בדפדפן:


curl -I http://localhost:8082
מצוין! האתר עובד. בוא נבדוק גם את Flower (ניטור Celery):


curl -I http://localhost:5555
זה תקין - זה רק אומר שהשירות רץ אבל לא מקבל HEAD requests. בוא נפתח את הדפדפן לבדוק:

Opened Simple Browser at http://localhost:8082

מעולה! בוא גם נפתח את Flower:

Opened Simple Browser at http://localhost:5555

פנטסטי! כל השירותים עובדים בהצלחה. בוא נסמן את המשימה הזו כמושלמת ונעבור לסיכום הישגים:
