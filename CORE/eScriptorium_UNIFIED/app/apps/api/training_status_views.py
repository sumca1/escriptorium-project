# -*- coding: utf-8 -*-
"""
Training Status API - Real-time Training Monitoring
Created: 21 אוקטובר 2025

מספק API endpoints מפורטים למעקב אחר אימון מודלים בזמן אמת.
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q, Avg, Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from core.models import OcrModel, Document, DocumentPart, Line
from reporting.models import TaskReport, TaskGroup


class ModelTrainingStatusViewSet(ViewSet):
    """
    API endpoints למעקב מפורט אחר אימון מודלים
    
    Endpoints:
    - GET /api/models/{id}/training-status/ - סטטוס אימון מפורט
    - GET /api/models/{id}/training-history/ - היסטוריית אימון
    - GET /api/models/{id}/data-stats/ - סטטיסטיקות דאטה
    - GET /api/training/active/ - כל האימונים הפעילים
    """
    permission_classes = [IsAuthenticated]
    
    def retrieve_training_status(self, request, pk=None):
        """
        מחזיר סטטוס אימון מפורט למודל ספציפי
        
        GET /api/models/{id}/training-status/
        
        Returns:
        {
            "model_id": 7,
            "model_name": "Hebrew_Ashkenazy_Test_v5",
            "training": true,
            "training_started_at": "2025-10-20T22:51:35Z",
            "training_duration_seconds": 21845,
            "current_epoch": 5,
            "total_epochs": null,
            "current_accuracy": 0.156,
            "best_accuracy": 0.191,
            "training_loss": null,
            "validation_loss": null,
            "data_stats": {
                "training_lines": 3582,
                "validation_lines": 397,
                "total_lines": 3979,
                "documents_count": 1,
                "parts_count": 56
            },
            "recent_tasks": [...],
            "estimated_completion": "2025-10-21T04:30:00Z"
        }
        """
        try:
            model = OcrModel.objects.get(pk=pk)
        except OcrModel.DoesNotExist:
            return Response(
                {"error": "Model not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # מציאת tasks קשורים
        recent_tasks = TaskReport.objects.filter(
            ocr_model_id=pk,
            method='core.tasks.segtrain'
        ).order_by('-started_at')[:10]
        
        # חישוב זמן אימון
        training_started_at = None
        training_duration = None
        if recent_tasks.exists():
            first_task = recent_tasks.last()
            training_started_at = first_task.started_at
            if model.training:
                training_duration = (timezone.now() - training_started_at).total_seconds()
        
        # סטטיסטיקות דאטה
        data_stats = self._get_data_stats(model)
        
        response_data = {
            "model_id": model.pk,
            "model_name": model.name,
            "model_type": "Segmentation" if model.job == 2 else "Recognition",
            "training": model.training,
            "training_started_at": training_started_at.isoformat() if training_started_at else None,
            "training_duration_seconds": int(training_duration) if training_duration else None,
            "training_duration_human": self._format_duration(training_duration) if training_duration else None,
            "current_epoch": model.training_epoch,
            "current_accuracy": float(model.training_accuracy) if model.training_accuracy else None,
            "accuracy_percent": float(model.accuracy_percent) if model.accuracy_percent else None,
            "data_stats": data_stats,
            "file_size_mb": round(model.file.size / 1024 / 1024, 2) if model.file else 0,
            "recent_tasks": [
                {
                    "id": task.pk,
                    "label": task.label,
                    "method": task.method,
                    "state": task.get_workflow_state_display(),
                    "queued_at": task.queued_at.isoformat() if task.queued_at else None,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "done_at": task.done_at.isoformat() if task.done_at else None,
                    "messages": task.messages[:500] if task.messages else None,  # First 500 chars
                }
                for task in recent_tasks
            ],
        }
        
        return Response(response_data)
    
    @action(detail=True, methods=['get'], url_path='training-history')
    def training_history(self, request, pk=None):
        """
        מחזיר היסטוריית אימון מפורטת - epoch by epoch
        
        GET /api/models/{id}/training-history/
        
        Returns:
        {
            "model_id": 7,
            "epochs": [
                {
                    "epoch": 0,
                    "timestamp": "2025-10-21T02:11:07Z",
                    "duration_minutes": 16.9,
                    "file_size_mb": 15.28,
                    "accuracy": 0.06
                },
                ...
            ]
        }
        """
        try:
            model = OcrModel.objects.get(pk=pk)
        except OcrModel.DoesNotExist:
            return Response(
                {"error": "Model not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # חילוץ נתונים מקבצי version
        import os
        from datetime import datetime
        from pathlib import Path
        
        epochs_data = []
        
        if model.file:
            model_dir = Path(model.file.path).parent
            
            if model_dir.exists():
                # מציאת כל קבצי version
                version_files = sorted(model_dir.glob("version_*.mlmodel"))
                
                prev_time = None
                for version_file in version_files:
                    epoch_num = int(version_file.stem.split('_')[1])
                    file_stat = version_file.stat()
                    file_size_mb = file_stat.st_size / (1024 * 1024)
                    modified_time = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    # חישוב duration מה-version הקודם
                    duration_minutes = None
                    if prev_time:
                        duration_minutes = (modified_time - prev_time).total_seconds() / 60
                    
                    epoch_info = {
                        "epoch": epoch_num,
                        "timestamp": modified_time.isoformat(),
                        "duration_minutes": round(duration_minutes, 1) if duration_minutes else None,
                        "file_size_mb": round(file_size_mb, 2),
                        "accuracy": None  # TODO: לחלץ מלוגים או מקובץ נפרד
                    }
                    
                    epochs_data.append(epoch_info)
                    prev_time = modified_time
        
        return Response({
            "model_id": model.pk,
            "model_name": model.name,
            "total_epochs": len(epochs_data),
            "epochs": epochs_data
        })
    
    def _get_data_stats(self, model):
        """חישוב סטטיסטיקות על הדאטה ששימש לאימון"""
        # מציאת documents שקשורים למודל
        docs = model.documents.all()
        
        if not docs.exists():
            return {
                "training_lines": 0,
                "validation_lines": 0,
                "total_lines": 0,
                "documents_count": 0,
                "parts_count": 0
            }
        
        parts_count = DocumentPart.objects.filter(document__in=docs).count()
        lines_count = Line.objects.filter(document_part__document__in=docs).count()
        
        # אומדן split train/validation (90/10)
        training_lines = int(lines_count * 0.9)
        validation_lines = lines_count - training_lines
        
        return {
            "training_lines": training_lines,
            "validation_lines": validation_lines,
            "total_lines": lines_count,
            "documents_count": docs.count(),
            "parts_count": parts_count,
            "avg_lines_per_part": round(lines_count / parts_count, 1) if parts_count > 0 else 0
        }
    
    def _format_duration(self, seconds):
        """המרת שניות לפורמט קריא"""
        if not seconds:
            return None
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


class ActiveTrainingsView(APIView):
    """
    API endpoint לקבלת כל האימונים הפעילים כרגע
    
    GET /api/training/active/
    
    Returns:
    {
        "active_trainings": [
            {
                "model_id": 7,
                "model_name": "Hebrew_Ashkenazy_Test_v5",
                "model_type": "Segmentation",
                "started_at": "2025-10-20T22:51:35Z",
                "duration_seconds": 21845,
                "current_accuracy": 0.156,
                "training_lines": 3582
            }
        ],
        "total_active": 1,
        "system_load": {
            "cpu_percent": 45.2,
            "memory_percent": 68.5,
            "gpu_available": true
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        active_models = OcrModel.objects.filter(training=True)
        
        trainings_data = []
        for model in active_models:
            # מציאת task הראשון
            first_task = TaskReport.objects.filter(
                ocr_model_id=model.pk,
                method='core.tasks.segtrain'
            ).order_by('started_at').first()
            
            started_at = first_task.started_at if first_task else None
            duration = (timezone.now() - started_at).total_seconds() if started_at else None
            
            trainings_data.append({
                "model_id": model.pk,
                "model_name": model.name,
                "model_type": "Segmentation" if model.job == 2 else "Recognition",
                "started_at": started_at.isoformat() if started_at else None,
                "duration_seconds": int(duration) if duration else None,
                "duration_human": self._format_duration(duration) if duration else None,
                "current_accuracy": float(model.training_accuracy) if model.training_accuracy else None,
                "current_epoch": model.training_epoch,
            })
        
        return Response({
            "active_trainings": trainings_data,
            "total_active": len(trainings_data),
            "timestamp": timezone.now().isoformat()
        })
    
    def _format_duration(self, seconds):
        """המרת שניות לפורמט קריא"""
        if not seconds:
            return None
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


class DataQualityAnalysisView(APIView):
    """
    API endpoint לניתוח איכות הדאטה לפני אימון
    
    GET /api/documents/{id}/data-quality/
    
    Returns:
    {
        "document_id": 4,
        "document_name": "Hebrew_Ashkenazy_Test_v1",
        "parts_count": 56,
        "lines_count": 3979,
        "quality_checks": {
            "transcriptions": {
                "total": 3979,
                "with_transcription": 3979,
                "coverage_percent": 100.0,
                "status": "excellent"
            },
            "baselines": {
                "total": 3979,
                "with_baseline": 3979,
                "coverage_percent": 100.0,
                "status": "excellent"
            },
            "images": {
                "total": 56,
                "available": 56,
                "missing": 0,
                "status": "excellent"
            }
        },
        "readiness": {
            "ready_for_segmentation": true,
            "ready_for_recognition": true,
            "warnings": [],
            "recommendations": []
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, document_id):
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # סטטיסטיקות בסיסיות
        parts = document.parts.all()
        parts_count = parts.count()
        lines = Line.objects.filter(document_part__document=document)
        lines_count = lines.count()
        
        # בדיקת transcriptions
        lines_with_trans = lines.filter(transcriptions__isnull=False).distinct().count()
        trans_coverage = (lines_with_trans / lines_count * 100) if lines_count > 0 else 0
        
        # בדיקת baselines
        lines_with_baseline = lines.exclude(Q(baseline='') | Q(baseline__isnull=True)).count()
        baseline_coverage = (lines_with_baseline / lines_count * 100) if lines_count > 0 else 0
        
        # בדיקת תמונות
        parts_with_images = parts.filter(image__isnull=False).count()
        
        # הערכת איכות
        warnings = []
        recommendations = []
        
        if trans_coverage < 80:
            warnings.append(f"Low transcription coverage: {trans_coverage:.1f}%")
            recommendations.append("Add more transcriptions for better recognition model")
        
        if baseline_coverage < 80:
            warnings.append(f"Low baseline coverage: {baseline_coverage:.1f}%")
            recommendations.append("Add baselines for segmentation model training")
        
        if parts_with_images < parts_count:
            warnings.append(f"Missing {parts_count - parts_with_images} images")
            recommendations.append("Upload missing images before training")
        
        # מוכנות לאימון
        ready_for_seg = baseline_coverage >= 80 and parts_with_images == parts_count
        ready_for_rec = trans_coverage >= 80 and parts_with_images == parts_count
        
        return Response({
            "document_id": document.pk,
            "document_name": document.name,
            "parts_count": parts_count,
            "lines_count": lines_count,
            "quality_checks": {
                "transcriptions": {
                    "total": lines_count,
                    "with_transcription": lines_with_trans,
                    "coverage_percent": round(trans_coverage, 1),
                    "status": self._get_status(trans_coverage)
                },
                "baselines": {
                    "total": lines_count,
                    "with_baseline": lines_with_baseline,
                    "coverage_percent": round(baseline_coverage, 1),
                    "status": self._get_status(baseline_coverage)
                },
                "images": {
                    "total": parts_count,
                    "available": parts_with_images,
                    "missing": parts_count - parts_with_images,
                    "status": "excellent" if parts_with_images == parts_count else "poor"
                }
            },
            "readiness": {
                "ready_for_segmentation": ready_for_seg,
                "ready_for_recognition": ready_for_rec,
                "warnings": warnings,
                "recommendations": recommendations
            },
            "estimated_training_time": self._estimate_training_time(lines_count)
        })
    
    def _get_status(self, coverage):
        """הערכת סטטוס לפי אחוז כיסוי"""
        if coverage >= 95:
            return "excellent"
        elif coverage >= 80:
            return "good"
        elif coverage >= 50:
            return "fair"
        else:
            return "poor"
    
    def _estimate_training_time(self, lines_count):
        """אומדן זמן אימון"""
        # אומדן גס: ~1 שניה ל-10 שורות per epoch, 15 epochs
        seconds_per_line = 0.1
        epochs = 15
        total_seconds = lines_count * seconds_per_line * epochs
        
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        return {
            "estimated_seconds": int(total_seconds),
            "estimated_human": f"~{hours}h {minutes}m" if hours > 0 else f"~{minutes}m",
            "note": "Rough estimate, actual time may vary significantly"
        }
