from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImportsConfig(AppConfig):
    name = 'imports'
    verbose_name = _('Imports')
