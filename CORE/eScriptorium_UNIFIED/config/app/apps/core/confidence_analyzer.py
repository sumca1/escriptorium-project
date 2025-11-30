# Confidence Analyzer - BiblIA Enhancement
# Created: 2025-10-20
# Purpose: Analyze OCR confidence scores to detect suspicious transcriptions
# Focus: Low-confidence characters and words

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# Confidence thresholds
CONFIDENCE_VERY_LOW = 0.5   # Red flag - very suspicious
CONFIDENCE_LOW = 0.7        # Yellow flag - needs review
CONFIDENCE_NORMAL = 0.85    # Acceptable confidence


@dataclass
class ConfidenceIssue:
    """Confidence issue detected in text"""
    text: str
    start_pos: int
    end_pos: int
    confidence: float
    severity: str  # 'critical', 'warning', 'info'
    description: str


class ConfidenceAnalyzer:
    """
    מנתח ציוני ביטחון של OCR לזיהוי תעתיקים חשודים
    Analyzes OCR confidence scores to detect suspicious transcriptions
    
    Features:
    1. Identifies low-confidence characters and words
    2. Flags suspicious character sequences
    3. Detects confidence drops within words
    4. Provides severity ratings
    """
    
    def __init__(self):
        self.very_low_threshold = CONFIDENCE_VERY_LOW
        self.low_threshold = CONFIDENCE_LOW
        self.normal_threshold = CONFIDENCE_NORMAL
        logger.info("ConfidenceAnalyzer initialized")
    
    def analyze_line(
        self, 
        text: str, 
        confidences: Optional[List[float]] = None,
        line_id: int = None
    ) -> List[Dict]:
        """
        מנתח שורת טקסט עם ציוני ביטחון
        Analyze a line of text with confidence scores
        
        Args:
            text: The transcribed text
            confidences: List of confidence scores (one per character)
            line_id: Optional LineTranscription ID
            
        Returns:
            List of detected confidence issues
        """
        if not confidences or len(confidences) == 0:
            logger.debug("No confidence scores provided")
            return []
        
        if len(confidences) != len(text):
            logger.warning(f"Confidence array length ({len(confidences)}) "
                         f"doesn't match text length ({len(text)})")
            # Pad or truncate to match
            if len(confidences) < len(text):
                confidences = confidences + [1.0] * (len(text) - len(confidences))
            else:
                confidences = confidences[:len(text)]
        
        issues = []
        
        # Find low confidence characters
        issues.extend(self._find_low_confidence_chars(text, confidences))
        
        # Find low confidence words
        issues.extend(self._find_low_confidence_words(text, confidences))
        
        # Find confidence drops
        issues.extend(self._find_confidence_drops(text, confidences))
        
        # Add line_id to all issues
        for issue in issues:
            issue['line_id'] = line_id
        
        return issues
    
    def _find_low_confidence_chars(
        self, 
        text: str, 
        confidences: List[float]
    ) -> List[Dict]:
        """
        מזהה תווים עם ציון ביטחון נמוך
        Find characters with low confidence scores
        """
        issues = []
        
        for i, (char, conf) in enumerate(zip(text, confidences)):
            # Skip whitespace
            if char.isspace():
                continue
            
            severity = self._get_severity(conf)
            
            if severity:
                issues.append({
                    'error_type': 'confidence',
                    'confidence_type': 'low_char',
                    'text': char,
                    'start_pos': i,
                    'end_pos': i + 1,
                    'confidence': conf,
                    'severity': severity,
                    'description': f'Low confidence character ({conf:.2%})',
                    'suggestions': []
                })
        
        return issues
    
    def _find_low_confidence_words(
        self, 
        text: str, 
        confidences: List[float]
    ) -> List[Dict]:
        """
        מזהה מילים עם ממוצע ביטחון נמוך
        Find words with low average confidence
        """
        issues = []
        words = self._split_into_words(text)
        
        for word_text, start, end in words:
            if len(word_text) == 0:
                continue
            
            # Calculate average confidence for word
            word_confidences = confidences[start:end]
            avg_confidence = sum(word_confidences) / len(word_confidences)
            
            severity = self._get_severity(avg_confidence)
            
            if severity:
                # Find minimum confidence in word
                min_conf = min(word_confidences)
                min_pos = word_confidences.index(min_conf)
                
                issues.append({
                    'error_type': 'confidence',
                    'confidence_type': 'low_word',
                    'text': word_text,
                    'start_pos': start,
                    'end_pos': end,
                    'confidence': avg_confidence,
                    'min_confidence': min_conf,
                    'min_confidence_pos': start + min_pos,
                    'severity': severity,
                    'description': f'Low confidence word (avg: {avg_confidence:.2%}, min: {min_conf:.2%})',
                    'suggestions': []
                })
        
        return issues
    
    def _find_confidence_drops(
        self, 
        text: str, 
        confidences: List[float]
    ) -> List[Dict]:
        """
        מזהה ירידות חדות בציון ביטחון בתוך מילים
        Find sharp confidence drops within words
        """
        issues = []
        words = self._split_into_words(text)
        
        for word_text, start, end in words:
            if len(word_text) < 3:  # Skip short words
                continue
            
            word_confidences = confidences[start:end]
            
            # Look for drops > 0.3
            for i in range(len(word_confidences) - 1):
                drop = word_confidences[i] - word_confidences[i + 1]
                
                if drop > 0.3:
                    issues.append({
                        'error_type': 'confidence',
                        'confidence_type': 'confidence_drop',
                        'text': word_text[i:i+2],
                        'start_pos': start + i,
                        'end_pos': start + i + 2,
                        'confidence': word_confidences[i + 1],
                        'drop_amount': drop,
                        'severity': 'warning',
                        'description': f'Sharp confidence drop ({drop:.2%}) within word',
                        'suggestions': []
                    })
        
        return issues
    
    def _get_severity(self, confidence: float) -> Optional[str]:
        """
        קובע רמת חומרה לפי ציון ביטחון
        Determine severity based on confidence score
        """
        if confidence < self.very_low_threshold:
            return 'critical'
        elif confidence < self.low_threshold:
            return 'warning'
        elif confidence < self.normal_threshold:
            return 'info'
        return None
    
    def _split_into_words(self, text: str) -> List[Tuple[str, int, int]]:
        """
        מפצל טקסט למילים עם מיקומים
        Split text into words with positions
        
        Returns:
            List of (word_text, start_pos, end_pos)
        """
        words = []
        current_word = []
        word_start = 0
        
        for i, char in enumerate(text):
            if char.isspace():
                if current_word:
                    words.append((
                        ''.join(current_word),
                        word_start,
                        i
                    ))
                    current_word = []
            else:
                if not current_word:
                    word_start = i
                current_word.append(char)
        
        # Add last word
        if current_word:
            words.append((
                ''.join(current_word),
                word_start,
                len(text)
            ))
        
        return words
    
    def get_line_score(self, confidences: List[float]) -> float:
        """
        מחשב ציון כולל לשורה
        Calculate overall score for a line
        """
        if not confidences:
            return 1.0
        return sum(confidences) / len(confidences)
    
    def get_statistics(self, confidences: List[float]) -> Dict:
        """
        מחזיר סטטיסטיקות על ציוני הביטחון
        Return statistics about confidence scores
        """
        if not confidences:
            return {}
        
        return {
            'average': sum(confidences) / len(confidences),
            'minimum': min(confidences),
            'maximum': max(confidences),
            'below_very_low': sum(1 for c in confidences if c < self.very_low_threshold),
            'below_low': sum(1 for c in confidences if c < self.low_threshold),
            'below_normal': sum(1 for c in confidences if c < self.normal_threshold),
            'total_chars': len(confidences)
        }


# Singleton instance
_confidence_analyzer_instance = None


def get_confidence_analyzer() -> ConfidenceAnalyzer:
    """
    קבל מופע יחיד של מנתח הביטחון
    Get singleton confidence analyzer instance
    """
    global _confidence_analyzer_instance
    if _confidence_analyzer_instance is None:
        _confidence_analyzer_instance = ConfidenceAnalyzer()
    return _confidence_analyzer_instance
