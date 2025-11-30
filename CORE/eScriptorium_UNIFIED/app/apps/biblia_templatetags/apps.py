"""
BiblIA Templatetags App Configuration
Custom Django template tags for BiblIA Hebrew translation project
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BibliaTemplatetagsConfig(AppConfig):
    """Configuration for BiblIA custom template tags application"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.biblia_templatetags'
    verbose_name = _('BiblIA Template Tags')
    
    def ready(self):
        """Import signals when app is ready"""
        pass
