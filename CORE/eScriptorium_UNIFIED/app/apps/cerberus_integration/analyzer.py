"""
CERberus Analyzer - Core CER Calculation Engine
================================================

Adapted from WHaverals/CERberus for eScriptorium integration.
"""

import re
import Levenshtein
from typing import Dict, List, Tuple, Optional
import pandas as pd
import json
from collections import defaultdict


class CERAnalyzer:
    """
    Character Error Rate (CER) analyzer with advanced statistics.
    
    Supports:
    - Basic CER calculation
    - Character-level statistics
    - Unicode block analysis
    - Confusion matrices
    - Customizable preprocessing
    """
    
    def __init__(self):
        """Initialize CER Analyzer"""
        self.last_results = None
        
    def calculate_cer(
        self,
        reference: str,
        hypothesis: str,
        ignore_punctuation: bool = False,
        ignore_case: bool = False,
        ignore_whitespace: bool = False,
        ignore_numbers: bool = False,
        ignore_chars: Optional[str] = None,
        ignore_newlines_and_returns: bool = False,
        unicode_ranges: Optional[Dict[str, list]] = None,
        discard_lines_with_chars: Optional[str] = None,
        replace_chars: Optional[str] = None,
        replacement_chars: Optional[str] = None,
    ) -> Dict:
        """
        Calculate Character Error Rate between reference and hypothesis.
        
        Args:
            reference: Ground truth text
            hypothesis: OCR output text
            ignore_punctuation: Remove punctuation from both texts
            ignore_case: Convert to lowercase
            ignore_whitespace: Remove all whitespace
            ignore_numbers: Remove digits
            ignore_chars: String of characters to ignore
            ignore_newlines_and_returns: Remove \\n and \\r
            unicode_ranges: Dict of {name: [start, end]} for Unicode block analysis
            discard_lines_with_chars: Discard lines containing these characters
            replace_chars: Characters to replace
            replacement_chars: Replacement characters
            
        Returns:
            Dict with CER results and statistics
        """
        # Apply character replacements if specified
        if replace_chars and replacement_chars:
            reference = reference.replace(replace_chars, replacement_chars)
            hypothesis = hypothesis.replace(replace_chars, replacement_chars)
        
        # Split into lines
        reference_lines = reference.splitlines()
        hypothesis_lines = hypothesis.splitlines()
        original_lines_count = len(reference_lines)
        
        # Discard lines with specified characters
        if discard_lines_with_chars:
            combined_lines = list(zip(reference_lines, hypothesis_lines))
            combined_lines = [
                lines for lines in combined_lines
                if not any(char in lines[0] for char in discard_lines_with_chars)
                and not any(char in lines[1] for char in discard_lines_with_chars)
            ]
            if combined_lines:
                reference_lines, hypothesis_lines = zip(*combined_lines)
            else:
                reference_lines, hypothesis_lines = [], []
        
        discarded_lines_count = original_lines_count - len(reference_lines)
        
        # Rejoin lines
        reference = "\\n".join(reference_lines)
        hypothesis = "\\n".join(hypothesis_lines)
        
        # Apply preprocessing
        if ignore_case:
            reference = reference.lower()
            hypothesis = hypothesis.lower()
        
        if ignore_punctuation:
            reference = re.sub(r'[^\\w\\s]', '', reference)
            hypothesis = re.sub(r'[^\\w\\s]', '', hypothesis)
        
        if ignore_whitespace:
            reference = re.sub(r'\\s', '', reference)
            hypothesis = re.sub(r'\\s', '', hypothesis)
        
        if ignore_numbers:
            reference = re.sub(r'\\d', '', reference)
            hypothesis = re.sub(r'\\d', '', hypothesis)
        
        if ignore_chars:
            for char in ignore_chars:
                reference = reference.replace(char, '')
                hypothesis = hypothesis.replace(char, '')
        
        if ignore_newlines_and_returns:
            reference = reference.replace('\\n', ' ').replace('\\r', '')
            hypothesis = hypothesis.replace('\\n', ' ').replace('\\r', '')
        
        # Validate reference
        if len(reference) == 0:
            raise ValueError("Reference string length cannot be zero after preprocessing.")
        
        # Calculate Levenshtein distance
        num_correct, num_substitutions, num_insertions, num_deletions, alignments = \
            self._levenshtein_with_alignment(reference, hypothesis)
        
        num_count = len(reference)
        cer_value = round(((num_substitutions + num_insertions + num_deletions) / num_count) * 100, 2)
        
        # Calculate character statistics
        char_stats = self._calculate_char_stats(reference, hypothesis, alignments)
        
        # Calculate Unicode block statistics if ranges provided
        block_stats = None
        if unicode_ranges:
            block_stats = self._calculate_block_stats(reference, hypothesis, unicode_ranges, alignments)
        
        # Calculate confusion statistics
        confusion_stats = self._calculate_confusion_stats(alignments)
        
        # Build results
        results = {
            'cer': cer_value,
            'num_correct': num_correct,
            'num_substitutions': num_substitutions,
            'num_insertions': num_insertions,
            'num_deletions': num_deletions,
            'total_characters': num_count,
            'original_lines_count': original_lines_count,
            'discarded_lines_count': discarded_lines_count,
            'processed_lines_count': len(reference_lines),
            'character_statistics': char_stats,
            'block_statistics': block_stats,
            'confusion_statistics': confusion_stats,
        }
        
        self.last_results = results
        return results
    
    def _levenshtein_with_alignment(
        self, reference: str, hypothesis: str
    ) -> Tuple[int, int, int, int, List[Tuple]]:
        """
        Calculate Levenshtein distance with alignment information.
        
        Returns:
            Tuple of (correct, substitutions, insertions, deletions, alignments)
        """
        ops = Levenshtein.editops(reference, hypothesis)
        
        num_correct = 0
        num_substitutions = 0
        num_insertions = 0
        num_deletions = 0
        
        alignments = []
        
        ref_idx = 0
        hyp_idx = 0
        
        for op, ref_pos, hyp_pos in ops:
            # Handle correct characters before this operation
            while ref_idx < ref_pos:
                alignments.append(('correct', reference[ref_idx], hypothesis[hyp_idx]))
                num_correct += 1
                ref_idx += 1
                hyp_idx += 1
            
            # Handle the operation
            if op == 'replace':
                alignments.append(('substitution', reference[ref_pos], hypothesis[hyp_pos]))
                num_substitutions += 1
                ref_idx += 1
                hyp_idx += 1
            elif op == 'insert':
                alignments.append(('insertion', '', hypothesis[hyp_pos]))
                num_insertions += 1
                hyp_idx += 1
            elif op == 'delete':
                alignments.append(('deletion', reference[ref_pos], ''))
                num_deletions += 1
                ref_idx += 1
        
        # Handle remaining correct characters
        while ref_idx < len(reference):
            if hyp_idx < len(hypothesis):
                alignments.append(('correct', reference[ref_idx], hypothesis[hyp_idx]))
                num_correct += 1
            ref_idx += 1
            hyp_idx += 1
        
        return num_correct, num_substitutions, num_insertions, num_deletions, alignments
    
    def _calculate_char_stats(
        self, reference: str, hypothesis: str, alignments: List[Tuple]
    ) -> Dict:
        """Calculate per-character statistics"""
        char_counts = defaultdict(lambda: {'count': 0, 'correct': 0, 'incorrect': 0})
        
        for op, ref_char, hyp_char in alignments:
            if op == 'correct':
                char_counts[ref_char]['count'] += 1
                char_counts[ref_char]['correct'] += 1
            elif op == 'substitution':
                char_counts[ref_char]['count'] += 1
                char_counts[ref_char]['incorrect'] += 1
            elif op == 'deletion':
                char_counts[ref_char]['count'] += 1
                char_counts[ref_char]['incorrect'] += 1
        
        # Convert to list with ratios
        stats = []
        for char, counts in sorted(char_counts.items()):
            total = counts['count']
            stats.append({
                'character': char,
                'count': total,
                'correct': counts['correct'],
                'incorrect': counts['incorrect'],
                'correct_ratio': round(counts['correct'] / total, 4) if total > 0 else 0,
                'incorrect_ratio': round(counts['incorrect'] / total, 4) if total > 0 else 0,
            })
        
        return stats
    
    def _calculate_block_stats(
        self, reference: str, hypothesis: str,
        unicode_ranges: Dict[str, list], alignments: List[Tuple]
    ) -> Dict:
        """Calculate statistics per Unicode block"""
        block_counts = defaultdict(lambda: {'count': 0, 'correct': 0, 'incorrect': 0})
        
        for op, ref_char, hyp_char in alignments:
            if not ref_char:
                continue
            
            # Determine which block this character belongs to
            char_code = ord(ref_char)
            for block_name, (start, end) in unicode_ranges.items():
                if start <= char_code <= end:
                    if op == 'correct':
                        block_counts[block_name]['count'] += 1
                        block_counts[block_name]['correct'] += 1
                    elif op in ('substitution', 'deletion'):
                        block_counts[block_name]['count'] += 1
                        block_counts[block_name]['incorrect'] += 1
                    break
        
        # Convert to list with ratios
        stats = []
        for block, counts in sorted(block_counts.items()):
            total = counts['count']
            stats.append({
                'block': block,
                'count': total,
                'correct': counts['correct'],
                'incorrect': counts['incorrect'],
                'correct_ratio': round(counts['correct'] / total, 4) if total > 0 else 0,
                'incorrect_ratio': round(counts['incorrect'] / total, 4) if total > 0 else 0,
            })
        
        return stats
    
    def _calculate_confusion_stats(self, alignments: List[Tuple]) -> List[Dict]:
        """Calculate confusion matrix statistics"""
        confusions = defaultdict(int)
        
        for op, ref_char, hyp_char in alignments:
            if op == 'substitution':
                confusions[(ref_char, hyp_char)] += 1
        
        # Convert to sorted list
        stats = []
        for (correct_char, generated_char), count in sorted(
            confusions.items(), key=lambda x: x[1], reverse=True
        ):
            stats.append({
                'correct_character': correct_char,
                'generated_character': generated_char,
                'count': count,
            })
        
        # Calculate ratios
        total_confusions = sum(item['count'] for item in stats)
        for item in stats:
            item['ratio'] = round(item['count'] / total_confusions, 4) if total_confusions > 0 else 0
        
        return stats
    
    def export_to_json(self, filepath: str) -> None:
        """Export last results to JSON file"""
        if self.last_results is None:
            raise ValueError("No results to export. Run calculate_cer first.")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.last_results, f, indent=2, ensure_ascii=False)
    
    def export_to_csv(self, filepath: str, data_type: str = 'character') -> None:
        """
        Export statistics to CSV file.
        
        Args:
            filepath: Output CSV file path
            data_type: Type of data to export ('character', 'block', or 'confusion')
        """
        if self.last_results is None:
            raise ValueError("No results to export. Run calculate_cer first.")
        
        if data_type == 'character':
            data = self.last_results.get('character_statistics', [])
        elif data_type == 'block':
            data = self.last_results.get('block_statistics', [])
        elif data_type == 'confusion':
            data = self.last_results.get('confusion_statistics', [])
        else:
            raise ValueError(f"Unknown data_type: {data_type}")
        
        if not data:
            raise ValueError(f"No {data_type} statistics available.")
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')  # UTF-8 with BOM for Excel


# Hebrew and Arabic Unicode ranges (commonly used)
UNICODE_RANGES_HEBREW_ARABIC = {
    'Hebrew': [0x0590, 0x05FF],
    'Arabic': [0x0600, 0x06FF],
    'Arabic Supplement': [0x0750, 0x077F],
    'Arabic Extended-A': [0x08A0, 0x08FF],
    'Basic Latin': [0x0020, 0x007F],
    'Latin-1 Supplement': [0x0080, 0x00FF],
    'Punctuation': [0x2000, 0x206F],
}
