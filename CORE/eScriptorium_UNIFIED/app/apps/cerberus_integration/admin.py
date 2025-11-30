"""
CERberus Integration Admin
===========================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import CERAnalysis


@admin.register(CERAnalysis)
class CERAnalysisAdmin(admin.ModelAdmin):
    """
    Admin interface for CER Analysis results.
    """
    
    list_display = [
        'id',
        'cer_display',
        'accuracy_display',
        'ground_truth_transcription',
        'hypothesis_transcription',
        'total_characters',
        'created_at',
    ]
    
    list_filter = [
        'created_at',
        'ignore_case',
        'ignore_punctuation',
        'ignore_whitespace',
        'ignore_numbers',
    ]
    
    search_fields = [
        'ground_truth_transcription__id',
        'hypothesis_transcription__id',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'cer_value',
        'accuracy',
        'num_correct',
        'num_substitutions',
        'num_insertions',
        'num_deletions',
        'total_characters',
        'original_lines_count',
        'discarded_lines_count',
        'processed_lines_count',
        'character_statistics',
        'block_statistics',
        'confusion_statistics',
        'error_breakdown_display',
        'top_confusions_display',
    ]
    
    fieldsets = (
        ('Transcriptions', {
            'fields': (
                'ground_truth_transcription',
                'hypothesis_transcription',
            )
        }),
        ('Analysis Options', {
            'fields': (
                'ignore_punctuation',
                'ignore_case',
                'ignore_whitespace',
                'ignore_numbers',
                'ignore_newlines',
                'ignore_chars',
            )
        }),
        ('Core Metrics', {
            'fields': (
                'cer_value',
                'accuracy',
                'total_characters',
                'error_breakdown_display',
            )
        }),
        ('Detailed Statistics', {
            'fields': (
                'num_correct',
                'num_substitutions',
                'num_insertions',
                'num_deletions',
            )
        }),
        ('Line Statistics', {
            'fields': (
                'original_lines_count',
                'discarded_lines_count',
                'processed_lines_count',
            )
        }),
        ('Advanced Statistics', {
            'fields': (
                'character_statistics',
                'block_statistics',
                'top_confusions_display',
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )
    
    def cer_display(self, obj):
        """Display CER with color coding"""
        if obj.cer_value < 5:
            color = 'green'
        elif obj.cer_value < 15:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color,
            obj.cer_value
        )
    cer_display.short_description = 'CER'
    cer_display.admin_order_field = 'cer_value'
    
    def accuracy_display(self, obj):
        """Display accuracy with color coding"""
        acc = obj.accuracy
        if acc > 95:
            color = 'green'
        elif acc > 85:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.2f}%</span>',
            color,
            acc
        )
    accuracy_display.short_description = 'Accuracy'
    
    def error_breakdown_display(self, obj):
        """Display error breakdown as HTML"""
        breakdown = obj.error_breakdown
        return format_html(
            '<ul style="margin: 0; padding-left: 20px;">'
            '<li>Substitutions: <strong>{:.2f}%</strong></li>'
            '<li>Insertions: <strong>{:.2f}%</strong></li>'
            '<li>Deletions: <strong>{:.2f}%</strong></li>'
            '</ul>',
            breakdown['substitutions'],
            breakdown['insertions'],
            breakdown['deletions']
        )
    error_breakdown_display.short_description = 'Error Breakdown'
    
    def top_confusions_display(self, obj):
        """Display top 10 confusions"""
        confusions = obj.get_top_confusions(limit=10)
        if not confusions:
            return format_html('<em>No confusions</em>')
        
        html = '<table style="border-collapse: collapse; width: 100%;">'
        html += '<tr style="background: #f5f5f5;"><th>Correct</th><th>Generated</th><th>Count</th></tr>'
        
        for conf in confusions:
            html += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                conf['correct_character'],
                conf['generated_character'],
                conf['count']
            )
        
        html += '</table>'
        return format_html(html)
    top_confusions_display.short_description = 'Top 10 Confusions'
    
    def has_add_permission(self, request):
        """Disable manual creation - use API"""
        return False
