"""
Django Admin for TABA Pipeline
"""
from django.contrib import admin
from .models import GroundTruthCorpus, GroundTruthText, AlignmentJob, AlignmentResult


@admin.register(GroundTruthCorpus)
class GroundTruthCorpusAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'total_texts', 'total_characters', 'owner', 'created_at']
    list_filter = ['source_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'total_texts', 'total_characters']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'owner')
        }),
        ('Source', {
            'fields': ('source_type', 'source_path')
        }),
        ('Statistics', {
            'fields': ('total_texts', 'total_characters'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GroundTruthText)
class GroundTruthTextAdmin(admin.ModelAdmin):
    list_display = ['title', 'corpus', 'character_count', 'word_count', 'language', 'created_at']
    list_filter = ['corpus', 'language', 'created_at']
    search_fields = ['title', 'filename', 'content']
    readonly_fields = ['character_count', 'word_count', 'created_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('corpus', 'title', 'filename')
        }),
        ('Content', {
            'fields': ('content', 'language')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('character_count', 'word_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AlignmentJob)
class AlignmentJobAdmin(admin.ModelAdmin):
    list_display = ['name', 'document', 'status', 'progress', 'total_aligned_lines', 'owner', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'document__name']
    readonly_fields = ['created_at', 'started_at', 'completed_at', 'total_aligned_lines', 'duration']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('name', 'owner', 'status', 'progress')
        }),
        ('Source', {
            'fields': ('document', 'ocr_transcription', 'gt_corpus')
        }),
        ('Passim Parameters', {
            'fields': ('passim_n', 'passim_cores', 'passim_memory', 'passim_driver_memory'),
            'classes': ('collapse',)
        }),
        ('Filtering', {
            'fields': ('levenshtein_threshold',)
        }),
        ('Results', {
            'fields': ('total_aligned_lines', 'aligned_gt_texts', 'results_path', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at', 'duration'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AlignmentResult)
class AlignmentResultAdmin(admin.ModelAdmin):
    list_display = ['part_title', 'job', 'gt_text', 'total_aligned_lines', 'max_cluster_size', 'average_levenshtein_ratio']
    list_filter = ['job', 'created_at']
    search_fields = ['part_title', 'gt_text__title']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Page Information', {
            'fields': ('job', 'part_pk', 'part_title')
        }),
        ('Ground Truth', {
            'fields': ('gt_text',)
        }),
        ('Alignment Statistics', {
            'fields': ('total_aligned_lines', 'aligned_clusters', 'max_cluster_size', 'average_levenshtein_ratio')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
