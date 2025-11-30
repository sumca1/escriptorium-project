<template>
  <div class="alignment-pair" :class="pairClass">
    <div class="pair-content">
      <!-- Left/Right text (Document 1) -->
      <div class="text-column text-1">
        <div class="line-number">#{{ pair.line1.id }}</div>
        <div class="text-content" v-html="highlightDifferences(pair.line1.text, pair.line2.text)"></div>
      </div>
      
      <!-- Similarity indicator -->
      <div class="similarity-column">
        <div class="similarity-bar">
          <div class="similarity-fill" :style="{ height: (pair.similarity * 100) + '%' }"></div>
        </div>
        <div class="similarity-value" :class="similarityClass">
          {{ (pair.similarity * 100).toFixed(0) }}%
        </div>
        <div class="method-badge">
          {{ pair.method }}
        </div>
      </div>
      
      <!-- Right/Left text (Document 2) -->
      <div class="text-column text-2">
        <div class="line-number">#{{ pair.line2.id }}</div>
        <div class="text-content" v-html="highlightDifferences(pair.line2.text, pair.line1.text)"></div>
      </div>
    </div>
    
    <!-- Action buttons -->
    <div class="pair-actions">
      <button 
        v-if="!pair.is_verified && !pair.is_rejected"
        @click="$emit('verify', pair.id)"
        class="btn btn-sm btn-success"
        :title="translate('Verify alignment')"
      >
        <i class="bi bi-check-lg"></i> {{ translate('alignment.verify') }}
      </button>
      
      <button 
        v-if="!pair.is_rejected && !pair.is_verified"
        @click="$emit('reject', pair.id)"
        class="btn btn-sm btn-danger"
        :title="translate('Reject alignment')"
      >
        <i class="bi bi-x-lg"></i> {{ translate('alignment.reject') }}
      </button>
      
      <span v-if="pair.is_verified" class="badge bg-success">
        <i class="bi bi-check-circle-fill"></i> {{ translate('alignment.verified') }}
        <small v-if="pair.verified_by">{{ translate('by') }} {{ pair.verified_by }}</small>
      </span>
      
      <span v-if="pair.is_rejected" class="badge bg-danger">
        <i class="bi bi-x-circle-fill"></i> {{ translate('alignment.rejected') }}
        <small v-if="pair.verified_by">{{ translate('by') }} {{ pair.verified_by }}</small>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlignmentPairRow',
  
  props: {
    pair: {
      type: Object,
      required: true
    },
    isRTL: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['verify', 'reject'],
  
  computed: {
    pairClass() {
      return {
        'is-verified': this.pair.is_verified,
        'is-rejected': this.pair.is_rejected,
        'high-similarity': this.pair.similarity >= 0.9,
        'medium-similarity': this.pair.similarity >= 0.7 && this.pair.similarity < 0.9,
        'low-similarity': this.pair.similarity < 0.7,
        'rtl-text': this.isRTL
      };
    },
    
    similarityClass() {
      if (this.pair.similarity >= 0.9) return 'text-success';
      if (this.pair.similarity >= 0.7) return 'text-warning';
      return 'text-danger';
    }
  },
  
  methods: {
    highlightDifferences(text1, text2) {
      // Simple character-level diff highlighting
      // In production, use a proper diff library like diff-match-patch
      
      if (!text1 || !text2) return text1 || '';
      
      // For now, just return the text as-is
      // TODO: Implement proper diff highlighting
      return this.escapeHtml(text1);
    },
    
    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }
  }
};
</script>

<style scoped>
.alignment-pair {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 16px;
  padding: 16px;
  transition: all 0.2s ease;
}

.alignment-pair:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #007bff;
}

.alignment-pair.is-verified {
  border-color: #28a745;
  background: #f8fff9;
}

.alignment-pair.is-rejected {
  border-color: #dc3545;
  background: #fff5f5;
  opacity: 0.7;
}

.pair-content {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 20px;
  margin-bottom: 12px;
  align-items: center;
}

.text-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.line-number {
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 600;
}

.text-content {
  font-size: 1.1rem;
  line-height: 1.6;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  min-height: 60px;
  word-wrap: break-word;
}

.rtl-text .text-content {
  direction: rtl;
  text-align: right;
}

.similarity-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
}

.similarity-bar {
  width: 20px;
  height: 80px;
  background: #e9ecef;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.similarity-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, #dc3545, #ffc107, #28a745);
  transition: height 0.3s ease;
}

.similarity-value {
  font-weight: 700;
  font-size: 1.1rem;
}

.method-badge {
  font-size: 0.7rem;
  padding: 2px 6px;
  background: #e9ecef;
  border-radius: 4px;
  color: #495057;
  text-transform: uppercase;
  font-weight: 600;
}

.pair-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  align-items: center;
}

.pair-actions .btn {
  min-width: 100px;
}

.pair-actions .badge {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.pair-actions .badge small {
  display: block;
  font-size: 0.75rem;
  opacity: 0.8;
  margin-top: 2px;
}

/* Similarity level indicators */
.high-similarity {
  border-left: 4px solid #28a745;
}

.medium-similarity {
  border-left: 4px solid #ffc107;
}

.low-similarity {
  border-left: 4px solid #dc3545;
}
</style>
