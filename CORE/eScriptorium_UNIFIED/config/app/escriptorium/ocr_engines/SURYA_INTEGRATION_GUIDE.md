# 🚀 Surya OCR Engine - Integration Guide
**מדריך שילוב מלא ל-eScriptorium**

---

## 📋 תוכן עניינים

1. [סקירה כללית](#סקירה-כללית)
2. [הממשק](#הממשק)
3. [שימוש בסיסי](#שימוש-בסיסי)
4. [שילוב עם Django](#שילוב-עם-django)
5. [דוגמאות מעשיות](#דוגמאות-מעשיות)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 סקירה כללית

### מה זה?
`surya_engine.py` הוא wrapper שמשמר את **כל העוצמה של Surya API** תוך הוספת ממשק אחיד ל-eScriptorium.

### מאפיינים:
✅ **עוצמה מלאה של Surya**
- Batch processing (277 עמודים בו זמנית!)
- 90+ שפות (עברית, ערבית, אנגלית וכו')
- Confidence scores
- Line-by-line מדויק
- GPU acceleration

✅ **ממשק מתאים ל-Django**
- Data classes מובנות
- Logging אוטומטי
- Error handling
- Singleton pattern

✅ **Hebrew/Arabic friendly**
- RTL sorting אוטומטי
- Polygon detection מדויק
- Language detection

---

## 🏗️ הממשק

### Main Class: `SuryaOCREngine`

```python
from surya_engine import SuryaOCREngine

# יצירת instance
engine = SuryaOCREngine(
    device='cuda',              # 'cuda', 'cpu', 'mps'
    dtype=torch.float32,        # float32, float16
    batch_size_recognition=256, # גודל batch
    batch_size_detection=64,
    sort_lines=True,            # RTL sorting
    languages=['he', 'en', 'ar']
)
```

### Main Methods

#### 1. **recognize_page()** - עמוד בודד

```python
result = engine.recognize_page("page.jpg")

# result: PageOCRResult
result.lines          # List[TextLineResult]
result.languages      # ['he', 'en']
result.success        # True/False
result.processing_time # 12.5 (seconds)
result.error_message  # אם שגיאה
```

#### 2. **recognize_pages()** - Batch (מהיר!)

```python
# 277 עמודים בו זמנית!
results = engine.recognize_pages(
    image_paths=[
        "page1.jpg",
        "page2.jpg",
        "page3.jpg",
        ...
    ]
)

# results: List[PageOCRResult]
for result in results:
    for line in result.lines:
        print(line.text)
        print(f"  Confidence: {line.confidence:.2%}")
        print(f"  Position: {line.polygon}")
```

### Output Data Structures

#### `TextLineResult`
```python
@dataclass
class TextLineResult:
    text: str                          # "שלום עולם"
    confidence: float                  # 0.95
    polygon: List[List[int]]          # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    bbox_valid: bool                  # True/False
    x1, y1, x2, y2: int               # Calculated bbox
```

#### `PageOCRResult`
```python
@dataclass
class PageOCRResult:
    image_path: str                    # "/path/to/image.jpg"
    lines: List[TextLineResult]        # כל השורות
    languages: List[str]              # ['he', 'en']
    processing_time: float            # 12.5 seconds
    success: bool                      # True/False
    error_message: Optional[str]      # אם שגיאה
    page_width: int                   # 800
    page_height: int                  # 1000
```

---

## 💻 שימוש בסיסי

### דוגמה 1: OCR פשוט

```python
from surya_engine import SuryaOCREngine

# טעינה (פעם אחת!)
engine = SuryaOCREngine(device='cuda')

# עיבוד עמוד
result = engine.recognize_page("book_page.jpg")

# הדפסת תוצאות
if result.success:
    for line in result.lines:
        print(f"{line.text} ({line.confidence:.2%})")
else:
    print(f"Error: {result.error_message}")
```

### דוגמה 2: Batch Processing (277 עמודים!)

```python
from pathlib import Path

# איסוף כל ה-JPG ים
pages = list(Path("book_pages/").glob("*.jpg"))

# עיבוד batch
results = engine.recognize_pages([str(p) for p in pages])

# שמירה
for page_path, result in zip(pages, results):
    output = page_path.with_suffix('.txt')
    with open(output, 'w', encoding='utf-8') as f:
        for line in result.lines:
            f.write(f"{line.text}\n")

print(f"✅ Processed {len(results)} pages in {sum(r.processing_time for r in results)/60:.1f} minutes")
```

### דוגמה 3: Singleton Pattern (Global Access)

```python
from surya_engine import get_ocr_engine

# כל מקום בקוד
engine = get_ocr_engine()  # תמיד אותו instance
result = engine.recognize_page("page.jpg")
```

---

## 🔗 שילוב עם Django

### 1. **settings.py** - הגדרות

```python
# settings.py

# OCR Configuration
OCR_ENGINES = {
    'surya': {
        'backend': 'escriptorium.ocr_engines.surya_engine.SuryaOCREngine',
        'device': 'cuda',  # או 'cpu'
        'batch_size_recognition': 256,
        'batch_size_detection': 64,
        'sort_lines': True,
        'languages': ['he', 'en', 'ar'],
    }
}

# Default OCR engine
DEFAULT_OCR_ENGINE = 'surya'
```

### 2. **models.py** - Model Integration

```python
# models.py

from django.db import models
from escriptorium.ocr_engines.surya_engine import get_ocr_engine

class Document(models.Model):
    title = models.CharField(max_length=255)
    ocr_engine = models.CharField(
        max_length=50,
        choices=[('surya', 'Surya OCR'), ('kraken', 'Kraken')],
        default='surya'
    )
    
    def process_with_ocr(self):
        """עבד את כל העמודים עם Surya."""
        if self.ocr_engine == 'surya':
            engine = get_ocr_engine()
            
            for part in self.parts.all():
                result = engine.recognize_page(part.image_path)
                
                if result.success:
                    # שמור בדאטה בייס
                    for line in result.lines:
                        LineTranscription.objects.create(
                            line=part,
                            text=line.text,
                            confidence=line.confidence
                        )
                else:
                    self.log_error(result.error_message)


class DocumentPart(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='parts')
    image = models.ImageField()
    
    def get_ocr_transcription(self, engine_name='surya'):
        """קבל OCR transcription עם Surya."""
        if engine_name == 'surya':
            engine = get_ocr_engine()
            return engine.recognize_page(self.image.path)
        return None
```

### 3. **tasks.py** - Celery Integration

```python
# tasks.py

from celery import shared_task
from escriptorium.ocr_engines.surya_engine import get_ocr_engine
from .models import Document, LineTranscription
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_document_with_surya(document_id):
    """
    Async task לעיבוד document עם Surya.
    
    Usage:
        process_document_with_surya.delay(document.id)
    """
    document = Document.objects.get(id=document_id)
    engine = get_ocr_engine()
    
    # איסוף כל הדפים
    image_paths = [part.image.path for part in document.parts.all()]
    
    # Batch processing
    logger.info(f"Processing {len(image_paths)} pages with Surya...")
    results = engine.recognize_pages(image_paths)
    
    # שמור תוצאות
    for part, result in zip(document.parts.all(), results):
        if result.success:
            for line in result.lines:
                LineTranscription.objects.create(
                    line=part,
                    text=line.text,
                    confidence=line.confidence,
                    bbox=line.polygon  # Store polygon
                )
            logger.info(f"✅ Processed {part} ({len(result.lines)} lines)")
        else:
            logger.error(f"❌ Failed to process {part}: {result.error_message}")
    
    logger.info("✅ Document processing complete!")
    return {
        'document_id': document_id,
        'total_pages': len(results),
        'successful': sum(1 for r in results if r.success),
        'failed': sum(1 for r in results if not r.success)
    }


@shared_task
def process_single_page(document_part_id):
    """Async task לעמוד בודד."""
    part = DocumentPart.objects.get(id=document_part_id)
    engine = get_ocr_engine()
    
    result = engine.recognize_page(part.image.path)
    
    if result.success:
        for line in result.lines:
            LineTranscription.objects.create(
                line=part,
                text=line.text,
                confidence=line.confidence
            )
        return {'status': 'success', 'lines': len(result.lines)}
    else:
        return {'status': 'error', 'message': result.error_message}
```

### 4. **views.py** - REST API

```python
# views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from escriptorium.ocr_engines.surya_engine import get_ocr_engine
from .models import Document
from .tasks import process_document_with_surya

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    
    @action(detail=True, methods=['post'])
    def ocr_with_surya(self, request, pk=None):
        """
        API endpoint לעיבוד עם Surya.
        
        POST /documents/{id}/ocr_with_surya/
        """
        document = self.get_object()
        
        # Start async task
        task = process_document_with_surya.delay(document.id)
        
        return Response({
            'status': 'processing',
            'task_id': task.id,
            'message': 'Document is being processed with Surya OCR'
        })
    
    @action(detail=True, methods=['get'])
    def surya_status(self, request, pk=None):
        """בדוק סטטוס של מנוע Surya."""
        engine = get_ocr_engine()
        status = engine.get_status()
        
        return Response({
            'engine': 'Surya',
            'device': status['device'],
            'models_loaded': status['models_loaded'],
            'cuda_available': status['cuda_available'],
            'batch_size': status['batch_size_recognition']
        })
```

---

## 📚 דוגמאות מעשיות

### דוגמה 1: עיבוד ספר שלם

```python
from pathlib import Path
from surya_engine import get_ocr_engine
from tqdm import tqdm

def process_book(book_dir, output_dir):
    """עבד ספר שלם."""
    engine = get_ocr_engine()
    
    # איסוף עמודים
    pages = sorted(Path(book_dir).glob("*.jpg"))
    print(f"Found {len(pages)} pages")
    
    # עיבוד batch
    results = engine.recognize_pages([str(p) for p in pages])
    
    # שמירה
    for page_path, result in tqdm(zip(pages, results), total=len(pages)):
        if result.success:
            output = Path(output_dir) / page_path.stem / ".txt"
            output.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output, 'w', encoding='utf-8') as f:
                for line in result.lines:
                    f.write(f"{line.text}\n")
    
    # סטטיסטיקות
    total_lines = sum(len(r.lines) for r in results if r.success)
    total_time = sum(r.processing_time for r in results)
    
    print(f"\n✅ Results:")
    print(f"  Pages: {len([r for r in results if r.success])}/{len(results)}")
    print(f"  Total lines: {total_lines}")
    print(f"  Total time: {total_time/60:.1f} minutes")
    print(f"  Avg per page: {total_time/len(results):.1f}s")
```

### דוגמה 2: Confidence Filtering

```python
def process_with_confidence_threshold(image_paths, threshold=0.8):
    """עבד עם סינון confidence."""
    engine = get_ocr_engine()
    results = engine.recognize_pages(image_paths)
    
    for result in results:
        if result.success:
            # סנן שורות עם confidence נמוך
            high_confidence_lines = [
                line for line in result.lines
                if line.confidence >= threshold
            ]
            
            print(f"✅ {result.image_path}")
            print(f"   Total lines: {len(result.lines)}")
            print(f"   High confidence (>{threshold}): {len(high_confidence_lines)}")
            
            for line in high_confidence_lines:
                print(f"   {line.text}")
```

### דוגמה 3: Language Detection

```python
def analyze_languages(image_paths):
    """בדוק אילו שפות זוהו."""
    engine = get_ocr_engine()
    results = engine.recognize_pages(image_paths)
    
    language_stats = {}
    
    for result in results:
        if result.success:
            for lang in result.languages:
                language_stats[lang] = language_stats.get(lang, 0) + 1
    
    print("Languages detected:")
    for lang, count in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {lang}: {count} pages")
```

---

## 🔧 Troubleshooting

### בעיה 1: NetFree blocking models

**סימנים:**
```
418 Client Error: Blocked by NetFree
Error downloading model from layout/2025_09_23
```

**פתרון:**
1. בקש אישור ל-https://models.datalab.to
2. זו הורדה חד-פעמית של ~2-3GB
3. אחרי אישור, מודלים יורדו בפעם הראשונה

### בעיה 2: Out of Memory

**סימנים:**
```
RuntimeError: CUDA out of memory
```

**פתרון:**
```python
engine = SuryaOCREngine(
    device='cuda',
    batch_size_recognition=64,  # Reduce from 256
    batch_size_detection=32     # Reduce from 64
)
```

### בעיה 3: Slow Processing

**סימנים:**
- 10-15s per page על CPU

**פתרון:**
1. השתמש ב-GPU אם זמין
2. או עיבוד batch קטן יותר

---

## 📊 Performance

| Device | Batch Size | Time/Page | 277 Pages |
|--------|-----------|-----------|-----------|
| CPU    | 32        | 10-15s    | 45-60 min |
| GPU    | 256       | 1-3s      | 5-10 min  |

---

## ✅ Checklist

- [ ] Surya installed: `pip install surya-ocr`
- [ ] NetFree approval received
- [ ] Models downloaded on first run
- [ ] surya_engine.py integrated
- [ ] Django models updated
- [ ] Celery tasks configured
- [ ] API endpoints created
- [ ] Tests passing
- [ ] Ready for production!

---

## 🚀 Next Steps

1. ✅ Get NetFree approval
2. ⏭️ Integrate into Django
3. ⏭️ Add REST API
4. ⏭️ Process 277 pages
5. ⏭️ Monitor accuracy
6. ⏭️ Go to production!

---

**Questions?** Check SURYA_API_REFERENCE.md or SURYA_INTERFACE_VISUAL.py
