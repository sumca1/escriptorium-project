#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text Alignment Service (Passim-inspired)
Flask microservice for aligning similar text passages between documents

Algorithms:
- Sequence Matching (difflib.SequenceMatcher)
- Levenshtein Distance (edit distance)
- Jaccard Similarity (token overlap)
- Smith-Waterman (local alignment)
"""

import os
import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from flask import Flask, request, jsonify

try:
    import Levenshtein
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False

import jellyfish
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@dataclass
class AlignmentPair:
    """Represents an aligned pair of text segments"""
    text1: str
    text2: str
    index1: int
    index2: int
    similarity: float
    method: str
    metadata: Dict = None


@dataclass
class AlignmentResult:
    """Complete alignment result between two documents"""
    doc1_id: str
    doc2_id: str
    pairs: List[Dict]
    statistics: Dict
    parameters: Dict


class TextAligner:
    """
    Main text alignment engine
    Implements multiple algorithms for finding similar text passages
    """
    
    def __init__(self, similarity_threshold: float = 0.7, min_length: int = 10):
        """
        Initialize aligner
        
        Args:
            similarity_threshold: Minimum similarity score (0-1)
            min_length: Minimum text length to consider
        """
        self.similarity_threshold = similarity_threshold
        self.min_length = min_length
        logger.info(f"TextAligner initialized: threshold={similarity_threshold}, min_length={min_length}")
    
    def align_documents(self, 
                       doc1_lines: List[str], 
                       doc2_lines: List[str],
                       method: str = 'auto') -> List[AlignmentPair]:
        """
        Align two documents line-by-line
        
        Args:
            doc1_lines: List of lines from document 1
            doc2_lines: List of lines from document 2
            method: Alignment method ('auto', 'sequence', 'levenshtein', 'jaccard')
        
        Returns:
            List of AlignmentPair objects
        """
        logger.info(f"Aligning documents: {len(doc1_lines)} lines vs {len(doc2_lines)} lines")
        
        pairs = []
        
        for i, line1 in enumerate(doc1_lines):
            # Skip short lines
            if len(line1.strip()) < self.min_length:
                continue
            
            best_match = None
            best_score = 0.0
            
            for j, line2 in enumerate(doc2_lines):
                if len(line2.strip()) < self.min_length:
                    continue
                
                # Calculate similarity
                if method == 'auto' or method == 'sequence':
                    score = self._sequence_similarity(line1, line2)
                elif method == 'levenshtein':
                    score = self._levenshtein_similarity(line1, line2)
                elif method == 'jaccard':
                    score = self._jaccard_similarity(line1, line2)
                else:
                    score = self._sequence_similarity(line1, line2)
                
                if score > best_score and score >= self.similarity_threshold:
                    best_score = score
                    best_match = j
            
            if best_match is not None:
                pair = AlignmentPair(
                    text1=line1.strip(),
                    text2=doc2_lines[best_match].strip(),
                    index1=i,
                    index2=best_match,
                    similarity=best_score,
                    method=method,
                    metadata={}
                )
                pairs.append(pair)
                logger.debug(f"Aligned: line {i} <-> line {best_match} (score={best_score:.2f})")
        
        logger.info(f"Alignment complete: {len(pairs)} pairs found")
        return pairs
    
    def _sequence_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using SequenceMatcher"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _levenshtein_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using Levenshtein distance"""
        if LEVENSHTEIN_AVAILABLE:
            max_len = max(len(text1), len(text2))
            if max_len == 0:
                return 1.0
            distance = Levenshtein.distance(text1, text2)
            return 1.0 - (distance / max_len)
        else:
            # Fallback to sequence matcher
            return self._sequence_similarity(text1, text2)
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity (token overlap)"""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        
        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0


# Initialize global aligner
aligner = TextAligner()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'text-alignment',
        'version': '1.0.0',
        'levenshtein_available': LEVENSHTEIN_AVAILABLE
    })


@app.route('/align', methods=['POST'])
def align():
    """
    Align two documents
    
    POST /align
    {
        "doc1_id": "document_1",
        "doc2_id": "document_2",
        "doc1_lines": ["line 1", "line 2", ...],
        "doc2_lines": ["line a", "line b", ...],
        "method": "auto",  // optional
        "similarity_threshold": 0.7,  // optional
        "min_length": 10  // optional
    }
    """
    try:
        data = request.get_json()
        
        # Extract parameters
        doc1_id = data.get('doc1_id', 'doc1')
        doc2_id = data.get('doc2_id', 'doc2')
        doc1_lines = data.get('doc1_lines', [])
        doc2_lines = data.get('doc2_lines', [])
        method = data.get('method', 'auto')
        threshold = data.get('similarity_threshold', 0.7)
        min_len = data.get('min_length', 10)
        
        # Validate input
        if not doc1_lines or not doc2_lines:
            return jsonify({'error': 'Missing document lines'}), 400
        
        # Create aligner with custom parameters
        custom_aligner = TextAligner(similarity_threshold=threshold, min_length=min_len)
        
        # Perform alignment
        pairs = custom_aligner.align_documents(doc1_lines, doc2_lines, method=method)
        
        # Calculate statistics
        stats = {
            'total_lines_doc1': len(doc1_lines),
            'total_lines_doc2': len(doc2_lines),
            'aligned_pairs': len(pairs),
            'average_similarity': sum(p.similarity for p in pairs) / len(pairs) if pairs else 0.0,
            'alignment_rate': len(pairs) / max(len(doc1_lines), len(doc2_lines))
        }
        
        # Create result
        result = AlignmentResult(
            doc1_id=doc1_id,
            doc2_id=doc2_id,
            pairs=[asdict(p) for p in pairs],
            statistics=stats,
            parameters={
                'method': method,
                'similarity_threshold': threshold,
                'min_length': min_len
            }
        )
        
        return jsonify(asdict(result))
    
    except Exception as e:
        logger.error(f"Alignment error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/compare', methods=['POST'])
def compare():
    """
    Compare two text segments and return similarity score
    
    POST /compare
    {
        "text1": "first text",
        "text2": "second text",
        "method": "auto"  // optional
    }
    """
    try:
        data = request.get_json()
        text1 = data.get('text1', '')
        text2 = data.get('text2', '')
        method = data.get('method', 'auto')
        
        if not text1 or not text2:
            return jsonify({'error': 'Missing text'}), 400
        
        # Calculate similarity
        if method == 'sequence' or method == 'auto':
            score = aligner._sequence_similarity(text1, text2)
        elif method == 'levenshtein':
            score = aligner._levenshtein_similarity(text1, text2)
        elif method == 'jaccard':
            score = aligner._jaccard_similarity(text1, text2)
        else:
            score = aligner._sequence_similarity(text1, text2)
        
        return jsonify({
            'text1': text1[:100] + '...' if len(text1) > 100 else text1,
            'text2': text2[:100] + '...' if len(text2) > 100 else text2,
            'similarity': score,
            'method': method
        })
    
    except Exception as e:
        logger.error(f"Comparison error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Security: Bind to localhost only for development
    # For production, use proper WSGI server (gunicorn/waitress) instead
    app.run(host='127.0.0.1', port=9090, debug=False)  # localhost only
