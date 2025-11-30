# -*- coding: utf-8 -*-
"""
Text Alignment Models - BiblIA Enhancement
Created: 20 October 2025

Models for storing text alignment results between documents.
Supports Passim-style text reuse detection and passage alignment.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import json

User = get_user_model()


class TextAlignment(models.Model):
    """
    יישור טקסט בין שני מסמכים
    Stores alignment relationship between two documents
    """
    
    # Documents being aligned
    document1 = models.ForeignKey(
        'core.Document',
        on_delete=models.CASCADE,
        related_name='alignments_as_doc1',
        verbose_name=_('Document 1'),
        help_text=_('First document in alignment')
    )
    
    document2 = models.ForeignKey(
        'core.Document',
        on_delete=models.CASCADE,
        related_name='alignments_as_doc2',
        verbose_name=_('Document 2'),
        help_text=_('Second document in alignment')
    )
    
    # Alignment metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_alignments',
        verbose_name=_('Created By')
    )
    
    # Alignment parameters
    method = models.CharField(
        max_length=50,
        default='auto',
        choices=[
            ('auto', 'Auto'),
            ('sequence', 'Sequence Matching'),
            ('levenshtein', 'Levenshtein Distance'),
            ('jaccard', 'Jaccard Similarity'),
        ],
        verbose_name=_('Alignment Method')
    )
    
    similarity_threshold = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name=_('Similarity Threshold'),
        help_text=_('Minimum similarity score (0-1) to consider a match')
    )
    
    min_length = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        verbose_name=_('Minimum Text Length'),
        help_text=_('Minimum characters to consider for alignment')
    )
    
    # Statistics
    total_pairs = models.IntegerField(
        default=0,
        verbose_name=_('Total Pairs'),
        help_text=_('Number of aligned line pairs found')
    )
    
    average_similarity = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name=_('Average Similarity'),
        help_text=_('Average similarity score across all pairs')
    )
    
    alignment_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name=_('Alignment Rate'),
        help_text=_('Percentage of lines successfully aligned')
    )
    
    # Processing status
    status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        verbose_name=_('Status')
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Error Message')
    )
    
    class Meta:
        app_label = 'core'
        verbose_name = _('Text Alignment')
        verbose_name_plural = _('Text Alignments')
        unique_together = ['document1', 'document2']
        indexes = [
            models.Index(fields=['document1', 'document2']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Alignment: {self.document1.name} ↔ {self.document2.name}"
    
    def update_statistics(self):
        """Calculate and update alignment statistics"""
        pairs = self.pairs.all()
        if pairs.exists():
            self.total_pairs = pairs.count()
            self.average_similarity = pairs.aggregate(
                models.Avg('similarity')
            )['similarity__avg'] or 0.0
            
            # Calculate alignment rate
            doc1_lines = self.document1.transcription_set.first().lines.count() if self.document1.transcription_set.exists() else 0
            doc2_lines = self.document2.transcription_set.first().lines.count() if self.document2.transcription_set.exists() else 0
            max_lines = max(doc1_lines, doc2_lines)
            self.alignment_rate = self.total_pairs / max_lines if max_lines > 0 else 0.0
            
            self.save()


class AlignmentPair(models.Model):
    """
    זוג שורות מיושרות
    A pair of aligned lines between two documents
    """
    
    alignment = models.ForeignKey(
        TextAlignment,
        on_delete=models.CASCADE,
        related_name='pairs',
        verbose_name=_('Alignment')
    )
    
    # Line references
    line1 = models.ForeignKey(
        'core.LineTranscription',
        on_delete=models.CASCADE,
        related_name='alignment_pairs_as_line1',
        verbose_name=_('Line 1')
    )
    
    line2 = models.ForeignKey(
        'core.LineTranscription',
        on_delete=models.CASCADE,
        related_name='alignment_pairs_as_line2',
        verbose_name=_('Line 2')
    )
    
    # Similarity metrics
    similarity = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name=_('Similarity Score'),
        help_text=_('How similar the two lines are (0-1)')
    )
    
    method_used = models.CharField(
        max_length=50,
        verbose_name=_('Method Used'),
        help_text=_('Algorithm used to calculate similarity')
    )
    
    # Additional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Metadata'),
        help_text=_('Additional alignment metadata (JSON)')
    )
    
    # User feedback
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verified'),
        help_text=_('User has verified this alignment is correct')
    )
    
    is_rejected = models.BooleanField(
        default=False,
        verbose_name=_('Rejected'),
        help_text=_('User has rejected this alignment as incorrect')
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_alignments',
        verbose_name=_('Verified By')
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Verified At')
    )
    
    class Meta:
        app_label = 'core'
        verbose_name = _('Alignment Pair')
        verbose_name_plural = _('Alignment Pairs')
        unique_together = ['alignment', 'line1', 'line2']
        indexes = [
            models.Index(fields=['alignment', 'similarity']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.line1.content[:30]}... ↔ {self.line2.content[:30]}... ({self.similarity:.2f})"


class AlignmentJob(models.Model):
    """
    משימת יישור טקסט
    Background job for processing text alignments
    """
    
    alignment = models.OneToOneField(
        TextAlignment,
        on_delete=models.CASCADE,
        related_name='job',
        verbose_name=_('Alignment')
    )
    
    # Job metadata
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Started At')
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )
    
    # Progress tracking
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Progress'),
        help_text=_('Job completion percentage (0-100)')
    )
    
    current_step = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Current Step'),
        help_text=_('Description of current processing step')
    )
    
    # Celery task ID
    task_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('Celery Task ID')
    )
    
    # Results
    result_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Result Data'),
        help_text=_('Detailed alignment results (JSON)')
    )
    
    class Meta:
        app_label = 'core'
        verbose_name = _('Alignment Job')
        verbose_name_plural = _('Alignment Jobs')
        indexes = [
            models.Index(fields=['task_id']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"Job for {self.alignment} ({self.progress}%)"
    
    def is_running(self):
        """Check if job is currently running"""
        return self.alignment.status == 'processing'
    
    def is_complete(self):
        """Check if job has completed"""
        return self.alignment.status in ['completed', 'failed']
