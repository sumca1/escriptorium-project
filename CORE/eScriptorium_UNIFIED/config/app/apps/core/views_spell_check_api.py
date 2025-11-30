"""
Spell Check API Views for Error Correction Workspace
Provides endpoints for the new visual error correction interface
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
import json
from datetime import datetime

from core.models import (
    DocumentPart, 
    Line, 
    Transcription,
    LineTranscription
)
from core.spell_checker import SpellChecker


@login_required
@require_http_methods(["GET"])
def get_document_lines(request, transcription_id):
    """
    Get all lines from a transcription with their errors and images
    Returns structured data for the error correction workspace
    """
    transcription = get_object_or_404(
        Transcription.objects.select_related('document'),
        id=transcription_id
    )
    
    # Get all lines with transcriptions
    lines = Line.objects.filter(
        document_part__document=transcription.document
    ).select_related(
        'document_part'
    ).prefetch_related(
        'transcriptions'
    ).order_by('document_part__order', 'order')
    
    spell_checker = SpellChecker()
    result_lines = []
    
    for line in lines:
        # Get transcription content for this line
        line_trans = line.transcriptions.filter(
            transcription=transcription
        ).first()
        
        if not line_trans:
            continue
        
        content = line_trans.content or ''
        
        # Check for spelling errors
        errors = spell_checker.check_text(content, language='auto')
        
        # Build image URL
        image_url = None
        if line.baseline:
            try:
                # Generate line image URL
                image_url = f"/api/lines/{line.id}/image/"
            except Exception:
                pass
        
        result_lines.append({
            'id': line.id,
            'line_trans_id': line_trans.id,
            'content': content,
            'line_order': line.order,
            'part_order': line.document_part.order,
            'image_url': image_url,
            'errors': [
                {
                    'word': err['word'],
                    'start': err['start'],
                    'end': err['end'],
                    'suggestions': err.get('suggestions', [])[:5]  # Top 5 suggestions
                }
                for err in errors
            ],
            'corrected': False
        })
    
    return JsonResponse({
        'success': True,
        'lines': result_lines,
        'total': len(result_lines),
        'with_errors': sum(1 for l in result_lines if l['errors'])
    })


@login_required
@require_http_methods(["POST"])
def update_line_content(request, line_trans_id):
    """
    Update the content of a line transcription
    """
    try:
        data = json.loads(request.body)
        new_content = data.get('content', '')
        
        line_trans = get_object_or_404(LineTranscription, id=line_trans_id)
        
        # Check permissions
        if line_trans.transcription.document.owner != request.user and not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        # Update content
        old_content = line_trans.content
        line_trans.content = new_content
        line_trans.save()
        
        return JsonResponse({
            'success': True,
            'old_content': old_content,
            'new_content': new_content,
            'updated_at': line_trans.updated_at.isoformat() if hasattr(line_trans, 'updated_at') else None
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def run_spell_check(request, transcription_id):
    """
    Run spell check on entire transcription
    Returns statistics about errors found
    """
    transcription = get_object_or_404(Transcription, id=transcription_id)
    
    # Check permissions
    if transcription.document.owner != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    spell_checker = SpellChecker()
    
    # Get all line transcriptions
    line_transcriptions = LineTranscription.objects.filter(
        transcription=transcription
    ).select_related('line')
    
    total_lines = 0
    total_errors = 0
    lines_with_errors = 0
    error_details = []
    
    for line_trans in line_transcriptions:
        total_lines += 1
        content = line_trans.content or ''
        
        errors = spell_checker.check_text(content, language='auto')
        
        if errors:
            lines_with_errors += 1
            total_errors += len(errors)
            
            error_details.append({
                'line_id': line_trans.line.id,
                'line_trans_id': line_trans.id,
                'error_count': len(errors),
                'errors': [
                    {
                        'word': err['word'],
                        'position': err['start'],
                        'suggestions': err.get('suggestions', [])[:3]
                    }
                    for err in errors[:5]  # Max 5 errors per line in summary
                ]
            })
    
    return JsonResponse({
        'success': True,
        'statistics': {
            'total_lines': total_lines,
            'lines_with_errors': lines_with_errors,
            'total_errors': total_errors,
            'error_rate': round((lines_with_errors / total_lines * 100), 2) if total_lines > 0 else 0
        },
        'error_details': error_details[:50],  # Return first 50 lines with errors
        'timestamp': datetime.now().isoformat()
    })


@login_required
@require_http_methods(["POST"])
def auto_correct_transcription(request, transcription_id):
    """
    Automatically correct high-confidence errors in transcription
    Safe mode: only corrects errors with single high-confidence suggestion
    """
    transcription = get_object_or_404(Transcription, id=transcription_id)
    
    # Check permissions
    if transcription.document.owner != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        mode = data.get('mode', 'safe')  # safe, review, aggressive
        confidence_threshold = data.get('confidence', 0.8)
        
        spell_checker = SpellChecker()
        
        line_transcriptions = LineTranscription.objects.filter(
            transcription=transcription
        )
        
        corrected_count = 0
        corrections_made = []
        
        for line_trans in line_transcriptions:
            content = line_trans.content or ''
            errors = spell_checker.check_text(content, language='auto')
            
            if not errors:
                continue
            
            modified = False
            new_content = content
            offset = 0  # Track position changes as we replace
            
            for error in sorted(errors, key=lambda x: x['start']):
                suggestions = error.get('suggestions', [])
                
                if not suggestions:
                    continue
                
                # Safe mode: only apply if there's one clear suggestion
                if mode == 'safe' and len(suggestions) > 1:
                    continue
                
                # Apply correction
                best_suggestion = suggestions[0]
                start = error['start'] + offset
                end = error['end'] + offset
                
                new_content = (
                    new_content[:start] + 
                    best_suggestion + 
                    new_content[end:]
                )
                
                # Update offset for next replacement
                offset += len(best_suggestion) - (end - start)
                
                corrected_count += 1
                modified = True
                
                corrections_made.append({
                    'line_id': line_trans.line.id,
                    'original': error['word'],
                    'correction': best_suggestion,
                    'position': error['start']
                })
            
            if modified:
                line_trans.content = new_content
                line_trans.save()
        
        return JsonResponse({
            'success': True,
            'corrected_count': corrected_count,
            'corrections': corrections_made[:100],  # First 100 corrections
            'mode': mode,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def export_error_report(request, transcription_id):
    """
    Export detailed error report as JSON
    """
    transcription = get_object_or_404(Transcription, id=transcription_id)
    
    # Check permissions
    if transcription.document.owner != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    spell_checker = SpellChecker()
    
    line_transcriptions = LineTranscription.objects.filter(
        transcription=transcription
    ).select_related('line')
    
    report = {
        'document': transcription.document.name,
        'transcription': transcription.name,
        'generated_at': datetime.now().isoformat(),
        'lines': []
    }
    
    for line_trans in line_transcriptions:
        content = line_trans.content or ''
        errors = spell_checker.check_text(content, language='auto')
        
        if errors:
            report['lines'].append({
                'line_id': line_trans.line.id,
                'order': line_trans.line.order,
                'content': content,
                'errors': [
                    {
                        'word': err['word'],
                        'position': err['start'],
                        'suggestions': err.get('suggestions', [])
                    }
                    for err in errors
                ]
            })
    
    # Return as downloadable JSON
    response = HttpResponse(
        json.dumps(report, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="error_report_{transcription_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    
    return response


@login_required
@require_http_methods(["GET"])
def get_line_image(request, line_id):
    """
    Get the image for a specific line
    Returns the line image cropped from the document part
    """
    from django.core.files.storage import default_storage
    from PIL import Image
    import io
    
    line = get_object_or_404(Line, id=line_id)
    
    try:
        # Get the document part image
        if not line.document_part.image:
            return HttpResponse(status=404)
        
        # Open the image
        image_path = line.document_part.image.path
        img = Image.open(image_path)
        
        # If baseline exists, crop to line
        if line.baseline and line.mask:
            # Get bounding box from mask
            # This is a simplified version - you might need more sophisticated cropping
            # based on your actual baseline/mask format
            pass
        
        # Convert to bytes
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        return HttpResponse(img_io, content_type='image/png')
        
    except Exception as e:
        return HttpResponse(status=404)
