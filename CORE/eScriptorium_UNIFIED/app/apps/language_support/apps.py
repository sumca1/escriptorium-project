from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LanguageSupportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.language_support'
    verbose_name = _('Language Support for OCR Models')
    
    def ready(self):
        # Import signals when Django is ready
        import apps.language_support.signals