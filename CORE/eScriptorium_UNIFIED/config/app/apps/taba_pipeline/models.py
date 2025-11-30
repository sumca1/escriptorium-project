"""
TABA Pipeline Models
Store Ground Truth corpus and alignment jobs
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from core.models import Document, Transcription

User = get_user_model()


class GroundTruthCorpus(models.Model):
    """
    Collection of known digital texts for alignment
    """
    name = models.CharField(
        max_length=255, 
        verbose_name=_("Corpus Name"),
        help_text=_("Name of the ground truth corpus (e.g., 'Sefaria Tanakh', 'Hebrew Literature Collection')")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Detailed description of this corpus and its sources")
    )
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='gt_corpora',
        verbose_name=_("Owner"),
        help_text=_("User who created this corpus")
    )
    
    # Source information
    source_type = models.CharField(
        max_length=50,
        choices=[
            ('sefaria', _('Sefaria API')),
            ('pdf', _('PDF Files')), 
            ('txt', _('Text Files')),
            ('manual', _('Manual Entry')),
            ('other', _('Other')),
        ],
        default='txt',
        verbose_name=_("Source Type"),
        help_text=_("Type of source for this corpus")
    )
    source_path = models.CharField(
        max_length=500, 
        blank=True,
        verbose_name=_("Source Path"),
        help_text=_("Path to source files or API endpoint")
    )
    language = models.CharField(
        max_length=10,
        default='heb',
        verbose_name=_("Language"),
        help_text=_("Primary language of this corpus (e.g., 'heb', 'ara', 'eng')")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )
    
    # Statistics
    total_texts = models.IntegerField(
        default=0,
        verbose_name=_("Total Texts"),
        help_text=_("Number of texts in this corpus")
    )
    total_characters = models.BigIntegerField(
        default=0,
        verbose_name=_("Total Characters"),
        help_text=_("Total character count in corpus")
    )
    
    class Meta:
        verbose_name = _("Ground Truth Corpus")
        verbose_name_plural = _("Ground Truth Corpora")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.total_texts} texts)"
    
    @property
    def text_count(self):
        """Alias for total_texts for compatibility"""
        return self.texts.count()


class GroundTruthText(models.Model):
    """
    Individual text in a Ground Truth corpus
    """
    corpus = models.ForeignKey(
        GroundTruthCorpus, 
        on_delete=models.CASCADE, 
        related_name='texts',
        verbose_name=_("Corpus"),
        help_text=_("The corpus this text belongs to")
    )
    
    # Text identification
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("Title or identifier for this text")
    )
    filename = models.CharField(
        max_length=255,
        verbose_name=_("Filename"),
        help_text=_("Original filename of the source document")
    )
    
    # Content
    content = models.TextField(
        verbose_name=_("Content"),
        help_text=_("Clean text content ready for alignment with OCR")
    )
    
    # Metadata
    language = models.CharField(
        max_length=10, 
        default='heb',
        verbose_name=_("Language"),
        help_text=_("Language code (e.g., 'heb' for Hebrew, 'ara' for Arabic)")
    )
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name=_("Metadata"),
        help_text=_("Additional metadata about this text (author, date, etc.)")
    )
    
    # Statistics
    character_count = models.IntegerField(
        default=0,
        verbose_name=_("Character Count"),
        help_text=_("Total number of characters in this text")
    )
    word_count = models.IntegerField(
        default=0,
        verbose_name=_("Word Count"),
        help_text=_("Total number of words in this text")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    
    class Meta:
        verbose_name = _("Ground Truth Text")
        verbose_name_plural = _("Ground Truth Texts")
        ordering = ['corpus', 'title']
        unique_together = [['corpus', 'filename']]
    
    def __str__(self):
        return f"{self.title} ({self.character_count} chars)"
    
    def save(self, *args, **kwargs):
        # Auto-calculate statistics
        if self.content:
            self.character_count = len(self.content)
            self.word_count = len(self.content.split())
        super().save(*args, **kwargs)


class AlignmentJob(models.Model):
    """
    TABA Pipeline alignment job
    """
    # Job identification
    name = models.CharField(
        max_length=255,
        verbose_name=_("Job Name"),
        help_text=_("Descriptive name for this alignment job")
    )
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='alignment_jobs',
        verbose_name=_("Owner"),
        help_text=_("User who created this job")
    )
    
    # Source document
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE, 
        related_name='alignment_jobs',
        verbose_name=_("Document"),
        help_text=_("Source document containing OCR to be aligned")
    )
    ocr_transcription = models.ForeignKey(
        Transcription, 
        on_delete=models.CASCADE,
        related_name='alignment_jobs_as_ocr',
        verbose_name=_("OCR Transcription"),
        help_text=_("OCR transcription to align with ground truth")
    )
    
    # Ground Truth corpus
    gt_corpus = models.ForeignKey(
        GroundTruthCorpus,
        on_delete=models.CASCADE,
        related_name='alignment_jobs',
        verbose_name=_("Ground Truth Corpus"),
        help_text=_("Corpus of clean texts to align against")
    )
    
    # Passim parameters
    passim_n = models.IntegerField(
        default=7,
        verbose_name=_("N-gram Order"),
        help_text=_("Character n-gram order for Passim alignment (default: 7)")
    )
    passim_cores = models.IntegerField(
        default=6,
        verbose_name=_("CPU Cores"),
        help_text=_("Number of CPU cores to use for alignment")
    )
    passim_memory = models.IntegerField(
        default=8,
        verbose_name=_("Memory (GB)"),
        help_text=_("Memory allocation in GB for alignment process")
    )
    passim_driver_memory = models.IntegerField(default=4, help_text="Driver memory in GB")
    
    # Filtering parameters
    levenshtein_threshold = models.FloatField(
        default=0.8,
        help_text="Minimum Levenshtein ratio (0.0-1.0)"
    )
    
    # Job status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing Data'),
        ('running_passim', 'Running Passim'),
        ('processing', 'Processing Results'),
        ('importing', 'Importing to eScriptorium'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0, help_text="Progress percentage (0-100)")
    
    # Results
    total_aligned_lines = models.IntegerField(default=0)
    aligned_gt_texts = models.JSONField(default=list, blank=True, help_text="List of GT texts found")
    results_path = models.CharField(max_length=500, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("Alignment Job")
        verbose_name_plural = _("Alignment Jobs")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    @property
    def duration(self):
        """Calculate job duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class AlignmentResult(models.Model):
    """
    Results of alignment for a specific page/part
    """
    job = models.ForeignKey(AlignmentJob, on_delete=models.CASCADE, related_name='results')
    
    # Page information
    part_pk = models.IntegerField(help_text="eScriptorium part (page) pk")
    part_title = models.CharField(max_length=255)
    
    # GT that was aligned
    gt_text = models.ForeignKey(
        GroundTruthText,
        on_delete=models.CASCADE,
        related_name='alignments'
    )
    
    # Alignment statistics
    total_aligned_lines = models.IntegerField(default=0)
    aligned_clusters = models.JSONField(
        default=list,
        help_text="Sizes of consecutive aligned line clusters"
    )
    max_cluster_size = models.IntegerField(default=0)
    
    # Quality metrics
    average_levenshtein_ratio = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Alignment Result")
        verbose_name_plural = _("Alignment Results")
        ordering = ['job', '-total_aligned_lines']
    
    def __str__(self):
        return f"{self.part_title}: {self.total_aligned_lines} lines aligned with {self.gt_text.title}"
