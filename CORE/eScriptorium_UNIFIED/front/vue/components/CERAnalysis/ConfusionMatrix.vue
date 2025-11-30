<template>
  <div class="confusion-matrix">
    <!-- Header -->
    <div class="matrix-header mb-3">
      <h5>
        <i class="fas fa-exchange-alt"></i>
        {{ translate('cer.topConfusions') }}
      </h5>
      <p class="text-muted small">
        {{ translate('cer.confusionDescription') }}
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ translate('cer.loading') }}</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="fas fa-exclamation-circle"></i>
      {{ error }}
    </div>

    <!-- Confusions Table -->
    <div v-else-if="confusionList.length > 0" class="table-responsive">
      <table class="table table-sm table-striped confusion-table">
        <thead class="table-light">
          <tr>
            <th class="text-center">#</th>
            <th>{{ translate('cer.correctChar') }}</th>
            <th class="text-center">
              <i class="fas fa-arrow-right"></i>
            </th>
            <th>{{ translate('cer.wrongChar') }}</th>
            <th class="text-center">{{ translate('cer.count') }}</th>
            <th>{{ translate('cer.percentage') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="(confusion, index) in confusionList" 
            :key="`${confusion.correct}-${confusion.wrong}`"
            :class="confusionClass(index)"
          >
            <td class="text-center text-muted">
              {{ index + 1 }}
            </td>
            <td class="char-cell">
              <span class="char-badge correct">{{ confusion.correct }}</span>
              <small class="text-muted ms-2">
                U+{{ confusion.correct.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0') }}
              </small>
            </td>
            <td class="text-center">
              <i class="fas fa-long-arrow-alt-right text-danger"></i>
            </td>
            <td class="char-cell">
              <span class="char-badge wrong">{{ confusion.wrong }}</span>
              <small class="text-muted ms-2">
                U+{{ confusion.wrong.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0') }}
              </small>
            </td>
            <td class="text-center">
              <span class="badge bg-secondary">{{ confusion.count }}</span>
            </td>
            <td>
              <div class="progress-wrapper">
                <div class="progress">
                  <div 
                    class="progress-bar bg-danger" 
                    :style="{ width: (confusion.percentage || 0) + '%' }"
                    role="progressbar"
                  >
                    {{ (confusion.percentage || 0).toFixed(1) }}%
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center text-muted py-5">
      <i class="fas fa-check-circle fa-3x mb-3"></i>
      <p>{{ translate('cer.noConfusions') }}</p>
    </div>

    <!-- Load More Button -->
    <div v-if="hasMore && !loading" class="text-center mt-3">
      <button @click="loadMore" class="btn btn-outline-primary btn-sm">
        <i class="fas fa-plus-circle"></i>
        {{ translate('cer.loadMore') }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfusionMatrix',

  props: {
    confusions: {
      type: Array,
      required: true,
      default: () => []
    },
    analysisId: {
      type: Number,
      required: false
    }
  },

  data() {
    return {
      loading: false,
      error: null,
      additionalConfusions: [],
      hasMore: false
    }
  },

  computed: {
    confusionList() {
      // Combine prop confusions with any additional loaded confusions
      const combined = [...this.confusions, ...this.additionalConfusions]
      
      // Ensure each confusion has a percentage
      return combined.map(c => ({
        ...c,
        percentage: c.percentage || (c.count / this.totalConfusions * 100)
      }))
    },

    totalConfusions() {
      return this.confusionList.reduce((sum, c) => sum + c.count, 0)
    }
  },

  methods: {
    async loadMore() {
      if (!this.analysisId) {
        console.warn('Cannot load more confusions without analysisId')
        return
      }

      this.loading = true
      this.error = null

      try {
        const response = await fetch(`/api/cerberus/analyses/${this.analysisId}/confusion_matrix/`)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()
        
        // Add new confusions that aren't already in the list
        const existingKeys = new Set(
          this.confusionList.map(c => `${c.correct}-${c.wrong}`)
        )
        
        const newConfusions = data.filter(c => 
          !existingKeys.has(`${c.correct}-${c.wrong}`)
        )
        
        this.additionalConfusions.push(...newConfusions)
        this.hasMore = false // Could implement pagination here

      } catch (err) {
        console.error('Error loading confusion matrix:', err)
        this.error = this.translate('cer.errorLoadingConfusions')
      } finally {
        this.loading = false
      }
    },

    confusionClass(index) {
      if (index < 3) return 'top-confusion'
      if (index < 10) return 'high-confusion'
      return ''
    }
  }
}
</script>

<style scoped>
.confusion-matrix {
  padding: 1rem;
}

.matrix-header h5 {
  margin-bottom: 0.5rem;
  color: #495057;
}

.confusion-table {
  font-size: 0.95rem;
}

.confusion-table thead th {
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

.char-cell {
  font-size: 1.1rem;
}

.char-badge {
  display: inline-block;
  min-width: 2.5rem;
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.char-badge.correct {
  background: #d1ecf1;
  color: #0c5460;
  border: 2px solid #bee5eb;
}

.char-badge.wrong {
  background: #f8d7da;
  color: #721c24;
  border: 2px solid #f5c6cb;
}

.progress-wrapper {
  min-width: 120px;
}

.progress {
  height: 22px;
  font-size: 0.8rem;
  font-weight: 600;
}

.top-confusion {
  background-color: #fff3cd !important;
}

.top-confusion:hover {
  background-color: #ffe69c !important;
}

.high-confusion {
  background-color: #f8f9fa !important;
}

.high-confusion:hover {
  background-color: #e9ecef !important;
}
</style>
