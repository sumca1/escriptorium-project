# 📊 Training Status API Documentation

## סקירה כללית

API מורחב למעקב בזמן אמת אחר אימון מודלים, ניתוח איכות דאטה, וסטטיסטיקות מפורטות.

**Base URL:** `http://localhost:8082/api/`

---

## 🔐 Authentication

כל ה-endpoints דורשים authentication. השתמש ב-token או session authentication.

**Token Authentication:**
```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
     http://localhost:8082/api/training/active/
```

---

## 📡 Endpoints

### 1. Training Status - סטטוס אימון מפורט

**GET** `/api/models/{id}/training-status/`

מחזיר מידע מפורט על אימון מודל ספציפי.

**דוגמה:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8082/api/models/7/training-status/
```

**Response:**
```json
{
    "model_id": 7,
    "model_name": "Hebrew_Ashkenazy_Test_v5",
    "model_type": "Segmentation",
    "training": true,
    "training_started_at": "2025-10-20T22:51:35Z",
    "training_duration_seconds": 21845,
    "training_duration_human": "6h 4m 5s",
    "current_epoch": 5,
    "current_accuracy": 0.156,
    "accuracy_percent": 15.6,
    "data_stats": {
        "training_lines": 3582,
        "validation_lines": 397,
        "total_lines": 3979,
        "documents_count": 1,
        "parts_count": 56,
        "avg_lines_per_part": 71.1
    },
    "file_size_mb": 15.28,
    "recent_tasks": [
        {
            "id": 345,
            "label": "Segmentation training: Model 7",
            "method": "core.tasks.segtrain",
            "state": "Running",
            "created_at": "2025-10-20T22:38:29Z",
            "start": "2025-10-20T22:38:30Z",
            "end": null,
            "messages": "Training set 3582 lines, validation set 397..."
        }
    ]
}
```

---

### 2. Active Trainings - אימונים פעילים

**GET** `/api/training/active/`

מחזיר רשימת כל האימונים הפעילים כרגע במערכת.

**דוגמה:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8082/api/training/active/
```

**Response:**
```json
{
    "active_trainings": [
        {
            "model_id": 7,
            "model_name": "Hebrew_Ashkenazy_Test_v5",
            "model_type": "Segmentation",
            "started_at": "2025-10-20T22:51:35Z",
            "duration_seconds": 21845,
            "duration_human": "6h 4m 5s",
            "current_accuracy": 0.156,
            "current_epoch": 5
        }
    ],
    "total_active": 1,
    "timestamp": "2025-10-21T04:55:40Z"
}
```

---

### 3. Data Quality Analysis - ניתוח איכות דאטה

**GET** `/api/documents/{id}/data-quality/`

מנתח את איכות הדאטה של מסמך ומחזיר המלצות לפני אימון.

**דוגמה:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8082/api/documents/4/data-quality/
```

**Response:**
```json
{
    "document_id": 4,
    "document_name": "Hebrew_Ashkenazy_Test_v1",
    "parts_count": 56,
    "lines_count": 3979,
    "quality_checks": {
        "transcriptions": {
            "total": 3979,
            "with_transcription": 3979,
            "coverage_percent": 100.0,
            "status": "excellent"
        },
        "baselines": {
            "total": 3979,
            "with_baseline": 3979,
            "coverage_percent": 100.0,
            "status": "excellent"
        },
        "images": {
            "total": 56,
            "available": 56,
            "missing": 0,
            "status": "excellent"
        }
    },
    "readiness": {
        "ready_for_segmentation": true,
        "ready_for_recognition": true,
        "warnings": [],
        "recommendations": []
    },
    "estimated_training_time": {
        "estimated_seconds": 8950,
        "estimated_human": "~2h 29m",
        "note": "Rough estimate, actual time may vary significantly"
    }
}
```

---

## 🔧 Python Usage Examples

### דוגמה 1: בדיקת סטטוס אימון

```python
import requests

API_URL = "http://localhost:8082/api"
TOKEN = "your_token_here"

headers = {"Authorization": f"Token {TOKEN}"}

# בדיקת סטטוס מודל 7
response = requests.get(
    f"{API_URL}/models/7/training-status/",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"Model: {data['model_name']}")
    print(f"Training: {data['training']}")
    print(f"Duration: {data['training_duration_human']}")
    print(f"Accuracy: {data['accuracy_percent']}%")
    print(f"Data: {data['data_stats']['total_lines']} lines")
else:
    print(f"Error: {response.status_code}")
```

### דוגמה 2: מעקב אחר כל האימונים

```python
def monitor_trainings():
    """מעקב בזמן אמת אחר אימונים פעילים"""
    import time
    
    while True:
        response = requests.get(
            f"{API_URL}/training/active/",
            headers=headers
        )
        
        data = response.json()
        
        print(f"\n=== {data['total_active']} Active Trainings ===")
        for training in data['active_trainings']:
            print(f"  {training['model_name']}:")
            print(f"    Duration: {training['duration_human']}")
            print(f"    Accuracy: {training['current_accuracy']:.1%}")
            print(f"    Epoch: {training['current_epoch']}")
        
        time.sleep(60)  # בדיקה כל דקה

# הפעלה
monitor_trainings()
```

### דוגמה 3: בדיקת איכות לפני אימון

```python
def check_document_quality(document_id):
    """בדיקת מוכנות מסמך לאימון"""
    response = requests.get(
        f"{API_URL}/documents/{document_id}/data-quality/",
        headers=headers
    )
    
    data = response.json()
    
    print(f"\n=== Quality Report: {data['document_name']} ===")
    print(f"Lines: {data['lines_count']}")
    print(f"Parts: {data['parts_count']}")
    
    checks = data['quality_checks']
    print(f"\nTranscriptions: {checks['transcriptions']['coverage_percent']:.1f}% - {checks['transcriptions']['status']}")
    print(f"Baselines: {checks['baselines']['coverage_percent']:.1f}% - {checks['baselines']['status']}")
    print(f"Images: {checks['images']['available']}/{checks['images']['total']} - {checks['images']['status']}")
    
    readiness = data['readiness']
    print(f"\nReady for Segmentation: {readiness['ready_for_segmentation']}")
    print(f"Ready for Recognition: {readiness['ready_for_recognition']}")
    
    if readiness['warnings']:
        print("\n⚠️  Warnings:")
        for warning in readiness['warnings']:
            print(f"  - {warning}")
    
    if readiness['recommendations']:
        print("\n💡 Recommendations:")
        for rec in readiness['recommendations']:
            print(f"  - {rec}")
    
    est = data['estimated_training_time']
    print(f"\n⏱️  Estimated training time: {est['estimated_human']}")

# בדיקת Document 4
check_document_quality(4)
```

---

## 📱 JavaScript/Vue Usage

### דוגמה: Dashboard Component

```vue
<template>
  <div class="training-dashboard">
    <h2>Active Trainings ({{ activeTrainings.length }})</h2>
    
    <div v-for="training in activeTrainings" :key="training.model_id" class="training-card">
      <h3>{{ training.model_name }}</h3>
      <p><strong>Type:</strong> {{ training.model_type }}</p>
      <p><strong>Duration:</strong> {{ training.duration_human }}</p>
      <p><strong>Accuracy:</strong> {{ (training.current_accuracy * 100).toFixed(1) }}%</p>
      <p><strong>Epoch:</strong> {{ training.current_epoch }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeTrainings: [],
      refreshInterval: null
    }
  },
  
  mounted() {
    this.fetchActiveTrainings();
    // רענון כל 30 שניות
    this.refreshInterval = setInterval(this.fetchActiveTrainings, 30000);
  },
  
  beforeDestroy() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  
  methods: {
    async fetchActiveTrainings() {
      try {
        const response = await fetch('/api/training/active/', {
          headers: {
            'Authorization': `Token ${this.userToken}`
          }
        });
        const data = await response.json();
        this.activeTrainings = data.active_trainings;
      } catch (error) {
        console.error('Failed to fetch trainings:', error);
      }
    }
  }
}
</script>
```

---

## 🎯 Status Codes

- **200 OK** - Request successful
- **404 Not Found** - Model/Document not found
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - No permission to access resource
- **500 Internal Server Error** - Server error

---

## 📊 Data Status Values

### Quality Status
- `excellent` - 95-100% coverage
- `good` - 80-94% coverage
- `fair` - 50-79% coverage
- `poor` - < 50% coverage

### Model Types
- `Segmentation` - Layout/Line detection (job=2)
- `Recognition` - Text recognition/OCR (job=1)

---

## 🔄 Rate Limiting

אין הגבלת rate כרגע. מומלץ polling לא יותר מפעם ב-30 שניות.

---

## 📝 Notes

1. **Timestamps** - כל התאריכים ב-ISO 8601 format (UTC)
2. **Accuracy** - ערכים בין 0-1 (להמרה לאחוזים: × 100)
3. **Duration** - בשניות, עם פורמט human-readable נוסף
4. **Estimated Times** - אומדנים גסים, הזמן האמיתי עשוי להשתנות

---

## 🐛 Troubleshooting

### שגיאה: "Model not found"
- ודא שה-model_id קיים
- בדוק הרשאות גישה

### שגיאה: "Authentication required"
- הוסף header: `Authorization: Token YOUR_TOKEN`
- קבל token מ-`/api/token-auth/`

### נתונים לא מתעדכנים
- הזמן לאחרונה: תוצאות cached עד 30 שניות
- בדוק שה-WebSocket מחובר לעדכונים real-time

---

## 📚 Additional Resources

- **API Browser:** http://localhost:8082/api/
- **Flower (Celery):** http://localhost:5555
- **Models Page:** http://localhost:8082/models/
- **Admin Panel:** http://localhost:8082/admin/

---

**נוצר:** 21 אוקטובר 2025  
**גרסה:** 1.0.0
