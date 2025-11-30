<template>
  <div class="error-breakdown-chart">
    <canvas ref="chartCanvas"></canvas>
    
    <!-- Fallback if no chart library -->
    <div v-if="!chartLoaded" class="simple-breakdown">
      <div class="breakdown-item">
        <div class="breakdown-bar substitutions" :style="{ width: getPercentage('substitutions') }">
          <span class="breakdown-label">
            {{ translate('substitutions') }}: {{ analysis.substitutions }}
          </span>
        </div>
      </div>
      <div class="breakdown-item">
        <div class="breakdown-bar insertions" :style="{ width: getPercentage('insertions') }">
          <span class="breakdown-label">
            {{ translate('insertions') }}: {{ analysis.insertions }}
          </span>
        </div>
      </div>
      <div class="breakdown-item">
        <div class="breakdown-bar deletions" :style="{ width: getPercentage('deletions') }">
          <span class="breakdown-label">
            {{ translate('deletions') }}: {{ analysis.deletions }}
          </span>
        </div>
      </div>
      <div class="breakdown-item">
        <div class="breakdown-bar correct" :style="{ width: getPercentage('correct') }">
          <span class="breakdown-label">
            {{ translate('correct') }}: {{ analysis.correct }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ErrorBreakdownChart',
  
  props: {
    analysis: {
      type: Object,
      required: true,
    },
  },
  
  data() {
    return {
      chartLoaded: false,
    }
  },
  
  computed: {
    total() {
      return this.analysis.substitutions + 
             this.analysis.insertions + 
             this.analysis.deletions + 
             this.analysis.correct
    },
  },
  
  methods: {
    translate(key) {
      return window.COMPARISON_TRANSLATIONS?.[key] || key
    },
    
    getPercentage(type) {
      if (this.total === 0) return '0%'
      const value = this.analysis[type] || 0
      return ((value / this.total) * 100) + '%'
    },
  },
}
</script>

<style scoped>
.error-breakdown-chart {
  width: 100%;
  min-height: 200px;
}

.simple-breakdown {
  width: 100%;
}

.breakdown-item {
  margin-bottom: 1rem;
}

.breakdown-bar {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.5s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.breakdown-bar.substitutions {
  background: linear-gradient(90deg, #ffc107 0%, #ffb300 100%);
}

.breakdown-bar.insertions {
  background: linear-gradient(90deg, #17a2b8 0%, #138496 100%);
}

.breakdown-bar.deletions {
  background: linear-gradient(90deg, #dc3545 0%, #c82333 100%);
}

.breakdown-bar.correct {
  background: linear-gradient(90deg, #28a745 0%, #218838 100%);
}

.breakdown-label {
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
</style>
