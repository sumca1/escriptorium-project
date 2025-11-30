# Error Detection API Views - BiblIA Enhancement
# Created: 2025-10-20
# Purpose: REST API endpoints for error detection and correction

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from core.models import (
    LineTranscription,
    DetectedError,
    ErrorCorrection,
    CustomDictionaryWord,
    ErrorPattern
)
from core.tasks import detect_errors_in_line

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def get_line_errors(request, line_id):
    """
    קבל רשימת שגיאות עבור שורה
    Get list of errors for a line
    
    GET /api/errors/line/<line_id>/
    
    Returns:
        {
            "line_id": 123,
            "errors": [
                {
                    "id": 1,
                    "error_type": "spelling",
                    "text": "שלוס",
                    "start_pos": 0,
                    "end_pos": 4,
                    "suggestions": ["שלום", "שלוש"],
                    "severity": "medium",
                    "status": "pending"
                }
            ]
        }
    """
    try:
        line_trans = get_object_or_404(LineTranscription, pk=line_id)
        
        # Check permissions
        if not line_trans.line.document_part.document.readable_by(request.user):
            return JsonResponse({"error": "Permission denied"}, status=403)
        
        errors = DetectedError.objects.filter(
            line=line_trans
        ).order_by('start_pos')
        
        errors_data = [{
            "id": error.pk,
            "error_type": error.error_type,
            "text": error.text,
            "start_pos": error.start_pos,
            "end_pos": error.end_pos,
            "suggestions": error.suggestions,
            "severity": error.severity,
            "status": error.status,
            "confidence_score": float(error.confidence_score) if error.confidence_score else None,
            "pattern_name": error.pattern_name if hasattr(error, 'pattern_name') else None
        } for error in errors]
        
        return JsonResponse({
            "line_id": line_id,
            "errors": errors_data,
            "total": len(errors_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting errors for line {line_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def correct_error(request, error_id):
    """
    תקן שגיאה
    Correct an error
    
    POST /api/errors/<error_id>/correct/
    Body: {
        "corrected_text": "שלום",
        "apply_to_line": true  // optional: apply correction to line content
    }
    
    Returns:
        {
            "success": true,
            "error_id": 1,
            "correction_id": 5,
            "was_from_suggestion": true,
            "suggestion_rank": 1
        }
    """
    import json
    
    try:
        error = get_object_or_404(DetectedError, pk=error_id)
        
        # Check permissions
        if not error.line.line.document_part.document.writable_by(request.user):
            return JsonResponse({"error": "Permission denied"}, status=403)
        
        data = json.loads(request.body)
        corrected_text = data.get('corrected_text', '').strip()
        apply_to_line = data.get('apply_to_line', False)
        
        if not corrected_text:
            return JsonResponse({"error": "corrected_text is required"}, status=400)
        
        # Check if correction was from suggestions
        was_from_suggestion = corrected_text in error.suggestions
        suggestion_rank = None
        if was_from_suggestion and error.suggestions:
            try:
                suggestion_rank = error.suggestions.index(corrected_text) + 1
            except ValueError:
                pass
        
        # Create correction record
        correction = error.mark_corrected(corrected_text, request.user)
        
        # Optionally apply to line content
        if apply_to_line and error.line.content:
            line_content = error.line.content
            # Replace the error text with corrected text
            new_content = (
                line_content[:error.start_pos] + 
                corrected_text + 
                line_content[error.end_pos:]
            )
            error.line.content = new_content
            error.line.save()
            logger.info(f"✓ Applied correction to line {error.line.pk}")
        
        return JsonResponse({
            "success": True,
            "error_id": error_id,
            "correction_id": correction.pk if correction else None,
            "was_from_suggestion": was_from_suggestion,
            "suggestion_rank": suggestion_rank,
            "applied_to_line": apply_to_line
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error correcting error {error_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ignore_error(request, error_id):
    """
    התעלם משגיאה
    Ignore an error
    
    POST /api/errors/<error_id>/ignore/
    """
    try:
        error = get_object_or_404(DetectedError, pk=error_id)
        
        # Check permissions
        if not error.line.line.document_part.document.writable_by(request.user):
            return JsonResponse({"error": "Permission denied"}, status=403)
        
        error.mark_ignored()
        
        return JsonResponse({
            "success": True,
            "error_id": error_id,
            "status": "ignored"
        })
        
    except Exception as e:
        logger.error(f"Error ignoring error {error_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def add_to_dictionary(request):
    """
    הוסף מילה למילון מותאם אישית
    Add word to custom dictionary
    
    POST /api/errors/dictionary/add/
    Body: {
        "word": "ירושלים",
        "language": "he",
        "project_id": 5  // optional
    }
    """
    import json
    
    try:
        data = json.loads(request.body)
        word = data.get('word', '').strip()
        language = data.get('language', 'he')
        project_id = data.get('project_id')
        
        if not word:
            return JsonResponse({"error": "word is required"}, status=400)
        
        # Get project if specified
        project = None
        if project_id:
            from core.models import Project
            project = get_object_or_404(Project, pk=project_id)
            if not project.writable_by(request.user):
                return JsonResponse({"error": "Permission denied"}, status=403)
        
        # Create custom word
        custom_word, created = CustomDictionaryWord.get_or_create(
            word=word,
            language=language,
            project=project,
            user=request.user
        )
        
        if not created:
            custom_word.increment_usage()
        
        return JsonResponse({
            "success": True,
            "word": word,
            "created": created,
            "usage_count": custom_word.usage_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error adding word to dictionary: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def rescan_line(request, line_id):
    """
    סרוק מחדש שורה לזיהוי שגיאות
    Rescan a line for errors
    
    POST /api/errors/line/<line_id>/rescan/
    """
    try:
        line_trans = get_object_or_404(LineTranscription, pk=line_id)
        
        # Check permissions
        if not line_trans.line.document_part.document.writable_by(request.user):
            return JsonResponse({"error": "Permission denied"}, status=403)
        
        # Run detection task
        result = detect_errors_in_line(line_id)
        
        return JsonResponse({
            "success": True,
            "line_id": line_id,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error rescanning line {line_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_error_statistics(request):
    """
    קבל סטטיסטיקות על שגיאות
    Get error statistics
    
    GET /api/errors/stats/
    Query params:
        - project_id: Filter by project
        - document_id: Filter by document
    """
    try:
        from django.db.models import Count
        
        # Base query
        errors = DetectedError.objects.all()
        
        # Filter by project
        project_id = request.GET.get('project_id')
        if project_id:
            errors = errors.filter(
                line__line__document_part__document__project_id=project_id
            )
        
        # Filter by document
        document_id = request.GET.get('document_id')
        if document_id:
            errors = errors.filter(
                line__line__document_part__document_id=document_id
            )
        
        # Calculate statistics
        total_errors = errors.count()
        by_type = list(errors.values('error_type').annotate(count=Count('id')))
        by_severity = list(errors.values('severity').annotate(count=Count('id')))
        by_status = list(errors.values('status').annotate(count=Count('id')))
        
        # Top patterns
        pattern_errors = errors.filter(error_type='pattern')
        top_patterns = list(
            pattern_errors.values('pattern_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        return JsonResponse({
            "total_errors": total_errors,
            "by_type": by_type,
            "by_severity": by_severity,
            "by_status": by_status,
            "top_patterns": top_patterns
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return JsonResponse({"error": str(e)}, status=500)
