<template>
  <div class="analysis-table-container">
    <h3>{{ translate('cerberus.dashboard.recentAnalyses') || 'Recent Analyses' }}</h3>
    
    <div v-if="loading" class="loading">
      <span class="spinner"></span>
      {{ translate('cerberus.analyzing') || 'Loading...' }}
    </div>
    
    <table v-else class="analysis-table">
      <thead>
        <tr>
          <th>{{ translate('cerberus.dashboard.date') || 'Date' }}</th>
          <th>{{ translate('cerberus.dashboard.document') || 'Document' }}</th>
          <th>{{ translate('cerberus.characterErrorRate') || 'CER' }}</th>
          <th>{{ translate('cerberus.dashboard.accuracy') || 'Accuracy' }}</th>
          <th>{{ translate('cerberus.dashboard.errors') || 'Total Errors' }}</th>
          <th>{{ translate('cerberus.dashboard.action') || 'Action' }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="analysis in analyses" :key="analysis.id" class="analysis-row">
          <td>{{ formatDate(analysis.created_at) }}</td>
          <td>{{ analysis.document_name }}</td>
          <td>
            <span :class="['cer-badge', getCERClass(analysis.cer)]">
              {{ analysis.cer.toFixed(2) }}%
            </span>
          </td>
          <td>
            <span :class="['accuracy-badge', getAccuracyClass(analysis.accuracy)]">
              {{ analysis.accuracy.toFixed(2) }}%
            </span>
          </td>
          <td>{{ analysis.errors }}</td>
          <td>
            <button @click="viewDetails(analysis.id)" class="btn-view">
              👁️ {{ translate('cerberus.dashboard.view') || 'View' }}
            </button>
          </td>
        </tr>
        <tr v-if="analyses.length === 0">
          <td colspan="6" class="empty-message">
            {{ translate('cerberus.dashboard.noAnalyses') || 'No analyses found' }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'CERAnalysisTable',
  props: {
    analyses: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('he-IL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    getCERClass(cer) {
      if (cer <= 5) return 'excellent'
      if (cer <= 10) return 'good'
      if (cer <= 20) return 'fair'
      return 'poor'
    },
    
    getAccuracyClass(accuracy) {
      if (accuracy >= 95) return 'excellent'
      if (accuracy >= 90) return 'good'
      if (accuracy >= 80) return 'fair'
      return 'poor'
    },
    
    viewDetails(analysisId) {
      this.$emit('view-details', analysisId)
    }
  }
}
</script>

<style scoped>
.analysis-table-container {
  width: 100%;
}

.analysis-table-container h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #2c3e50;
  font-size: 1.3rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}

.spinner {
  display: inline-block;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.analysis-table {
  width: 100%;
  border-collapse: collapse;
}

.analysis-table thead {
  background-color: #ecf0f1;
  border-bottom: 2px solid #bdc3c7;
}

.analysis-table th {
  padding: 1rem;
  text-align: right;
  font-weight: 600;
  color: #2c3e50;
  direction: rtl;
}

.analysis-table td {
  padding: 1rem;
  border-bottom: 1px solid #ecf0f1;
  text-align: right;
}

.analysis-row:hover {
  background-color: #f5f7fa;
}

.empty-message {
  text-align: center;
  color: #7f8c8d;
  font-style: italic;
  padding: 2rem !important;
}

.cer-badge,
.accuracy-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.9rem;
}

.cer-badge.excellent,
.accuracy-badge.excellent {
  background-color: #d5f4e6;
  color: #27ae60;
}

.cer-badge.good,
.accuracy-badge.good {
  background-color: #d5eaf4;
  color: #2980b9;
}

.cer-badge.fair,
.accuracy-badge.fair {
  background-color: #fef5e7;
  color: #f39c12;
}

.cer-badge.poor,
.accuracy-badge.poor {
  background-color: #fadbd8;
  color: #e74c3c;
}

.btn-view {
  padding: 0.4rem 0.8rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.btn-view:hover {
  background-color: #2980b9;
}

@media (max-width: 768px) {
  .analysis-table {
    font-size: 0.9rem;
  }
  
  .analysis-table th,
  .analysis-table td {
    padding: 0.5rem;
  }
  
  .btn-view {
    padding: 0.3rem 0.6rem;
    font-size: 0.8rem;
  }
}
</style>
