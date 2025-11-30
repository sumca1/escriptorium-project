"""
TABA Pipeline URL Configuration
"""
from django.urls import path
from . import views

app_name = 'taba'

urlpatterns = [
    # Dashboard
    path('', views.TABADashboardView.as_view(), name='dashboard'),
    
    # Ground Truth Corpus Management
    path('corpus/', views.CorpusListView.as_view(), name='corpus-list'),
    path('corpus/<int:pk>/', views.CorpusDetailView.as_view(), name='corpus-detail'),
    
    # Alignment Jobs
    path('jobs/', views.AlignmentJobListView.as_view(), name='job-list'),
    path('jobs/create/', views.CreateAlignmentJobView.as_view(), name='job-create'),
    path('jobs/<int:pk>/', views.AlignmentJobDetailView.as_view(), name='job-detail'),
    path('jobs/<int:pk>/run/', views.RunAlignmentJobView.as_view(), name='job-run'),
    
    # API endpoints
    path('api/jobs/<int:pk>/status/', views.JobStatusAPIView.as_view(), name='job-status-api'),
]
