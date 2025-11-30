<template>
  <div class="ocr-comparison-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="mb-2">
              <i class="fas fa-balance-scale text-primary"></i>
              {{ translate('compareEngines') }}
            </h1>
            <p class="subtitle text-muted mb-0">
              {{ documentName }} - {{ totalTranscriptions }} {{ translate('transcription1') }}
            </p>
          </div>
          <div class="col-md-4 text-end">
            <button 
              @click="refreshData" 
              class="btn btn-outline-secondary me-2"
              :disabled="loading"
            >
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
              {{ translate('refresh') }}
            </button>
            <button 
              @click="showStatistics = !showStatistics" 
              class="btn btn-outline-info"
            >
              <i class="fas fa-chart-bar"></i>
              {{ translate('statistics') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Panel (Collapsible) -->
    <transition name="slide-down">
      <div v-if="showStatistics" class="statistics-panel">
        <div class="container-fluid">
          <comparison-statistics
            :document-id="documentId"
            :statistics="statistics"
            @close="showStatistics = false"
          />
        </div>
      </div>
    </transition>

    <!-- Main Content -->
    <div class="container-fluid mt-4">
      <div class="row">
        <!-- Left Panel: Selection -->
        <div class="col-lg-4 mb-4">
          <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">
                <i class="fas fa-list-check"></i>
                {{ translate('selectTranscriptions') }}
              </h5>
            </div>
            <div class="card-body">
              <!-- Transcription 1 Selector -->
              <div class="mb-3">
                <label class="form-label fw-bold">
                  {{ translate('transcription1') }}
                  <span class="badge bg-info">A</span>
                </label>
                <transcription-selector
                  :transcriptions="transcriptions"
                  :selected-id="selectedTrans1"
                  :exclude-id="selectedTrans2"
                  @select="selectTranscription1"
                />
              </div>

              <!-- Transcription 2 Selector -->
              <div class="mb-3">
                <label class="form-label fw-bold">
                  {{ translate('transcription2') }}
                  <span class="badge bg-success">B</span>
                </label>
                <transcription-selector
                  :transcriptions="transcriptions"
                  :selected-id="selectedTrans2"
                  :exclude-id="selectedTrans1"
                  @select="selectTranscription2"
                />
              </div>

              <!-- Ground Truth Selector (Optional) -->
              <div class="mb-3">
                <label class="form-label fw-bold">
                  {{ translate('groundTruth') }}
                  <span class="badge bg-warning">GT</span>
                  <small class="text-muted">({{ translate('optional') }})</small>
                </label>
                <transcription-selector
                  :transcriptions="transcriptions"
                  :selected-id="selectedGroundTruth"
                  :exclude-id="null"
                  :allow-none="true"
                  @select="selectGroundTruth"
                />
              </div>

              <!-- Comparison Options -->
              <div class="comparison-options mb-3">
                <h6 class="fw-bold">{{ translate('options') }}</h6>
                <div class="form-check">
                  <input 
                    v-model="options.ignore_case" 
                    class="form-check-input" 
                    type="checkbox" 
                    id="opt-ignore-case"
                  >
                  <label class="form-check-label" for="opt-ignore-case">
                    {{ translate('ignoreCase') }}
                  </label>
                </div>
                <div class="form-check">
                  <input 
                    v-model="options.ignore_punctuation" 
                    class="form-check-input" 
                    type="checkbox" 
                    id="opt-ignore-punct"
                  >
                  <label class="form-check-label" for="opt-ignore-punct">
                    {{ translate('ignorePunctuation') }}
                  </label>
                </div>
                <div class="form-check">
                  <input 
                    v-model="options.ignore_whitespace" 
                    class="form-check-input" 
                    type="checkbox" 
                    id="opt-ignore-space"
                  >
                  <label class="form-check-label" for="opt-ignore-space">
                    {{ translate('ignoreWhitespace') }}
                  </label>
                </div>
                <div class="form-check">
                  <input 
                    v-model="options.show_diff" 
                    class="form-check-input" 
                    type="checkbox" 
                    id="opt-show-diff"
                  >
                  <label class="form-check-label" for="opt-show-diff">
                    {{ translate('showDiff') }}
                  </label>
                </div>
              </div>

              <!-- Compare Button -->
              <button 
                @click="performComparison" 
                class="btn btn-primary btn-lg w-100"
                :disabled="!canCompare || comparing"
              >
                <span v-if="comparing">
                  <span class="spinner-border spinner-border-sm me-2"></span>
                  {{ translate('comparing') }}...
                </span>
                <span v-else>
                  <i class="fas fa-play me-2"></i>
                  {{ translate('compare') }}
                </span>
              </button>

              <div v-if="!canCompare" class="alert alert-warning mt-3 mb-0">
                <small>
                  <i class="fas fa-info-circle"></i>
                  {{ translate('selectAtLeastTwo') }}
                </small>
              </div>
            </div>
          </div>

          <!-- Quick Stats Card -->
          <div v-if="comparisonResult" class="card shadow-sm mt-3">
            <div class="card-header bg-success text-white">
              <h6 class="mb-0">
                <i class="fas fa-trophy"></i>
                {{ translate('winner') }}
              </h6>
            </div>
            <div class="card-body">
              <quick-comparison-stats :result="comparisonResult" />
            </div>
          </div>
        </div>

        <!-- Right Panel: Results -->
        <div class="col-lg-8">
          <!-- No Results Yet -->
          <div v-if="!comparisonResult" class="empty-state">
            <div class="card shadow-sm text-center p-5">
              <i class="fas fa-search fa-4x text-muted mb-3"></i>
              <h4 class="text-muted">{{ translate('noComparison') }}</h4>
              <p class="text-muted">
                {{ translate('selectTranscriptionsHint') }}
              </p>
            </div>
          </div>

          <!-- Comparison Results -->
          <div v-else class="comparison-results">
            <!-- Metrics Cards -->
            <div class="row mb-4">
              <div class="col-md-6">
                <metrics-card
                  :title="comparisonResult.transcription_1.name"
                  :metrics="getMetrics1()"
                  badge="A"
                  badge-color="info"
                  :is-winner="comparisonResult.metrics?.winner === 'transcription_1'"
                />
              </div>
              <div class="col-md-6">
                <metrics-card
                  :title="comparisonResult.transcription_2.name"
                  :metrics="getMetrics2()"
                  badge="B"
                  badge-color="success"
                  :is-winner="comparisonResult.metrics?.winner === 'transcription_2'"
                />
              </div>
            </div>

            <!-- Detailed Comparison Tabs -->
            <div class="card shadow-sm">
              <div class="card-header">
                <ul class="nav nav-tabs card-header-tabs" role="tablist">
                  <li class="nav-item">
                    <a 
                      class="nav-link" 
                      :class="{ active: activeTab === 'diff' }"
                      @click="activeTab = 'diff'"
                      href="#"
                    >
                      <i class="fas fa-columns"></i>
                      {{ translate('visualDiff') }}
                    </a>
                  </li>
                  <li class="nav-item">
                    <a 
                      class="nav-link" 
                      :class="{ active: activeTab === 'metrics' }"
                      @click="activeTab = 'metrics'"
                      href="#"
                    >
                      <i class="fas fa-chart-line"></i>
                      {{ translate('metrics') }}
                    </a>
                  </li>
                  <li class="nav-item" v-if="comparisonResult.metrics">
                    <a 
                      class="nav-link" 
                      :class="{ active: activeTab === 'analysis' }"
                      @click="activeTab = 'analysis'"
                      href="#"
                    >
                      <i class="fas fa-microscope"></i>
                      {{ translate('detailedAnalysis') }}
                    </a>
                  </li>
                  <li class="nav-item">
                    <a 
                      class="nav-link" 
                      :class="{ active: activeTab === 'export' }"
                      @click="activeTab = 'export'"
                      href="#"
                    >
                      <i class="fas fa-download"></i>
                      {{ translate('export') }}
                    </a>
                  </li>
                </ul>
              </div>
              <div class="card-body">
                <!-- Visual Diff Tab -->
                <div v-show="activeTab === 'diff'">
                  <visual-diff-viewer
                    v-if="comparisonResult.diff_data"
                    :diff-data="comparisonResult.diff_data"
                    :trans1-name="comparisonResult.transcription_1.name"
                    :trans2-name="comparisonResult.transcription_2.name"
                  />
                </div>

                <!-- Metrics Tab -->
                <div v-show="activeTab === 'metrics'">
                  <comparison-charts
                    v-if="comparisonResult.metrics"
                    :metrics="comparisonResult.metrics"
                    :trans1="comparisonResult.transcription_1"
                    :trans2="comparisonResult.transcription_2"
                  />
                </div>

                <!-- Detailed Analysis Tab -->
                <div v-show="activeTab === 'analysis'">
                  <detailed-analysis
                    v-if="comparisonResult.metrics"
                    :analysis1="comparisonResult.detailed_analysis_1"
                    :analysis2="comparisonResult.detailed_analysis_2"
                    :trans1="comparisonResult.transcription_1"
                    :trans2="comparisonResult.transcription_2"
                  />
                </div>

                <!-- Export Tab -->
                <div v-show="activeTab === 'export'">
                  <export-panel
                    :comparison-result="comparisonResult"
                    :document-name="documentName"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Alert -->
    <div 
      v-if="errorMessage" 
      class="alert alert-danger alert-dismissible position-fixed bottom-0 end-0 m-3"
      style="z-index: 1050; max-width: 400px;"
    >
      <button 
        type="button" 
        class="btn-close" 
        @click="errorMessage = ''"
      ></button>
      <i class="fas fa-exclamation-triangle"></i>
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import TranscriptionSelector from './TranscriptionSelector.vue'
import ComparisonStatistics from './ComparisonStatistics.vue'
import QuickComparisonStats from './QuickComparisonStats.vue'
import MetricsCard from './MetricsCard.vue'
import VisualDiffViewer from './VisualDiffViewer.vue'
import ComparisonCharts from './ComparisonCharts.vue'
import DetailedAnalysis from './DetailedAnalysis.vue'
import ExportPanel from './ExportPanel.vue'

export default {
  name: 'OCRComparisonDashboard',
  
  components: {
    AdvancedAnalysisPanel: () => import('./AdvancedAnalysisPanel.vue'),
    TranscriptionSelector,
    ComparisonStatistics,
    QuickComparisonStats,
    MetricsCard,
    VisualDiffViewer,
    ComparisonCharts,
    DetailedAnalysis,
    ExportPanel,
  },
  
  props: {
    documentId: {
      type: Number,
      required: true,
    },
    documentName: {
      type: String,
      required: true,
    },
    initialTranscriptions: {
      type: Array,
      default: () => [],
    },
  },
  
  data() {
    return {
    // Phase 2 Integration
    phase1Available: false,
    advancedMetrics: null,
      transcriptions: [],
      selectedTrans1: null,
      selectedTrans2: null,
      selectedGroundTruth: null,
      options: {
        ignore_case: false,
        ignore_punctuation: false,
        ignore_whitespace: false,
        show_diff: true,
      },
      comparisonResult: null,
      statistics: null,
      loading: false,
      comparing: false,
      showStatistics: false,
      activeTab: 'diff',
      errorMessage: '',
    }
  },
  
  computed: {
    totalTranscriptions() {
      return this.transcriptions.length
    },
    
    canCompare() {
      return this.selectedTrans1 && this.selectedTrans2
    },
  },
  
  mounted() {
    this.loadTranscriptions()
    this.loadStatistics()
  },
  
  methods: {
    translate(key) {
      return window.COMPARISON_TRANSLATIONS?.[key] || key
    },
    
    async loadTranscriptions() {
      this.loading = true
      try {
        const response = await fetch(
          `/cerberus/api/document/${this.documentId}/transcriptions/`
        )
        if (!response.ok) throw new Error('Failed to load transcriptions')
        
        const data = await response.json()
        this.transcriptions = data.transcriptions
      } catch (error) {
        console.error('Error loading transcriptions:', error)
        this.errorMessage = 'Failed to load transcriptions'
      } finally {
        this.loading = false
      }
    },
    
    async loadStatistics() {
      try {
        const response = await fetch(
          `/cerberus/api/document/${this.documentId}/statistics/`
        )
        if (!response.ok) return
        
        this.statistics = await response.json()
      } catch (error) {
        console.error('Error loading statistics:', error)
      }
    },
    
    selectTranscription1(id) {
      this.selectedTrans1 = id
    },
    
    selectTranscription2(id) {
      this.selectedTrans2 = id
    },
    
    selectGroundTruth(id) {
      this.selectedGroundTruth = id
    },
    
    async performComparison() {
      if (!this.canCompare) return
      
      this.comparing = true
      this.errorMessage = ''
      
      try {
        const payload = {
          transcription_1_id: this.selectedTrans1,
          transcription_2_id: this.selectedTrans2,
          ground_truth_id: this.selectedGroundTruth,
          options: this.options,
        }
        
        const response = await fetch('/cerberus/api/compare/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken(),
          },
          body: JSON.stringify(payload),
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.error || 'Comparison failed')
        }
        
        this.comparisonResult = await response.json()
        this.activeTab = 'diff'
      } catch (error) {
        console.error('Comparison error:', error)
        this.errorMessage = error.message
      } finally {
        this.comparing = false
      }
    },
    
    refreshData() {
      this.loadTranscriptions()
      this.loadStatistics()
      if (this.canCompare) {
        this.performComparison()
      }
    },
    
    getMetrics1() {
      const result = this.comparisonResult
      if (!result.metrics) {
        return {
          length: result.transcription_1.text_length,
          model: result.transcription_1.model,
        }
      }
      
      return {
        cer: result.metrics.cer_1,
        wer: result.metrics.wer_1,
        accuracy: result.metrics.accuracy_1,
        length: result.transcription_1.text_length,
        model: result.transcription_1.model,
      }
    },
    
    getMetrics2() {
      const result = this.comparisonResult
      if (!result.metrics) {
        return {
          length: result.transcription_2.text_length,
          model: result.transcription_2.model,
        }
      }
      
      return {
        cer: result.metrics.cer_2,
        wer: result.metrics.wer_2,
        accuracy: result.metrics.accuracy_2,
        length: result.transcription_2.text_length,
        model: result.transcription_2.model,
      }
    },
    
    getCsrfToken() {
      const cookies = document.cookie.split(';')
      for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=')
        if (name === 'csrftoken') {
          return value
        }
      }
      return ''
    },
  },
}
</script>

<style scoped>
.ocr-comparison-dashboard {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 2rem 0;
  direction: rtl;
}

.dashboard-header {
  background: white;
  padding: 1.5rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

.subtitle {
  font-size: 1rem;
}

.statistics-panel {
  background: white;
  padding: 1.5rem 0;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from, .slide-down-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

.card {
  border: none;
  border-radius: 8px;
}

.card-header {
  border-radius: 8px 8px 0 0 !important;
  border-bottom: 2px solid rgba(0,0,0,0.1);
}

.comparison-options .form-check {
  margin-bottom: 0.5rem;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 500px;
}

.nav-tabs .nav-link {
  border: none;
  color: #6c757d;
  font-weight: 500;
  padding: 0.75rem 1.25rem;
}

.nav-tabs .nav-link:hover {
  border-color: transparent;
  color: #495057;
}

.nav-tabs .nav-link.active {
  color: #007bff;
  border-bottom: 3px solid #007bff;
  background: transparent;
}

@media (max-width: 768px) {
  .dashboard-header h1 {
    font-size: 1.5rem;
  }
  
  .ocr-comparison-dashboard {
    padding: 1rem 0;
  }
}
</style>

