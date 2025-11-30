# Statistics API for BiblIA eScriptorium Homepage
# This view provides real-time statistics for the homepage dashboard

from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Q
from core.models import Document, DocumentPart, Transcription, OcrModel


class SystemStatsView(View):
    """
    API endpoint for system statistics
    Returns JSON with current system metrics
    """
    
    def get(self, request):
        """Get system statistics"""
        try:
            stats = self._calculate_stats()
            return JsonResponse(stats, safe=False)
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'documents': 0,
                'pages': 0,
                'transcriptions': 0,
                'accuracy': 0,
                'active_users': 0
            }, status=500)
    
    def _calculate_stats(self):
        """Calculate all statistics"""
        # Basic counts
        total_documents = Document.objects.count()
        total_pages = DocumentPart.objects.count()
        total_transcriptions = Transcription.objects.count()
        
        # Active users (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users = User.objects.filter(
            last_login__gte=thirty_days_ago
        ).count()
        
        # Average accuracy/confidence
        avg_confidence = Transcription.objects.aggregate(
            avg=Avg('avg_confidence')
        )['avg'] or 0
        
        # Engine breakdown
        kraken_count = OcrModel.objects.filter(
            file__iendswith='.mlmodel'
        ).count()
        
        tesseract_count = OcrModel.objects.filter(
            file__iendswith='.traineddata'
        ).count()
        
        # Recent activity (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_transcriptions = Transcription.objects.filter(
            created_at__gte=seven_days_ago
        ).count()
        
        recent_documents = Document.objects.filter(
            created_at__gte=seven_days_ago
        ).count()
        
        return {
            'documents': total_documents,
            'pages': total_pages,
            'transcriptions': total_transcriptions,
            'accuracy': round(avg_confidence, 1) if avg_confidence else 0,
            'active_users': active_users,
            'models': {
                'kraken': kraken_count,
                'tesseract': tesseract_count,
                'total': kraken_count + tesseract_count
            },
            'recent_activity': {
                'transcriptions': recent_transcriptions,
                'documents': recent_documents
            },
            'timestamp': timezone.now().isoformat()
        }


class EngineComparisonStatsView(View):
    """
    API endpoint for engine comparison statistics
    Compares Kraken vs Tesseract performance
    """
    
    def get(self, request):
        """Get engine comparison stats"""
        try:
            stats = self._calculate_engine_stats()
            return JsonResponse(stats, safe=False)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    def _calculate_engine_stats(self):
        """Calculate engine-specific statistics"""
        # Kraken statistics
        kraken_transcriptions = Transcription.objects.filter(
            model__file__iendswith='.mlmodel'
        )
        
        kraken_stats = {
            'count': kraken_transcriptions.count(),
            'avg_confidence': kraken_transcriptions.aggregate(
                avg=Avg('avg_confidence')
            )['avg'] or 0,
        }
        
        # Tesseract statistics
        tesseract_transcriptions = Transcription.objects.filter(
            model__file__iendswith='.traineddata'
        )
        
        tesseract_stats = {
            'count': tesseract_transcriptions.count(),
            'avg_confidence': tesseract_transcriptions.aggregate(
                avg=Avg('avg_confidence')
            )['avg'] or 0,
        }
        
        return {
            'kraken': kraken_stats,
            'tesseract': tesseract_stats,
            'timestamp': timezone.now().isoformat()
        }


class WeeklyActivityView(View):
    """
    API endpoint for weekly activity chart
    Returns daily counts for the last 7 days
    """
    
    def get(self, request):
        """Get weekly activity data"""
        try:
            data = self._calculate_weekly_activity()
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    def _calculate_weekly_activity(self):
        """Calculate activity for each day of the last week"""
        today = timezone.now().date()
        daily_data = []
        
        for i in range(6, -1, -1):  # Last 7 days
            date = today - timedelta(days=i)
            start = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
            end = start + timedelta(days=1)
            
            transcriptions = Transcription.objects.filter(
                created_at__gte=start,
                created_at__lt=end
            ).count()
            
            documents = Document.objects.filter(
                created_at__gte=start,
                created_at__lt=end
            ).count()
            
            daily_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'transcriptions': transcriptions,
                'documents': documents
            })
        
        return {
            'days': daily_data,
            'timestamp': timezone.now().isoformat()
        }
