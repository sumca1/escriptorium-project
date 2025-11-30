"""
CERberus Integration - Model Evaluation Views
תצוגות הערכת מודלים - שילוב CERberus

Character Error Rate (CER) evaluation tool integrated into BiblIA.
כלי הערכת שיעור שגיאות תווים (CER) משולב ב-BiblIA.
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
import logging
import re

logger = logging.getLogger(__name__)

# Import CERberus engine
try:
    from core.cerberus_engine import cer as calculate_cer
    CERBERUS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"CERberus module not available: {e}")
    CERBERUS_AVAILABLE = False



class CERberusDashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard for CERberus model evaluation.
    לוח מחוונים ראשי להערכת מודלים CERberus.
    """
    template_name = 'core/cerberus/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cerberus_available'] = CERBERUS_AVAILABLE
        
        # Get user's documents for testing
        from core.models import Document
        user_documents = Document.objects.filter(
            owner=self.request.user
        ).distinct().order_by('-updated_at')[:20]
        
        context['user_documents'] = user_documents
        
        return context


class CERCalculationView(LoginRequiredMixin, View):
    """
    API endpoint to calculate CER between reference and hypothesis texts.
    נקודת קצה API לחישוב CER בין טקסט יעד והשערה.
    """
    
    def post(self, request, *args, **kwargs):
        if not CERBERUS_AVAILABLE:
            return JsonResponse({
                'success': False,
                'error': 'CERberus module is not available'
            }, status=503)
        
        try:
            import json
            data = json.loads(request.body)
            
            reference = data.get('reference', '')
            hypothesis = data.get('hypothesis', '')
            
            if not reference or not hypothesis:
                return JsonResponse({
                    'success': False,
                    'error': 'Both reference and hypothesis texts are required'
                }, status=400)
            
            # Get options
            options = {
                'ignore_punctuation': data.get('ignore_punctuation', False),
                'ignore_case': data.get('ignore_case', False),
                'ignore_whitespace': data.get('ignore_whitespace', False),
                'ignore_numbers': data.get('ignore_numbers', False),
                'ignore_newlines_and_returns': data.get('ignore_newlines', False),
                'ignore_chars': data.get('ignore_chars', None),
                'discard_lines_with_chars': data.get('discard_chars', None),
                'debug': False,
                'return_char_stats': True
            }
            
            # Calculate CER
            result = calculate_cer(reference, hypothesis, **options)
            
            # Format character statistics for JSON
            if 'char_stats' in result and result['char_stats'] is not None:
                # Convert DataFrame to dict if needed
                if hasattr(result['char_stats'], 'to_dict'):
                    char_stats = result['char_stats'].to_dict('records')
                else:
                    char_stats = result['char_stats']
                result['char_stats'] = char_stats
            
            # Format block statistics
            if 'block_stats' in result and result['block_stats'] is not None:
                if hasattr(result['block_stats'], 'to_dict'):
                    block_stats = result['block_stats'].to_dict('records')
                else:
                    block_stats = result['block_stats']
                result['block_stats'] = block_stats
            
            return JsonResponse({
                'success': True,
                'result': result
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)
        except Exception as e:
            logger.error(f"CER calculation error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class DocumentCERView(LoginRequiredMixin, View):
    """
    API endpoint to calculate CER for a specific document.
    נקודת קצה API לחישוב CER עבור מסמך ספציפי.
    """
    
    def post(self, request, *args, **kwargs):
        if not CERBERUS_AVAILABLE:
            return JsonResponse({
                'success': False,
                'error': 'CERberus module is not available'
            }, status=503)
        
        try:
            import json
            from core.models import Document, LineTranscription
            
            data = json.loads(request.body)
            
            doc_id = data.get('document_id')
            reference_transcription_id = data.get('reference_transcription')
            hypothesis_transcription_id = data.get('hypothesis_transcription')
            
            if not doc_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Document ID is required'
                }, status=400)
            
            # Get document and verify permissions
            try:
                doc = Document.objects.get(pk=doc_id)
            except Document.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Document not found'
                }, status=404)
            
            # Check permissions
            if not (doc.owner == request.user or request.user in doc.shared_with_users.all()):
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied'
                }, status=403)
            
            # Get transcriptions
            reference_lines = []
            hypothesis_lines = []
            
            # Get all parts in order
            parts = doc.parts.all().order_by('order')
            
            for part in parts:
                # Get transcriptions for this part
                if reference_transcription_id and hypothesis_transcription_id:
                    ref_trans = LineTranscription.objects.filter(
                        line__document_part=part,
                        transcription_id=reference_transcription_id
                    ).order_by('line__order')
                    
                    hyp_trans = LineTranscription.objects.filter(
                        line__document_part=part,
                        transcription_id=hypothesis_transcription_id
                    ).order_by('line__order')
                    
                    for ref in ref_trans:
                        reference_lines.append(ref.content or '')
                    
                    for hyp in hyp_trans:
                        hypothesis_lines.append(hyp.content or '')
            
            if not reference_lines or not hypothesis_lines:
                return JsonResponse({
                    'success': False,
                    'error': 'No transcriptions found for the selected document'
                }, status=400)
            
            # Join lines
            reference = '\n'.join(reference_lines)
            hypothesis = '\n'.join(hypothesis_lines)
            
            # Get options
            options = {
                'ignore_punctuation': data.get('ignore_punctuation', False),
                'ignore_case': data.get('ignore_case', False),
                'ignore_whitespace': data.get('ignore_whitespace', False),
                'ignore_numbers': data.get('ignore_numbers', False),
                'ignore_newlines_and_returns': data.get('ignore_newlines', False),
                'debug': False,
                'return_char_stats': True
            }
            
            # Calculate CER
            result = calculate_cer(reference, hypothesis, **options)
            
            # Format for JSON
            if 'char_stats' in result and result['char_stats'] is not None:
                if hasattr(result['char_stats'], 'to_dict'):
                    result['char_stats'] = result['char_stats'].to_dict('records')
            
            if 'block_stats' in result and result['block_stats'] is not None:
                if hasattr(result['block_stats'], 'to_dict'):
                    result['block_stats'] = result['block_stats'].to_dict('records')
            
            return JsonResponse({
                'success': True,
                'result': result,
                'document_name': doc.name
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)
        except Exception as e:
            logger.error(f"Document CER calculation error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
