from django.urls import include, path
from rest_framework_nested import routers

from api.views import (
    AnnotationComponentViewSet,
    AnnotationTaxonomyViewSet,
    AnnotationTypeViewSet,
    BlockTypeViewSet,
    BlockViewSet,
    DocumentLanguageDetectionView,  # 🌍 New: Language detection & OCR recommendations
    DocumentMetadataViewSet,
    DocumentPartTypeViewSet,
    DocumentTagViewSet,
    DocumentTranscriptionViewSet,
    DocumentViewSet,
    GroupViewSet,
    ImageAnnotationViewSet,
    ImportListView,  # 📦 New: Import list API
    ImportProgressView,  # 📦 New: Import progress tracking
    ImportViewSet,
    LineTranscriptionViewSet,
    LineTypeViewSet,
    LineViewSet,
    OcrModelStatusView,  # 🎯 New: Model status details API
    OcrModelViewSet,
    PartMetadataViewSet,
    PartViewSet,
    ProjectTagViewSet,
    ProjectViewSet,
    RegenerableAuthToken,
    ScriptViewSet,
    SearchViewSet,  # 🔍 New: Elasticsearch search
    TaskGroupDetailView,  # 📊 New: Task group status API
    TaskGroupViewSet,
    TaskListView,  # 📋 New: Task list API
    TaskReportListView,  # 📋 New: Task report list API
    TaskReportViewSet,
    TaskStatusView,  # ✅ New: Task status API
    TextAnnotationViewSet,
    TextualWitnessViewSet,
    UserViewSet,
)

# 📊 Training Status API - Real-time monitoring
from api.training_status_views import (
    ModelTrainingStatusViewSet,
    ActiveTrainingsView,
    DataQualityAnalysisView,
)

router = routers.DefaultRouter()
router.register(r'scripts', ScriptViewSet)
router.register(r'textual-witnesses', TextualWitnessViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'tasks', TaskReportViewSet)
router.register(r'models', OcrModelViewSet)
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'search', SearchViewSet, basename='search')  # 🔍 New: Elasticsearch search
router.register(r'tags/project', ProjectTagViewSet, basename='project-tag')
router.register(r'types/block', BlockTypeViewSet)
router.register(r'types/line', LineTypeViewSet)
router.register(r'types/annotations', AnnotationTypeViewSet)
router.register(r'types/part', DocumentPartTypeViewSet)

projects_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
projects_router.register(r'tags', DocumentTagViewSet, basename='document-tag')

documents_router = routers.NestedSimpleRouter(router, r'documents', lookup='document')
documents_router.register(r'metadata', DocumentMetadataViewSet, basename='metadata')
documents_router.register(r'parts', PartViewSet, basename='part')
documents_router.register(r'transcriptions', DocumentTranscriptionViewSet, basename='transcription')
documents_router.register(r'taxonomies/annotations', AnnotationTaxonomyViewSet)
documents_router.register(r'taxonomies/components', AnnotationComponentViewSet)
documents_router.register(r'import', ImportViewSet, basename='import')
documents_router.register(r'task_groups', TaskGroupViewSet, basename='task-group')

parts_router = routers.NestedSimpleRouter(documents_router, r'parts', lookup='part')
parts_router.register(r'blocks', BlockViewSet)
parts_router.register(r'lines', LineViewSet)
parts_router.register(r'transcriptions', LineTranscriptionViewSet)
parts_router.register(r'annotations/image', ImageAnnotationViewSet)
parts_router.register(r'annotations/text', TextAnnotationViewSet)
parts_router.register(r'metadata', PartMetadataViewSet, basename='partmetadata')

app_name = 'api'
urlpatterns = [
    path('', include(router.urls)),
    path('', include(documents_router.urls)),
    path('', include(parts_router.urls)),
    path('', include(projects_router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('token-auth/', RegenerableAuthToken.as_view()),
    
    # 📊 Training Status API endpoints
    path('models/<int:pk>/training-status/', 
         ModelTrainingStatusViewSet.as_view({'get': 'retrieve_training_status'}), 
         name='model-training-status'),
    path('models/<int:pk>/training-history/', 
         ModelTrainingStatusViewSet.as_view({'get': 'training_history'}), 
         name='model-training-history'),
    path('training/active/', 
         ActiveTrainingsView.as_view(), 
         name='active-trainings'),
    path('documents/<int:document_id>/data-quality/', 
         DataQualityAnalysisView.as_view(), 
         name='document-data-quality'),
    
    # 📋 Task Status & Progress API - New endpoints for task tracking
    path('tasks/<int:task_id>/status/', 
         TaskStatusView.as_view(), 
         name='task-status'),
    path('tasks/list/', 
         TaskListView.as_view(), 
         name='task-list'),
    
    # 📦 Import Progress API - Track import progress
    path('imports/', 
         ImportListView.as_view(), 
         name='import-list'),
    path('imports/<int:import_id>/status/', 
         ImportProgressView.as_view(), 
         name='import-status'),
    
    # 🎯 Enhanced Task & Model Status API - Detailed monitoring
    path('tasks/', 
         TaskReportListView.as_view(), 
         name='task-report-list'),
    path('tasks/group/<int:pk>/', 
         TaskGroupDetailView.as_view(), 
         name='task-group-detail'),
    path('models/<int:pk>/status/', 
         OcrModelStatusView.as_view(), 
         name='model-status-detail'),
    
    # 🌍 Language Detection & OCR Recommendations API - BiblIA Enhancement
    path('documents/<int:document_id>/detect-language/', 
         DocumentLanguageDetectionView.as_view(), 
         name='document-language-detection'),
]
