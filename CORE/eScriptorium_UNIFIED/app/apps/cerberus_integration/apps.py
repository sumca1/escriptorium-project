from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CerberusIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cerberus_integration'
    verbose_name = _('CERberus Integration')
    
    def ready(self):
        """Import signals when app is ready"""
        pass
