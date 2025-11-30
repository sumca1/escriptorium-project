<template>
  <div
    v-if="$store.state.parts.loaded"
    class="nav-div nav-item"
  >
    <button
      type="button"
      class="comparison-btn nav-item btn btn-outline-primary"
      :title="translate('Compare OCR Engines (Kraken vs Tesseract)')"
      :disabled="!hasMultipleTranscriptions"
      @click="openComparisonViewer"
    >
      <i class="fas fa-balance-scale" />
      <span class="btn-text ml-1">{{ translate('Compare Engines') }}</span>
    </button>
  </div>
</template>

<script>
export default {
  name: 'ComparisonButton',
  
  computed: {
    hasMultipleTranscriptions() {
      // בדוק אם יש לפחות 2 transcriptions
      const transcriptions = this.$store.state.transcriptions?.all || [];
      const activeTranscriptions = transcriptions.filter(t => !t.archived);
      return activeTranscriptions.length >= 2;
    },
    
    documentId() {
      return this.$store.state.document?.id;
    }
  },
  
  methods: {
    translate(key) {
      // שימוש ב-window.EDITOR_TRANSLATIONS כמו שאר הרכיבים
      return window.EDITOR_TRANSLATIONS && window.EDITOR_TRANSLATIONS[key] || key;
    },
    
    openComparisonViewer() {
      if (!this.documentId) {
        console.error('No document ID available');
        return;
      }
      
      // פתיחת דף ההשוואה בחלון חדש
      const url = `/comparison/document/${this.documentId}/`;
      window.open(url, '_blank', 'width=1400,height=900');
    }
  }
};
</script>

<style scoped>
.comparison-btn {
  white-space: nowrap;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.comparison-btn:hover:not(:disabled) {
  background-color: #667eea;
  border-color: #667eea;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.comparison-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.comparison-btn i {
  font-size: 16px;
}

.btn-text {
  display: inline;
}

/* הסתרת הטקסט במסכים קטנים */
@media (max-width: 768px) {
  .btn-text {
    display: none;
  }
  
  .comparison-btn {
    padding: 6px 10px;
  }
}
</style>
