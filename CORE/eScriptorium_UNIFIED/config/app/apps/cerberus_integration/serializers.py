"""
CERberus Integration Serializers
=================================

DRF serializers for CER analysis API.
"""

from rest_framework import serializers
from .models import CERAnalysis


class CERAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for CERAnalysis model - full representation.
    """
    
    accuracy = serializers.FloatField(read_only=True)
    error_breakdown = serializers.DictField(read_only=True)
    
    class Meta:
        model = CERAnalysis
        fields = [
            'id',
            'ground_truth_transcription',
            'hypothesis_transcription',
            'created_at',
            'updated_at',
            
            # Analysis options
            'ignore_punctuation',
            'ignore_case',
            'ignore_whitespace',
            'ignore_numbers',
            'ignore_newlines',
            'ignore_chars',
            
            # Core metrics
            'cer_value',
            'accuracy',
            'num_correct',
            'num_substitutions',
            'num_insertions',
            'num_deletions',
            'total_characters',
            
            # Line statistics
            'original_lines_count',
            'discarded_lines_count',
            'processed_lines_count',
            
            # Detailed statistics
            'character_statistics',
            'block_statistics',
            'confusion_statistics',
            
            # Computed fields
            'error_breakdown',
        ]
        read_only_fields = [
            'id',
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
            'error_breakdown',
        ]


class CERAnalysisCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new CER analysis.
    """
    
    ground_truth_transcription_id = serializers.IntegerField(
        required=True,
        help_text='ID of the ground truth transcription'
    )
    hypothesis_transcription_id = serializers.IntegerField(
        required=True,
        help_text='ID of the hypothesis (OCR output) transcription'
    )
    
    # Analysis options
    ignore_punctuation = serializers.BooleanField(
        default=False,
        help_text='Ignore punctuation in comparison'
    )
    ignore_case = serializers.BooleanField(
        default=False,
        help_text='Ignore case differences'
    )
    ignore_whitespace = serializers.BooleanField(
        default=False,
        help_text='Ignore all whitespace'
    )
    ignore_numbers = serializers.BooleanField(
        default=False,
        help_text='Ignore numeric characters'
    )
    ignore_newlines = serializers.BooleanField(
        default=False,
        help_text='Ignore newline and carriage return characters'
    )
    ignore_chars = serializers.CharField(
        default='',
        allow_blank=True,
        max_length=255,
        help_text='String of characters to ignore'
    )
    analyze_unicode_blocks = serializers.BooleanField(
        default=True,
        help_text='Analyze Unicode blocks (Hebrew, Arabic, etc.)'
    )


class CERAnalysisListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views.
    """
    
    accuracy = serializers.FloatField(read_only=True)
    
    class Meta:
        model = CERAnalysis
        fields = [
            'id',
            'ground_truth_transcription',
            'hypothesis_transcription',
            'created_at',
            'cer_value',
            'accuracy',
            'total_characters',
        ]
