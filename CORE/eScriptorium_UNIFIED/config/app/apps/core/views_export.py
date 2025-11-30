"""
BiblIA Export Views
===================
Views for exporting transcriptions to PDF and DOCX
"""

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _

from core.models import Document, Transcription
from core.export_pdf import PDFExporter
from core.export_docx import DOCXExporter


@login_required
@require_http_methods(["POST"])
def export_pdf(request, document_pk):
    """
    Export document transcription to PDF
    
    POST parameters:
    - transcription_id: ID of transcription to export
    - layout: text_only | image_only | image_text_overlay | image_text_side_by_side
    - include_metadata: true | false
    - font_size: 8-24 (default: 12)
    - line_spacing: 1.0-3.0 (default: 1.5)
    """
    document = get_object_or_404(Document, pk=document_pk)
    
    # Check permissions
    if document.owner != request.user and not request.user.is_staff:
        return JsonResponse({'error': _('Permission denied')}, status=403)
    
    # Get parameters
    transcription_id = request.POST.get('transcription_id')
    if not transcription_id:
        return JsonResponse({'error': _('Transcription ID required')}, status=400)
    
    transcription = get_object_or_404(Transcription, pk=transcription_id, document=document)
    
    layout = request.POST.get('layout', PDFExporter.LAYOUT_TEXT_ONLY)
    include_metadata = request.POST.get('include_metadata', 'true').lower() == 'true'
    
    try:
        font_size = int(request.POST.get('font_size', 12))
        font_size = max(8, min(24, font_size))  # Clamp between 8-24
    except (ValueError, TypeError):
        font_size = 12
    
    try:
        line_spacing = float(request.POST.get('line_spacing', 1.5))
        line_spacing = max(1.0, min(3.0, line_spacing))  # Clamp between 1.0-3.0
    except (ValueError, TypeError):
        line_spacing = 1.5
    
    # Export to PDF
    try:
        exporter = PDFExporter(document, transcription)
        pdf_buffer = exporter.export(
            layout=layout,
            include_metadata=include_metadata,
            font_size=font_size,
            line_spacing=line_spacing
        )
        
        # Create response
        filename = f"{document.name}_{transcription.name}.pdf"
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def export_docx(request, document_pk):
    """
    Export document transcription to DOCX
    
    POST parameters:
    - transcription_id: ID of transcription to export
    - include_metadata: true | false
    - include_images: true | false
    - paragraph_per_line: true | false
    """
    document = get_object_or_404(Document, pk=document_pk)
    
    # Check permissions
    if document.owner != request.user and not request.user.is_staff:
        return JsonResponse({'error': _('Permission denied')}, status=403)
    
    # Get parameters
    transcription_id = request.POST.get('transcription_id')
    if not transcription_id:
        return JsonResponse({'error': _('Transcription ID required')}, status=400)
    
    transcription = get_object_or_404(Transcription, pk=transcription_id, document=document)
    
    include_metadata = request.POST.get('include_metadata', 'true').lower() == 'true'
    include_images = request.POST.get('include_images', 'false').lower() == 'true'
    paragraph_per_line = request.POST.get('paragraph_per_line', 'true').lower() == 'true'
    
    # Export to DOCX
    try:
        exporter = DOCXExporter(document, transcription)
        docx_buffer = exporter.export(
            include_metadata=include_metadata,
            include_images=include_images,
            paragraph_per_line=paragraph_per_line
        )
        
        # Create response
        filename = f"{document.name}_{transcription.name}.docx"
        response = HttpResponse(
            docx_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def export_options(request, document_pk):
    """
    Get available export options for a document
    
    Returns JSON with:
    - transcriptions: List of available transcriptions
    - layouts: Available PDF layouts
    - default_options: Default export options
    """
    document = get_object_or_404(Document, pk=document_pk)
    
    # Check permissions
    if document.owner != request.user and not request.user.is_staff:
        return JsonResponse({'error': _('Permission denied')}, status=403)
    
    # Get transcriptions
    transcriptions = Transcription.objects.filter(document=document)
    trans_list = [{
        'id': t.pk,
        'name': t.name,
        'archived': t.archived
    } for t in transcriptions]
    
    return JsonResponse({
        'transcriptions': trans_list,
        'layouts': {
            'text_only': _('Text Only'),
            'image_only': _('Image Only'),
            'image_text_overlay': _('Image with Text Overlay'),
            'image_text_side_by_side': _('Image and Text Side by Side')
        },
        'default_options': {
            'layout': 'text_only',
            'include_metadata': True,
            'include_images': False,
            'font_size': 12,
            'line_spacing': 1.5,
            'paragraph_per_line': True
        }
    })
