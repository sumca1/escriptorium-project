from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = _('Users')

    def ready(self):
        super().ready()
        # Import admin to ensure it's loaded
        from django.contrib import admin
        from rest_framework.authtoken.models import Token
        from rest_framework.authtoken.apps import AuthTokenConfig
        
        # Override authtoken app verbose_name
        AuthTokenConfig.verbose_name = _('Auth Token')
        
        # Override Token model verbose_name
        Token._meta.verbose_name = _('token')
        Token._meta.verbose_name_plural = _('tokens')
