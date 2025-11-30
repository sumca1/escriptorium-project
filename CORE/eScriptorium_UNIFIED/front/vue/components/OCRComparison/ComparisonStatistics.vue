<template>
  <div class="comparison-statistics">
    <!-- Loading State -->
    <div v-if="loading" class="text-center p-4">
      <div class="spinner-border text-primary" role="status">
        <span class="sr-only">{{ translate('loading') }}...</span>
      </div>
    </div>

    <!-- Statistics Content -->
    <div v-else-if="statistics" class="statistics-content">
      <!-- Overall Document Statistics -->
      <div class="stats-section">
        <h6 class="section-title">
          <i class="fas fa-chart-line"></i>
          {{ translate('documentStatistics') }}
        </h6>
        
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-file-alt text-primary"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.total_transcriptions }}</div>
              <div class="stat-label">{{ translate('totalTranscriptions') }}</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-robot text-info"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.models.length }}</div>
              <div class="stat-label">{{ translate('modelsUsed') }}</div>
            </div>
          </div>

          <div class="stat-card" v-if="statistics.best_cer">
            <div class="stat-icon">
              <i class="fas fa-trophy text-warning"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.best_cer.toFixed(2) }}%</div>
              <div class="stat-label">{{ translate('bestCER') }}</div>
            </div>
          </div>

          <div class="stat-card" v-if="statistics.average_cer">
            <div class="stat-icon">
              <i class="fas fa-calculator text-secondary"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.average_cer.toFixed(2) }}%</div>
              <div class="stat-label">{{ translate('averageCER') }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Model Performance Comparison -->
      <div class="stats-section" v-if="statistics.model_performance">
        <h6 class="section-title">
          <i class="fas fa-balance-scale"></i>
          {{ translate('modelPerformance') }}
        </h6>
        
        <div class="model-comparison-table">
          <table class="table table-sm table-bordered">
            <thead>
              <tr>
                <th>{{ translate('model') }}</th>
                <th>{{ translate('count') }}</th>
                <th>{{ translate('avgCER') }}</th>
                <th>{{ translate('bestCER') }}</th>
                <th>{{ translate('worstCER') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="model in statistics.model_performance" :key="model.name">
                <td>
                  <span class="model-badge" :class="getModelClass(model.name)">
                    {{ model.name }}
                  </span>
                </td>
                <td>{{ model.count }}</td>
                <td>
                  <span class="cer-badge" :class="getCERQuality(model.avg_cer)">
                    {{ model.avg_cer.toFixed(2) }}%
                  </span>
                </td>
                <td>{{ model.best_cer.toFixed(2) }}%</td>
                <td>{{ model.worst_cer.toFixed(2) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Recommendations -->
      <div class="stats-section" v-if="statistics.recommendations && statistics.recommendations.length > 0">
        <h6 class="section-title">
          <i class="fas fa-lightbulb"></i>
          {{ translate('recommendations') }}
        </h6>
        
        <div class="recommendations-list">
          <div v-for="(rec, index) in statistics.recommendations" 
               :key="index"
               class="recommendation-card"
               :class="rec.priority">
            <div class="rec-icon">
              <i :class="getRecommendationIcon(rec.priority)"></i>
            </div>
            <div class="rec-content">
              <div class="rec-title">{{ rec.title }}</div>
              <div class="rec-description">{{ rec.description }}</div>
              <div v-if="rec.action" class="rec-action">
                <i class="fas fa-arrow-right"></i>
                {{ rec.action }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Trend Analysis -->
      <div class="stats-section" v-if="statistics.trends">
        <h6 class="section-title">
          <i class="fas fa-chart-area"></i>
          {{ translate('trendAnalysis') }}
        </h6>
        
        <div class="trends-container">
          <div class="trend-item" v-if="statistics.trends.improving">
            <i class="fas fa-arrow-up text-success"></i>
            <span>{{ translate('improvingQuality') }}</span>
            <div class="trend-detail">
              {{ statistics.trends.improvement_rate.toFixed(1) }}% {{ translate('betterThanAverage') }}
            </div>
          </div>
          
          <div class="trend-item" v-if="statistics.trends.declining">
            <i class="fas fa-arrow-down text-danger"></i>
            <span>{{ translate('decliningQuality') }}</span>
            <div class="trend-detail">
              {{ statistics.trends.decline_rate.toFixed(1) }}% {{ translate('worseThanAverage') }}
            </div>
          </div>
          
          <div class="trend-item" v-if="statistics.trends.stable">
            <i class="fas fa-minus text-info"></i>
            <span>{{ translate('stableQuality') }}</span>
            <div class="trend-detail">
              {{ translate('consistentPerformance') }}
            </div>
          </div>
        </div>
      </div>

      <!-- Refresh Button -->
      <div class="text-center mt-3">
        <button @click="refreshStatistics" class="btn btn-outline-primary">
          <i class="fas fa-sync-alt"></i>
          {{ translate('refresh') }}
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="alert alert-warning">
      <i class="fas fa-exclamation-triangle"></i>
      {{ translate('noStatistics') }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'ComparisonStatistics',
  
  props: {
    documentId: {
      type: [Number, String],
      required: true,
    },
  },
  
  data() {
    return {
      loading: false,
      statistics: null,
      error: null,
    }
  },
  
  mounted() {
    this.loadStatistics()
  },
  
  methods: {
    translate(key) {
      return window.COMPARISON_TRANSLATIONS?.[key] || key
    },
    
    async loadStatistics() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch(`/cerberus/api/document/${this.documentId}/statistics/`, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
          },
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const data = await response.json()
        this.statistics = data
        this.$emit('statistics-loaded', data)
      } catch (error) {
        console.error('Failed to load statistics:', error)
        this.error = error.message
        this.$emit('error', error)
      } finally {
        this.loading = false
      }
    },
    
    refreshStatistics() {
      this.loadStatistics()
    },
    
    getModelClass(modelName) {
      const name = modelName.toLowerCase()
      if (name.includes('kraken')) return 'model-kraken'
      if (name.includes('tesseract')) return 'model-tesseract'
      if (name.includes('manual')) return 'model-manual'
      return 'model-other'
    },
    
    getCERQuality(cer) {
      if (cer < 5) return 'cer-excellent'
      if (cer < 10) return 'cer-good'
      if (cer < 20) return 'cer-fair'
      return 'cer-poor'
    },
    
    getRecommendationIcon(priority) {
      switch (priority) {
        case 'high': return 'fas fa-exclamation-circle text-danger'
        case 'medium': return 'fas fa-info-circle text-warning'
        case 'low': return 'fas fa-check-circle text-success'
        default: return 'fas fa-lightbulb text-info'
      }
    },
    
    getCookie(name) {
      const value = `; ${document.cookie}`
      const parts = value.split(`; ${name}=`)
      if (parts.length === 2) return parts.pop().split(';').shift()
      return ''
    },
  },
}
</script>

<style scoped>
.comparison-statistics {
  padding: 1rem;
}

.stats-section {
  margin-bottom: 2rem;
}

.section-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #007bff;
}

.section-title i {
  margin-left: 0.5rem;
  color: #007bff;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.stat-icon {
  font-size: 2rem;
  margin-left: 1rem;
}

.stat-content {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
}

.stat-label {
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.model-comparison-table {
  overflow-x: auto;
}

.model-comparison-table table {
  width: 100%;
  background: white;
}

.model-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.model-kraken {
  background: #e3f2fd;
  color: #1976d2;
}

.model-tesseract {
  background: #e8f5e9;
  color: #388e3c;
}

.model-manual {
  background: #fff3e0;
  color: #f57c00;
}

.model-other {
  background: #f5f5f5;
  color: #616161;
}

.cer-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.cer-excellent {
  background: #c8e6c9;
  color: #2e7d32;
}

.cer-good {
  background: #fff9c4;
  color: #f9a825;
}

.cer-fair {
  background: #ffe0b2;
  color: #e65100;
}

.cer-poor {
  background: #ffcdd2;
  color: #c62828;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recommendation-card {
  display: flex;
  align-items: start;
  padding: 1rem;
  background: white;
  border-right: 4px solid #007bff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.recommendation-card.high {
  border-right-color: #dc3545;
  background: #fff5f5;
}

.recommendation-card.medium {
  border-right-color: #ffc107;
  background: #fffef5;
}

.recommendation-card.low {
  border-right-color: #28a745;
  background: #f5fff5;
}

.rec-icon {
  font-size: 1.5rem;
  margin-left: 1rem;
}

.rec-content {
  flex: 1;
}

.rec-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.rec-description {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.rec-action {
  color: #007bff;
  font-size: 0.85rem;
  font-weight: 500;
}

.rec-action i {
  margin-left: 0.5rem;
}

.trends-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.trend-item {
  padding: 1rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.trend-item i {
  font-size: 1.5rem;
}

.trend-detail {
  margin-right: auto;
  color: #6c757d;
  font-size: 0.9rem;
}

/* RTL Support */
[dir="rtl"] .stat-icon {
  margin-left: 0;
  margin-right: 1rem;
}

[dir="rtl"] .rec-icon {
  margin-left: 0;
  margin-right: 1rem;
}

[dir="rtl"] .rec-action i {
  margin-left: 0;
  margin-right: 0.5rem;
}

[dir="rtl"] .recommendation-card {
  border-right: none;
  border-left: 4px solid #007bff;
}

[dir="rtl"] .recommendation-card.high {
  border-left-color: #dc3545;
}

[dir="rtl"] .recommendation-card.medium {
  border-left-color: #ffc107;
}

[dir="rtl"] .recommendation-card.low {
  border-left-color: #28a745;
}
</style>
