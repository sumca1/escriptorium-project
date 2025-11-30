<template>
  <div class="alignment-viewer" :class="{ 'rtl-mode': isRTL }">
    <!-- Header with document names -->
    <div class="alignment-header">
      <div class="document-info">
        <h3 class="document-title">
          <i class="bi bi-file-text"></i>
          {{ document1Name }}
        </h3>
      </div>
      
      <div class="alignment-status">
        <div v-if="status === 'pending' || status === 'processing'" class="status-indicator processing">
          <div class="spinner-border spinner-border-sm" role="status"></div>
          <span class="mx-2">{{ currentStep || translate('alignment.processing') }}</span>
          <div class="progress" style="width: 200px">
            <div 
              class="progress-bar progress-bar-striped progress-bar-animated" 
              :style="{ width: progress + '%' }"
            ></div>
          </div>
          <span class="badge bg-secondary">{{ progress }}%</span>
        </div>
        
        <div v-else-if="status === 'completed'" class="status-indicator success">
          <i class="bi bi-check-circle-fill text-success"></i>
          <span class="mx-2">{{ translate('alignment.completed') }}</span>
          <span class="badge bg-success">{{ totalPairs }} {{ translate('alignment.pairs') }}</span>
        </div>
        
        <div v-else-if="status === 'failed'" class="status-indicator error">
          <i class="bi bi-exclamation-triangle-fill text-danger"></i>
          <span class="mx-2 text-danger">{{ translate('alignment.failed') }}</span>
        </div>
      </div>
      
      <div class="document-info">
        <h3 class="document-title">
          <i class="bi bi-file-text"></i>
          {{ document2Name }}
        </h3>
      </div>
    </div>
    
    <!-- Statistics bar -->
    <div v-if="status === 'completed'" class="alignment-stats">
      <div class="stat-item">
        <span class="stat-label">{{ translate('alignment.totalPairs') }}:</span>
        <span class="stat-value">{{ totalPairs }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">{{ translate('alignment.avgSimilarity') }}:</span>
        <span class="stat-value">{{ (averageSimilarity * 100).toFixed(1) }}%</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">{{ translate('alignment.alignmentRate') }}:</span>
        <span class="stat-value">{{ (alignmentRate * 100).toFixed(1) }}%</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">{{ translate('alignment.method') }}:</span>
        <span class="stat-value">{{ method }}</span>
      </div>
    </div>
    
    <!-- Filters -->
    <div v-if="status === 'completed'" class="alignment-filters">
      <div class="filter-group">
        <label for="similarity-filter">{{ translate('alignment.minSimilarity') }}:</label>
        <input 
          id="similarity-filter"
          type="range" 
          v-model.number="minSimilarity" 
          min="0" 
          max="1" 
          step="0.05"
          class="form-range"
        />
        <span class="filter-value">{{ (minSimilarity * 100).toFixed(0) }}%</span>
      </div>
      
      <div class="filter-group">
        <input 
          type="checkbox" 
          v-model="showVerifiedOnly" 
          id="verified-only"
          class="form-check-input"
        />
        <label for="verified-only" class="form-check-label">
          {{ translate('alignment.verifiedOnly') }}
        </label>
      </div>
      
      <div class="filter-group">
        <button 
          @click="exportAlignment('json')" 
          class="btn btn-sm btn-outline-primary"
        >
          <i class="bi bi-download"></i> JSON
        </button>
        <button 
          @click="exportAlignment('csv')" 
          class="btn btn-sm btn-outline-primary"
        >
          <i class="bi bi-download"></i> CSV
        </button>
      </div>
    </div>
    
    <!-- Split view with alignment pairs -->
    <div v-if="status === 'completed'" class="alignment-content">
      <div class="pairs-container" ref="pairsContainer">
        <AlignmentPairRow
          v-for="pair in filteredPairs"
          :key="pair.id"
          :pair="pair"
          :is-rtl="isRTL"
          @verify="handleVerify"
          @reject="handleReject"
        />
        
        <div v-if="filteredPairs.length === 0" class="no-results">
          <i class="bi bi-inbox"></i>
          <p>{{ translate('alignment.noPairs') }}</p>
        </div>
        
        <!-- Load more button -->
        <div v-if="hasMore" class="load-more">
          <button @click="loadMore" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm"></span>
            {{ translate('alignment.loadMore') }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Loading overlay -->
    <div v-if="loading && !pairs.length" class="loading-overlay">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-3">{{ translate('alignment.loading') }}</p>
    </div>
  </div>
</template>

<script>
import AlignmentPairRow from './AlignmentPairRow.vue';

export default {
  name: 'AlignmentViewer',
  
  components: {
    AlignmentPairRow
  },
  
  props: {
    alignmentId: {
      type: Number,
      required: true
    },
    document1Name: {
      type: String,
      default: 'Document 1'
    },
    document2Name: {
      type: String,
      default: 'Document 2'
    },
    isRTL: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      status: 'pending',
      progress: 0,
      currentStep: '',
      totalPairs: 0,
      averageSimilarity: 0,
      alignmentRate: 0,
      method: 'auto',
      pairs: [],
      filteredPairs: [],
      currentPage: 1,
      perPage: 50,
      hasMore: true,
      loading: false,
      minSimilarity: 0.0,
      showVerifiedOnly: false,
      pollInterval: null
    };
  },
  
  mounted() {
    this.loadAlignmentStatus();
    this.startPolling();
  },
  
  beforeUnmount() {
    this.stopPolling();
  },
  
  watch: {
    minSimilarity() {
      this.applyFilters();
    },
    showVerifiedOnly() {
      this.applyFilters();
    }
  },
  
  methods: {
    async loadAlignmentStatus() {
      try {
        const response = await fetch(`/api/alignments/${this.alignmentId}/`);
        const data = await response.json();
        
        this.status = data.status;
        this.progress = data.progress || 0;
        this.currentStep = data.current_step || '';
        this.totalPairs = data.total_pairs || 0;
        this.averageSimilarity = data.average_similarity || 0;
        this.alignmentRate = data.alignment_rate || 0;
        this.method = data.method || 'auto';
        
        if (this.status === 'completed' && this.pairs.length === 0) {
          await this.loadPairs();
        }
      } catch (error) {
        console.error('Failed to load alignment status:', error);
      }
    },
    
    async loadPairs(page = 1) {
      this.loading = true;
      
      try {
        const params = new URLSearchParams({
          page: page,
          per_page: this.perPage
        });
        
        const response = await fetch(
          `/api/alignments/${this.alignmentId}/pairs/?${params}`
        );
        const data = await response.json();
        
        if (page === 1) {
          this.pairs = data.pairs;
        } else {
          this.pairs.push(...data.pairs);
        }
        
        this.currentPage = data.page;
        this.hasMore = data.page < data.total_pages;
        
        this.applyFilters();
      } catch (error) {
        console.error('Failed to load pairs:', error);
      } finally {
        this.loading = false;
      }
    },
    
    applyFilters() {
      this.filteredPairs = this.pairs.filter(pair => {
        if (pair.similarity < this.minSimilarity) return false;
        if (this.showVerifiedOnly && !pair.is_verified) return false;
        return true;
      });
    },
    
    async loadMore() {
      await this.loadPairs(this.currentPage + 1);
    },
    
    async handleVerify(pairId) {
      await this.updatePairStatus(pairId, 'verify');
    },
    
    async handleReject(pairId) {
      await this.updatePairStatus(pairId, 'reject');
    },
    
    async updatePairStatus(pairId, action) {
      try {
        const response = await fetch(
          `/api/alignments/pairs/${pairId}/verify/`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({ action })
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          
          // Update local pair
          const pair = this.pairs.find(p => p.id === pairId);
          if (pair) {
            pair.is_verified = data.is_verified;
            pair.is_rejected = data.is_rejected;
            pair.verified_by = data.verified_by;
            pair.verified_at = data.verified_at;
          }
          
          this.applyFilters();
        }
      } catch (error) {
        console.error('Failed to update pair status:', error);
      }
    },
    
    async exportAlignment(format) {
      const params = new URLSearchParams({ format });
      if (this.showVerifiedOnly) {
        params.append('verified_only', 'true');
      }
      
      window.location.href = `/api/alignments/${this.alignmentId}/export/?${params}`;
    },
    
    startPolling() {
      this.pollInterval = setInterval(() => {
        if (this.status === 'pending' || this.status === 'processing') {
          this.loadAlignmentStatus();
        } else {
          this.stopPolling();
        }
      }, 2000); // Poll every 2 seconds
    },
    
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = null;
      }
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
.alignment-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
}

.rtl-mode {
  direction: rtl;
}

.alignment-header {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 20px;
  padding: 20px;
  background: white;
  border-bottom: 2px solid #dee2e6;
  align-items: center;
}

.document-info {
  display: flex;
  align-items: center;
}

.document-title {
  margin: 0;
  font-size: 1.1rem;
  color: #495057;
}

.document-title i {
  margin-right: 8px;
  color: #6c757d;
}

.alignment-status {
  display: flex;
  justify-content: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 500;
}

.status-indicator.processing {
  background: #e7f3ff;
}

.status-indicator.success {
  background: #d4edda;
}

.status-indicator.error {
  background: #f8d7da;
}

.alignment-stats {
  display: flex;
  gap: 30px;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #dee2e6;
  justify-content: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  color: #6c757d;
  font-weight: 500;
}

.stat-value {
  color: #007bff;
  font-weight: 600;
}

.alignment-filters {
  display: flex;
  gap: 20px;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #dee2e6;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-value {
  min-width: 50px;
  text-align: right;
  font-weight: 600;
  color: #007bff;
}

.alignment-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.pairs-container {
  max-width: 1400px;
  margin: 0 auto;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.no-results i {
  font-size: 4rem;
  opacity: 0.5;
}

.load-more {
  text-align: center;
  padding: 20px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.form-range {
  width: 200px;
}
</style>
