# Engine Comparison Module for BiblIA eScriptorium
# Compares Kraken vs Tesseract OCR results
# Created: 20 October 2025
# Enhanced: 3 November 2025 - CERAnalyzer Integration

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q
from difflib import SequenceMatcher
import json
from collections import defaultdict

# Try importing Levenshtein, fall back to SequenceMatcher if not available
try:
    import Levenshtein
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False
    print("Warning: Levenshtein module not available, using SequenceMatcher for similarity")

# Import CERAnalyzer for advanced CER calculation
try:
    from cerberus_integration.analyzer import CERAnalyzer, UNICODE_RANGES_HEBREW_ARABIC
    from cerberus_integration.diff_engine import CharacterDiffEngine
    CERBERUS_AVAILABLE = True
except ImportError:
    CERBERUS_AVAILABLE = False
    print("Warning: CERberus not available, using basic Levenshtein distance")

from core.models import Document, DocumentPart, Transcription, LineTranscription


class TranscriptionSelectorView(LoginRequiredMixin, TemplateView):
    """
    Selector view for choosing transcriptions to compare
    Displays Kraken and Tesseract transcriptions separately
    """
    template_name = 'core/comparison/selector.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all transcriptions for current user
        user_docs = Document.objects.filter(
            Q(owner=self.request.user) | Q(shared_with_users=self.request.user)
        )
        
        # Get transcriptions by engine (via LineTranscription.version_source)
        kraken_trans = Transcription.objects.filter(
            document__in=user_docs,
            linetranscription__version_source__startswith='kraken:'
        ).distinct().select_related('document').order_by('-created_at')
        
        tesseract_trans = Transcription.objects.filter(
            document__in=user_docs,
            linetranscription__version_source__startswith='tesseract:'
        ).distinct().select_related('document').order_by('-created_at')
        
        context['kraken_transcriptions'] = kraken_trans
        context['tesseract_transcriptions'] = tesseract_trans
        context['transcriptions'] = kraken_trans.exists() and tesseract_trans.exists()
        
        return context


def calculate_levenshtein_distance(str1, str2):
    """
    Calculate Levenshtein distance with fallback to SequenceMatcher
    """
    if LEVENSHTEIN_AVAILABLE:
        return Levenshtein.distance(str1, str2)
    else:
        # Fallback: use SequenceMatcher to approximate Levenshtein distance
        matcher = SequenceMatcher(None, str1, str2)
        ratio = matcher.ratio()
        max_len = max(len(str1), len(str2))
        # Convert similarity ratio to distance approximation
        return int((1 - ratio) * max_len)


def calculate_advanced_cer(reference: str, hypothesis: str, detailed: bool = False):
    """
    Calculate CER using CERAnalyzer with advanced statistics.
    Falls back to basic Levenshtein if CERberus not available.
    
    Args:
        reference: Ground truth text
        hypothesis: OCR output text
        detailed: If True, include character-level statistics
        
    Returns:
        Dict with CER, error breakdown, and optional detailed statistics
    """
    if CERBERUS_AVAILABLE:
        analyzer = CERAnalyzer()
        try:
            results = analyzer.calculate_cer(
                reference=reference,
                hypothesis=hypothesis,
                ignore_case=False,
                ignore_whitespace=False,
                unicode_ranges=UNICODE_RANGES_HEBREW_ARABIC if detailed else None
            )
            
            # Format results for API response
            formatted = {
                'cer': results['cer'],
                'wer': calculate_wer(reference, hypothesis),  # Add WER
                'num_correct': results['num_correct'],
                'num_substitutions': results['num_substitutions'],
                'num_insertions': results['num_insertions'],
                'num_deletions': results['num_deletions'],
                'total_characters': results['total_characters'],
                'error_breakdown': {
                    'substitutions': results['num_substitutions'],
                    'insertions': results['num_insertions'],
                    'deletions': results['num_deletions']
                }
            }
            
            if detailed:
                formatted['character_statistics'] = results.get('character_statistics', [])
                formatted['block_statistics'] = results.get('block_statistics', [])
                formatted['confusion_statistics'] = results.get('confusion_statistics', [])
            
            return formatted
            
        except Exception as e:
            print(f"CERAnalyzer error: {e}, falling back to basic calculation")
    
    # Fallback to basic Levenshtein
    distance = calculate_levenshtein_distance(reference, hypothesis)
    total_chars = len(reference)
    cer = (distance / total_chars * 100) if total_chars > 0 else 0
    
    return {
        'cer': round(cer, 2),
        'wer': calculate_wer(reference, hypothesis),
        'num_correct': total_chars - distance,
        'num_substitutions': distance,  # Approximation
        'num_insertions': 0,
        'num_deletions': 0,
        'total_characters': total_chars,
        'error_breakdown': {
            'substitutions': distance,
            'insertions': 0,
            'deletions': 0
        }
    }


def calculate_wer(reference: str, hypothesis: str):
    """
    Calculate Word Error Rate (WER)
    """
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    if len(ref_words) == 0:
        return 0.0
    
    if LEVENSHTEIN_AVAILABLE:
        distance = Levenshtein.distance(ref_words, hyp_words)
    else:
        matcher = SequenceMatcher(None, ref_words, hyp_words)
        ratio = matcher.ratio()
        distance = int((1 - ratio) * len(ref_words))
    
    wer = (distance / len(ref_words) * 100)
    return round(wer, 2)


def generate_recommendations(cer_result: dict, engine_name: str = None):
    """
    Generate smart recommendations based on CER analysis.
    
    Args:
        cer_result: CER calculation results
        engine_name: Name of OCR engine ('kraken', 'tesseract')
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    cer = cer_result.get('cer', 0)
    error_breakdown = cer_result.get('error_breakdown', {})
    
    # CER-based recommendations
    if cer < 5:
        recommendations.append("✅ Excellent accuracy! This model performs very well.")
    elif cer < 10:
        recommendations.append("✓ Good accuracy. Minor improvements possible.")
    elif cer < 20:
        recommendations.append("⚠️ Moderate accuracy. Consider retraining or using a different model.")
    else:
        recommendations.append("❌ Low accuracy. Retraining strongly recommended.")
    
    # Error type recommendations
    if error_breakdown:
        subs = error_breakdown.get('substitutions', 0)
        ins = error_breakdown.get('insertions', 0)
        dels = error_breakdown.get('deletions', 0)
        
        total_errors = subs + ins + dels
        if total_errors > 0:
            subs_pct = (subs / total_errors) * 100
            ins_pct = (ins / total_errors) * 100
            dels_pct = (dels / total_errors) * 100
            
            if subs_pct > 50:
                recommendations.append("🔤 High substitution rate - model may need more training data for similar characters.")
            if ins_pct > 30:
                recommendations.append("➕ High insertion rate - check for over-segmentation issues.")
            if dels_pct > 30:
                recommendations.append("➖ High deletion rate - check for under-segmentation or missing characters.")
    
    # Engine-specific recommendations
    if engine_name:
        if engine_name.lower() == 'tesseract':
            if cer > 15:
                recommendations.append("📖 Tesseract: Consider using '--psm' parameter tuning or language-specific training.")
        elif engine_name.lower() == 'kraken':
            if cer > 15:
                recommendations.append("🐙 Kraken: Try training with more epochs or adjusting learning rate.")
    
    # Block statistics recommendations (if available)
    block_stats = cer_result.get('block_statistics', [])
    if block_stats:
        for block in block_stats:
            if block.get('incorrect_ratio', 0) > 0.2:  # >20% error rate
                block_name = block.get('block', 'Unknown')
                recommendations.append(f"📊 Unicode Block '{block_name}' has high error rate - consider targeted training.")
    
    return recommendations


class ComparisonDashboardView(LoginRequiredMixin, TemplateView):
    """
    Main comparison dashboard
    Shows side-by-side comparison of Kraken vs Tesseract
    """
    template_name = 'core/comparison/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's documents with multiple transcriptions
        documents_with_comparisons = Document.objects.filter(
            parts__lines__transcriptions__isnull=False
        ).distinct().filter(
            Q(owner=self.request.user) | Q(shared_with_users=self.request.user)
        )
        
        context['documents'] = documents_with_comparisons
        context['page_title'] = 'Engine Comparison'
        
        return context


class DocumentComparisonView(LoginRequiredMixin, TemplateView):
    """
    Document-specific comparison view
    Shows comparison options for a single document
    Accessible via document navigation tabs
    """
    template_name = 'core/comparison/document_comparison.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the document
        document_pk = self.kwargs.get('pk')
        document = get_object_or_404(
            Document,
            pk=document_pk,
            owner=self.request.user
        )
        
        # Get all transcriptions for this document
        transcriptions = Transcription.objects.filter(
            document=document
        ).select_related('document').order_by('-created_at')
        
        # Group by engine
        kraken_trans = [t for t in transcriptions if any(
            lt.version_source and lt.version_source.startswith('kraken:') 
            for lt in t.linetranscription_set.all()[:1]
        )]
        
        tesseract_trans = [t for t in transcriptions if any(
            lt.version_source and lt.version_source.startswith('tesseract:')
            for lt in t.linetranscription_set.all()[:1]
        )]
        
        context['document'] = document
        context['transcriptions'] = transcriptions
        context['kraken_transcriptions'] = kraken_trans
        context['tesseract_transcriptions'] = tesseract_trans
        context['can_compare'] = len(transcriptions) >= 2
        context['page_title'] = f'Comparison - {document.name}'
        
        return context


class TranscriptionComparisonView(LoginRequiredMixin, View):
    """
    Compare two transcriptions side-by-side
    Calculate accuracy metrics (CER, WER)
    """
    
    def get(self, request, transcription1_id, transcription2_id):
        """Get comparison data"""
        try:
            trans1 = get_object_or_404(Transcription, pk=transcription1_id)
            trans2 = get_object_or_404(Transcription, pk=transcription2_id)
            
            # Check permissions
            if not (self.has_permission(trans1) and self.has_permission(trans2)):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Get comparison results
            comparison = self._compare_transcriptions(trans1, trans2)
            
            return JsonResponse(comparison, safe=False)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    def has_permission(self, transcription):
        """Check if user has access to transcription"""
        doc = transcription.document
        return (doc.owner == self.request.user or 
                self.request.user in doc.shared_with_users.all())
    
    def _compare_transcriptions(self, trans1, trans2):
        """
        Compare two transcriptions and calculate metrics
        Returns: {
            'engine1': info,
            'engine2': info,
            'metrics': CER/WER/accuracy,
            'diff': line-by-line differences
        }
        """
        # Get all lines from both transcriptions
        lines1 = LineTranscription.objects.filter(
            transcription=trans1
        ).select_related('line').order_by('line__order')
        
        lines2 = LineTranscription.objects.filter(
            transcription=trans2
        ).select_related('line').order_by('line__order')
        
        # Build comparison data
        comparison_data = {
            'engine1': {
                'name': self._get_engine_name(trans1),
                'model': self._get_model_name(trans1),
                'avg_confidence': trans1.avg_confidence or 0,
                'created': trans1.created_at.isoformat(),
                'line_count': lines1.count()
            },
            'engine2': {
                'name': self._get_engine_name(trans2),
                'model': self._get_model_name(trans2),
                'avg_confidence': trans2.avg_confidence or 0,
                'created': trans2.created_at.isoformat(),
                'line_count': lines2.count()
            },
            'metrics': self._calculate_metrics(lines1, lines2),
            'diff': self._generate_diff(lines1, lines2)
        }
        
        return comparison_data
    
    def _get_engine_name(self, transcription):
        """Determine engine type from LineTranscription.version_source"""
        # Get first line transcription to check version_source
        first_line = LineTranscription.objects.filter(
            transcription=transcription
        ).first()
        
        if not first_line or not first_line.version_source:
            return 'Unknown'
        
        source = first_line.version_source.lower()
        if source.startswith('kraken:'):
            return 'Kraken'
        elif source.startswith('tesseract:'):
            return 'Tesseract'
        else:
            return 'Unknown'
    
    def _get_model_name(self, transcription):
        """Extract model name from LineTranscription.version_source"""
        first_line = LineTranscription.objects.filter(
            transcription=transcription
        ).first()
        
        if not first_line or not first_line.version_source:
            return 'Unknown'
        
        # version_source format: "engine:model_name"
        parts = first_line.version_source.split(':', 1)
        if len(parts) == 2:
            return parts[1]
        else:
            return first_line.version_source
    
    def _calculate_metrics(self, lines1, lines2, detailed=False):
        """
        Calculate CER (Character Error Rate) and WER (Word Error Rate)
        Uses advanced CERAnalyzer if available.
        
        Args:
            lines1: First transcription lines
            lines2: Second transcription lines
            detailed: If True, include detailed statistics
        """
        # Combine all text
        text1_full = ' '.join([line.content for line in lines1 if line.content])
        text2_full = ' '.join([line.content for line in lines2 if line.content])
        
        # Use advanced CER calculation
        cer_result = calculate_advanced_cer(text1_full, text2_full, detailed=detailed)
        
        # Accuracy (inverse of error rate)
        accuracy = max(0, 100 - cer_result['cer'])
        
        # Similarity score (SequenceMatcher)
        similarity = SequenceMatcher(None, text1_full, text2_full).ratio() * 100
        
        # Build metrics dict
        metrics = {
            'cer': cer_result['cer'],
            'wer': cer_result['wer'],
            'accuracy': round(accuracy, 2),
            'similarity': round(similarity, 2),
            'total_chars_1': len(text1_full),
            'total_chars_2': len(text2_full),
            'total_words_1': len(text1_full.split()),
            'total_words_2': len(text2_full.split()),
            'error_breakdown': cer_result['error_breakdown']
        }
        
        # Add detailed statistics if requested
        if detailed:
            metrics['character_statistics'] = cer_result.get('character_statistics', [])
            metrics['block_statistics'] = cer_result.get('block_statistics', [])
            metrics['confusion_statistics'] = cer_result.get('confusion_statistics', [])
        
        # Add recommendations
        engine_name = self._get_engine_name(lines1[0].transcription) if lines1 else None
        metrics['recommendations'] = generate_recommendations(cer_result, engine_name)
        
        return metrics
    
    def _calculate_cer(self, text1, text2):
        """Calculate Character Error Rate using Levenshtein distance"""
        if not text1 or not text2:
            return 100.0
        
        distance = calculate_levenshtein_distance(text1, text2)
        max_len = max(len(text1), len(text2))
        
        if max_len == 0:
            return 0.0
        
        cer = (distance / max_len) * 100
        return min(cer, 100.0)
    
    def _calculate_wer(self, text1, text2):
        """Calculate Word Error Rate"""
        words1 = text1.split()
        words2 = text2.split()
        
        if not words1 or not words2:
            return 100.0
        
        # Convert to strings for Levenshtein
        str1 = ' '.join(words1)
        str2 = ' '.join(words2)
        
        distance = calculate_levenshtein_distance(str1, str2)
        max_len = max(len(words1), len(words2))
        
        if max_len == 0:
            return 0.0
        
        wer = (distance / max_len) * 100
        return min(wer, 100.0)
    
    def _generate_diff(self, lines1, lines2):
        """
        Generate line-by-line diff with highlighting
        Returns array of {line_num, text1, text2, diff_type, char_diff}
        """
        diff_data = []
        
        # Create line mapping
        lines1_dict = {line.line.order: line for line in lines1}
        lines2_dict = {line.line.order: line for line in lines2}
        
        # Get all line numbers
        all_line_nums = sorted(set(lines1_dict.keys()) | set(lines2_dict.keys()))
        
        for line_num in all_line_nums:
            line1 = lines1_dict.get(line_num)
            line2 = lines2_dict.get(line_num)
            
            text1 = line1.content if line1 else ''
            text2 = line2.content if line2 else ''
            
            # Determine diff type
            if text1 == text2:
                diff_type = 'identical'
            elif not text1:
                diff_type = 'added'
            elif not text2:
                diff_type = 'removed'
            else:
                diff_type = 'modified'
            
            # Character-level diff for modified lines
            char_diff = None
            if diff_type == 'modified':
                char_diff = self._character_diff(text1, text2)
            
            diff_data.append({
                'line_num': line_num,
                'text1': text1,
                'text2': text2,
                'diff_type': diff_type,
                'char_diff': char_diff,
                'confidence1': line1.avg_confidence if line1 else None,
                'confidence2': line2.avg_confidence if line2 else None
            })
        
        return diff_data
    
    def _character_diff(self, text1, text2):
        """
        Generate character-level diff highlighting
        Returns: {positions: [{pos, char1, char2, type}]}
        """
        matcher = SequenceMatcher(None, text1, text2)
        diffs = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                diffs.append({
                    'type': 'replace',
                    'pos1': i1,
                    'pos2': i2,
                    'text1': text1[i1:i2],
                    'text2': text2[j1:j2]
                })
            elif tag == 'delete':
                diffs.append({
                    'type': 'delete',
                    'pos1': i1,
                    'pos2': i2,
                    'text': text1[i1:i2]
                })
            elif tag == 'insert':
                diffs.append({
                    'type': 'insert',
                    'pos': j1,
                    'text': text2[j1:j2]
                })
        
        return diffs


class BatchComparisonView(LoginRequiredMixin, View):
    """
    Batch comparison for multiple documents
    Compare all Kraken vs Tesseract transcriptions
    """
    
    def post(self, request):
        """Run batch comparison"""
        try:
            document_ids = request.POST.getlist('document_ids[]')
            
            if not document_ids:
                return JsonResponse({'error': 'No documents selected'}, status=400)
            
            results = []
            
            for doc_id in document_ids:
                doc = get_object_or_404(Document, pk=doc_id)
                
                # Check permissions
                if not (doc.owner == request.user or 
                        request.user in doc.shared_with_users.all()):
                    continue
                
                # Find Kraken and Tesseract transcriptions
                kraken_trans = Transcription.objects.filter(
                    document=doc,
                    linetranscription__version_source__startswith='kraken:'
                ).distinct().first()
                
                tesseract_trans = Transcription.objects.filter(
                    document=doc,
                    linetranscription__version_source__startswith='tesseract:'
                ).distinct().first()
                
                if kraken_trans and tesseract_trans:
                    # Calculate quick metrics
                    lines_k = LineTranscription.objects.filter(
                        transcription=kraken_trans
                    )
                    lines_t = LineTranscription.objects.filter(
                        transcription=tesseract_trans
                    )
                    
                    text_k = ' '.join([l.content for l in lines_k if l.content])
                    text_t = ' '.join([l.content for l in lines_t if l.content])
                    
                    cer = self._quick_cer(text_k, text_t)
                    
                    results.append({
                        'document_id': doc.pk,
                        'document_name': doc.name,
                        'kraken_confidence': kraken_trans.avg_confidence or 0,
                        'tesseract_confidence': tesseract_trans.avg_confidence or 0,
                        'cer': round(cer, 2),
                        'accuracy': round(max(0, 100 - cer), 2),
                        'winner': 'Kraken' if kraken_trans.avg_confidence > tesseract_trans.avg_confidence else 'Tesseract'
                    })
            
            return JsonResponse({
                'results': results,
                'count': len(results)
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    def _quick_cer(self, text1, text2):
        """Quick CER calculation"""
        if not text1 or not text2:
            return 100.0
        
        distance = calculate_levenshtein_distance(text1, text2)
        max_len = max(len(text1), len(text2))
        
        if max_len == 0:
            return 0.0
        
        return min((distance / max_len) * 100, 100.0)


class ExportComparisonView(LoginRequiredMixin, View):
    """
    Export comparison results to CSV/Excel
    """
    
    def get(self, request, transcription1_id, transcription2_id):
        """Export comparison as CSV"""
        import csv
        from django.http import HttpResponse
        
        try:
            trans1 = get_object_or_404(Transcription, pk=transcription1_id)
            trans2 = get_object_or_404(Transcription, pk=transcription2_id)
            
            # Check permissions
            if not (self._has_permission(trans1, request.user) and 
                    self._has_permission(trans2, request.user)):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Create CSV response
            response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
            response['Content-Disposition'] = f'attachment; filename="comparison_{trans1.pk}_vs_{trans2.pk}.csv"'
            
            # Add BOM for Excel UTF-8 support
            response.write('\ufeff')
            
            writer = csv.writer(response)
            writer.writerow(['Line', 'Engine 1', 'Engine 2', 'Confidence 1', 'Confidence 2', 'Match'])
            
            # Get lines
            lines1 = LineTranscription.objects.filter(
                transcription=trans1
            ).select_related('line').order_by('line__order')
            
            lines2 = LineTranscription.objects.filter(
                transcription=trans2
            ).select_related('line').order_by('line__order')
            
            # Create mapping
            lines1_dict = {line.line.order: line for line in lines1}
            lines2_dict = {line.line.order: line for line in lines2}
            
            all_lines = sorted(set(lines1_dict.keys()) | set(lines2_dict.keys()))
            
            for line_num in all_lines:
                l1 = lines1_dict.get(line_num)
                l2 = lines2_dict.get(line_num)
                
                text1 = l1.content if l1 else ''
                text2 = l2.content if l2 else ''
                conf1 = l1.avg_confidence if l1 else ''
                conf2 = l2.avg_confidence if l2 else ''
                match = 'Yes' if text1 == text2 else 'No'
                
                writer.writerow([line_num, text1, text2, conf1, conf2, match])
            
            return response
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _has_permission(self, transcription, user):
        """Check permissions"""
        doc = transcription.document
        return doc.owner == user or user in doc.shared_with_users.all()


class EngineComparisonStatsView(LoginRequiredMixin, View):
    """
    API endpoint for engine comparison statistics
    Used by dashboard.html JavaScript
    """
    
    def get(self, request):
        """Get overall comparison statistics"""
        try:
            # Get all documents with multiple transcriptions (user has access to)
            user_documents = Document.objects.filter(
                Q(owner=request.user) | Q(shared_with_users=request.user)
            ).distinct()
            
            # Count documents with comparisons (Kraken + Tesseract)
            comparisons_count = 0
            total_accuracy = 0
            accuracy_count = 0
            kraken_wins = 0
            tesseract_wins = 0
            
            for doc in user_documents:
                # Check if document has both Kraken and Tesseract transcriptions
                kraken_trans = Transcription.objects.filter(
                    document=doc,
                    linetranscription__version_source__startswith='kraken:'
                ).distinct().first()
                
                tesseract_trans = Transcription.objects.filter(
                    document=doc,
                    linetranscription__version_source__startswith='tesseract:'
                ).distinct().first()
                
                if kraken_trans and tesseract_trans:
                    comparisons_count += 1
                    
                    # Track which engine has better confidence
                    kraken_conf = kraken_trans.avg_confidence or 0
                    tesseract_conf = tesseract_trans.avg_confidence or 0
                    
                    if kraken_conf > tesseract_conf:
                        kraken_wins += 1
                        total_accuracy += kraken_conf
                        accuracy_count += 1
                    elif tesseract_conf > kraken_conf:
                        tesseract_wins += 1
                        total_accuracy += tesseract_conf
                        accuracy_count += 1
                    else:
                        # Equal confidence, count both
                        total_accuracy += (kraken_conf + tesseract_conf) / 2
                        accuracy_count += 1
            
            # Calculate average accuracy
            avg_accuracy = (total_accuracy / accuracy_count * 100) if accuracy_count > 0 else 0
            
            # Determine best engine
            if kraken_wins > tesseract_wins:
                best_engine = 'Kraken'
            elif tesseract_wins > kraken_wins:
                best_engine = 'Tesseract'
            elif kraken_wins == tesseract_wins and kraken_wins > 0:
                best_engine = 'Tied'
            else:
                best_engine = 'N/A'
            
            return JsonResponse({
                'total': comparisons_count,
                'avg_accuracy': round(avg_accuracy, 1),
                'best_engine': best_engine,
                'kraken_wins': kraken_wins,
                'tesseract_wins': tesseract_wins,
                'documents_with_comparisons': comparisons_count
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'total': 0,
                'avg_accuracy': 0,
                'best_engine': 'Error'
            }, status=500)


class AdvancedComparisonView(LoginRequiredMixin, View):
    """
    Advanced comparison with detailed CER analysis and Tesseract confidence data.
    
    GET parameters:
        - trans1: First transcription ID
        - trans2: Second transcription ID
        - detailed: Include detailed statistics (default: false)
        - include_confidence: Include per-character confidence (default: false)
    """
    
    def get(self, request):
        """Get advanced comparison with detailed metrics"""
        try:
            trans1_id = request.GET.get('trans1')
            trans2_id = request.GET.get('trans2')
            detailed = request.GET.get('detailed', 'false').lower() == 'true'
            include_confidence = request.GET.get('include_confidence', 'false').lower() == 'true'
            
            if not trans1_id or not trans2_id:
                return JsonResponse({
                    'error': 'Missing parameters: trans1 and trans2 required'
                }, status=400)
            
            trans1 = get_object_or_404(Transcription, pk=trans1_id)
            trans2 = get_object_or_404(Transcription, pk=trans2_id)
            
            # Check permissions
            if not (self.has_permission(trans1) and self.has_permission(trans2)):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Get comparison with advanced metrics
            comparison = self._advanced_compare(trans1, trans2, detailed, include_confidence)
            
            return JsonResponse(comparison, safe=False)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    def has_permission(self, transcription):
        """Check if user has access to transcription"""
        doc = transcription.document
        return (doc.owner == self.request.user or 
                self.request.user in doc.shared_with_users.all())
    
    def _advanced_compare(self, trans1, trans2, detailed=False, include_confidence=False):
        """
        Advanced comparison with CERAnalyzer and Tesseract confidence.
        
        Returns comprehensive analysis including:
        - CER/WER with error breakdown
        - Per-character/Unicode block statistics
        - Confusion matrix
        - Confidence analysis (for Tesseract)
        - Smart recommendations
        """
        # Get lines
        lines1 = LineTranscription.objects.filter(
            transcription=trans1
        ).select_related('line').order_by('line__order')
        
        lines2 = LineTranscription.objects.filter(
            transcription=trans2
        ).select_related('line').order_by('line__order')
        
        # Extract engine info
        engine1_name = self._get_engine_name(trans1)
        engine2_name = self._get_engine_name(trans2)
        
        # Combine text
        text1 = ' '.join([line.content for line in lines1 if line.content])
        text2 = ' '.join([line.content for line in lines2 if line.content])
        
        # Advanced CER analysis
        cer_result = calculate_advanced_cer(text1, text2, detailed=detailed)
        
        # Build comparison data
        comparison = {
            'engine1': {
                'name': engine1_name,
                'model': self._get_model_name(trans1),
                'line_count': lines1.count(),
                'total_chars': len(text1),
                'avg_confidence': self._calculate_avg_confidence(lines1)
            },
            'engine2': {
                'name': engine2_name,
                'model': self._get_model_name(trans2),
                'line_count': lines2.count(),
                'total_chars': len(text2),
                'avg_confidence': self._calculate_avg_confidence(lines2)
            },
            'metrics': cer_result,
            'recommendations': generate_recommendations(cer_result, engine1_name)
        }
        
        # Add confidence analysis for Tesseract
        if include_confidence:
            if engine1_name == 'Tesseract':
                comparison['engine1']['confidence_analysis'] = self._analyze_tesseract_confidence(lines1)
            if engine2_name == 'Tesseract':
                comparison['engine2']['confidence_analysis'] = self._analyze_tesseract_confidence(lines2)
        
        # Add visual diff if CharacterDiffEngine available
        if CERBERUS_AVAILABLE:
            try:
                diff_engine = CharacterDiffEngine()
                diff_result = diff_engine.diff(text1, text2)
                comparison['visual_diff'] = {
                    'summary': diff_result.get('summary', {}),
                    'alignment_sample': diff_result.get('alignment', [])[:100]  # First 100 chars
                }
            except Exception as e:
                comparison['visual_diff'] = {'error': str(e)}
        
        return comparison
    
    def _get_engine_name(self, transcription):
        """Extract engine name from version_source"""
        first_line = LineTranscription.objects.filter(
            transcription=transcription
        ).first()
        
        if not first_line or not first_line.version_source:
            return 'Unknown'
        
        source = first_line.version_source.lower()
        if source.startswith('kraken:'):
            return 'Kraken'
        elif source.startswith('tesseract:'):
            return 'Tesseract'
        else:
            return 'Unknown'
    
    def _get_model_name(self, transcription):
        """Extract model name from version_source"""
        first_line = LineTranscription.objects.filter(
            transcription=transcription
        ).first()
        
        if not first_line or not first_line.version_source:
            return 'Unknown'
        
        parts = first_line.version_source.split(':', 1)
        return parts[1] if len(parts) == 2 else first_line.version_source
    
    def _calculate_avg_confidence(self, lines):
        """Calculate average confidence across all lines"""
        confidences = [line.avg_confidence for line in lines if line.avg_confidence is not None]
        if not confidences:
            return None
        return round(sum(confidences) / len(confidences), 4)
    
    def _analyze_tesseract_confidence(self, lines):
        """
        Analyze Tesseract per-character confidence data.
        
        Returns:
            Dict with confidence statistics and low-confidence segments
        """
        all_confidences = []
        low_confidence_chars = []  # Characters with <70% confidence
        
        for line in lines:
            if line.graphs:
                for graph in line.graphs:
                    if isinstance(graph, dict) and 'confidence' in graph:
                        conf = graph.get('confidence', 0)
                        all_confidences.append(conf)
                        
                        # Track low confidence characters
                        if conf < 0.7:
                            low_confidence_chars.append({
                                'char': graph.get('c', ''),
                                'confidence': round(conf, 3),
                                'line': line.line.order if line.line else None
                            })
        
        if not all_confidences:
            return {
                'available': False,
                'message': 'No confidence data available'
            }
        
        # Calculate statistics
        avg_conf = sum(all_confidences) / len(all_confidences)
        min_conf = min(all_confidences)
        max_conf = max(all_confidences)
        
        # Confidence bins
        bins = {
            'high': sum(1 for c in all_confidences if c >= 0.9),
            'medium': sum(1 for c in all_confidences if 0.7 <= c < 0.9),
            'low': sum(1 for c in all_confidences if c < 0.7)
        }
        
        return {
            'available': True,
            'avg_confidence': round(avg_conf, 4),
            'min_confidence': round(min_conf, 4),
            'max_confidence': round(max_conf, 4),
            'total_chars': len(all_confidences),
            'confidence_bins': bins,
            'low_confidence_chars': low_confidence_chars[:50]  # Top 50 worst
        }

