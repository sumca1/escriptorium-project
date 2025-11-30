from django.urls import path
from django.views.generic import TemplateView

from core.views import (
    CreateDocument,
    CreateProject,
    DeleteDocumentUserShare,
    DeleteProjectUserShare,
    DocumentDashboard,
    DocumentImages,
    DocumentModels,
    DocumentOntology,
    DocumentPartsProcessAjax,
    DocumentsList,
    DocumentsTasksList,
    EditPart,
    FindAndReplace,
    Home,
    MigrateDocument,
    ModelCancelTraining,
    ModelDelete,
    ModelRightDelete,
    ModelRights,
    ModelUnbind,
    ModelUpload,
    ProjectDashboard,
    ProjectList,
    PublishDocument,
    Search,
    ShareDocument,
    ShareProject,
    UpdateDocument,
    UpdateProject,
    UserModels,
    AnalyticsDashboard,
    # FastAPI Integration Views (Day 6)
    fastapi_auto_process,
    fastapi_binarize,
    fastapi_denoise,
    fastapi_deskew,
    fastapi_enhance,
    fastapi_health,
)
from core.system_views import SystemStatusAPI, SystemMaintenanceAPI

# Import Error Correction Workspace view
from core.views_workspace import ErrorCorrectionWorkspaceView

# Import Analytics API views
from core.views_analytics_api import (
    get_model_training_status,
    get_model_training_history,
    get_models_overview,
    get_document_statistics,
    get_system_statistics,
    export_analytics_report,
)

# Import Export views
from core.views_export import (
    export_pdf,
    export_docx,
    export_options,
)

# Import Spell Check API views
from core.views_spell_check_api import (
    get_document_lines,
    update_line_content,
    run_spell_check,
    auto_correct_transcription,
    export_error_report,
    get_line_image,
)

# Import Error Correction views from the new error_correction_views package
from core.error_correction_views.comparison import (
    ComparisonDashboardView,
    DocumentComparisonView,
    TranscriptionComparisonView,
    BatchComparisonView,
    ExportComparisonView,
    EngineComparisonStatsView,
    TranscriptionSelectorView,
    AdvancedComparisonView,  # New: Advanced comparison with CERAnalyzer
)

# Import Model Checker View
from core.views import ModelCheckerView

# Import Passim Text Alignment views
from core.views_passim import (
    PassimDashboardView,
    PassimHealthCheckView,
    PassimAlignDocumentsView,
    PassimCompareTextsView,
)

# Import CERberus Model Evaluation views
from core.views_cerberus import (
    CERberusDashboardView,
    CERCalculationView,
    DocumentCERView,
)

# Import Error Detection API views (BiblIA Enhancement Feature #2)
from core.views_errors import (
    get_line_errors,
    correct_error,
    ignore_error,
    add_to_dictionary,
    rescan_line,
    get_error_statistics,
)
from core.error_correction_views.error_dashboard import ErrorCorrectionDashboardView
from core.error_correction_views.error_correction import (
    SpellCheckView,
    ErrorDetectionView,
    AutoCorrectionView,
    SuggestCorrectionModeView,
)

# Import Text Alignment API views (BiblIA Enhancement Feature #4)
from core.alignment_views import (
    create_alignment,
    get_alignment_status,
    get_alignment_pairs,
    verify_alignment_pair,
    export_alignment,
    list_alignments,
)

urlpatterns = [
    path('', Home.as_view(), name='home'),

    path('search/', Search.as_view(), name='search'),
    path('advanced-search/', TemplateView.as_view(template_name='core/search/advanced_search.html'), name='advanced-search'),
    path('find-replace/', FindAndReplace.as_view(), name='find-replace'),

    path('projects/create/', CreateProject.as_view(), name='project-create'),
    path('projects/', ProjectList.as_view(), name='projects-list'),
    path('project/<str:slug>/', ProjectDashboard.as_view(), name='project-dashboard'),
    path('project/<str:slug>/edit/', UpdateProject.as_view(), name='project-update'),
    path('project/<str:slug>/documents/', DocumentsList.as_view(), name='documents-list'),
    path('project/<str:slug>/document/create/', CreateDocument.as_view(), name='document-create'),
    path('project/<int:pk>/share/', ShareProject.as_view(), name='project-share'),
    path('project/delete_share/', DeleteProjectUserShare.as_view(), name='delete-project-share'),

    path('documents/tasks/', DocumentsTasksList.as_view(), name='documents-tasks-list'),
    path('document/<int:pk>/', DocumentDashboard.as_view(), name='document-detail'),
    path('document/<int:pk>/edit/', UpdateDocument.as_view(), name='document-update'),
    path('document/<int:pk>/ontology/', DocumentOntology.as_view(), name='document-ontology'),
    path('document/<int:pk>/parts/edit/', EditPart.as_view(), name='document-part-edit'),
    path('document/<int:pk>/part/<int:part_pk>/edit/', EditPart.as_view(),
         name='document-part-edit'),
    path('document/<int:pk>/images/', DocumentImages.as_view(), name='document-images'),
    path('models/', UserModels.as_view(), name='user-models'),
    path('analytics/', AnalyticsDashboard.as_view(), name='analytics-dashboard'),
    
    # Analytics API Endpoints
    path('api/models/<int:model_id>/training-status/', get_model_training_status, name='model-training-status'),
    path('api/models/<int:model_id>/training-history/', get_model_training_history, name='model-training-history'),
    path('api/analytics/models-overview/', get_models_overview, name='models-overview'),
    path('api/analytics/document/<int:document_id>/', get_document_statistics, name='document-statistics'),
    path('api/analytics/system/', get_system_statistics, name='system-statistics'),
    path('api/analytics/export/<int:model_id>/', export_analytics_report, name='export-analytics'),
    
    # Export Endpoints - PDF/DOCX
    path('document/<int:document_pk>/export/pdf/', export_pdf, name='export-pdf'),
    path('document/<int:document_pk>/export/docx/', export_docx, name='export-docx'),
    path('document/<int:document_pk>/export/options/', export_options, name='export-options'),
    
    path('models/new/', ModelUpload.as_view(), name='model-upload'),
    path('model/<int:pk>/delete/', ModelDelete.as_view(), name='model-delete'),
    path('model/<int:pk>/unbind/<int:docPk>/', ModelUnbind.as_view(), name='model-unbind'),
    path('model/<int:pk>/cancel_training/', ModelCancelTraining.as_view(),
         name='model-cancel-training'),
    path('model/<int:pk>/rights/', ModelRights.as_view(), name='model-rights'),
    path('model/<int:modelPk>/right/<int:pk>/delete/', ModelRightDelete.as_view(), name='model-right-delete'),
    path('document/<int:document_pk>/models/', DocumentModels.as_view(), name='document-models'),
    path('document/<int:pk>/publish/', PublishDocument.as_view(), name='document-publish'),
    path('document/<int:pk>/share/', ShareDocument.as_view(), name='document-share'),
    path('document/<int:pk>/migrate/', MigrateDocument.as_view(), name='document-migrate'),
    path('document/delete_share/', DeleteDocumentUserShare.as_view(), name='delete-document-share'),
    path('document/<int:pk>/process/', DocumentPartsProcessAjax.as_view(),
         name='document-parts-process'),
    path('contributors/', TemplateView.as_view(template_name='core/contributors.html'), name='contributors'),
    path('credits/', TemplateView.as_view(template_name='core/credits.html'), name='credits'),
    path('system-maintenance/', TemplateView.as_view(template_name='core/system_maintenance.html'), name='system-maintenance'),
    
    # System APIs
    path('api/system-status/', SystemStatusAPI.as_view(), name='api-system-status'),
    path('api/system-maintenance/', SystemMaintenanceAPI.as_view(), name='api-system-maintenance'),
    
    # Model Checker - NEW!
    path('model-checker/', ModelCheckerView.as_view(), name='model-checker'),
    
    # Engine Comparison - NEW!
    path('comparison/', ComparisonDashboardView.as_view(), name='comparison-dashboard'),
    path('comparison/selector/', TranscriptionSelectorView.as_view(), name='comparison-selector'),
    path('comparison/document/<int:pk>/', DocumentComparisonView.as_view(), name='comparison-document'),
    path('comparison/viewer/', TemplateView.as_view(template_name='core/comparison/viewer.html'), 
         name='comparison-viewer'),
    path('api/comparison/<int:transcription1_id>/<int:transcription2_id>/', 
         TranscriptionComparisonView.as_view(), name='comparison-transcriptions'),
    path('api/comparison/batch/', BatchComparisonView.as_view(), name='comparison-batch'),
    path('api/comparison/<int:transcription1_id>/<int:transcription2_id>/export/', 
         ExportComparisonView.as_view(), name='comparison-export'),
    path('api/engine-comparison-stats/', EngineComparisonStatsView.as_view(), 
         name='engine-comparison-stats'),
    # Advanced Comparison with CERAnalyzer + Tesseract confidence
    path('api/comparison/advanced/', AdvancedComparisonView.as_view(), 
         name='comparison-advanced'),
    
    # Error Correction Dashboard
    path('error-correction/', ErrorCorrectionDashboardView.as_view(), name='error-correction-dashboard'),
    
    # Error Detection & Correction APIs (OCR Quality)
    path('api/spell-check/<int:transcription_id>/', SpellCheckView.as_view(), name='spell-check'),
    path('api/error-detection/<int:transcription_id>/', ErrorDetectionView.as_view(), name='error-detection'),
    path('api/auto-correct/<int:transcription_id>/', AutoCorrectionView.as_view(), name='auto-correct'),
    path('api/suggest-mode/<int:transcription_id>/', SuggestCorrectionModeView.as_view(), name='suggest-correction-mode'),
    
    # New Error Correction Workspace APIs
    path('error-correction/workspace/', ErrorCorrectionWorkspaceView.as_view(), name='error-correction-workspace'),
    path('api/spell-check/document/<int:transcription_id>/', get_document_lines, name='spell-check-document-lines'),
    path('api/lines/<int:line_trans_id>/update/', update_line_content, name='update-line-content'),
    path('api/spell-check/run/<int:transcription_id>/', run_spell_check, name='run-spell-check'),
    path('api/spell-check/auto-correct/<int:transcription_id>/', auto_correct_transcription, name='auto-correct-transcription'),
    path('api/spell-check/export/<int:transcription_id>/', export_error_report, name='export-error-report'),
    path('api/lines/<int:line_id>/image/', get_line_image, name='get-line-image'),
    
    path('test/', TemplateView.as_view(template_name='core/test.html')),
    
    # FastAPI Integration Endpoints (Day 6)
    path('api/fastapi/auto-process/', fastapi_auto_process, name='fastapi-auto-process'),
    path('api/fastapi/binarize/', fastapi_binarize, name='fastapi-binarize'),
    path('api/fastapi/denoise/', fastapi_denoise, name='fastapi-denoise'),
    path('api/fastapi/deskew/', fastapi_deskew, name='fastapi-deskew'),
    path('api/fastapi/enhance/', fastapi_enhance, name='fastapi-enhance'),
    path('api/fastapi/health/', fastapi_health, name='fastapi-health'),
    
    # BiblIA Error Detection API (Feature #2)
    path('api/errors/line/<int:line_id>/', get_line_errors, name='api-line-errors'),
    path('api/errors/<int:error_id>/correct/', correct_error, name='api-correct-error'),
    path('api/errors/<int:error_id>/ignore/', ignore_error, name='api-ignore-error'),
    path('api/errors/dictionary/add/', add_to_dictionary, name='api-add-to-dictionary'),
    path('api/errors/line/<int:line_id>/rescan/', rescan_line, name='api-rescan-line'),
    path('api/errors/stats/', get_error_statistics, name='api-error-stats'),
    
    # BiblIA Text Alignment - Passim Integration (Feature #4)
    path('passim/', PassimDashboardView.as_view(), name='passim-dashboard'),
    path('api/passim/health/', PassimHealthCheckView.as_view(), name='passim-health'),
    path('api/passim/align/', PassimAlignDocumentsView.as_view(), name='passim-align'),
    path('api/passim/compare/', PassimCompareTextsView.as_view(), name='passim-compare'),
    
    # BiblIA Model Evaluation - CERberus Integration (Feature #5)
    path('cerberus/', CERberusDashboardView.as_view(), name='cerberus-dashboard'),
    path('api/cerberus/calculate/', CERCalculationView.as_view(), name='cerberus-calculate'),
    path('api/cerberus/document/', DocumentCERView.as_view(), name='cerberus-document'),
    
    # BiblIA Text Alignment API (Feature #4 - Passim Integration)
    path('api/alignments/', list_alignments, name='api-alignments-list'),
    path('api/alignments/create/', create_alignment, name='api-alignment-create'),
    path('api/alignments/<int:alignment_id>/', get_alignment_status, name='api-alignment-status'),
    path('api/alignments/<int:alignment_id>/pairs/', get_alignment_pairs, name='api-alignment-pairs'),
    path('api/alignments/<int:alignment_id>/export/', export_alignment, name='api-alignment-export'),
    path('api/alignments/pairs/<int:pair_id>/verify/', verify_alignment_pair, name='api-alignment-verify'),
]
