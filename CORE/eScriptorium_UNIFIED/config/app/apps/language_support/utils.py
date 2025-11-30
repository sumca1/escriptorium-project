"""
Utils for Language Support App
Integrates with escriptorium_model_checker.py without modifying core
"""

import os
import sys
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


def get_model_checker_path():
    """מחזיר נתיב ל-escriptorium_model_checker.py"""
    base_dir = Path(settings.BASE_DIR)  # BASE_DIR הוא /usr/src/app
    checker_path = base_dir / "escriptorium_model_checker.py"  # הקובץ מועתק לשורש
    return checker_path


def analyze_hebrew_support(ocr_model):
    """
    מפעיל ניתוח Hebrew support עבור מודל OCR ספציפי
    משתמש ב-escriptorium_model_checker.py הקיים בלי לשנות כלום בליבה
    """
    try:
        # הוספת הנתיב למערכת
        checker_path = get_model_checker_path()
        
        if not checker_path.exists():
            raise FileNotFoundError(f"Model checker not found: {checker_path}")
        
        # הוספת הנתיב ל-sys.path אם לא קיים
        checker_dir = str(checker_path.parent)
        if checker_dir not in sys.path:
            sys.path.insert(0, checker_dir)
        
        # ייבוא המודול
        import escriptorium_model_checker as checker_module
        
        # קריאה לפונקציית הניתוח
        model_path = ocr_model.file.path if ocr_model.file else None
        
        if not model_path or not os.path.exists(model_path):
            return {
                'hebrew_support': 'unknown',
                'confidence_score': 0.0,
                'notes': f'Model file not found: {model_path}'
            }
        
        # יצירת אינסטנס של הבודק ויהפעלת הניתוח
        model_checker = checker_module.EscriptoriumModelChecker()
        result = model_checker.check_model(model_path)
        
        # שימוש בפונקציית הניתוח החדשה הגנרית
        language_analysis = analyze_model_language_support(result)
        
        return language_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing Hebrew support for {ocr_model.name}: {e}")
        return {
            'hebrew_support': 'unknown', 
            'confidence_score': 0.0,
            'notes': f'Analysis error: {str(e)}'
        }


def analyze_model_language_support(checker_result):
    """
    ניתוח גנרי של תמיכת שפות במודל - לא רק עברית!
    מתבסס על ניתוח התווים במקום מילות מפתח בלבד
    """
    if not checker_result or 'error' in checker_result:
        return {
            'hebrew_support': 'unknown',
            'confidence_score': 0.0,
            'notes': 'Analysis failed or no data available'
        }
    
    # ניתוח charset
    charset_info = checker_result.get('charset_info', {})
    hebrew_detection = checker_result.get('hebrew_detection', {})
    
    # משתנים לחישוב
    hebrew_support_level = 'unknown'
    confidence_score = 0.0
    notes_parts = []
    
    # בדיקה מבוססת charset (עדיפה על מילות מפתח)
    if charset_info.get('success') and charset_info.get('charset_size', 0) > 0:
        hebrew_percentage = charset_info.get('hebrew_percentage', 0)
        charset_size = charset_info.get('charset_size', 0)
        hebrew_chars_count = charset_info.get('hebrew_chars_count', 0)
        
        # ניתוח מבוסס תווים עבריים בפועל
        if hebrew_percentage >= 60:
            hebrew_support_level = 'full'
            confidence_score = 0.9
            notes_parts.append(f'High Hebrew charset coverage: {hebrew_percentage}%')
        elif hebrew_percentage >= 30:
            hebrew_support_level = 'partial'
            confidence_score = 0.75
            notes_parts.append(f'Moderate Hebrew charset coverage: {hebrew_percentage}%')
        elif hebrew_percentage >= 10:
            hebrew_support_level = 'partial'
            confidence_score = 0.6
            notes_parts.append(f'Limited Hebrew charset coverage: {hebrew_percentage}%')
        elif hebrew_chars_count > 0:
            hebrew_support_level = 'partial'
            confidence_score = 0.4
            notes_parts.append(f'Minimal Hebrew support: {hebrew_chars_count} Hebrew chars')
        else:
            hebrew_support_level = 'none'
            confidence_score = 0.8  # גבוה כי אנחנו יודעים בוודאות שאין תמיכה
            notes_parts.append(f'No Hebrew characters detected in charset')
        
        notes_parts.append(f'Total charset size: {charset_size}')
        
    # אם ניתוח charset נכשל, נסתמך על זיהוי מילות מפתח (פחות אמין)
    elif hebrew_detection.get('score', 0) > 0:
        notes_parts.append('Charset analysis failed, using keyword detection')
        
        if hebrew_detection.get('is_hebrew', False):
            confidence_level = hebrew_detection.get('confidence', '').lower()
            score = hebrew_detection.get('score', 0)
            
            if confidence_level == 'גבוהה' and score >= 15:
                hebrew_support_level = 'full'
                confidence_score = 0.7  # נמוך יותר כי מבוסס מילות מפתח
            elif confidence_level == 'בינונית' or score >= 10:
                hebrew_support_level = 'partial'
                confidence_score = 0.6
            else:
                hebrew_support_level = 'partial'
                confidence_score = 0.4
        else:
            hebrew_support_level = 'none'
            confidence_score = 0.6
        
        found_keywords = hebrew_detection.get('found_keywords', [])
        if found_keywords:
            notes_parts.append(f"Keywords found: {', '.join(found_keywords)}")
    else:
        # לא ניתן לבצע ניתוח
        hebrew_support_level = 'unknown'
        confidence_score = 0.0
        notes_parts.append('No charset or keyword analysis available')
    
    return {
        'hebrew_support': hebrew_support_level,
        'confidence_score': confidence_score,
        'notes': '; '.join(notes_parts),
        'analysis_details': checker_result,
        'analyzer_version': '2.0_generic',
        'analyzed_by': 'language_support_app'
    }