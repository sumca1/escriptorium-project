<template>
  <div class="surya-ocr-panel">
    <!-- Header -->
    <div class="panel-header">
      <span class="engine-icon">🔍</span>
      <h3>Surya OCR</h3>
      <span class="badge" :class="engineStatus.status">
        {{ engineStatus.status }}
      </span>
    </div>

    <!-- Engine Status -->
    <div v-if="!isEngineReady" class="status-warning">
      <p>{{ engineStatus.message }}</p>
      <button @click="checkEngineStatus" class="btn btn-sm btn-primary">
        Retry Connection
      </button>
    </div>

    <!-- Processing Form -->
    <div v-else class="form-section">
      <!-- Language Selection -->
      <div class="form-group">
        <label>Target Language</label>
        <div class="language-options">
          <button
            v-for="lang in supportedLanguages"
            :key="lang.code"
            @click="selectedLanguage = lang.code"
            :class="['lang-btn', { active: selectedLanguage === lang.code }]"
            :title="lang.name"
          >
            {{ lang.flag }} {{ lang.code }}
          </button>
        </div>
      </div>

      <!-- Processing Options -->
      <div class="form-group">
        <label class="checkbox">
          <input
            v-model="forceReprocess"
            type="checkbox"
          />
          Force reprocessing (overwrite existing)
        </label>
      </div>

      <!-- Page Range (Optional) -->
      <div class="form-group">
        <label>Pages to Process</label>
        <div class="page-range">
          <span>{{ pageInfo.total }} pages</span>
          <span v-if="pageInfo.processed > 0" class="ml-2">
            ({{ pageInfo.processed }} already processed)
          </span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div v-if="isProcessing" class="progress-section">
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: progress + '%' }"
          ></div>
        </div>
        <div class="progress-text">
          <span>{{ currentPage }} / {{ totalPages }} pages</span>
          <span class="time-estimate">
            ~{{ estimatedTime }}m remaining
          </span>
        </div>
        <p class="status-message">{{ statusMessage }}</p>
      </div>

      <!-- Results Summary -->
      <div v-else-if="processingComplete" class="results-section">
        <div class="success-badge">✓ Completed</div>
        <div class="results-grid">
          <div class="result-item">
            <span class="label">Pages Processed</span>
            <span class="value">{{ results.pages_processed }}</span>
          </div>
          <div class="result-item">
            <span class="label">Lines Created</span>
            <span class="value">{{ results.lines_created }}</span>
          </div>
          <div class="result-item">
            <span class="label">Processing Time</span>
            <span class="value">{{ results.processing_time }}s</span>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="button-group">
        <button
          @click="startProcessing"
          :disabled="isProcessing || !isEngineReady"
          class="btn btn-primary"
        >
          <span v-if="!isProcessing">▶ Start Surya OCR</span>
          <span v-else>⏸ Processing...</span>
        </button>

        <button
          @click="viewResults"
          v-if="processingComplete"
          class="btn btn-secondary"
        >
          View Results
        </button>

        <button
          @click="resetForm"
          class="btn btn-outline"
        >
          Reset
        </button>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-alert">
      <strong>Error:</strong> {{ error }}
      <button @click="error = null" class="close-btn">×</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SuryaOCRPanel',
  
  props: {
    documentId: {
      type: Number,
      required: true
    }
  },

  data() {
    return {
      engineStatus: {
        status: 'checking',
        message: 'Checking Surya engine status...'
      },
      isEngineReady: false,
      selectedLanguage: 'he',
      forceReprocess: false,
      isProcessing: false,
      processingComplete: false,
      error: null,
      
      // Progress tracking
      progress: 0,
      currentPage: 0,
      totalPages: 0,
      statusMessage: '',
      estimatedTime: 0,
      
      // Results
      results: {
        pages_processed: 0,
        lines_created: 0,
        processing_time: 0
      },
      
      // Page info
      pageInfo: {
        total: 0,
        processed: 0
      },
      
      // Languages
      supportedLanguages: [
        { code: 'he', name: 'Hebrew', flag: '🇮🇱' },
        { code: 'ar', name: 'Arabic', flag: '🇸🇦' },
        { code: 'en', name: 'English', flag: '🇺🇸' },
        { code: 'fr', name: 'French', flag: '🇫🇷' },
        { code: 'de', name: 'German', flag: '🇩🇪' }
      ],
      
      // Polling
      pollInterval: null,
      taskId: null
    }
  },

  mounted() {
    this.checkEngineStatus();
    this.getPageInfo();
  },

  beforeDestroy() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
  },

  methods: {
    /**
     * Check if Surya engine is available
     */
    async checkEngineStatus() {
      try {
        const response = await fetch('/api/ocr/engines/surya/');
        const data = await response.json();
        
        if (response.ok) {
          this.engineStatus = {
            status: 'ready',
            message: `Surya OCR ready (CUDA: ${data.status.cuda_available})`
          };
          this.isEngineReady = true;
        } else {
          this.engineStatus = {
            status: 'unavailable',
            message: data.error || 'Surya engine not available'
          };
          this.isEngineReady = false;
        }
      } catch (e) {
        this.engineStatus = {
          status: 'error',
          message: `Connection error: ${e.message}`
        };
        this.isEngineReady = false;
      }
    },

    /**
     * Get page information
     */
    async getPageInfo() {
      try {
        const response = await fetch(`/api/documents/${this.documentId}/ocr/surya/status/`);
        const data = await response.json();
        
        this.pageInfo = {
          total: data.total_parts,
          processed: data.parts_processed
        };
        this.totalPages = data.total_parts;
      } catch (e) {
        console.error('Failed to get page info:', e);
      }
    },

    /**
     * Start Surya OCR processing
     */
    async startProcessing() {
      this.isProcessing = true;
      this.processingComplete = false;
      this.error = null;
      this.progress = 0;
      this.currentPage = 0;

      try {
        // Start processing
        const response = await fetch(
          `/api/documents/${this.documentId}/ocr/surya/`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              language: this.selectedLanguage,
              force: this.forceReprocess
            })
          }
        );

        const data = await response.json();

        if (response.ok && data.task_id) {
          this.taskId = data.task_id;
          this.statusMessage = data.message;
          this.startPolling();
        } else if (response.ok) {
          // Synchronous processing completed
          this.results = {
            pages_processed: data.transcriptions_created,
            lines_created: data.transcriptions_created,
            processing_time: 0
          };
          this.progress = 100;
          this.isProcessing = false;
          this.processingComplete = true;
        } else {
          throw new Error(data.error || 'Processing failed');
        }
      } catch (e) {
        this.error = e.message;
        this.isProcessing = false;
      }
    },

    /**
     * Poll for progress updates
     */
    startPolling() {
      this.pollInterval = setInterval(() => {
        this.checkProgress();
      }, 2000); // Poll every 2 seconds
    },

    /**
     * Check processing progress
     */
    async checkProgress() {
      try {
        const response = await fetch(
          `/api/documents/${this.documentId}/ocr/surya/status/`
        );
        const data = await response.json();

        this.progress = data.progress;
        this.currentPage = data.parts_processed;
        this.statusMessage = `Processing page ${this.currentPage}/${this.totalPages}...`;

        // Calculate estimated time (rough estimate: 3 pages per minute on CPU)
        const remainingPages = this.totalPages - this.currentPage;
        this.estimatedTime = Math.ceil(remainingPages / 3);

        // Check if completed
        if (data.status === 'completed') {
          clearInterval(this.pollInterval);
          this.isProcessing = false;
          this.processingComplete = true;
          this.results = {
            pages_processed: data.parts_processed,
            lines_created: data.processed_lines,
            processing_time: '~' + Math.ceil(
              (this.totalPages / 3) * 60
            )
          };
        }
      } catch (e) {
        console.error('Failed to check progress:', e);
      }
    },

    /**
     * View processing results
     */
    viewResults() {
      fetch(`/api/documents/${this.documentId}/ocr/surya/results/`)
        .then(r => r.json())
        .then(data => {
          console.log('Results:', data);
          // Could open a modal or navigate to results page
          this.$emit('results-ready', data);
        })
        .catch(e => {
          this.error = `Failed to load results: ${e.message}`;
        });
    },

    /**
     * Reset form
     */
    resetForm() {
      this.isProcessing = false;
      this.processingComplete = false;
      this.progress = 0;
      this.error = null;
      this.forceReprocess = false;
    }
  }
}
</script>

<style scoped>
.surya-ocr-panel {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 15px;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.engine-icon {
  font-size: 24px;
}

.badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  margin-left: auto;
}

.badge.ready {
  background: #d4edda;
  color: #155724;
}

.badge.checking {
  background: #d1ecf1;
  color: #0c5460;
}

.badge.error,
.badge.unavailable {
  background: #f8d7da;
  color: #721c24;
}

.status-warning {
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 20px;
  color: #856404;
}

.status-warning p {
  margin: 0 0 10px 0;
}

.form-section {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.language-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.lang-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.lang-btn:hover {
  border-color: #007bff;
}

.lang-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.checkbox input {
  cursor: pointer;
}

.page-range {
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  color: #666;
}

.ml-2 {
  margin-left: 8px;
}

.progress-section {
  margin: 20px 0;
}

.progress-bar {
  width: 100%;
  height: 24px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #0056b3);
  transition: width 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
}

.time-estimate {
  color: #999;
}

.status-message {
  margin: 10px 0 0 0;
  color: #666;
  font-size: 13px;
}

.results-section {
  background: #f0f8ff;
  border: 1px solid #b3d9ff;
  border-radius: 4px;
  padding: 15px;
  margin: 20px 0;
}

.success-badge {
  color: #28a745;
  font-weight: bold;
  margin-bottom: 10px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.result-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.result-item .label {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.result-item .value {
  font-size: 20px;
  font-weight: bold;
  color: #007bff;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-outline {
  background: white;
  color: #007bff;
  border: 1px solid #007bff;
}

.btn-outline:hover {
  background: #f8f9fa;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.error-alert {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
  border-radius: 4px;
  padding: 12px 16px;
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  color: #721c24;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
}

.close-btn:hover {
  opacity: 0.7;
}
</style>
