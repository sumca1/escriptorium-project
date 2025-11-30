# TABA Pipeline Integration for BiblIA

## 📖 Overview

**TABA (Text Alignment for Building Annotations)** is an external pipeline integrated into BiblIA that automatically generates Ground Truth for training OCR models by aligning known digital texts with OCR results using Passim.

**Original Project:** https://github.com/Freymat/from_eScriptorium_to_Passim_and_back

## 🏗�? Architecture

TABA runs as an **external standalone pipeline**, not embedded inside BiblIA/eScriptorium. BiblIA provides a **management interface** to:
- Manage Ground Truth corpora
- Create and monitor alignment jobs
- Export XML to TABA
- Import aligned results back

```
┌──────────────────────────────────────┐
�?         BiblIA (Django App)          │
�?  ┌────────────────────────────────�?  �?
�?  �?  TABA Management Interface     �?  │
�?  �?  - Corpus management           �?  │
�?  �?  - Job creation/monitoring     �?  │
�?  �?  - XML export/import           �?  �?
�?  └────────────────────────────────�?  │
└──────────────�?───────────────────────┘
               │
               �? Export XML (API)
               ↓
�?──────────────────────────────────────┐
�?  TABA External Pipeline              │
�?  (Conda environment: Python 3.11)    │
�?  ┌────────────────────────────────�?  │
�?  �? 1. Prepare OCR data            �?  │
�?  �? 2. Run Passim alignment        �?  │
�?  �? 3. Process results             �?  │
�?  �? 4. Generate aligned XMLs       �?  │
�?  └────────────────────────────────�?  │
�?──────────────�?───────────────────────┘
               │
               �? Import XML (API)
               ↓
┌──────────────────────────────────────┐
�?  BiblIA: New GT Transcription Layers │
└──────────────────────────────────────┘
```

## 📋 Installation (Follow Official TABA Documentation)

### Step 1: Create TABA Conda Environment

```bash
# Navigate to project root
cd /path/to/BiblIA_dataset/eScriptorium_CLEAN

# Create dedicated TABA directory (parallel to app/)
mkdir -p taba_external
cd taba_external

# Create conda environment
conda create -n alignment_pipeline python=3.11
conda activate alignment_pipeline

# Install Passim
pip install git+https://github.com/dasmiq/passim.git

# Clone TABA repository
git clone https://github.com/Freymat/from_eScriptorium_to_Passim_and_back.git .

# Install requirements
pip install -r requirements.txt
```

### Step 2: Configure TABA

Create `credentials.py`:
```python
# eScriptorium API credentials
root_url = "http://localhost:8082"  # BiblIA URL
headers = {
    "Authorization": "Token YOUR_API_TOKEN_HERE"
}
headersbrief = headers
```

Create/Edit `config.py`:
```python
# Connection to eScriptorium
eSc_connexion = True

# Document to process (will be set by BiblIA jobs)
doc_pk = None  # Set dynamically by BiblIA
region_type_pk_list = []
transcription_level_pk = None

# Passim parameters
n = 7  # Character n-gram order
n_cores = 6  # Number of CPU cores
mem = 8  # Memory in GB
driver_mem = 4  # Driver memory in GB

# Filtering
levenshtein_threshold = 0.8  # Minimum similarity ratio

# Results
n_best_gt = 5  # Top GT texts to display
```

### Step 3: Prepare Ground Truth Texts

```bash
# Create directory for your GT corpus
mkdir -p data/raw/digital_editions

# Add your Hebrew texts (TXT files)
# Example structure:
# data/raw/digital_editions/
#   ├── tanakh_genesis.txt
#   �?── tanakh_exodus.txt
#   ├── talmud_berachot.txt
#   �?── ...
```

### Step 4: Set Environment Variable

Add to your `.env` or `docker-compose.yml`:

```bash
# Path to TABA external pipeline
TABA_PIPELINE_PATH=/path/to/BiblIA/taba_external

# Conda environment name
TABA_CONDA_ENV=alignment_pipeline
```

### Step 5: Run Django Migrations

```bash
# From BiblIA app directory
python manage.py makemigrations taba_pipeline
python manage.py migrate taba_pipeline
```

## 🚀 Usage

### 1. Access TABA Dashboard

Navigate to: `http://localhost:8082/taba/`

### 2. Create Ground Truth Corpus

1. Go to **Corpus Management**
2. Click **Add Corpus**
3. Fill in:
   - Name: e.g., "Sefaria Hebrew Bible"
   - Source Type: TXT, PDF, or Sefaria API
   - Source Path: `/path/to/taba_external/data/raw/digital_editions/`

### 3. Create Alignment Job

1. Go to **Jobs** �? **Create New Job**
2. Select:
   - **Document**: Your eScriptorium document
   - **OCR Transcription**: The Kraken OCR layer
   - **GT Corpus**: Your ground truth corpus
   - **Parameters**:
     - Passim n-grams: 7 (default)
     - Cores: 6
     - Memory: 8 GB
     - Levenshtein threshold: 0.8

### 4. Run the Pipeline

Click **Start Job** �? TABA will:
1. Export XML from eScriptorium
2. Prepare data for Passim
3. Run Passim alignment
4. Process results
5. Import aligned XMLs back to eScriptorium

### 5. View Results

- **Job Details**: See alignment statistics
- **eScriptorium Document**: New transcription layers created (one per GT text)
- **Reports**: TSV files with detailed metrics

## 📊 How It Works

### Pipeline Steps (from TABA documentation)

1. **XML Export**: BiblIA exports ALTO XMLs with OCR results
2. **Data Preparation**: 
   - Extract OCR lines from XMLs
   - Load GT texts from corpus
   - Create JSON input for Passim
3. **Passim Alignment**:
   - Find text reuse between OCR and GT
   - Use n-gram matching
4. **Results Processing**:
   - Filter alignments by Levenshtein distance
   - Replace OCR lines with aligned GT (if valid)
   - Empty lines without alignment
5. **XML Import**: Import modified XMLs back to eScriptorium
6. **Transcription Layers**: New layer created for each GT source

### Example Alignment

**Original OCR:**
```
הגדול הגבור ודנורא אל עליון קונה ברחמיו
```

**Aligned GT (Levenshtein ratio: 0.861):**
```
הגדול הגבור והנורא. אל עליון קונה
```

�? GT replaces OCR in new transcription layer!

## 🔧 Manual TABA Execution (Advanced)

If needed, you can run TABA directly:

```bash
# Activate TABA environment
conda activate alignment_pipeline
cd /path/to/taba_external

# Run full pipeline
python main.py --run_all --no_import

# Or run steps separately:
python main.py --prepare_data_for_passim
python main.py --compute_alignments_with_passim
python main.py --create_xmls_from_passim_results
python main.py --export_xmls_to_eSc
```

## 📁 Directory Structure

```
BiblIA_dataset/eScriptorium_CLEAN/
�?── app/
�?   ├── apps/
�?   �?   └── taba_pipeline/          # Django management app
�?   �?       ├── models.py            # DB: Corpus, Jobs, Results
�?   �?       �?── views.py             # UI for TABA management
�?   �?       ├── admin.py             # Django admin integration
�?   �?       └── templates/           # Dashboard templates
�?   �?── escriptorium/
�?       └── settings.py              # TABA_PIPELINE_PATH config
│
└── taba_external/                   # External TABA pipeline
    ├── main.py                      # Main execution script
    ├── config.py                    # Configuration
    �?── credentials.py               # API tokens
    ├── requirements.txt             # Python dependencies
    ├── src/                         # Pipeline modules
    �?   �?── fetch_xmls_from_eSc.py
    �?   ├── prepare_data_for_passim.py
    �?   ├── comxxxxxalignments_with_passim.py
    �?   �?── process_alignment_results.py
    �?   └── export_results_to_eSc.py
    └── data/
        ├── raw/
        �?   ├── xmls_from_eSc/       # Exported from BiblIA
        �?   └── digital_editions/    # Your GT texts (TXT)
        ├── processed/
        └── output/
            └── xmls_for_eSc/        # Aligned XMLs to import
```

## ⚙️ Configuration Options

### Passim Parameters

- `n`: N-gram size (default: 7 for Hebrew)
- `n_cores`: CPU cores for Spark
- `mem`: Memory per node (GB)
- `driver_mem`: Driver memory (GB)

### Quality Filtering

- `levenshtein_threshold`: 0.0-1.0 (default: 0.8)
  - Higher = stricter matching
  - Lower = more alignments but less accurate

### Results Display

- `n_best_gt`: Number of top GT texts in summary

## 🐛 Troubleshooting

### Passim Not Installed
```bash
conda activate alignment_pipeline
pip install git+https://github.com/dasmiq/passim.git
```

### Memory Issues
Reduce in `config.py`:
```python
mem = 4  # Instead of 8
n_cores = 4  # Instead of 6
```

### No Alignments Found
- Check Levenshtein threshold (try lowering to 0.7)
- Verify GT texts are in correct language
- Ensure OCR quality is reasonable

## 📚 References

- **TABA GitHub**: https://github.com/Freymat/from_eScriptorium_to_Passim_and_back
- **Passim**: https://github.com/dasmiq/passim
- **Sefaria API**: https://www.sefaria.org/texts (for Hebrew texts)

## 🎯 Key Benefits

�? **Automated GT Generation**: No manual transcription needed
�? **Large Scale**: Process thousands of pages automatically
�? **Quality Controlled**: Levenshtein filtering ensures accuracy
�? **BiblIA Integrated**: Seamless workflow with eScriptorium
�? **External Pipeline**: Doesn't modify BiblIA core code

---

**Integrated:** 26 October 2025
**Original Author:** Freymat (MiDRASH Project - EPHE)
**BiblIA Integration:** BiblIA Development Team
