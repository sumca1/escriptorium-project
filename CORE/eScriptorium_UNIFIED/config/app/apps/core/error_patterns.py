# Error Pattern Detector - BiblIA Enhancement
# Created: 2025-10-20
# Purpose: Detect common OCR error patterns in Hebrew text
# Focus: Hebrew-specific OCR patterns

import logging
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ErrorPattern:
    """Error pattern definition"""
    name: str
    pattern: re.Pattern
    description: str
    severity: str  # 'high', 'medium', 'low'
    replacement_suggestions: List[str]


class ErrorPatternDetector:
    """
    מזהה דפוסי שגיאות OCR נפוצים בטקסט עברי
    Detects common OCR error patterns in Hebrew text
    
    Focus areas:
    1. Digits mixed with Hebrew letters (OCR confusion)
    2. Latin letters mixed with Hebrew
    3. Arabic-Hebrew character confusion (ר ↔ ו)
    4. Repeated vav (וו instead of ר)
    5. Spacing issues before punctuation
    6. Mixed RTL/LTR issues
    """
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        logger.info(f"ErrorPatternDetector initialized with {len(self.patterns)} patterns")
    
    def _initialize_patterns(self) -> List[ErrorPattern]:
        """
        אתחול דפוסי השגיאות
        Initialize error patterns
        """
        patterns = []
        
        # Pattern 1: Digit in Hebrew word
        # Example: "סו5" instead of "סוף", "ד0ר" instead of "דור"
        patterns.append(ErrorPattern(
            name='digit_in_word',
            pattern=re.compile(r'[\u0590-\u05FF]+[0-9][\u0590-\u05FF]*|[\u0590-\u05FF]*[0-9][\u0590-\u05FF]+'),
            description='Digit mixed within Hebrew word (OCR confusion: 0↔ס, 5↔ה, 1↔ו)',
            severity='high',
            replacement_suggestions=['Replace digit with similar Hebrew letter']
        ))
        
        # Pattern 2: Latin letter in Hebrew word
        # Example: "שlום" instead of "שלום"
        patterns.append(ErrorPattern(
            name='latin_in_hebrew',
            pattern=re.compile(r'[\u0590-\u05FF]{1,}[a-zA-Z][\u0590-\u05FF]{1,}'),
            description='Latin letter mixed with Hebrew (OCR confusion: l↔ל, o↔ס)',
            severity='high',
            replacement_suggestions=['Replace Latin with Hebrew equivalent']
        ))
        
        # Pattern 3: Repeated vav (וו) - often OCR mistake for ר
        # Example: "דבוו" instead of "דבר"
        patterns.append(ErrorPattern(
            name='repeated_vav',
            pattern=re.compile(r'[\u0590-\u05FF]*וו[\u0590-\u05FF]*'),
            description='Double vav (וו) - might be ר',
            severity='medium',
            replacement_suggestions=['Try replacing וו with ר']
        ))
        
        # Pattern 4: Arabic ر (reh) confused with Hebrew ו (vav)
        # Example: "שלוم" with Arabic ر
        patterns.append(ErrorPattern(
            name='arabic_confusion',
            pattern=re.compile(r'[\u0590-\u05FF]*[\u0600-\u06FF][\u0590-\u05FF]*'),
            description='Arabic character in Hebrew text',
            severity='high',
            replacement_suggestions=['Replace Arabic char with Hebrew equivalent']
        ))
        
        # Pattern 5: Space before punctuation
        # Example: "שלום ." instead of "שלום."
        patterns.append(ErrorPattern(
            name='space_before_punctuation',
            pattern=re.compile(r'[\u0590-\u05FF]\s+[.,:;!?]'),
            description='Incorrect space before punctuation',
            severity='low',
            replacement_suggestions=['Remove space before punctuation']
        ))
        
        # Pattern 6: Multiple spaces (OCR artifact)
        patterns.append(ErrorPattern(
            name='multiple_spaces',
            pattern=re.compile(r'\s{2,}'),
            description='Multiple consecutive spaces',
            severity='low',
            replacement_suggestions=['Replace with single space']
        ))
        
        # Pattern 7: Orphan niqqud (diacritical marks without letters)
        # Example: standalone ְ or ַ
        patterns.append(ErrorPattern(
            name='orphan_niqqud',
            pattern=re.compile(r'(?<![א-ת])[\u0591-\u05C7]'),
            description='Niqqud mark without base letter',
            severity='medium',
            replacement_suggestions=['Remove orphan niqqud or attach to previous letter']
        ))
        
        # Pattern 8: Final letter in wrong position
        # Hebrew finals: ך, ם, ן, ף, ץ should only appear at word end
        patterns.append(ErrorPattern(
            name='misplaced_final',
            pattern=re.compile(r'[ךםןףץ][\u0590-\u05FF]'),
            description='Final letter not at end of word',
            severity='high',
            replacement_suggestions=['Replace with non-final form (כ→ך, מ→ם, נ→ן, פ→ף, צ→ץ)']
        ))
        
        return patterns
    
    def analyze_line(self, text: str, line_id: int = None) -> List[Dict]:
        """
        מנתח שורת טקסט ומחזיר רשימת שגיאות דפוס
        Analyze a line of text and return list of pattern errors
        
        Args:
            text: Text to analyze
            line_id: Optional LineTranscription ID for reference
            
        Returns:
            List of detected errors with details
        """
        errors = []
        
        for pattern_def in self.patterns:
            matches = pattern_def.pattern.finditer(text)
            
            for match in matches:
                error = {
                    'error_type': 'pattern',
                    'pattern_name': pattern_def.name,
                    'text': match.group(),
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'description': pattern_def.description,
                    'severity': pattern_def.severity,
                    'suggestions': self._generate_suggestions(
                        pattern_def.name, 
                        match.group()
                    ),
                    'line_id': line_id
                }
                errors.append(error)
        
        return errors
    
    def _generate_suggestions(self, pattern_name: str, matched_text: str) -> List[str]:
        """
        יוצר הצעות תיקון לפי סוג הדפוס
        Generate correction suggestions based on pattern type
        """
        suggestions = []
        
        if pattern_name == 'digit_in_word':
            # Common OCR digit↔letter confusions
            replacements = {
                '0': 'ס',  # samekh
                '1': 'ו',  # vav
                '5': 'ה',  # he
                '7': 'ז',  # zayin
                '8': 'ח',  # het
                '9': 'ט',  # tet
            }
            for digit, letter in replacements.items():
                if digit in matched_text:
                    suggestions.append(matched_text.replace(digit, letter))
        
        elif pattern_name == 'latin_in_hebrew':
            # Common OCR Latin↔Hebrew confusions
            replacements = {
                'l': 'ל',  # lamed
                'o': 'ס',  # samekh
                'O': 'ס',
                'c': 'ס',
                'C': 'ס',
                'n': 'ן',  # final nun
                'u': 'ו',  # vav
            }
            for latin, hebrew in replacements.items():
                if latin in matched_text:
                    suggestions.append(matched_text.replace(latin, hebrew))
        
        elif pattern_name == 'repeated_vav':
            # Replace וו with ר
            suggestions.append(matched_text.replace('וו', 'ר'))
        
        elif pattern_name == 'arabic_confusion':
            # Common Arabic↔Hebrew confusions
            replacements = {
                'ر': 'ו',  # Arabic reh → Hebrew vav
                'و': 'ו',  # Arabic waw → Hebrew vav
                'ا': 'א',  # Arabic alef → Hebrew alef
                'ب': 'ב',  # Arabic beh → Hebrew bet
            }
            for arabic, hebrew in replacements.items():
                if arabic in matched_text:
                    suggestions.append(matched_text.replace(arabic, hebrew))
        
        elif pattern_name == 'space_before_punctuation':
            # Remove space before punctuation
            suggestions.append(matched_text.replace(' ', ''))
        
        elif pattern_name == 'multiple_spaces':
            # Replace multiple spaces with single space
            suggestions.append(' ')
        
        elif pattern_name == 'misplaced_final':
            # Replace final letters with regular forms
            replacements = {
                'ך': 'כ',
                'ם': 'מ',
                'ן': 'נ',
                'ף': 'פ',
                'ץ': 'צ',
            }
            for final, regular in replacements.items():
                if final in matched_text:
                    suggestions.append(matched_text.replace(final, regular))
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_pattern_statistics(self) -> Dict:
        """
        מחזיר סטטיסטיקות על הדפוסים
        Return statistics about patterns
        """
        return {
            'total_patterns': len(self.patterns),
            'patterns_by_severity': {
                'high': len([p for p in self.patterns if p.severity == 'high']),
                'medium': len([p for p in self.patterns if p.severity == 'medium']),
                'low': len([p for p in self.patterns if p.severity == 'low']),
            },
            'pattern_names': [p.name for p in self.patterns]
        }


# Singleton instance
_pattern_detector_instance = None


def get_pattern_detector() -> ErrorPatternDetector:
    """
    קבל מופע יחיד של מזהה הדפוסים
    Get singleton pattern detector instance
    """
    global _pattern_detector_instance
    if _pattern_detector_instance is None:
        _pattern_detector_instance = ErrorPatternDetector()
    return _pattern_detector_instance
