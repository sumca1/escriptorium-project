<template>
  <div class="batch-analysis-panel" dir="rtl">
    <!-- Header -->
    <div class="panel-header">
      <h2>{{ translate('cerberus.batchAnalysis.title') }}</h2>
      <p class="description">{{ translate('cerberus.batchAnalysis.description') }}</p>
    </div>

    <!-- Step 1: Select Transcriptions -->
    <div class="selection-section" v-if="currentStep === 'select'">
      <h3>{{ translate('cerberus.batchAnalysis.selectTranscriptions') }}</h3>
      
      <div class="transcription-selector">
        <div class="selector-column">
          <label>{{ translate('cerberus.batchAnalysis.groundTruth') }}</label>
          <select 
            v-model="selectedGroundTruth" 
            @change="addPair"
            class="form-control"
          >
            <option value="">{{ translate('cerberus.batchAnalysis.selectOne') }}</option>
            <option 
              v-for="trans in availableTranscriptions" 
              :key="trans.id" 
              :value="trans.id"
            >
              {{ trans.name }} ({{ trans.id }})
            </option>
          </select>
        </div>

        <div class="selector-column">
          <label>{{ translate('cerberus.batchAnalysis.hypothesis') }}</label>
          <select 
            v-model="selectedHypothesis" 
            @change="addPair"
            class="form-control"
          >
            <option value="">{{ translate('cerberus.batchAnalysis.selectOne') }}</option>
            <option 
              v-for="trans in availableTranscriptions" 
              :key="trans.id" 
              :value="trans.id"
            >
              {{ trans.name }} ({{ trans.id }})
            </option>
          </select>
        </div>

        <div class="selector-column">
          <label>{{ translate('cerberus.batchAnalysis.name') }}</label>
          <input 
            v-model="pairName" 
            type="text" 
            class="form-control"
            :placeholder="translate('cerberus.batchAnalysis.namePlaceholder')"
          />
        </div>

        <div class="selector-column">
          <button 
            @click="addPair" 
            class="btn btn-primary"
            :disabled="!selectedGroundTruth || !selectedHypothesis"
          >
            {{ translate('cerberus.batchAnalysis.addPair') }}
          </button>
        </div>
      </div>

      <!-- Selected Pairs Table -->
      <div class="selected-pairs" v-if="transcriptionPairs.length > 0">
        <h4>{{ translate('cerberus.batchAnalysis.selectedPairs') }} ({{ transcriptionPairs.length }})</h4>
        
        <table class="table table-striped">
          <thead>
            <tr>
              <th>{{ translate('cerberus.batchAnalysis.name') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.groundTruth') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.hypothesis') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(pair, index) in transcriptionPairs" :key="index">
              <td>{{ pair.name }}</td>
              <td>{{ pair.ground_truth_id }}</td>
              <td>{{ pair.hypothesis_id }}</td>
              <td>
                <button 
                  @click="removePair(index)" 
                  class="btn btn-sm btn-danger"
                >
                  {{ translate('cerberus.batchAnalysis.remove') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Mode Selection -->
        <div class="mode-selection">
          <label>
            <input 
              type="radio" 
              v-model="mode" 
              value="sequential"
            />
            {{ translate('cerberus.batchAnalysis.sequential') }}
            <span class="mode-hint">{{ translate('cerberus.batchAnalysis.sequentialHint') }}</span>
          </label>
          <label>
            <input 
              type="radio" 
              v-model="mode" 
              value="parallel"
            />
            {{ translate('cerberus.batchAnalysis.parallel') }}
            <span class="mode-hint">{{ translate('cerberus.batchAnalysis.parallelHint') }}</span>
          </label>
        </div>

        <!-- Start Button -->
        <div class="action-buttons">
          <button 
            @click="startBatchAnalysis" 
            class="btn btn-success btn-lg"
            :disabled="isProcessing"
          >
            {{ translate('cerberus.batchAnalysis.startAnalysis') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Step 2: Progress Tracking -->
    <div class="progress-section" v-if="currentStep === 'processing'">
      <h3>{{ translate('cerberus.batchAnalysis.analyzing') }}</h3>
      
      <!-- Progress Bar -->
      <div class="progress-container">
        <div class="progress-bar-wrapper">
          <div 
            class="progress-bar" 
            :style="{ width: progress.percentage + '%' }"
          >
            {{ progress.percentage }}%
          </div>
        </div>
        
        <div class="progress-stats">
          <span class="stat completed">
            ✓ {{ translate('cerberus.batchAnalysis.completed') }}: {{ progress.completed }}
          </span>
          <span class="stat pending">
            ⏳ {{ translate('cerberus.batchAnalysis.pending') }}: {{ progress.pending }}
          </span>
          <span class="stat failed" v-if="progress.failed > 0">
            ✗ {{ translate('cerberus.batchAnalysis.failed') }}: {{ progress.failed }}
          </span>
        </div>
      </div>

      <!-- Live Results Table -->
      <div class="live-results" v-if="results.length > 0">
        <h4>{{ translate('cerberus.batchAnalysis.results') }}</h4>
        
        <table class="table table-hover">
          <thead>
            <tr>
              <th>{{ translate('cerberus.batchAnalysis.name') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.status') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.cer') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.accuracy') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.errors') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="result in results" :key="result.name">
              <td>{{ result.name }}</td>
              <td>
                <span 
                  class="badge" 
                  :class="getStatusClass(result.status)"
                >
                  {{ translate('cerberus.batchAnalysis.' + result.status) }}
                </span>
              </td>
              <td>{{ formatNumber(result.cer) }}</td>
              <td>{{ formatNumber(result.accuracy) }}%</td>
              <td>{{ result.errors || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Auto-refresh Notice -->
      <div class="auto-refresh-notice">
        <span>🔄 {{ translate('cerberus.batchAnalysis.autoRefresh') }}</span>
      </div>
    </div>

    <!-- Step 3: Results -->
    <div class="results-section" v-if="currentStep === 'completed'">
      <h3>{{ translate('cerberus.batchAnalysis.analysisComplete') }}</h3>
      
      <!-- Summary -->
      <div class="summary-cards">
        <div class="summary-card">
          <div class="card-value">{{ progress.total }}</div>
          <div class="card-label">{{ translate('cerberus.batchAnalysis.total') }}</div>
        </div>
        <div class="summary-card success">
          <div class="card-value">{{ progress.completed }}</div>
          <div class="card-label">{{ translate('cerberus.batchAnalysis.completed') }}</div>
        </div>
        <div class="summary-card danger" v-if="progress.failed > 0">
          <div class="card-value">{{ progress.failed }}</div>
          <div class="card-label">{{ translate('cerberus.batchAnalysis.failed') }}</div>
        </div>
        <div class="summary-card">
          <div class="card-value">{{ averageCER }}</div>
          <div class="card-label">{{ translate('cerberus.batchAnalysis.averageCER') }}</div>
        </div>
      </div>

      <!-- Results Table -->
      <div class="final-results">
        <h4>{{ translate('cerberus.batchAnalysis.detailedResults') }}</h4>
        
        <table class="table table-bordered">
          <thead>
            <tr>
              <th>{{ translate('cerberus.batchAnalysis.name') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.cer') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.accuracy') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.errors') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.substitutions') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.insertions') }}</th>
              <th>{{ translate('cerberus.batchAnalysis.deletions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="result in results" :key="result.name">
              <td>{{ result.name }}</td>
              <td>{{ formatNumber(result.cer) }}</td>
              <td>{{ formatNumber(result.accuracy) }}%</td>
              <td>{{ result.errors || 0 }}</td>
              <td>{{ result.substitutions || 0 }}</td>
              <td>{{ result.insertions || 0 }}</td>
              <td>{{ result.deletions || 0 }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Export Buttons -->
      <div class="export-buttons">
        <button 
          @click="exportResults('csv')" 
          class="btn btn-primary"
        >
          📄 {{ translate('cerberus.batchAnalysis.exportCSV') }}
        </button>
        <button 
          @click="exportResults('json')" 
          class="btn btn-secondary"
        >
          📋 {{ translate('cerberus.batchAnalysis.exportJSON') }}
        </button>
        <button 
          @click="resetAnalysis" 
          class="btn btn-outline"
        >
          🔄 {{ translate('cerberus.batchAnalysis.newAnalysis') }}
        </button>
      </div>
    </div>

    <!-- Error Display -->
    <div class="error-message" v-if="errorMessage">
      <div class="alert alert-danger">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BatchAnalysisPanel',
  
  data() {
    return {
      // UI State
      currentStep: 'select', // 'select', 'processing', 'completed'
      isProcessing: false,
      errorMessage: null,
      
      // Selection
      availableTranscriptions: [],
      selectedGroundTruth: '',
      selectedHypothesis: '',
      pairName: '',
      transcriptionPairs: [],
      mode: 'sequential',
      
      // Batch Processing
      batchId: null,
      progress: {
        total: 0,
        completed: 0,
        pending: 0,
        failed: 0,
        percentage: 0
      },
      results: [],
      
      // Auto-refresh
      refreshInterval: null
    };
  },
  
  computed: {
    averageCER() {
      if (this.results.length === 0) return '0.00';
      
      const validResults = this.results.filter(r => r.cer !== null);
      if (validResults.length === 0) return '0.00';
      
      const sum = validResults.reduce((acc, r) => acc + r.cer, 0);
      return (sum / validResults.length).toFixed(3);
    }
  },
  
  mounted() {
    this.loadAvailableTranscriptions();
  },
  
  beforeDestroy() {
    // Clear auto-refresh interval
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  
  methods: {
    async loadAvailableTranscriptions() {
      try {
        // Get document ID from URL (if available)
        const documentId = this.getDocumentIdFromURL();
        
        if (documentId) {
          const response = await fetch(
            `${window.API_BASE_URL}/api/documents/${documentId}/transcriptions/`,
            {
              headers: {
                'Authorization': `Token ${window.USER_TOKEN}`,
                'Content-Type': 'application/json'
              }
            }
          );
          
          if (response.ok) {
            const data = await response.json();
            this.availableTranscriptions = data.results || data;
          }
        }
      } catch (error) {
        console.error('Failed to load transcriptions:', error);
        this.errorMessage = this.translate('cerberus.batchAnalysis.loadError');
      }
    },
    
    getDocumentIdFromURL() {
      // Extract document ID from URL like /document/5/part/114/edit/
      const match = window.location.pathname.match(/\/document\/(\d+)\//);
      return match ? match[1] : null;
    },
    
    addPair() {
      if (!this.selectedGroundTruth || !this.selectedHypothesis) {
        return;
      }
      
      const gtTrans = this.availableTranscriptions.find(
        t => t.id === parseInt(this.selectedGroundTruth)
      );
      const hypTrans = this.availableTranscriptions.find(
        t => t.id === parseInt(this.selectedHypothesis)
      );
      
      const name = this.pairName || 
        `${gtTrans?.name || this.selectedGroundTruth} vs ${hypTrans?.name || this.selectedHypothesis}`;
      
      this.transcriptionPairs.push({
        ground_truth_id: parseInt(this.selectedGroundTruth),
        hypothesis_id: parseInt(this.selectedHypothesis),
        name: name
      });
      
      // Reset selection
      this.selectedGroundTruth = '';
      this.selectedHypothesis = '';
      this.pairName = '';
    },
    
    removePair(index) {
      this.transcriptionPairs.splice(index, 1);
    },
    
    async startBatchAnalysis() {
      if (this.transcriptionPairs.length === 0) {
        this.errorMessage = this.translate('cerberus.batchAnalysis.noPairsError');
        return;
      }
      
      this.isProcessing = true;
      this.errorMessage = null;
      
      try {
        const response = await fetch(
          `${window.API_BASE_URL}/api/cerberus/analyses/batch-analyze/`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Token ${window.USER_TOKEN}`,
              'Content-Type': 'application/json',
              'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
              transcription_pairs: this.transcriptionPairs,
              mode: this.mode
            })
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          this.batchId = data.batch_id;
          this.progress.total = data.total;
          
          // Switch to processing view
          this.currentStep = 'processing';
          
          // Start polling for progress
          this.startProgressPolling();
        } else {
          const error = await response.json();
          this.errorMessage = error.error || this.translate('cerberus.batchAnalysis.startError');
          this.isProcessing = false;
        }
      } catch (error) {
        console.error('Failed to start batch analysis:', error);
        this.errorMessage = this.translate('cerberus.batchAnalysis.startError');
        this.isProcessing = false;
      }
    },
    
    startProgressPolling() {
      // Poll every 2 seconds
      this.refreshInterval = setInterval(() => {
        this.updateProgress();
      }, 2000);
      
      // Initial update
      this.updateProgress();
    },
    
    async updateProgress() {
      if (!this.batchId) return;
      
      try {
        const response = await fetch(
          `${window.API_BASE_URL}/api/cerberus/analyses/batch-progress/${this.batchId}/`,
          {
            headers: {
              'Authorization': `Token ${window.USER_TOKEN}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          
          this.progress = data.progress;
          this.results = data.results;
          
          // Check if completed
          if (data.status === 'completed') {
            clearInterval(this.refreshInterval);
            this.currentStep = 'completed';
            this.isProcessing = false;
          }
        }
      } catch (error) {
        console.error('Failed to update progress:', error);
      }
    },
    
    async exportResults(format) {
      if (!this.batchId) return;
      
      const url = `${window.API_BASE_URL}/api/cerberus/analyses/batch-export/${this.batchId}/?format=${format}`;
      
      // Trigger download
      window.open(url, '_blank');
    },
    
    resetAnalysis() {
      this.currentStep = 'select';
      this.transcriptionPairs = [];
      this.batchId = null;
      this.progress = {
        total: 0,
        completed: 0,
        pending: 0,
        failed: 0,
        percentage: 0
      };
      this.results = [];
      this.isProcessing = false;
      this.errorMessage = null;
    },
    
    getStatusClass(status) {
      const classes = {
        'completed': 'badge-success',
        'pending': 'badge-warning',
        'failed': 'badge-danger',
        'running': 'badge-info'
      };
      return classes[status] || 'badge-secondary';
    },
    
    formatNumber(num) {
      if (num === null || num === undefined) return '-';
      return parseFloat(num).toFixed(3);
    },
    
    getCSRFToken() {
      const name = 'csrftoken';
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return decodeURIComponent(value);
      }
      return '';
    }
  }
};
</script>

<style scoped>
.batch-analysis-panel {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.panel-header {
  margin-bottom: 30px;
  text-align: center;
}

.panel-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.description {
  color: #7f8c8d;
  font-size: 14px;
}

/* Transcription Selector */
.transcription-selector {
  display: grid;
  grid-template-columns: 2fr 2fr 2fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.selector-column label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #2c3e50;
}

/* Selected Pairs Table */
.selected-pairs {
  margin-top: 30px;
}

.selected-pairs h4 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.table th,
.table td {
  padding: 12px;
  text-align: right;
  border-bottom: 1px solid #dee2e6;
}

.table thead th {
  background: #e9ecef;
  font-weight: 600;
  color: #2c3e50;
}

.table-striped tbody tr:nth-child(odd) {
  background: #f8f9fa;
}

.table-hover tbody tr:hover {
  background: #e9ecef;
}

/* Mode Selection */
.mode-selection {
  margin: 20px 0;
  padding: 15px;
  background: #fff3cd;
  border-radius: 8px;
}

.mode-selection label {
  display: block;
  margin-bottom: 10px;
  cursor: pointer;
}

.mode-hint {
  display: block;
  margin-right: 25px;
  font-size: 12px;
  color: #856404;
}

/* Progress Section */
.progress-container {
  margin: 30px 0;
}

.progress-bar-wrapper {
  width: 100%;
  height: 40px;
  background: #e9ecef;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 15px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #20c997);
  text-align: center;
  line-height: 40px;
  color: white;
  font-weight: 600;
  transition: width 0.3s ease;
}

.progress-stats {
  display: flex;
  justify-content: space-around;
  gap: 20px;
}

.stat {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
}

.stat.completed {
  background: #d4edda;
  color: #155724;
}

.stat.pending {
  background: #fff3cd;
  color: #856404;
}

.stat.failed {
  background: #f8d7da;
  color: #721c24;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin: 30px 0;
}

.summary-card {
  padding: 20px;
  background: white;
  border: 2px solid #dee2e6;
  border-radius: 12px;
  text-align: center;
}

.summary-card.success {
  border-color: #28a745;
  background: #d4edda;
}

.summary-card.danger {
  border-color: #dc3545;
  background: #f8d7da;
}

.card-value {
  font-size: 36px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
}

.card-label {
  font-size: 14px;
  color: #7f8c8d;
  text-transform: uppercase;
}

/* Buttons */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #218838;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-outline {
  background: white;
  border: 2px solid #dee2e6;
  color: #2c3e50;
}

.btn-lg {
  padding: 15px 40px;
  font-size: 18px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-buttons,
.export-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin: 30px 0;
}

/* Auto-refresh Notice */
.auto-refresh-notice {
  text-align: center;
  padding: 10px;
  background: #d1ecf1;
  border-radius: 6px;
  color: #0c5460;
  margin-top: 20px;
}

/* Badges */
.badge {
  padding: 5px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-success {
  background: #28a745;
  color: white;
}

.badge-warning {
  background: #ffc107;
  color: #212529;
}

.badge-danger {
  background: #dc3545;
  color: white;
}

.badge-info {
  background: #17a2b8;
  color: white;
}

/* Error Message */
.error-message {
  margin: 20px 0;
}

.alert {
  padding: 15px;
  border-radius: 8px;
}

.alert-danger {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
