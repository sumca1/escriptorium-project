"""
⚡ Celery Tasks for Surya OCR Processing

This handles asynchronous Surya OCR processing in the background.

Usage:
    from apps.core.tasks import process_document_with_surya_task
    
    task = process_document_with_surya_task.delay(
        document_id=1,
        image_paths=['path/to/image.jpg'],
        force_reprocess=False
    )
    
    # Later: check status
    task.status  # 'PENDING', 'PROGRESS', 'SUCCESS', 'FAILURE'
    task.result  # {'pages_processed': 5, 'lines_created': 123}
"""

from celery import shared_task, current_task
from django.db import transaction
from django.utils import timezone
from apps.core.models import Document, DocumentPart, LineTranscription, Line
from escriptorium.ocr_engines.surya_engine import get_ocr_engine
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_document_with_surya_task(
    self,
    document_id,
    image_paths,
    force_reprocess=False
):
    """
    Process a document with Surya OCR in background.
    
    Args:
        document_id: ID of document to process
        image_paths: List of image file paths
        force_reprocess: Whether to reprocess existing lines
    
    Returns:
        dict with processing results
    """
    try:
        logger.info(f"Starting Surya OCR for document {document_id}")
        
        document = Document.objects.get(id=document_id)
        
        # Update task state
        current_task.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': len(image_paths),
                'status': 'Initializing Surya engine...'
            }
        )
        
        # Get engine
        try:
            engine = get_ocr_engine()
        except Exception as e:
            logger.error(f"Failed to initialize Surya engine: {e}")
            raise self.retry(exc=e, countdown=60)
        
        # Process pages
        results = engine.recognize_pages(image_paths)
        
        lines_created = 0
        pages_processed = 0
        
        with transaction.atomic():
            for i, (part, result) in enumerate(zip(
                document.parts.all(),
                results
            )):
                # Update progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': len(image_paths),
                        'status': f'Processing page {i + 1}/{len(image_paths)}...',
                        'lines_created': lines_created
                    }
                )
                
                if not result.success:
                    logger.warning(f"Failed to process page {i}: {result.error}")
                    continue
                
                # Delete existing transcriptions if force_reprocess
                if force_reprocess:
                    part.lines.all().delete()
                
                # Create lines and transcriptions
                for line_result in result.lines:
                    try:
                        # Create line if it doesn't exist
                        line, created = Line.objects.get_or_create(
                            document_part=part,
                            bounding_box=line_result.polygon,
                            defaults={'order': line_result.line_number or 0}
                        )
                        
                        # Create transcription
                        transcription = LineTranscription.objects.create(
                            line=line,
                            transcription=line_result.text,
                            confidence=line_result.confidence
                        )
                        
                        lines_created += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to create transcription: {e}")
                        continue
                
                pages_processed += 1
        
        logger.info(
            f"Completed Surya OCR for document {document_id}: "
            f"{pages_processed} pages, {lines_created} lines"
        )
        
        return {
            'document_id': document_id,
            'pages_processed': pages_processed,
            'lines_created': lines_created,
            'status': 'completed'
        }
        
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        return {
            'error': f'Document {document_id} not found',
            'status': 'failed'
        }
    
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}", exc_info=True)
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def cleanup_old_ocr_tasks():
    """
    Clean up old OCR processing records.
    Remove transcriptions older than 30 days without active references.
    """
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    # Find old transcriptions
    old_transcriptions = LineTranscription.objects.filter(
        created_at__lt=cutoff_date
    ).delete()
    
    logger.info(f"Cleaned up {old_transcriptions[0]} old transcriptions")
    
    return {'deleted': old_transcriptions[0]}
