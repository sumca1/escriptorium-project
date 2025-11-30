#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Auto-Corrector
Automatically corrects OCR errors with different confidence modes
"""

import logging
from typing import List, Dict, Optional, Tuple
from .spell_checker import MultilingualSpellChecker
from .error_detector import OCRErrorDetector

logger = logging.getLogger(__name__)


class AutoCorrector:
    """
    Automatic OCR correction with multiple modes:
    - safe: Only high-confidence corrections (>90%)
    - review: Flag for manual review
    - aggressive: Apply all suggestions
    """
    
    def __init__(self):
        """Initialize auto-corrector with spell checker and error detector"""
        self.spell_checker = MultilingualSpellChecker()
        self.error_detector = OCRErrorDetector()
        logger.info("Auto-corrector initialized")
    
    def correct_transcription(
        self,
        transcription_data: Dict,
        mode: str = 'safe',
        confidence_threshold: float = 0.9
    ) -> Dict:
        """
        Auto-correct transcription with specified mode
        
        Args:
            transcription_data: Dict with transcription information
            mode: 'safe', 'review', or 'aggressive'
            confidence_threshold: Minimum confidence for 'safe' mode
            
        Returns:
            Dictionary with:
            - corrected_lines: List of corrected line data
            - corrections_made: List of applied corrections
            - review_needed: List of items flagged for review
            - statistics: Correction statistics
        """
        if mode not in ['safe', 'review', 'aggressive']:
            raise ValueError(f"Invalid mode: {mode}. Must be 'safe', 'review', or 'aggressive'")
        
        corrected_lines = []
        corrections_made = []
        review_needed = []
        
        lines = transcription_data.get('lines', [])
        language = transcription_data.get('language', None)
        
        for line_idx, line_data in enumerate(lines):
            content = line_data.get('content', '')
            avg_confidence = line_data.get('avg_confidence')
            graphs = line_data.get('graphs', [])
            
            # Detect language if not specified
            if not language:
                language = self.spell_checker.detect_language(content)
            
            # Check spelling
            spell_result = self.spell_checker.check_text(content, language)
            
            # check_text returns a list of errors directly
            spell_errors = spell_result if isinstance(spell_result, list) else []
            
            if not spell_errors:
                # No spelling errors - keep original
                corrected_lines.append(line_data.copy())
                continue
            
            # Apply corrections based on mode
            if mode == 'safe':
                corrected_content, line_corrections = self._safe_correct(
                    content, spell_errors, confidence_threshold
                )
            elif mode == 'review':
                corrected_content, line_corrections = self._review_correct(
                    content, spell_errors, line_idx
                )
            elif mode == 'aggressive':
                corrected_content, line_corrections = self._aggressive_correct(
                    content, spell_errors
                )
            
            # Update line data
            corrected_line = line_data.copy()
            corrected_line['content'] = corrected_content
            corrected_line['original_content'] = content
            corrected_line['was_corrected'] = len(line_corrections) > 0
            
            corrected_lines.append(corrected_line)
            
            # Add to corrections log
            for correction in line_corrections:
                correction['line_index'] = line_idx
                corrections_made.append(correction)
            
            # Flag for review if needed (in review mode)
            if mode == 'review' and spell_errors:
                review_needed.append({
                    'line_index': line_idx,
                    'original': content,
                    'suggested': corrected_content,
                    'errors': spell_errors,
                    'confidence': avg_confidence
                })
        
        # Calculate statistics
        statistics = self._calculate_statistics(
            lines, corrected_lines, corrections_made, review_needed
        )
        
        return {
            'corrected_lines': corrected_lines,
            'corrections_made': corrections_made,
            'review_needed': review_needed,
            'statistics': statistics,
            'mode': mode
        }
    
    def _safe_correct(
        self,
        content: str,
        errors: List[Dict],
        confidence_threshold: float
    ) -> Tuple[str, List[Dict]]:
        """
        Safe mode: Only apply high-confidence corrections
        
        Returns:
            (corrected_text, list_of_corrections)
        """
        corrected_text = content
        corrections = []
        
        for error in errors:
            suggestions = error.get('suggestions', [])
            if not suggestions:
                continue
            
            # Get best suggestion
            word = error.get('word', '')
            
            # For safe mode, we need high confidence
            if error.get('confidence', 0) >= confidence_threshold:
                # Use top suggestion
                suggestion = suggestions[0]
                
                # Replace in text
                corrected_text = corrected_text.replace(word, suggestion, 1)
                
                corrections.append({
                    'original': word,
                    'corrected': suggestion,
                    'confidence': error.get('confidence'),
                    'type': 'safe_auto_correct'
                })
        
        return corrected_text, corrections
    
    def _review_correct(
        self,
        content: str,
        errors: List[Dict],
        line_idx: int
    ) -> Tuple[str, List[Dict]]:
        """
        Review mode: Flag errors for manual review, don't auto-correct
        
        Returns:
            (original_text, list_of_flagged_items)
        """
        corrections = []
        
        for error in errors:
            corrections.append({
                'original': error.get('word', ''),
                'suggestions': error.get('suggestions', []),
                'confidence': error.get('confidence'),
                'type': 'flagged_for_review',
                'needs_review': True
            })
        
        # Return original text unchanged in review mode
        return content, corrections
    
    def _aggressive_correct(
        self,
        content: str,
        errors: List[Dict]
    ) -> Tuple[str, List[Dict]]:
        """
        Aggressive mode: Apply all available corrections
        
        Returns:
            (corrected_text, list_of_corrections)
        """
        corrected_text = content
        corrections = []
        
        for error in errors:
            suggestions = error.get('suggestions', [])
            if not suggestions:
                continue
            
            word = error.get('word', '')
            suggestion = suggestions[0]  # Always use top suggestion
            
            # Replace in text
            corrected_text = corrected_text.replace(word, suggestion, 1)
            
            corrections.append({
                'original': word,
                'corrected': suggestion,
                'confidence': error.get('confidence'),
                'type': 'aggressive_auto_correct',
                'all_suggestions': suggestions
            })
        
        return corrected_text, corrections
    
    def correct_with_context(
        self,
        transcription_data: Dict,
        previous_lines: List[str] = None,
        next_lines: List[str] = None
    ) -> Dict:
        """
        Context-aware correction using surrounding lines
        
        Args:
            transcription_data: Current transcription data
            previous_lines: Previous lines for context
            next_lines: Following lines for context
            
        Returns:
            Correction results with context analysis
        """
        # Build context
        context = {
            'previous': previous_lines or [],
            'next': next_lines or []
        }
        
        # Detect common words/patterns in context
        context_words = set()
        for line in context['previous'] + context['next']:
            context_words.update(line.split())
        
        # Perform standard correction
        result = self.correct_transcription(transcription_data, mode='safe')
        
        # Enhance with context
        for correction in result['corrections_made']:
            original = correction['original']
            corrected = correction['corrected']
            
            # Boost confidence if corrected word appears in context
            if corrected in context_words:
                correction['confidence'] = min(1.0, correction.get('confidence', 0.5) + 0.2)
                correction['context_boost'] = True
        
        result['used_context'] = True
        result['context_words_count'] = len(context_words)
        
        return result
    
    def batch_correct(
        self,
        transcriptions: List[Dict],
        mode: str = 'safe'
    ) -> Dict:
        """
        Correct multiple transcriptions in batch
        
        Args:
            transcriptions: List of transcription dicts
            mode: Correction mode
            
        Returns:
            Aggregated correction results
        """
        all_results = []
        total_corrections = 0
        total_review_needed = 0
        
        for trans_idx, trans_data in enumerate(transcriptions):
            result = self.correct_transcription(trans_data, mode=mode)
            
            result['transcription_index'] = trans_idx
            all_results.append(result)
            
            total_corrections += len(result['corrections_made'])
            total_review_needed += len(result['review_needed'])
        
        return {
            'results': all_results,
            'summary': {
                'total_transcriptions': len(transcriptions),
                'total_corrections': total_corrections,
                'total_review_needed': total_review_needed,
                'mode': mode
            }
        }
    
    def _calculate_statistics(
        self,
        original_lines: List[Dict],
        corrected_lines: List[Dict],
        corrections: List[Dict],
        review_items: List[Dict]
    ) -> Dict:
        """Calculate correction statistics"""
        total_lines = len(original_lines)
        corrected_count = sum(1 for line in corrected_lines if line.get('was_corrected', False))
        
        # Calculate correction rate
        correction_rate = corrected_count / total_lines if total_lines > 0 else 0
        
        # Average confidence of corrections
        confidences = [c.get('confidence', 0) for c in corrections if c.get('confidence')]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'total_lines': total_lines,
            'lines_corrected': corrected_count,
            'correction_rate': correction_rate,
            'total_corrections': len(corrections),
            'average_correction_confidence': avg_confidence,
            'items_needing_review': len(review_items)
        }
    
    def suggest_best_mode(self, transcription_data: Dict) -> Dict[str, any]:
        """
        Analyze transcription and suggest best correction mode
        
        Returns:
            Dictionary with:
            - suggested_mode: str ('safe', 'review', or 'aggressive')
            - explanation: str (reasoning)
            - avg_confidence: float
            - total_errors: int
            - quality_score: int
        """
        # Detect errors first
        errors = self.error_detector.detect_errors(transcription_data)
        error_report = self.error_detector.generate_error_report(errors)
        
        high_severity = error_report['by_severity'].get('high', 0)
        total_errors = error_report['total_errors']
        quality_score = error_report.get('quality_score', 50)
        
        # Calculate average confidence
        lines = transcription_data.get('lines', [])
        confidences = [line.get('avg_confidence', 0) for line in lines if line.get('avg_confidence')]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Decision logic
        if quality_score > 85:
            # High quality - safe to auto-correct
            mode = 'safe'
            explanation = 'High quality OCR - safe to auto-correct with high confidence'
        elif quality_score > 60 and high_severity < 5:
            # Medium quality with few critical errors - safe mode
            mode = 'safe'
            explanation = f'Medium-high quality with only {high_severity} critical errors - safe mode recommended'
        elif high_severity > 10 or quality_score < 40:
            # Many critical errors or low quality - needs review
            mode = 'review'
            explanation = f'Quality score {quality_score} with {high_severity} critical errors - manual review recommended'
        else:
            # Middle ground - review recommended
            mode = 'review'
            explanation = f'Medium quality (score: {quality_score}) - review mode recommended for safety'
        
        return {
            'suggested_mode': mode,
            'explanation': explanation,
            'avg_confidence': avg_confidence,
            'total_errors': total_errors,
            'quality_score': quality_score
        }
