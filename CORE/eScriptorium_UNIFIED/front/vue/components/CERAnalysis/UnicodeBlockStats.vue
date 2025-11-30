<template>
  <div class="unicode-block-stats">
    <!-- Header -->
    <div class="blocks-header mb-3">
      <h5>
        <i class="fas fa-layer-group"></i>
        {{ translate('cer.unicodeBlocks') }}
      </h5>
      <p class="text-muted small">
        {{ translate('cer.unicodeBlocksDescription') }}
      </p>
    </div>

    <!-- Blocks Grid -->
    <div v-if="blocks && blocks.length > 0" class="row g-3">
      <div 
        v-for="block in sortedBlocks" 
        :key="block.block"
        class="col-md-6 col-lg-4"
      >
        <div class="card block-card">
          <div class="card-body">
            <!-- Block Name -->
            <h6 class="card-title">
              <i :class="blockIcon(block.block)" class="me-2"></i>
              {{ blockDisplayName(block.block) }}
            </h6>

            <!-- Stats -->
            <div class="block-stats mb-3">
              <div class="stat-row">
                <span class="stat-label">{{ translate('cer.totalCharacters') }}:</span>
                <span class="stat-value">{{ block.total_chars }}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">{{ translate('cer.correct') }}:</span>
                <span class="stat-value text-success">{{ block.correct_chars }}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">{{ translate('cer.incorrect') }}:</span>
                <span class="stat-value text-danger">{{ block.total_chars - block.correct_chars }}</span>
              </div>
            </div>

            <!-- Accuracy Bar -->
            <div class="accuracy-display">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <small class="text-muted">{{ translate('cer.accuracy') }}</small>
                <strong :class="accuracyClass(block.accuracy)">
                  {{ (block.accuracy * 100).toFixed(1) }}%
                </strong>
              </div>
              <div class="progress">
                <div 
                  class="progress-bar" 
                  :class="accuracyProgressClass(block.accuracy)"
                  :style="{ width: (block.accuracy * 100) + '%' }"
                  role="progressbar"
                >
                </div>
              </div>
            </div>

            <!-- Character Range -->
            <div class="char-range mt-2">
              <small class="text-muted">
                <i class="fas fa-info-circle"></i>
                {{ translate('cer.range') }}: {{ block.range_start }} - {{ block.range_end }}
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center text-muted py-5">
      <i class="fas fa-inbox fa-3x mb-3"></i>
      <p>{{ translate('cer.noUnicodeBlocks') }}</p>
    </div>

    <!-- Summary -->
    <div v-if="blocks && blocks.length > 0" class="blocks-summary mt-4">
      <div class="card">
        <div class="card-body">
          <h6 class="card-title">
            <i class="fas fa-chart-bar"></i>
            {{ translate('cer.summary') }}
          </h6>
          <div class="row g-3">
            <div class="col-md-4">
              <div class="summary-item">
                <div class="summary-label">{{ translate('cer.totalBlocks') }}</div>
                <div class="summary-value">{{ blocks.length }}</div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="summary-item">
                <div class="summary-label">{{ translate('cer.totalCharacters') }}</div>
                <div class="summary-value">{{ totalChars }}</div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="summary-item">
                <div class="summary-label">{{ translate('cer.overallAccuracy') }}</div>
                <div class="summary-value" :class="accuracyClass(overallAccuracy)">
                  {{ (overallAccuracy * 100).toFixed(1) }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UnicodeBlockStats',

  props: {
    blocks: {
      type: Array,
      required: true,
      default: () => []
    }
  },

  computed: {
    sortedBlocks() {
      // Sort by total characters (most used first)
      return [...this.blocks].sort((a, b) => b.total_chars - a.total_chars)
    },

    totalChars() {
      return this.blocks.reduce((sum, b) => sum + b.total_chars, 0)
    },

    overallAccuracy() {
      const totalCorrect = this.blocks.reduce((sum, b) => sum + b.correct_chars, 0)
      return this.totalChars > 0 ? totalCorrect / this.totalChars : 0
    }
  },

  methods: {
    blockDisplayName(blockName) {
      const names = {
        'Hebrew': 'עברית',
        'Arabic': 'ערבית',
        'Latin': 'לטינית',
        'Basic Latin': 'לטינית בסיסית',
        'Latin-1 Supplement': 'לטינית מורחבת',
        'Greek': 'יוונית',
        'Cyrillic': 'קירילית',
        'Syriac': 'סורית',
        'Punctuation': 'פיסוק',
        'General Punctuation': 'פיסוק כללי',
        'Hebrew Marks': 'ניקוד עברי',
        'Arabic Marks': 'ניקוד ערבי',
        'Diacritics': 'סימני ניקוד',
        'Combining Diacritical Marks': 'סימני ניקוד משולבים',
        'Numbers': 'מספרים',
        'Digits': 'ספרות',
        'Symbols': 'סמלים',
        'Mathematical Operators': 'אופרטורים מתמטיים'
      }
      return names[blockName] || blockName
    },

    blockIcon(blockName) {
      const icons = {
        'Hebrew': 'fas fa-alef',
        'Arabic': 'fas fa-language',
        'Latin': 'fas fa-font',
        'Basic Latin': 'fas fa-font',
        'Greek': 'fas fa-omega',
        'Cyrillic': 'fas fa-globe',
        'Punctuation': 'fas fa-ellipsis-h',
        'General Punctuation': 'fas fa-ellipsis-h',
        'Numbers': 'fas fa-hashtag',
        'Digits': 'fas fa-hashtag',
        'Symbols': 'fas fa-icons',
        'Diacritics': 'fas fa-dot-circle',
        'Hebrew Marks': 'fas fa-dot-circle',
        'Arabic Marks': 'fas fa-dot-circle'
      }
      return icons[blockName] || 'fas fa-layer-group'
    },

    accuracyClass(accuracy) {
      if (accuracy > 0.95) return 'text-success'
      if (accuracy > 0.85) return 'text-warning'
      return 'text-danger'
    },

    accuracyProgressClass(accuracy) {
      if (accuracy > 0.95) return 'bg-success'
      if (accuracy > 0.85) return 'bg-warning'
      return 'bg-danger'
    }
  }
}
</script>

<style scoped>
.unicode-block-stats {
  padding: 1rem;
}

.blocks-header h5 {
  margin-bottom: 0.5rem;
  color: #495057;
}

.block-card {
  transition: all 0.3s ease;
  border: 1px solid #dee2e6;
  height: 100%;
}

.block-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.block-card .card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.block-stats {
  font-size: 0.9rem;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
}

.stat-label {
  color: #6c757d;
  font-size: 0.85rem;
}

.stat-value {
  font-weight: 600;
  font-size: 1rem;
}

.accuracy-display {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.progress {
  height: 10px;
}

.char-range {
  padding-top: 0.5rem;
  border-top: 1px solid #e9ecef;
}

.blocks-summary {
  margin-top: 2rem;
}

.blocks-summary .card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.blocks-summary .card-title {
  color: white;
  font-weight: 600;
  margin-bottom: 1rem;
}

.summary-item {
  text-align: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.summary-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.summary-label {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
  opacity: 0.9;
}

.summary-value {
  font-size: 2rem;
  font-weight: bold;
}
</style>
