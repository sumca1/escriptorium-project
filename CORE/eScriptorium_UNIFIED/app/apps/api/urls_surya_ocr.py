"""
🔌 URL Configuration for Surya OCR API

This registers the Surya OCR API endpoints.

Import in your main urls.py:
    from apps.api.urls_surya_ocr import surya_router
    
    router.registry.extend(surya_router.registry)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.api.views_surya_ocr import OCREngineViewSet, DocumentSuryaOCRViewSet

# Create routers
surya_router = DefaultRouter()
surya_router.register(r'ocr', OCREngineViewSet, basename='ocr-engine')

# Document OCR endpoints are added to documents viewset via actions
# So no need to register separately

app_name = 'surya_ocr'

urlpatterns = [
    path('', include(surya_router.urls)),
]
