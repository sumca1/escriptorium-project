<template>
  <div class="cer-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <h1>{{ translate('cerberus.dashboard.title') || 'CERberus Dashboard' }}</h1>
      <p class="subtitle">{{ translate('cerberus.dashboard.subtitle') || 'Monitor and analyze OCR quality' }}</p>
    </div>

    <!-- Stats Cards -->
    <div class="stats-cards-container">
      <CERStatsCard
        :title="translate('cerberus.dashboard.totalAnalyses') || 'Total Analyses'"
        :value="dashboardStats.total_analyses"
        icon="📊"
        color="#3498db"
      />
      <CERStatsCard
        :title="translate('cerberus.dashboard.avgCER') || 'Average CER'"
        :value="`${dashboardStats.avg_cer}%`"
        icon="📈"
        color="#e74c3c"
      />
      <CERStatsCard
        :title="translate('cerberus.dashboard.avgAccuracy') || 'Average Accuracy'"
        :value="`${dashboardStats.avg_accuracy}%`"
        icon="✅"
        color="#2ecc71"
      />
      <CERStatsCard
        :title="translate('cerberus.dashboard.problematicChars') || 'Problematic Characters'"
        :value="dashboardStats.problematic_chars ? dashboardStats.problematic_chars.length : 0"
        icon="⚠️"
        color="#f39c12"
      />
    </div>

    <!-- Filters -->
    <div class="dashboard-filters">
      <div class="filter-group">
        <label>{{ translate('cerberus.dashboard.filterByDocument') || 'Filter by Document' }}</label>
        <select v-model="selectedDocument" @change="onFilterChange">
          <option value="">{{ translate('cerberus.dashboard.allDocuments') || 'All Documents' }}</option>
          <option value="recent">{{ translate('cerberus.dashboard.recentOnly') || 'Recent Only' }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>{{ translate('cerberus.dashboard.timeRange') || 'Time Range' }}</label>
        <select v-model="selectedTimeRange" @change="onFilterChange">
          <option value="7">{{ translate('cerberus.dashboard.last7Days') || '7 Days' }}</option>
          <option value="30">{{ translate('cerberus.dashboard.last30Days') || '30 Days' }}</option>
          <option value="90">{{ translate('cerberus.dashboard.last90Days') || '90 Days' }}</option>
        </select>
      </div>
      <button @click="refreshData" class="btn-refresh">
        🔄 {{ translate('cerberus.dashboard.refresh') || 'Refresh' }}
      </button>
    </div>

    <!-- Tabs -->
    <div class="dashboard-tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        @click="activeTab = tab"
        :class="['tab-button', { active: activeTab === tab }]"
      >
        {{ translate(`cerberus.dashboard.tab${tab}`) || tab }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Analyses Table -->
      <div v-show="activeTab === 'Analyses'" class="tab-pane">
        <CERAnalysisTable
          :analyses="recentAnalyses"
          :loading="loading"
          @view-details="onViewAnalysis"
        />
      </div>

      <!-- Trends Chart -->
      <div v-show="activeTab === 'Trends'" class="tab-pane">
        <CERTrendsChart
          :trends="trendData"
          :model-comparison="modelComparison"
          :loading="loading"
        />
      </div>

      <!-- Confusions -->
      <div v-show="activeTab === 'TopConfusions'" class="tab-pane">
        <div class="confusions-container">
          <h3>{{ translate('cerberus.dashboard.topConfusions') || 'Top Character Confusions' }}</h3>
          <table class="confusions-table">
            <thead>
              <tr>
                <th>{{ translate('cerberus.dashboard.confusionPair') || 'Confusion Pair' }}</th>
                <th>{{ translate('cerberus.dashboard.count') || 'Count' }}</th>
                <th>{{ translate('cerberus.dashboard.percentage') || 'Percentage' }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(confusion, idx) in dashboardStats.top_confusions" :key="idx">
                <td><code>{{ confusion.pair }}</code></td>
                <td>{{ confusion.count }}</td>
                <td>{{ ((confusion.count / dashboardStats.total_analyses) * 100).toFixed(2) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Problematic Characters -->
      <div v-show="activeTab === 'ProblematicChars'" class="tab-pane">
        <div class="problematic-container">
          <h3>{{ translate('cerberus.dashboard.problematicCharactersDetail') || 'Characters with Lowest Accuracy' }}</h3>
          <table class="chars-table">
            <thead>
              <tr>
                <th>{{ translate('cerberus.dashboard.character') || 'Character' }}</th>
                <th>{{ translate('cerberus.dashboard.total') || 'Total' }}</th>
                <th>{{ translate('cerberus.dashboard.correct') || 'Correct' }}</th>
                <th>{{ translate('cerberus.dashboard.accuracy') || 'Accuracy' }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(char, idx) in dashboardStats.problematic_chars" :key="idx">
                <td class="char-display">{{ char.character }}</td>
                <td>{{ char.total }}</td>
                <td>{{ char.correct }}</td>
                <td :style="{ color: getAccuracyColor(char.accuracy) }">
                  {{ char.accuracy.toFixed(2) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>{{ translate('cerberus.analyzing') || 'Loading...' }}</p>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      ❌ {{ errorMessage }}
      <button @click="errorMessage = ''" class="btn-close">✕</button>
    </div>
  </div>
</template>

<script>
import CERStatsCard from './CERStatsCard.vue'
import CERAnalysisTable from './CERAnalysisTable.vue'
import CERTrendsChart from './CERTrendsChart.vue'

export default {
  name: 'CERDashboard',
  components: {
    CERStatsCard,
    CERAnalysisTable,
    CERTrendsChart
  },
  data() {
    return {
      activeTab: 'Analyses',
      tabs: ['Analyses', 'Trends', 'TopConfusions', 'ProblematicChars'],
      loading: false,
      errorMessage: '',
      selectedDocument: '',
      selectedTimeRange: '30',
      
      dashboardStats: {
        total_analyses: 0,
        avg_cer: 0,
        avg_accuracy: 0,
        top_confusions: [],
        problematic_chars: []
      },
      recentAnalyses: [],
      trendData: [],
      modelComparison: {}
    }
  },
  computed: {
    apiBaseUrl() {
      return window.API_BASE_URL || '/api'
    }
  },
  mounted() {
    this.loadDashboardData()
    // Auto-refresh every 5 minutes
    setInterval(() => this.loadDashboardData(), 5 * 60 * 1000)
  },
  methods: {
    async loadDashboardData() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        // Load stats
        const statsRes = await fetch(`${this.apiBaseUrl}/cerberus/analyses/dashboard-stats/`)
        if (!statsRes.ok) throw new Error('Failed to load stats')
        this.dashboardStats = await statsRes.json()
        
        // Load recent analyses
        const recentRes = await fetch(`${this.apiBaseUrl}/cerberus/analyses/recent-analyses/?limit=10`)
        if (!recentRes.ok) throw new Error('Failed to load recent analyses')
        this.recentAnalyses = await recentRes.json()
        
        // Load trends
        const trendsRes = await fetch(`${this.apiBaseUrl}/cerberus/analyses/dashboard-trends/?days=${this.selectedTimeRange}`)
        if (!trendsRes.ok) throw new Error('Failed to load trends')
        const trendsData = await trendsRes.json()
        this.trendData = trendsData.trends
        this.modelComparison = trendsData.model_comparison
      } catch (error) {
        console.error('Dashboard error:', error)
        this.errorMessage = error.message || 'Failed to load dashboard data'
      } finally {
        this.loading = false
      }
    },
    
    onFilterChange() {
      this.loadDashboardData()
    },
    
    refreshData() {
      this.loadDashboardData()
    },
    
    onViewAnalysis(analysisId) {
      // Navigate to analysis detail page
      window.location.href = `/cerberus/analysis/${analysisId}/`
    },
    
    getAccuracyColor(accuracy) {
      if (accuracy >= 90) return '#2ecc71'
      if (accuracy >= 70) return '#f39c12'
      return '#e74c3c'
    }
  }
}
</script>

<style scoped>
.cer-dashboard {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
  direction: rtl;
}

.dashboard-header {
  margin-bottom: 2rem;
  border-bottom: 2px solid #3498db;
  padding-bottom: 1rem;
}

.dashboard-header h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 2rem;
}

.subtitle {
  color: #7f8c8d;
  margin: 0.5rem 0 0 0;
}

.stats-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.dashboard-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.filter-group select {
  padding: 0.5rem 1rem;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
}

.btn-refresh {
  padding: 0.5rem 1.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s;
}

.btn-refresh:hover {
  background-color: #2980b9;
}

.dashboard-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #ecf0f1;
  flex-wrap: wrap;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  color: #7f8c8d;
  font-weight: 600;
  transition: all 0.3s;
}

.tab-button.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.tab-button:hover {
  color: #2c3e50;
}

.tab-content {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-pane {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.confusions-container,
.problematic-container {
  width: 100%;
}

.confusions-table,
.chars-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.confusions-table thead,
.chars-table thead {
  background-color: #ecf0f1;
}

.confusions-table th,
.chars-table th {
  padding: 1rem;
  text-align: right;
  font-weight: 600;
  color: #2c3e50;
}

.confusions-table td,
.chars-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #ecf0f1;
}

.confusions-table tbody tr:hover,
.chars-table tbody tr:hover {
  background-color: #f5f7fa;
}

.char-display {
  font-family: monospace;
  font-size: 1.2rem;
  font-weight: bold;
  color: #3498db;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay p {
  color: white;
  margin-top: 1rem;
  font-size: 1.1rem;
}

.error-message {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background-color: #e74c3c;
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 1rem;
  z-index: 999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-close {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1.2rem;
}

@media (max-width: 768px) {
  .cer-dashboard {
    padding: 1rem;
  }
  
  .stats-cards-container {
    grid-template-columns: 1fr;
  }
  
  .dashboard-tabs {
    flex-wrap: wrap;
  }
  
  .tab-content {
    padding: 1rem;
  }
}
</style>
