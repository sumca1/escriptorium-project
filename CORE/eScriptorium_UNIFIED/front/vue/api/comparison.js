/**
 * 🎯 OCR Comparison API - Phase 1 Integration
 * ==========================================
 * חיבור ל-Phase 1 Backend (AdvancedComparisonView)
 * 
 * Endpoints:
 * - POST /api/comparison/advanced/ - Advanced CER analysis
 * - GET  /api/comparison/transcriptions/{doc_id}/ - List transcriptions
 * - POST /api/comparison/batch/ - Batch comparison
 * 
 * @author BiblIA Phase 2
 * @date 3 נובמבר 2025
 */

import axios from 'axios'

// Base URL - יכול להגדיר ב-environment
const API_BASE = process.env.VUE_APP_API_URL || ''

/**
 * @typedef {Object} AdvancedCERResponse
 * @property {number} advanced_cer - CER מתקדם עם breakdown
 * @property {number} wer - Word Error Rate
 * @property {Object} error_breakdown - פירוט שגיאות
 * @property {number} error_breakdown.substitutions - החלפות
 * @property {number} error_breakdown.insertions - הוספות
 * @property {number} error_breakdown.deletions - מחיקות
 * @property {number} error_breakdown.correct - תווים נכונים
 * @property {Array<string>} recommendations - המלצות
 * @property {Object} [confidence_analysis] - ניתוח ביטחון Tesseract
 * @property {Object} [unicode_blocks] - ניתוח Unicode blocks
 */

/**
 * מבצע השוואה מתקדמת של 2 transcriptions
 * @param {number} transcriptionId1 - Transcription A
 * @param {number} transcriptionId2 - Transcription B
 * @param {number} [lineId] - Line ספציפי (אופציונלי)
 * @returns {Promise<AdvancedCERResponse>}
 */
export async function fetchAdvancedComparison(transcriptionId1, transcriptionId2, lineId = null) {
  try {
    const payload = {
      transcription_id_1: transcriptionId1,
      transcription_id_2: transcriptionId2
    }
    
    if (lineId !== null) {
      payload.line_id = lineId
    }
    
    const response = await axios.post(
      `${API_BASE}/api/comparison/advanced/`,
      payload,
      {
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      }
    )
    
    return response.data
  } catch (error) {
    console.error('❌ Advanced comparison failed:', error)
    
    // אם Phase 1 Backend לא זמין - fallback לBasic
    if (error.response?.status === 404 || error.response?.status === 500) {
      console.warn('⚠️ Phase 1 API not available, falling back to basic comparison')
      return await fetchBasicComparison(transcriptionId1, transcriptionId2, lineId)
    }
    
    throw error
  }
}

/**
 * Fallback - השוואה בסיסית (API ישן)
 * @param {number} transcriptionId1
 * @param {number} transcriptionId2
 * @param {number} [lineId]
 * @returns {Promise<Object>}
 */
async function fetchBasicComparison(transcriptionId1, transcriptionId2, lineId = null) {
  try {
    const params = new URLSearchParams({
      transcription_1: transcriptionId1,
      transcription_2: transcriptionId2
    })
    
    if (lineId !== null) {
      params.append('line', lineId)
    }
    
    const response = await axios.get(
      `${API_BASE}/api/comparison/basic/?${params.toString()}`
    )
    
    // המר לפורמט Phase 1
    const data = response.data
    return {
      advanced_cer: data.cer || 0,
      wer: data.wer || 0,
      error_breakdown: {
        substitutions: data.substitutions || 0,
        insertions: data.insertions || 0,
        deletions: data.deletions || 0,
        correct: data.correct || 0
      },
      recommendations: data.recommendations || [],
      _fallback: true
    }
  } catch (error) {
    console.error('❌ Basic comparison also failed:', error)
    throw error
  }
}

/**
 * קבל רשימת transcriptions עבור document
 * @param {number} documentId - Document ID
 * @returns {Promise<Array>}
 */
export async function fetchTranscriptions(documentId) {
  try {
    const response = await axios.get(
      `${API_BASE}/api/comparison/transcriptions/${documentId}/`
    )
    return response.data
  } catch (error) {
    console.error('❌ Failed to fetch transcriptions:', error)
    throw error
  }
}

/**
 * השוואה של כל השורות במסמך (Batch)
 * @param {number} transcriptionId1
 * @param {number} transcriptionId2
 * @param {Object} [options] - אופציות נוספות
 * @returns {Promise<Object>}
 */
export async function fetchBatchComparison(transcriptionId1, transcriptionId2, options = {}) {
  try {
    const payload = {
      transcription_id_1: transcriptionId1,
      transcription_id_2: transcriptionId2,
      ...options
    }
    
    const response = await axios.post(
      `${API_BASE}/api/comparison/batch/`,
      payload
    )
    
    return response.data
  } catch (error) {
    console.error('❌ Batch comparison failed:', error)
    throw error
  }
}

/**
 * ייצוא תוצאות השוואה
 * @param {number} transcriptionId1
 * @param {number} transcriptionId2
 * @param {string} format - 'json' | 'csv' | 'xlsx'
 * @returns {Promise<Blob>}
 */
export async function exportComparison(transcriptionId1, transcriptionId2, format = 'json') {
  try {
    const response = await axios.post(
      `${API_BASE}/api/comparison/export/`,
      {
        transcription_id_1: transcriptionId1,
        transcription_id_2: transcriptionId2,
        format
      },
      {
        responseType: 'blob'
      }
    )
    
    return response.data
  } catch (error) {
    console.error('❌ Export failed:', error)
    throw error
  }
}

/**
 * שמור תוצאות השוואה
 * @param {Object} comparisonData - נתוני ההשוואה
 * @returns {Promise<Object>}
 */
export async function saveComparison(comparisonData) {
  try {
    const response = await axios.post(
      `${API_BASE}/api/comparison/save/`,
      comparisonData
    )
    
    return response.data
  } catch (error) {
    console.error('❌ Save failed:', error)
    throw error
  }
}

/**
 * Helper: בדוק אם Phase 1 API זמין
 * @returns {Promise<boolean>}
 */
export async function checkPhase1Available() {
  try {
    const response = await axios.get(`${API_BASE}/api/comparison/health/`)
    return response.data.phase1_available === true
  } catch (error) {
    return false
  }
}

// Export default object
export default {
  fetchAdvancedComparison,
  fetchTranscriptions,
  fetchBatchComparison,
  exportComparison,
  saveComparison,
  checkPhase1Available
}
