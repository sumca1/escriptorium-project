import json
import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import connection, transaction
from django.db.models import Count, F, Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from django_filters import Filter, FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView

from api.serializers import (
    AlignSerializer,
    AnnotationComponentSerializer,
    AnnotationTaxonomySerializer,
    AnnotationTypeSerializer,
    BlockSerializer,
    BlockTypeSerializer,
    DetailedGroupSerializer,
    DetailedLineSerializer,
    DocumentMetadataSerializer,
    DocumentPartMetadataSerializer,
    DocumentPartTypeSerializer,
    DocumentSerializer,
    DocumentTagSerializer,
    DocumentTasksSerializer,
    ImageAnnotationSerializer,
    ImportSerializer,
    LineOrderSerializer,
    LineSerializer,
    LineTranscriptionSerializer,
    LineTypeSerializer,
    OcrModelSerializer,
    OcrModelStatusSerializer,
    PartBulkMoveSerializer,
    PartDetailSerializer,
    PartMoveSerializer,
    PartSerializer,
    ProjectSerializer,
    ProjectTagSerializer,
    ScriptSerializer,
    SegmentSerializer,
    SegTrainSerializer,
    TaskGroupSerializer,
    TaskReportSerializer,
    TextAnnotationSerializer,
    TextualWitnessSerializer,
    TrainSerializer,
    TranscribeSerializer,
    TranscriptionSerializer,
    UserSerializer,
)
from core.merger import MAX_MERGE_SIZE, merge_lines
from core.models import (
    AlreadyProcessingException,
    AnnotationComponent,
    AnnotationTaxonomy,
    AnnotationType,
    Block,
    BlockType,
    Document,
    DocumentMetadata,
    DocumentPart,
    DocumentPartMetadata,
    DocumentPartType,
    DocumentTag,
    ImageAnnotation,
    Line,
    LineTranscription,
    LineType,
    OcrModel,
    Project,
    ProjectTag,
    ProtectedObjectException,
    Script,
    TextAnnotation,
    TextualWitness,
    Transcription,
)
from core.tasks import recalculate_masks
from imports.forms import ExportForm, ImportForm
from imports.models import DocumentImport
from imports.parsers import ParseError
from reporting.models import TaskGroup, TaskReport
from users.consumers import send_event
from users.models import Group, User
from versioning.models import NoChangeException

logger = logging.getLogger(__name__)

CLIENT_TASK_NAME_MAP = {
    'segtrain': 'training',
    'train': 'training',
    'document_export': 'export',
    'document_import': 'import'
}


class TagFilter(Filter):
    def filter(self, qs, value):
        if value and '|' in value:
            # OR boolean
            values = value.split('|')
            if 'none' in values:
                values.remove('none')
                qs = (qs.annotate(tag_count=Count('tags'))
                      .filter(Q(tag_count=0) | Q(**{'tags__in': values})))
            else:
                return qs.filter(**{'tags__in': values})
        elif value and ',' in value:
            # AND boolean
            values = value.split(',')
            for tag in values:
                qs = qs.filter(tags=tag)
        elif value == 'none':
            return qs.annotate(tag_count=Count('tags')).filter(tag_count=0)
        else:
            return super().filter(qs, value)
        return qs


class TagFilterSet(FilterSet):
    tags = TagFilter()


class DocumentTagFilterSet(TagFilterSet):
    class Meta:
        model = Document
        fields = ['project', 'tags']


class IsAdminOrSelfOnly(BasePermission):
    """
    Permission class letting a non-admin user only update his own record,
    and admin users can update everyone and create/delete users.
    Really only makes sense for the UserViewset.
    """

    def has_permission(self, request, view):
        return bool(request.method in ("GET", "PUT", "PATCH")
                    or (request.method in ("POST", "DELETE") and request.user.is_staff))

    def has_object_permission(self, request, view, obj):
        return bool(obj == request.user
                    or request.user.is_staff)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100


class ExtraLargeResultsSetPagination(PageNumberPagination):
    page_size = 500


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrSelfOnly,)

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            return qs.filter(id=self.request.user.id)
        return qs

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the currently logged in user"""
        if not request.user.is_authenticated:
            raise NotAuthenticated
        qs = self.get_queryset()
        # get_queryset will contain only the current user for non-staff, so we can save a DB query
        if not request.user.is_staff:
            user = qs.first()
        else:
            user = qs.get(id=request.user.id)
        serializer = UserSerializer(user)
        json = serializer.data
        return Response(
            status=status.HTTP_200_OK,
            data=json,
        )


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = DetailedGroupSerializer

    def get_queryset(self):
        return self.request.user.groups.all()


class ScriptViewSet(ReadOnlyModelViewSet):
    pagination_class = ExtraLargeResultsSetPagination
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer


class TextualWitnessViewSet(ModelViewSet):
    queryset = TextualWitness.objects.all()
    serializer_class = TextualWitnessSerializer

    def get_queryset(self):
        return TextualWitness.objects.filter(
            owner=self.request.user
        )


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = TagFilterSet
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['created_at', 'documents_count', 'id', 'name', 'owner', 'updated_at']

    def get_queryset(self):
        return (Project.objects
                .for_user_read(self.request.user)
                .annotate(documents_count=Count(
                    'documents',
                    filter=~Q(documents__workflow_state=Document.WORKFLOW_STATE_ARCHIVED),
                    distinct=True))
                .select_related('owner')
                .order_by('-updated_at')
                )

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        project = self.get_object()
        if 'group' in request.data:
            try:
                target = (Group.objects
                          .filter(user=request.user)
                          .get(pk=request.data['group']))
            except Group.DoesNotExist:
                return Response({'error': 'invalid group.'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                project.shared_with_groups.add(target)
        elif 'user' in request.data:
            try:
                target = User.objects.get(username=request.data['user'])
            except User.DoesNotExist:
                return Response({'error': 'invalid username.'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                project.shared_with_users.add(target)
        else:
            return Response({'error': 'Please provide either a group(pk) or user(username).'},
                            status=status.HTTP_400_BAD_REQUEST)

        # re-instantiate serializer to use updated data
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectTagViewSet(ModelViewSet):
    queryset = ProjectTag.objects.all()
    serializer_class = ProjectTagSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        return ProjectTag.objects.filter(user=self.request.user)


class DocumentTagViewSet(ModelViewSet):
    queryset = DocumentTag.objects.all()
    serializer_class = DocumentTagSerializer
    pagination_class = LargeResultsSetPagination

    def perform_create(self, serializer):
        project = Project.objects.get(pk=self.kwargs.get('project_pk'))
        return serializer.save(project=project)

    def get_queryset(self):
        return DocumentTag.objects.filter(project__pk=self.kwargs.get('project_pk'))


class DocumentViewSet(ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['project', 'tags']
    filterset_class = DocumentTagFilterSet
    ordering_fields = ['name', 'parts_count', 'updated_at']

    def get_queryset(self):
        qs = Document.objects.for_user(self.request.user).prefetch_related(
            Prefetch('valid_block_types', queryset=BlockType.objects.order_by('name')),
            Prefetch('valid_line_types', queryset=LineType.objects.order_by('name')),
        ).annotate(parts_count=Count('parts', distinct=True)).order_by('-updated_at')

        if self.action in ['retrieve', 'list']:
            qs = qs.prefetch_related(
                Prefetch('tags', queryset=DocumentTag.objects.all()),
                Prefetch('transcriptions', queryset=Transcription.objects.filter(archived=False))
            )

        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def form_error(self, msg):
        return Response({'status': 'error', 'error': msg}, status=400)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def tasks(self, request):
        extra = {}

        if not request.user.is_staff:
            extra["owner"] = request.user
        else:
            # Filter results by owner
            user_id_filter = request.GET.get('user_id')

            if user_id_filter:
                try:
                    user_id_filter = int(user_id_filter)
                except ValueError:
                    return Response(
                        {'error': 'Invalid user_id, it should be an int.'},
                        status=400
                    )

                extra["owner"] = user_id_filter

        # Filter results by querying their name
        document_name_filter = request.GET.get('name')
        if document_name_filter:
            extra["name__icontains"] = document_name_filter

        # Filter results by TaskReport.workflow_state
        state_filter = request.GET.get('task_state', '').lower()
        if state_filter:
            mapped_labels = {label.lower(): state for state, label in TaskReport.WORKFLOW_STATE_CHOICES}
            if state_filter not in mapped_labels:
                return Response(
                    {'error': 'Invalid task_state, it should match a valid workflow_state.'},
                    status=400
                )

            extra["reports__workflow_state__in"] = [mapped_labels[state_filter]]

        documents = Document.objects.filter(reports__isnull=False, **extra).select_related('owner').distinct()

        page = self.paginate_queryset(documents)
        if page is not None:
            serializer = DocumentTasksSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DocumentTasksSerializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel_tasks(self, request, pk=None):
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={'status': 'Not Found', 'error': f"Document with pk {pk} doesn't exist"}
            )

        if not request.user.is_staff and document.owner != request.user:
            raise PermissionDenied

        # Revoking all pending/running tasks for the specified document

        reports = (document.reports
                   .prefetch_related('document_part')
                   .filter(workflow_state__in=[TaskReport.WORKFLOW_STATE_QUEUED,
                                               TaskReport.WORKFLOW_STATE_STARTED]))

        if request.data.get("task_report"):
            # If a task report PK is provided, try to locate it
            task_report_pk = int(request.data.get("task_report"))
            try:
                TaskReport.objects.get(pk=task_report_pk)
                # limit the canceled tasks to just the one with that pk
                reports = reports.filter(pk=task_report_pk)
            except TaskReport.DoesNotExist:
                # otherwise there is an error here, so let's return a response
                return Response({
                    'status': 'error',
                    'error': 'Could not cancel: the requested task could not be found.'
                }, status=400)

        count = len(reports)  # evaluate query
        for report in reports:
            report.cancel(request.user.username)

            method_name = report.method.split('.')[-1]
            task_name = CLIENT_TASK_NAME_MAP.get(method_name, method_name)

            if report.document_part:
                continue

            try:
                send_event('document', document.pk, f'{task_name}:error', {'reason': _('Canceled.')})
            except Exception as e:
                # don't crash on websocket error
                logger.exception(e)

        if count:
            try:
                # send a single websocket message for all parts
                if report.document_part:
                    send_event('document', document.pk, 'parts:workflow', {
                        'parts': [{
                            'id': report.document_part.pk,
                            'process': task_name,
                            'status': 'error',
                            'reason': _('Canceled.')
                        } for report in reports]
                    })
            except Exception as e:
                # don't crash on websocket error
                logger.exception(e)

        # Executing all the glue code outside the real revoking of tasks to maintain db objects
        # up-to-date with the real state of the app (e.g.: we stopped a training, we need to set
        # the model.training attribute to False)
        for model in document.ocr_models.filter(training=True):
            model.cancel_training(revoke_task=False, username=request.user.username)  # We already revoked the Celery task

        for doc_import in document.documentimport_set.all():
            doc_import.cancel(revoke_task=False, username=request.user.username)  # We already revoked the Celery task

        return Response({
            'status': 'canceled',
            'details': f'Canceled {count} pending/running tasks linked to document {document.name}.'
        })

    @action(detail=True, methods=['post'])
    def imports(self, request, pk=None):
        document = self.get_object()
        
        # Handle multiple file uploads
        upload_files = request.FILES.getlist('upload_file')
        
        if upload_files and len(upload_files) > 1:
            # Multiple files uploaded - process each one
            successful_imports = 0
            failed_imports = []
            
            for upload_file in upload_files:
                # Create a new FILES dict with single file
                single_file_dict = {'upload_file': upload_file}
                
                form = ImportForm(document, request.user,
                                  request.data, single_file_dict)
                if form.is_valid():
                    form.save()  # create the import
                    try:
                        form.process()
                        successful_imports += 1
                    except ParseError as e:
                        failed_imports.append(f"{upload_file.name}: {_('Parse error')}")
                else:
                    failed_imports.append(f"{upload_file.name}: {json.dumps(form.errors)}")
            
            # Return summary of results
            if failed_imports:
                return Response({
                    'status': 'partial',
                    'successful': successful_imports,
                    'failed': len(failed_imports),
                    'errors': failed_imports
                })
            else:
                return Response({
                    'status': 'ok',
                    'message': _('Successfully imported %(count)s files') % {'count': successful_imports}
                })
        else:
            # Single file or no file - original behavior
            form = ImportForm(document, request.user,
                              request.data, request.FILES)
            if form.is_valid():
                form.save()  # create the import
                try:
                    form.process()
                except ParseError:
                    return self.form_error("Incorrectly formatted file, couldn't parse it.")
                return Response({'status': 'ok'})
            else:
                return self.form_error(json.dumps(form.errors))

    @action(detail=True, methods=['post'])
    def cancel_import(self, request, pk=None):
        document = self.get_object()
        current_import = document.documentimport_set.order_by('started_on').last()
        if current_import.is_cancelable():
            current_import.cancel(username=request.user.username)
            return Response({'status': 'canceled'})
        else:
            return Response({'status': 'already stopped'}, status=400)

    @action(detail=True, methods=['post'])
    def cancel_training(self, request, pk=None):
        document = self.get_object()
        model = document.ocr_models.filter(training=True).last()
        try:
            model.cancel_training(username=request.user.username)
        except Exception as e:
            logger.exception(e)
            return Response({'status': 'failed'}, status=400)
        return Response({'status': 'canceled'})

    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        document = self.get_object()
        form = ExportForm(document, request.user, request.data)
        if form.is_valid():
            # return form.stream()
            form.process()
            return Response({'status': 'ok'})
        else:
            return self.form_error(json.dumps(form.errors))

    def get_process_response(self, request, serializer_class):
        context = self.get_serializer_context()
        context['document'] = self.get_object()
        serializer = serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            try:
                serializer.process()
            except AlreadyProcessingException:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'status': 'error',
                                      'error': 'Already processing.'})

            return Response(status=status.HTTP_200_OK,
                            data={'status': 'ok'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'status': 'error',
                                  'error': serializer.errors})

    @action(detail=True, methods=['post'])
    def segment(self, request, pk=None):
        return self.get_process_response(request, SegmentSerializer)

    @action(detail=True, methods=['post'])
    def train(self, request, pk=None):
        return self.get_process_response(request, TrainSerializer)

    @action(detail=True, methods=['post'])
    def segtrain(self, request, pk=None):
        return self.get_process_response(request, SegTrainSerializer)

    @action(detail=True, methods=['post'])
    def transcribe(self, request, pk=None):
        return self.get_process_response(request, TranscribeSerializer)

    @action(detail=True, methods=['post'])
    def align(self, request, pk=None):
        return self.get_process_response(request, AlignSerializer)

    @action(detail=True, methods=['post'])
    def forced_align(self, request, pk=None):

        document = self.get_object()

        if 'parts' in request.data:
            pks = request.data.get('parts')
            try:
                iter(pks)
            except TypeError:
                return Response({'error': "'parts' has to be a list."},
                                status=status.HTTP_400_BAD_REQUEST)
            parts = document.parts.filter(pk__in=pks)
        else:
            parts = document.parts.all()

        if 'model' not in request.data:
            return Response({'error': "model(pk) is mandatory."},
                            status=status.HTTP_400_BAD_REQUEST)

        if 'transcription' not in request.data:
            return Response({'error': "transcription(pk) is mandatory."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            document.transcriptions.get(pk=self.request.data.get('transcription'))
        except Transcription.DoesNotExist:
            return Response({'error': "Invalid transcription."},
                            status=status.HTTP_400_BAD_REQUEST)

        from core.tasks import forced_align
        for part in parts:
            forced_align.delay(
                instance_pk=part.pk,
                model_pk=request.data['model'],
                transcription_pk=request.data['transcription'],
                part_pk=part.pk,
                user_pk=request.user.pk
            )

        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def modify_ontology(self, request, pk=None):
        # special PATCH action to modify documents' ontology nested relationships
        # (can't be done from normal PUT/PATCH on a document because nested)

        # check for needed params
        if not any(param in request.data for param in [
            'valid_part_types', 'valid_line_types', 'valid_block_types'
        ]):
            return Response(
                {'error': "Must supply at least one of valid_part_types, valid_line_types, or valid_block_types."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        document = self.get_object()

        # for all ontologies (part, line, block): check if array of pks is valid, and
        # matching type objects exist, then set relations on the document to them

        # part (image)
        if 'valid_part_types' in request.data:
            part_types = request.data['valid_part_types']
            if not all([isinstance(pk, int) for pk in part_types]):
                return Response(
                    {'error': "valid_part_types must be an array of PKs."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            valid_part_types = DocumentPartType.objects.filter(pk__in=part_types)
            if valid_part_types.count() < len(part_types):
                return Response(
                    {'error': "At least one pk in valid_part_types is invalid."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            document.valid_part_types.set(valid_part_types)

        # line
        if 'valid_line_types' in request.data:
            line_types = request.data['valid_line_types']
            if not all([isinstance(pk, int) for pk in line_types]):
                return Response(
                    {'error': "valid_line_types must be an array of PKs."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            valid_line_types = LineType.objects.filter(pk__in=line_types)
            if valid_line_types.count() < len(line_types):
                return Response(
                    {'error': "At least one pk in valid_line_types is invalid."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            document.valid_line_types.set(valid_line_types)

        # block (region)
        if 'valid_block_types' in request.data:
            block_types = request.data['valid_block_types']
            if not all([isinstance(pk, int) for pk in block_types]):
                return Response(
                    {'error': "valid_block_types must be an array of PKs."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            valid_block_types = BlockType.objects.filter(pk__in=block_types)
            if valid_block_types.count() < len(block_types):
                return Response(
                    {'error': "At least one pk in valid_block_types is invalid."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            document.valid_block_types.set(valid_block_types)

        # save the document and return it in the response data
        document.save()
        serializer = self.get_serializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def bulk_move_parts(self, request, pk=None):
        # move multiple parts
        data = request.data
        # we pass parts in POST data since this is on a Document
        part_pks = data.pop("parts")
        parts = DocumentPart.objects.filter(document=pk, pk__in=part_pks).order_by("order")
        serializer = PartBulkMoveSerializer(parts=parts, data=data)
        if serializer.is_valid() and parts.count():
            serializer.bulk_move()
            return Response({'status': 'moved'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        document = self.get_object()
        if 'group' in request.data:
            try:
                target = (Group.objects
                          .filter(user=request.user)
                          .get(pk=request.data['group']))
            except Group.DoesNotExist:
                return Response({'error': 'invalid group.'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                document.shared_with_groups.add(target)
        elif 'user' in request.data:
            try:
                target = User.objects.get(username=request.data['user'])
            except User.DoesNotExist:
                return Response({'error': 'invalid username.'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                document.shared_with_users.add(target)
        else:
            return Response({'error': 'Please provide either a group(pk) or user(username).'},
                            status=status.HTTP_400_BAD_REQUEST)

        # re-instantiate serializer to use updated data
        serializer = DocumentSerializer(document, context={'user': request.user})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @method_decorator(cache_page(60 * 60))  # one hour
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        document = self.get_object()
        order_param = self.request.query_params.get('ordering')

        if order_param in ['frequency', '-frequency']:
            order_by = order_param
        elif order_param in ['typology', '-typology']:
            order_by = order_param + '__name'
        else:
            order_by = '-frequency'

        regions = (Block.objects
                   .filter(document_part__document=document)
                   .values('typology_id')
                   .annotate(typology_name=F('typology__name'),
                             frequency=Count('*'))
                   .order_by(order_by))

        lines = (Line.objects
                 .filter(document_part__document=document)
                 .values('typology_id')
                 .annotate(typology_name=F('typology__name'),
                           frequency=Count('*'))
                 .order_by(order_by))

        if order_param in ['typology', '-typology']:
            order_by = '-frequency'
        elif order_param in ['taxonomy', '-taxonomy']:
            order_by = order_param + '__name'

        text_annotations = (TextAnnotation.objects
                            .filter(part__document=document)
                            .values('taxonomy_id')
                            .annotate(taxonomy_name=F('taxonomy__name'),
                                      frequency=Count('*'))
                            .order_by(order_by))

        img_annotations = (ImageAnnotation.objects
                           .filter(part__document=document)
                           .values('taxonomy_id')
                           .annotate(taxonomy_name=F('taxonomy__name'),
                                     frequency=Count('*'))
                           .order_by(order_by))

        return Response({
            'regions': regions,
            'lines': lines,
            'image_annotations': img_annotations,
            'text_annotations': text_annotations
        })


class TaskGroupViewSet(ModelViewSet):
    queryset = TaskGroup.objects.all().select_related('created_by')
    serializer_class = TaskGroupSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(document=self.kwargs.get('document_pk'))
        return qs


class TaskReportViewSet(ModelViewSet):
    queryset = TaskReport.objects.all()
    serializer_class = TaskReportSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'group']
    ordering_fields = ['queued_at', 'started_at', 'done_at']
    ordering = ['-queued_at', '-started_at', '-done_at']

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        return qs


class DocumentPermissionMixin():
    def get_queryset(self):
        try:
            self.document = (Document.objects
                             .for_user(self.request.user)
                             .get(pk=self.kwargs.get('document_pk')))
        except Document.DoesNotExist:
            raise PermissionDenied

        return super().get_queryset()


class DocumentMetadataViewSet(DocumentPermissionMixin, ModelViewSet):
    queryset = DocumentMetadata.objects.all().select_related('document')
    serializer_class = DocumentMetadataSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(document=self.kwargs.get('document_pk'))
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['document'] = Document.objects.get(pk=self.kwargs.get('document_pk'))
        return context


class PartMetadataViewSet(DocumentPermissionMixin, ModelViewSet):
    queryset = DocumentPartMetadata.objects.all().select_related('part')
    serializer_class = DocumentPartMetadataSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(part=self.kwargs.get('part_pk'))
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['part'] = DocumentPart.objects.get(pk=self.kwargs.get('part_pk'))
        return context


class ImportViewSet(DocumentPermissionMixin, GenericViewSet, CreateModelMixin):
    queryset = DocumentPart.objects.all()
    serializer_class = ImportSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['document'] = Document.objects.get(pk=self.kwargs.get('document_pk'))
        return context

    def create(self, request, document_pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.process()
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)


class PartViewSet(DocumentPermissionMixin, ModelViewSet):
    filter_backends = (OrderingFilter,)
    queryset = DocumentPart.objects.all().select_related('document')
    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(document=self.kwargs.get('document_pk'))
        if self.action == 'retrieve':
            return qs.prefetch_related('lines', 'blocks', 'metadata')
        else:
            return qs

    def get_serializer_class(self):
        # different serializer because we don't want to query all the lines in the list view
        if self.action == 'retrieve':
            return PartDetailSerializer
        else:  # list & create
            return PartSerializer
    
    def get_serializer_context(self):
        """העברת transcription_id מה-query params ל-serializer context"""
        context = super().get_serializer_context()
        transcription_id = self.request.query_params.get('transcription')
        if transcription_id:
            try:
                context['transcription_id'] = int(transcription_id)
            except ValueError:
                pass
        return context

    @action(detail=False, methods=['get'])
    def byorder(self, request, document_pk=None):
        try:
            order = int(request.GET.get('order'))
        except ValueError:
            return Response({'error': 'invalid order.'})
        except TypeError:
            return Response({'error': 'pass order as an url parameter.'})
        try:
            part = self.get_queryset().get(order=order)
        except DocumentPart.DoesNotExist:
            return Response({'error': 'Out of bounds.'})
        return HttpResponseRedirect(reverse('api:part-detail',
                                            kwargs={'document_pk': self.kwargs.get('document_pk'),
                                                    'pk': part.pk}))

    @action(detail=True, methods=['post'])
    def move(self, request, document_pk=None, pk=None):
        part = DocumentPart.objects.get(document=document_pk, pk=pk)
        serializer = PartMoveSerializer(part=part, data=request.data)
        if serializer.is_valid():
            serializer.move()
            return Response({'status': 'moved'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, document_pk=None, pk=None):
        part = DocumentPart.objects.get(document=document_pk, pk=pk)
        part.cancel_tasks(username=self.request.user.username)
        part.refresh_from_db()
        return Response({'status': 'canceled', 'workflow': part.workflow})

    @action(detail=True, methods=['post'])
    def reset_masks(self, request, document_pk=None, pk=None):
        # If quotas are enforced, assert that the user still has free CPU minutes
        if not settings.DISABLE_QUOTAS and not request.user.has_free_cpu_minutes():
            return Response({'error': "You don't have any CPU minutes left."}, status=status.HTTP_400_BAD_REQUEST)
        part = DocumentPart.objects.get(document=document_pk, pk=pk)
        onlyParam = request.query_params.get("only")
        only = onlyParam and list(map(int, onlyParam.split(',')))
        recalculate_masks.delay(instance_pk=part.pk, user_pk=request.user.pk, only=only)
        return Response({'status': 'ok'})

    @action(detail=True, methods=['post'])
    def recalculate_ordering(self, request, document_pk=None, pk=None):
        document_part = DocumentPart.objects.get(pk=pk)
        document_part.recalculate_ordering()
        serializer = LineOrderSerializer(document_part.lines.all(), many=True)
        return Response({'status': 'done', 'lines': serializer.data}, status=200)

    @action(detail=True, methods=['post'])
    def rotate(self, request, document_pk=None, pk=None):
        document_part = DocumentPart.objects.get(pk=pk)
        angle = self.request.data.get('angle')
        if angle:
            document_part.rotate(angle, user=self.request.user)
            return Response({'status': 'done'}, status=200)
        else:
            return Response({'error': "Post an angle."},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def crop(self, request, document_pk=None, pk=None):
        document_part = DocumentPart.objects.get(pk=pk)
        x1 = self.request.data.get('x1')
        y1 = self.request.data.get('y1')
        x2 = self.request.data.get('x2')
        y2 = self.request.data.get('y2')
        if (x1 is not None
            and y1 is not None
            and x2 is not None
                and y2 is not None):
            document_part.crop(x1, y1, x2, y2)
            return Response({'status': 'done'}, status=200)
        else:
            return Response({'error': "Post corners as x1, y1 (top left) and x2, y2 (bottom right)."},
                            status=status.HTTP_400_BAD_REQUEST)


class DocumentTranscriptionViewSet(DocumentPermissionMixin, ModelViewSet):
    # Note: there is no dedicated Transcription viewset, it's always in the context of a Document
    queryset = Transcription.objects.all()
    serializer_class = TranscriptionSerializer
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(
            archived=False,
            document=self.document)
        return qs

    def destroy(self, request, *args, **kwargs):
        try:
            self.get_object().archive()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedObjectException:
            return Response("This transcription can not be deleted.", status=400)

    def characters_query(self, transcription, order_param):
        # Security: Use strict whitelist for ORDER BY clause to prevent SQL injection
        # Only allow predefined safe values
        ALLOWED_ORDER_BY = {
            'frequency': "frequency ASC",
            'char': "char ASC",
            '-char': "char DESC",
            '-frequency': "frequency DESC",  # default case
        }
        order_by = ALLOWED_ORDER_BY.get(order_param, "frequency DESC")

        # Security: Using f-string with whitelisted value (not user input)
        # order_by is guaranteed to be one of 4 safe values from ALLOWED_ORDER_BY dict
        # SQL injection is prevented by strict whitelist - not vulnerable despite B608 warning
        query = (  # nosec B608
            f"SELECT char, count(*) as frequency "  # nosec B608
            f"FROM \"core_linetranscription\", regexp_split_to_table(content, '') t(char), core_line, core_documentpart "
            f"WHERE \"core_linetranscription\".\"line_id\" = \"core_line\".\"id\" "
            f"AND \"core_line\".\"document_part_id\" = \"core_documentpart\".\"id\" "
            f"AND (\"core_documentpart\".\"document_id\" = %s AND \"core_linetranscription\".\"transcription_id\" = %s) "
            f"GROUP BY char ORDER BY {order_by};"
        )
        
        with connection.cursor() as cursor:
            # Security: SQL injection prevented by ALLOWED_ORDER_BY whitelist above
            # order_by can only be one of 4 hardcoded safe values
            cursor.execute(query, [self.document.pk, transcription.pk])  # nosec B608
            all_ = cursor.fetchall()
            data = [{'char': char, 'frequency': freq} for char, freq in all_]

        return data

    @method_decorator(cache_page(60 * 60))  # one hour
    @action(detail=True, methods=['GET'])
    def stats(self, request, document_pk=None, pk=None):
        transcription = self.get_object()
        # Note: we don't have access to OrderingFilter goodies in an @action
        order_param = self.request.query_params.get('ordering')
        chars = self.characters_query(transcription, order_param)
        line_count = transcription.linetranscription_set.exclude(content='').count()

        return Response({
            'line_count': line_count,
            'characters': chars
        })


class TypologyViewSet(ModelViewSet):
    def get_queryset(self):
        qs = super().get_queryset()
        # POST queryset should be all()
        if self.request.method == "GET":
            # GET queryset should be only public types
            return qs.filter(public=True)
        elif self.request.method in ["PUT", "PATCH", "DELETE"]:
            # PUT/PATCH/DELETE (updating and deleting) require permissions
            return qs.filter(
                Q(valid_in__owner=self.request.user)
                | Q(valid_in__shared_with_users=self.request.user)
                | Q(valid_in__shared_with_groups__user=self.request.user)
                | Q(valid_in__project__owner=self.request.user)
                | Q(valid_in__project__shared_with_users=self.request.user)
            ).distinct()
        return qs


class BlockTypeViewSet(TypologyViewSet):
    queryset = BlockType.objects.all()
    serializer_class = BlockTypeSerializer


class LineTypeViewSet(TypologyViewSet):
    queryset = LineType.objects.all()
    serializer_class = LineTypeSerializer


class AnnotationTypeViewSet(TypologyViewSet):
    queryset = AnnotationType.objects.all()
    serializer_class = AnnotationTypeSerializer


class DocumentPartTypeViewSet(TypologyViewSet):
    queryset = DocumentPartType.objects.all()
    serializer_class = DocumentPartTypeSerializer


class AnnotationComponentViewSet(DocumentPermissionMixin, ModelViewSet):
    queryset = AnnotationComponent.objects.all()
    serializer_class = AnnotationComponentSerializer

    def get_queryset(self):
        return super().get_queryset().filter(document=self.document)


class AnnotationTaxonomyViewSet(DocumentPermissionMixin, ModelViewSet):
    queryset = AnnotationTaxonomy.objects.all()
    serializer_class = AnnotationTaxonomySerializer

    def get_queryset(self):
        qs = (super().get_queryset()
              .filter(document=self.document)
              .prefetch_related('typology', 'components'))
        target = self.request.query_params.get('target')
        if target == 'image':
            return qs.filter(
                marker_type__in=[c[0] for c in AnnotationTaxonomy.IMG_MARKER_TYPE_CHOICES])
        elif target == 'text':
            return qs.filter(
                marker_type__in=[c[0] for c in AnnotationTaxonomy.TEXT_MARKER_TYPE_CHOICES])
        else:
            return qs


class ImageAnnotationViewSet(DocumentPermissionMixin, ModelViewSet):
    queryset = ImageAnnotation.objects.all()
    serializer_class = ImageAnnotationSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        return (super().get_queryset()
                .filter(part=self.kwargs['part_pk'])
                .filter(part__document=self.kwargs['document_pk']))


class TextAnnotationViewSet(DocumentPermissionMixin, ModelViewSet):
    queryset = TextAnnotation.objects.all()
    serializer_class = TextAnnotationSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        qs = (super().get_queryset()
              .filter(part=self.kwargs['part_pk'])
              .filter(part__document=self.kwargs['document_pk']))
        try:
            transcription = int(self.request.GET.get('transcription'))
        except (ValueError, TypeError):
            pass
        else:
            qs = qs.filter(transcription=transcription)
        return qs


class BlockViewSet(DocumentPermissionMixin, ModelViewSet):
    queryset = Block.objects.select_related('typology')
    serializer_class = BlockSerializer

    def get_queryset(self):
        return (super().get_queryset()
                .filter(document_part=self.kwargs['part_pk'])
                .filter(document_part__document=self.kwargs['document_pk']))


class LineViewSet(DocumentPermissionMixin, ModelViewSet):
    queryset = (Line.objects.select_related('block')
                            .select_related('typology'))

    def get_queryset(self):
        return (super().get_queryset()
                .filter(document_part=self.kwargs['part_pk'])
                .filter(document_part__document=self.kwargs['document_pk']))

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DetailedLineSerializer
        else:  # create, list
            return LineSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DetailedLineSerializer(instance)
        json = serializer.data
        super().destroy(request, *args, **kwargs)
        return Response(status=200, data=json)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def bulk_create(self, request, document_pk=None, part_pk=None):
        lines = request.data.get("lines")

        response_json = self._bulk_create_helper(lines)
        return Response({'status': 'ok', 'lines': response_json})

    def _bulk_create_helper(self, lines):
        # Performs the actual creation, called from two endpoints

        # We create the lines in two parts - first the lines, then their transcriptions.
        # We can't used the DetailedLineSerializer, since the Transcription serializer requires a line property,
        # which is unknown at this time - the line has not been created yet.
        # We may want to move this code into the DetailedLineSerializer's create method at some point.
        serializer = LineSerializer(data=lines, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Now we go over the lines retrieved from the request, take their transcriptions, and add the right line PK to each one.
        # serializer.data is ordered, in the same order as lines
        if len(lines) != len(serializer.data):
            raise ValueError(f"LineSerializer created {len(serializer.data)} lines, while {len(lines)} were expected")

        transcriptions = []
        line_pks = []
        for i in range(len(lines)):
            pk = serializer.data[i]['pk']
            line_transcriptions = lines[i].get('transcriptions', [])
            for lt in line_transcriptions:
                lt['line'] = pk
            transcriptions += line_transcriptions
            line_pks.append(pk)

        serializer = LineTranscriptionSerializer(data=transcriptions, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Finally, for a response, we want to create all the newly created lines along with their transcriptions.
        # Simplest way to do this - just use the PKs to load the lines again
        qs = Line.objects.filter(pk__in=line_pks)
        serializer = DetailedLineSerializer(qs, many=True)
        return serializer.data

    @action(detail=False, methods=['put'])
    def bulk_update(self, request, document_pk=None, part_pk=None):
        lines = request.data.get("lines")
        qs = self.get_queryset().filter(pk__in=[line['pk'] for line in lines])
        serializer = LineSerializer(qs, data=lines, partial=True, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'ok', 'lines': serializer.data}, status=200)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request, document_pk=None, part_pk=None):
        deleted_lines = request.data.get("lines")
        qs = Line.objects.filter(pk__in=deleted_lines)
        serializer = DetailedLineSerializer(qs, many=True)
        json = serializer.data
        qs.delete()
        return Response({'status': 'ok', 'lines': json}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def merge(self, request, document_pk=None, part_pk=None):
        original_lines = request.data.get("lines")

        if not original_lines:
            return Response({'status': 'error', 'error': _("'lines' is mandatory.")}, status=status.HTTP_400_BAD_REQUEST)

        if len(original_lines) > MAX_MERGE_SIZE:
            return Response(dict(status='error', error=f"Can't merge more than {MAX_MERGE_SIZE} lines"), status=status.HTTP_400_BAD_REQUEST)

        lines = list(Line.objects.filter(pk__in=original_lines))
        for line in lines:
            if not line.baseline:
                return Response(dict(status='error', error="Lines without a baseline cannot be merged"), status=status.HTTP_400_BAD_REQUEST)

        original_serializer = DetailedLineSerializer(lines, many=True)
        deleted_json = original_serializer.data

        merged_line_json = merge_lines(lines)
        created_json = self._bulk_create_helper([merged_line_json])
        for line in lines:
            line.delete()

        response_json = dict(created=created_json[0], deleted=deleted_json)
        return Response(dict(status='ok', lines=response_json), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def move(self, request, document_pk=None, part_pk=None, pk=None):
        data = request.data.get('lines')
        qs = Line.objects.filter(pk__in=[line['pk'] for line in data])
        serializer = LineOrderSerializer(qs, data=data, many=True)
        if serializer.is_valid():
            resp = serializer.save()
            return Response(resp, status=200)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LineTranscriptionViewSet(DocumentPermissionMixin, ModelViewSet):
    queryset = LineTranscription.objects.all()
    serializer_class = LineTranscriptionSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        qs = (super().get_queryset()
              .filter(line__document_part=self.kwargs['part_pk'])
              .filter(line__document_part__document=self.kwargs['document_pk'])
              .select_related('line', 'transcription')
              .order_by('line__order', 'id'))
        transcription = self.request.GET.get('transcription')
        if transcription:
            qs = qs.filter(transcription=transcription)
        return qs

    def create(self, request, document_pk=None, part_pk=None):
        response = super().create(request, document_pk=document_pk, part_pk=part_pk)
        document_part = DocumentPart.objects.get(pk=part_pk)
        document_part.calculate_progress()
        document_part.save()
        return response

    def perform_create(self, serializer):
        serializer.save(version_author=self.request.user.username)

    def update(self, request, document_pk=None, part_pk=None, pk=None, partial=False):
        instance = self.get_object()
        try:
            instance.new_version(author=request.user.username,
                                 source=settings.VERSIONING_DEFAULT_SOURCE)
        except NoChangeException:
            # Note we can safely pass here
            pass

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_serializer_class(self):
        lines = Line.objects.filter(document_part=self.kwargs['part_pk'])

        class RuntimeSerializer(self.serializer_class):
            line = PrimaryKeyRelatedField(queryset=lines)
        return RuntimeSerializer

    @action(detail=False, methods=['POST'])
    def bulk_create(self, request, document_pk=None, part_pk=None, pk=None):
        lines = request.data.get("lines")
        serializer = LineTranscriptionSerializer(data=lines, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'status': 'ok', 'lines': serializer.data}, status=200)

    @action(detail=False, methods=['PUT'])
    def bulk_update(self, request, document_pk=None, part_pk=None, pk=None):
        lines = request.data.get('lines')
        response = []
        errors = []
        for line in lines:
            lt = get_object_or_404(LineTranscription, pk=line["pk"])
            serializer = LineTranscriptionSerializer(lt, data=line, partial=True)

            if serializer.is_valid():
                try:
                    lt.new_version(author=request.user.username,
                                   source=settings.VERSIONING_DEFAULT_SOURCE)
                except NoChangeException:
                    pass

                serializer.save()
                response.append(serializer.data)

            else:
                errors.append(serializer.errors)

        if errors:
            return Response(errors,
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(status=200, data=response)

    @action(detail=False, methods=['POST'])
    def bulk_delete(self, request, document_pk=None, part_pk=None, pk=None):
        lines = request.data.get("lines")
        qs = LineTranscription.objects.filter(pk__in=lines)
        qs.update(content='')
        return Response(status=status.HTTP_204_NO_CONTENT, )


class OcrModelViewSet(ModelViewSet):
    queryset = OcrModel.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['documents', 'job']
    serializer_class = OcrModelSerializer

    def get_queryset(self):
        return (super().get_queryset()
                .filter(Q(owner=self.request.user)
                        | Q(ocr_model_rights__user=self.request.user)
                        | Q(ocr_model_rights__group__user=self.request.user))
                .distinct()
                )

    @action(detail=True, methods=['post'])
    def cancel_training(self, request, pk=None):
        model = self.get_object()
        try:
            model.cancel_training(username=request.user.username)
        except Exception as e:
            logger.exception(e)
            return Response({'status': 'failed'}, status=400)
        return Response({'status': 'canceled'})


class RegenerableAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        if not created and request.data.get('regenerate'):
            token.delete()
            token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key})


# ============================================================================
# 🔍 Elasticsearch Search ViewSet
# Created: 20 אוקטובר 2025
# ============================================================================

class SearchViewSet(GenericViewSet):
    """
    ViewSet לחיפוש מתקדם באמצעות Elasticsearch
    
    Endpoints:
    - GET /api/search/?q=query - חיפוש בסיסי
    - GET /api/search/?q=query&document=123 - חיפוש במסמך ספציפי
    - GET /api/search/?q=query&project=456 - חיפוש בפרויקט ספציפי
    - GET /api/search/stats/ - סטטיסטיקות ES
    """
    
    permission_classes = [BasePermission]
    
    def list(self, request):
        """
        חיפוש עם פרמטרים:
        - q: מחרוזת חיפוש (required)
        - document: ID של מסמך (optional)
        - project: ID של פרויקט (optional)
        - min_confidence: סף ביטחון מינימלי (optional)
        - page: מספר עמוד (default: 1)
        - page_size: גודל עמוד (default: 20)
        """
        from core.search import get_es_service
        
        query = request.query_params.get('q', '')
        document_id = request.query_params.get('document')
        project_id = request.query_params.get('project')
        min_confidence = request.query_params.get('min_confidence')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # המר לint אם ניתן
        try:
            document_id = int(document_id) if document_id else None
            project_id = int(project_id) if project_id else None
            min_confidence = float(min_confidence) if min_confidence else None
        except ValueError:
            return Response(
                {"error": "Invalid parameter format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # חיפוש
        es_service = get_es_service()
        results = es_service.search_advanced(
            query=query,
            document_id=document_id,
            project_id=project_id,
            min_confidence=min_confidence,
            page=page,
            page_size=page_size
        )
        
        # בדוק שגיאות
        if 'error' in results:
            return Response(results, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response(results)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        קבל סטטיסטיקות Elasticsearch
        GET /api/search/stats/
        """
        from core.search import get_es_service
        
        es_service = get_es_service()
        stats = es_service.get_stats()
        
        return Response(stats)


# ============================================================================
# Task Status & Progress Tracking API
# ============================================================================

class TaskStatusView(APIView):
    """
    API endpoint לבדיקת סטטוס task ספציפי
    
    GET /api/tasks/{task_id}/status/
    
    Returns:
        - task_id: מזהה Task
        - method: סוג המשימה
        - state: סטטוס (Queued/Running/Done/Error)
        - progress: אחוזי התקדמות (0-100)
        - messages: הודעות מהמשימה
        - started_at: זמן התחלה
        - done_at: זמן סיום (אם הסתיים)
        - document: מסמך קשור
        - user: משתמש שהריץ
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        try:
            task = TaskReport.objects.select_related(
                'user', 'document', 'document_part', 'ocr_model'
            ).get(pk=task_id)
        except TaskReport.DoesNotExist:
            return Response(
                {"error": "Task not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # בדיקת הרשאות - רק בעלים או admin
        if task.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "Permission denied"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # חישוב estimated completion (אם רץ)
        estimated_completion = None
        if task.workflow_state == TaskReport.WORKFLOW_STATE_STARTED:
            from datetime import timedelta
            from django.utils import timezone
            
            if task.started_at:
                elapsed = (timezone.now() - task.started_at).total_seconds()
                # אם יש progress, נחשב estimated completion
                # Note: לא כל tasks יש להם progress field, רק חלקם
                # אז נשתמש בזמן ממוצע במקום
                avg_task_duration = 300  # 5 דקות כדיפולט
                remaining = max(0, avg_task_duration - elapsed)
                if remaining > 0:
                    estimated_completion = timezone.now() + timedelta(seconds=remaining)
        
        response_data = {
            "task_id": task.pk,
            "method": task.method,
            "state": task.get_workflow_state_display(),
            "state_code": task.workflow_state,
            "label": task.label,
            "messages": task.messages,
            "queued_at": task.queued_at.isoformat() if task.queued_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "done_at": task.done_at.isoformat() if task.done_at else None,
            "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
            "document": {
                "id": task.document.pk,
                "name": task.document.name
            } if task.document else None,
            "document_part": {
                "id": task.document_part.pk,
                "name": str(task.document_part)
            } if task.document_part else None,
            "user": task.user.username if task.user else None,
            "ocr_model": {
                "id": task.ocr_model.pk,
                "name": task.ocr_model.name
            } if task.ocr_model else None,
            "cpu_cost": float(task.cpu_cost) if task.cpu_cost else None,
            "gpu_cost": float(task.gpu_cost) if task.gpu_cost else None
        }
        
        return Response(response_data)


class TaskListView(APIView):
    """
    API endpoint לרשימת tasks
    
    GET /api/tasks/?document_id=4&state=running
    
    Query params:
        - document_id: סינון לפי מסמך
        - state: סינון לפי סטטוס (queued/running/done/error)
        - method: סינון לפי סוג משימה
        - limit: מספר תוצאות מקסימלי (default: 50)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # התחל עם tasks של המשתמש
        queryset = TaskReport.objects.filter(
            user=request.user
        ).select_related('document', 'document_part', 'ocr_model').order_by('-queued_at')
        
        # סינונים
        document_id = request.query_params.get('document_id')
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        
        state = request.query_params.get('state')
        if state:
            state_map = {
                'queued': TaskReport.WORKFLOW_STATE_QUEUED,
                'running': TaskReport.WORKFLOW_STATE_STARTED,
                'done': TaskReport.WORKFLOW_STATE_DONE,
                'error': TaskReport.WORKFLOW_STATE_ERROR
            }
            if state in state_map:
                queryset = queryset.filter(workflow_state=state_map[state])
        
        method = request.query_params.get('method')
        if method:
            queryset = queryset.filter(method__icontains=method)
        
        # Limit
        limit = int(request.query_params.get('limit', 50))
        queryset = queryset[:limit]
        
        # Statistics
        all_tasks = TaskReport.objects.filter(user=request.user)
        stats = {
            'total': all_tasks.count(),
            'active': all_tasks.filter(
                workflow_state=TaskReport.WORKFLOW_STATE_STARTED
            ).count(),
            'queued': all_tasks.filter(
                workflow_state=TaskReport.WORKFLOW_STATE_QUEUED
            ).count(),
            'completed': all_tasks.filter(
                workflow_state=TaskReport.WORKFLOW_STATE_DONE
            ).count(),
            'failed': all_tasks.filter(
                workflow_state=TaskReport.WORKFLOW_STATE_ERROR
            ).count()
        }
        
        # Build response
        tasks = []
        for task in queryset:
            tasks.append({
                "task_id": task.pk,
                "method": task.method,
                "label": task.label,
                "state": task.get_workflow_state_display(),
                "state_code": task.workflow_state,
                "queued_at": task.queued_at.isoformat() if task.queued_at else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "done_at": task.done_at.isoformat() if task.done_at else None,
                "document": {
                    "id": task.document.pk,
                    "name": task.document.name
                } if task.document else None
            })
        
        return Response({
            "tasks": tasks,
            "statistics": stats,
            "count": len(tasks)
        })


class ImportProgressView(APIView):
    """
    API endpoint למעקב אחר התקדמות ייבוא
    
    GET /api/imports/{import_id}/status/
    
    Returns:
        - import_id: מזהה Import
        - workflow_state: סטטוס (created/started/done/error)
        - total_files: סך הכל קבצים
        - processed_files: כמה כבר עובדו
        - progress_percent: אחוזים
        - messages: הודעות שגיאה/אזהרות
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, import_id):
        try:
            doc_import = DocumentImport.objects.select_related(
                'document', 'document__owner'
            ).get(pk=import_id)
        except DocumentImport.DoesNotExist:
            return Response(
                {"error": "Import not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # בדיקת הרשאות
        if doc_import.document.owner != request.user and not request.user.is_staff:
            return Response(
                {"error": "Permission denied"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # חישוב progress
        total_files = doc_import.total if doc_import.total else 0
        processed_files = doc_import.processed if doc_import.processed else 0
        progress_percent = (processed_files / total_files * 100) if total_files > 0 else 0
        
        # ספירת failures ו-messages
        messages = []
        if doc_import.report:
            if doc_import.report.messages:
                messages = [msg.strip() for msg in doc_import.report.messages.split('\n') if msg.strip()]
        
        # חישוב estimated completion
        estimated_completion = None
        if doc_import.workflow_state == DocumentImport.WORKFLOW_STATE_STARTED:
            if doc_import.report and doc_import.report.started_at and processed_files > 0:
                from datetime import timedelta
                from django.utils import timezone
                
                elapsed = (timezone.now() - doc_import.report.started_at).total_seconds()
                if processed_files > 0:
                    avg_time_per_file = elapsed / processed_files
                    remaining_files = total_files - processed_files
                    remaining_seconds = avg_time_per_file * remaining_files
                    estimated_completion = timezone.now() + timedelta(seconds=remaining_seconds)
        
        response_data = {
            "import_id": doc_import.pk,
            "document_id": doc_import.document.pk,
            "document_name": doc_import.document.name,
            "workflow_state": doc_import.get_workflow_state_display(),
            "workflow_state_code": doc_import.workflow_state,
            "total_files": total_files,
            "processed_files": processed_files,
            "progress_percent": round(progress_percent, 1),
            "messages": messages,
            "started_at": doc_import.report.started_at.isoformat() if (
                doc_import.report and doc_import.report.started_at
            ) else None,
            "completed_at": doc_import.report.done_at.isoformat() if (
                doc_import.report and doc_import.report.done_at
            ) else None,
            "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
            "import_file": doc_import.import_file.name if doc_import.import_file else None
        }
        
        return Response(response_data)


class ImportListView(APIView):
    """
    API endpoint לרשימת imports
    
    GET /api/imports/?document_id=7
    
    Query params:
        - document_id: סינון לפי מסמך (optional)
        - state: סינון לפי workflow_state (optional)
        - limit: מספר תוצאות מקסימלי (default: 50)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # התחל עם imports נגישים למשתמש
        queryset = DocumentImport.objects.select_related(
            'document', 'document__owner', 'report'
        ).filter(
            Q(document__owner=request.user) | Q(document__shared_with_users=request.user)
        ).order_by('-started_on')
        
        # סינונים
        document_id = request.query_params.get('document_id')
        if document_id:
            try:
                queryset = queryset.filter(document_id=int(document_id))
            except ValueError:
                return Response(
                    {"error": "Invalid document_id"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        state = request.query_params.get('state')
        if state:
            queryset = queryset.filter(workflow_state=state)
        
        # Limit
        limit = int(request.query_params.get('limit', 50))
        queryset = queryset[:limit]
        
        # בניית תוצאות
        results = []
        for doc_import in queryset:
            total = doc_import.total if doc_import.total else 0
            processed = doc_import.processed if doc_import.processed else 0
            progress = (processed / total * 100) if total > 0 else 0
            
            results.append({
                "pk": doc_import.pk,
                "document_id": doc_import.document.pk,
                "document_name": doc_import.document.name,
                "name": doc_import.name,
                "workflow_state": doc_import.get_workflow_state_display(),
                "workflow_state_code": doc_import.workflow_state,
                "total": total,
                "processed": processed,
                "progress_percent": round(progress, 1),
                "import_started": doc_import.report.started_at is not None if doc_import.report else False,
                "started_on": doc_import.started_on.isoformat() if doc_import.started_on else None,
                "upload_file": None,  # DocumentImport doesn't have upload_file
                "override": doc_import.override,
            })
        
        return Response({
            "count": len(results),
            "results": results
        })


class TaskGroupDetailView(RetrieveAPIView):
    """
    Get detailed, enhanced status of a task group including all tasks
    
    GET /api/tasks/group/{id}/
    
    Returns rich response with:
    - Progress indicators with icons
    - Human-readable status messages  
    - Next steps and recommendations
    - Detailed task breakdown
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskGroupSerializer
    queryset = TaskGroup.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Use enhanced response generator
        data = ResponseEnhancer.task_group_status(instance, include_details=True)
        return Response(data)


class TaskReportListView(ListAPIView):
    """
    List task reports with filtering by document, method, and workflow_state
    
    GET /api/tasks/?document_id=7&method=core.tasks.segtrain&workflow_state=1
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskReportSerializer
    filterset_fields = ['document_id', 'method', 'workflow_state', 'user']
    ordering_fields = ['queued_at', 'started_at', 'done_at']
    ordering = ['-queued_at']
    
    def get_queryset(self):
        return TaskReport.objects.select_related('document', 'user').all()


class OcrModelStatusView(RetrieveAPIView):
    """
    Get detailed, enhanced status of a training model
    
    GET /api/models/{id}/status/
    
    Returns rich response with:
    - Training status with visual indicators
    - Model capabilities and readiness
    - Trained documents history
    - Next steps and usage recommendations
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OcrModelStatusSerializer
    queryset = OcrModel.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Use enhanced response generator
        data = ResponseEnhancer.model_status(instance)
        return Response(data)


class DocumentLanguageDetectionView(APIView):
    """
    Detect document language/script and recommend OCR model
    
    GET /api/documents/{document_id}/detect-language/
    
    Auto-detects the primary script (Hebrew, Arabic, Latin, etc.) from
    existing transcriptions and provides OCR model recommendations.
    
    Returns:
        {
            "script": "hebrew",
            "direction": "rtl",
            "confidence": 0.95,
            "has_nikud": true,
            "has_teamim": false,
            "has_tashkeel": false,
            "recommended_engine": "kraken",
            "model_hint": "hebrew_best.mlmodel",
            "preprocessing": ["binarization", "deskew", "despeckle"],
            "sample_text": "שלום עולם...",
            "statistics": {
                "hebrew": 45,
                "arabic": 0,
                "latin": 5,
                ...
            }
        }
    
    Query Parameters:
        - sample_size: Number of characters to analyze (default: 500)
        - auto_set_direction: Automatically update document read_direction (default: false)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, document_id):
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # בדיקת הרשאות - רק בעלים או admin
        if document.owner != request.user and not request.user.is_staff:
            # Check if user has access through project
            if not document.project.users.filter(pk=request.user.pk).exists():
                return Response(
                    {"error": "Permission denied"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get query parameters
        sample_size = int(request.query_params.get('sample_size', 500))
        auto_set_direction = request.query_params.get('auto_set_direction', 'false').lower() == 'true'
        
        # Run detection
        try:
            detection_result = document.detect_language_and_recommend_model(sample_size=sample_size)
            
            # Optionally auto-set direction
            if auto_set_direction:
                direction_changed = document.auto_detect_and_set_direction()
                detection_result['direction_auto_updated'] = direction_changed
            
            return Response(detection_result)
            
        except Exception as e:
            import traceback
            return Response(
                {
                    "error": "Language detection failed",
                    "details": str(e),
                    "traceback": traceback.format_exc() if settings.DEBUG else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
