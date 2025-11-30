/**
 * 🎯 Enhanced OCR Comparison Dashboard - Phase 1 Integration
 * ===========================================================
 * משדרג את OCRComparisonDashboard.vue עם חיבור ל-Phase 1 Backend
 * 
 * @component OCRComparisonDashboardEnhanced
 * @description Dashboard מתקדם עם CERAnalyzer, WER, Recommendations
 * @author BiblIA Phase 2
 * @date 3 נובמבר 2025
 */

import { fetchAdvancedComparison, fetchTranscriptions, checkPhase1Available } from '@/api/comparison'

export default {
  /**
   * 🔧 תיקון ב-methods.performComparison()
   * החלף את הקוד הישן ב:
   */
  async performComparison() {
    if (!this.canCompare) return
    
    this.comparing = true
    this.errorMessage = ''
    this.advancedMetrics = null  // Reset
    
    try {
      // 🎯 Phase 1: נסה Advanced Comparison קודם
      if (this.phase1Available) {
        console.log('✅ Using Phase 1 Advanced Comparison API')
        
        const advancedData = await fetchAdvancedComparison(
          this.selectedTrans1,
          this.selectedTrans2,
          null  // null = כל המסמך, או lineId ספציפי
        )
        
        // שמור metrics מתקדמים
        this.advancedMetrics = advancedData
        
        // המר לפורמט הישן לbackward compatibility
        this.comparisonResult = {
          cer: advancedData.advanced_cer,
          wer: advancedData.wer,
          error_breakdown: advancedData.error_breakdown,
          recommendations: advancedData.recommendations,
          confidence_analysis: advancedData.confidence_analysis || null,
          unicode_blocks: advancedData.unicode_blocks || null,
          
          // שמור גם נתונים ישנים אם יש
          ...this.comparisonResult
        }
        
        console.log('✅ Advanced metrics:', this.advancedMetrics)
        this.activeTab = 'advanced'  // Tab חדש!
        
      } else {
        // Fallback: API ישן (cerberus)
        console.warn('⚠️ Phase 1 API not available, using legacy comparison')
        
        const payload = {
          transcription_1_id: this.selectedTrans1,
          transcription_2_id: this.selectedTrans2,
          ground_truth_id: this.selectedGroundTruth,
          options: this.options,
        }
        
        const response = await fetch('/cerberus/api/compare/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken(),
          },
          body: JSON.stringify(payload),
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.error || 'Comparison failed')
        }
        
        this.comparisonResult = await response.json()
        this.activeTab = 'diff'
      }
      
    } catch (error) {
      console.error('❌ Comparison error:', error)
      this.errorMessage = error.message || 'Failed to perform comparison'
      
      // אם Phase 1 נכשל, נסה fallback
      if (this.phase1Available && !error._fallback) {
        console.warn('⚠️ Phase 1 failed, trying fallback...')
        this.phase1Available = false
        await this.performComparison()  // Retry with fallback
      }
    } finally {
      this.comparing = false
    }
  },
  
  /**
   * 🔧 תיקון ב-methods.loadTranscriptions()
   * החלף את הקוד הישן ב:
   */
  async loadTranscriptions() {
    this.loading = true
    try {
      // 🎯 Phase 1: נסה API חדש קודם
      if (this.phase1Available) {
        console.log('✅ Using Phase 1 Transcriptions API')
        this.transcriptions = await fetchTranscriptions(this.documentId)
      } else {
        // Fallback: API ישן
        const response = await fetch(
          `/cerberus/api/document/${this.documentId}/transcriptions/`
        )
        if (!response.ok) throw new Error('Failed to load transcriptions')
        
        const data = await response.json()
        this.transcriptions = data.transcriptions
      }
    } catch (error) {
      console.error('❌ Error loading transcriptions:', error)
      this.errorMessage = 'Failed to load transcriptions'
    } finally {
      this.loading = false
    }
  },
  
  /**
   * 🆕 הוסף ב-mounted() hook
   */
  async mounted() {
    // בדוק אם Phase 1 API זמין
    this.phase1Available = await checkPhase1Available()
    console.log(`🎯 Phase 1 API: ${this.phase1Available ? '✅ Available' : '❌ Not available'}`)
    
    // טען transcriptions
    await this.loadTranscriptions()
    await this.loadStatistics()
  },
  
  /**
   * 🆕 הוסף ב-data()
   * הוסף את השורות הבאות לתוך return {}:
   */
  // phase1Available: false,
  // advancedMetrics: null,  // { advanced_cer, wer, error_breakdown, recommendations, ... }
}

/**
 * 📝 Template Changes
 * ==================
 * הוסף tab חדש ל-Advanced Metrics:
 * 
 * <template>
 *   ...
 *   <ul class="nav nav-tabs">
 *     <li class="nav-item">
 *       <a class="nav-link" :class="{ active: activeTab === 'diff' }" @click="activeTab = 'diff'">
 *         {{ translate('visualDiff') }}
 *       </a>
 *     </li>
 *     <li class="nav-item">
 *       <a class="nav-link" :class="{ active: activeTab === 'charts' }" @click="activeTab = 'charts'">
 *         {{ translate('charts') }}
 *       </a>
 *     </li>
 *     <li class="nav-item">
 *       <a class="nav-link" :class="{ active: activeTab === 'details' }" @click="activeTab = 'details'">
 *         {{ translate('detailedAnalysis') }}
 *       </a>
 *     </li>
 *     <!-- 🆕 Phase 1 Tab -->
 *     <li class="nav-item" v-if="advancedMetrics">
 *       <a class="nav-link" :class="{ active: activeTab === 'advanced' }" @click="activeTab = 'advanced'">
 *         <i class="fas fa-brain"></i>
 *         {{ translate('advancedAnalysis') }}
 *         <span class="badge bg-success">Phase 1</span>
 *       </a>
 *     </li>
 *   </ul>
 *   
 *   <!-- Tab Content -->
 *   <div class="tab-content">
 *     <!-- ... existing tabs ... -->
 *     
 *     <!-- 🆕 Advanced Analysis Tab -->
 *     <div v-if="activeTab === 'advanced' && advancedMetrics" class="tab-pane active">
 *       <div class="row">
 *         <!-- Advanced CER Card -->
 *         <div class="col-md-4">
 *           <div class="card mb-3">
 *             <div class="card-header bg-primary text-white">
 *               <i class="fas fa-calculator"></i>
 *               Advanced CER
 *             </div>
 *             <div class="card-body text-center">
 *               <h2 class="display-4">{{ advancedMetrics.advanced_cer.toFixed(2) }}%</h2>
 *               <p class="text-muted">Character Error Rate</p>
 *             </div>
 *           </div>
 *         </div>
 *         
 *         <!-- WER Card -->
 *         <div class="col-md-4">
 *           <div class="card mb-3">
 *             <div class="card-header bg-info text-white">
 *               <i class="fas fa-text-width"></i>
 *               WER
 *             </div>
 *             <div class="card-body text-center">
 *               <h2 class="display-4">{{ advancedMetrics.wer.toFixed(2) }}%</h2>
 *               <p class="text-muted">Word Error Rate</p>
 *             </div>
 *           </div>
 *         </div>
 *         
 *         <!-- Error Breakdown Card -->
 *         <div class="col-md-4">
 *           <div class="card mb-3">
 *             <div class="card-header bg-warning text-dark">
 *               <i class="fas fa-chart-pie"></i>
 *               Error Breakdown
 *             </div>
 *             <div class="card-body">
 *               <error-breakdown-chart :analysis="advancedMetrics.error_breakdown" />
 *             </div>
 *           </div>
 *         </div>
 *       </div>
 *       
 *       <!-- Recommendations -->
 *       <div class="card mb-3" v-if="advancedMetrics.recommendations && advancedMetrics.recommendations.length > 0">
 *         <div class="card-header bg-success text-white">
 *           <i class="fas fa-lightbulb"></i>
 *           Recommendations
 *         </div>
 *         <div class="card-body">
 *           <ul class="list-group list-group-flush">
 *             <li class="list-group-item" v-for="(rec, index) in advancedMetrics.recommendations" :key="index">
 *               <i class="fas fa-check-circle text-success"></i>
 *               {{ rec }}
 *             </li>
 *           </ul>
 *         </div>
 *       </div>
 *       
 *       <!-- Confidence Analysis (if available) -->
 *       <div class="card mb-3" v-if="advancedMetrics.confidence_analysis">
 *         <div class="card-header">
 *           <i class="fas fa-chart-line"></i>
 *           Tesseract Confidence Analysis
 *         </div>
 *         <div class="card-body">
 *           <p><strong>Average Confidence:</strong> {{ (advancedMetrics.confidence_analysis.average * 100).toFixed(1) }}%</p>
 *           <p><strong>Low Confidence Characters:</strong> {{ advancedMetrics.confidence_analysis.low_confidence_count }}</p>
 *         </div>
 *       </div>
 *       
 *       <!-- Unicode Blocks (if available) -->
 *       <div class="card" v-if="advancedMetrics.unicode_blocks">
 *         <div class="card-header">
 *           <i class="fas fa-globe"></i>
 *           Unicode Block Analysis
 *         </div>
 *         <div class="card-body">
 *           <div class="row">
 *             <div class="col-md-4" v-for="(count, block) in advancedMetrics.unicode_blocks" :key="block">
 *               <strong>{{ block }}:</strong> {{ count }} characters
 *             </div>
 *           </div>
 *         </div>
 *       </div>
 *     </div>
 *   </div>
 * </template>
 */

/**
 * 📝 Usage Instructions
 * ====================
 * 
 * 1. ייבוא ב-main component:
 *    import { fetchAdvancedComparison } from '@/api/comparison'
 * 
 * 2. הוסף לdata():
 *    phase1Available: false,
 *    advancedMetrics: null,
 * 
 * 3. הוסף mounted():
 *    this.phase1Available = await checkPhase1Available()
 * 
 * 4. החלף performComparison() בקוד למעלה
 * 
 * 5. החלף loadTranscriptions() בקוד למעלה
 * 
 * 6. הוסף template changes (Advanced tab)
 * 
 * 7. הרץ:
 *    npm run dev
 * 
 * 8. בדוק:
 *    - בחר 2 transcriptions
 *    - לחץ "Compare"
 *    - לחץ על tab "Advanced Analysis"
 *    - ראה: CER, WER, Error Breakdown, Recommendations!
 */

/**
 * 🎯 תוצאה צפויה
 * ==============
 * 
 * ✅ כשPhase 1 זמין:
 *    - Tab "Advanced Analysis" מופיע
 *    - CER מתקדם עם breakdown
 *    - WER calculation
 *    - Recommendations list
 *    - Tesseract confidence (if available)
 *    - Unicode blocks analysis
 * 
 * ✅ כשPhase 1 לא זמין:
 *    - Fallback לAPI ישן
 *    - עובד כרגיל (backward compatible)
 *    - Log warning בconsole
 * 
 * ✅ Performance:
 *    - Phase 1 API: ~1-2 שניות
 *    - Fallback API: ~0.5-1 שניה
 *    - Auto-detect בטעינה
 */
