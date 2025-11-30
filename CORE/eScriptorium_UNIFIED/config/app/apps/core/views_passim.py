"""
Passim Text Alignment Views
תצוגות יישור טקסט Passim

Provides UI and API endpoints for text alignment using Passim service.
מספק ממשק משתמש וממשקי API ליישור טקסט באמצעות שירות Passim.
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.db.models import Q
import logging

from core.models import Document, DocumentPart, LineTranscription
from core.passim_wrapper import PassimWrapper, is_service_available

logger = logging.getLogger(__name__)


class PassimDashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard for Passim text alignment.
    לוח מחוונים ראשי ליישור טקסט Passim.
    """
    template_name = 'core/passim/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check Passim service availability
        is_available = is_service_available()
        context['passim_available'] = is_available
        
        if is_available:
            with PassimWrapper() as wrapper:
                is_healthy, health_data = wrapper.check_health()
                context['passim_healthy'] = is_healthy
                context['passim_health'] = health_data
        else:
            context['passim_healthy'] = False
            context['passim_health'] = {'error': 'Service unavailable'}
        
        # Get user's documents for selection
        user_documents = Document.objects.filter(
            Q(owner=self.request.user) | Q(shared_with_users=self.request.user)
        ).distinct().order_by('-updated_at')[:50]
        
        context['user_documents'] = user_documents
        
        return context


class PassimHealthCheckView(LoginRequiredMixin, View):
    """
    API endpoint to check Passim service health.
    נקודת קצה API לבדיקת תקינות שירות Passim.
    """
    
    def get(self, request, *args, **kwargs):
        try:
            with PassimWrapper() as wrapper:
                is_healthy, health_data = wrapper.check_health()
                
                return JsonResponse({
                    'available': True,
                    'healthy': is_healthy,
                    'data': health_data
                })
        except Exception as e:
            logger.error(f"Passim health check failed: {e}")
            return JsonResponse({
                'available': False,
                'healthy': False,
                'error': str(e)
            }, status=503)


class PassimAlignDocumentsView(LoginRequiredMixin, View):
    """
    API endpoint to align two documents.
    נקודת קצה API ליישור שני מסמכים.
    """
    
    def post(self, request, *args, **kwargs):
        try:
            import json
            data = json.loads(request.body)
            
            doc1_id = data.get('doc1_id')
            doc2_id = data.get('doc2_id')
            method = data.get('method', 'auto')
            threshold = float(data.get('threshold', 0.7))
            min_length = int(data.get('min_length', 10))
            
            if not doc1_id or not doc2_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Both document IDs are required'
                }, status=400)
            
            # Get documents and verify permissions
            try:
                doc1 = Document.objects.get(pk=doc1_id)
                doc2 = Document.objects.get(pk=doc2_id)
            except Document.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Document not found'
                }, status=404)
            
            # Check permissions
            if not (doc1.owner == request.user or request.user in doc1.shared_with_users.all()):
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied for document 1'
                }, status=403)
            
            if not (doc2.owner == request.user or request.user in doc2.shared_with_users.all()):
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied for document 2'
                }, status=403)
            
            # Get transcriptions from both documents
            doc1_lines = self._get_document_lines(doc1)
            doc2_lines = self._get_document_lines(doc2)
            
            if not doc1_lines or not doc2_lines:
                return JsonResponse({
                    'success': False,
                    'error': 'One or both documents have no transcriptions'
                }, status=400)
            
            # Perform alignment
            with PassimWrapper() as wrapper:
                result = wrapper.align_documents(
                    doc1_lines=doc1_lines,
                    doc2_lines=doc2_lines,
                    method=method,
                    threshold=threshold,
                    min_length=min_length,
                    doc1_id=str(doc1_id),
                    doc2_id=str(doc2_id)
                )
            
            if result is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Alignment failed'
                }, status=500)
            
            # Convert result to JSON-serializable format
            pairs_data = [
                {
                    'text1': pair.text1,
                    'text2': pair.text2,
                    'index1': pair.index1,
                    'index2': pair.index2,
                    'similarity': pair.similarity,
                    'method': pair.method,
                    'metadata': pair.metadata or {}
                }
                for pair in result.pairs
            ]
            
            return JsonResponse({
                'success': True,
                'result': {
                    'doc1_id': result.doc1_id,
                    'doc2_id': result.doc2_id,
                    'pairs': pairs_data,
                    'statistics': result.statistics,
                    'parameters': result.parameters,
                    'timestamp': result.timestamp.isoformat() if result.timestamp else None
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)
        except Exception as e:
            logger.error(f"Alignment error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def _get_document_lines(self, document):
        """Get all transcription lines from a document."""
        lines = []
        
        # Get all parts
        parts = document.parts.all().order_by('order')
        
        for part in parts:
            # Get all transcriptions for this part
            transcriptions = LineTranscription.objects.filter(
                line__document_part=part
            ).exclude(
                content__isnull=True
            ).exclude(
                content=''
            ).order_by('line__order')
            
            for trans in transcriptions:
                lines.append(trans.content)
        
        return lines


class PassimCompareTextsView(LoginRequiredMixin, View):
    """
    API endpoint to compare two text strings.
    נקודת קצה API להשוואת שני מחרוזות טקסט.
    """
    
    def post(self, request, *args, **kwargs):
        try:
            import json
            data = json.loads(request.body)
            
            text1 = data.get('text1', '')
            text2 = data.get('text2', '')
            method = data.get('method', 'auto')
            
            if not text1 or not text2:
                return JsonResponse({
                    'success': False,
                    'error': 'Both texts are required'
                }, status=400)
            
            # Compare texts
            with PassimWrapper() as wrapper:
                similarity = wrapper.compare_texts(text1, text2, method)
            
            if similarity is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Comparison failed'
                }, status=500)
            
            return JsonResponse({
                'success': True,
                'similarity': similarity,
                'method': method
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)
        except Exception as e:
            logger.error(f"Comparison error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
