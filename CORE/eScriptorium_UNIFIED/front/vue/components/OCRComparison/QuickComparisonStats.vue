<template>
  <div class="quick-stats">
    <div v-if="result.metrics" class="stats-content">
      <!-- Winner Badge -->
      <div class="winner-badge text-center mb-3">
        <i class="fas fa-trophy fa-2x text-warning mb-2"></i>
        <div class="winner-name">
          {{ getWinnerName() }}
        </div>
        <div class="winner-details">
          <small>
            {{ translate('betterBy') }}
            <strong>{{ result.metrics.cer_difference.toFixed(2) }}%</strong>
            CER
          </small>
        </div>
      </div>

      <!-- Quick Metrics -->
      <div class="quick-metrics">
        <div class="metric-row">
          <span class="metric-label">{{ translate('bestCER') }}:</span>
          <span class="metric-value text-success">
            {{ getBestCER().toFixed(2) }}%
          </span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ translate('bestAccuracy') }}:</span>
          <span class="metric-value text-success">
            {{ getBestAccuracy().toFixed(2) }}%
          </span>
        </div>
        <div class="metric-row" v-if="result.ground_truth">
          <span class="metric-label">{{ translate('vsGroundTruth') }}:</span>
          <span class="metric-value">
            {{ result.ground_truth.name }}
          </span>
        </div>
      </div>
    </div>

    <!-- No ground truth -->
    <div v-else class="text-center text-muted py-3">
      <i class="fas fa-info-circle"></i>
      <div class="mt-2">
        <small>{{ translate('selectGroundTruthForMetrics') }}</small>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuickComparisonStats',
  
  props: {
    result: {
      type: Object,
      required: true,
    },
  },
  
  methods: {
    translate(key) {
      return window.COMPARISON_TRANSLATIONS?.[key] || key
    },
    
    getWinnerName() {
      if (!this.result.metrics) return ''
      return this.result.metrics.winner === 'transcription_1'
        ? this.result.transcription_1.name
        : this.result.transcription_2.name
    },
    
    getBestCER() {
      if (!this.result.metrics) return 0
      return Math.min(this.result.metrics.cer_1, this.result.metrics.cer_2)
    },
    
    getBestAccuracy() {
      if (!this.result.metrics) return 0
      return Math.max(this.result.metrics.accuracy_1, this.result.metrics.accuracy_2)
    },
  },
}
</script>

<style scoped>
.quick-stats {
  padding: 0.5rem;
}

.winner-badge {
  padding: 1rem;
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  border-radius: 8px;
  color: #2c3e50;
}

.winner-name {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.winner-details {
  color: #495057;
}

.quick-metrics {
  padding: 0.5rem 0;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-row:last-child {
  border-bottom: none;
}

.metric-label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.9rem;
}

.metric-value {
  font-weight: bold;
  font-size: 1rem;
}
</style>
