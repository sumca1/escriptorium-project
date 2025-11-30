"""
OCR Comparison Views for CERberus
==================================

Provides side-by-side comparison of different OCR engines (Kraken vs Tesseract)
with detailed metrics and visual diff highlighting.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.models import Document, Transcription
from .models import CERAnalysis
from .analyzer import CERAnalyzer
from .diff_engine import CharacterDiffEngine
from typing import List, Dict
import json


@login_required
def comparison_page(request, document_id):
    """
    Render the OCR Comparison page for a specific document.
    
    Args:
        document_id: The document to compare transcriptions for
    """
    document = get_object_or_404(Document, pk=document_id)
    
    # Get all active transcriptions for this document
    transcriptions = Transcription.objects.filter(
        document=document,
        archived=False
    ).select_related('model').order_by('-created_at')
    
    context = {
        'document': document,
        'transcriptions': transcriptions,
        'transcription_count': transcriptions.count(),
    }
    
    return render(request, 'cerberus/comparison.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compare_transcriptions(request):
    """
    Compare two transcriptions and return detailed comparison data.
    
    Request body:
    {
        "transcription_1_id": 123,
        "transcription_2_id": 456,
        "ground_truth_id": 789,  // optional
        "options": {
            "ignore_case": false,
            "ignore_punctuation": false,
            "ignore_whitespace": false,
            "show_diff": true
        }
    }
    
    Response:
    {
        "comparison_id": "trans-123-vs-456",
        "transcription_1": {...},
        "transcription_2": {...},
        "metrics": {
            "cer_1": 12.5,
            "cer_2": 15.3,
            "accuracy_1": 87.5,
            "accuracy_2": 84.7,
            "winner": "transcription_1"
        },
        "diff_data": {...},
        "visual_comparison": {...}
    }
    """
    
    trans1_id = request.data.get('transcription_1_id')
    trans2_id = request.data.get('transcription_2_id')
    gt_id = request.data.get('ground_truth_id')
    options = request.data.get('options', {})
    
    if not trans1_id or not trans2_id:
        return Response(
            {'error': 'Both transcription IDs are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get transcriptions
    trans1 = get_object_or_404(Transcription, pk=trans1_id)
    trans2 = get_object_or_404(Transcription, pk=trans2_id)
    
    # Get texts
    text1 = _get_transcription_text(trans1)
    text2 = _get_transcription_text(trans2)
    
    result = {
        'comparison_id': f'trans-{trans1_id}-vs-{trans2_id}',
        'transcription_1': {
            'id': trans1.id,
            'name': trans1.name,
            'model': trans1.model.name if trans1.model else 'Manual',
            'created_at': trans1.created_at.isoformat(),
            'text_length': len(text1),
        },
        'transcription_2': {
            'id': trans2.id,
            'name': trans2.name,
            'model': trans2.model.name if trans2.model else 'Manual',
            'created_at': trans2.created_at.isoformat(),
            'text_length': len(text2),
        },
    }
    
    # If ground truth provided, calculate CER for both
    if gt_id:
        gt = get_object_or_404(Transcription, pk=gt_id)
        gt_text = _get_transcription_text(gt)
        
        # Analyze both transcriptions against ground truth
        analyzer = CERAnalyzer()
        
        analysis1 = analyzer.analyze(
            gt_text, 
            text1,
            ignore_case=options.get('ignore_case', False),
            ignore_punctuation=options.get('ignore_punctuation', False),
            ignore_whitespace=options.get('ignore_whitespace', False)
        )
        
        analysis2 = analyzer.analyze(
            gt_text,
            text2,
            ignore_case=options.get('ignore_case', False),
            ignore_punctuation=options.get('ignore_punctuation', False),
            ignore_whitespace=options.get('ignore_whitespace', False)
        )
        
        result['ground_truth'] = {
            'id': gt.id,
            'name': gt.name,
            'text_length': len(gt_text),
        }
        
        result['metrics'] = {
            'cer_1': round(analysis1['cer_value'], 2),
            'cer_2': round(analysis2['cer_value'], 2),
            'accuracy_1': round(analysis1['accuracy'], 2),
            'accuracy_2': round(analysis2['accuracy'], 2),
            'wer_1': round(_calculate_wer(gt_text, text1), 2),
            'wer_2': round(_calculate_wer(gt_text, text2), 2),
            'winner': 'transcription_1' if analysis1['cer_value'] < analysis2['cer_value'] else 'transcription_2',
            'cer_difference': abs(round(analysis1['cer_value'] - analysis2['cer_value'], 2)),
        }
        
        result['detailed_analysis_1'] = {
            'substitutions': analysis1['num_substitutions'],
            'insertions': analysis1['num_insertions'],
            'deletions': analysis1['num_deletions'],
            'correct': analysis1['num_correct'],
        }
        
        result['detailed_analysis_2'] = {
            'substitutions': analysis2['num_substitutions'],
            'insertions': analysis2['num_insertions'],
            'deletions': analysis2['num_deletions'],
            'correct': analysis2['num_correct'],
        }
    
    # Generate diff visualization if requested
    if options.get('show_diff', True):
        diff_engine = CharacterDiffEngine(
            ignore_case=options.get('ignore_case', False)
        )
        
        diff_result = diff_engine.diff(text1, text2)
        
        result['diff_data'] = {
            'summary': diff_result['summary'],
            'visualization': diff_result['visualization'],
            'has_differences': diff_result['visualization']['has_differences'],
        }
    
    # Calculate similarity metrics
    result['similarity'] = {
        'exact_match': text1 == text2,
        'length_ratio': round(len(text2) / len(text1), 2) if len(text1) > 0 else 0,
        'common_characters': _count_common_chars(text1, text2),
    }
    
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_transcriptions(request, document_id):
    """
    Get all transcriptions for a document, grouped by model type.
    
    Response:
    {
        "document_id": 123,
        "document_name": "My Document",
        "transcriptions": [
            {
                "id": 1,
                "name": "Kraken Model v1",
                "model": "Kraken Hebrew",
                "model_type": "kraken",
                "created_at": "...",
                "text_preview": "first 100 chars..."
            },
            ...
        ],
        "grouped_by_model": {
            "kraken": [...],
            "tesseract": [...],
            "manual": [...]
        }
    }
    """
    document = get_object_or_404(Document, pk=document_id)
    
    transcriptions = Transcription.objects.filter(
        document=document,
        archived=False
    ).select_related('model').order_by('-created_at')
    
    trans_data = []
    grouped = {'kraken': [], 'tesseract': [], 'manual': [], 'other': []}
    
    for trans in transcriptions:
        text = _get_transcription_text(trans)
        preview = text[:100] + '...' if len(text) > 100 else text
        
        # Determine model type
        model_type = 'manual'
        if trans.model:
            model_name_lower = trans.model.name.lower()
            if 'kraken' in model_name_lower:
                model_type = 'kraken'
            elif 'tesseract' in model_name_lower:
                model_type = 'tesseract'
            else:
                model_type = 'other'
        
        data = {
            'id': trans.id,
            'name': trans.name,
            'model': trans.model.name if trans.model else 'Manual',
            'model_type': model_type,
            'created_at': trans.created_at.isoformat(),
            'text_preview': preview,
            'text_length': len(text),
        }
        
        trans_data.append(data)
        grouped[model_type].append(data)
    
    return Response({
        'document_id': document.id,
        'document_name': document.name,
        'transcriptions': trans_data,
        'grouped_by_model': grouped,
        'total_count': len(trans_data),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comparison_statistics(request, document_id):
    """
    Get statistical comparison of all OCR models used in a document.
    
    Response:
    {
        "document_id": 123,
        "models_summary": {
            "kraken": {
                "count": 5,
                "avg_cer": 12.5,
                "best_cer": 8.2,
                "worst_cer": 18.3
            },
            "tesseract": {...}
        },
        "best_model": "Kraken Hebrew v2",
        "recommendations": [...]
    }
    """
    document = get_object_or_404(Document, pk=document_id)
    
    # Get all CER analyses for this document
    analyses = CERAnalysis.objects.filter(
        ground_truth_transcription__document=document
    ).select_related(
        'ground_truth_transcription__model',
        'hypothesis_transcription__model'
    )
    
    models_summary = {}
    
    for analysis in analyses:
        model_name = (analysis.hypothesis_transcription.model.name 
                     if analysis.hypothesis_transcription.model 
                     else 'Manual')
        
        if model_name not in models_summary:
            models_summary[model_name] = {
                'count': 0,
                'total_cer': 0,
                'cers': [],
                'model_type': _detect_model_type(model_name),
            }
        
        models_summary[model_name]['count'] += 1
        models_summary[model_name]['total_cer'] += analysis.cer_value
        models_summary[model_name]['cers'].append(analysis.cer_value)
    
    # Calculate statistics
    for model_name, data in models_summary.items():
        data['avg_cer'] = round(data['total_cer'] / data['count'], 2)
        data['best_cer'] = round(min(data['cers']), 2)
        data['worst_cer'] = round(max(data['cers']), 2)
        del data['total_cer']
        del data['cers']
    
    # Determine best model
    best_model = None
    if models_summary:
        best_model = min(models_summary.items(), key=lambda x: x[1]['avg_cer'])
    
    # Generate recommendations
    recommendations = _generate_recommendations(models_summary)
    
    return Response({
        'document_id': document.id,
        'models_summary': models_summary,
        'best_model': best_model[0] if best_model else None,
        'best_avg_cer': best_model[1]['avg_cer'] if best_model else None,
        'recommendations': recommendations,
    })


# Helper functions

def _get_transcription_text(transcription: Transcription) -> str:
    """Extract text from a transcription."""
    try:
        # Get all lines in order
        lines = transcription.lines.order_by('order')
        text_parts = []
        
        for line in lines:
            line_text = line.content if hasattr(line, 'content') else ''
            text_parts.append(line_text)
        
        return '\n'.join(text_parts)
    except Exception as e:
        print(f"Error getting transcription text: {e}")
        return ''


def _calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate Word Error Rate."""
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    if len(ref_words) == 0:
        return 0.0
    
    # Simple WER calculation using edit distance
    from difflib import SequenceMatcher
    matcher = SequenceMatcher(None, ref_words, hyp_words)
    
    correct = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            correct += (i2 - i1)
    
    errors = len(ref_words) - correct
    return (errors / len(ref_words)) * 100


def _count_common_chars(text1: str, text2: str) -> int:
    """Count characters that appear in both texts."""
    set1 = set(text1)
    set2 = set(text2)
    return len(set1.intersection(set2))


def _detect_model_type(model_name: str) -> str:
    """Detect model type from name."""
    name_lower = model_name.lower()
    if 'kraken' in name_lower:
        return 'kraken'
    elif 'tesseract' in name_lower:
        return 'tesseract'
    elif 'manual' in name_lower:
        return 'manual'
    else:
        return 'other'


def _generate_recommendations(models_summary: Dict) -> List[str]:
    """Generate recommendations based on model performance."""
    recommendations = []
    
    if not models_summary:
        return ['No analyses available yet. Create CER analyses to get recommendations.']
    
    # Find best and worst
    sorted_models = sorted(models_summary.items(), key=lambda x: x[1]['avg_cer'])
    best = sorted_models[0]
    
    if best[1]['avg_cer'] < 5:
        recommendations.append(f"✅ Excellent! {best[0]} achieves <5% CER - production ready.")
    elif best[1]['avg_cer'] < 15:
        recommendations.append(f"👍 Good! {best[0]} achieves <15% CER - minor improvements possible.")
    else:
        recommendations.append(f"⚠️ {best[0]} has {best[1]['avg_cer']}% CER - consider fine-tuning.")
    
    # Compare Kraken vs Tesseract if both exist
    kraken_models = [m for m, d in models_summary.items() if d['model_type'] == 'kraken']
    tesseract_models = [m for m, d in models_summary.items() if d['model_type'] == 'tesseract']
    
    if kraken_models and tesseract_models:
        kraken_avg = sum(models_summary[m]['avg_cer'] for m in kraken_models) / len(kraken_models)
        tesseract_avg = sum(models_summary[m]['avg_cer'] for m in tesseract_models) / len(tesseract_models)
        
        if abs(kraken_avg - tesseract_avg) < 2:
            recommendations.append("📊 Kraken and Tesseract perform similarly - choose based on speed/accuracy needs.")
        elif kraken_avg < tesseract_avg:
            diff = round(tesseract_avg - kraken_avg, 1)
            recommendations.append(f"🏆 Kraken outperforms Tesseract by {diff}% CER on average.")
        else:
            diff = round(kraken_avg - tesseract_avg, 1)
            recommendations.append(f"🏆 Tesseract outperforms Kraken by {diff}% CER on average.")
    
    # Variation check
    for model_name, data in models_summary.items():
        if data['count'] >= 3:
            variation = data['worst_cer'] - data['best_cer']
            if variation > 10:
                recommendations.append(
                    f"⚠️ {model_name} shows high variation ({variation}% CER range) - "
                    "check image quality consistency."
                )
    
    return recommendations
