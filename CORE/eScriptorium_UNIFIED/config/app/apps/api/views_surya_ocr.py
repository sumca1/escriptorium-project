"""
🌐 REST API Views for Surya OCR Integration

This provides REST API endpoints for Surya OCR in eScriptorium.

Endpoints:
  POST /api/documents/{id}/ocr/surya/                - Start OCR
  GET /api/documents/{id}/ocr/surya/status/         - Check status
  GET /api/ocr/engines/                              - List engines
  GET /api/ocr/engines/surya/                        - Surya metadata
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from apps.core.models import Document, DocumentPart, LineTranscription
from escriptorium.ocr_engines import get_registry
from escriptorium.ocr_engines.surya_engine import get_ocr_engine
import logging
from celery import current_task

logger = logging.getLogger(__name__)


class OCREngineViewSet(viewsets.ViewSet):
    """API for OCR engine management."""
    
    @action(detail=False, methods=['get'])
    def list_engines(self, request):
        """
        GET /api/ocr/engines/
        
        List all available OCR engines.
        """
        registry = get_registry()
        engines = registry.list_engines()
        
        return Response({
            'count': len(engines),
            'engines': engines
        })
    
    @action(detail=False, methods=['get'], url_path='surya')
    def surya_info(self, request):
        """
        GET /api/ocr/engines/surya/
        
        Get Surya engine metadata.
        """
        registry = get_registry()
        metadata = registry.get_metadata('surya')
        
        if metadata is None:
            return Response(
                {'error': 'Surya engine not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Add current status
        try:
            engine = get_ocr_engine()
            status_info = engine.get_status()
        except Exception as e:
            status_info = {'error': str(e)}
        
        return Response({
            'metadata': metadata,
            'status': status_info
        })
    
    @action(detail=False, methods=['post'], url_path='surya/test')
    def test_surya(self, request):
        """
        POST /api/ocr/engines/surya/test/
        
        Test if Surya is working.
        """
        try:
            engine = get_ocr_engine()
            status_info = engine.get_status()
            return Response({
                'status': 'ok',
                'device': status_info['device'],
                'models_loaded': status_info['models_loaded'],
                'cuda_available': status_info['cuda_available']
            })
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class DocumentSuryaOCRViewSet(viewsets.ViewSet):
    """API for processing documents with Surya OCR."""
    
    @action(detail=True, methods=['post'], url_path='ocr/surya')
    def process_with_surya(self, request, pk=None):
        """
        POST /api/documents/{id}/ocr/surya/
        
        Start Surya OCR processing for a document.
        
        Body:
        {
            "task_id": "async-task-id",  # Optional
            "force": false,               # Reprocess if exists
            "language": "he"              # Target language
        }
        """
        document = get_object_or_404(Document, pk=pk)
        
        force = request.data.get('force', False)
        
        # Check existing transcriptions
        has_transcriptions = (
            document.parts
            .filter(lines__transcriptions__isnull=False)
            .count() > 0
        )
        
        if has_transcriptions and not force:
            return Response(
                {
                    'error': 'Document already has transcriptions. Set force=true to reprocess',
                    'has_transcriptions': True
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get image paths
        parts = document.parts.all()
        image_paths = [str(p.image.path) for p in parts if p.image]
        
        if not image_paths:
            return Response(
                {'error': 'Document has no images'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to import Celery task
        try:
            from apps.core.tasks import process_document_with_surya_task
            
            task = process_document_with_surya_task.delay(
                document_id=document.id,
                image_paths=image_paths,
                force_reprocess=force
            )
            
            return Response({
                'status': 'processing',
                'task_id': task.id,
                'message': f'Processing {len(image_paths)} pages with Surya OCR',
                'document_id': document.id
            }, status=status.HTTP_202_ACCEPTED)
            
        except ImportError:
            # Fallback: Process synchronously
            logger.warning("Celery not available, processing synchronously")
            
            try:
                engine = get_ocr_engine()
                results = engine.recognize_pages(image_paths)
                
                created = 0
                for part, result in zip(parts, results):
                    if result.success:
                        for line in result.lines:
                            LineTranscription.objects.create(
                                line=part,
                                transcription=line.text,
                                confidence=line.confidence,
                                bounding_box=line.polygon
                            )
                            created += 1
                
                return Response({
                    'status': 'completed',
                    'message': f'Processed {len(results)} pages',
                    'transcriptions_created': created
                })
                
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @action(detail=True, methods=['get'], url_path='ocr/surya/status')
    def surya_status(self, request, pk=None):
        """
        GET /api/documents/{id}/ocr/surya/status/
        
        Get OCR processing status for a document.
        """
        document = get_object_or_404(Document, pk=pk)
        
        parts = document.parts.all()
        
        total_lines = 0
        processed_lines = 0
        parts_processed = 0
        
        for part in parts:
            lines = part.lines.all()
            total_lines += lines.count()
            
            transcribed = lines.filter(transcriptions__isnull=False).count()
            processed_lines += transcribed
            
            if transcribed > 0:
                parts_processed += 1
        
        progress = 0
        if total_lines > 0:
            progress = (processed_lines / total_lines) * 100
        
        return Response({
            'document_id': document.id,
            'total_parts': parts.count(),
            'parts_processed': parts_processed,
            'total_lines': total_lines,
            'processed_lines': processed_lines,
            'progress': round(progress, 1),
            'status': 'completed' if progress == 100 else 'in_progress'
        })
    
    @action(detail=True, methods=['get'], url_path='ocr/surya/results')
    def surya_results(self, request, pk=None):
        """
        GET /api/documents/{id}/ocr/surya/results/
        
        Get OCR results (transcriptions) for a document.
        """
        document = get_object_or_404(Document, pk=pk)
        
        results = []
        for part in document.parts.all():
            transcriptions = part.lines.filter(
                transcriptions__isnull=False
            ).values_list('transcriptions__transcription', flat=True)
            
            results.append({
                'part_id': part.id,
                'page_number': part.order,
                'transcriptions': list(transcriptions)
            })
        
        return Response({
            'document_id': document.id,
            'pages': results
        })
