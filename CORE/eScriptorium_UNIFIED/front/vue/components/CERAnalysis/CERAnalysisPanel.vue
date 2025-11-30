<template>
  <div class="cer-analysis-panel">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="sr-only">{{ translate('loading') }}...</span>
      </div>
      <p class="mt-3">{{ translate('cer.analyzing') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="fas fa-exclamation-triangle"></i>
      {{ error }}
    </div>

    <!-- Analysis Results -->
    <div v-else-if="analysis" class="analysis-content">
      <!-- Header with CER Display -->
      <div class="cer-header card mb-3">
        <div class="card-body">
          <div class="row align-items-center">
            <div class="col-md-4 text-center">
              <h5 class="text-muted mb-2">{{ translate('cer.characterErrorRate') }}</h5>
              <div :class="cerClass" class="cer-value">
                {{ analysis.cer_value.toFixed(2) }}%
              </div>
              <small class="text-muted">{{ cerLabel }}</small>
            </div>
            <div class="col-md-4 text-center border-start border-end">
              <h5 class="text-muted mb-2">{{ translate('cer.accuracy') }}</h5>
              <div :class="accuracyClass" class="accuracy-value">
                {{ analysis.accuracy.toFixed(2) }}%
              </div>
              <small class="text-muted">{{ accuracyLabel }}</small>
            </div>
            <div class="col-md-4 text-center">
              <h5 class="text-muted mb-2">{{ translate('cer.totalCharacters') }}</h5>
              <div class="total-chars-value">
                {{ analysis.total_characters.toLocaleString() }}
              </div>
              <small class="text-muted">{{ translate('cer.characters') }}</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Breakdown -->
      <div class="error-breakdown card mb-3">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-chart-pie"></i>
            {{ translate('cer.errorBreakdown') }}
          </h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-4">
              <div class="metric-box substitutions">
                <i class="fas fa-exchange-alt"></i>
                <div class="metric-label">{{ translate('cer.substitutions') }}</div>
                <div class="metric-value">{{ analysis.num_substitutions }}</div>
                <div class="metric-percent">
                  {{ analysis.error_breakdown.substitutions.toFixed(1) }}%
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="metric-box insertions">
                <i class="fas fa-plus-circle"></i>
                <div class="metric-label">{{ translate('cer.insertions') }}</div>
                <div class="metric-value">{{ analysis.num_insertions }}</div>
                <div class="metric-percent">
                  {{ analysis.error_breakdown.insertions.toFixed(1) }}%
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="metric-box deletions">
                <i class="fas fa-minus-circle"></i>
                <div class="metric-label">{{ translate('cer.deletions') }}</div>
                <div class="metric-value">{{ analysis.num_deletions }}</div>
                <div class="metric-percent">
                  {{ analysis.error_breakdown.deletions.toFixed(1) }}%
                </div>
              </div>
            </div>
          </div>
          <div class="mt-3">
            <small class="text-muted">
              <i class="fas fa-check-circle text-success"></i>
              {{ translate('cer.correctCharacters') }}: 
              <strong>{{ analysis.num_correct }}</strong>
            </small>
          </div>
        </div>
      </div>

      <!-- Tabs for Detailed Analysis -->
      <b-tabs content-class="mt-3" class="cer-tabs">
        <!-- Character Statistics Tab -->
        <b-tab :title="translate('cer.characterStatistics')" active>
          <CharacterStats 
            v-if="analysis.character_statistics"
            :stats="analysis.character_statistics"
          />
        </b-tab>

        <!-- Confusion Matrix Tab -->
        <b-tab :title="translate('cer.confusionMatrix')">
          <ConfusionMatrix
            v-if="analysis.confusion_statistics"
            :confusions="analysis.confusion_statistics"
            :analysis-id="analysis.id"
          />
        </b-tab>

        <!-- Unicode Blocks Tab -->
        <b-tab :title="translate('cer.unicodeBlocks')" v-if="analysis.block_statistics && analysis.block_statistics.length > 0">
          <UnicodeBlockStats
            :blocks="analysis.block_statistics"
          />
        </b-tab>

        <!-- Analysis Options Tab -->
        <b-tab :title="translate('cer.options')">
          <div class="card">
            <div class="card-body">
              <h6>{{ translate('cer.analysisOptions') }}</h6>
              <ul class="list-unstyled">
                <li>
                  <i :class="analysis.ignore_case ? 'fas fa-check-circle text-success' : 'fas fa-times-circle text-muted'"></i>
                  {{ translate('cer.ignoreCase') }}
                </li>
                <li>
                  <i :class="analysis.ignore_punctuation ? 'fas fa-check-circle text-success' : 'fas fa-times-circle text-muted'"></i>
                  {{ translate('cer.ignorePunctuation') }}
                </li>
                <li>
                  <i :class="analysis.ignore_whitespace ? 'fas fa-check-circle text-success' : 'fas fa-times-circle text-muted'"></i>
                  {{ translate('cer.ignoreWhitespace') }}
                </li>
                <li>
                  <i :class="analysis.ignore_numbers ? 'fas fa-check-circle text-success' : 'fas fa-times-circle text-muted'"></i>
                  {{ translate('cer.ignoreNumbers') }}
                </li>
                <li>
                  <i :class="analysis.ignore_newlines ? 'fas fa-check-circle text-success' : 'fas fa-times-circle text-muted'"></i>
                  {{ translate('cer.ignoreNewlines') }}
                </li>
              </ul>
              <div v-if="analysis.ignore_chars" class="mt-2">
                <small class="text-muted">
                  {{ translate('cer.ignoredChars') }}: <code>{{ analysis.ignore_chars }}</code>
                </small>
              </div>
            </div>
          </div>
        </b-tab>

        <!-- Batch Analysis Tab -->
        <b-tab :title="translate('cerberus.batchAnalysis.title') || 'Batch Analysis'">
          <BatchAnalysisPanel />
        </b-tab>
      </b-tabs>

      <!-- Export Actions -->
      <div class="export-actions mt-4">
        <div class="btn-group" role="group">
          <button 
            @click="exportJSON" 
            class="btn btn-outline-primary"
            :disabled="exporting"
          >
            <i class="fas fa-download"></i>
            {{ translate('cer.exportJSON') }}
          </button>
          <button 
            @click="exportCSVConfusion" 
            class="btn btn-outline-primary"
            :disabled="exporting"
          >
            <i class="fas fa-file-csv"></i>
            {{ translate('cer.exportCSVConfusion') }}
          </button>
          <button 
            @click="exportCSVCharacter" 
            class="btn btn-outline-primary"
            :disabled="exporting"
          >
            <i class="fas fa-file-csv"></i>
            {{ translate('cer.exportCSVCharacter') }}
          </button>
        </div>
        <small class="text-muted d-block mt-2">
          <i class="fas fa-info-circle"></i>
          {{ translate('cer.exportHint') }}
        </small>
      </div>

      <!-- Analysis Metadata -->
      <div class="analysis-metadata mt-4">
        <small class="text-muted">
          <i class="fas fa-calendar"></i>
          {{ translate('cer.createdAt') }}: {{ formatDate(analysis.created_at) }}
          <span class="ms-3">
            <i class="fas fa-fingerprint"></i>
            {{ translate('cer.analysisId') }}: {{ analysis.id }}
          </span>
        </small>
      </div>
    </div>
  </div>
</template>

<script>
import CharacterStats from './CharacterStats.vue'
import ConfusionMatrix from './ConfusionMatrix.vue'
import UnicodeBlockStats from './UnicodeBlockStats.vue'
import BatchAnalysisPanel from './BatchAnalysisPanel.vue'

export default {
  name: 'CERAnalysisPanel',
  
  components: {
    CharacterStats,
    ConfusionMatrix,
    UnicodeBlockStats,
    BatchAnalysisPanel
  },

  props: {
    analysisId: {
      type: Number,
      required: false,  // Changed from true to false - can be undefined initially
      default: null
    }
  },

  data() {
    return {
      analysis: null,
      loading: true,
      error: null,
      exporting: false
    }
  },

  computed: {
    cerClass() {
      if (!this.analysis) return ''
      const cer = this.analysis.cer_value
      if (cer < 5) return 'cer-excellent'
      if (cer < 15) return 'cer-good'
      return 'cer-needs-work'
    },

    cerLabel() {
      if (!this.analysis) return ''
      const cer = this.analysis.cer_value
      if (cer < 5) return this.translate('cer.excellent')
      if (cer < 15) return this.translate('cer.good')
      return this.translate('cer.needsImprovement')
    },

    accuracyClass() {
      if (!this.analysis) return ''
      const acc = this.analysis.accuracy
      if (acc > 95) return 'accuracy-excellent'
      if (acc > 85) return 'accuracy-good'
      return 'accuracy-needs-work'
    },

    accuracyLabel() {
      if (!this.analysis) return ''
      const acc = this.analysis.accuracy
      if (acc > 95) return this.translate('cer.excellent')
      if (acc > 85) return this.translate('cer.good')
      return this.translate('cer.needsImprovement')
    }
  },

  mounted() {
    this.fetchAnalysis()
  },

  methods: {
    async fetchAnalysis() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch(`/api/cerberus/analyses/${this.analysisId}/`, {
          headers: {
            'Accept': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        this.analysis = await response.json()
      } catch (err) {
        console.error('Failed to fetch CER analysis:', err)
        this.error = this.translate('cer.errorFetching') + ': ' + err.message
      } finally {
        this.loading = false
      }
    },

    async exportJSON() {
      this.exporting = true
      try {
        const url = `/api/cerberus/analyses/${this.analysisId}/export/?format=json`
        window.location.href = url
      } catch (err) {
        console.error('Export failed:', err)
        alert(this.translate('cer.exportError'))
      } finally {
        setTimeout(() => { this.exporting = false }, 1000)
      }
    },

    async exportCSVConfusion() {
      this.exporting = true
      try {
        const url = `/api/cerberus/analyses/${this.analysisId}/export/?format=csv&data_type=confusion`
        window.location.href = url
      } catch (err) {
        console.error('Export failed:', err)
        alert(this.translate('cer.exportError'))
      } finally {
        setTimeout(() => { this.exporting = false }, 1000)
      }
    },

    async exportCSVCharacter() {
      this.exporting = true
      try {
        const url = `/api/cerberus/analyses/${this.analysisId}/export/?format=csv&data_type=character`
        window.location.href = url
      } catch (err) {
        console.error('Export failed:', err)
        alert(this.translate('cer.exportError'))
      } finally {
        setTimeout(() => { this.exporting = false }, 1000)
      }
    },

    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString(this.$i18n.locale)
    }
  }
}
</script>

<style scoped>
.cer-analysis-panel {
  padding: 1rem;
}

.cer-header .card-body {
  padding: 1.5rem;
}

.cer-value,
.accuracy-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0.5rem 0;
}

.total-chars-value {
  font-size: 2rem;
  font-weight: bold;
  color: #6c757d;
  margin: 0.5rem 0;
}

.cer-excellent {
  color: #28a745;
}

.cer-good {
  color: #ffc107;
}

.cer-needs-work {
  color: #dc3545;
}

.accuracy-excellent {
  color: #28a745;
}

.accuracy-good {
  color: #ffc107;
}

.accuracy-needs-work {
  color: #dc3545;
}

.error-breakdown .metric-box {
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  background: #f8f9fa;
  border: 2px solid #dee2e6;
}

.metric-box i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  display: block;
}

.metric-box.substitutions i {
  color: #007bff;
}

.metric-box.insertions i {
  color: #28a745;
}

.metric-box.deletions i {
  color: #dc3545;
}

.metric-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #212529;
}

.metric-percent {
  font-size: 1rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.export-actions {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.analysis-metadata {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.cer-tabs >>> .nav-link {
  font-weight: 500;
}

.cer-tabs >>> .nav-link.active {
  background-color: #007bff;
  color: white;
}
</style>
