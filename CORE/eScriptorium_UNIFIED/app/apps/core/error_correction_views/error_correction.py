#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Error Detection and Correction Views
API endpoints for spell checking, error detection, and auto-correction
"""

import logging
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from core.models import Transcription, LineTranscription

# Try importing old services (optional - may not be available)
try:
    from core.services import (
        MultilingualSpellChecker,
        OCRErrorDetector,
        AutoCorrector
    )
except ImportError:
    # Old services not available - these views won't work but won't break the app
    MultilingualSpellChecker = None
    OCRErrorDetector = None
    AutoCorrector = None

logger = logging.getLogger(__name__)


class SpellCheckView(LoginRequiredMixin, View):
    """
    API endpoint for spell checking transcriptions
    
    POST /api/spell-check/<transcription_id>/
    {
        "language": "hebrew",  // optional: auto-detect if not provided
        "lines": [1, 2, 3]  // optional: specific line IDs, or all if not provided
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spell_checker = MultilingualSpellChecker() if MultilingualSpellChecker else None
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, transcription_id):
        """Check spelling for transcription"""
        try:
            # Get transcription
            transcription = Transcription.objects.get(pk=transcription_id)
            
            # Check permissions
            if not request.user.has_perm('core.view_transcription', transcription):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Parse request data
            import json
            data = json.loads(request.body) if request.body else {}
            language = data.get('language')
            line_ids = data.get('lines')
            
            # Get lines
            if line_ids:
                lines = LineTranscription.objects.filter(
                    transcription=transcription,
                    pk__in=line_ids
                )
            else:
                lines = transcription.linetranscription_set.all()
            
            # Check each line
            results = []
            total_errors = 0
            
            for line in lines:
                content = line.content or ''
                
                if not content.strip():
                    continue
                
                # Run spell check
                check_result = self.spell_checker.check_text(content, language)
                
                errors = check_result.get('errors', [])
                if isinstance(errors, dict):
                    # Mixed language - flatten errors
                    all_errors = []
                    for lang_errors in errors.values():
                        all_errors.extend(lang_errors)
                    errors = all_errors
                
                if errors:
                    total_errors += len(errors)
                    results.append({
                        'line_id': line.pk,
                        'line_order': line.line.order if line.line else None,
                        'content': content,
                        'errors': errors,
                        'error_count': len(errors),
                        'detected_language': check_result.get('detected_language')
                    })
            
            return JsonResponse({
                'success': True,
                'transcription_id': transcription_id,
                'total_lines_checked': lines.count(),
                'lines_with_errors': len(results),
                'total_errors': total_errors,
                'results': results
            })
            
        except Transcription.DoesNotExist:
            return JsonResponse({'error': 'Transcription not found'}, status=404)
        except Exception as e:
            logger.error(f"Spell check error: {e}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


class ErrorDetectionView(LoginRequiredMixin, View):
    """
    API endpoint for OCR error detection
    
    POST /api/error-detection/<transcription_id>/
    {
        "confidence_threshold": 0.7,  // optional
        "include_report": true  // optional: include summary report
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.error_detector = None
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, transcription_id):
        """Detect errors in transcription"""
        try:
            # Get transcription
            transcription = Transcription.objects.get(pk=transcription_id)
            
            # Check permissions
            if not request.user.has_perm('core.view_transcription', transcription):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Parse request
            import json
            data = json.loads(request.body) if request.body else {}
            confidence_threshold = data.get('confidence_threshold', 0.7)
            include_report = data.get('include_report', True)
            
            # Initialize detector
            self.error_detector = OCRErrorDetector(confidence_threshold=confidence_threshold) if OCRErrorDetector else None
            if not self.error_detector:
                return JsonResponse({'error': 'Error detector not available'}, status=501)
            
            # Prepare transcription data
            lines = transcription.linetranscription_set.all()
            transcription_data = {
                'lines': [
                    {
                        'content': line.content or '',
                        'avg_confidence': line.avg_confidence,
                        'graphs': line.graphs or []
                    }
                    for line in lines
                ]
            }
            
            # Detect errors
            errors = self.error_detector.detect_errors(transcription_data)
            
            response_data = {
                'success': True,
                'transcription_id': transcription_id,
                'errors': errors,
                'total_errors': len(errors)
            }
            
            # Add report if requested
            if include_report:
                report = self.error_detector.generate_error_report(errors)
                response_data['report'] = report
            
            return JsonResponse(response_data)
            
        except Transcription.DoesNotExist:
            return JsonResponse({'error': 'Transcription not found'}, status=404)
        except Exception as e:
            logger.error(f"Error detection failed: {e}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


class AutoCorrectionView(LoginRequiredMixin, View):
    """
    API endpoint for auto-correction
    
    POST /api/auto-correct/<transcription_id>/
    {
        "mode": "safe",  // "safe", "review", or "aggressive"
        "confidence_threshold": 0.9,  // for safe mode
        "apply_corrections": false  // if true, save to database
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auto_corrector = AutoCorrector() if AutoCorrector else None
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, transcription_id):
        """Auto-correct transcription"""
        try:
            # Get transcription
            transcription = Transcription.objects.get(pk=transcription_id)
            
            # Check permissions
            if not request.user.has_perm('core.change_transcription', transcription):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Parse request
            import json
            data = json.loads(request.body) if request.body else {}
            mode = data.get('mode', 'safe')
            confidence_threshold = data.get('confidence_threshold', 0.9)
            apply_corrections = data.get('apply_corrections', False)
            
            # Prepare transcription data
            lines = transcription.linetranscription_set.all().order_by('line__order')
            transcription_data = {
                'lines': [
                    {
                        'id': line.pk,
                        'content': line.content or '',
                        'avg_confidence': line.avg_confidence,
                        'graphs': line.graphs or []
                    }
                    for line in lines
                ]
            }
            
            # Run auto-correction
            result = self.auto_corrector.correct_transcription(
                transcription_data,
                mode=mode,
                confidence_threshold=confidence_threshold
            )
            
            # Apply corrections to database if requested
            if apply_corrections and result['corrections_made']:
                for corrected_line in result['corrected_lines']:
                    if corrected_line.get('was_corrected'):
                        line_id = corrected_line.get('id')
                        new_content = corrected_line.get('content')
                        
                        line = LineTranscription.objects.get(pk=line_id)
                        line.content = new_content
                        line.save()
                
                result['applied_to_database'] = True
            else:
                result['applied_to_database'] = False
            
            return JsonResponse({
                'success': True,
                'transcription_id': transcription_id,
                **result
            })
            
        except Transcription.DoesNotExist:
            return JsonResponse({'error': 'Transcription not found'}, status=404)
        except Exception as e:
            logger.error(f"Auto-correction failed: {e}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


class SuggestCorrectionModeView(LoginRequiredMixin, View):
    """
    API endpoint to suggest best correction mode based on transcription quality
    
    GET /api/suggest-mode/<transcription_id>/
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auto_corrector = AutoCorrector() if AutoCorrector else None
    
    def get(self, request, transcription_id):
        """Suggest best correction mode"""
        try:
            # Get transcription
            transcription = Transcription.objects.get(pk=transcription_id)
            
            # Check permissions
            if not request.user.has_perm('core.view_transcription', transcription):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Prepare data
            lines = transcription.linetranscription_set.all()
            transcription_data = {
                'lines': [
                    {
                        'content': line.content or '',
                        'avg_confidence': line.avg_confidence,
                        'graphs': line.graphs or []
                    }
                    for line in lines
                ]
            }
            
            # Get suggestion
            suggested_mode = self.auto_corrector.suggest_best_mode(transcription_data)
            
            # Get explanation
            explanations = {
                'safe': 'High quality OCR - safe to auto-correct with high confidence',
                'review': 'Medium quality or complex errors - manual review recommended',
                'aggressive': 'Use with caution - applies all suggestions automatically'
            }
            
            return JsonResponse({
                'success': True,
                'transcription_id': transcription_id,
                'suggested_mode': suggested_mode,
                'explanation': explanations.get(suggested_mode, ''),
                'avg_confidence': transcription.avg_confidence
            })
            
        except Transcription.DoesNotExist:
            return JsonResponse({'error': 'Transcription not found'}, status=404)
        except Exception as e:
            logger.error(f"Mode suggestion failed: {e}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
