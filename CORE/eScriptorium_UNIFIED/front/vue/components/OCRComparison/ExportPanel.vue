<template>
  <div class="export-panel">
    <div class="export-options">
      <!-- Export as JSON -->
      <div class="export-option-card">
        <div class="export-icon">
          <i class="fas fa-file-code fa-3x text-primary"></i>
        </div>
        <h6>{{ translate('exportJSON') }}</h6>
        <p class="text-muted small">
          {{ translate('fullDataStructure') }}
        </p>
        <button @click="exportJSON" class="btn btn-primary w-100">
          <i class="fas fa-download"></i>
          {{ translate('downloadJSON') }}
        </button>
      </div>

      <!-- Export as CSV -->
      <div class="export-option-card">
        <div class="export-icon">
          <i class="fas fa-file-csv fa-3x text-success"></i>
        </div>
        <h6>{{ translate('exportCSV') }}</h6>
        <p class="text-muted small">
          {{ translate('forExcelAnalysis') }}
        </p>
        <button @click="exportCSV" class="btn btn-success w-100">
          <i class="fas fa-download"></i>
          {{ translate('downloadCSV') }}
        </button>
      </div>

      <!-- Export as Text Report -->
      <div class="export-option-card">
        <div class="export-icon">
          <i class="fas fa-file-alt fa-3x text-info"></i>
        </div>
        <h6>{{ translate('exportReport') }}</h6>
        <p class="text-muted small">
          {{ translate('humanReadableReport') }}
        </p>
        <button @click="exportReport" class="btn btn-info w-100">
          <i class="fas fa-download"></i>
          {{ translate('downloadReport') }}
        </button>
      </div>
    </div>

    <!-- Export Preview -->
    <div v-if="exportPreview" class="export-preview mt-4">
      <h6>{{ translate('preview') }}</h6>
      <pre class="preview-content">{{ exportPreview }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExportPanel',
  
  props: {
    comparisonResult: {
      type: Object,
      required: true,
    },
    documentName: {
      type: String,
      required: true,
    },
  },
  
  data() {
    return {
      exportPreview: '',
    }
  },
  
  methods: {
    translate(key) {
      return window.COMPARISON_TRANSLATIONS?.[key] || key
    },
    
    exportJSON() {
      const data = JSON.stringify(this.comparisonResult, null, 2)
      this.download(data, `comparison-${this.getTimestamp()}.json`, 'application/json')
    },
    
    exportCSV() {
      const csv = this.generateCSV()
      this.download(csv, `comparison-${this.getTimestamp()}.csv`, 'text/csv;charset=utf-8')
    },
    
    exportReport() {
      const report = this.generateTextReport()
      this.download(report, `comparison-report-${this.getTimestamp()}.txt`, 'text/plain;charset=utf-8')
    },
    
    generateCSV() {
      const result = this.comparisonResult
      let csv = '\uFEFF' // UTF-8 BOM for Excel
      
      // Header
      csv += 'Metric,Transcription 1,Transcription 2,Difference\n'
      
      // Basic info
      csv += `Document,"${this.documentName}","${this.documentName}",\n`
      csv += `Transcription Name,"${result.transcription_1.name}","${result.transcription_2.name}",\n`
      csv += `Model,"${result.transcription_1.model}","${result.transcription_2.model}",\n`
      csv += `Text Length,${result.transcription_1.text_length},${result.transcription_2.text_length},\n`
      
      if (result.metrics) {
        csv += `\nMetrics,,,\n`
        csv += `CER,%${result.metrics.cer_1},%${result.metrics.cer_2},${result.metrics.cer_difference}\n`
        csv += `Accuracy,%${result.metrics.accuracy_1},%${result.metrics.accuracy_2},\n`
        csv += `WER,%${result.metrics.wer_1},%${result.metrics.wer_2},\n`
        
        csv += `\nError Breakdown,,,\n`
        csv += `Substitutions,${result.detailed_analysis_1.substitutions},${result.detailed_analysis_2.substitutions},\n`
        csv += `Insertions,${result.detailed_analysis_1.insertions},${result.detailed_analysis_2.insertions},\n`
        csv += `Deletions,${result.detailed_analysis_1.deletions},${result.detailed_analysis_2.deletions},\n`
        csv += `Correct,${result.detailed_analysis_1.correct},${result.detailed_analysis_2.correct},\n`
      }
      
      return csv
    },
    
    generateTextReport() {
      const result = this.comparisonResult
      let report = '═══════════════════════════════════════════════════\n'
      report += '         OCR COMPARISON REPORT\n'
      report += '═══════════════════════════════════════════════════\n\n'
      
      report += `Document: ${this.documentName}\n`
      report += `Generated: ${new Date().toLocaleString()}\n`
      report += `Comparison ID: ${result.comparison_id}\n\n`
      
      report += '─────────────────────────────────────────────────────\n'
      report += 'TRANSCRIPTION 1 (A)\n'
      report += '─────────────────────────────────────────────────────\n'
      report += `Name: ${result.transcription_1.name}\n`
      report += `Model: ${result.transcription_1.model}\n`
      report += `Text Length: ${result.transcription_1.text_length} characters\n`
      report += `Created: ${result.transcription_1.created_at}\n\n`
      
      report += '─────────────────────────────────────────────────────\n'
      report += 'TRANSCRIPTION 2 (B)\n'
      report += '─────────────────────────────────────────────────────\n'
      report += `Name: ${result.transcription_2.name}\n`
      report += `Model: ${result.transcription_2.model}\n`
      report += `Text Length: ${result.transcription_2.text_length} characters\n`
      report += `Created: ${result.transcription_2.created_at}\n\n`
      
      if (result.metrics) {
        report += '═══════════════════════════════════════════════════\n'
        report += '                  METRICS\n'
        report += '═══════════════════════════════════════════════════\n\n'
        
        if (result.ground_truth) {
          report += `Ground Truth: ${result.ground_truth.name}\n\n`
        }
        
        report += 'Character Error Rate (CER):\n'
        report += `  Transcription 1: ${result.metrics.cer_1.toFixed(2)}%\n`
        report += `  Transcription 2: ${result.metrics.cer_2.toFixed(2)}%\n`
        report += `  Difference: ${result.metrics.cer_difference.toFixed(2)}%\n\n`
        
        report += 'Accuracy:\n'
        report += `  Transcription 1: ${result.metrics.accuracy_1.toFixed(2)}%\n`
        report += `  Transcription 2: ${result.metrics.accuracy_2.toFixed(2)}%\n\n`
        
        report += 'Word Error Rate (WER):\n'
        report += `  Transcription 1: ${result.metrics.wer_1.toFixed(2)}%\n`
        report += `  Transcription 2: ${result.metrics.wer_2.toFixed(2)}%\n\n`
        
        report += '─────────────────────────────────────────────────────\n'
        report += 'ERROR BREAKDOWN\n'
        report += '─────────────────────────────────────────────────────\n\n'
        
        report += 'Transcription 1:\n'
        report += `  Correct: ${result.detailed_analysis_1.correct}\n`
        report += `  Substitutions: ${result.detailed_analysis_1.substitutions}\n`
        report += `  Insertions: ${result.detailed_analysis_1.insertions}\n`
        report += `  Deletions: ${result.detailed_analysis_1.deletions}\n\n`
        
        report += 'Transcription 2:\n'
        report += `  Correct: ${result.detailed_analysis_2.correct}\n`
        report += `  Substitutions: ${result.detailed_analysis_2.substitutions}\n`
        report += `  Insertions: ${result.detailed_analysis_2.insertions}\n`
        report += `  Deletions: ${result.detailed_analysis_2.deletions}\n\n`
        
        report += '─────────────────────────────────────────────────────\n'
        report += 'WINNER\n'
        report += '─────────────────────────────────────────────────────\n\n'
        
        const winner = result.metrics.winner === 'transcription_1' 
          ? result.transcription_1.name 
          : result.transcription_2.name
        report += `🏆 ${winner}\n`
        report += `(Better by ${result.metrics.cer_difference.toFixed(2)}% CER)\n\n`
      }
      
      report += '═══════════════════════════════════════════════════\n'
      report += '                END OF REPORT\n'
      report += '═══════════════════════════════════════════════════\n'
      
      return report
    },
    
    download(content, filename, mimeType) {
      const blob = new Blob([content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      URL.revokeObjectURL(url)
    },
    
    getTimestamp() {
      return new Date().toISOString().split('T')[0]
    },
  },
}
</script>

<style scoped>
.export-panel {
  padding: 1rem;
}

.export-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.export-option-card {
  padding: 1.5rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  text-align: center;
  background: white;
  transition: all 0.3s;
}

.export-option-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
  border-color: #007bff;
}

.export-icon {
  margin-bottom: 1rem;
}

.export-option-card h6 {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.export-preview {
  padding: 1.5rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
}

.preview-content {
  background: white;
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 0.85rem;
  direction: ltr;
  text-align: left;
}
</style>
