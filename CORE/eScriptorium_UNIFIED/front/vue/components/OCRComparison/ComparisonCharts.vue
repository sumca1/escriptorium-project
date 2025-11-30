<template>
  <div class="comparison-charts">
    <!-- Bar Chart: CER Comparison -->
    <div class="chart-container mb-4">
      <h6 class="chart-title">
        <i class="fas fa-chart-bar"></i>
        {{ translate('cerComparison') }}
      </h6>
      <div class="bar-chart">
        <div class="bar-group">
          <div class="bar-label">{{ trans1.name }}</div>
          <div class="bar-wrapper">
            <div 
              class="bar bar-1" 
              :style="{ width: getBarWidth(metrics.cer_1, 'cer') }"
              :class="getCerBarClass(metrics.cer_1)"
            >
              <span class="bar-value">{{ metrics.cer_1.toFixed(2) }}%</span>
            </div>
          </div>
        </div>
        <div class="bar-group">
          <div class="bar-label">{{ trans2.name }}</div>
          <div class="bar-wrapper">
            <div 
              class="bar bar-2" 
              :style="{ width: getBarWidth(metrics.cer_2, 'cer') }"
              :class="getCerBarClass(metrics.cer_2)"
            >
              <span class="bar-value">{{ metrics.cer_2.toFixed(2) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bar Chart: Accuracy Comparison -->
    <div class="chart-container mb-4">
      <h6 class="chart-title">
        <i class="fas fa-chart-line"></i>
        {{ translate('accuracyComparison') }}
      </h6>
      <div class="bar-chart">
        <div class="bar-group">
          <div class="bar-label">{{ trans1.name }}</div>
          <div class="bar-wrapper">
            <div 
              class="bar bar-1" 
              :style="{ width: metrics.accuracy_1 + '%' }"
              :class="getAccuracyBarClass(metrics.accuracy_1)"
            >
              <span class="bar-value">{{ metrics.accuracy_1.toFixed(2) }}%</span>
            </div>
          </div>
        </div>
        <div class="bar-group">
          <div class="bar-label">{{ trans2.name }}</div>
          <div class="bar-wrapper">
            <div 
              class="bar bar-2" 
              :style="{ width: metrics.accuracy_2 + '%' }"
              :class="getAccuracyBarClass(metrics.accuracy_2)"
            >
              <span class="bar-value">{{ metrics.accuracy_2.toFixed(2) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Difference Indicator -->
    <div class="difference-card">
      <div class="row text-center">
        <div class="col-md-6">
          <div class="diff-stat">
            <div class="diff-label">{{ translate('cerDifference') }}</div>
            <div class="diff-value" :class="getDiffClass()">
              {{ metrics.cer_difference.toFixed(2) }}%
            </div>
            <div class="diff-description">
              {{ getDiffDescription() }}
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="diff-stat">
            <div class="diff-label">{{ translate('winner') }}</div>
            <div class="diff-value text-success">
              <i class="fas fa-trophy"></i>
              {{ getWinnerName() }}
            </div>
            <div class="diff-description">
              {{ translate('betterAccuracy') }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ComparisonCharts',
  
  props: {
    metrics: {
      type: Object,
      required: true,
    },
    trans1: {
      type: Object,
      required: true,
    },
    trans2: {
      type: Object,
      required: true,
    },
  },
  
  methods: {
    translate(key) {
      return window.COMPARISON_TRANSLATIONS?.[key] || key
    },
    
    getBarWidth(value, type) {
      if (type === 'cer') {
        // CER: normalize to 0-100 scale, cap at 50 for visualization
        const normalized = Math.min(value, 50)
        return (normalized / 50 * 100) + '%'
      }
      return value + '%'
    },
    
    getCerBarClass(cer) {
      if (cer < 5) return 'bg-success'
      if (cer < 15) return 'bg-warning'
      return 'bg-danger'
    },
    
    getAccuracyBarClass(accuracy) {
      if (accuracy >= 95) return 'bg-success'
      if (accuracy >= 85) return 'bg-warning'
      return 'bg-danger'
    },
    
    getDiffClass() {
      const diff = this.metrics.cer_difference
      if (diff < 2) return 'text-success'
      if (diff < 5) return 'text-warning'
      return 'text-danger'
    },
    
    getDiffDescription() {
      const diff = this.metrics.cer_difference
      if (diff < 2) return this.translate('veryClose')
      if (diff < 5) return this.translate('noticeable')
      return this.translate('significant')
    },
    
    getWinnerName() {
      return this.metrics.winner === 'transcription_1' 
        ? this.trans1.name 
        : this.trans2.name
    },
  },
}
</script>

<style scoped>
.comparison-charts {
  width: 100%;
}

.chart-container {
  padding: 1.5rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
}

.chart-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #007bff;
}

.bar-chart {
  width: 100%;
}

.bar-group {
  margin-bottom: 1.5rem;
}

.bar-label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.bar-wrapper {
  background: #f8f9fa;
  border-radius: 8px;
  height: 40px;
  position: relative;
  overflow: hidden;
}

.bar {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-left: 1rem;
  border-radius: 8px;
  transition: width 0.8s ease;
  position: relative;
}

.bar-value {
  color: white;
  font-weight: bold;
  font-size: 0.9rem;
  padding-left: 0.75rem;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.difference-card {
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.diff-stat {
  padding: 1rem;
}

.diff-label {
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.diff-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.diff-description {
  font-size: 0.95rem;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .bar-label {
    font-size: 0.85rem;
  }
  
  .bar-wrapper {
    height: 35px;
  }
  
  .bar-value {
    font-size: 0.8rem;
  }
  
  .diff-value {
    font-size: 2rem;
  }
}
</style>
