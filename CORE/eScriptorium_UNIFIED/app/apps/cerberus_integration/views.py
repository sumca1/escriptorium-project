"""
CERberus Integration Views
==========================

API endpoints for CER analysis.
"""

from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.models import Transcription
from .models import CERAnalysis
from .analyzer import CERAnalyzer, UNICODE_RANGES_HEBREW_ARABIC
from .serializers import CERAnalysisSerializer, CERAnalysisCreateSerializer

import csv
import io
import json


@login_required
def dashboard_view(request):
    """
    Render the CERberus Dashboard page.
    """
    return render(request, 'cerberus/dashboard.html')


class CERAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CER Analysis operations.
    
    Endpoints:
    - POST /api/cerberus/analyze/ - Create new CER analysis
    - GET /api/cerberus/analyses/ - List all analyses
    - GET /api/cerberus/analyses/{id}/ - Get specific analysis
    - GET /api/cerberus/analyses/{id}/confusion_matrix/ - Get confusion matrix
    - GET /api/cerberus/analyses/{id}/export/ - Export results (JSON/CSV)
    """
    
    queryset = CERAnalysis.objects.all()
    serializer_class = CERAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CERAnalysisCreateSerializer
        return CERAnalysisSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new CER analysis.
        
        Request body:
        {
            "ground_truth_transcription_id": 123,
            "hypothesis_transcription_id": 456,
            "ignore_punctuation": false,
            "ignore_case": false,
            "ignore_whitespace": false,
            "ignore_numbers": false,
            "ignore_newlines": false,
            "ignore_chars": "",
            "analyze_unicode_blocks": true
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract parameters
        gt_id = serializer.validated_data['ground_truth_transcription_id']
        hyp_id = serializer.validated_data['hypothesis_transcription_id']
        
        # Get transcriptions
        gt_transcription = get_object_or_404(Transcription, pk=gt_id)
        hyp_transcription = get_object_or_404(Transcription, pk=hyp_id)
        
        # Get text from transcriptions
        gt_text = self._get_transcription_text(gt_transcription)
        hyp_text = self._get_transcription_text(hyp_transcription)
        
        if not gt_text:
            return Response(
                {'error': 'Ground truth transcription is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Analysis options
        options = {
            'ignore_punctuation': serializer.validated_data.get('ignore_punctuation', False),
            'ignore_case': serializer.validated_data.get('ignore_case', False),
            'ignore_whitespace': serializer.validated_data.get('ignore_whitespace', False),
            'ignore_numbers': serializer.validated_data.get('ignore_numbers', False),
            'ignore_newlines_and_returns': serializer.validated_data.get('ignore_newlines', False),
            'ignore_chars': serializer.validated_data.get('ignore_chars', ''),
        }
        
        # Add Unicode ranges if requested
        if serializer.validated_data.get('analyze_unicode_blocks', True):
            options['unicode_ranges'] = UNICODE_RANGES_HEBREW_ARABIC
        
        # Run CER analysis
        analyzer = CERAnalyzer()
        try:
            results = analyzer.calculate_cer(gt_text, hyp_text, **options)
        except Exception as e:
            return Response(
                {'error': f'CER analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create CERAnalysis object
        cer_analysis = CERAnalysis.objects.create(
            ground_truth_transcription=gt_transcription,
            hypothesis_transcription=hyp_transcription,
            ignore_punctuation=options['ignore_punctuation'],
            ignore_case=options['ignore_case'],
            ignore_whitespace=options['ignore_whitespace'],
            ignore_numbers=options['ignore_numbers'],
            ignore_newlines=options['ignore_newlines_and_returns'],
            ignore_chars=options.get('ignore_chars', ''),
            cer_value=results['cer'],
            num_correct=results['num_correct'],
            num_substitutions=results['num_substitutions'],
            num_insertions=results['num_insertions'],
            num_deletions=results['num_deletions'],
            total_characters=results['total_characters'],
            original_lines_count=results['original_lines_count'],
            discarded_lines_count=results['discarded_lines_count'],
            processed_lines_count=results['processed_lines_count'],
            character_statistics=results['character_statistics'],
            block_statistics=results.get('block_statistics'),
            confusion_statistics=results['confusion_statistics'],
        )
        
        output_serializer = CERAnalysisSerializer(cer_analysis)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def confusion_matrix(self, request, pk=None):
        """
        Get confusion matrix for a CER analysis.
        
        Returns the top N character confusions (default: 20).
        
        Query params:
        - limit: Number of confusions to return (default: 20)
        """
        analysis = self.get_object()
        limit = int(request.query_params.get('limit', 20))
        
        confusions = analysis.get_top_confusions(limit=limit)
        
        return Response({
            'analysis_id': analysis.id,
            'cer': analysis.cer_value,
            'total_confusions': len(analysis.confusion_statistics),
            'top_confusions': confusions,
        })
    
    @action(detail=True, methods=['get'])
    def problematic_characters(self, request, pk=None):
        """
        Get characters with low accuracy.
        
        Query params:
        - threshold: Minimum accuracy (0.0-1.0, default: 0.5)
        """
        analysis = self.get_object()
        threshold = float(request.query_params.get('threshold', 0.5))
        
        problematic = analysis.get_problematic_characters(threshold=threshold)
        
        return Response({
            'analysis_id': analysis.id,
            'threshold': threshold,
            'problematic_characters': problematic,
        })
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """
        Export analysis results.
        
        Query params:
        - format: 'json' or 'csv' (default: 'json')
        - data_type: For CSV - 'character', 'block', or 'confusion' (default: 'character')
        """
        analysis = self.get_object()
        export_format = request.query_params.get('format', 'json').lower()
        
        if export_format == 'json':
            # Export full analysis as JSON
            serializer = CERAnalysisSerializer(analysis)
            response = JsonResponse(serializer.data)
            response['Content-Disposition'] = f'attachment; filename="cer_analysis_{analysis.id}.json"'
            return response
        
        elif export_format == 'csv':
            # Export specific data type as CSV
            data_type = request.query_params.get('data_type', 'character')
            
            if data_type == 'character':
                data = analysis.character_statistics
                fields = ['character', 'count', 'correct', 'incorrect', 'correct_ratio', 'incorrect_ratio']
            elif data_type == 'block':
                data = analysis.block_statistics or []
                fields = ['block', 'count', 'correct', 'incorrect', 'correct_ratio', 'incorrect_ratio']
            elif data_type == 'confusion':
                data = analysis.confusion_statistics
                fields = ['correct_character', 'generated_character', 'count', 'ratio']
            else:
                return Response(
                    {'error': f'Invalid data_type: {data_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
            
            # Return as downloadable file
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="cer_{data_type}_{analysis.id}.csv"'
            # Add UTF-8 BOM for Excel compatibility
            return HttpResponse(
                '\ufeff' + output.getvalue(),
                content_type='text/csv; charset=utf-8-sig'
            )
        
        else:
            return Response(
                {'error': f'Invalid format: {export_format}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='dashboard-stats')
    def dashboard_stats(self, request):
        """
        Get dashboard statistics.
        
        Returns:
        - total_analyses: Total number of analyses
        - avg_cer: Average CER across all analyses
        - avg_accuracy: Average accuracy
        - analyses_by_day: Analyses created per day (last 30 days)
        - top_confusions: Most common character confusions
        - problematic_chars: Characters with lowest accuracy
        """
        from django.db.models import Avg, Count
        from django.utils import timezone
        from datetime import timedelta
        from collections import Counter
        
        # Get user's analyses only
        user_analyses = self.queryset.filter(created_by=request.user)
        
        # Basic stats
        total_analyses = user_analyses.count()
        avg_cer = user_analyses.aggregate(Avg('cer'))['cer__avg'] or 0
        avg_accuracy = user_analyses.aggregate(Avg('accuracy'))['accuracy__avg'] or 0
        
        # Analyses by day (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        analyses_by_day = []
        for i in range(30):
            day = thirty_days_ago + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            count = user_analyses.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            
            analyses_by_day.append({
                'date': day.strftime('%Y-%m-%d'),
                'count': count
            })
        
        # Top confusions across all analyses
        all_confusions = []
        for analysis in user_analyses.filter(confusion_statistics__isnull=False):
            all_confusions.extend(analysis.confusion_statistics[:10])  # Top 10 from each
        
        # Count and sort
        confusion_counter = Counter()
        for conf in all_confusions:
            key = f"{conf['correct_character']}→{conf['generated_character']}"
            confusion_counter[key] += conf['count']
        
        top_confusions = [
            {
                'pair': pair,
                'count': count,
                'correct': pair.split('→')[0],
                'generated': pair.split('→')[1]
            }
            for pair, count in confusion_counter.most_common(10)
        ]
        
        # Problematic characters (lowest accuracy)
        char_stats = {}
        for analysis in user_analyses.filter(character_statistics__isnull=False):
            for char_stat in analysis.character_statistics:
                char = char_stat['character']
                if char not in char_stats:
                    char_stats[char] = {'total': 0, 'correct': 0}
                char_stats[char]['total'] += char_stat['count']
                char_stats[char]['correct'] += char_stat['correct']
        
        problematic_chars = []
        for char, stats in char_stats.items():
            if stats['total'] > 5:  # At least 5 occurrences
                accuracy = (stats['correct'] / stats['total']) * 100
                problematic_chars.append({
                    'character': char,
                    'total': stats['total'],
                    'correct': stats['correct'],
                    'accuracy': round(accuracy, 2)
                })
        
        problematic_chars.sort(key=lambda x: x['accuracy'])
        problematic_chars = problematic_chars[:10]  # Bottom 10
        
        return Response({
            'total_analyses': total_analyses,
            'avg_cer': round(avg_cer, 4),
            'avg_accuracy': round(avg_accuracy, 2),
            'analyses_by_day': analyses_by_day,
            'top_confusions': top_confusions,
            'problematic_chars': problematic_chars
        })
    
    @action(detail=False, methods=['get'], url_path='recent-analyses')
    def recent_analyses(self, request):
        """
        Get recent analyses with summary info.
        
        Query params:
        - limit: Number of results (default 10)
        - document: Filter by document ID
        """
        limit = int(request.query_params.get('limit', 10))
        document_id = request.query_params.get('document')
        
        queryset = self.queryset.filter(created_by=request.user)
        
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        
        analyses = queryset.order_by('-created_at')[:limit]
        
        results = []
        for analysis in analyses:
            results.append({
                'id': analysis.id,
                'created_at': analysis.created_at,
                'cer': analysis.cer,
                'accuracy': analysis.accuracy,
                'document_name': analysis.document.name if analysis.document else 'N/A',
                'ground_truth_name': analysis.ground_truth.name if analysis.ground_truth else 'N/A',
                'hypothesis_name': analysis.hypothesis.name if analysis.hypothesis else 'N/A',
                'total_characters': analysis.total_characters,
                'errors': analysis.substitutions + analysis.insertions + analysis.deletions
            })
        
        return Response(results)
    
    @action(detail=False, methods=['get'], url_path='dashboard-trends')
    def dashboard_trends(self, request):
        """
        Get CER trends over time.
        
        Returns daily average CER, accuracy, and error counts.
        
        Query params:
        - days: Number of days to include (default: 30)
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg, Count
        
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Get daily statistics
        daily_stats = CERAnalysis.objects.filter(
            created_at__gte=start_date
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(
            avg_cer=Avg('cer_value'),
            avg_accuracy=Avg('num_correct') / Avg('total_characters') * 100,
            total_analyses=Count('id'),
            total_errors=Count('num_substitutions') + Count('num_insertions') + Count('num_deletions')
        ).order_by('date')
        
        # Format response
        trends = []
        for stat in daily_stats:
            trends.append({
                'date': stat['date'].isoformat() if stat['date'] else None,
                'cer': round(stat['avg_cer'] or 0, 2),
                'accuracy': round(stat['avg_accuracy'] or 0, 2),
                'analyses': stat['total_analyses'],
                'total_errors': stat['total_errors']
            })
        
        # Get model comparison (if multiple hypotheses for same GT)
        model_comparison = {}
        all_analyses = CERAnalysis.objects.filter(
            created_at__gte=start_date
        ).select_related('hypothesis_transcription')
        
        for analysis in all_analyses:
            hyp_name = analysis.hypothesis_transcription.name if analysis.hypothesis_transcription else 'Unknown'
            if hyp_name not in model_comparison:
                model_comparison[hyp_name] = {
                    'analyses': 0,
                    'avg_cer': 0,
                    'total_cer': 0
                }
            model_comparison[hyp_name]['analyses'] += 1
            model_comparison[hyp_name]['total_cer'] += analysis.cer_value
        
        # Calculate averages
        for model in model_comparison:
            model_comparison[model]['avg_cer'] = round(
                model_comparison[model]['total_cer'] / model_comparison[model]['analyses'],
                2
            )
        
        return Response({
            'trends': trends,
            'model_comparison': model_comparison,
            'period_days': days
        })
    
    @action(detail=False, methods=['post'], url_path='character-diff')
    def character_diff(self, request):
        """
        Perform character-level diff between two transcriptions.
        
        Request body:
        {
            "ground_truth_transcription_id": 123,
            "hypothesis_transcription_id": 456,
            "ignore_case": false
        }
        
        Returns:
            Character-level alignment with highlighted differences
        """
        from .diff_engine import CharacterDiffEngine
        
        # Get transcription IDs
        gt_id = request.data.get('ground_truth_transcription_id')
        hyp_id = request.data.get('hypothesis_transcription_id')
        ignore_case = request.data.get('ignore_case', False)
        
        if not gt_id or not hyp_id:
            return Response(
                {'error': 'Both ground_truth_transcription_id and hypothesis_transcription_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get transcriptions
        try:
            gt_transcription = Transcription.objects.get(pk=gt_id)
            hyp_transcription = Transcription.objects.get(pk=hyp_id)
        except Transcription.DoesNotExist as e:
            return Response(
                {'error': f'Transcription not found: {str(e)}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get text
        gt_text = self._get_transcription_text(gt_transcription)
        hyp_text = self._get_transcription_text(hyp_transcription)
        
        if not gt_text:
            return Response(
                {'error': 'Ground truth transcription is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Run diff
        try:
            engine = CharacterDiffEngine(ignore_case=ignore_case)
            result = engine.diff(gt_text, hyp_text)
        except Exception as e:
            return Response(
                {'error': f'Diff failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Format response for Vue visualization
        response_data = {
            'ground_truth': result['ground_truth'],
            'hypothesis': result['hypothesis'],
            'summary': result['summary'],
            'visualization': {
                'ground_truth_html': result['visualization']['ground_truth_html'],
                'hypothesis_html': result['visualization']['hypothesis_html'],
                'has_differences': result['visualization']['has_differences']
            },
            'diffs': [
                {
                    'position': d.position,
                    'character': d.character,
                    'diff_type': d.diff_type,
                    'expected': d.expected,
                    'confidence': d.confidence
                }
                for d in result['diffs']
            ]
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _get_transcription_text(self, transcription):
        """
        Extract text from a Transcription object.
        
        Concatenates all line transcriptions.
        """
        from core.models import LineTranscription
        
        line_transcriptions = LineTranscription.objects.filter(
            transcription=transcription
        ).order_by('line__order')
        
        text_lines = []
        for lt in line_transcriptions:
            if lt.content:
                text_lines.append(lt.content)
        
        return '\n'.join(text_lines)
    
    @action(detail=False, methods=['post'], url_path='batch-analyze')
    def batch_analyze(self, request):
        """
        Batch analyze multiple transcriptions.
        
        POST /api/cerberus/analyses/batch-analyze/
        
        Request body:
        {
            "transcription_pairs": [
                {
                    "ground_truth_id": 1,
                    "hypothesis_id": 2,
                    "name": "Genesis 1:1" (optional)
                },
                ...
            ],
            "mode": "parallel" or "sequential" (optional, default: "sequential")
        }
        
        Response:
        {
            "batch_id": "uuid",
            "total": 5,
            "started": "2025-10-26T23:45:00Z",
            "mode": "sequential"
        }
        """
        transcription_pairs = request.data.get('transcription_pairs', [])
        mode = request.data.get('mode', 'sequential')
        
        if not transcription_pairs:
            return Response(
                {'error': 'transcription_pairs is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import here to avoid circular imports
        from .batch_analyzer import BatchAnalysisManager
        import uuid
        from django.utils import timezone
        
        batch_id = str(uuid.uuid4())
        
        # Create batch manager
        manager = BatchAnalysisManager(
            batch_id=batch_id,
            transcription_pairs=transcription_pairs,
            mode=mode,
            user=request.user
        )
        
        # Start processing (this will run in background if mode=parallel)
        manager.start()
        
        return Response({
            'batch_id': batch_id,
            'total': len(transcription_pairs),
            'started': timezone.now().isoformat(),
            'mode': mode
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'], url_path='batch-progress/(?P<batch_id>[^/.]+)')
    def batch_progress(self, request, batch_id=None):
        """
        Get progress of a batch analysis.
        
        GET /api/cerberus/analyses/batch-progress/{batch_id}/
        
        Response:
        {
            "batch_id": "uuid",
            "status": "running" | "completed" | "failed",
            "progress": {
                "total": 10,
                "completed": 7,
                "pending": 2,
                "failed": 1,
                "percentage": 70
            },
            "results": [
                {
                    "name": "Genesis 1:1",
                    "status": "completed",
                    "cer": 0.025,
                    "accuracy": 97.5,
                    "analysis_id": 123
                },
                ...
            ]
        }
        """
        from .batch_analyzer import BatchAnalysisManager
        
        # Get batch status from cache/database
        manager = BatchAnalysisManager.get_batch(batch_id)
        
        if not manager:
            return Response(
                {'error': 'Batch not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        progress_data = manager.get_progress()
        
        return Response(progress_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='batch-export/(?P<batch_id>[^/.]+)')
    def batch_export(self, request, batch_id=None):
        """
        Export batch analysis results to CSV or JSON.
        
        GET /api/cerberus/analyses/batch-export/{batch_id}/?format=csv|json
        
        Response: File download
        """
        from .batch_analyzer import BatchAnalysisManager
        
        export_format = request.query_params.get('format', 'csv')
        
        # Get batch results
        manager = BatchAnalysisManager.get_batch(batch_id)
        
        if not manager:
            return Response(
                {'error': 'Batch not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        results = manager.get_results()
        
        if export_format == 'csv':
            # Generate CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                'name', 'ground_truth_id', 'hypothesis_id', 
                'cer', 'accuracy', 'total_characters', 'errors',
                'substitutions', 'insertions', 'deletions',
                'status', 'created_at'
            ])
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'name': result.get('name', ''),
                    'ground_truth_id': result.get('ground_truth_id', ''),
                    'hypothesis_id': result.get('hypothesis_id', ''),
                    'cer': result.get('cer', 0),
                    'accuracy': result.get('accuracy', 0),
                    'total_characters': result.get('total_characters', 0),
                    'errors': result.get('errors', 0),
                    'substitutions': result.get('substitutions', 0),
                    'insertions': result.get('insertions', 0),
                    'deletions': result.get('deletions', 0),
                    'status': result.get('status', ''),
                    'created_at': result.get('created_at', '')
                })
            
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="batch_{batch_id}.csv"'
            return response
        
        else:  # JSON
            response = HttpResponse(
                json.dumps(results, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="batch_{batch_id}.json"'
            return response
