<template>
  <div class="transcription-selector">
    <select 
      :value="selectedId" 
      @change="$emit('select', $event.target.value ? parseInt($event.target.value) : null)"
      class="form-select"
      :class="{ 'is-valid': selectedId }"
    >
      <option :value="null" v-if="allowNone">
        {{ translate('none') }} - {{ translate('optional') }}
      </option>
      <option value="" disabled selected v-else>
        {{ translate('selectTranscription') }}
      </option>
      
      <optgroup 
        v-for="(group, modelType) in groupedTranscriptions" 
        :key="modelType"
        :label="getModelTypeLabel(modelType)"
      >
        <option 
          v-for="trans in group" 
          :key="trans.id"
          :value="trans.id"
          :disabled="trans.id === excludeId"
        >
          {{ trans.name }} ({{ trans.text_length }} {{ translate('chars') }})
        </option>
      </optgroup>
    </select>
    
    <!-- Preview of selected transcription -->
    <div v-if="selectedTranscription" class="selected-preview mt-2">
      <small class="text-muted d-block">
        <i class="fas fa-info-circle"></i>
        {{ translate('model') }}: <strong>{{ selectedTranscription.model }}</strong>
      </small>
      <small class="text-muted d-block">
        <i class="fas fa-calendar"></i>
        {{ formatDate(selectedTranscription.created_at) }}
      </small>
      <div class="preview-text mt-1 p-2 bg-light rounded" dir="auto">
        <small class="text-monospace">
          {{ selectedTranscription.text_preview }}
        </small>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TranscriptionSelector',
  
  props: {
    transcriptions: {
      type: Array,
      required: true,
    },
    selectedId: {
      type: Number,
      default: null,
    },
    excludeId: {
      type: Number,
      default: null,
    },
    allowNone: {
      type: Boolean,
      default: false,
    },
  },
  
  computed: {
    groupedTranscriptions() {
      const groups = {
        kraken: [],
        tesseract: [],
        manual: [],
        other: [],
      }
      
      this.transcriptions.forEach(trans => {
        if (trans.id === this.excludeId) return
        
        const type = trans.model_type || 'other'
        if (groups[type]) {
          groups[type].push(trans)
        } else {
          groups.other.push(trans)
        }
      })
      
      // Remove empty groups
      Object.keys(groups).forEach(key => {
        if (groups[key].length === 0) {
          delete groups[key]
        }
      })
      
      return groups
    },
    
    selectedTranscription() {
      if (!this.selectedId) return null
      return this.transcriptions.find(t => t.id === this.selectedId)
    },
  },
  
  methods: {
    translate(key) {
      return window.COMPARISON_TRANSLATIONS?.[key] || key
    },
    
    getModelTypeLabel(type) {
      const labels = {
        kraken: '🔷 Kraken',
        tesseract: '🔶 Tesseract',
        manual: '✍️ Manual',
        other: '📝 Other',
      }
      return labels[type] || type
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('he-IL', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    },
  },
}
</script>

<style scoped>
.transcription-selector {
  width: 100%;
}

.form-select {
  border-radius: 6px;
  border: 2px solid #dee2e6;
  transition: all 0.3s;
}

.form-select:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-select.is-valid {
  border-color: #28a745;
}

.selected-preview {
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.preview-text {
  max-height: 100px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  line-height: 1.4;
  white-space: pre-wrap;
  word-break: break-word;
}

optgroup {
  font-weight: bold;
  font-size: 0.9rem;
}

option {
  font-weight: normal;
  padding: 0.5rem;
}

option:disabled {
  opacity: 0.5;
  text-decoration: line-through;
}
</style>
