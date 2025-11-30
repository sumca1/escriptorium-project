<template>
  <div class="trends-chart-container">
    <h3>{{ translate('cerberus.dashboard.trendsTitle') || 'CER Trends Over Time' }}</h3>
    
    <div v-if="loading" class="loading">
      <span class="spinner"></span>
      {{ translate('cerberus.analyzing') || 'Loading...' }}
    </div>
    
    <div v-else class="charts-grid">
      <!-- CER Trend Line Chart -->
      <div class="chart-box">
        <h4>{{ translate('cerberus.dashboard.cerTrend') || 'CER Trend' }}</h4>
        <canvas id="cer-trend-chart"></canvas>
      </div>
      
      <!-- Model Comparison Bar Chart -->
      <div class="chart-box">
        <h4>{{ translate('cerberus.dashboard.modelComparison') || 'Model Comparison' }}</h4>
        <canvas id="model-comparison-chart"></canvas>
      </div>
      
      <!-- Model Statistics Table -->
      <div class="model-stats">
        <h4>{{ translate('cerberus.dashboard.modelStatistics') || 'Model Statistics' }}</h4>
        <table class="stats-table">
          <thead>
            <tr>
              <th>{{ translate('cerberus.dashboard.modelName') || 'Model Name' }}</th>
              <th>{{ translate('cerberus.dashboard.analyses') || 'Analyses' }}</th>
              <th>{{ translate('cerberus.dashboard.avgCER') || 'Avg CER' }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(stats, model) in modelComparison" :key="model">
              <td>{{ model }}</td>
              <td>{{ stats.analyses }}</td>
              <td>
                <span :class="['cer-badge', getCERClass(stats.avg_cer)]">
                  {{ stats.avg_cer }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CERTrendsChart',
  props: {
    trends: {
      type: Array,
      default: () => []
    },
    modelComparison: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  mounted() {
    this.$nextTick(() => {
      if (this.trends.length > 0) {
        this.renderCharts()
      }
    })
  },
  watch: {
    trends() {
      this.$nextTick(() => {
        if (this.trends.length > 0) {
          this.renderCharts()
        }
      })
    }
  },
  methods: {
    renderCharts() {
      // Load Chart.js if not already loaded
      if (typeof Chart === 'undefined') {
        this.loadChartJS()
      } else {
        this.drawCharts()
      }
    },
    
    loadChartJS() {
      const script = document.createElement('script')
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js'
      script.onload = () => this.drawCharts()
      document.head.appendChild(script)
    },
    
    drawCharts() {
      this.drawCERTrendChart()
      this.drawModelComparisonChart()
    },
    
    drawCERTrendChart() {
      const ctx = document.getElementById('cer-trend-chart')
      if (!ctx) return
      
      const dates = this.trends.map(t => t.date)
      const cers = this.trends.map(t => t.cer)
      const accuracies = this.trends.map(t => t.accuracy)
      
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: dates,
          datasets: [
            {
              label: this.translate('cerberus.characterErrorRate') || 'CER',
              data: cers,
              borderColor: '#e74c3c',
              backgroundColor: 'rgba(231, 76, 60, 0.1)',
              borderWidth: 2,
              tension: 0.4,
              fill: true,
              yAxisID: 'y'
            },
            {
              label: this.translate('cerberus.dashboard.accuracy') || 'Accuracy',
              data: accuracies,
              borderColor: '#2ecc71',
              backgroundColor: 'rgba(46, 204, 113, 0.1)',
              borderWidth: 2,
              tension: 0.4,
              fill: true,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          interaction: {
            mode: 'index',
            intersect: false
          },
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              title: {
                display: true,
                text: this.translate('cerberus.characterErrorRate') || 'CER (%)'
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              title: {
                display: true,
                text: this.translate('cerberus.dashboard.accuracy') || 'Accuracy (%)'
              }
            }
          },
          plugins: {
            legend: {
              position: 'top'
            }
          }
        }
      })
    },
    
    drawModelComparisonChart() {
      const ctx = document.getElementById('model-comparison-chart')
      if (!ctx) return
      
      const models = Object.keys(this.modelComparison)
      const cers = models.map(m => this.modelComparison[m].avg_cer)
      
      const colors = [
        '#3498db',
        '#e74c3c',
        '#2ecc71',
        '#f39c12',
        '#9b59b6',
        '#1abc9c',
        '#34495e',
        '#e67e22'
      ]
      
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: models,
          datasets: [
            {
              label: this.translate('cerberus.characterErrorRate') || 'CER',
              data: cers,
              backgroundColor: colors.slice(0, models.length),
              borderColor: colors.slice(0, models.length),
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: this.translate('cerberus.characterErrorRate') || 'CER (%)'
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    },
    
    getCERClass(cer) {
      if (cer <= 5) return 'excellent'
      if (cer <= 10) return 'good'
      if (cer <= 20) return 'fair'
      return 'poor'
    }
  }
}
</script>

<style scoped>
.trends-chart-container {
  width: 100%;
}

.trends-chart-container h3 {
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

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-box {
  background-color: #f5f7fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #ecf0f1;
}

.chart-box h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.model-stats {
  grid-column: 1 / -1;
  background-color: #f5f7fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #ecf0f1;
}

.model-stats h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
}

.stats-table thead {
  background-color: white;
  border-bottom: 2px solid #bdc3c7;
}

.stats-table th {
  padding: 1rem;
  text-align: right;
  font-weight: 600;
  color: #2c3e50;
}

.stats-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #ecf0f1;
  text-align: right;
}

.stats-table tbody tr:hover {
  background-color: white;
}

.cer-badge {
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.85rem;
}

.cer-badge.excellent {
  background-color: #d5f4e6;
  color: #27ae60;
}

.cer-badge.good {
  background-color: #d5eaf4;
  color: #2980b9;
}

.cer-badge.fair {
  background-color: #fef5e7;
  color: #f39c12;
}

.cer-badge.poor {
  background-color: #fadbd8;
  color: #e74c3c;
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
