<template>
  <div class="search-panel" :class="{ 'rtl': isRTL }">
    <!-- Search Input -->
    <div class="search-header">
      <h3>{{ translate('search.title') || 'חיפוש מתקדם' }}</h3>
      <div class="search-input-group">
        <input
          v-model="searchQuery"
          type="text"
          class="form-control search-input"
          :placeholder="translate('search.placeholder') || 'חפש בכל המסמכים...'"
          @keyup.enter="performSearch"
          @input="debounceSearch"
        />
        <button 
          class="btn btn-primary search-btn"
          @click="performSearch"
          :disabled="!searchQuery || isSearching"
        >
          <i class="fas fa-search"></i>
          {{ isSearching ? (translate('search.searching') || 'מחפש...') : (translate('search.search') || 'חפש') }}
        </button>
      </div>
      
      <!-- Filters -->
      <div class="search-filters" v-if="showFilters">
        <div class="filter-group">
          <label>{{ translate('search.filters.document') || 'מסמך' }}:</label>
          <select v-model="filters.document" class="form-control">
            <option :value="null">{{ translate('search.filters.all') || 'הכל' }}</option>
            <!-- Add documents dynamically -->
          </select>
        </div>
        
        <div class="filter-group">
          <label>{{ translate('search.filters.project') || 'פרויקט' }}:</label>
          <select v-model="filters.project" class="form-control">
            <option :value="null">{{ translate('search.filters.all') || 'הכל' }}</option>
            <!-- Add projects dynamically -->
          </select>
        </div>
        
        <div class="filter-group">
          <label>{{ translate('search.filters.confidence') || 'ביטחון מינימלי' }}:</label>
          <input 
            v-model.number="filters.minConfidence" 
            type="number" 
            min="0" 
            max="1" 
            step="0.1"
            class="form-control"
          />
        </div>
      </div>
      
      <button 
        class="btn btn-link toggle-filters"
        @click="showFilters = !showFilters"
      >
        <i :class="showFilters ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
        {{ showFilters ? (translate('search.hideFilters') || 'הסתר מסננים') : (translate('search.showFilters') || 'הצג מסננים') }}
      </button>
    </div>

    <!-- Search Stats -->
    <div class="search-stats" v-if="searchResults">
      <span class="results-count">
        {{ translate('search.resultsCount') || 'נמצאו' }}: 
        <strong>{{ searchResults.total }}</strong> 
        {{ translate('search.results') || 'תוצאות' }}
      </span>
      <span class="search-time" v-if="searchResults.took_ms">
        ({{ searchResults.took_ms }}ms)
      </span>
    </div>

    <!-- Loading State -->
    <div class="search-loading" v-if="isSearching">
      <div class="spinner-border text-primary" role="status">
        <span class="sr-only">{{ translate('search.loading') || 'טוען...' }}</span>
      </div>
      <p>{{ translate('search.searching') || 'מחפש...' }}</p>
    </div>

    <!-- Error State -->
    <div class="alert alert-danger search-error" v-if="searchError">
      <i class="fas fa-exclamation-triangle"></i>
      {{ searchError }}
    </div>

    <!-- No Results -->
    <div class="search-no-results" v-if="!isSearching && searchResults && searchResults.total === 0">
      <i class="fas fa-search"></i>
      <p>{{ translate('search.noResults') || 'לא נמצאו תוצאות' }}</p>
      <p class="text-muted">
        {{ translate('search.tryDifferent') || 'נסה מונח חיפוש אחר או שנה את המסננים' }}
      </p>
    </div>

    <!-- Search Results -->
    <div class="search-results" v-if="!isSearching && searchResults && searchResults.results.length > 0">
      <div 
        v-for="result in searchResults.results" 
        :key="result.id"
        class="search-result-item"
        @click="goToResult(result)"
      >
        <div class="result-header">
          <h4 class="result-document">
            <i class="fas fa-file-alt"></i>
            {{ result.document_name }}
          </h4>
          <span class="result-score" :title="translate('search.relevanceScore') || 'ציון רלוונטיות'">
            <i class="fas fa-star"></i>
            {{ result.score.toFixed(2) }}
          </span>
        </div>
        
        <div class="result-meta">
          <span class="result-project" v-if="result.project_name">
            <i class="fas fa-folder"></i>
            {{ result.project_name }}
          </span>
          <span class="result-page">
            <i class="fas fa-file"></i>
            {{ translate('search.page') || 'עמוד' }} {{ result.page_number }}
          </span>
          <span class="result-line">
            <i class="fas fa-stream"></i>
            {{ translate('search.line') || 'שורה' }} {{ result.line_order }}
          </span>
          <span class="result-confidence" v-if="result.confidence">
            <i class="fas fa-check-circle"></i>
            {{ (result.confidence * 100).toFixed(0) }}%
          </span>
        </div>
        
        <div class="result-content">
          <!-- Highlighted content -->
          <div 
            v-if="result.highlight && result.highlight.length > 0"
            v-for="(snippet, idx) in result.highlight"
            :key="idx"
            class="result-snippet"
            v-html="snippet"
          ></div>
          <!-- Fallback to full content -->
          <div v-else class="result-snippet">
            {{ result.content }}
          </div>
        </div>
        
        <div class="result-actions">
          <button 
            class="btn btn-sm btn-outline-primary"
            @click.stop="goToResult(result)"
          >
            <i class="fas fa-external-link-alt"></i>
            {{ translate('search.openDocument') || 'פתח מסמך' }}
          </button>
        </div>
      </div>

      <!-- Pagination -->
      <div class="search-pagination" v-if="searchResults.total > pageSize">
        <button 
          class="btn btn-outline-secondary"
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          <i class="fas fa-chevron-right"></i>
          {{ translate('search.previous') || 'הקודם' }}
        </button>
        
        <span class="pagination-info">
          {{ translate('search.page') || 'עמוד' }} {{ currentPage }} {{ translate('search.of') || 'מתוך' }} {{ totalPages }}
        </span>
        
        <button 
          class="btn btn-outline-secondary"
          :disabled="currentPage >= totalPages"
          @click="changePage(currentPage + 1)"
        >
          {{ translate('search.next') || 'הבא' }}
          <i class="fas fa-chevron-left"></i>
        </button>
      </div>
    </div>

    <!-- Elasticsearch Stats (Debug) -->
    <div class="search-debug" v-if="showDebug && esStats">
      <details>
        <summary>📊 Elasticsearch Stats</summary>
        <pre>{{ JSON.stringify(esStats, null, 2) }}</pre>
      </details>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchPanel',
  
  data() {
    return {
      searchQuery: '',
      searchResults: null,
      isSearching: false,
      searchError: null,
      showFilters: false,
      filters: {
        document: null,
        project: null,
        minConfidence: null
      },
      currentPage: 1,
      pageSize: 20,
      debounceTimer: null,
      esStats: null,
      showDebug: false, // Set to true for development
      isRTL: document.dir === 'rtl' || document.documentElement.lang === 'he'
    };
  },
  
  computed: {
    totalPages() {
      if (!this.searchResults) return 0;
      return Math.ceil(this.searchResults.total / this.pageSize);
    }
  },
  
  mounted() {
    // Load ES stats on mount
    this.loadESStats();
    
    // Load from URL query if present
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    if (query) {
      this.searchQuery = query;
      this.performSearch();
    }
  },
  
  methods: {
    async loadESStats() {
      try {
        const response = await fetch('/api/search/stats/');
        if (response.ok) {
          this.esStats = await response.json();
        }
      } catch (error) {
        console.error('Failed to load ES stats:', error);
      }
    },
    
    debounceSearch() {
      // Auto-search after 500ms of no typing
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        if (this.searchQuery.length >= 2) {
          this.performSearch();
        }
      }, 500);
    },
    
    async performSearch() {
      if (!this.searchQuery || this.searchQuery.length < 2) {
        this.searchError = this.translate('search.minLength') || 'הזן לפחות 2 תווים לחיפוש';
        return;
      }
      
      this.isSearching = true;
      this.searchError = null;
      
      try {
        // Build query params
        const params = new URLSearchParams({
          q: this.searchQuery,
          page: this.currentPage,
          page_size: this.pageSize
        });
        
        if (this.filters.document) {
          params.append('document', this.filters.document);
        }
        if (this.filters.project) {
          params.append('project', this.filters.project);
        }
        if (this.filters.minConfidence) {
          params.append('min_confidence', this.filters.minConfidence);
        }
        
        // Fetch results
        const response = await fetch(`/api/search/?${params}`);
        
        if (!response.ok) {
          throw new Error(`Search failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
          this.searchError = data.error;
          this.searchResults = null;
        } else {
          this.searchResults = data;
          
          // Update URL
          const newUrl = new URL(window.location);
          newUrl.searchParams.set('q', this.searchQuery);
          window.history.pushState({}, '', newUrl);
        }
      } catch (error) {
        console.error('Search error:', error);
        this.searchError = this.translate('search.error') || 'שגיאה בחיפוש. נסה שוב.';
        this.searchResults = null;
      } finally {
        this.isSearching = false;
      }
    },
    
    changePage(page) {
      this.currentPage = page;
      this.performSearch();
      
      // Scroll to top
      this.$el.scrollIntoView({ behavior: 'smooth' });
    },
    
    goToResult(result) {
      // Navigate to document editor with the specific line
      const url = `/document/${result.document_id}/part/${result.document_part_id}/edit/#line-${result.line_id}`;
      window.location.href = url;
    }
  }
};
</script>

<style scoped>
.search-panel {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.search-panel.rtl {
  direction: rtl;
  text-align: right;
}

.search-header h3 {
  margin-bottom: 20px;
  color: #333;
}

.search-input-group {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.search-input {
  flex: 1;
  font-size: 16px;
  padding: 10px 15px;
  border: 2px solid #ddd;
  border-radius: 4px;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #007bff;
  outline: none;
}

.search-btn {
  padding: 10px 20px;
  white-space: nowrap;
}

.search-filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.filter-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  font-size: 14px;
}

.toggle-filters {
  padding: 5px 10px;
  font-size: 14px;
}

.search-stats {
  margin-bottom: 20px;
  padding: 10px;
  background: #e9ecef;
  border-radius: 4px;
}

.results-count {
  font-size: 14px;
}

.search-time {
  margin-left: 10px;
  color: #6c757d;
  font-size: 12px;
}

.search-loading {
  text-align: center;
  padding: 40px;
}

.search-error {
  margin-top: 20px;
}

.search-no-results {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.search-no-results i {
  font-size: 48px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.search-results {
  margin-top: 20px;
}

.search-result-item {
  padding: 20px;
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  transition: all 0.3s;
  cursor: pointer;
}

.search-result-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0,123,255,0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.result-document {
  margin: 0;
  font-size: 18px;
  color: #007bff;
}

.result-score {
  padding: 4px 8px;
  background: #ffc107;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.result-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 10px;
  font-size: 14px;
  color: #6c757d;
}

.result-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.result-content {
  margin: 15px 0;
}

.result-snippet {
  padding: 10px;
  background: #f8f9fa;
  border-left: 3px solid #007bff;
  margin-bottom: 5px;
  line-height: 1.6;
}

.result-snippet >>> mark {
  background: #ffeb3b;
  padding: 2px 4px;
  border-radius: 2px;
  font-weight: 600;
}

.result-actions {
  margin-top: 10px;
}

.search-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
  padding: 20px;
}

.pagination-info {
  font-size: 14px;
  color: #6c757d;
}

.search-debug {
  margin-top: 30px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.search-debug pre {
  margin: 10px 0 0 0;
  font-size: 12px;
  max-height: 300px;
  overflow: auto;
}

/* RTL specific adjustments */
.rtl .result-snippet {
  border-left: none;
  border-right: 3px solid #007bff;
}

.rtl .search-time {
  margin-left: 0;
  margin-right: 10px;
}
</style>
