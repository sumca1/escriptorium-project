"""
Django App Configuration for TABA Pipeline
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TabaPipelineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.taba_pipeline'
    verbose_name = _('TABA Pipeline - Auto Ground Truth Generation')
    
    def ready(self):
        """
        Initialize TABA pipeline when Django starts
        """
        pass
