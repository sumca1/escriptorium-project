from django.conf import settings
import time
import os


def disable_search(request):
    return {'DISABLE_ELASTICSEARCH': getattr(settings,
                                             'DISABLE_ELASTICSEARCH',
                                             True)}


def enable_cookie_consent(request):
    return {'ENABLE_COOKIE_CONSENT': getattr(settings,
                                             'ENABLE_COOKIE_CONSENT',
                                             True)}


def custom_homepage(request):
    return {'CUSTOM_HOME': getattr(settings, 'CUSTOM_HOME', False)}


def custom_contributors(request):
    return {'CUSTOM_CONTRIBUTORS': getattr(settings, 'CUSTOM_CONTRIBUTORS', False)}


def enable_text_alignment(request):
    return {'TEXT_ALIGNMENT_ENABLED': getattr(settings,
                                              'TEXT_ALIGNMENT_ENABLED',
                                              True)}


def enable_markdown_export(request):
    return {'EXPORT_OPENITI_MARKDOWN_ENABLED': getattr(
        settings, 'EXPORT_OPENITI_MARKDOWN_ENABLED', True,
    )}


def enable_tei_export(request):
    return {'EXPORT_TEI_XML_ENABLED': getattr(settings,
                                              'EXPORT_TEI_XML_ENABLED',
                                              True)}


def models_version_retention(request):
    return {'MODELS_VERSION_RETENTION': getattr(settings,
                                                'MODELS_VERSION_RETENTION')}


def cache_buster(request):
    """
    Add cache-busting version string to static files.
    
    This helps browsers refresh cached JS/CSS files when they change.
    Uses current timestamp as version number.
    
    Usage in templates:
        <script src="{% static 'editor.js' %}?v={{ STATIC_VERSION }}"></script>
    """
    # Use timestamp-based version for cache busting
    static_root = getattr(settings, 'STATIC_ROOT', None)
    
    if static_root and os.path.exists(static_root):
        # Use the modification time of the static directory
        try:
            mtime = os.path.getmtime(static_root)
            version = str(int(mtime))
        except (OSError, ValueError):
            # Fallback to current timestamp
            version = str(int(time.time()))
    else:
        # Development mode - use current timestamp (changes on restart)
        version = str(int(time.time()))
    
    return {
        'STATIC_VERSION': version,
        'JS_VERSION': version,
        'CSS_VERSION': version,
    }

