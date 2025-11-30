"""
View for the Error Correction Workspace
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Transcription


class ErrorCorrectionWorkspaceView(LoginRequiredMixin, TemplateView):
    """
    Main view for the visual error correction workspace
    Provides side-by-side image + text editing interface
    """
    template_name = 'core/error_correction/workspace.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all transcriptions accessible to the user
        if self.request.user.is_staff:
            transcriptions = Transcription.objects.select_related(
                'document'
            ).all()
        else:
            transcriptions = Transcription.objects.select_related(
                'document'
            ).filter(document__owner=self.request.user)
        
        context['transcriptions'] = transcriptions
        return context
