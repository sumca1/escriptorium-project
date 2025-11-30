<template>
  <div class="language-detector-panel card mb-3" v-if="detection">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h6 class="mb-0">
        <i class="fas fa-language"></i>
        {{ $t('language_detection.title') }}
      </h6>
      <button 
        class="btn btn-sm btn-outline-primary" 
        @click="detectLanguage"
        :disabled="loading">
        <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
        {{ loading ? $t('language_detection.detecting') : $t('language_detection.redetect') }}
      </button>
    </div>

    <div class="card-body">
      <!-- Error Message -->
      <div v-if="error" class="alert alert-danger">
        <i class="fas fa-exclamation-triangle"></i>
        {{ error }}
      </div>

      <!-- Detection Results -->
      <div v-else-if="detection && !loading">
        <!-- Script & Direction -->
        <div class="row mb-3">
          <div class="col-md-6">
            <div class="info-box">
              <label class="text-muted small">{{ $t('language_detection.script') }}</label>
              <div class="d-flex align-items-center">
                <span class="badge" :class="scriptBadgeClass">
                  {{ scriptIcon }} {{ scriptName }}
                </span>
                <span class="ms-2 small text-muted">
                  {{ (detection.confidence * 100).toFixed(0) }}% {{ $t('language_detection.confidence') }}
                </span>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="info-box">
              <label class="text-muted small">{{ $t('language_detection.direction') }}</label>
              <div>
                <span class="badge bg-secondary">
                  {{ detection.direction === 'rtl' ? '→ RTL' : '← LTR' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Special Features (Nikud/Tashkeel) -->
        <div v-if="hasSpecialFeatures" class="mb-3">
          <label class="text-muted small">{{ $t('language_detection.features') }}</label>
          <div class="d-flex gap-2">
            <span v-if="detection.has_nikud" class="badge bg-info">
              ✨ {{ $t('language_detection.has_nikud') }}
            </span>
            <span v-if="detection.has_teamim" class="badge bg-info">
              📖 {{ $t('language_detection.has_teamim') }}
            </span>
            <span v-if="detection.has_tashkeel" class="badge bg-info">
              ✨ {{ $t('language_detection.has_tashkeel') }}
            </span>
          </div>
        </div>

        <!-- OCR Recommendations -->
        <div class="recommendations-box p-3 bg-light rounded">
          <h6 class="mb-2">
            <i class="fas fa-magic"></i>
            {{ $t('language_detection.recommendations') }}
          </h6>

          <div class="mb-2">
            <strong>{{ $t('language_detection.recommended_engine') }}:</strong>
            <span class="ms-2 badge bg-success">
              {{ detection.recommended_engine }}
            </span>
          </div>

          <div v-if="detection.model_hint" class="mb-2">
            <strong>{{ $t('language_detection.suggested_model') }}:</strong>
            <code class="ms-2">{{ detection.model_hint }}</code>
          </div>

          <div v-if="detection.preprocessing && detection.preprocessing.length > 0">
            <strong>{{ $t('language_detection.preprocessing') }}:</strong>
            <div class="mt-1">
              <span 
                v-for="step in detection.preprocessing" 
                :key="step" 
                class="badge bg-secondary me-1">
                {{ step }}
              </span>
            </div>
          </div>
        </div>

        <!-- Sample Text -->
        <div v-if="detection.sample_text" class="mt-3">
          <label class="text-muted small">{{ $t('language_detection.sample_text') }}</label>
          <div 
            class="sample-text p-2 bg-white border rounded small" 
            :dir="detection.direction">
            {{ detection.sample_text }}
          </div>
        </div>

        <!-- Auto-Set Direction Button -->
        <div class="mt-3 text-end">
          <button 
            class="btn btn-sm btn-primary" 
            @click="autoSetDirection"
            :disabled="loadingAutoSet">
            <i class="fas fa-magic" :class="{ 'fa-spin': loadingAutoSet }"></i>
            {{ $t('language_detection.auto_set_direction') }}
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-else-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ $t('language_detection.loading') }}</span>
        </div>
        <p class="mt-2 text-muted">{{ $t('language_detection.analyzing') }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LanguageDetector',
  
  props: {
    documentId: {
      type: Number,
      required: true
    },
    autoLoad: {
      type: Boolean,
      default: true
    }
  },

  data() {
    return {
      detection: null,
      loading: false,
      loadingAutoSet: false,
      error: null
    };
  },

  computed: {
    scriptName() {
      const names = {
        'hebrew': this.$t('language_detection.scripts.hebrew'),
        'arabic': this.$t('language_detection.scripts.arabic'),
        'latin': this.$t('language_detection.scripts.latin'),
        'greek': this.$t('language_detection.scripts.greek'),
        'cyrillic': this.$t('language_detection.scripts.cyrillic'),
        'mixed': this.$t('language_detection.scripts.mixed'),
        'unknown': this.$t('language_detection.scripts.unknown')
      };
      return names[this.detection.script] || this.detection.script;
    },

    scriptIcon() {
      const icons = {
        'hebrew': '🔤',
        'arabic': '🕌',
        'latin': '📝',
        'greek': '🏛️',
        'cyrillic': '☭',
        'mixed': '🌐',
        'unknown': '❓'
      };
      return icons[this.detection.script] || '';
    },

    scriptBadgeClass() {
      const classes = {
        'hebrew': 'bg-primary',
        'arabic': 'bg-success',
        'latin': 'bg-info',
        'mixed': 'bg-warning',
        'unknown': 'bg-secondary'
      };
      return classes[this.detection.script] || 'bg-secondary';
    },

    hasSpecialFeatures() {
      return this.detection.has_nikud || 
             this.detection.has_teamim || 
             this.detection.has_tashkeel;
    }
  },

  mounted() {
    if (this.autoLoad) {
      this.detectLanguage();
    }
  },

  methods: {
    async detectLanguage(sampleSize = 500) {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch(
          `/api/documents/${this.documentId}/detect-language/?sample_size=${sampleSize}`,
          {
            headers: {
              'Authorization': `Token ${window.csrfToken}`,  // Adjust as needed
              'Content-Type': 'application/json'
            }
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Detection failed');
        }

        this.detection = await response.json();
        this.$emit('detected', this.detection);
        
      } catch (err) {
        this.error = err.message;
        console.error('Language detection error:', err);
      } finally {
        this.loading = false;
      }
    },

    async autoSetDirection() {
      this.loadingAutoSet = true;

      try {
        const response = await fetch(
          `/api/documents/${this.documentId}/detect-language/?auto_set_direction=true`,
          {
            headers: {
              'Authorization': `Token ${window.csrfToken}`,
              'Content-Type': 'application/json'
            }
          }
        );

        if (!response.ok) {
          throw new Error('Failed to set direction');
        }

        const result = await response.json();
        this.detection = result;
        
        if (result.direction_auto_updated) {
          this.$emit('direction-updated', result.direction);
          // Show success message
          alert(this.$t('language_detection.direction_updated'));
          // Reload page to reflect changes
          window.location.reload();
        } else {
          alert(this.$t('language_detection.direction_already_correct'));
        }

      } catch (err) {
        alert('Error: ' + err.message);
        console.error('Auto-set direction error:', err);
      } finally {
        this.loadingAutoSet = false;
      }
    }
  }
};
</script>

<style scoped>
.language-detector-panel {
  border: 1px solid #dee2e6;
}

.info-box {
  padding: 0.5rem;
}

.recommendations-box {
  border-left: 4px solid #28a745;
}

.sample-text {
  font-family: 'Noto Sans', 'Arial Unicode MS', sans-serif;
  line-height: 1.6;
  max-height: 100px;
  overflow-y: auto;
}

.badge {
  font-size: 0.875rem;
  padding: 0.375rem 0.75rem;
}

.gap-2 {
  gap: 0.5rem;
}
</style>
