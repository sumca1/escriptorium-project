"""
CERberus Integration Models
"""

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _


class CERAnalysis(models.Model):
    """
    Store CER analysis results for transcription comparisons.
    """
    
    # Relations (using string reference to avoid circular import)
    ground_truth_transcription = models.ForeignKey(
        'core.Transcription',
        on_delete=models.CASCADE,
        related_name='cer_analyses_as_ground_truth',
        help_text='Ground truth transcription'
    )
    hypothesis_transcription = models.ForeignKey(
        'core.Transcription',
        on_delete=models.CASCADE,
        related_name='cer_analyses_as_hypothesis',
        help_text='Hypothesis (OCR output) transcription'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Analysis parameters
    ignore_punctuation = models.BooleanField(default=False)
    ignore_case = models.BooleanField(default=False)
    ignore_whitespace = models.BooleanField(default=False)
    ignore_numbers = models.BooleanField(default=False)
    ignore_newlines = models.BooleanField(default=False)
    ignore_chars = models.CharField(max_length=255, blank=True, null=True)
    
    # Core CER metrics
    cer_value = models.FloatField(
        help_text='Character Error Rate percentage'
    )
    num_correct = models.IntegerField(
        help_text='Number of correctly recognized characters'
    )
    num_substitutions = models.IntegerField(
        help_text='Number of substituted characters'
    )
    num_insertions = models.IntegerField(
        help_text='Number of inserted characters'
    )
    num_deletions = models.IntegerField(
        help_text='Number of deleted characters'
    )
    total_characters = models.IntegerField(
        help_text='Total number of characters in ground truth'
    )
    
    # Line statistics
    original_lines_count = models.IntegerField(default=0)
    discarded_lines_count = models.IntegerField(default=0)
    processed_lines_count = models.IntegerField(default=0)
    
    # Detailed statistics (stored as JSON)
    character_statistics = models.JSONField(
        default=list,
        blank=True,
        help_text='Per-character accuracy statistics'
    )
    block_statistics = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text='Unicode block statistics'
    )
    confusion_statistics = models.JSONField(
        default=list,
        blank=True,
        help_text='Character confusion matrix'
    )
    
    class Meta:
        verbose_name = _('CER Analysis')
        verbose_name_plural = _('CER Analyses')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ground_truth_transcription', 'hypothesis_transcription']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"CER Analysis: {self.cer_value}% (GT: {self.ground_truth_transcription.id}, Hyp: {self.hypothesis_transcription.id})"
    
    @property
    def accuracy(self):
        """Calculate accuracy percentage"""
        if self.total_characters == 0:
            return 0.0
        return round((self.num_correct / self.total_characters) * 100, 2)
    
    @property
    def error_breakdown(self):
        """Get error breakdown as percentages"""
        if self.total_characters == 0:
            return {
                'substitutions': 0.0,
                'insertions': 0.0,
                'deletions': 0.0,
            }
        
        return {
            'substitutions': round((self.num_substitutions / self.total_characters) * 100, 2),
            'insertions': round((self.num_insertions / self.total_characters) * 100, 2),
            'deletions': round((self.num_deletions / self.total_characters) * 100, 2),
        }
    
    def get_top_confusions(self, limit=10):
        """Get top N most common character confusions"""
        if not self.confusion_statistics:
            return []
        
        return sorted(
            self.confusion_statistics,
            key=lambda x: x['count'],
            reverse=True
        )[:limit]
    
    def get_problematic_characters(self, threshold=0.5):
        """
        Get characters with accuracy below threshold.
        
        Args:
            threshold: Minimum correct_ratio (0.0 to 1.0)
        
        Returns:
            List of characters with low accuracy
        """
        if not self.character_statistics:
            return []
        
        return [
            char_stat for char_stat in self.character_statistics
            if char_stat.get('correct_ratio', 1.0) < threshold
        ]
