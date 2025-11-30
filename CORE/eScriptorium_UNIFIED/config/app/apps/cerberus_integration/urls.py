"""
CERberus Integration URLs
=========================
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CERAnalysisViewSet, dashboard_view
from .comparison_views import (
    comparison_page,
    compare_transcriptions,
    get_document_transcriptions,
    comparison_statistics,
)

app_name = 'cerberus'

# DRF Router
router = DefaultRouter()
router.register(r'analyses', CERAnalysisViewSet, basename='analysis')

urlpatterns = [
    # Dashboard
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # OCR Comparison Pages
    path('comparison/document/<int:document_id>/', comparison_page, name='comparison_page'),
    
    # OCR Comparison API
    path('api/compare/', compare_transcriptions, name='compare_transcriptions'),
    path('api/document/<int:document_id>/transcriptions/', get_document_transcriptions, name='document_transcriptions'),
    path('api/document/<int:document_id>/statistics/', comparison_statistics, name='comparison_statistics'),
    
    # API (existing)
    path('', include(router.urls)),
]
