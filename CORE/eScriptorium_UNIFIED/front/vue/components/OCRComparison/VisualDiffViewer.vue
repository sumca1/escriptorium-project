<template>
  <div class="visual-diff-viewer">
    <!-- Summary Stats -->
    <div class="diff-summary mb-4">
      <div class="row text-center">
        <div class="col-md-3">
          <div class="stat-box">
            <i class="fas fa-check-circle text-success"></i>
            <div class="stat-value">{{ summary.correct }}</div>
            <div class="stat-label">{{ translate('correct') }}</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-box">
            <i class="fas fa-exchange-alt text-primary"></i>
            <div class="stat-value">{{ summary.substitutions }}</div>
            <div class="stat-label">{{ translate('substitutions') }}</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-box">
            <i class="fas fa-plus-circle text-info"></i>
            <div class="stat-value">{{ summary.insertions }}</div>
            <div class="stat-label">{{ translate('insertions') }}</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-box">
            <i class="fas fa-minus-circle text-danger"></i>
            <div class="stat-value">{{ summary.deletions }}</div>
            <div class="stat-label">{{ translate('deletions') }}</div>
          </div>
        </div>
      </div>
      
      <div class="accuracy-bar mt-3">
        <div class="progress" style="height: 30px;">
          <div 
            class="progress-bar" 
            :class="getAccuracyClass()"
            :style="{ width: summary.accuracy + '%' }"
            role="progressbar"
          >
            <strong>{{ summary.accuracy.toFixed(2) }}% {{ translate('accuracy') }}</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- View Controls -->
    <div class="view-controls mb-3">
      <div class="btn-group" role="group">
        <button 
          @click="viewMode = 'split'" 
          class="btn btn-sm"
          :class="viewMode === 'split' ? 'btn-primary' : 'btn-outline-primary'"
        >
          <i class="fas fa-columns"></i>
          {{ translate('splitView') }}
        </button>
        <button 
          @click="viewMode = 'unified'" 
          class="btn btn-sm"
          :class="viewMode === 'unified' ? 'btn-primary' : 'btn-outline-primary'"
        >
          <i class="fas fa-align-justify"></i>
          {{ translate('unifiedView') }}
        </button>
      </div>
      
      <div class="btn-group ms-3" role="group">
        <button 
          @click="highlightMode = 'all'" 
          class="btn btn-sm"
          :class="highlightMode === 'all' ? 'btn-secondary' : 'btn-outline-secondary'"
        >
          {{ translate('allChanges') }}
        </button>
        <button 
          @click="highlightMode = 'errors'" 
          class="btn btn-sm"
          :class="highlightMode === 'errors' ? 'btn-secondary' : 'btn-outline-secondary'"
        >
          {{ translate('errorsOnly') }}
        </button>
      </div>
      
      <div class="float-end">
        <button @click="syncScroll = !syncScroll" class="btn btn-sm btn-outline-info">
          <i class="fas" :class="syncScroll ? 'fa-link' : 'fa-unlink'"></i>
          {{ translate('syncScroll') }}
        </button>
      </div>
    </div>

    <!-- Legend -->
    <div class="diff-legend mb-3">
      <span class="legend-item">
        <span class="legend-color diff-correct"></span>
        {{ translate('correct') }}
      </span>
      <span class="legend-item">
        <span class="legend-color diff-substitution"></span>
        {{ translate('substitution') }}
      </span>
      <span class="legend-item">
        <span class="legend-color diff-insertion"></span>
        {{ translate('insertion') }}
      </span>
      <span class="legend-item">
        <span class="legend-color diff-deletion"></span>
        {{ translate('deletion') }}
      </span>
    </div>

    <!-- Split View -->
    <div v-if="viewMode === 'split'" class="split-view">
      <div class="row">
        <div class="col-md-6">
          <div class="diff-panel">
            <div class="diff-header">
              <h6>
                <span class="badge bg-info">A</span>
                {{ trans1Name }}
              </h6>
            </div>
            <div 
              ref="leftPanel"
              class="diff-content" 
              @scroll="onScroll('left')"
              v-html="visualization.ground_truth_html"
              dir="auto"
            ></div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="diff-panel">
            <div class="diff-header">
              <h6>
                <span class="badge bg-success">B</span>
                {{ trans2Name }}
              </h6>
            </div>
            <div 
              ref="rightPanel"
              class="diff-content" 
              @scroll="onScroll('right')"
              v-html="visualization.hypothesis_html"
              dir="auto"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Unified View -->
    <div v-else class="unified-view">
      <div class="diff-panel">
        <div class="unified-content" dir="auto">
          <div 
            v-for="(line, idx) in unifiedLines" 
            :key="idx"
            class="unified-line"
          >
            <div class="line-number">{{ idx + 1 }}</div>
            <div class="line-content">
              <div class="line-a" v-html="line.a"></div>
              <div class="line-b" v-html="line.b"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Differences Message -->
    <div v-if="!visualization.has_differences" class="alert alert-success mt-3">
      <i class="fas fa-check-circle"></i>
      <strong>{{ translate('perfectMatch') }}!</strong>
      {{ translate('noChanges') }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'VisualDiffViewer',
  
  props: {
    diffData: {
      type: Object,
      required: true,
    },
    trans1Name: {
      type: String,
      required: true,
    },
    trans2Name: {
      type: String,
      required: true,
    },
  },
  
  data() {
    return {
      viewMode: 'split', // 'split' or 'unified'
      highlightMode: 'all', // 'all' or 'errors'
      syncScroll: true,
      scrolling: false,
    }
  },
  
  computed: {
    summary() {
      return this.diffData.summary || {}
    },
    
    visualization() {
      return this.diffData.visualization || {
        ground_truth_html: '',
        hypothesis_html: '',
        has_differences: false,
      }
    },
    
    unifiedLines() {
      const lines1 = this.visualization.ground_truth_lines || []
      const lines2 = this.visualization.hypothesis_lines || []
      const maxLen = Math.max(lines1.length, lines2.length)
      
      const unified = []
      for (let i = 0; i < maxLen; i++) {
        unified.push({
          a: lines1[i] || '',
          b: lines2[i] || '',
        })
      }
      return unified
    },
  },
  
  methods: {
    translate(key) {
      return window.COMPARISON_TRANSLATIONS?.[key] || key
    },
    
    getAccuracyClass() {
      const acc = this.summary.accuracy || 0
      if (acc >= 95) return 'bg-success'
      if (acc >= 85) return 'bg-warning'
      return 'bg-danger'
    },
    
    onScroll(source) {
      if (!this.syncScroll || this.scrolling) return
      
      this.scrolling = true
      
      if (source === 'left' && this.$refs.rightPanel) {
        this.$refs.rightPanel.scrollTop = this.$refs.leftPanel.scrollTop
      } else if (source === 'right' && this.$refs.leftPanel) {
        this.$refs.leftPanel.scrollTop = this.$refs.rightPanel.scrollTop
      }
      
      setTimeout(() => {
        this.scrolling = false
      }, 100)
    },
  },
}
</script>

<style scoped>
.visual-diff-viewer {
  width: 100%;
}

.diff-summary {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.stat-box {
  padding: 1rem;
}

.stat-box i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.view-controls {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.diff-legend {
  padding: 0.75rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  margin-left: 1.5rem;
  font-size: 0.9rem;
}

.legend-color {
  display: inline-block;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  margin-left: 0.5rem;
  border: 1px solid #dee2e6;
}

.split-view {
  margin-top: 1rem;
}

.diff-panel {
  border: 2px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  height: 600px;
  display: flex;
  flex-direction: column;
}

.diff-header {
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.diff-header h6 {
  margin: 0;
  font-weight: 600;
}

.diff-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  font-family: 'Courier New', Monaco, monospace;
  font-size: 1rem;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Diff highlighting styles */
.diff-content >>> .diff-correct {
  /* No highlight for correct */
}

.diff-content >>> .diff-substitution {
  background-color: #fff3cd;
  border-bottom: 2px solid #ffc107;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: bold;
}

.diff-content >>> .diff-insertion {
  background-color: #d4edda;
  border-bottom: 2px solid #28a745;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: bold;
}

.diff-content >>> .diff-deletion {
  background-color: #f8d7da;
  border-bottom: 2px solid #dc3545;
  padding: 2px 4px;
  border-radius: 3px;
  text-decoration: line-through;
  font-weight: bold;
}

.unified-view {
  margin-top: 1rem;
}

.unified-content {
  border: 2px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  max-height: 600px;
  overflow-y: auto;
}

.unified-line {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  font-family: 'Courier New', Monaco, monospace;
  font-size: 0.95rem;
}

.unified-line:hover {
  background: #f8f9fa;
}

.line-number {
  width: 60px;
  padding: 0.5rem;
  text-align: center;
  background: #f8f9fa;
  color: #6c757d;
  border-left: 2px solid #dee2e6;
  font-size: 0.85rem;
}

.line-content {
  flex: 1;
  display: flex;
}

.line-a, .line-b {
  flex: 1;
  padding: 0.5rem 1rem;
  white-space: pre-wrap;
  word-break: break-word;
}

.line-a {
  background: #f0f8ff;
  border-left: 3px solid #007bff;
}

.line-b {
  background: #f0fff0;
  border-left: 3px solid #28a745;
}

@media (max-width: 768px) {
  .diff-panel {
    height: 400px;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .diff-content {
    font-size: 0.9rem;
    padding: 1rem;
  }
}
</style>
