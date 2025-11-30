#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Error Detector
Detects various types of OCR errors using multiple techxxxxxxxxx"""

import re
import logging
from typing import List, Dict, Optional, Set
from statistics import mean
import Levenshtein

logger = logging.getLogger(__name__)


class OCRErrorDetector:
    """
    Detects OCR errors using multiple strategies:
    1. Confidence-based detection
    2. Pattern-based detection
    3. Character confusion detection
    4. Context analysis
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize error detector
        
        Args:
            confidence_threshold: Minimum confidence for accepting OCR results
        """
        self.confidence_threshold = confidence_threshold
        
        # Hebrew character confusion patterns (OCR common mistakes)
        self.hebrew_confusion = {
            'ח': ['ה', 'כ', 'ת'],
            'ה': ['ח', 'ת', 'ן'],
            'ב': ['כ', 'ד', 'פ'],
            'כ': ['ב', 'ח', 'ר'],
            'ו': ['ז', 'י', 'ן'],
            'ז': ['ו', 'ן'],
            'נ': ['ג', 'צ', 'ך'],
            'ג': ['נ', 'ע', 'ך'],
            'ר': ['ד', 'ך', 'ן'],
            'ד': ['ר', 'ה', 'ך'],
            'ם': ['ס', 'ן', 'ם'],
            'ס': ['ם', 'ם', 'ע'],
            'ן': ['ז', 'ם', 'ך'],
            'ך': ['ר', 'ל', 'ן'],
            'ת': ['ח', 'ה'],
            'ש': ['ש', 'ששש'],  # Sometimes OCR duplicates
            'פ': ['ב', 'כ'],
            'צ': ['נ', 'ץ'],
            'ע': ['ס', 'ג'],
            'ל': ['ך', 'ד'],
        }
        
        # Arabic character confusion
        self.arabic_confusion = {
            'ب': ['ت', 'ث', 'ن', 'ي'],
            'ت': ['ب', 'ث', 'ن'],
            'ث': ['ب', 'ت', 'ن'],
            'ج': ['ح', 'خ'],
            'ح': ['ج', 'خ'],
            'خ': ['ج', 'ح'],
            'د': ['ذ'],
            'ذ': ['د'],
            'ر': ['ز'],
            'ز': ['ر'],
            'س': ['ش'],
            'ش': ['س'],
            'ص': ['ض'],
            'ض': ['ص'],
            'ط': ['ظ'],
            'ظ': ['ط'],
            'ع': ['غ'],
            'غ': ['ع'],
            'ف': ['ق'],
            'ق': ['ف'],
        }
        
        # Suspicious patterns (regex)
        self.suspicious_patterns = [
            (r'(.)\1{3,}', 'repeated_chars'),  # 3+ repeated chars (likely error)
            (r'[^\u0590-\u05FF\u0600-\u06FF\sA-Za-z0-9.,;:!?\'"\-()]', 'invalid_chars'),
            (r'\s{3,}', 'excessive_spaces'),
            (r'[א-ת]{20,}', 'very_long_word'),  # Hebrew words >20 chars suspicious
            (r'[\u0600-\u06FF]{20,}', 'very_long_word'),  # Arabic words >20 chars
        ]
        
        logger.info(f"OCR Error Detector initialized (threshold={confidence_threshold})")
    
    def detect_errors(self, transcription_data: Dict) -> List[Dict]:
        """
        Detect all types of errors in transcription
        
        Args:
            transcription_data: Dict with 'lines' containing LineTranscription data
            
        Returns:
            List of detected errors with metadata
        """
        all_errors = []
        
        lines = transcription_data.get('lines', [])
        
        for line_idx, line_data in enumerate(lines):
            # Extract line information
            content = line_data.get('content', '')
            avg_confidence = line_data.get('avg_confidence')
            graphs = line_data.get('graphs', [])
            
            # 1. Confidence-based errors
            confidence_errors = self._detect_low_confidence(
                content, avg_confidence, graphs, line_idx
            )
            all_errors.extend(confidence_errors)
            
            # 2. Pattern-based errors
            pattern_errors = self._detect_suspicious_patterns(content, line_idx)
            all_errors.extend(pattern_errors)
            
            # 3. Character confusion errors
            confusion_errors = self._detect_character_confusion(
                content, graphs, line_idx
            )
            all_errors.extend(confusion_errors)
            
            # 4. Context errors (unusual sequences)
            context_errors = self._detect_context_errors(content, line_idx)
            all_errors.extend(context_errors)
        
        # Sort by severity
        all_errors.sort(key=lambda x: x.get('severity_score', 0), reverse=True)
        
        return all_errors
    
    def _detect_low_confidence(
        self, 
        content: str, 
        avg_confidence: Optional[float],
        graphs: List[Dict],
        line_idx: int
    ) -> List[Dict]:
        """Detect errors based on low confidence scores"""
        errors = []
        
        # Line-level confidence check
        if avg_confidence is not None and avg_confidence < self.confidence_threshold:
            errors.append({
                'type': 'low_confidence_line',
                'line_index': line_idx,
                'content': content,
                'confidence': avg_confidence,
                'severity': 'medium',
                'severity_score': 50 + (1 - avg_confidence) * 30,
                'message': f'Line has low confidence: {avg_confidence:.2%}',
                'recommendation': 'Review entire line carefully'
            })
        
        # Character-level confidence check
        if graphs:
            low_conf_chars = []
            for graph in graphs:
                char = graph.get('c', '')
                conf = graph.get('confidence')
                
                if conf is not None and conf < self.confidence_threshold:
                    low_conf_chars.append({
                        'char': char,
                        'confidence': conf,
                        'position': len(low_conf_chars)
                    })
            
            if low_conf_chars:
                errors.append({
                    'type': 'low_confidence_characters',
                    'line_index': line_idx,
                    'content': content,
                    'characters': low_conf_chars,
                    'count': len(low_conf_chars),
                    'severity': 'high' if len(low_conf_chars) > 3 else 'medium',
                    'severity_score': 60 + len(low_conf_chars) * 5,
                    'message': f'{len(low_conf_chars)} characters with low confidence',
                    'recommendation': 'Check highlighted characters'
                })
        
        return errors
    
    def _detect_suspicious_patterns(self, content: str, line_idx: int) -> List[Dict]:
        """Detect suspicious patterns using regex"""
        errors = []
        
        for pattern, error_type in self.suspicious_patterns:
            matches = list(re.finditer(pattern, content))
            
            for match in matches:
                severity = self._calculate_pattern_severity(error_type, match)
                
                errors.append({
                    'type': f'suspicious_pattern_{error_type}',
                    'line_index': line_idx,
                    'content': content,
                    'matched_text': match.group(),
                    'position': match.start(),
                    'severity': severity,
                    'severity_score': 40 if severity == 'medium' else 70,
                    'message': self._get_pattern_message(error_type, match),
                    'recommendation': self._get_pattern_recommendation(error_type)
                })
        
        return errors
    
    def _detect_character_confusion(
        self, 
        content: str, 
        graphs: List[Dict],
        line_idx: int
    ) -> List[Dict]:
        """Detect potential character confusion based on common OCR mistakes"""
        errors = []
        
        # Detect language
        has_hebrew = bool(re.search('[\u0590-\u05FF]', content))
        has_arabic = bool(re.search('[\u0600-\u06FF]', content))
        
        confusion_map = {}
        if has_hebrew:
            confusion_map.update(self.hebrew_confusion)
        if has_arabic:
            confusion_map.update(self.arabic_confusion)
        
        if not graphs or not confusion_map:
            return errors
        
        # Check each character
        for i, graph in enumerate(graphs):
            char = graph.get('c', '')
            conf = graph.get('confidence')
            
            # If character has low confidence AND is in confusion map
            if conf and conf < 0.8 and char in confusion_map:
                confused_with = confusion_map[char]
                
                errors.append({
                    'type': 'character_confusion',
                    'line_index': line_idx,
                    'content': content,
                    'character': char,
                    'position': i,
                    'confidence': conf,
                    'possible_confusion': confused_with,
                    'severity': 'high' if conf < 0.5 else 'medium',
                    'severity_score': 65 + (1 - conf) * 20,
                    'message': f'Character "{char}" (conf: {conf:.2%}) may be confused with {confused_with}',
                    'recommendation': f'Check if "{char}" should be one of: {", ".join(confused_with)}'
                })
        
        return errors
    
    def _detect_context_errors(self, content: str, line_idx: int) -> List[Dict]:
        """Detect errors based on unusual character sequences"""
        errors = []
        
        # Check for unusual sequences
        # Example: consonant clusters that don't make sense in Hebrew
        hebrew_chars = re.findall('[\u0590-\u05FF]', content)
        
        if len(hebrew_chars) > 0:
            # Check for sequences that are unlikely in Hebrew
            # (This is a simplified check - can be expanded)
            
            # Check for too many final letters in non-final positions
            final_letters = {'ך', 'ם', 'ן', 'ף', 'ץ'}
            words = content.split()
            
            for word_idx, word in enumerate(words):
                hebrew_word = ''.join(re.findall('[\u0590-\u05FF]', word))
                if len(hebrew_word) > 1:
                    # Check if final letters appear in middle
                    middle_chars = hebrew_word[:-1]
                    final_in_middle = [c for c in middle_chars if c in final_letters]
                    
                    if final_in_middle:
                        errors.append({
                            'type': 'context_error_final_letters',
                            'line_index': line_idx,
                            'content': content,
                            'word': word,
                            'word_index': word_idx,
                            'invalid_chars': final_in_middle,
                            'severity': 'high',
                            'severity_score': 75,
                            'message': f'Final letter(s) {final_in_middle} in wrong position',
                            'recommendation': 'Check word structure - may be OCR error'
                        })
        
        return errors
    
    def _calculate_pattern_severity(self, error_type: str, match: re.Match) -> str:
        """Calculate severity based on pattern type"""
        if error_type == 'repeated_chars':
            repeat_count = len(match.group())
            return 'high' if repeat_count > 5 else 'medium'
        elif error_type == 'invalid_chars':
            return 'high'
        elif error_type == 'excessive_spaces':
            return 'low'
        elif error_type == 'very_long_word':
            return 'medium'
        return 'medium'
    
    def _get_pattern_message(self, error_type: str, match: re.Match) -> str:
        """Get human-readable message for pattern error"""
        messages = {
            'repeated_chars': f'Repeated characters detected: "{match.group()}"',
            'invalid_chars': f'Invalid character(s) detected: "{match.group()}"',
            'excessive_spaces': 'Excessive spacing detected',
            'very_long_word': f'Unusually long word: "{match.group()}" ({len(match.group())} chars)',
        }
        return messages.get(error_type, 'Suspicious pattern detected')
    
    def _get_pattern_recommendation(self, error_type: str) -> str:
        """Get recommendation for fixing pattern error"""
        recommendations = {
            'repeated_chars': 'Check if character should appear only once',
            'invalid_chars': 'Remove or replace invalid characters',
            'excessive_spaces': 'Reduce to single space',
            'very_long_word': 'Check if this should be multiple words',
        }
        return recommendations.get(error_type, 'Review and correct manually')
    
    def generate_error_report(self, errors: List[Dict]) -> Dict:
        """
        Generate summary report of detected errors
        
        Returns:
            Dictionary with statistics and grouped errors
        """
        if not errors:
            return {
                'total_errors': 0,
                'by_severity': {'high': 0, 'medium': 0, 'low': 0},
                'by_type': {},
                'recommendations': ['No errors detected - good OCR quality!']
            }
        
        # Count by severity
        by_severity = {'high': 0, 'medium': 0, 'low': 0}
        for error in errors:
            severity = error.get('severity', 'medium')
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Count by type
        by_type = {}
        for error in errors:
            error_type = error.get('type', 'unknown')
            by_type[error_type] = by_type.get(error_type, 0) + 1
        
        # Calculate average severity score
        severity_scores = [e.get('severity_score', 50) for e in errors]
        avg_severity = mean(severity_scores) if severity_scores else 0
        
        # Generate recommendations
        recommendations = []
        if by_severity['high'] > 0:
            recommendations.append(f'⚠️ {by_severity["high"]} high-severity errors require immediate attention')
        if by_severity['medium'] > 5:
            recommendations.append(f'⚡ {by_severity["medium"]} medium-severity errors should be reviewed')
        if 'low_confidence_line' in by_type:
            recommendations.append(f'📊 {by_type["low_confidence_line"]} lines with low confidence - review carefully')
        if 'character_confusion' in by_type:
            recommendations.append(f'🔤 {by_type["character_confusion"]} possible character confusions detected')
        
        if not recommendations:
            recommendations.append('✅ Minor errors detected - review flagged items')
        
        return {
            'total_errors': len(errors),
            'average_severity_score': avg_severity,
            'by_severity': by_severity,
            'by_type': by_type,
            'recommendations': recommendations,
            'quality_score': max(0, 100 - avg_severity),  # Inverse of severity
        }
