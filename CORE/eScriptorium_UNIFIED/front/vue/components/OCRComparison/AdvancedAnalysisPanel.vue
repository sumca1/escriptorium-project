<template>
  <div class="advanced-analysis-panel" dir="rtl">
    <!-- Header -->
    <div class="analysis-header mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h3 class="mb-1">
            <i class="fas fa-brain text-primary"></i>
            ניתוח מתקדם (Phase 1)
          </h3>
          <p class="text-muted mb-0">
            <small>
              מופעל ע"י CERAnalyzer + CharacterDiffEngine
            </small>
          </p>
        </div>
        <span class="badge bg-success fs-6">✅ Phase 1 Active</span>
      </div>
    </div>

    <!-- Main Metrics Row -->
    <div class="row mb-4">
      <!-- Advanced CER Card -->
      <div class="col-md-4 mb-3">
        <div class="card metric-card border-primary">
          <div class="card-header bg-primary text-white">
            <i class="fas fa-calculator"></i>
            <strong>Advanced CER</strong>
          </div>
          <div class="card-body text-center">
            <div class="metric-value text-primary">
              {{ metrics.advanced_cer.toFixed(2) }}%
            </div>
            <p class="metric-label">Character Error Rate</p>
            <div class="metric-status" :class="cerStatusClass">
              <i :class="cerStatusIcon"></i>
              {{ cerStatusText }}
            </div>
          </div>
        </div>
      </div>

      <!-- WER Card -->
      <div class="col-md-4 mb-3">
        <div class="card metric-card border-info">
          <div class="card-header bg-info text-white">
            <i class="fas fa-text-width"></i>
            <strong>WER</strong>
          </div>
          <div class="card-body text-center">
            <div class="metric-value text-info">
              {{ metrics.wer.toFixed(2) }}%
            </div>
            <p class="metric-label">Word Error Rate</p>
            <div class="metric-comparison">
              <small class="text-muted">
                {{ werComparison }}
              </small>
            </div>
          </div>
        </div>
      </div>

      <!-- Total Errors Card -->
      <div class="col-md-4 mb-3">
        <div class="card metric-card border-warning">
          <div class="card-header bg-warning text-dark">
            <i class="fas fa-exclamation-triangle"></i>
            <strong>סה"כ שגיאות</strong>
          </div>
          <div class="card-body text-center">
            <div class="metric-value text-warning">
              {{ totalErrors }}
            </div>
            <p class="metric-label">מתוך {{ totalCharacters }} תווים</p>
            <div class="metric-comparison">
              <small class="text-muted">
                {{ correctPercentage }}% נכונים
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Breakdown Section -->
    <div class="row mb-4">
      <div class="col-lg-6 mb-3">
        <div class="card">
          <div class="card-header">
            <i class="fas fa-chart-pie text-primary"></i>
            <strong>פירוט שגיאות</strong>
          </div>
          <div class="card-body">
            <!-- Error Breakdown Chart Component -->
            <error-breakdown-chart 
              v-if="metrics.error_breakdown" 
              :analysis="metrics.error_breakdown" 
            />
            
            <!-- Breakdown Stats -->
            <div class="breakdown-stats mt-3">
              <div class="stat-row">
                <div class="stat-item bg-danger-subtle">
                  <span class="stat-label">החלפות</span>
                  <span class="stat-value">{{ metrics.error_breakdown.substitutions }}</span>
                  <span class="stat-percent">{{ getErrorPercentage('substitutions') }}%</span>
                </div>
              </div>
              <div class="stat-row">
                <div class="stat-item bg-warning-subtle">
                  <span class="stat-label">הוספות</span>
                  <span class="stat-value">{{ metrics.error_breakdown.insertions }}</span>
                  <span class="stat-percent">{{ getErrorPercentage('insertions') }}%</span>
                </div>
              </div>
              <div class="stat-row">
                <div class="stat-item bg-info-subtle">
                  <span class="stat-label">מחיקות</span>
                  <span class="stat-value">{{ metrics.error_breakdown.deletions }}</span>
                  <span class="stat-percent">{{ getErrorPercentage('deletions') }}%</span>
                </div>
              </div>
              <div class="stat-row">
                <div class="stat-item bg-success-subtle">
                  <span class="stat-label">נכונים</span>
                  <span class="stat-value">{{ metrics.error_breakdown.correct }}</span>
                  <span class="stat-percent">{{ getErrorPercentage('correct') }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations Panel -->
      <div class="col-lg-6 mb-3">
        <div class="card h-100">
          <div class="card-header bg-success text-white">
            <i class="fas fa-lightbulb"></i>
            <strong>המלצות לשיפור</strong>
          </div>
          <div class="card-body">
            <div v-if="metrics.recommendations && metrics.recommendations.length > 0">
              <ul class="recommendations-list">
                <li 
                  v-for="(rec, index) in metrics.recommendations" 
                  :key="index"
                  class="recommendation-item"
                >
                  <i class="fas fa-check-circle text-success me-2"></i>
                  <span>{{ rec }}</span>
                </li>
              </ul>
            </div>
            <div v-else class="text-center text-muted py-4">
              <i class="fas fa-thumbs-up fs-1 mb-2"></i>
              <p>אין המלצות נוספות - ההשוואה טובה!</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Advanced Features Row -->
    <div class="row">
      <!-- Tesseract Confidence (if available) -->
      <div 
        v-if="metrics.confidence_analysis" 
        class="col-lg-6 mb-3"
      >
        <div class="card">
          <div class="card-header">
            <i class="fas fa-chart-line text-primary"></i>
            <strong>ניתוח ביטחון Tesseract</strong>
          </div>
          <div class="card-body">
            <!-- Average Confidence -->
            <div class="confidence-metric mb-3">
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-bold">ביטחון ממוצע:</span>
                <span class="fs-5" :class="confidenceClass">
                  {{ (metrics.confidence_analysis.average * 100).toFixed(1) }}%
                </span>
              </div>
              <div class="progress mt-2" style="height: 20px;">
                <div 
                  class="progress-bar" 
                  :class="confidenceBarClass"
                  :style="{ width: (metrics.confidence_analysis.average * 100) + '%' }"
                >
                  {{ (metrics.confidence_analysis.average * 100).toFixed(0) }}%
                </div>
              </div>
            </div>

            <!-- Low Confidence Count -->
            <div class="confidence-metric">
              <div class="d-flex justify-content-between align-items-center">
                <span>תווים עם ביטחון נמוך:</span>
                <span class="badge bg-warning">
                  {{ metrics.confidence_analysis.low_confidence_count }}
                </span>
              </div>
            </div>

            <!-- Per-character breakdown (if available) -->
            <div v-if="metrics.confidence_analysis.per_character" class="mt-3">
              <small class="text-muted">
                <i class="fas fa-info-circle"></i>
                ניתוח תו-תו זמין - ראה בתצוגה מפורטת
              </small>
            </div>
          </div>
        </div>
      </div>

      <!-- Unicode Blocks Analysis (if available) -->
      <div 
        v-if="metrics.unicode_blocks" 
        class="col-lg-6 mb-3"
      >
        <div class="card">
          <div class="card-header">
            <i class="fas fa-globe text-info"></i>
            <strong>ניתוח Unicode Blocks</strong>
          </div>
          <div class="card-body">
            <div class="unicode-blocks-list">
              <div 
                v-for="(count, block) in metrics.unicode_blocks" 
                :key="block"
                class="unicode-block-item mb-2"
              >
                <div class="d-flex justify-content-between align-items-center">
                  <span class="unicode-block-name">
                    <i class="fas fa-font text-muted me-2"></i>
                    {{ formatBlockName(block) }}
                  </span>
                  <span class="badge bg-primary">{{ count }} תווים</span>
                </div>
                <div class="progress mt-1" style="height: 8px;">
                  <div 
                    class="progress-bar bg-info" 
                    :style="{ width: getBlockPercentage(count) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions Footer -->
    <div class="analysis-footer mt-4">
      <div class="d-flex justify-content-between">
        <button 
          class="btn btn-outline-secondary"
          @click="$emit('close')"
        >
          <i class="fas fa-times"></i>
          סגור
        </button>
        <div>
          <button 
            class="btn btn-outline-primary me-2"
            @click="exportAnalysis"
          >
            <i class="fas fa-download"></i>
            ייצוא
          </button>
          <button 
            class="btn btn-primary"
            @click="$emit('view-details')"
          >
            <i class="fas fa-search-plus"></i>
            תצוגה מפורטת
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ErrorBreakdownChart from './ErrorBreakdownChart.vue'

export default {
  name: 'AdvancedAnalysisPanel',
  
  components: {
    ErrorBreakdownChart
  },
  
  props: {
    metrics: {
      type: Object,
      required: true,
      // Structure:
      // {
      //   advanced_cer: number,
      //   wer: number,
      //   error_breakdown: { substitutions, insertions, deletions, correct },
      //   recommendations: string[],
      //   confidence_analysis: { average, low_confidence_count, per_character? },
      //   unicode_blocks: { Hebrew: 100, Arabic: 50, ... }
      // }
    }
  },
  
  computed: {
    totalErrors() {
      const eb = this.metrics.error_breakdown
      return eb.substitutions + eb.insertions + eb.deletions
    },
    
    totalCharacters() {
      const eb = this.metrics.error_breakdown
      return eb.substitutions + eb.insertions + eb.deletions + eb.correct
    },
    
    correctPercentage() {
      if (this.totalCharacters === 0) return 0
      return ((this.metrics.error_breakdown.correct / this.totalCharacters) * 100).toFixed(1)
    },
    
    // CER Status
    cerStatusClass() {
      const cer = this.metrics.advanced_cer
      if (cer < 5) return 'text-success'
      if (cer < 15) return 'text-warning'
      return 'text-danger'
    },
    
    cerStatusIcon() {
      const cer = this.metrics.advanced_cer
      if (cer < 5) return 'fas fa-check-circle'
      if (cer < 15) return 'fas fa-exclamation-circle'
      return 'fas fa-times-circle'
    },
    
    cerStatusText() {
      const cer = this.metrics.advanced_cer
      if (cer < 5) return 'מצוין'
      if (cer < 15) return 'טוב'
      return 'צריך שיפור'
    },
    
    // WER Comparison
    werComparison() {
      const diff = this.metrics.wer - this.metrics.advanced_cer
      if (Math.abs(diff) < 1) return 'דומה ל-CER'
      if (diff > 0) return `גבוה ב-${diff.toFixed(1)}% מ-CER`
      return `נמוך ב-${Math.abs(diff).toFixed(1)}% מ-CER`
    },
    
    // Confidence Class
    confidenceClass() {
      if (!this.metrics.confidence_analysis) return ''
      const avg = this.metrics.confidence_analysis.average
      if (avg >= 0.9) return 'text-success fw-bold'
      if (avg >= 0.7) return 'text-warning fw-bold'
      return 'text-danger fw-bold'
    },
    
    confidenceBarClass() {
      if (!this.metrics.confidence_analysis) return 'bg-secondary'
      const avg = this.metrics.confidence_analysis.average
      if (avg >= 0.9) return 'bg-success'
      if (avg >= 0.7) return 'bg-warning'
      return 'bg-danger'
    },
    
    // Unicode Blocks Total
    totalUnicodeChars() {
      if (!this.metrics.unicode_blocks) return 0
      return Object.values(this.metrics.unicode_blocks).reduce((sum, count) => sum + count, 0)
    }
  },
  
  methods: {
    getErrorPercentage(type) {
      if (this.totalCharacters === 0) return 0
      const value = this.metrics.error_breakdown[type]
      return ((value / this.totalCharacters) * 100).toFixed(1)
    },
    
    formatBlockName(block) {
      // Format Unicode block names nicely
      const names = {
        'Hebrew': 'עברית',
        'Arabic': 'ערבית',
        'Latin': 'לטינית',
        'Common': 'נפוץ',
        'Unknown': 'לא ידוע'
      }
      return names[block] || block
    },
    
    getBlockPercentage(count) {
      if (this.totalUnicodeChars === 0) return 0
      return (count / this.totalUnicodeChars) * 100
    },
    
    exportAnalysis() {
      // Export analysis as JSON
      const dataStr = JSON.stringify(this.metrics, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `advanced_analysis_${new Date().getTime()}.json`
      link.click()
      URL.revokeObjectURL(url)
      
      this.$emit('export', this.metrics)
    }
  }
}
</script>

<style scoped>
.advanced-analysis-panel {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.analysis-header {
  border-bottom: 2px solid #dee2e6;
  padding-bottom: 1rem;
}

.metric-card {
  border-width: 2px;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.metric-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0.5rem 0;
}

.metric-label {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.metric-status,
.metric-comparison {
  font-weight: 600;
}

.breakdown-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-row {
  width: 100%;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 6px;
}

.stat-label {
  font-weight: 600;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
}

.stat-percent {
  color: #6c757d;
  font-size: 0.85rem;
}

.recommendations-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.recommendation-item {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: #f8f9fa;
  border-radius: 6px;
  border-right: 4px solid #198754;
}

.confidence-metric {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.unicode-blocks-list {
  max-height: 300px;
  overflow-y: auto;
}

.unicode-block-item {
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.unicode-block-name {
  font-weight: 500;
}

.analysis-footer {
  border-top: 2px solid #dee2e6;
  padding-top: 1rem;
}

/* RTL adjustments */
[dir="rtl"] .recommendation-item {
  border-right: none;
  border-left: 4px solid #198754;
}
</style>
