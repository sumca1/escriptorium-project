#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Correction Dashboard View
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Transcription


class ErrorCorrectionDashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard for error detection and correction tools
    """
    template_name = 'core/error_correction/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all transcriptions accessible by user
        user = self.request.user
        
        if user.is_superuser:
            transcriptions = Transcription.objects.all()
        else:
            # Get transcriptions from user's documents
            transcriptions = Transcription.objects.filter(
                document__owner=user
            ) | Transcription.objects.filter(
                document__shared_with_users=user
            ) | Transcription.objects.filter(
                document__shared_with_groups__in=user.groups.all()
            )
        
        # Order by most recent
        transcriptions = transcriptions.distinct().order_by('-updated_at')[:100]
        
        context['transcriptions'] = transcriptions
        
        return context
