"""
Analytics API Views
Provides comprehensive analytics data for models, training, and OCR operations
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import timedelta
import json

from core.models import (
    OcrModel,
    OcrModelDocument,
    Document,
    DocumentPart,
    Line,
    Transcription,
    LineTranscription,
)


@login_required
@require_http_methods(["GET"])
def get_model_training_status(request, model_id):
    """
    Get current training status and basic metrics for a model
    """
    model = get_object_or_404(
        OcrModel.objects.select_related('owner', 'script'),
        id=model_id
    )
    
    # Check permissions
    if not (model.public or model.owner == request.user or 
            model.ocr_model_rights.filter(user=request.user).exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get training data statistics
    training_docs = OcrModelDocument.objects.filter(
        ocr_model=model
    ).select_related('document')
    
    training_lines = 0
    
    for doc_model in training_docs:
        doc = doc_model.document
        total_lines = Line.objects.filter(
            document_part__document=doc
        ).count()
        training_lines += total_lines
    
    return JsonResponse({
        'model_id': model.id,
        'model_name': model.name,
        'accuracy': float(model.training_accuracy) if model.training_accuracy else None,
        'training': model.training,
        'job': model.job,
        'script': model.script.name if model.script else None,
        'owner': model.owner.username,
        'public': model.public,
        'file_size': model.file.size if model.file else None,
        'created': model.created_at.isoformat() if hasattr(model, 'created_at') else None,
        'updated': model.updated_at.isoformat() if hasattr(model, 'updated_at') else None,
        'training_data': {
            'training_lines': training_lines,
            'total_lines': training_lines,
            'documents_count': training_docs.count(),
        },
        'training_analytics': {
            'started_at': model.training_started_at.isoformat() if model.training_started_at else None,
            'completed_at': model.training_completed_at.isoformat() if model.training_completed_at else None,
            'duration_seconds': model.training_duration_seconds,
            'duration_minutes': round(model.training_duration_seconds / 60, 2) if model.training_duration_seconds else None,
            'total_epochs': model.training_total_epochs,
        }
    })


@login_required
@require_http_methods(["GET"])
def get_model_training_history(request, model_id):
    """
    Get training history with epoch-by-epoch metrics
    Returns real data if available, otherwise simulated progression
    """
    model = get_object_or_404(OcrModel, id=model_id)
    
    # Check permissions
    if not (model.public or model.owner == request.user or 
            model.ocr_model_rights.filter(user=request.user).exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    epochs = []
    
    # Check if we have real epoch history
    if model.training_epoch_history:
        epochs = model.training_epoch_history
        note = 'Real training history from model'
    elif model.training_accuracy:
        # Generate simulated training progression
        num_epochs = model.training_total_epochs if model.training_total_epochs > 0 else 10
        for i in range(1, num_epochs + 1):
            # Simulate accuracy improvement curve
            progress = i / num_epochs
            accuracy = progress * float(model.training_accuracy)
            
            epochs.append({
                'epoch': i,
                'accuracy': round(accuracy, 2),
                'loss': round((1 - progress) * 0.5, 4),  # Simulated
                'duration_minutes': 5 + (i * 2),  # Simulated
                'learning_rate': 0.001,  # Default
            })
        note = 'Historical epoch data not available - showing estimated progression'
    else:
        note = 'No training data available'
    
    return JsonResponse({
        'model_id': model.id,
        'epochs': epochs,
        'total_epochs': len(epochs),
        'best_accuracy': float(model.training_accuracy) if model.training_accuracy else None,
        'note': note
    })


@login_required
@require_http_methods(["GET"])
def get_models_overview(request):
    """
    Get overview statistics for all accessible models
    """
    # Get models the user can access
    models = OcrModel.objects.filter(
        Q(owner=request.user) | Q(public=True) | Q(ocr_model_rights__user=request.user)
    ).distinct().select_related('owner', 'script')
    
    total_models = models.count()
    active_training = models.filter(training=True).count()
    
    # Calculate average accuracy
    accuracies = [m.training_accuracy for m in models if m.training_accuracy]
    avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
    
    # Get model details
    models_data = []
    for model in models:
        # Get training data
        training_docs = OcrModelDocument.objects.filter(ocr_model=model)
        training_lines = 0
        
        for doc_model in training_docs:
            training_lines += Line.objects.filter(
                document_part__document=doc_model.document
            ).count()
        
        models_data.append({
            'id': model.id,
            'name': model.name,
            'accuracy': float(model.training_accuracy) if model.training_accuracy else 0,
            'training': model.training,
            'script': model.script.name if model.script else 'Unknown',
            'owner': model.owner.username,
            'training_lines': training_lines,
            'file_size': model.file.size if model.file else 0,
            'public': model.public,
            'total_epochs': model.training_total_epochs or 0,
            'duration_minutes': round(model.training_duration_seconds / 60, 2) if model.training_duration_seconds else 0,
            'completed_at': model.training_completed_at.isoformat() if model.training_completed_at else None,
        })
    
    return JsonResponse({
        'total_models': total_models,
        'active_training': active_training,
        'avg_accuracy': round(avg_accuracy, 2),
        'models': models_data
    })


@login_required
@require_http_methods(["GET"])
def get_document_statistics(request, document_id):
    """
    Get detailed statistics for a document
    """
    document = get_object_or_404(
        Document.objects.select_related('owner'),
        id=document_id
    )
    
    # Check permissions
    if document.owner != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get document parts
    parts = DocumentPart.objects.filter(document=document).order_by('order')
    
    # Get lines
    lines = Line.objects.filter(document_part__document=document)
    total_lines = lines.count()
    
    # Get transcriptions
    transcriptions = Transcription.objects.filter(document=document)
    
    transcription_stats = []
    for trans in transcriptions:
        line_trans = LineTranscription.objects.filter(
            transcription=trans
        )
        
        total_chars = sum(len(lt.content or '') for lt in line_trans)
        completed_lines = line_trans.exclude(Q(content='') | Q(content__isnull=True)).count()
        
        transcription_stats.append({
            'id': trans.id,
            'name': trans.name,
            'lines_count': line_trans.count(),
            'completed_lines': completed_lines,
            'completion_rate': round((completed_lines / line_trans.count() * 100), 2) if line_trans.count() > 0 else 0,
            'total_characters': total_chars,
            'avg_chars_per_line': round(total_chars / completed_lines, 2) if completed_lines > 0 else 0,
        })
    
    return JsonResponse({
        'document_id': document.id,
        'document_name': document.name,
        'parts_count': parts.count(),
        'total_lines': total_lines,
        'avg_lines_per_part': round(total_lines / parts.count(), 2) if parts.count() > 0 else 0,
        'transcriptions': transcription_stats,
        'created': document.created_at.isoformat() if hasattr(document, 'created_at') else None,
        'updated': document.updated_at.isoformat() if hasattr(document, 'updated_at') else None,
    })


@login_required
@require_http_methods(["GET"])
def get_system_statistics(request):
    """
    Get overall system statistics (admin only)
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    # Get counts
    total_documents = Document.objects.count()
    total_models = OcrModel.objects.count()
    total_users = request.user.__class__.objects.count()
    total_lines = Line.objects.count()
    total_transcriptions = Transcription.objects.count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    recent_documents = Document.objects.filter(
        created_at__gte=thirty_days_ago
    ).count() if hasattr(Document, 'created_at') else 0
    
    recent_models = OcrModel.objects.filter(
        created_at__gte=thirty_days_ago
    ).count() if hasattr(OcrModel, 'created_at') else 0
    
    # Training statistics
    models_with_accuracy = OcrModel.objects.exclude(
        training_accuracy__isnull=True
    )
    
    avg_model_accuracy = models_with_accuracy.aggregate(
        Avg('training_accuracy')
    )['training_accuracy__avg'] or 0
    
    return JsonResponse({
        'totals': {
            'documents': total_documents,
            'models': total_models,
            'users': total_users,
            'lines': total_lines,
            'transcriptions': total_transcriptions,
        },
        'recent_activity': {
            'new_documents': recent_documents,
            'new_models': recent_models,
        },
        'training': {
            'avg_accuracy': round(avg_model_accuracy, 2),
            'active_training': OcrModel.objects.filter(training=True).count(),
            'total_trained_models': models_with_accuracy.count(),
        },
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["GET"])
def export_analytics_report(request, model_id):
    """
    Export analytics report as JSON
    """
    model = get_object_or_404(OcrModel, id=model_id)
    
    # Check permissions
    if not (model.public or model.owner == request.user or 
            model.ocr_model_rights.filter(user=request.user).exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Gather all analytics data
    status_data = json.loads(
        get_model_training_status(request, model_id).content
    )
    history_data = json.loads(
        get_model_training_history(request, model_id).content
    )
    
    report = {
        'generated_at': timezone.now().isoformat(),
        'model': status_data,
        'training_history': history_data,
    }
    
    from django.http import HttpResponse
    response = HttpResponse(
        json.dumps(report, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="model_{model_id}_analytics_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
    
    return response
