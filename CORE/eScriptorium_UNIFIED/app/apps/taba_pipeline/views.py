"""
TABA Pipeline Views
Manages external TABA pipeline execution and monitoring
"""
import os
import json
import subprocess
import threading
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages

from core.models import Document, Transcription
from .models import GroundTruthCorpus, GroundTruthText, AlignmentJob, AlignmentResult
from .executor import TABAPipelineExecutor


def _check_taba_installation():
    """Check if TABA pipeline directory exists"""
    try:
        taba_path = getattr(settings, 'TABA_PIPELINE_PATH', None)
        if taba_path and os.path.exists(taba_path):
            return os.path.exists(os.path.join(taba_path, 'main.py'))
        return False
    except (OSError, AttributeError):
        return False


def _check_passim_installation():
    """Check if Passim is installed"""
    try:
        result = subprocess.run(
            ['seriatim', '--version'],
            capture_output=True,
            text=True,
            timeout=5  # 5 seconds timeout
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


class TABADashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard for TABA pipeline management
    """
    template_name = 'taba_pipeline/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's GT corpora
        context['corpora'] = GroundTruthCorpus.objects.filter(
            owner=self.request.user
        ).order_by('-created_at')
        
        # Get recent alignment jobs
        context['recent_jobs'] = AlignmentJob.objects.filter(
            owner=self.request.user
        ).order_by('-created_at')[:10]
        
        # Statistics
        context['total_corpora'] = context['corpora'].count()
        context['total_jobs'] = AlignmentJob.objects.filter(owner=self.request.user).count()
        context['running_jobs'] = AlignmentJob.objects.filter(
            owner=self.request.user,
            status__in=['preparing', 'running_passim', 'processing']
        ).count()
        
        # Check if TABA pipeline is installed
        context['taba_installed'] = _check_taba_installation()
        context['passim_installed'] = _check_passim_installation()
        
        return context


class CorpusListView(LoginRequiredMixin, ListView):
    """
    List all Ground Truth corpora
    """
    model = GroundTruthCorpus
    template_name = 'taba_pipeline/corpus_list.html'
    context_object_name = 'corpora'
    paginate_by = 20
    
    def get_queryset(self):
        return GroundTruthCorpus.objects.filter(
            owner=self.request.user
        ).order_by('-created_at')


class CorpusDetailView(LoginRequiredMixin, DetailView):
    """
    View Ground Truth corpus details
    """
    model = GroundTruthCorpus
    template_name = 'taba_pipeline/corpus_detail.html'
    context_object_name = 'corpus'
    
    def get_queryset(self):
        return GroundTruthCorpus.objects.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get texts in this corpus
        context['texts'] = self.object.texts.all().order_by('title')
        
        # Statistics
        context['total_texts'] = self.object.texts.count()
        context['total_chars'] = sum(t.character_count for t in context['texts'])
        
        return context


class AlignmentJobListView(LoginRequiredMixin, ListView):
    """
    List all alignment jobs
    """
    model = AlignmentJob
    template_name = 'taba_pipeline/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 20
    
    def get_queryset(self):
        return AlignmentJob.objects.filter(
            owner=self.request.user
        ).select_related('document', 'ocr_transcription', 'gt_corpus').order_by('-created_at')


class AlignmentJobDetailView(LoginRequiredMixin, DetailView):
    """
    View alignment job details and results
    """
    model = AlignmentJob
    template_name = 'taba_pipeline/job_detail.html'
    context_object_name = 'job'
    
    def get_queryset(self):
        return AlignmentJob.objects.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get alignment results
        context['results'] = self.object.results.select_related('gt_text').order_by('-total_aligned_lines')
        
        # Statistics by GT text
        gt_stats = {}
        for result in context['results']:
            gt_id = result.gt_text.id
            if gt_id not in gt_stats:
                gt_stats[gt_id] = {
                    'gt_text': result.gt_text,
                    'total_pages': 0,
                    'total_lines': 0,
                    'max_cluster': 0
                }
            gt_stats[gt_id]['total_pages'] += 1
            gt_stats[gt_id]['total_lines'] += result.total_aligned_lines
            gt_stats[gt_id]['max_cluster'] = max(
                gt_stats[gt_id]['max_cluster'],
                result.max_cluster_size
            )
        
        context['gt_statistics'] = list(gt_stats.values())
        
        return context


class CreateAlignmentJobView(LoginRequiredMixin, CreateView):
    """
    Create new alignment job
    """
    model = AlignmentJob
    template_name = 'taba_pipeline/job_create.html'
    fields = [
        'name', 'document', 'ocr_transcription', 'gt_corpus',
        'passim_n', 'passim_cores', 'passim_memory', 'passim_driver_memory',
        'levenshtein_threshold'
    ]
    success_url = reverse_lazy('taba-job-list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = 'pending'
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f'Alignment job "{form.instance.name}" created successfully. '
            f'Go to job details to start the pipeline.'
        )
        
        return response
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Filter documents and transcriptions by user
        form.fields['document'].queryset = Document.objects.filter(
            owner=self.request.user
        )
        form.fields['ocr_transcription'].queryset = Transcription.objects.filter(
            document__owner=self.request.user
        )
        form.fields['gt_corpus'].queryset = GroundTruthCorpus.objects.filter(
            owner=self.request.user
        )
        
        return form


class RunAlignmentJobView(LoginRequiredMixin, TemplateView):
    """
    Execute TABA pipeline for an alignment job
    """
    def post(self, request, *args, **kwargs):
        job_id = kwargs.get('pk')
        job = get_object_or_404(
            AlignmentJob,
            pk=job_id,
            owner=request.user
        )
        
        # Check if already running
        if job.status in ['preparing', 'running_passim', 'processing']:
            return JsonResponse({
                'error': 'Job is already running'
            }, status=400)
        
        # Execute TABA pipeline in background thread
        def run_pipeline():
            executor = TABAPipelineExecutor(job)
            success, message = executor.execute()
            
        thread = threading.Thread(target=run_pipeline)
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'success': True,
            'message': f'Job {job.name} started in background',
            'job_id': job.id,
            'status': 'preparing'
        })



class JobStatusAPIView(LoginRequiredMixin, TemplateView):
    """
    Get current status of alignment job (for AJAX polling)
    """
    def get(self, request, *args, **kwargs):
        job_id = kwargs.get('pk')
        job = get_object_or_404(
            AlignmentJob,
            pk=job_id,
            owner=request.user
        )
        
        return JsonResponse({
            'job_id': job.id,
            'name': job.name,
            'status': job.status,
            'progress': job.progress,
            'total_aligned_lines': job.total_aligned_lines,
            'error_message': job.error_message,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
        })
