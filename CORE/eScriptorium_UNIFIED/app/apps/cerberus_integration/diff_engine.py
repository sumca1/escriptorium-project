"""
Character-level Diff Engine for CERberus

Compares ground truth and hypothesis transcriptions at character level
and provides detailed alignment information for visualization.

Usage:
    engine = CharacterDiffEngine()
    result = engine.diff(ground_truth, hypothesis)
    # result contains aligned characters with diff type (correct/substitution/insertion/deletion)
"""

import difflib
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class CharacterDiff:
    """Represents a single character with its diff status"""
    position: int
    character: str
    diff_type: str  # 'correct', 'substitution', 'insertion', 'deletion'
    expected: str = None  # For substitutions, what was expected
    confidence: float = 1.0


class CharacterDiffEngine:
    """
    Performs character-level diff between ground truth and hypothesis transcriptions.
    
    Supports:
    - Direct character comparison (fast)
    - Aligned character comparison (more accurate for case of insertions/deletions)
    - Unicode support (Hebrew, Arabic)
    - RTL script handling
    """
    
    def __init__(self, normalize: bool = True, ignore_case: bool = False):
        """
        Initialize diff engine.
        
        Args:
            normalize: Whether to normalize Unicode (decompose combining marks)
            ignore_case: Whether to ignore case differences
        """
        self.normalize = normalize
        self.ignore_case = ignore_case
    
    def diff(self, ground_truth: str, hypothesis: str) -> Dict:
        """
        Compare ground truth and hypothesis at character level.
        
        Args:
            ground_truth: Expected/reference text
            hypothesis: OCR output text
            
        Returns:
            Dictionary with:
            - diffs: List of CharacterDiff objects
            - alignment: List of tuples [(gt_char, hyp_char, status), ...]
            - summary: Statistics (correct, substitutions, insertions, deletions)
            - visualization: Data for HTML/Vue visualization
        """
        
        # Preprocess if needed
        gt = self._preprocess(ground_truth)
        hyp = self._preprocess(hypothesis)
        
        # Get character-level alignment
        alignment = self._align_characters(gt, hyp)
        
        # Create diff list with metadata
        diffs = []
        gt_pos = 0
        hyp_pos = 0
        
        for gt_char, hyp_char, status in alignment:
            if status == 'correct':
                diffs.append(CharacterDiff(
                    position=gt_pos,
                    character=gt_char,
                    diff_type='correct',
                    confidence=1.0
                ))
                gt_pos += 1
                hyp_pos += 1
            elif status == 'substitution':
                diffs.append(CharacterDiff(
                    position=gt_pos,
                    character=hyp_char,
                    diff_type='substitution',
                    expected=gt_char,
                    confidence=0.0
                ))
                gt_pos += 1
                hyp_pos += 1
            elif status == 'deletion':
                diffs.append(CharacterDiff(
                    position=gt_pos,
                    character=None,
                    diff_type='deletion',
                    expected=gt_char,
                    confidence=0.0
                ))
                gt_pos += 1
            elif status == 'insertion':
                diffs.append(CharacterDiff(
                    position=gt_pos,
                    character=hyp_char,
                    diff_type='insertion',
                    confidence=0.0
                ))
                hyp_pos += 1
        
        # Calculate summary
        summary = {
            'total_characters': len(gt),
            'correct': len([d for d in diffs if d.diff_type == 'correct']),
            'substitutions': len([d for d in diffs if d.diff_type == 'substitution']),
            'insertions': len([d for d in diffs if d.diff_type == 'insertion']),
            'deletions': len([d for d in diffs if d.diff_type == 'deletion']),
        }
        
        # Calculate accuracy
        total_errors = (summary['substitutions'] + summary['insertions'] + 
                       summary['deletions'])
        summary['accuracy'] = (summary['correct'] / len(gt) * 100) if len(gt) > 0 else 0
        summary['error_rate'] = (total_errors / len(gt) * 100) if len(gt) > 0 else 0
        
        # Create visualization data
        visualization = self._create_visualization(diffs, gt, hyp)
        
        return {
            'diffs': diffs,
            'alignment': alignment,
            'summary': summary,
            'visualization': visualization,
            'ground_truth': gt,
            'hypothesis': hyp
        }
    
    def _preprocess(self, text: str) -> str:
        """Preprocess text for comparison."""
        if self.normalize:
            import unicodedata
            text = unicodedata.normalize('NFD', text)
        
        if self.ignore_case:
            text = text.lower()
        
        return text
    
    def _align_characters(self, ground_truth: str, hypothesis: str) -> List[Tuple]:
        """
        Align characters from ground truth and hypothesis.
        
        Uses difflib.SequenceMatcher for intelligent alignment that handles
        insertions and deletions correctly.
        
        Returns:
            List of tuples: (gt_char, hyp_char, status)
            Where status is 'correct', 'substitution', 'insertion', or 'deletion'
        """
        
        matcher = difflib.SequenceMatcher(None, ground_truth, hypothesis)
        alignment = []
        
        # Track positions in both strings
        gt_pos = 0
        hyp_pos = 0
        
        # Get matching blocks
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Matching characters
                for i in range(i1, i2):
                    alignment.append((ground_truth[i], hypothesis[j1 + (i - i1)], 'correct'))
                gt_pos = i2
                hyp_pos = j2
            
            elif tag == 'replace':
                # Substitutions or complex edits
                # Try to pair up characters
                gt_chars = ground_truth[i1:i2]
                hyp_chars = hypothesis[j1:j2]
                
                if len(gt_chars) == len(hyp_chars):
                    # Same length - treat as substitutions
                    for i, (gt_c, hyp_c) in enumerate(zip(gt_chars, hyp_chars)):
                        alignment.append((gt_c, hyp_c, 'substitution'))
                else:
                    # Different length - some chars are deleted/inserted
                    # For simplicity, treat first N as substitutions
                    min_len = min(len(gt_chars), len(hyp_chars))
                    for i in range(min_len):
                        alignment.append((gt_chars[i], hyp_chars[i], 'substitution'))
                    
                    # Remaining chars in GT are deletions
                    for i in range(min_len, len(gt_chars)):
                        alignment.append((gt_chars[i], None, 'deletion'))
                    
                    # Remaining chars in hypothesis are insertions
                    for j in range(min_len, len(hyp_chars)):
                        alignment.append((None, hyp_chars[j], 'insertion'))
                
                gt_pos = i2
                hyp_pos = j2
            
            elif tag == 'insert':
                # Insertions in hypothesis
                for j in range(j1, j2):
                    alignment.append((None, hypothesis[j], 'insertion'))
                hyp_pos = j2
            
            elif tag == 'delete':
                # Deletions from ground truth
                for i in range(i1, i2):
                    alignment.append((ground_truth[i], None, 'deletion'))
                gt_pos = i2
        
        return alignment
    
    def _create_visualization(self, diffs: List[CharacterDiff], 
                            ground_truth: str, hypothesis: str) -> Dict:
        """
        Create data structure for visualization in UI.
        
        Returns HTML-friendly representation for Vue components.
        """
        
        # Split by line for display
        gt_lines = ground_truth.split('\n')
        hyp_lines = hypothesis.split('\n')
        
        # Create colored HTML for ground truth
        gt_html = self._create_html_with_highlights(
            diffs, ground_truth, 'ground_truth'
        )
        
        # Create colored HTML for hypothesis
        hyp_html = self._create_html_with_highlights(
            diffs, hypothesis, 'hypothesis'
        )
        
        return {
            'ground_truth_html': gt_html,
            'hypothesis_html': hyp_html,
            'ground_truth_lines': gt_lines,
            'hypothesis_lines': hyp_lines,
            'has_differences': any(d.diff_type != 'correct' for d in diffs)
        }
    
    def _create_html_with_highlights(self, diffs: List[CharacterDiff], 
                                     text: str, source: str) -> str:
        """
        Create HTML with character-level highlighting.
        
        Returns HTML string with <span> tags for colored highlighting.
        """
        
        html_parts = []
        char_index = 0
        
        for diff in diffs:
            if diff.character is None:
                # Deletion marker (show expected character in different color)
                if source == 'ground_truth':
                    html_parts.append(
                        f'<span class="diff-deletion" title="حُذِفَ: {diff.expected}">'
                        f'{diff.expected}</span>'
                    )
                continue
            
            if diff.diff_type == 'correct':
                html_parts.append(diff.character)
                char_index += 1
            
            elif diff.diff_type == 'substitution':
                if source == 'hypothesis':
                    html_parts.append(
                        f'<span class="diff-substitution" '
                        f'title="Expected: {diff.expected}">'
                        f'{diff.character}</span>'
                    )
                else:  # ground_truth
                    html_parts.append(
                        f'<span class="diff-substitution" '
                        f'title="Got: {diff.character}">'
                        f'{diff.expected}</span>'
                    )
                char_index += 1
            
            elif diff.diff_type == 'insertion':
                if source == 'hypothesis':
                    html_parts.append(
                        f'<span class="diff-insertion" title="Extra character">'
                        f'{diff.character}</span>'
                    )
            
            elif diff.diff_type == 'deletion':
                if source == 'ground_truth':
                    html_parts.append(
                        f'<span class="diff-deletion" title="Missing character">'
                        f'{diff.expected}</span>'
                    )
        
        return ''.join(html_parts)


def compare_transcriptions(ground_truth: str, hypothesis: str,
                          ignore_case: bool = False) -> Dict:
    """
    Convenience function to compare two transcriptions.
    
    Args:
        ground_truth: Reference/expected text
        hypothesis: OCR output text
        ignore_case: Whether to ignore case
        
    Returns:
        Dictionary with diff results
    """
    engine = CharacterDiffEngine(ignore_case=ignore_case)
    return engine.diff(ground_truth, hypothesis)


if __name__ == '__main__':
    # Example usage
    gt = "שלום עולם"
    hyp = "שלום אולם"
    
    result = compare_transcriptions(gt, hyp)
    
    print(f"Ground Truth: {result['ground_truth']}")
    print(f"Hypothesis:  {result['hypothesis']}")
    print(f"\nSummary:")
    print(f"  Correct: {result['summary']['correct']}")
    print(f"  Substitutions: {result['summary']['substitutions']}")
    print(f"  Insertions: {result['summary']['insertions']}")
    print(f"  Deletions: {result['summary']['deletions']}")
    print(f"  Accuracy: {result['summary']['accuracy']:.2f}%")
