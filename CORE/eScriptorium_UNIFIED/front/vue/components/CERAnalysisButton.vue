<template>
  <div class="cer-analysis-wrapper">
    <!-- CER Button -->
    <button
      type="button"
      class="cer-analysis-btn nav-item btn btn-outline-info"
      :title="translate('cer.createAnalysis')"
      @click="showModal = true"
    >
      <i class="fas fa-chart-line"></i>
      <span class="btn-label">CER</span>
    </button>

    <!-- CER Analysis Modal -->
    <b-modal
      v-model="showModal"
      :title="translate('cer.title')"
      size="xl"
      hide-footer
      @hidden="onModalHidden"
    >
      <!-- Step 1: Create Analysis -->
      <div v-if="!currentAnalysisId" class="create-analysis-section">
        <div class="alert alert-info">
          <i class="fas fa-info-circle"></i>
          {{ translate('cer.pleaseSelectBothTranscriptions') }}
        </div>

        <div class="row mb-3">
          <div class="col-md-6">
            <label class="form-label">
              <strong>{{ translate('cer.groundTruth') }}:</strong>
            </label>
            <select v-model="selectedGroundTruth" class="form-select">
              <option :value="null">-- {{ translate('cer.selectGroundTruth') }} --</option>
              <option 
                v-for="transcription in availableTranscriptions" 
                :key="transcription.id"
                :value="transcription.id"
              >
                {{ transcription.name }}
              </option>
            </select>
          </div>

          <div class="col-md-6">
            <label class="form-label">
              <strong>{{ translate('cer.hypothesis') }}:</strong>
            </label>
            <select v-model="selectedHypothesis" class="form-select">
              <option :value="null">-- {{ translate('cer.selectHypothesis') }} --</option>
              <option 
                v-for="transcription in availableTranscriptions" 
                :key="transcription.id"
                :value="transcription.id"
                :disabled="transcription.id === selectedGroundTruth"
              >
                {{ transcription.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Preprocessing Options -->
        <div class="preprocessing-options mb-3">
          <h6>{{ translate('cer.preprocessingOptions') }}:</h6>
          <div class="row">
            <div class="col-md-4">
              <div class="form-check">
                <input v-model="options.remove_whitespace" type="checkbox" class="form-check-input" id="opt-whitespace">
                <label class="form-check-label" for="opt-whitespace">
                  {{ translate('cer.removeWhitespace') }}
                </label>
              </div>
            </div>
            <div class="col-md-4">
              <div class="form-check">
                <input v-model="options.remove_punctuation" type="checkbox" class="form-check-input" id="opt-punct">
                <label class="form-check-label" for="opt-punct">
                  {{ translate('cer.removePunctuation') }}
                </label>
              </div>
            </div>
            <div class="col-md-4">
              <div class="form-check">
                <input v-model="options.lowercase" type="checkbox" class="form-check-input" id="opt-lowercase">
                <label class="form-check-label" for="opt-lowercase">
                  {{ translate('cer.lowercase') }}
                </label>
              </div>
            </div>
            <div class="col-md-4">
              <div class="form-check">
                <input v-model="options.remove_nikud" type="checkbox" class="form-check-input" id="opt-nikud">
                <label class="form-check-label" for="opt-nikud">
                  {{ translate('cer.removeNikud') }}
                </label>
              </div>
            </div>
            <div class="col-md-4">
              <div class="form-check">
                <input v-model="options.normalize_hebrew_final" type="checkbox" class="form-check-input" id="opt-final">
                <label class="form-check-label" for="opt-final">
                  {{ translate('cer.normalizeFinalLetters') }}
                </label>
              </div>
            </div>
            <div class="col-md-4">
              <div class="form-check">
                <input v-model="options.remove_non_alpha" type="checkbox" class="form-check-input" id="opt-non-alpha">
                <label class="form-check-label" for="opt-non-alpha">
                  {{ translate('cer.removeNonAlpha') }}
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Create Button -->
        <div class="text-center">
          <button 
            @click="createAnalysis"
            :disabled="!canCreateAnalysis || creating"
            class="btn btn-primary btn-lg"
          >
            <span v-if="creating">
              <span class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ translate('cer.analyzing') }}
            </span>
            <span v-else>
              <i class="fas fa-chart-line me-2"></i>
              {{ translate('cer.analyze') }}
            </span>
          </button>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="alert alert-danger mt-3">
          <i class="fas fa-exclamation-circle"></i>
          {{ error }}
        </div>
      </div>

      <!-- Step 2: Display Analysis -->
      <div v-else class="analysis-display-section">
        <CERAnalysisPanel :analysis-id="currentAnalysisId" />
        
        <div class="text-center mt-3">
          <button @click="resetAnalysis" class="btn btn-secondary">
            <i class="fas fa-redo"></i>
            {{ translate('cer.createAnalysis') }}
          </button>
        </div>
      </div>
    </b-modal>
  </div>
</template>

<script>
import CERAnalysisPanel from './CERAnalysis/CERAnalysisPanel.vue'

export default {
  name: 'CERAnalysisButton',

  components: {
    CERAnalysisPanel
  },

  data() {
    return {
      showModal: false,
      selectedGroundTruth: null,
      selectedHypothesis: null,
      currentAnalysisId: null,
      creating: false,
      error: null,
      options: {
        remove_whitespace: false,
        remove_punctuation: false,
        lowercase: false,
        remove_nikud: false,
        normalize_hebrew_final: false,
        remove_non_alpha: false
      }
    }
  },

  computed: {
    availableTranscriptions() {
      // Get transcriptions from Vuex store
      // This assumes the store has transcriptions available
      return this.$store.state.document?.transcriptions || []
    },

    canCreateAnalysis() {
      return this.selectedGroundTruth && this.selectedHypothesis && 
             this.selectedGroundTruth !== this.selectedHypothesis
    }
  },

  methods: {
    async createAnalysis() {
      if (!this.canCreateAnalysis) {
        this.error = this.translate('cer.pleaseSelectBothTranscriptions')
        return
      }

      this.creating = true
      this.error = null

      try {
        const response = await fetch('/api/cerberus/analyses/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken()
          },
          body: JSON.stringify({
            ground_truth_id: this.selectedGroundTruth,
            hypothesis_id: this.selectedHypothesis,
            ...this.options
          })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `HTTP ${response.status}`)
        }

        const analysis = await response.json()
        this.currentAnalysisId = analysis.id

      } catch (err) {
        console.error('Error creating CER analysis:', err)
        this.error = this.translate('cer.errorCreatingAnalysis') + ': ' + err.message
      } finally {
        this.creating = false
      }
    },

    resetAnalysis() {
      this.currentAnalysisId = null
      this.selectedGroundTruth = null
      this.selectedHypothesis = null
      this.error = null
    },

    onModalHidden() {
      // Reset when modal closes
      setTimeout(() => {
        this.resetAnalysis()
      }, 300)
    },

    getCsrfToken() {
      // Get CSRF token from cookie
      const name = 'csrftoken'
      const cookies = document.cookie.split(';')
      for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=')
        if (key === name) return decodeURIComponent(value)
      }
      return ''
    }
  }
}
</script>

<style scoped>
.cer-analysis-btn {
  margin-left: 10px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-label {
  font-size: 0.9rem;
  font-weight: 600;
}

.create-analysis-section {
  padding: 1rem;
}

.preprocessing-options {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.preprocessing-options h6 {
  margin-bottom: 1rem;
  color: #495057;
}

.analysis-display-section {
  min-height: 500px;
}
</style>
