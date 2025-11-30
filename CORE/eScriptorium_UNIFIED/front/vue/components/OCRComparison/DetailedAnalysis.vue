<template>
  <div class="detailed-analysis">
    <!-- Error Types Comparison -->
    <div class="row mb-4">
      <div class="col-12">
        <h6 class="section-title">
          <i class="fas fa-microscope"></i>
          {{ translate('errorTypesBreakdown') }}
        </h6>
      </div>
    </div>

    <div class="row">
      <!-- Transcription 1 Analysis -->
      <div class="col-md-6">
        <div class="analysis-card">
          <div class="card-header bg-info text-white">
            <strong>{{ trans1.name }}</strong>
          </div>
          <div class="card-body">
            <error-breakdown-chart :analysis="analysis1" />
          </div>
        </div>
      </div>

      <!-- Transcription 2 Analysis -->
      <div class="col-md-6">
        <div class="analysis-card">
          <div class="card-header bg-success text-white">
            <strong>{{ trans2.name }}</strong>
          </div>
          <div class="card-body">
            <error-breakdown-chart :analysis="analysis2" />
          </div>
        </div>
      </div>
    </div>

    <!-- Side-by-Side Comparison Table -->
    <div class="row mt-4">
      <div class="col-12">
        <h6 class="section-title">
          <i class="fas fa-table"></i>
          {{ translate('detailedComparison') }}
        </h6>
        <div class="table-responsive">
          <table class="table table-bordered table-hover">
            <thead class="table-light">
              <tr>
                <th>{{ translate('metric') }}</th>
                <th class="text-center">{{ trans1.name }}</th>
                <th class="text-center">{{ trans2.name }}</th>
                <th class="text-center">{{ translate('difference') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>{{ translate('correct') }}</strong></td>
                <td class="text-center">{{ analysis1.correct }}</td>
                <td class="text-center">{{ analysis2.correct }}</td>
                <td class="text-center" :class="getDiffClass(analysis1.correct, analysis2.correct, true)">
                  {{ getDiff(analysis1.correct, analysis2.correct) }}
                </td>
              </tr>
              <tr>
                <td><strong>{{ translate('substitutions') }}</strong></td>
                <td class="text-center">{{ analysis1.substitutions }}</td>
                <td class="text-center">{{ analysis2.substitutions }}</td>
                <td class="text-center" :class="getDiffClass(analysis1.substitutions, analysis2.substitutions, false)">
                  {{ getDiff(analysis1.substitutions, analysis2.substitutions) }}
                </td>
              </tr>
              <tr>
                <td><strong>{{ translate('insertions') }}</strong></td>
                <td class="text-center">{{ analysis1.insertions }}</td>
                <td class="text-center">{{ analysis2.insertions }}</td>
                <td class="text-center" :class="getDiffClass(analysis1.insertions, analysis2.insertions, false)">
                  {{ getDiff(analysis1.insertions, analysis2.insertions) }}
                </td>
              </tr>
              <tr>
                <td><strong>{{ translate('deletions') }}</strong></td>
                <td class="text-center">{{ analysis1.deletions }}</td>
                <td class="text-center">{{ analysis2.deletions }}</td>
                <td class="text-center" :class="getDiffClass(analysis1.deletions, analysis2.deletions, false)">
                  {{ getDiff(analysis1.deletions, analysis2.deletions) }}
                </td>
              </tr>
              <tr class="table-active">
                <td><strong>{{ translate('totalErrors') }}</strong></td>
                <td class="text-center">
                  <strong>{{ getTotalErrors(analysis1) }}</strong>
                </td>
                <td class="text-center">
                  <strong>{{ getTotalErrors(analysis2) }}</strong>
                </td>
                <td class="text-center" :class="getDiffClass(getTotalErrors(analysis1), getTotalErrors(analysis2), false)">
                  <strong>{{ getDiff(getTotalErrors(analysis1), getTotalErrors(analysis2)) }}</strong>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ErrorBreakdownChart from './ErrorBreakdownChart.vue'

export default {
  name: 'DetailedAnalysis',
  
  components: {
    ErrorBreakdownChart,
  },
  
  props: {
    analysis1: {
      type: Object,
      required: true,
    },
    analysis2: {
      type: Object,
      required: true,
    },
    trans1: {
      type: Object,
      required: true,
    },
    trans2: {
      type: Object,
      required: true,
    },
  },
  
  methods: {
    translate(key) {
      return window.COMPARISON_TRANSLATIONS?.[key] || key
    },
    
    getTotalErrors(analysis) {
      return analysis.substitutions + analysis.insertions + analysis.deletions
    },
    
    getDiff(val1, val2) {
      const diff = val1 - val2
      if (diff === 0) return '='
      if (diff > 0) return `+${diff}`
      return `${diff}`
    },
    
    getDiffClass(val1, val2, higherIsBetter) {
      if (val1 === val2) return 'text-muted'
      
      if (higherIsBetter) {
        return val1 > val2 ? 'text-success' : 'text-danger'
      } else {
        return val1 < val2 ? 'text-success' : 'text-danger'
      }
    },
  },
}
</script>

<style scoped>
.detailed-analysis {
  padding: 1rem 0;
}

.section-title {
  font-weight: 600;
  color: #2c3e50;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #007bff;
  margin-bottom: 1rem;
}

.analysis-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  height: 100%;
}

.analysis-card .card-header {
  padding: 0.75rem 1rem;
}

.analysis-card .card-body {
  padding: 1.5rem;
}

.table {
  margin-bottom: 0;
}

.table th {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.table td {
  vertical-align: middle;
}

.table-hover tbody tr:hover {
  background-color: #f8f9fa;
}
</style>
