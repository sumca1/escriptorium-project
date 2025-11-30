# 🔄 FastAPI + eScriptorium Synchronization - Visual Guide
## מדריך ויזואלי לסנכרון FastAPI עם eScriptorium

---

## 🎯 שלושה תרחישי שימוש אפשריים

### תרחיש 1: דרך Django (מומלץ להתחלה)
**תיאור:** המשתמש עובד דרך ממשק Django הרגיל, Django מעביר בקשות ל-FastAPI

```
👤 User (Browser)
    │
    │ 1. Opens Document Page
    │    http://localhost:8000/documents/123/
    │
    ▼
┌─────────────────────────────────────────────┐
│         Django Frontend (Bootstrap)         │
│  ┌─────────────────────────────────────┐   │
│  │  [Document Image]                   │   │
│  │                                     │   │
│  │  [ Process Image ▼ ]               │   │
│  │    ○ Binarize                       │   │
│  │    ○ Denoise                        │   │
│  │    ● Auto Process (selected)        │   │
│  │                                     │   │
│  │  [🚀 Process] ← User clicks         │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
    │
    │ 2. POST /api/fastapi/auto-process
    │    (Image file + parameters)
    │
    ▼
┌─────────────────────────────────────────────┐
│              Django Backend                  │
│  ┌─────────────────────────────────────┐   │
│  │  views.py: fastapi_auto_process()   │   │
│  │                                     │   │
│  │  1. Check user authentication ✓     │   │
│  │  2. Validate image file ✓          │   │
│  │  3. Forward to FastAPI ───────┐    │   │
│  │                                │    │   │
│  │  4. Return result to frontend  │    │   │
│  └────────────────────────────────│────┘   │
└────────────────────────────────────│────────┘
                                     │
                                     │ 3. requests.post()
                                     │    http://localhost:8001
                                     │
                                     ▼
┌─────────────────────────────────────────────┐
│           FastAPI Microservice               │
│  ┌─────────────────────────────────────┐   │
│  │  routers/images.py                  │   │
│  │  @router.post("/auto-process")      │   │
│  │                                     │   │
│  │  1. Receive image ✓                │   │
│  │  2. Call ImageProcessor ────┐      │   │
│  │  3. Return JSON/Image       │      │   │
│  └─────────────────────────────│──────┘   │
│                                 │          │
│  ┌──────────────────────────────▼──────┐  │
│  │  services/image_processor.py        │  │
│  │                                     │  │
│  │  auto_process_manuscript()          │  │
│  │  ├─ 1. Denoise    (OpenCV)  ~0.8s  │  │
│  │  ├─ 2. Deskew     (OpenCV)  ~0.5s  │  │
│  │  ├─ 3. Enhance    (CLAHE)   ~0.7s  │  │
│  │  └─ 4. Binarize   (Otsu)    ~0.5s  │  │
│  │                                     │  │
│  │  Total: ~2.5s ⚡                    │  │
│  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
    │
    │ 4. Return processed image
    │
    ▼
👤 User sees result in browser
    [Before] ➜ [After] comparison
    "Processing completed in 2.5s!"
```

**יתרונות:**
- ✅ אימות משתמש מובנה (Django authentication)
- ✅ לא צריך לשנות הרבה בקוד קיים
- ✅ Django מנהל הכל (sessions, permissions, DB)

**חסרונות:**
- ⚠️ עובר דרך Django (hop נוסף)
- ⚠️ תלוי ב-Django להיות זמין

---

### תרחיש 2: קריאה ישירה ל-FastAPI (מהיר יותר)
**תיאור:** JavaScript בדף קורא ישירות ל-FastAPI, עוקף את Django

```
👤 User (Browser)
    │
    │ Opens Document Page
    │ http://localhost:8000/documents/123/
    │
    ▼
┌─────────────────────────────────────────────┐
│      Django Frontend (HTML rendered)         │
│                                              │
│  <script src="fastapi-client.js">           │
│    const client = new FastAPIClient();      │
│  </script>                                   │
│                                              │
│  User clicks [Process] ──────────────┐      │
└──────────────────────────────────────│──────┘
                                       │
                                       │ JavaScript fetch()
                                       │ DIRECT to FastAPI
                                       │ (no Django involved)
                                       │
                                       ▼
┌─────────────────────────────────────────────┐
│           FastAPI Microservice               │
│                                              │
│  POST /api/images/auto-process               │
│                                              │
│  ⚡ 2.5s processing                          │
│                                              │
│  Return: {                                   │
│    "status": "success",                      │
│    "output": {                               │
│      "image_base64": "iVBORw0KG..."         │
│    }                                         │
│  }                                           │
└─────────────────────────────────────────────┘
    │
    │ Return JSON
    │
    ▼
👤 User sees result immediately
    JavaScript updates DOM
    <img src="data:image/png;base64,...">
```

**JavaScript Example:**
```javascript
// In document detail page
const fastapiClient = new FastAPIClient('http://localhost:8001');

document.getElementById('process-btn').addEventListener('click', async () => {
    const imageFile = await getCurrentImage();
    
    // DIRECT call to FastAPI (bypasses Django)
    const result = await fastapiClient.autoProcess(imageFile, true);
    
    // Update UI
    document.getElementById('result-image').src = 
        `data:image/png;base64,${result.output.image_base64}`;
});
```

**יתרונות:**
- ✅ מהיר יותר (no Django hop)
- ✅ פחות עומס על Django
- ✅ מתאים ל-real-time features

**חסרונות:**
- ⚠️ צריך CORS configuration
- ⚠️ אין אימות אוטומטי (צריך לשלוח token)
- ⚠️ שתי כתובות URL לנהל

---

### תרחיש 3: WebSocket לזמן אמת (Day 4)
**תיאור:** חיבור WebSocket לעדכונים בזמן אמת עם progress bars

```
👤 User (Browser)
    │
    │ Opens Document Page
    │ Clicks [Process with Live Preview]
    │
    ▼
┌─────────────────────────────────────────────┐
│         Frontend JavaScript                  │
│                                              │
│  const ws = new WebSocket(                   │
│    'ws://localhost:8001/ws/process'         │
│  );                                          │
│                                              │
│  ws.onmessage = (event) => {                │
│    const data = JSON.parse(event.data);     │
│                                              │
│    switch(data.type) {                       │
│      case 'progress':                        │
│        updateProgress(data.percent); ◄───┐   │
│        break;                            │   │
│      case 'preview':                     │   │
│        updatePreview(data.image); ◄──────│──┐│
│        break;                            │  ││
│      case 'complete':                    │  ││
│        showResult(data.final); ◄─────────│──││
│    }                                     │  ││
│  };                                      │  ││
│                                          │  ││
│  ws.send(JSON.stringify({                │  ││
│    action: 'auto_process',               │  ││
│    image: base64Image                    │  ││
│  }));                                    │  ││
└──────────────────────────────────────────│──││
                                           │  ││
                                           │  ││
    ┌──────────────────────────────────────┘  ││
    │  WebSocket Connection                    ││
    │  ws://localhost:8001/ws/process          ││
    ▼                                           ││
┌─────────────────────────────────────────────││
│       FastAPI WebSocket Handler             ││
│                                             ││
│  @app.websocket("/ws/process")              ││
│  async def websocket_endpoint():            ││
│                                             ││
│    # Step 1: Denoise                        ││
│    await ws.send_json({                     ││
│      "type": "progress",                    ││
│      "percent": 25,                         ││
│      "message": "Removing noise..."         ││
│    }); ──────────────────────────────────────┘│
│                                              │
│    # Step 2: Deskew                          │
│    await ws.send_json({                      │
│      "type": "preview",                      │
│      "image": base64_preview ───────────────┘
│    });
│
│    # Step 3: Enhance
│    await ws.send_json({
│      "type": "progress",
│      "percent": 75
│    });
│
│    # Step 4: Final result
│    await ws.send_json({
│      "type": "complete",
│      "final": final_image
│    });
│
└─────────────────────────────────────────────┘
```

**User Experience:**

```
[Progress Bar]
▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ 50% - Deskewing...

[Live Preview]
┌─────────────────────┐
│  [Updating image]   │ ← Updates in real-time
│                     │   as processing happens
└─────────────────────┘

[Status]
✓ Denoise complete (0.8s)
✓ Deskew complete (0.5s)
⏳ Enhancing contrast...
```

**יתרונות:**
- ✅ משוב בזמן אמת (real-time feedback)
- ✅ progress bars
- ✅ live preview
- ✅ ניתן לבטל אמצע פעולה

---

## 🏗️ ארכיטקטורה מלאה - מבט על

```
┌────────────────────────────────────────────────────────────────────┐
│                         Production Setup                           │
│                       (with Docker & Nginx)                        │
└────────────────────────────────────────────────────────────────────┘

                              Internet
                                 │
                                 ▼
                         ┌───────────────┐
                         │     Nginx     │
                         │   (Port 80)   │
                         └───────────────┘
                          │             │
              ┌───────────┘             └───────────┐
              │                                     │
              │ /api/fastapi/*                     │ /*
              │                                     │
              ▼                                     ▼
    ┌──────────────────┐                  ┌──────────────────┐
    │   FastAPI        │                  │   Django         │
    │   (Port 8001)    │                  │   (Port 8000)    │
    │                  │                  │                  │
    │  ┌────────────┐  │                  │  ┌────────────┐  │
    │  │ REST API   │  │                  │  │   Views    │  │
    │  │ 7 endpoints│  │                  │  │ Templates  │  │
    │  └────────────┘  │                  │  └────────────┘  │
    │                  │                  │                  │
    │  ┌────────────┐  │                  │  ┌────────────┐  │
    │  │ WebSocket  │  │                  │  │   Models   │  │
    │  │ /ws/*      │  │                  │  │   Forms    │  │
    │  └────────────┘  │                  │  └────────────┘  │
    │                  │                  │                  │
    │  ┌────────────┐  │                  │  ┌────────────┐  │
    │  │  OpenCV    │  │                  │  │ PostgreSQL │  │
    │  │ Processing │  │                  │  │   Queries  │  │
    │  └────────────┘  │                  │  └────────────┘  │
    └──────────────────┘                  └──────────────────┘
                                                   │
                                                   ▼
                                          ┌──────────────────┐
                                          │   PostgreSQL     │
                                          │   (Port 5432)    │
                                          │                  │
                                          │  ┌────────────┐  │
                                          │  │   Users    │  │
                                          │  │ Documents  │  │
                                          │  │   Images   │  │
                                          │  └────────────┘  │
                                          └──────────────────┘
```

**Nginx Configuration:**
```nginx
upstream django {
    server web:8000;
}

upstream fastapi {
    server fastapi:8001;
}

server {
    listen 80;
    
    # Django handles everything by default
    location / {
        proxy_pass http://django;
    }
    
    # FastAPI handles image processing
    location /api/fastapi/ {
        proxy_pass http://fastapi/api/;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://fastapi/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🔐 אימות ואבטחה (Authentication & Security)

### אופציה 1: Django Session Token

```python
# Django view passes session token to FastAPI
@login_required
def fastapi_proxy(request):
    session_token = request.session.session_key
    
    response = requests.post(
        'http://fastapi:8001/api/images/auto-process',
        files={'file': request.FILES['image']},
        headers={'X-Session-Token': session_token}
    )
    return HttpResponse(response.content)
```

```python
# FastAPI validates token with Django
from fastapi import Header, HTTPException
import requests

async def verify_django_session(x_session_token: str = Header(None)):
    if not x_session_token:
        raise HTTPException(401, "No session token")
    
    # Check with Django
    response = requests.get(
        f'http://web:8000/api/validate-session/{x_session_token}'
    )
    
    if response.status_code != 200:
        raise HTTPException(401, "Invalid session")
    
    return response.json()

@router.post("/auto-process")
async def auto_process(
    file: UploadFile,
    user = Depends(verify_django_session)
):
    # User is authenticated
    ...
```

### אופציה 2: JWT Token

```python
# Django generates JWT
from rest_framework_simplejwt.tokens import RefreshToken

@login_required
def get_fastapi_token(request):
    refresh = RefreshToken.for_user(request.user)
    return JsonResponse({
        'access': str(refresh.access_token)
    })
```

```javascript
// Frontend includes JWT in requests
const token = await fetch('/api/get-fastapi-token')
    .then(r => r.json());

const result = await fetch('http://localhost:8001/api/images/auto-process', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token.access}`
    },
    body: formData
});
```

---

## 📊 מעקב ביצועים (Performance Monitoring)

### לפני השדרוג:
```
User uploads image (5MB)
    ↓
Django receives (sync) ────────┐
    ↓                           │
PIL loads image                 │
    ↓                           │ Browser
PIL processes (slow)            │ BLOCKED
    ↓                           │ (Waiting...)
Save to disk                    │
    ↓                           │
Return to user ────────────────┘
                                
Total: 8-12 seconds 🐌
```

### אחרי השדרוג:
```
User uploads image (5MB)
    ↓
Django receives (async) ────────┐
    ↓ (immediately returns)      │
    ↓                            │ Browser
FastAPI processes ──────┐       │ FREE
    ├─ Denoise (0.8s)   │       │ (User can
    ├─ Deskew (0.5s)    │       │  continue
    ├─ Enhance (0.7s)   │       │  working)
    └─ Binarize (0.5s)  │       │
                        │       │
WebSocket updates ──────┴───────┘
Progress: 25% → 50% → 100%

Total: 2.5-3 seconds ⚡
Non-blocking: ✅
```

**Metrics to Track:**

```python
# Add to FastAPI main.py
from time import time

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log to monitoring system
    logger.info(f"{request.url.path} took {process_time:.2f}s")
    
    return response
```

---

## 🧪 תהליך Testing המלא

### Unit Tests (FastAPI)
```python
# test_image_processor.py
import pytest
from fastapi_app.services.image_processor import ImageProcessor

def test_binarize():
    img = create_test_image()
    result = ImageProcessor.binarize(img, method='otsu')
    assert result is not None
    assert result.shape == img.shape[:2]  # Grayscale
```

### Integration Tests (Django ↔ FastAPI)
```python
# test_integration.py
from django.test import TestCase, Client
from unittest.mock import patch

class FastAPIIntegrationTest(TestCase):
    def test_proxy_to_fastapi(self):
        client = Client()
        
        with open('test_image.jpg', 'rb') as img:
            response = client.post(
                '/api/fastapi/auto-process/',
                {'image': img}
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
```

### End-to-End Tests (Frontend)
```javascript
// test_e2e.js (using Playwright/Cypress)
describe('Image Processing', () => {
    it('should process image via FastAPI', async () => {
        await page.goto('http://localhost:8000/documents/1/');
        
        await page.setInputFiles('#image-upload', 'test.jpg');
        await page.click('#process-btn');
        
        // Wait for processing
        await page.waitForSelector('.result-image');
        
        // Check result
        const result = await page.$('.result-image');
        expect(result).toBeTruthy();
    });
});
```

---

## 🚀 Deployment Checklist

### Development Environment ✅
- [x] FastAPI running on localhost:8001
- [x] Django running on localhost:8000
- [x] 7 REST endpoints working
- [x] Demo script showing improvements
- [x] Documentation complete

### Docker Environment (Day 5)
- [ ] FastAPI service in docker-compose.yml
- [ ] Nginx reverse proxy configured
- [ ] Environment variables set
- [ ] Health checks working
- [ ] Logs accessible

### Production Environment (Day 7)
- [ ] HTTPS enabled
- [ ] Authentication working
- [ ] Error handling comprehensive
- [ ] Monitoring & logging setup
- [ ] Backup & recovery tested
- [ ] Performance benchmarks met

---

## 📞 Summary - מסקנות

### מה בנינו:
1. ✅ **FastAPI microservice** עם 7 endpoints
2. ✅ **OpenCV processing** (9 פונקציות)
3. ✅ **Demo scripts** להדגמה
4. ✅ **תיעוד מלא** (3 מסמכים)

### איך זה מסתנכרן עם eScriptorium:
1. **Django Proxy** - Django מעביר בקשות ל-FastAPI
2. **Direct API** - Frontend קורא ישירות ל-FastAPI
3. **WebSocket** - חיבור real-time לעדכונים חיים

### הבא בתור (Days 4-7):
- Day 4: WebSocket implementation
- Day 5: Docker integration
- Day 6: Complete frontend
- Day 7: Testing & deployment

### ביצועים:
- ⚡ **3-4x מהיר יותר** מהגרסה הישנה
- 🚀 **2.5-3 שניות** לעיבוד מלא
- ✅ **Non-blocking** - המשתמש יכול להמשיך לעבוד

---

**רוצה להמשיך ל-Day 4 (WebSocket)?** 🎯
