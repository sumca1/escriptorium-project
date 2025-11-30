<template>
  <div class="alignment-controls">
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">
          <i class="bi bi-sliders"></i>
          {{ translate('alignment.createAlignment') }}
        </h5>
      </div>
      
      <div class="card-body">
        <!-- Document selection -->
        <div class="form-group mb-3">
          <label for="doc1-select">{{ translate('alignment.document1') }}</label>
          <select 
            id="doc1-select"
            v-model="selectedDoc1"
            class="form-select"
            :disabled="isProcessing"
          >
            <option value="">{{ translate('alignment.selectDocument') }}</option>
            <option 
              v-for="doc in availableDocuments"
              :key="doc.id"
              :value="doc.id"
            >
              {{ doc.name }}
            </option>
          </select>
        </div>
        
        <div class="form-group mb-3">
          <label for="doc2-select">{{ translate('alignment.document2') }}</label>
          <select 
            id="doc2-select"
            v-model="selectedDoc2"
            class="form-select"
            :disabled="isProcessing"
          >
            <option value="">{{ translate('alignment.selectDocument') }}</option>
            <option 
              v-for="doc in availableDocuments"
              :key="doc.id"
              :value="doc.id"
              :disabled="doc.id === selectedDoc1"
            >
              {{ doc.name }}
            </option>
          </select>
        </div>
        
        <!-- Method selection -->
        <div class="form-group mb-3">
          <label for="method-select">{{ translate('alignment.method') }}</label>
          <select 
            id="method-select"
            v-model="method"
            class="form-select"
            :disabled="isProcessing"
          >
            <option value="auto">{{ translate('alignment.methodAuto') }}</option>
            <option value="sequence">{{ translate('alignment.methodSequence') }}</option>
            <option value="levenshtein">{{ translate('alignment.methodLevenshtein') }}</option>
            <option value="jaccard">{{ translate('alignment.methodJaccard') }}</option>
          </select>
          <div class="form-text">
            <small>{{ methodDescription }}</small>
          </div>
        </div>
        
        <!-- Threshold slider -->
        <div class="form-group mb-3">
          <label for="threshold-slider">
            {{ translate('alignment.threshold') }}: 
            <strong>{{ (threshold * 100).toFixed(0) }}%</strong>
          </label>
          <input 
            id="threshold-slider"
            type="range"
            v-model.number="threshold"
            min="0"
            max="1"
            step="0.05"
            class="form-range"
            :disabled="isProcessing"
          />
          <div class="form-text">
            <small>{{ translate('alignment.thresholdHelp') }}</small>
          </div>
        </div>
        
        <!-- Min length -->
        <div class="form-group mb-4">
          <label for="min-length-input">{{ translate('alignment.minLength') }}</label>
          <input 
            id="min-length-input"
            type="number"
            v-model.number="minLength"
            min="1"
            max="100"
            class="form-control"
            :disabled="isProcessing"
          />
          <div class="form-text">
            <small>{{ translate('alignment.minLengthHelp') }}</small>
          </div>
        </div>
        
        <!-- Action buttons -->
        <div class="d-grid gap-2">
          <button 
            @click="startAlignment"
            class="btn btn-primary btn-lg"
            :disabled="!canStart || isProcessing"
          >
            <span v-if="isProcessing" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-play-fill"></i>
            {{ isProcessing ? translate('alignment.processing') : translate('alignment.start') }}
          </button>
          
          <button 
            v-if="currentAlignmentId"
            @click="$emit('view-results', currentAlignmentId)"
            class="btn btn-outline-primary"
          >
            <i class="bi bi-eye"></i>
            {{ translate('alignment.viewResults') }}
          </button>
        </div>
        
        <!-- Error message -->
        <div v-if="errorMessage" class="alert alert-danger mt-3 mb-0">
          <i class="bi bi-exclamation-triangle-fill"></i>
          {{ errorMessage }}
        </div>
        
        <!-- Success message -->
        <div v-if="successMessage" class="alert alert-success mt-3 mb-0">
          <i class="bi bi-check-circle-fill"></i>
          {{ successMessage }}
        </div>
      </div>
    </div>
    
    <!-- Recent alignments -->
    <div v-if="recentAlignments.length > 0" class="card mt-3">
      <div class="card-header">
        <h6 class="mb-0">
          <i class="bi bi-clock-history"></i>
          {{ translate('alignment.recentAlignments') }}
        </h6>
      </div>
      <div class="card-body p-0">
        <div class="list-group list-group-flush">
          <a 
            v-for="alignment in recentAlignments"
            :key="alignment.id"
            @click.prevent="$emit('view-results', alignment.id)"
            href="#"
            class="list-group-item list-group-item-action"
          >
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="fw-bold">{{ alignment.document1.name }} ↔ {{ alignment.document2.name }}</div>
                <small class="text-muted">
                  {{ alignment.total_pairs }} {{ translate('alignment.pairs') }}
                  • {{ (alignment.average_similarity * 100).toFixed(0) }}% {{ translate('alignment.similarity') }}
                </small>
              </div>
              <span :class="'badge bg-' + getStatusColor(alignment.status)">
                {{ translate('alignment.status_' + alignment.status) }}
              </span>
            </div>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlignmentControls',
  
  props: {
    availableDocuments: {
      type: Array,
      default: () => []
    }
  },
  
  emits: ['alignment-created', 'view-results'],
  
  data() {
    return {
      selectedDoc1: '',
      selectedDoc2: '',
      method: 'auto',
      threshold: 0.7,
      minLength: 10,
      isProcessing: false,
      errorMessage: '',
      successMessage: '',
      currentAlignmentId: null,
      recentAlignments: []
    };
  },
  
  computed: {
    canStart() {
      return this.selectedDoc1 && 
             this.selectedDoc2 && 
             this.selectedDoc1 !== this.selectedDoc2;
    },
    
    methodDescription() {
      const descriptions = {
        auto: this.translate('alignment.methodAutoDesc'),
        sequence: this.translate('alignment.methodSequenceDesc'),
        levenshtein: this.translate('alignment.methodLevenshteinDesc'),
        jaccard: this.translate('alignment.methodJaccardDesc')
      };
      return descriptions[this.method] || '';
    }
  },
  
  mounted() {
    this.loadRecentAlignments();
  },
  
  methods: {
    async startAlignment() {
      this.errorMessage = '';
      this.successMessage = '';
      this.isProcessing = true;
      
      try {
        const response = await fetch('/api/alignments/create/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken()
          },
          body: JSON.stringify({
            document1_id: this.selectedDoc1,
            document2_id: this.selectedDoc2,
            method: this.method,
            threshold: this.threshold,
            min_length: this.minLength
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.currentAlignmentId = data.alignment_id;
          this.successMessage = this.translate('alignment.startedSuccessfully');
          this.$emit('alignment-created', data);
          await this.loadRecentAlignments();
          
          // Clear success message after 3 seconds
          setTimeout(() => {
            this.successMessage = '';
          }, 3000);
        } else {
          this.errorMessage = data.error || this.translate('alignment.errorStarting');
        }
      } catch (error) {
        console.error('Failed to start alignment:', error);
        this.errorMessage = this.translate('alignment.errorNetwork');
      } finally {
        this.isProcessing = false;
      }
    },
    
    async loadRecentAlignments() {
      try {
        const response = await fetch('/api/alignments/?per_page=5');
        const data = await response.json();
        this.recentAlignments = data.alignments || [];
      } catch (error) {
        console.error('Failed to load recent alignments:', error);
      }
    },
    
    getStatusColor(status) {
      const colors = {
        pending: 'secondary',
        processing: 'info',
        completed: 'success',
        failed: 'danger'
      };
      return colors[status] || 'secondary';
    },
    
    getCsrfToken() {
      const name = 'csrftoken';
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          return cookie.substring(name.length + 1);
        }
      }
      return '';
    }
  }
};
</script>

<style scoped>
.alignment-controls {
  max-width: 500px;
}

.card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  padding: 15px 20px;
}

.card-header h5,
.card-header h6 {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-group label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
  display: block;
}

.form-text {
  margin-top: 5px;
}

.list-group-item {
  border-left: 3px solid transparent;
  transition: all 0.2s ease;
}

.list-group-item:hover {
  border-left-color: #007bff;
  background: #f8f9fa;
}
</style>
