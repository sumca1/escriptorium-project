"""
Celery tasks for text alignment using Passim service.

משימות Celery ליישור טקסט באמצעות שירות Passim.
"""

from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging

from core.models import (
    TextAlignment, 
    AlignmentPair, 
    AlignmentJob,
    Document,
    LineTranscription
)
from core.passim_wrapper import PassimWrapper

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def align_documents_task(self, alignment_id: int):
    """
    Background task to align two documents using Passim service.
    
    משימת רקע ליישור שני מסמכים באמצעות שירות Passim.
    
    Args:
        alignment_id: ID of TextAlignment object
        
    Returns:
        dict: Task results with statistics
    """
    try:
        # Get alignment object
        alignment = TextAlignment.objects.select_related(
            'document1', 'document2'
        ).get(id=alignment_id)
        
        # Create or get job tracking object
        job, created = AlignmentJob.objects.get_or_create(
            alignment=alignment,
            defaults={'task_id': self.request.id}
        )
        if not created:
            job.task_id = self.request.id
            job.save()
        
        logger.info(
            f"Starting alignment task {self.request.id} for "
            f"documents {alignment.document1.id} and {alignment.document2.id}"
        )
        
        # Update status
        alignment.status = 'processing'
        alignment.save(update_fields=['status'])
        
        job.started_at = timezone.now()
        job.progress = 0
        job.current_step = "Fetching document lines"
        job.save(update_fields=['started_at', 'progress', 'current_step'])
        
        # Step 1: Get all lines from both documents (10%)
        doc1_lines = list(
            LineTranscription.objects.filter(
                line__document_part__document=alignment.document1
            ).order_by('line__document_part__order', 'line__order')
            .values_list('id', 'content', flat=False)
        )
        
        doc2_lines = list(
            LineTranscription.objects.filter(
                line__document_part__document=alignment.document2
            ).order_by('line__document_part__order', 'line__order')
            .values_list('id', 'content', flat=False)
        )
        
        if not doc1_lines or not doc2_lines:
            raise ValueError("One or both documents have no transcriptions")
        
        job.progress = 10
        job.current_step = f"Processing {len(doc1_lines)} vs {len(doc2_lines)} lines"
        job.save(update_fields=['progress', 'current_step'])
        
        logger.info(
            f"Found {len(doc1_lines)} lines in doc1 and "
            f"{len(doc2_lines)} lines in doc2"
        )
        
        # Step 2: Prepare line data (20%)
        doc1_line_ids = [line_id for line_id, _ in doc1_lines]
        doc1_texts = [content for _, content in doc1_lines]
        
        doc2_line_ids = [line_id for line_id, _ in doc2_lines]
        doc2_texts = [content for _, content in doc2_lines]
        
        job.progress = 20
        job.current_step = "Calling Passim alignment service"
        job.save(update_fields=['progress', 'current_step'])
        
        # Step 3: Call Passim service (40%)
        with PassimWrapper(timeout=600) as wrapper:  # 10 min timeout for large docs
            result = wrapper.align_documents(
                doc1_lines=doc1_texts,
                doc2_lines=doc2_texts,
                method=alignment.method,
                threshold=alignment.similarity_threshold,
                min_length=alignment.min_length,
                doc1_id=str(alignment.document1.id),
                doc2_id=str(alignment.document2.id)
            )
        
        if not result:
            raise Exception("Passim alignment service returned no results")
        
        job.progress = 60
        job.current_step = f"Creating {len(result.pairs)} alignment pairs"
        job.save(update_fields=['progress', 'current_step'])
        
        logger.info(
            f"Passim returned {len(result.pairs)} pairs with "
            f"avg similarity {result.statistics['average_similarity']:.2%}"
        )
        
        # Step 4: Create AlignmentPair objects (30%)
        pairs_created = 0
        batch_size = 100
        alignment_pairs = []
        
        for pair in result.pairs:
            # Get corresponding LineTranscription IDs
            line1_id = doc1_line_ids[pair.index1]
            line2_id = doc2_line_ids[pair.index2]
            
            alignment_pairs.append(
                AlignmentPair(
                    alignment=alignment,
                    line1_id=line1_id,
                    line2_id=line2_id,
                    similarity=pair.similarity,
                    method_used=pair.method
                )
            )
            
            pairs_created += 1
            
            # Bulk create in batches
            if len(alignment_pairs) >= batch_size:
                with transaction.atomic():
                    AlignmentPair.objects.bulk_create(
                        alignment_pairs,
                        ignore_conflicts=True
                    )
                alignment_pairs = []
                
                # Update progress
                progress = 60 + int((pairs_created / len(result.pairs)) * 30)
                job.progress = min(progress, 90)
                job.save(update_fields=['progress'])
        
        # Create remaining pairs
        if alignment_pairs:
            with transaction.atomic():
                AlignmentPair.objects.bulk_create(
                    alignment_pairs,
                    ignore_conflicts=True
                )
        
        job.progress = 90
        job.current_step = "Calculating statistics"
        job.save(update_fields=['progress', 'current_step'])
        
        # Step 5: Update alignment statistics (10%)
        alignment.total_pairs = len(result.pairs)
        alignment.average_similarity = result.statistics['average_similarity']
        alignment.alignment_rate = result.statistics['alignment_rate']
        alignment.status = 'completed'
        alignment.completed_at = timezone.now()
        alignment.save()
        
        # Complete job
        job.progress = 100
        job.current_step = "Completed"
        job.completed_at = timezone.now()
        job.result_data = {
            'total_pairs': alignment.total_pairs,
            'average_similarity': alignment.average_similarity,
            'alignment_rate': alignment.alignment_rate,
            'parameters': result.parameters,
            'statistics': result.statistics
        }
        job.save()
        
        logger.info(
            f"Alignment task {self.request.id} completed successfully: "
            f"{alignment.total_pairs} pairs created"
        )
        
        return {
            'status': 'success',
            'alignment_id': alignment_id,
            'total_pairs': alignment.total_pairs,
            'average_similarity': alignment.average_similarity,
            'alignment_rate': alignment.alignment_rate
        }
        
    except TextAlignment.DoesNotExist:
        logger.error(f"TextAlignment {alignment_id} not found")
        return {
            'status': 'error',
            'error': 'Alignment object not found'
        }
        
    except Exception as e:
        logger.error(f"Alignment task failed: {str(e)}", exc_info=True)
        
        # Update alignment status
        try:
            alignment.status = 'failed'
            alignment.error_message = str(e)
            alignment.save(update_fields=['status', 'error_message'])
            
            if job:
                job.current_step = f"Failed: {str(e)}"
                job.completed_at = timezone.now()
                job.save(update_fields=['current_step', 'completed_at'])
        except:
            pass
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying alignment task (attempt {self.request.retries + 1})")
            raise self.retry(exc=e)
        
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def cleanup_old_alignments(days=30):
    """
    Clean up old failed/cancelled alignments.
    
    נקה יישורים ישנים שנכשלו או בוטלו.
    
    Args:
        days: Delete alignments older than this many days
    """
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Delete failed alignments
    deleted_failed = TextAlignment.objects.filter(
        status='failed',
        created_at__lt=cutoff_date
    ).delete()
    
    logger.info(f"Cleaned up {deleted_failed[0]} failed alignments older than {days} days")
    
    return {
        'deleted_failed': deleted_failed[0],
        'cutoff_date': cutoff_date.isoformat()
    }


@shared_task
def batch_align_documents(alignment_ids: list):
    """
    Process multiple alignments in sequence.
    
    עבד מספר יישורים ברצף.
    
    Args:
        alignment_ids: List of TextAlignment IDs to process
    """
    results = []
    
    for alignment_id in alignment_ids:
        logger.info(f"Starting batch alignment for ID {alignment_id}")
        result = align_documents_task.delay(alignment_id)
        results.append({
            'alignment_id': alignment_id,
            'task_id': result.id
        })
    
    return {
        'status': 'success',
        'total': len(alignment_ids),
        'tasks': results
    }
