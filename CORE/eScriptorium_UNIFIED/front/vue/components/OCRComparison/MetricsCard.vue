<template>
  <div class="metrics-card" :class="{ 'winner-card': isWinner }">
    <div class="card-header">
      <h6 class="mb-0">
        <span class="badge" :class="'bg-' + badgeColor">{{ badge }}</span>
        {{ title }}
        <span v-if="isWinner" class="trophy-badge">
          <i class="fas fa-trophy text-warning"></i>
          {{ translate('winner') }}
        </span>
      </h6>
    </div>
    <div class="card-body">
      <!-- Model Info -->
      <div class="model-info mb-3">
        <small class="text-muted">
          <i class="fas fa-robot"></i>
          <strong>{{ translate('model') }}:</strong> {{ metrics.model || 'N/A' }}
        </small>
      </div>

      <!-- Metrics -->
      <div v-if="metrics.cer !== undefined" class="metrics-grid">
        <!-- CER -->
        <div class="metric-item">
          <div class="metric-label">
            <i class="fas fa-percent"></i>
            {{ translate('cer') }}
          </div>
          <div class="metric-value" :class="getCerClass(metrics.cer)">
            {{ metrics.cer.toFixed(2) }}%
          </div>
          <div class="metric-quality">
            {{ getCerQuality(metrics.cer) }}
          </div>
        </div>

        <!-- Accuracy -->
        <div class="metric-item">
          <div class="metric-label">
            <i class="fas fa-check-circle"></i>
            {{ translate('accuracy') }}
          </div>
          <div class="metric-value" :class="getAccuracyClass(metrics.accuracy)">
            {{ metrics.accuracy.toFixed(2) }}%
          </div>
          <div class="progress mt-2" style="height: 8px;">
            <div 
              class="progress-bar" 
              :class="getAccuracyClass(metrics.accuracy)"
              :style="{ width: metrics.accuracy + '%' }"
            ></div>
          </div>
        </div>

        <!-- WER -->
        <div class="metric-item" v-if="metrics.wer !== undefined">
          <div class="metric-label">
            <i class="fas fa-spell-check"></i>
            {{ translate('wer') }}
          </div>
          <div class="metric-value">
            {{ metrics.wer.toFixed(2) }}%
          </div>
        </div>

        <!-- Text Length -->
        <div class="metric-item">
          <div class="metric-label">
            <i class="fas fa-text-width"></i>
            {{ translate('textLength') }}
          </div>
          <div class="metric-value text-muted">
            {{ metrics.length.toLocaleString() }}
          </div>
          <small class="text-muted">{{ translate('chars') }}</small>
        </div>
      </div>

      <!-- No metrics available -->
      <div v-else class="text-center text-muted py-3">
        <i class="fas fa-info-circle"></i>
        {{ translate('noGroundTruth') }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MetricsCard',
  
  props: {
    title: {
      type: String,
      required: true,
    },
    metrics: {
      type: Object,
      required: true,
    },
    badge: {
      type: String,
      required: true,
    },
    badgeColor: {
      type: String,
      default: 'primary',
    },
    isWinner: {
      type: Boolean,
      default: false,
    },
  },
  
  methods: {
    translate(key) {
      return window.COMPARISON_TRANSLATIONS?.[key] || key
    },
    
    getCerClass(cer) {
      if (cer < 5) return 'text-success'
      if (cer < 15) return 'text-warning'
      return 'text-danger'
    },
    
    getCerQuality(cer) {
      if (cer < 5) return '🟢 ' + this.translate('excellent')
      if (cer < 15) return '🟡 ' + this.translate('good')
      return '🔴 ' + this.translate('needsWork')
    },
    
    getAccuracyClass(accuracy) {
      if (accuracy >= 95) return 'bg-success'
      if (accuracy >= 85) return 'bg-warning'
      return 'bg-danger'
    },
  },
}
</script>

<style scoped>
.metrics-card {
  border: 2px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  transition: all 0.3s;
  height: 100%;
}

.metrics-card.winner-card {
  border-color: #ffc107;
  box-shadow: 0 0 20px rgba(255, 193, 7, 0.3);
}

.metrics-card .card-header {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  padding: 1rem;
}

.trophy-badge {
  float: left;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.model-info {
  padding: 0.75rem;
  background: #f0f8ff;
  border-radius: 6px;
  border-right: 3px solid #007bff;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.metric-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  transition: all 0.3s;
}

.metric-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.metric-label {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.metric-quality {
  font-size: 0.9rem;
  font-weight: 600;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .metric-value {
    font-size: 1.5rem;
  }
}
</style>
