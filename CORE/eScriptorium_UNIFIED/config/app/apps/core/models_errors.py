# Error Detection Models - BiblIA Enhancement
# Created: 2025-10-20
# Purpose: Automatic OCR error detection with focus on Hebrew text

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class DetectedError(models.Model):
    """
    שגיאה שזוהתה אוטומטית במערכת
    Automatically detected error in transcription
    """
    ERROR_TYPES = [
        ('spelling', 'שגיאת איות / Spelling error'),
        ('pattern', 'תבנית שגיאה / Error pattern'),
        ('confidence', 'ביטחון נמוך / Low confidence'),
        ('manual', 'סומן ידנית / Manually marked'),
    ]
    
    SEVERITY_LEVELS = [
        ('critical', 'קריטי / Critical'),
        ('high', 'גבוה / High'),
        ('medium', 'בינוני / Medium'),
        ('low', 'נמוך / Low'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'ממתין / Pending'),
        ('corrected', 'תוקן / Corrected'),
        ('ignored', 'התעלם / Ignored'),
        ('false_positive', 'לא שגיאה / False positive'),
    ]
    
    # Foreign key to LineTranscription
    line_transcription = models.ForeignKey(
        'core.LineTranscription',
        on_delete=models.CASCADE,
        related_name='detected_errors',
        verbose_name='תמלול שורה'
    )
    
    # Error classification
    error_type = models.CharField(
        max_length=20,
        choices=ERROR_TYPES,
        verbose_name='סוג שגיאה'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        verbose_name='חומרה'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='סטטוס'
    )
    
    # Error location
    word = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='מילה שגויה'
    )
    position = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='מיקום התחלה'
    )
    end_position = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='מיקום סיום'
    )
    
    # Correction suggestions
    suggestions = models.JSONField(
        default=list,
        verbose_name='הצעות תיקון',
        help_text='List of suggested corrections'
    )
    
    # Metadata
    description = models.TextField(
        blank=True,
        verbose_name='תיאור'
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name='ציון ביטחון',
        help_text='OCR confidence score (0.0-1.0)'
    )
    
    # Timestamps
    detected_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='זוהה ב'
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='טופל ב'
    )
    
    # User who resolved the error
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_errors',
        verbose_name='טופל על ידי'
    )
    
    class Meta:
        app_label = 'core'
        ordering = ['-severity', '-detected_at']
        verbose_name = 'שגיאה מזוהה'
        verbose_name_plural = 'שגיאות מזוהות'
        indexes = [
            models.Index(fields=['line_transcription', 'status']),
            models.Index(fields=['error_type', 'severity']),
            models.Index(fields=['status', 'detected_at']),
        ]
    
    def __str__(self):
        return f"{self.get_error_type_display()} - {self.word or 'N/A'}"
    
    def mark_corrected(self, user):
        """Mark error as corrected"""
        self.status = 'corrected'
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()
    
    def mark_false_positive(self, user):
        """Mark error as not actually an error"""
        self.status = 'false_positive'
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()


class ErrorCorrection(models.Model):
    """
    תיקון שבוצע על ידי משתמש
    User-performed correction for learning purposes
    """
    detected_error = models.ForeignKey(
        DetectedError,
        on_delete=models.CASCADE,
        related_name='corrections',
        verbose_name='שגיאה'
    )
    
    # The correction
    original_text = models.CharField(
        max_length=500,
        verbose_name='טקסט מקורי'
    )
    corrected_text = models.CharField(
        max_length=500,
        verbose_name='טקסט מתוקן'
    )
    
    # Learning metadata
    was_from_suggestion = models.BooleanField(
        default=False,
        verbose_name='מהצעה?',
        help_text='Was this correction from a suggested option?'
    )
    suggestion_rank = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='דירוג הצעה',
        help_text='Which suggestion was chosen (1-5)'
    )
    
    # User and timestamp
    corrected_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='תוקן על ידי'
    )
    corrected_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='תוקן ב'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='הערות'
    )
    
    class Meta:
        app_label = 'core'
        ordering = ['-corrected_at']
        verbose_name = 'תיקון'
        verbose_name_plural = 'תיקונים'
    
    def __str__(self):
        return f"{self.original_text} → {self.corrected_text}"
    
    def save(self, *args, **kwargs):
        """After saving, trigger learning update"""
        super().save(*args, **kwargs)
        # Update machine learning from this correction
        from core.tasks import update_error_learning
        update_error_learning.delay(self.id)


class CustomDictionaryWord(models.Model):
    """
    מילון מותאם אישית - מילים שהמשתמש אישר שהן נכונות
    Custom dictionary for user-approved words (names, terminology, etc.)
    """
    word = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='מילה'
    )
    language = models.CharField(
        max_length=10,
        default='he',
        verbose_name='שפה',
        help_text='Language code (he, ar, en)'
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='קטגוריה',
        help_text='e.g., "שמות", "מקומות", "מונחים"'
    )
    
    # Metadata
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='נוסף על ידי'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='נוסף ב'
    )
    usage_count = models.IntegerField(
        default=0,
        verbose_name='ספירת שימוש'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='הערות'
    )
    
    class Meta:
        app_label = 'core'
        ordering = ['-usage_count', 'word']
        verbose_name = 'מילה במילון מותאם'
        verbose_name_plural = 'מילון מותאם אישית'
    
    def __str__(self):
        return f"{self.word} ({self.language})"
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class ErrorPattern(models.Model):
    """
    תבניות שגיאה שנלמדו מתיקונים קודמים
    Learned error patterns from previous corrections
    
    Example: "ו" → "ד" (common OCR confusion in Hebrew)
    """
    # The pattern
    pattern_from = models.CharField(
        max_length=200,
        verbose_name='תבנית שגויה'
    )
    pattern_to = models.CharField(
        max_length=200,
        verbose_name='תבנית מתוקנת'
    )
    language = models.CharField(
        max_length=10,
        verbose_name='שפה'
    )
    
    # Pattern type
    pattern_type = models.CharField(
        max_length=50,
        default='character',
        choices=[
            ('character', 'תו בודד / Single character'),
            ('sequence', 'רצף תווים / Character sequence'),
            ('word', 'מילה / Word'),
            ('regex', 'ביטוי רגולרי / Regex pattern'),
        ],
        verbose_name='סוג תבנית'
    )
    
    # Learning stats
    frequency = models.IntegerField(
        default=1,
        verbose_name='תדירות',
        help_text='How many times this pattern was observed'
    )
    confidence = models.FloatField(
        default=0.5,
        verbose_name='ביטחון',
        help_text='Confidence score (0.0-1.0)'
    )
    success_rate = models.FloatField(
        default=0.0,
        verbose_name='אחוז הצלחה',
        help_text='Success rate when suggested (0.0-1.0)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='נוצר ב'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='עודכן ב'
    )
    
    # Context
    context = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='הקשר',
        help_text='Additional context (e.g., common surrounding characters)'
    )
    
    class Meta:
        app_label = 'core'
        unique_together = ['pattern_from', 'pattern_to', 'language']
        ordering = ['-frequency', '-confidence']
        verbose_name = 'תבנית שגיאה'
        verbose_name_plural = 'תבניות שגיאה'
    
    def __str__(self):
        return f"{self.pattern_from} → {self.pattern_to} (×{self.frequency})"
    
    def increment_frequency(self):
        """Increment pattern frequency"""
        self.frequency += 1
        self.save(update_fields=['frequency', 'updated_at'])
    
    def update_success_rate(self, was_successful):
        """Update success rate based on user feedback"""
        # Simple moving average
        total_attempts = self.frequency
        current_successes = self.success_rate * (total_attempts - 1)
        if was_successful:
            current_successes += 1
        self.success_rate = current_successes / total_attempts
        self.save(update_fields=['success_rate', 'updated_at'])
