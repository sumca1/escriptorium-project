# 📚 TABA Pipeline - Complete Documentation

## Overview

The **TABA Pipeline** integration allows eScriptorium to leverage external Ground Truth alignment tools for improving OCR quality through intelligent corpus matching.

### What is TABA?

**TABA** (Text Alignment for Better Accuracy) is a pipeline that:
1. Takes OCR output from eScriptorium
2. Aligns it with high-quality Ground Truth texts using **Passim**
3. Identifies matching segments with configurable similarity thresholds
4. Returns aligned results to improve OCR accuracy

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    eScriptorium                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         TABA Pipeline Django App                 │  │
│  │                                                  │  │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────┐ │  │
│  │  │   Models   │  │    Views    │  │Templates │ │  │
│  │  │            │  │             │  │          │ │  │
│  │  │ • Corpus   │  │ • Dashboard │  │ • UI     │ │  │
│  │  │ • Text     │  │ • Job Mgmt  │  │          │ │  │
│  │  │ • Job      │  │ • API       │  │          │ │  │
│  │  │ • Result   │  │             │  │          │ │  │
│  │  └────────────┘  └─────────────┘  └──────────┘ │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │        TABAPipelineExecutor              │  │  │
│  │  │                                          │  │  │
│  │  │  1. Export OCR to XML                    │  │  │
│  │  │  2. Export GT texts                      │  │  │
│  │  │  3. Build TABA command                   │  │  │
│  │  │  4. Execute pipeline                     │  │  │
│  │  │  5. Import results                       │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│            External TABA Pipeline (Conda)               │
│                                                         │
│  ┌───────────┐      ┌──────────┐     ┌──────────────┐ │
│  │  Passim   │ ───▶ │ Alignment│ ───▶│   Results    │ │
│  │ (Apache   │      │ Algorithm│     │ (JSON files) │ │
│  │  Spark)   │      │          │     │              │ │
│  └───────────┘      └──────────┘     └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                  Back to eScriptorium DB
```

---

## Database Models

### 1. **GroundTruthCorpus**

Represents a collection of high-quality texts for alignment.

**Fields:**
- `name` - Corpus name (e.g., "Hebrew Bible Corpus")
- `description` - Detailed description
- `language` - Language code (he, ar, en, etc.)
- `source_type` - Where texts came from (sefaria, wikisource, custom)
- `owner` - User who owns the corpus
- `created_at` - When corpus was created
- `updated_at` - Last update time

**Computed Properties:**
- `text_count` - Number of texts in corpus
- `total_characters` - Total character count across all texts

### 2. **GroundTruthText**

Individual text within a corpus.

**Fields:**
- `corpus` - ForeignKey to GroundTruthCorpus
- `title` - Text title (e.g., "Genesis 1:1")
- `filename` - Storage filename
- `content` - Full text content (TextField)
- `language` - Language code
- `source_url` - Original source URL
- `character_count` - Number of characters
- `created_at` - Upload time
- `updated_at` - Last modification

### 3. **AlignmentJob**

Represents a TABA pipeline execution job.

**Fields:**
- `name` - Job name
- `document` - eScriptorium Document to align
- `ocr_transcription` - Which transcription to use
- `gt_corpus` - Ground Truth corpus for alignment
- `owner` - User who created job
- `status` - Current job status (pending/preparing/running/completed/failed)
- `progress` - Progress percentage (0-100)
- `passim_n`, `passim_cores`, `passim_memory`, `passim_driver_memory` - Passim parameters
- `levenshtein_threshold` - Similarity threshold (0.0-1.0)
- `total_aligned_lines` - Number of lines successfully aligned
- `aligned_gt_texts` - List of GT text titles used
- `results_path` - Path to result files
- `error_message` - Error details if failed
- `started_at`, `completed_at` - Execution timestamps

**Status Flow:**
```
pending → preparing → running_passim → processing → completed
                                                   → failed
```

### 4. **AlignmentResult**

Stores alignment results for each document part.

**Fields:**
- `job` - ForeignKey to AlignmentJob
- `part_pk` - Document part ID
- `part_title` - Part name
- `gt_text` - Which GT text matched
- `total_aligned_lines` - Lines aligned in this part
- `aligned_clusters` - List of cluster sizes
- `max_cluster_size` - Largest cluster
- `average_levenshtein_ratio` - Average similarity score
- `created_at` - When result was created

---

## Views & URLs

### Dashboard

**URL:** `/taba/`  
**View:** `TABADashboardView`  
**Template:** `taba_pipeline/dashboard.html`

Shows overview:
- System status (Passim installed?)
- Recent jobs
- Corpus statistics
- Quick actions

### Corpus Management

**List:** `/taba/corpus/`  
**Detail:** `/taba/corpus/<id>/`  
**Create:** `/taba/corpus/create/`

Manage Ground Truth corpora and texts.

### Job Management

**List:** `/taba/jobs/`  
**Detail:** `/taba/jobs/<id>/`  
**Create:** `/taba/jobs/create/`  
**Run:** `/taba/jobs/<id>/run/` (POST)  
**Status:** `/taba/jobs/<id>/status/` (AJAX polling)

Create and monitor alignment jobs.

---

## TABAPipelineExecutor

The core execution engine.

### Workflow

```python
executor = TABAPipelineExecutor(job)
success, message = executor.execute()
```

**Steps:**

1. **Validate Setup**
   - Check TABA_PIPELINE_PATH exists
   - Verify main.py is present
   - Validate conda environment

2. **Prepare Workspace**
   ```
   /tmp/taba_work/job_{id}_{timestamp}/
       ├── ocr/           # Exported OCR XML
       ├── ground_truth/  # GT text files
       └── ...
   
   /tmp/taba_output/job_{id}_{timestamp}/
       └── results/       # JSON results
   ```

3. **Export OCR to XML**
   - Extracts OCR transcription from eScriptorium
   - Converts to PAGE XML format
   - Saves to `ocr/document_{id}.xml`

4. **Export Ground Truth**
   - Iterates through corpus texts
   - Writes each to separate `.txt` file
   - Saves to `ground_truth/` directory

5. **Build TABA Command**
   ```bash
   conda run -n taba_alignment python main.py \
       --ocr ocr/document_5.xml \
       --gt-dir ground_truth/ \
       --output results/ \
       --n 5 \
       --cores 4 \
       --memory 4g \
       --driver-memory 2g \
       --threshold 0.8
   ```

6. **Run Pipeline**
   - Execute command via subprocess
   - Stream output for progress tracking
   - Update job.progress in real-time

7. **Import Results**
   - Read JSON files from `results/`
   - Create AlignmentResult records
   - Update job statistics

### Error Handling

```python
try:
    executor.execute()
except Exception as e:
    job.status = 'failed'
    job.error_message = str(e)
    job.save()
```

---

## Configuration

### Required Settings

Add to `settings.py`:

```python
# TABA Pipeline Configuration
TABA_PIPELINE_PATH = '/path/to/TABA-Groundtruth-Alignment-Pipeline'
TABA_WORK_DIR = '/tmp/taba_work'
TABA_OUTPUT_DIR = '/tmp/taba_output'
TABA_CONDA_ENV = 'taba_alignment'

# Defaults
TABA_DEFAULT_PASSIM_N = 5
TABA_DEFAULT_PASSIM_CORES = 4
TABA_DEFAULT_PASSIM_MEMORY = 4
TABA_DEFAULT_PASSIM_DRIVER_MEMORY = 2
TABA_DEFAULT_LEVENSHTEIN_THRESHOLD = 0.8

# Limits
TABA_MAX_EXECUTION_TIME = 3600  # 1 hour
TABA_CLEANUP_AFTER_DAYS = 7
```

### Environment Setup

1. **Install TABA Pipeline:**
   ```bash
   git clone https://github.com/your-org/TABA-Groundtruth-Alignment-Pipeline.git
   cd TABA-Groundtruth-Alignment-Pipeline
   conda env create -f environment.yml
   ```

2. **Configure eScriptorium:**
   ```bash
   # In eScriptorium settings
   export TABA_PIPELINE_PATH=/path/to/TABA-Groundtruth-Alignment-Pipeline
   ```

3. **Test Installation:**
   ```python
   python manage.py shell
   >>> from apps.taba_pipeline.views import _check_passim_installation
   >>> _check_passim_installation()
   True
   ```

---

## Usage Examples

### 1. Create Ground Truth Corpus

```python
from apps.taba_pipeline.models import GroundTruthCorpus, GroundTruthText
from users.models import User

user = User.objects.get(username='admin')

# Create corpus
corpus = GroundTruthCorpus.objects.create(
    name='Hebrew Bible Corpus',
    description='Biblical Hebrew texts from Sefaria',
    language='he',
    source_type='sefaria',
    owner=user
)

# Add texts
GroundTruthText.objects.create(
    corpus=corpus,
    title='Genesis 1:1',
    filename='genesis_1_1.txt',
    content='בראשית ברא אלהים את השמים ואת הארץ',
    language='he',
    character_count=38
)
```

### 2. Create and Run Alignment Job

```python
from apps.taba_pipeline.models import AlignmentJob
from core.models import Document, Transcription

document = Document.objects.get(pk=5)
transcription = document.transcriptions.first()

job = AlignmentJob.objects.create(
    name='Hebrew Bible Alignment',
    document=document,
    ocr_transcription=transcription,
    gt_corpus=corpus,
    owner=user,
    passim_n=5,
    passim_cores=4,
    levenshtein_threshold=0.8
)

# Execute (via view or directly)
from apps.taba_pipeline.executor import TABAPipelineExecutor
executor = TABAPipelineExecutor(job)
success, message = executor.execute()
```

### 3. Monitor Job Progress

Via AJAX polling in frontend:

```javascript
function pollJobStatus(jobId) {
    fetch(`/taba/jobs/${jobId}/status/`)
        .then(response => response.json())
        .then(data => {
            updateProgress(data.progress);
            if (data.status === 'completed') {
                showResults(data);
            } else if (data.status === 'failed') {
                showError(data.error_message);
            } else {
                setTimeout(() => pollJobStatus(jobId), 2000);
            }
        });
}
```

---

## Testing

### Run Tests

```bash
python manage.py test apps.taba_pipeline
```

### Test Coverage

```bash
coverage run --source='apps.taba_pipeline' manage.py test apps.taba_pipeline
coverage report
coverage html
```

### Manual Testing

1. **Test Corpus Creation:**
   - Navigate to `/taba/corpus/create/`
   - Create a test corpus
   - Add sample texts

2. **Test Job Execution:**
   - Create an alignment job via `/taba/jobs/create/`
   - Click "Run Job"
   - Monitor status updates

3. **Test Results:**
   - Check job detail page for results
   - Verify alignment statistics
   - Download result files if available

---

## Troubleshooting

### Common Issues

#### 1. "TABA pipeline not found"

**Solution:**
```bash
# Check TABA_PIPELINE_PATH in settings
echo $TABA_PIPELINE_PATH

# Verify directory exists
ls -la /path/to/TABA-Groundtruth-Alignment-Pipeline

# Check main.py exists
ls /path/to/TABA-Groundtruth-Alignment-Pipeline/main.py
```

#### 2. "Conda environment not found"

**Solution:**
```bash
# List conda environments
conda env list

# Create if missing
cd /path/to/TABA-Groundtruth-Alignment-Pipeline
conda env create -f environment.yml

# Activate and test
conda activate taba_alignment
python -c "import passim; print('OK')"
```

#### 3. "Job stuck in 'running' status"

**Solution:**
```bash
# Check logs
docker-compose logs web | grep -i taba

# Check TABA process
ps aux | grep taba

# Manually reset job
python manage.py shell
>>> from apps.taba_pipeline.models import AlignmentJob
>>> job = AlignmentJob.objects.get(pk=1)
>>> job.status = 'failed'
>>> job.error_message = 'Manually reset'
>>> job.save()
```

#### 4. "Permission denied" errors

**Solution:**
```bash
# Fix work directory permissions
sudo chown -R $(whoami):$(whoami) /tmp/taba_work
sudo chmod -R 755 /tmp/taba_work

# Same for output
sudo chown -R $(whoami):$(whoami) /tmp/taba_output
sudo chmod -R 755 /tmp/taba_output
```

---

## Performance Optimization

### For Large Documents

1. **Increase Passim Memory:**
   ```python
   job.passim_memory = 8  # 8GB
   job.passim_driver_memory = 4  # 4GB
   job.save()
   ```

2. **Use More Cores:**
   ```python
   job.passim_cores = 8
   job.save()
   ```

3. **Adjust Threshold:**
   ```python
   # Lower threshold = more matches but slower
   job.levenshtein_threshold = 0.7
   job.save()
   ```

### Background Processing

For production, use **Celery**:

```python
# tasks.py
from celery import shared_task

@shared_task
def run_taba_pipeline(job_id):
    from apps.taba_pipeline.models import AlignmentJob
    from apps.taba_pipeline.executor import TABAPipelineExecutor
    
    job = AlignmentJob.objects.get(pk=job_id)
    executor = TABAPipelineExecutor(job)
    return executor.execute()

# views.py
def post(self, request, *args, **kwargs):
    # ...
    run_taba_pipeline.delay(job.pk)
    # ...
```

---

## Future Enhancements

### Planned Features

- [ ] Batch job processing
- [ ] Advanced filtering of alignment results
- [ ] Visual diff viewer for OCR vs GT
- [ ] Automatic GT corpus import from Sefaria API
- [ ] ML-based threshold optimization
- [ ] Integration with eScriptorium training pipeline
- [ ] Result export to various formats (CSV, JSON, XML)
- [ ] Visualization dashboard for alignment quality

### API Endpoints (Future)

```
POST /api/taba/corpus/          - Create corpus
GET  /api/taba/corpus/{id}/     - Get corpus details
POST /api/taba/jobs/            - Create job
POST /api/taba/jobs/{id}/run/   - Run job
GET  /api/taba/jobs/{id}/       - Get job status
GET  /api/taba/results/         - List results
```

---

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Write tests for new features

### Pull Request Process

1. Create feature branch
2. Write code + tests
3. Update documentation
4. Submit PR with description

---

## License

Same as eScriptorium (MIT)

---

## Support

- **GitHub Issues:** [eScriptorium Issues](https://github.com/escriptorium/escriptorium/issues)
- **Documentation:** This file
- **Community:** eScriptorium Slack/Discord

---

## Credits

- **TABA Pipeline:** [Original TABA Project]
- **eScriptorium:** [eScriptorium Team]
- **Integration:** BiblIA Project Team

---

**Last Updated:** October 26, 2025  
**Version:** 1.0.0
