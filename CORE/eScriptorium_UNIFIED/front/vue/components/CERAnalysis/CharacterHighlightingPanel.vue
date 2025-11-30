<template>
  <div class="character-highlighting-panel">
    <!-- Header -->
    <div class="panel-header">
      <h3>{{ translate('cerberus.characterHighlighting.title') || 'Character Highlighting' }}</h3>
      <button @click="closePanel" class="btn-close">✕</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ translate('cerberus.analyzing') || 'Analyzing...' }}</p>
    </div>

    <!-- Main Content -->
    <div v-else class="highlighting-content">
      <!-- Summary Stats -->
      <div class="summary-stats">
        <div class="stat">
          <span class="label">{{ translate('cerberus.characterHighlighting.accuracy') || 'Accuracy' }}:</span>
          <span :class="['value', getAccuracyClass(summary.accuracy)]">
            {{ summary.accuracy.toFixed(2) }}%
          </span>
        </div>
        <div class="stat">
          <span class="label">{{ translate('cerberus.characterErrorRate') || 'CER' }}:</span>
          <span :class="['value', getCERClass(summary.error_rate)]">
            {{ summary.error_rate.toFixed(2) }}%
          </span>
        </div>
        <div class="stat">
          <span class="label">{{ translate('cerberus.characterHighlighting.correct') || 'Correct' }}:</span>
          <span class="value">{{ summary.correct }}/{{ summary.total_characters }}</span>
        </div>
      </div>

      <!-- Error breakdown -->
      <div class="error-breakdown">
        <div v-if="summary.substitutions > 0" class="error-type substitution">
          <span class="icon">🔄</span>
          <span class="label">{{ translate('cerberus.characterHighlighting.substitutions') || 'Substitutions' }}:</span>
          <span class="count">{{ summary.substitutions }}</span>
        </div>
        <div v-if="summary.insertions > 0" class="error-type insertion">
          <span class="icon">➕</span>
          <span class="label">{{ translate('cerberus.characterHighlighting.insertions') || 'Insertions' }}:</span>
          <span class="count">{{ summary.insertions }}</span>
        </div>
        <div v-if="summary.deletions > 0" class="error-type deletion">
          <span class="icon">➖</span>
          <span class="label">{{ translate('cerberus.characterHighlighting.deletions') || 'Deletions' }}:</span>
          <span class="count">{{ summary.deletions }}</span>
        </div>
      </div>

      <!-- Side-by-side comparison -->
      <div class="comparison-container">
        <!-- Ground Truth (Left) -->
        <div class="comparison-column ground-truth">
          <h4>{{ translate('cerberus.groundTruth') || 'Ground Truth' }}</h4>
          <div class="text-display" v-html="groundTruthHtml"></div>
        </div>

        <!-- Arrow indicator -->
        <div class="arrow">
          <span>VS</span>
        </div>

        <!-- Hypothesis (Right) -->
        <div class="comparison-column hypothesis">
          <h4>{{ translate('cerberus.hypothesis') || 'Hypothesis' }}</h4>
          <div class="text-display" v-html="hypothesisHtml"></div>
        </div>
      </div>

      <!-- Legend -->
      <div class="legend">
        <h5>{{ translate('cerberus.characterHighlighting.legend') || 'Legend' }}</h5>
        <div class="legend-items">
          <div class="legend-item">
            <span class="color-box correct"></span>
            <span>{{ translate('cerberus.characterHighlighting.correct') || 'Correct' }}</span>
          </div>
          <div class="legend-item">
            <span class="color-box substitution"></span>
            <span>{{ translate('cerberus.characterHighlighting.substitution') || 'Substitution' }}</span>
          </div>
          <div class="legend-item">
            <span class="color-box insertion"></span>
            <span>{{ translate('cerberus.characterHighlighting.insertion') || 'Insertion' }}</span>
          </div>
          <div class="legend-item">
            <span class="color-box deletion"></span>
            <span>{{ translate('cerberus.characterHighlighting.deletion') || 'Deletion' }}</span>
          </div>
        </div>
      </div>

      <!-- Detailed Diff List -->
      <div class="detailed-diffs">
        <h5>{{ translate('cerberus.characterHighlighting.detailedDifferences') || 'Detailed Differences' }}</h5>
        <table v-if="diffs.filter(d => d.diff_type !== 'correct').length > 0" class="diffs-table">
          <thead>
            <tr>
              <th>{{ translate('cerberus.characterHighlighting.position') || 'Position' }}</th>
              <th>{{ translate('cerberus.characterHighlighting.type') || 'Type' }}</th>
              <th>{{ translate('cerberus.characterHighlighting.expected') || 'Expected' }}</th>
              <th>{{ translate('cerberus.characterHighlighting.got') || 'Got' }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="diff in diffs.filter(d => d.diff_type !== 'correct')" :key="`${diff.position}-${diff.diff_type}`">
              <td>{{ diff.position }}</td>
              <td :class="['type-badge', diff.diff_type]">{{ diff.diff_type }}</td>
              <td class="char-cell">
                <span v-if="diff.expected" class="char">{{ diff.expected }}</span>
                <span v-else class="char-null">-</span>
              </td>
              <td class="char-cell">
                <span v-if="diff.character" class="char">{{ diff.character }}</span>
                <span v-else class="char-null">-</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="no-diffs">
          ✅ {{ translate('cerberus.characterHighlighting.noDifferences') || 'No differences found' }}
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      ❌ {{ errorMessage }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'CharacterHighlightingPanel',
  props: {
    groundTruthTranscriptionId: {
      type: Number,
      required: true
    },
    hypothesisTranscriptionId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      errorMessage: '',
      summary: {
        correct: 0,
        substitutions: 0,
        insertions: 0,
        deletions: 0,
        total_characters: 0,
        accuracy: 0,
        error_rate: 0
      },
      diffs: [],
      groundTruthHtml: '',
      hypothesisHtml: ''
    }
  },
  computed: {
    apiBaseUrl() {
      return window.API_BASE_URL || '/api'
    }
  },
  mounted() {
    this.loadDiff()
  },
  methods: {
    async loadDiff() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        const response = await fetch(
          `${this.apiBaseUrl}/cerberus/analyses/character-diff/`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
              ground_truth_transcription_id: this.groundTruthTranscriptionId,
              hypothesis_transcription_id: this.hypothesisTranscriptionId,
              ignore_case: false
            })
          }
        )
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const data = await response.json()
        this.summary = data.summary
        this.diffs = data.diffs
        this.groundTruthHtml = data.visualization.ground_truth_html
        this.hypothesisHtml = data.visualization.hypothesis_html
      } catch (error) {
        console.error('Diff error:', error)
        this.errorMessage = error.message || 'Failed to load diff data'
      } finally {
        this.loading = false
      }
    },
    
    getCsrfToken() {
      const name = 'csrftoken'
      let cookieValue = null
      
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let cookie of cookies) {
          cookie = cookie.trim()
          if (cookie.substring(0, name.length + 1) === name + '=') {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
          }
        }
      }
      
      return cookieValue || ''
    },
    
    getAccuracyClass(accuracy) {
      if (accuracy >= 95) return 'excellent'
      if (accuracy >= 90) return 'good'
      if (accuracy >= 80) return 'fair'
      return 'poor'
    },
    
    getCERClass(cer) {
      if (cer <= 5) return 'excellent'
      if (cer <= 10) return 'good'
      if (cer <= 20) return 'fair'
      return 'poor'
    },
    
    closePanel() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.character-highlighting-panel {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-height: 90vh;
  overflow-y: auto;
  direction: rtl;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #ecf0f1;
}

.panel-header h3 {
  margin: 0;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
}

.loading-state {
  text-align: center;
  padding: 2rem;
}

.spinner {
  display: inline-block;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat {
  background: #f5f7fa;
  padding: 1rem;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat .label {
  color: #7f8c8d;
  font-weight: 600;
}

.stat .value {
  font-size: 1.3rem;
  font-weight: bold;
  margin-right: 0.5rem;
}

.stat .value.excellent {
  color: #27ae60;
}

.stat .value.good {
  color: #2980b9;
}

.stat .value.fair {
  color: #f39c12;
}

.stat .value.poor {
  color: #e74c3c;
}

.error-breakdown {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.error-type {
  padding: 0.75rem;
  border-radius: 4px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-type.substitution {
  background: rgba(230, 126, 34, 0.1);
  color: #e67e22;
}

.error-type.insertion {
  background: rgba(155, 89, 182, 0.1);
  color: #9b59b6;
}

.error-type.deletion {
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
}

.comparison-container {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: start;
}

.comparison-column {
  background: #f5f7fa;
  padding: 1rem;
  border-radius: 6px;
  border: 2px solid #ecf0f1;
}

.comparison-column h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 0.95rem;
  text-transform: uppercase;
}

.text-display {
  font-family: 'Courier New', monospace;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.95rem;
  color: #2c3e50;
  max-height: 300px;
  overflow-y: auto;
}

.arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 1rem;
  color: #7f8c8d;
  font-weight: bold;
}

/* Character highlighting colors */
.text-display :deep(.diff-correct) {
  background-color: transparent;
  color: #27ae60;
}

.text-display :deep(.diff-substitution) {
  background-color: #ffeaa7;
  color: #e67e22;
  font-weight: bold;
  padding: 0 2px;
  border-radius: 2px;
}

.text-display :deep(.diff-insertion) {
  background-color: #a29bfe;
  color: #6c5ce7;
  font-weight: bold;
  padding: 0 2px;
  border-radius: 2px;
}

.text-display :deep(.diff-deletion) {
  background-color: #fab1a0;
  color: #d63031;
  font-weight: bold;
  padding: 0 2px;
  border-radius: 2px;
  text-decoration: line-through;
}

.legend {
  background: #ecf0f1;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.legend h5 {
  margin-top: 0;
  margin-bottom: 0.75rem;
  color: #2c3e50;
}

.legend-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #2c3e50;
}

.color-box {
  width: 24px;
  height: 24px;
  border-radius: 3px;
}

.color-box.correct {
  background-color: #27ae60;
}

.color-box.substitution {
  background-color: #ffeaa7;
}

.color-box.insertion {
  background-color: #a29bfe;
}

.color-box.deletion {
  background-color: #fab1a0;
}

.detailed-diffs {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #ecf0f1;
}

.detailed-diffs h5 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.diffs-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.diffs-table thead {
  background-color: #ecf0f1;
}

.diffs-table th {
  padding: 0.75rem;
  text-align: right;
  font-weight: 600;
  color: #2c3e50;
}

.diffs-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #ecf0f1;
  text-align: right;
}

.diffs-table tbody tr:hover {
  background-color: #f5f7fa;
}

.type-badge {
  padding: 0.3rem 0.6rem;
  border-radius: 3px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.type-badge.substitution {
  background-color: #ffeaa7;
  color: #e67e22;
}

.type-badge.insertion {
  background-color: #a29bfe;
  color: #6c5ce7;
}

.type-badge.deletion {
  background-color: #fab1a0;
  color: #d63031;
}

.char {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  padding: 0.2rem 0.4rem;
  background: #ecf0f1;
  border-radius: 2px;
}

.char-null {
  color: #95a5a6;
  font-style: italic;
}

.no-diffs {
  text-align: center;
  padding: 1rem;
  color: #27ae60;
  font-weight: 600;
}

.error-message {
  background: #fadbd8;
  border: 1px solid #f5b7b1;
  color: #c0392b;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

@media (max-width: 1024px) {
  .comparison-container {
    grid-template-columns: 1fr;
  }
  
  .arrow {
    display: none;
  }
}

@media (max-width: 768px) {
  .character-highlighting-panel {
    padding: 1rem;
  }
  
  .summary-stats {
    grid-template-columns: 1fr;
  }
  
  .legend-items {
    grid-template-columns: 1fr;
  }
}
</style>
