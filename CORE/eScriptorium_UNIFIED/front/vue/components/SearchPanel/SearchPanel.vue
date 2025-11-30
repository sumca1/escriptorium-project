<template>
  <div class="search-panel" :class="{ 'rtl': isRTL }">
    <!-- Legacy Simple Search (shown when data prop exists) -->
    <div v-if="data && data.searchScope" class="legacy-search-form">
      <form method="get" action="/search/">
        <input v-if="data.projectId" name="project" type="text" :value="data.projectId" hidden>
        <input v-if="data.documentId" name="document" type="text" :value="data.documentId" hidden>
        
        <div class="escr-search-form">
          <h3>{{ translate('search_text_in') }} {{ data.searchScope }}</h3>
          <label class="escr-text-field escr-form-field">
            <input
              type="text"
              :placeholder="translate('Text to search')"
              :aria-label="translate('Search')"
              :disabled="data.disabled"
              name="query"
            >
            <span class="escr-help-text">
              Surround one or more terms with quotation marks to deactivate fuzziness.
            </span>
          </label>
        </div>
        <EscrButton
          :disabled="data.disabled"
          :on-click="data.onSearch || (() => {})"
          :label="translate('Search')"
          color="primary"
          type="submit"
        />
      </form>
    </div>

    <!-- Advanced Elasticsearch Search (shown when no data prop) -->
    <div v-else class="advanced-search">
      <!-- Search Input -->
      <div class="search-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3 style="margin: 0;">{{ translate('search.title') || 'חיפוש מתקדם' }}</h3>
        <HelpButton topic="search" />
      </div>
      <div class="search-controls">
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
            </select>
          </div>
          
          <div class="filter-group">
            <label>{{ translate('search.filters.project') || 'פרויקט' }}:</label>
            <select v-model="filters.project" class="form-control">
              <option :value="null">{{ translate('search.filters.all') || 'הכל' }}</option>
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
            <div 
              v-if="result.highlight && result.highlight.length > 0"
              v-for="(snippet, idx) in result.highlight"
              :key="idx"
              class="result-snippet"
              v-html="snippet"
            ></div>
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
  </div>
</template>

<script>
import EscrButton from "../Button/Button.vue";
import HelpButton from "../HelpButton/HelpButton.vue";
import "./SearchPanel.css";

export default {
  name: 'EscrSearchPanel',
  components: { 
    EscrButton,
    HelpButton
  },
  props: {
    /**
     * Legacy prop: Data for the simple search panel. When present, shows legacy form.
     * When null/undefined, shows advanced Elasticsearch search.
     */
    data: {
      type: Object,
      required: false,
      default: null
    }
  },
  
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
      showDebug: false,
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
    // Only load advanced search if no data prop (legacy mode)
    if (!this.data) {
      this.loadESStats();
      
      const urlParams = new URLSearchParams(window.location.search);
      const query = urlParams.get('q');
      if (query) {
        this.searchQuery = query;
        this.performSearch();
      }
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
        const params = new URLSearchParams({
          q: this.searchQuery,
          page: this.currentPage,
          page_size: this.pageSize
        });
        
        if (this.filters.document) params.append('document', this.filters.document);
        if (this.filters.project) params.append('project', this.filters.project);
        if (this.filters.minConfidence) params.append('min_confidence', this.filters.minConfidence);
        
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
      this.$el.scrollIntoView({ behavior: 'smooth' });
    },
    
    goToResult(result) {
      const url = `/document/${result.document_id}/part/${result.document_part_id}/edit/#line-${result.line_id}`;
      window.location.href = url;
    }
  }
};
</script>
