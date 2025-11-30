"""
CERberus Batch Analysis Manager
================================

Manages batch processing of multiple CER analyses.
Supports both sequential and parallel processing modes.
"""

import threading
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from django.core.cache import cache
from django.utils import timezone
from django.db import transaction

from core.models import Transcription
from .models import CERAnalysis
from .analyzer import CERAnalyzer


class BatchAnalysisManager:
    """
    Manages batch analysis of multiple transcription pairs.
    
    Features:
    - Sequential or parallel processing
    - Progress tracking via Django cache
    - Error handling per transcription
    - Result aggregation and export
    
    Usage:
        manager = BatchAnalysisManager(
            batch_id="uuid",
            transcription_pairs=[
                {"ground_truth_id": 1, "hypothesis_id": 2, "name": "Test 1"},
                ...
            ],
            mode="sequential",
            user=request.user
        )
        manager.start()
        
        # Later, check progress:
        progress = manager.get_progress()
    """
    
    # Cache TTL: 24 hours
    CACHE_TTL = 86400
    
    def __init__(
        self,
        batch_id: str,
        transcription_pairs: List[Dict[str, Any]],
        mode: str = 'sequential',
        user=None
    ):
        """
        Initialize batch analysis manager.
        
        Args:
            batch_id: Unique identifier for this batch
            transcription_pairs: List of dicts with ground_truth_id, hypothesis_id, name
            mode: 'sequential' or 'parallel'
            user: Django user object (for permissions)
        """
        self.batch_id = batch_id
        self.transcription_pairs = transcription_pairs
        self.mode = mode
        self.user = user
        
        # Initialize cache data
        self._init_cache()
    
    def _init_cache(self):
        """Initialize batch data in cache."""
        cache_key = f'cerberus_batch_{self.batch_id}'
        
        cache.set(cache_key, {
            'batch_id': self.batch_id,
            'status': 'pending',
            'mode': self.mode,
            'total': len(self.transcription_pairs),
            'completed': 0,
            'pending': len(self.transcription_pairs),
            'failed': 0,
            'started_at': timezone.now().isoformat(),
            'completed_at': None,
            'results': []
        }, self.CACHE_TTL)
    
    def start(self):
        """
        Start batch processing.
        
        If mode is 'parallel', spawns a background thread.
        If mode is 'sequential', processes immediately.
        """
        if self.mode == 'parallel':
            # Spawn background thread
            thread = threading.Thread(target=self._process_batch)
            thread.daemon = True
            thread.start()
        else:
            # Process synchronously
            self._process_batch()
    
    def _process_batch(self):
        """
        Process all transcription pairs.
        
        Updates cache with progress after each transcription.
        """
        cache_key = f'cerberus_batch_{self.batch_id}'
        
        # Update status to running
        batch_data = cache.get(cache_key)
        batch_data['status'] = 'running'
        cache.set(cache_key, batch_data, self.CACHE_TTL)
        
        results = []
        completed = 0
        failed = 0
        
        for pair in self.transcription_pairs:
            try:
                result = self._analyze_pair(pair)
                result['status'] = 'completed'
                completed += 1
            except Exception as e:
                result = {
                    'name': pair.get('name', f"Pair {completed + failed + 1}"),
                    'ground_truth_id': pair.get('ground_truth_id'),
                    'hypothesis_id': pair.get('hypothesis_id'),
                    'status': 'failed',
                    'error': str(e),
                    'cer': None,
                    'accuracy': None
                }
                failed += 1
            
            results.append(result)
            
            # Update cache with progress
            batch_data = cache.get(cache_key)
            batch_data['completed'] = completed
            batch_data['failed'] = failed
            batch_data['pending'] = len(self.transcription_pairs) - completed - failed
            batch_data['results'] = results
            cache.set(cache_key, batch_data, self.CACHE_TTL)
        
        # Mark as completed
        batch_data = cache.get(cache_key)
        batch_data['status'] = 'completed'
        batch_data['completed_at'] = timezone.now().isoformat()
        cache.set(cache_key, batch_data, self.CACHE_TTL)
    
    def _analyze_pair(self, pair: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single transcription pair.
        
        Args:
            pair: Dict with ground_truth_id, hypothesis_id, name
            
        Returns:
            Dict with analysis results
        """
        ground_truth_id = pair['ground_truth_id']
        hypothesis_id = pair['hypothesis_id']
        name = pair.get('name', f'Analysis {ground_truth_id} vs {hypothesis_id}')
        
        # Get transcriptions
        ground_truth = Transcription.objects.get(pk=ground_truth_id)
        hypothesis = Transcription.objects.get(pk=hypothesis_id)
        
        # Extract text
        gt_text = self._get_transcription_text(ground_truth)
        hyp_text = self._get_transcription_text(hypothesis)
        
        # Create CER analysis
        with transaction.atomic():
            analysis = CERAnalysis.objects.create(
                ground_truth_transcription=ground_truth,
                hypothesis_transcription=hypothesis,
                created_by=self.user
            )
            
            # Run analysis
            analyzer = CERAnalyzer()
            result = analyzer.analyze(gt_text, hyp_text)
            
            # Update analysis with results
            analysis.total_characters = result['total_characters']
            analysis.total_errors = result['total_errors']
            analysis.substitutions = result['substitutions']
            analysis.insertions = result['insertions']
            analysis.deletions = result['deletions']
            analysis.cer = result['cer']
            analysis.wer = result.get('wer', 0)
            analysis.accuracy = result['accuracy']
            
            if result.get('confusion_matrix'):
                analysis.confusion_matrix = result['confusion_matrix']
            
            analysis.save()
        
        # Return summary
        return {
            'name': name,
            'ground_truth_id': ground_truth_id,
            'hypothesis_id': hypothesis_id,
            'analysis_id': analysis.id,
            'cer': float(analysis.cer),
            'accuracy': float(analysis.accuracy),
            'total_characters': analysis.total_characters,
            'errors': analysis.total_errors,
            'substitutions': analysis.substitutions,
            'insertions': analysis.insertions,
            'deletions': analysis.deletions,
            'created_at': analysis.created_at.isoformat()
        }
    
    def _get_transcription_text(self, transcription: Transcription) -> str:
        """
        Extract text from a Transcription object.
        
        Concatenates all line transcriptions.
        """
        from core.models import LineTranscription
        
        line_transcriptions = LineTranscription.objects.filter(
            transcription=transcription
        ).order_by('line__order')
        
        text_lines = []
        for lt in line_transcriptions:
            if lt.content:
                text_lines.append(lt.content)
        
        return '\n'.join(text_lines)
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get current progress of batch analysis.
        
        Returns:
            Dict with status, progress, and results
        """
        cache_key = f'cerberus_batch_{self.batch_id}'
        batch_data = cache.get(cache_key)
        
        if not batch_data:
            return {
                'error': 'Batch not found',
                'batch_id': self.batch_id
            }
        
        # Calculate percentage
        total = batch_data['total']
        completed = batch_data['completed']
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        return {
            'batch_id': self.batch_id,
            'status': batch_data['status'],
            'progress': {
                'total': total,
                'completed': completed,
                'pending': batch_data['pending'],
                'failed': batch_data['failed'],
                'percentage': percentage
            },
            'results': batch_data['results'],
            'started_at': batch_data['started_at'],
            'completed_at': batch_data.get('completed_at')
        }
    
    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get all results from batch analysis.
        
        Returns:
            List of result dicts
        """
        cache_key = f'cerberus_batch_{self.batch_id}'
        batch_data = cache.get(cache_key)
        
        if not batch_data:
            return []
        
        return batch_data.get('results', [])
    
    @classmethod
    def get_batch(cls, batch_id: str) -> Optional['BatchAnalysisManager']:
        """
        Retrieve an existing batch by ID.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            BatchAnalysisManager instance or None if not found
        """
        cache_key = f'cerberus_batch_{batch_id}'
        batch_data = cache.get(cache_key)
        
        if not batch_data:
            return None
        
        # Create manager instance (without re-initializing)
        manager = cls.__new__(cls)
        manager.batch_id = batch_id
        manager.transcription_pairs = []  # Not needed for retrieval
        manager.mode = batch_data.get('mode', 'sequential')
        manager.user = None
        
        return manager
