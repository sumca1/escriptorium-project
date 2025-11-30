"""
Text Alignment API Views - BiblIA Enhancement Feature #4
Created: 2025-10-20
Purpose: REST API endpoints for text alignment using Passim service

תצוגות API ליישור טקסט - שיפור BiblIA תכונה #4
מטרה: endpoints של REST API ליישור טקסט באמצעות שירות Passim
"""

import logging
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Q
from django.core.paginator import Paginator

from core.models import (
    TextAlignment,
    AlignmentPair,
    AlignmentJob,
    Document,
    LineTranscription
)
from core.alignment_tasks import align_documents_task

logger = logging.getLogger(__name__)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_alignment(request):
    """
    Create new text alignment between two documents.
    
    צור יישור טקסט חדש בין שני מסמכים.
    
    POST /api/alignments/create/
    
    Request body:
        {
            "document1_id": 123,
            "document2_id": 456,
            "method": "auto",  // auto, sequence, levenshtein, jaccard
            "threshold": 0.7,  // 0.0-1.0
            "min_length": 10   // minimum characters
        }
    
    Returns:
        {
            "alignment_id": 789,
            "status": "pending",
            "task_id": "abc-123-def-456",
            "message": "Alignment task started"
        }
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        doc1_id = data.get('document1_id')
        doc2_id = data.get('document2_id')
        
        if not doc1_id or not doc2_id:
            return JsonResponse({
                'error': 'Both document1_id and document2_id are required'
            }, status=400)
        
        if doc1_id == doc2_id:
            return JsonResponse({
                'error': 'Cannot align a document with itself'
            }, status=400)
        
        # Get documents
        doc1 = get_object_or_404(Document, id=doc1_id)
        doc2 = get_object_or_404(Document, id=doc2_id)
        
        # Check permissions
        if not (request.user.has_perm('core.view_document', doc1) and
                request.user.has_perm('core.view_document', doc2)):
            return JsonResponse({
                'error': 'Permission denied'
            }, status=403)
        
        # Get parameters with defaults
        method = data.get('method', 'auto')
        threshold = float(data.get('threshold', 0.7))
        min_length = int(data.get('min_length', 10))
        
        # Validate parameters
        if method not in ['auto', 'sequence', 'levenshtein', 'jaccard']:
            return JsonResponse({
                'error': f'Invalid method: {method}'
            }, status=400)
        
        if not 0.0 <= threshold <= 1.0:
            return JsonResponse({
                'error': 'Threshold must be between 0.0 and 1.0'
            }, status=400)
        
        # Check if alignment already exists
        existing = TextAlignment.objects.filter(
            document1=doc1,
            document2=doc2,
            status__in=['pending', 'processing', 'completed']
        ).first()
        
        if existing:
            job = AlignmentJob.objects.filter(alignment=existing).first()
            return JsonResponse({
                'alignment_id': existing.id,
                'status': existing.status,
                'task_id': job.task_id if job else None,
                'message': 'Alignment already exists',
                'progress': job.progress if job else 0
            })
        
        # Create new alignment
        alignment = TextAlignment.objects.create(
            document1=doc1,
            document2=doc2,
            method=method,
            similarity_threshold=threshold,
            min_length=min_length,
            created_by=request.user,
            status='pending'
        )
        
        # Start background task
        task = align_documents_task.delay(alignment.id)
        
        logger.info(
            f"User {request.user.username} started alignment {alignment.id} "
            f"between documents {doc1_id} and {doc2_id}"
        )
        
        return JsonResponse({
            'alignment_id': alignment.id,
            'status': 'pending',
            'task_id': task.id,
            'message': 'Alignment task started successfully'
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error creating alignment: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(["GET"])
def get_alignment_status(request, alignment_id):
    """
    Get alignment status and statistics.
    
    קבל סטטוס ונתונים סטטיסטיים של יישור.
    
    GET /api/alignments/<alignment_id>/
    
    Returns:
        {
            "id": 789,
            "document1": {"id": 123, "name": "Doc 1"},
            "document2": {"id": 456, "name": "Doc 2"},
            "status": "completed",
            "progress": 100,
            "current_step": "Completed",
            "method": "auto",
            "threshold": 0.7,
            "min_length": 10,
            "total_pairs": 150,
            "average_similarity": 0.85,
            "alignment_rate": 0.92,
            "created_at": "2025-10-20T12:00:00Z",
            "completed_at": "2025-10-20T12:05:00Z"
        }
    """
    try:
        alignment = get_object_or_404(
            TextAlignment.objects.select_related(
                'document1', 'document2', 'created_by'
            ),
            id=alignment_id
        )
        
        # Check permissions
        if not request.user.has_perm('core.view_document', alignment.document1):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get job info
        job = AlignmentJob.objects.filter(alignment=alignment).first()
        
        response_data = {
            'id': alignment.id,
            'document1': {
                'id': alignment.document1.id,
                'name': alignment.document1.name
            },
            'document2': {
                'id': alignment.document2.id,
                'name': alignment.document2.name
            },
            'status': alignment.status,
            'method': alignment.method,
            'threshold': alignment.similarity_threshold,
            'min_length': alignment.min_length,
            'total_pairs': alignment.total_pairs,
            'average_similarity': alignment.average_similarity,
            'alignment_rate': alignment.alignment_rate,
            'created_at': alignment.created_at.isoformat(),
            'created_by': alignment.created_by.username if alignment.created_by else None,
            'completed_at': alignment.completed_at.isoformat() if alignment.completed_at else None,
        }
        
        if job:
            response_data.update({
                'progress': job.progress,
                'current_step': job.current_step,
                'task_id': job.task_id,
                'started_at': job.started_at.isoformat() if job.started_at else None,
            })
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error getting alignment status: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(["GET"])
def get_alignment_pairs(request, alignment_id):
    """
    Get list of alignment pairs with pagination.
    
    קבל רשימת זוגות יישור עם דפדוף.
    
    GET /api/alignments/<alignment_id>/pairs/?page=1&per_page=50&min_similarity=0.8
    
    Query parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50, max: 200)
        - min_similarity: Filter by minimum similarity (0.0-1.0)
        - verified_only: Show only verified pairs (true/false)
    
    Returns:
        {
            "alignment_id": 789,
            "total": 150,
            "page": 1,
            "per_page": 50,
            "total_pages": 3,
            "pairs": [
                {
                    "id": 1001,
                    "line1": {
                        "id": 5001,
                        "text": "בראשית ברא אלהים"
                    },
                    "line2": {
                        "id": 6001,
                        "text": "בראשית ברא אלוהים"
                    },
                    "similarity": 0.95,
                    "method": "levenshtein",
                    "is_verified": false,
                    "is_rejected": false
                }
            ]
        }
    """
    try:
        alignment = get_object_or_404(TextAlignment, id=alignment_id)
        
        # Check permissions
        if not request.user.has_perm('core.view_document', alignment.document1):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get query parameters
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 200)
        min_similarity = float(request.GET.get('min_similarity', 0.0))
        verified_only = request.GET.get('verified_only', '').lower() == 'true'
        
        # Build query
        pairs_query = AlignmentPair.objects.filter(
            alignment=alignment
        ).select_related('line1', 'line2')
        
        if min_similarity > 0:
            pairs_query = pairs_query.filter(similarity__gte=min_similarity)
        
        if verified_only:
            pairs_query = pairs_query.filter(is_verified=True)
        
        # Order by similarity (highest first)
        pairs_query = pairs_query.order_by('-similarity')
        
        # Paginate
        paginator = Paginator(pairs_query, per_page)
        pairs_page = paginator.get_page(page)
        
        # Format response
        pairs_data = []
        for pair in pairs_page:
            pairs_data.append({
                'id': pair.id,
                'line1': {
                    'id': pair.line1.id,
                    'text': pair.line1.content
                },
                'line2': {
                    'id': pair.line2.id,
                    'text': pair.line2.content
                },
                'similarity': pair.similarity,
                'method': pair.method_used,
                'is_verified': pair.is_verified,
                'is_rejected': pair.is_rejected,
                'verified_at': pair.verified_at.isoformat() if pair.verified_at else None,
                'verified_by': pair.verified_by.username if pair.verified_by else None
            })
        
        return JsonResponse({
            'alignment_id': alignment_id,
            'total': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'pairs': pairs_data
        })
        
    except ValueError:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    except Exception as e:
        logger.error(f"Error getting alignment pairs: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def verify_alignment_pair(request, pair_id):
    """
    Verify or reject an alignment pair.
    
    אשר או דחה זוג יישור.
    
    POST /api/alignments/pairs/<pair_id>/verify/
    
    Request body:
        {
            "action": "verify" | "reject" | "reset"
        }
    
    Returns:
        {
            "pair_id": 1001,
            "action": "verify",
            "is_verified": true,
            "is_rejected": false,
            "verified_by": "username",
            "verified_at": "2025-10-20T12:00:00Z"
        }
    """
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if action not in ['verify', 'reject', 'reset']:
            return JsonResponse({
                'error': 'Invalid action. Must be verify, reject, or reset'
            }, status=400)
        
        pair = get_object_or_404(
            AlignmentPair.objects.select_related('alignment'),
            id=pair_id
        )
        
        # Check permissions
        if not request.user.has_perm('core.change_document', pair.alignment.document1):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Update pair
        if action == 'verify':
            pair.is_verified = True
            pair.is_rejected = False
            pair.verified_by = request.user
            pair.save()
        elif action == 'reject':
            pair.is_verified = False
            pair.is_rejected = True
            pair.verified_by = request.user
            pair.save()
        elif action == 'reset':
            pair.is_verified = False
            pair.is_rejected = False
            pair.verified_by = None
            pair.verified_at = None
            pair.save()
        
        logger.info(
            f"User {request.user.username} performed {action} on "
            f"alignment pair {pair_id}"
        )
        
        return JsonResponse({
            'pair_id': pair.id,
            'action': action,
            'is_verified': pair.is_verified,
            'is_rejected': pair.is_rejected,
            'verified_by': pair.verified_by.username if pair.verified_by else None,
            'verified_at': pair.verified_at.isoformat() if pair.verified_at else None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error verifying pair: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(["GET"])
def export_alignment(request, alignment_id):
    """
    Export alignment results in various formats.
    
    ייצא תוצאות יישור בפורמטים שונים.
    
    GET /api/alignments/<alignment_id>/export/?format=json|csv
    
    Query parameters:
        - format: Export format (json, csv)
        - verified_only: Export only verified pairs (true/false)
    
    Returns:
        File download with alignment data
    """
    try:
        alignment = get_object_or_404(
            TextAlignment.objects.select_related('document1', 'document2'),
            id=alignment_id
        )
        
        # Check permissions
        if not request.user.has_perm('core.view_document', alignment.document1):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        export_format = request.GET.get('format', 'json').lower()
        verified_only = request.GET.get('verified_only', '').lower() == 'true'
        
        # Get pairs
        pairs_query = AlignmentPair.objects.filter(
            alignment=alignment
        ).select_related('line1', 'line2').order_by('id')
        
        if verified_only:
            pairs_query = pairs_query.filter(is_verified=True)
        
        if export_format == 'csv':
            # CSV export
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'Pair ID', 'Line 1 ID', 'Text 1', 'Line 2 ID', 'Text 2',
                'Similarity', 'Method', 'Verified', 'Rejected'
            ])
            
            # Data
            for pair in pairs_query:
                writer.writerow([
                    pair.id,
                    pair.line1.id,
                    pair.line1.content,
                    pair.line2.id,
                    pair.line2.content,
                    pair.similarity,
                    pair.method_used,
                    pair.is_verified,
                    pair.is_rejected
                ])
            
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = (
                f'attachment; filename="alignment_{alignment_id}.csv"'
            )
            return response
            
        else:  # JSON export (default)
            pairs_data = []
            for pair in pairs_query:
                pairs_data.append({
                    'pair_id': pair.id,
                    'line1': {
                        'id': pair.line1.id,
                        'text': pair.line1.content
                    },
                    'line2': {
                        'id': pair.line2.id,
                        'text': pair.line2.content
                    },
                    'similarity': pair.similarity,
                    'method': pair.method_used,
                    'is_verified': pair.is_verified,
                    'is_rejected': pair.is_rejected
                })
            
            export_data = {
                'alignment_id': alignment.id,
                'document1': {
                    'id': alignment.document1.id,
                    'name': alignment.document1.name
                },
                'document2': {
                    'id': alignment.document2.id,
                    'name': alignment.document2.name
                },
                'method': alignment.method,
                'threshold': alignment.similarity_threshold,
                'statistics': {
                    'total_pairs': alignment.total_pairs,
                    'average_similarity': alignment.average_similarity,
                    'alignment_rate': alignment.alignment_rate
                },
                'created_at': alignment.created_at.isoformat(),
                'completed_at': alignment.completed_at.isoformat() if alignment.completed_at else None,
                'pairs': pairs_data
            }
            
            response = JsonResponse(export_data, json_dumps_params={'indent': 2})
            response['Content-Disposition'] = (
                f'attachment; filename="alignment_{alignment_id}.json"'
            )
            return response
        
    except Exception as e:
        logger.error(f"Error exporting alignment: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(["GET"])
def list_alignments(request):
    """
    List all alignments for current user's documents.
    
    הצג רשימת כל היישורים עבור מסמכי המשתמש הנוכחי.
    
    GET /api/alignments/?status=completed&page=1&per_page=20
    
    Query parameters:
        - status: Filter by status (pending, processing, completed, failed)
        - document_id: Filter by document ID
        - page: Page number
        - per_page: Items per page
    
    Returns:
        {
            "total": 50,
            "page": 1,
            "per_page": 20,
            "alignments": [...]
        }
    """
    try:
        # Get user's documents
        user_docs = Document.objects.filter(
            Q(project__owner=request.user) | Q(project__users=request.user)
        ).distinct()
        
        # Build query
        alignments = TextAlignment.objects.filter(
            Q(document1__in=user_docs) | Q(document2__in=user_docs)
        ).select_related('document1', 'document2', 'created_by').distinct()
        
        # Filters
        status = request.GET.get('status')
        if status:
            alignments = alignments.filter(status=status)
        
        document_id = request.GET.get('document_id')
        if document_id:
            alignments = alignments.filter(
                Q(document1_id=document_id) | Q(document2_id=document_id)
            )
        
        # Order by most recent
        alignments = alignments.order_by('-created_at')
        
        # Paginate
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 20)), 100)
        paginator = Paginator(alignments, per_page)
        alignments_page = paginator.get_page(page)
        
        # Format response
        alignments_data = []
        for alignment in alignments_page:
            alignments_data.append({
                'id': alignment.id,
                'document1': {
                    'id': alignment.document1.id,
                    'name': alignment.document1.name
                },
                'document2': {
                    'id': alignment.document2.id,
                    'name': alignment.document2.name
                },
                'status': alignment.status,
                'total_pairs': alignment.total_pairs,
                'average_similarity': alignment.average_similarity,
                'created_at': alignment.created_at.isoformat(),
                'completed_at': alignment.completed_at.isoformat() if alignment.completed_at else None
            })
        
        return JsonResponse({
            'total': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'alignments': alignments_data
        })
        
    except ValueError:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    except Exception as e:
        logger.error(f"Error listing alignments: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)
