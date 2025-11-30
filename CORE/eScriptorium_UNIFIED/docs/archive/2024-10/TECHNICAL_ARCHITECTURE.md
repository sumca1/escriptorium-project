# 🔧 Technical Architecture Deep Dive

## 🎯 Flow: ממשקים → Implementation

### **Flow 1: Batch OCR Pipeline**

```
User Input (Web/CLI)
    ↓
┌─────────────────────────────────────────┐
│  1. ValidationLayer                    │
│   • Validate input directory exists     │
│   • Check output permissions            │
│   • Parse language codes                │
│   • Verify engine availability          │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  2. JobManagement                       │
│   • Create ConversionJob record         │
│   • Generate job_id                     │
│   • Set status = 'pending'              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  3. ModelLoading                        │
│   • Check if engine cached locally      │
│   • If not cached: attempt download     │
│   • If download fails: use fallback     │
│   • Load models to GPU/CPU              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  4. ImageDiscovery                      │
│   • Scan input directory                │
│   • Find all image files                │
│   • Sort by name (for consistency)      │
│   • Count total images (277 in example) │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  5. BatchProcessing                     │
│   • Group images into batches           │
│   • For each batch:                     │
│     - Load images to memory             │
│     - Run OCR engine                    │
│     - Collect results                   │
│     - Save intermediate results         │
│     - Update progress %                 │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  6. ResultConversion                    │
│   • Convert to requested formats        │
│   • Save as PAGE-XML                    │
│   • Save as JSON                        │
│   • Save as TXT                         │
│   • Generate confidence reports         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  7. PostProcessing                      │
│   • Combine individual results          │
│   • Generate metadata                   │
│   • Create summary report               │
│   • Calculate statistics                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  8. Finalization                        │
│   • Update job status = 'completed'     │
│   • Set completion time                 │
│   • Trigger notifications               │
│   • Clean up temp files                 │
└─────────────────────────────────────────┘
    ↓
✅ Return results to user
```

---

### **Flow 2: Model Conversion Pipeline**

```
User Request: "Convert Surya PyTorch → Kraken ONNX"
    ↓
┌─────────────────────────────────────────┐
│  1. ModelValidation                     │
│   • Check source model exists           │
│   • Verify target format supported      │
│   • Check disk space available          │
│   • Estimate conversion time            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  2. ModelPreparation                    │
│   • Load source model                   │
│   • Parse model architecture            │
│   • Verify model weights integrity      │
│   • Check compatibility                 │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  3. ConversionProcess                   │
│   • Initialize converter                │
│   • Transform model architecture        │
│   • Convert weights to target format    │
│   • Apply optimizations                 │
│   • Test converted model                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  4. OptimizationPhase                   │
│   • If quantization requested:          │
│     - Convert to int8 (80% size)        │
│   • If mobile requested:                │
│     - Reduce precision                  │
│     - Optimize ops                      │
│   • Compress model (gzip)               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  5. ValidationPhase                     │
│   • Test on sample image                │
│   • Compare accuracy (should be ~95%)   │
│   • Verify output format                │
│   • Check file integrity                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  6. Caching                             │
│   • Save converted model locally        │
│   • Calculate checksum                  │
│   • Register in model cache             │
│   • Update metadata                     │
└─────────────────────────────────────────┘
    ↓
✅ Return converted model path
```

---

### **Flow 3: Format Conversion (Results)**

```
User: "Convert result.pagexml → result.alto.xml"
    ↓
┌─────────────────────────────────────────┐
│  1. FormatDetection                     │
│   • Read file header                    │
│   • Parse XML namespace                 │
│   • Auto-detect format (PAGE/ALTO/JSON) │
│   • Check version/compatibility         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  2. Parsing                             │
│   • Load source file                    │
│   • Parse XML/JSON structure            │
│   • Extract metadata                    │
│   • Build in-memory representation      │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  3. Mapping                             │
│   • Map source fields to target fields  │
│   • Convert coordinates if needed       │
│   • Transform metadata                  │
│   • Handle missing fields               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  4. Transformation                      │
│   • PAGE-XML → ALTO-XML                 │
│     - Create PageArea elements          │
│     - Convert TextLine blocks           │
│     - Map confidence scores             │
│     - Preserve bounding boxes           │
│                                         │
│   • PAGE-XML → JSON                     │
│     - Create document structure         │
│     - Array of pages, lines, words      │
│     - Flatten if requested              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  5. Filtering & Processing              │
│   • If confidence threshold set:        │
│     - Remove low-confidence items       │
│   • If layout preservation requested:   │
│     - Keep spatial relationships        │
│   • Clean up text (unicode normalize)   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  6. OutputGeneration                    │
│   • Generate target format              │
│   • Write to file                       │
│   • Add metadata (date, version)        │
│   • Create backup if exists             │
└─────────────────────────────────────────┘
    ↓
✅ Return success + file path
```

---

## 🏗️ Component Architecture

### **Model Manager (핵심)**

```python
class ModelManager:
    def __init__(self, cache_dir):
        self.cache = ModelCache(cache_dir)
        self.engines = {}  # Surya, Kraken, etc.
        self.converters = {}  # Format converters
    
    def get_or_download_model(self, engine, model_name):
        """Get cached model or download (with NetFree fallback)."""
        # Check local cache first
        cached = self.cache.get(engine, model_name)
        if cached:
            return cached
        
        # Try to download
        try:
            model = self.download_model(engine, model_name)
            self.cache.save(model)
            return model
        except NetworkError:
            # NetFree blocked - use fallback
            return self.get_fallback_model(engine)
    
    def convert_model(self, source, target):
        """Convert between model formats."""
        source_model = self.get_or_download_model(*source)
        converter = self.get_converter(source.engine, target.engine)
        return converter.convert(source_model, target)
    
    def batch_ocr(self, input_dir, engine, **kwargs):
        """Run batch OCR on directory."""
        engine_instance = self.get_engine(engine)
        images = self.discover_images(input_dir)
        
        results = []
        for batch in self.batch_images(images, batch_size=32):
            batch_results = engine_instance.process_batch(batch)
            results.extend(batch_results)
            self.emit_progress()
        
        return results
```

### **Format Converters (עיבוד תוצאות)**

```python
class FormatConverter:
    @staticmethod
    def pagexml_to_alto(pagexml_path, output_path, options=None):
        """PAGE-XML → ALTO-XML."""
        tree = ET.parse(pagexml_path)
        root = tree.getroot()
        
        # Extract data
        pages = extract_pages_from_pagexml(root)
        
        # Create ALTO structure
        alto_root = create_alto_root()
        for page in pages:
            alto_page = convert_page_to_alto(page)
            alto_root.append(alto_page)
        
        # Write output
        ET.ElementTree(alto_root).write(output_path)
        return True
    
    @staticmethod
    def pagexml_to_json(pagexml_path, output_path, options=None):
        """PAGE-XML → JSON (eScriptorium format)."""
        tree = ET.parse(pagexml_path)
        root = tree.getroot()
        
        # Convert to dict
        document = {
            'pages': [],
            'metadata': extract_metadata(root)
        }
        
        for page in root.findall('.//Page'):
            page_data = {
                'id': page.get('imageFilename'),
                'lines': [],
                'regions': []
            }
            
            for line in page.findall('.//TextLine'):
                line_data = {
                    'text': extract_text(line),
                    'bbox': extract_bbox(line),
                    'confidence': extract_confidence(line)
                }
                page_data['lines'].append(line_data)
            
            document['pages'].append(page_data)
        
        # Write JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        
        return True
```

### **Batch Processor (עיבוד batch)**

```python
class BatchProcessor:
    def __init__(self, engine, batch_size=32):
        self.engine = engine
        self.batch_size = batch_size
        self.job_id = None
    
    def process_directory(self, input_dir, output_dir, **kwargs):
        """Process all images in directory."""
        # Discover images
        images = list(Path(input_dir).glob("*.[jp][pn][g]"))
        total = len(images)
        
        # Create job
        self.job_id = self.create_job(
            type='batch_ocr',
            total_items=total,
            input_dir=input_dir,
            output_dir=output_dir
        )
        
        # Process batches
        all_results = []
        for i in range(0, total, self.batch_size):
            batch = images[i:i+self.batch_size]
            
            try:
                results = self.engine.process_batch(batch)
                all_results.extend(results)
                
                # Update progress
                progress = min(100, (i + len(batch)) / total * 100)
                self.update_job_progress(self.job_id, progress)
                
            except Exception as e:
                self.log_error(self.job_id, str(e))
                # Continue with next batch
        
        # Save results
        self.save_results(self.job_id, all_results, output_dir)
        self.mark_job_complete(self.job_id)
        
        return all_results
    
    def create_job(self, **kwargs):
        """Create job record in database."""
        # Django ORM
        job = ConversionJob.objects.create(**kwargs)
        return job.id
    
    def update_job_progress(self, job_id, progress):
        """Update progress in database."""
        job = ConversionJob.objects.get(id=job_id)
        job.progress = int(progress)
        job.save()
```

---

## 🔌 Integration Points

### **eScriptorium Integration**

```
eScriptorium Views
    ↓
┌─────────────────────────────┐
│ views_surya_ocr.py          │
│                             │
│ • OCREngineViewSet          │
│ • batch_ocr() action        │
│ • convert_model() action    │
│ • model_status() action     │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│ Model Manager               │
│ (external_tools/)           │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│ OCR Engines                 │
│ • Surya                     │
│ • Kraken                    │
│ • PaddleOCR                 │
└─────────────────────────────┘
```

### **Database Schema**

```python
class ConversionJob(models.Model):
    id = AutoField()
    
    # Input/Output
    input_path = TextField()
    output_path = TextField()
    
    # Job Details
    job_type = CharField(choices=[
        ('batch_ocr', 'Batch OCR'),
        ('model_convert', 'Model Conversion'),
        ('result_convert', 'Results Format Conversion')
    ])
    
    # Engine/Format
    source_engine = CharField()
    target_engine = CharField(null=True)
    source_format = CharField()
    target_format = CharField(null=True)
    
    # Status Tracking
    status = CharField(choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ])
    progress = IntegerField(default=0)  # 0-100
    
    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    started_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    
    # Error Handling
    error_message = TextField(blank=True)
    
    # Metadata
    input_size = BigIntegerField(null=True)
    output_size = BigIntegerField(null=True)
    duration_seconds = IntegerField(null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            Index(fields=['status', 'created_at']),
            Index(fields=['job_type', 'status']),
        ]


class ModelCache(models.Model):
    engine = CharField()                    # 'surya', 'kraken'
    model_name = CharField()
    model_path = TextField()
    
    format = CharField(choices=[
        ('torch', 'PyTorch'),
        ('onnx', 'ONNX'),
        ('tflite', 'TensorFlow Lite'),
        ('ort', 'ONNX Runtime')
    ])
    
    file_size = BigIntegerField()
    checksum = CharField(unique=True)
    
    downloaded_at = DateTimeField(auto_now_add=True)
    last_used_at = DateTimeField(auto_now=True)
    usage_count = IntegerField(default=0)
    
    class Meta:
        unique_together = ('engine', 'model_name', 'format')
        ordering = ['-last_used_at']
```

---

## 🛡️ NetFree Solution Implementation

### **Problem Analysis**

```
Surya tries to download from:
  https://models.datalab.to/...
           ↓
NetFree firewall blocks (418 Blocked by NetFree)
           ↓
Download fails
```

### **Solution: Offline Model Strategy**

```python
class OfflineModelManager:
    
    MODELS_CACHE_DIR = Path("external_tools/surya/models_cache")
    
    @staticmethod
    def setup_offline_models():
        """
        Call this ONCE to pre-download models locally.
        After that, Surya will use local cache automatically.
        """
        models_to_download = [
            "detection/2025_09_23",
            "recognition/2025_09_23",
            "ordering/2025_09_23",
            "layout/2025_09_23"
        ]
        
        # This runs without internet issues
        # (Downloads happen once during setup)
        for model in models_to_download:
            download_and_cache_model(model)
    
    @staticmethod
    def load_offline_models():
        """Load models from local cache (no internet needed)."""
        
        # Set environment to use local cache
        os.environ['SURYA_MODELS_DIR'] = str(
            OfflineModelManager.MODELS_CACHE_DIR
        )
        
        # Now Surya won't try to download
        from surya import models
        predictors = models.load_predictors()
        
        return predictors
    
    @staticmethod
    def fallback_to_paddle_ocr():
        """If Surya models unavailable, use PaddleOCR (simpler setup)."""
        from paddleocr import PaddleOCR
        
        ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',  # Support Hebrew through transliteration
            use_gpu=torch.cuda.is_available()
        )
        return ocr
```

---

## 🧪 Testing Strategy

```python
class TestIntegration:
    
    @pytest.fixture
    def setup(self):
        self.manager = ModelManager()
        self.test_image = load_test_image()
        self.test_results = load_test_pagexml()
    
    def test_batch_ocr_277_pages(self):
        """Test with 277 pages (real scenario)."""
        job_id = self.manager.batch_ocr(
            input_dir=TEST_IMAGES_DIR,
            engine='surya',
            languages=['he', 'ar']
        )
        
        job = wait_for_completion(job_id, timeout=600)
        assert job.status == 'completed'
        assert job.progress == 100
        assert len(job.results) == 277
    
    def test_model_conversion(self):
        """Test PyTorch → ONNX conversion."""
        result = self.manager.convert_model(
            source=('surya', 'detection', 'pytorch'),
            target=('kraken', 'detection', 'onnx')
        )
        
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
    
    def test_format_conversion(self):
        """Test PAGE-XML → ALTO-XML."""
        output = FormatConverter.pagexml_to_alto(
            pagexml_path=self.test_results,
            output_path='test_output.alto.xml'
        )
        
        assert output is True
        assert Path('test_output.alto.xml').exists()
    
    def test_offline_mode(self):
        """Test with offline models (NetFree blocked)."""
        # Disable internet
        with mock_no_internet():
            # Should work with cached models
            results = self.manager.batch_ocr(
                input_dir=TEST_IMAGES_DIR,
                engine='surya'
            )
            assert len(results) > 0
```

---

**זה ה-Architecture המלא!** 🏗️
