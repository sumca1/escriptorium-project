import logging
import os
import os.path
import shutil
import tempfile
from collections import defaultdict
from itertools import groupby
from pathlib import Path
from typing import List

import numpy as np
from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F, Q
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.utils.translation import gettext as _
from easy_thumbnails.files import get_thumbnailer
from kraken.containers import BaselineLine, Region, Segmentation
from kraken.kraken import SEGMENTATION_DEFAULT_MODEL
from kraken.lib.arrow_dataset import build_binary_dataset
from kraken.lib.default_specs import RECOGNITION_HYPER_PARAMS, SEGMENTATION_HYPER_PARAMS
from kraken.lib.train import KrakenTrainer, RecognitionModel, SegmentationModel
from lightning.pytorch.callbacks import Callback

from core.search import (
    REGEX_SEARCH_MODE,
    WORD_BY_WORD_SEARCH_MODE,
    build_highlighted_replacement_psql,
    search_content_psql_regex,
    search_content_psql_word,
)

# DO NOT REMOVE THIS IMPORT, it will break celery tasks located in this file
from reporting.tasks import create_task_reporting  # noqa F401
from users.consumers import send_event

logger = logging.getLogger(__name__)
User = get_user_model()


class DidNotConverge(Exception):
    pass


# ============================================================================
# 🔧 Tesseract Training Support - Additional imports will be in function scope
# Note: tesserocr, BeautifulSoup4, and other Tesseract-specific imports
# are loaded inside train_tesseract() to avoid import errors when
# modified Tesseract is not yet installed.
# ============================================================================


def _chunks(lst, n):
    """Yield successive n-sized chunks from lst. If n<0 yields one chunk of whole list."""
    if n < 0:
        yield lst
    else:
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


@shared_task(autoretry_for=(MemoryError,), default_retry_delay=60)
def generate_part_thumbnails(instance_pk=None, user_pk=None, **kwargs):
    if not getattr(settings, 'THUMBNAIL_ENABLE', True):
        return

    try:
        DocumentPart = apps.get_model('core', 'DocumentPart')
        part = DocumentPart.objects.get(pk=instance_pk)
    except DocumentPart.DoesNotExist:
        logger.error('Trying to compress non-existent DocumentPart : %d', instance_pk)
        return

    aliases = {}
    thbnr = get_thumbnailer(part.image)
    for alias, config in settings.THUMBNAIL_ALIASES[''].items():
        aliases[alias] = thbnr.get_thumbnail(config).url
    return aliases


@shared_task(autoretry_for=(MemoryError,), default_retry_delay=3 * 60)
def convert(instance_pk=None, user_pk=None, **kwargs):
    if user_pk:
        try:
            user = User.objects.get(pk=user_pk)
            # If quotas are enforced, assert that the user still has free CPU minutes
            if not settings.DISABLE_QUOTAS and user.cpu_minutes_limit() is not None:
                assert user.has_free_cpu_minutes(), f"User {user.id} doesn't have any CPU minutes left"
        except User.DoesNotExist:
            user = None

    try:
        DocumentPart = apps.get_model('core', 'DocumentPart')
        part = DocumentPart.objects.get(pk=instance_pk)
    except DocumentPart.DoesNotExist:
        logger.error('Trying to convert non-existent DocumentPart : %d', instance_pk)
        return
    part.convert()


@shared_task(autoretry_for=(MemoryError,), default_retry_delay=5 * 60)
def lossless_compression(instance_pk=None, user_pk=None, **kwargs):
    if user_pk:
        try:
            user = User.objects.get(pk=user_pk)
            # If quotas are enforced, assert that the user still has free CPU minutes
            if not settings.DISABLE_QUOTAS and user.cpu_minutes_limit() is not None:
                assert user.has_free_cpu_minutes(), f"User {user.id} doesn't have any CPU minutes left"
        except User.DoesNotExist:
            user = None

    try:
        DocumentPart = apps.get_model('core', 'DocumentPart')
        part = DocumentPart.objects.get(pk=instance_pk)
    except DocumentPart.DoesNotExist:
        logger.error('Trying to compress non-existent DocumentPart : %d', instance_pk)
        return
    part.compress()


def make_recognition_segmentation(lines) -> List[Segmentation]:
    """
    Groups training data by image for optimized compilation and returns a list
    of Segmentation objects.
    """
    lines_by_img = defaultdict(list)
    for lt in lines:
        lines_by_img[lt['image']].append(BaselineLine(id='foo',
                                                      baseline=lt['baseline'],
                                                      boundary=lt['mask'],
                                                      text=lt['content']))
    segs = []
    for img, lines in lines_by_img.items():
        segs.append(Segmentation(text_direction='horizontal-lr',
                                 imagename=os.path.join(settings.MEDIA_ROOT, img),
                                 type='baselines',
                                 lines=lines,
                                 script_detection=False))
    return segs


def make_segmentation_training_data(parts) -> List[Segmentation]:
    """
    Converts eScriptorium data model to list of Segmentation objects.
    """
    segs = []
    for part in parts:
        blls = []
        for line in part.lines.only('baseline', 'typology'):
            if line.baseline:
                blls.append(BaselineLine(id='foo',
                                         baseline=line.baseline,
                                         boundary=line.mask,
                                         tags={'type': line.typology and line.typology.name or 'default'}))

        regions = {}
        for typo, regs in groupby(part.blocks.only('box',
                                                   'typology').order_by('typology'),
                                  key=lambda reg: reg.typology and reg.typology.name or 'default'):
            regions[typo] = [Region(id='bar',
                                    boundary=reg.box,
                                    tags={'type': 'typo'}) for reg in regs]

        segs.append(Segmentation(text_direction='horizontal-lr',
                                 imagename=part.image.path,
                                 type='baselines',
                                 lines=blls,
                                 regions=regions,
                                 script_detection=False))
    return segs


class FrontendFeedback(Callback):
    """
    Lightning callback that sends websocket messages to the front for feedback
    display.
    """
    def __init__(self, es_model, model_directory, document_pk, *args, **kwargs):
        self.es_model = es_model
        self.model_directory = model_directory
        self.document_pk = document_pk
        super().__init__(*args, **kwargs)

    def on_train_epoch_end(self, trainer, pl_module) -> None:
        self.es_model.refresh_from_db()
        self.es_model.training_epoch = trainer.current_epoch
        val_metric = float(trainer.logged_metrics['val_accuracy'])
        logger.info(f'Epoch {trainer.current_epoch} finished.')
        self.es_model.training_accuracy = val_metric
        # model.training_total = chars
        # model.training_errors = error
        relpath = os.path.relpath(self.model_directory, settings.MEDIA_ROOT)
        self.es_model.new_version(file=f'{relpath}/version_{trainer.current_epoch}.mlmodel')
        self.es_model.save()

        send_event('document', self.document_pk, "training:eval", {
            "id": self.es_model.pk,
            'versions': self.es_model.versions,
            'epoch': trainer.current_epoch,
            'accuracy': val_metric
            # 'chars': chars,
            # 'error': error
        })


def _to_ptl_device(device: str):
    if device in ['cpu', 'mps']:
        return device, 'auto'
    elif any([device.startswith(x) for x in ['tpu', 'cuda', 'hpu', 'ipu']]):
        dev, idx = device.split(':')
        if dev == 'cuda':
            dev = 'gpu'
        return dev, [int(idx)]
    raise Exception(f'Invalid device {device} specified')


@shared_task(autoretry_for=(MemoryError,), default_retry_delay=60 * 60)
def segtrain(model_pk=None, part_pks=[], document_pk=None, task_group_pk=None, user_pk=None, **kwargs):
    # # Note hack to circumvent AssertionError: daemonic processes are not allowed to have children
    from multiprocessing import current_process
    current_process().daemon = False

    if user_pk:
        try:
            user = User.objects.get(pk=user_pk)
            # If quotas are enforced, assert that the user still has free CPU minutes, GPU minutes and disk storage
            if not settings.DISABLE_QUOTAS:
                if user.cpu_minutes_limit() is not None:
                    assert user.has_free_cpu_minutes(), f"User {user.id} doesn't have any CPU minutes left"
                if user.gpu_minutes_limit() is not None:
                    assert user.has_free_gpu_minutes(), f"User {user.id} doesn't have any GPU minutes left"
                if user.disk_storage_limit() is not None:
                    assert user.has_free_disk_storage(), f"User {user.id} doesn't have any disk storage left"
        except User.DoesNotExist:
            user = None
    else:
        user = None

    Document = apps.get_model('core', 'Document')
    DocumentPart = apps.get_model('core', 'DocumentPart')
    OcrModel = apps.get_model('core', 'OcrModel')

    model = OcrModel.objects.get(pk=model_pk)

    try:
        load = model.file.path
    except ValueError:  # model is empty
        load = SEGMENTATION_DEFAULT_MODEL
        model.file = model.file.field.upload_to(model, slugify(model.name) + '.mlmodel')

    model_dir = os.path.join(settings.MEDIA_ROOT, os.path.split(model.file.path)[0])

    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    try:
        model.training = True
        model.save()
        send_event('document', document_pk, "training:start", {
            "id": model.pk,
        })
        qs = DocumentPart.objects.filter(pk__in=part_pks).prefetch_related('lines')

        ground_truth = list(qs)
        if ground_truth[0].document.line_offset == Document.LINE_OFFSET_TOPLINE:
            topline = True
        elif ground_truth[0].document.line_offset == Document.LINE_OFFSET_CENTERLINE:
            topline = None
        else:
            topline = False

        np.random.default_rng(241960353267317949653744176059648850006).shuffle(ground_truth)
        partition = max(1, int(len(ground_truth) / 10))

        training_data = make_segmentation_training_data(qs[partition:])
        evaluation_data = make_segmentation_training_data(qs[:partition])

        accelerator, device = _to_ptl_device(getattr(settings, 'KRAKEN_TRAINING_DEVICE', 'cpu'))

        LOAD_THREADS = getattr(settings, 'KRAKEN_TRAINING_LOAD_THREADS', 0)
        AMP_MODE = getattr(settings, 'KRAKEN_TRAINING_PRECISION', '32')

        logger.info(f'Starting segmentation training on {accelerator}/{device} '
                    f'(precision: {AMP_MODE}, workers: {LOAD_THREADS}) with '
                    f'{len(training_data)} files')

        kraken_model = SegmentationModel(SEGMENTATION_HYPER_PARAMS,
                                         output=os.path.join(model_dir, 'version'),
                                         # spec=spec,
                                         model=load,
                                         format_type=None,
                                         training_data=training_data,
                                         evaluation_data=evaluation_data,
                                         partition=partition,
                                         num_workers=LOAD_THREADS,
                                         load_hyper_parameters=True,
                                         # force_binarization=force_binarization,
                                         # suppress_regions=suppress_regions,
                                         # suppress_baselines=suppress_baselines,
                                         # valid_regions=valid_regions,
                                         # valid_baselines=valid_baselines,
                                         # merge_regions=merge_regions,
                                         # merge_baselines=merge_baselines,
                                         # bounding_regions=bounding_regions,
                                         resize='both',
                                         topline=topline)

        trainer = KrakenTrainer(accelerator=accelerator,
                                devices=device,
                                # max_epochs=2,
                                # min_epochs=5,
                                precision=AMP_MODE,
                                enable_summary=False,
                                enable_progress_bar=False,
                                val_check_interval=1.0,
                                callbacks=[FrontendFeedback(model, model_dir, document_pk)])

        trainer.fit(kraken_model)

        if kraken_model.best_epoch == -1:
            logger.info(f'Model {os.path.split(model.file.path)[0]} did not improve.')
            raise DidNotConverge

        best_version = os.path.join(model_dir, kraken_model.best_model)

        try:
            logger.info(f'Moving best model {best_version} (accuracy: {kraken_model.best_metric}) to {model.file.path}.')
            shutil.copy(best_version, model.file.path)  # os.path.join(model_dir, filename)
            model.training_accuracy = kraken_model.best_metric
        except FileNotFoundError:
            logger.info(f'Model {os.path.split(model.file.path)[0]} did not improve.')
            user.notify(_("Training didn't get better results than base model!"),
                        id="seg-no-gain-error", level='warning')
            shutil.copy(load, model.file.path)

    except DidNotConverge:
        send_event('document', ground_truth[0].document.pk, "training:error", {
            "id": model.pk,
        })
        user.notify(_("The model did not converge, probably because of lack of data."),
                    id="training-warning", level='warning')
        model.delete()

    except Exception as e:
        send_event('document', document_pk, "training:error", {
            "id": model.pk,
        })
        if user:
            user.notify(_("Something went wrong during the segmenter training process!"),
                        id="training-error", level='danger')
        logger.exception(e)
        raise e
    else:
        model.file_size = model.file.size

        if user:
            user.notify(_("Training finished!"),
                        id="training-success",
                        level='success')
    finally:
        model.training = False
        model.save()

        send_event('document', document_pk, "training:done", {
            "id": model.pk,
        })


@shared_task(bind=True, autoretry_for=(MemoryError,), default_retry_delay=60)
def segment(self, instance_pks, user_pk=None, model_pk=None, steps=None, text_direction=None, override=None, task_group_pk=None, **kwargs):
    """
    steps can be either 'regions', 'lines' or 'both'
    """
    DocumentPart = apps.get_model('core', 'DocumentPart')
    OcrModel = apps.get_model('core', 'OcrModel')

    # load model
    try:
        model = OcrModel.objects.get(pk=model_pk)
    except OcrModel.DoesNotExist:
        model = None

    # load user & quota‐check
    user = None
    if user_pk:
        try:
            user = User.objects.get(pk=user_pk)
            if not settings.DISABLE_QUOTAS and user.cpu_minutes_limit() is not None:
                assert user.has_free_cpu_minutes(), f"User {user.id} doesn't have any CPU minutes left"
        except User.DoesNotExist:
            user = None

    for pk in instance_pks:
        # fetch part
        try:
            part = DocumentPart.objects.get(pk=pk)
        except DocumentPart.DoesNotExist:
            logger.error('Trying to segment non-existent DocumentPart : %s', pk)
            continue

        # actual segmentation call
        try:
            if steps == 'masks':
                part.make_masks()
            else:
                part.segment(
                    steps=steps,
                    override=override,
                    text_direction=text_direction,
                    model=model
                )
        except Exception as e:
            # on failure, rollback state & notify
            if user:
                user.notify(
                    _("Something went wrong during the segmentation!"),
                    id="segmentation-error",
                    level='danger'
                )
            part.workflow_state = part.WORKFLOW_STATE_CONVERTED
            part.save()
            send_event(
                "document", part.document.pk, "part:workflow",
                {
                    "id": part.pk,
                    "process": "segment",
                    "status": "canceled",
                    "task_id": self.request.id,
                }
            )
            logger.exception(e)
            # re-raise to allow retry of the batch if desired
            raise
        else:
            # on success, notify & send done event
            if user:
                user.notify(
                    _("Segmentation done!"),
                    id="segmentation-success",
                    level='success'
                )
            send_event(
                "document", part.document.pk, "part:workflow",
                {
                    "id": part.pk,
                    "process": "segment",
                    "status": "done",
                    "task_id": self.request.id,
                }
            )


@shared_task(bind=True, autoretry_for=(MemoryError,), default_retry_delay=600)
def transcribe(self, instance_pks, model_pk=None, user_pk=None, transcription_pk=None, text_direction=None, task_group_pk=None, **kwargs):
    """
    Run recognition on multiple pages in one celery task.
    """
    DocumentPart = apps.get_model('core', 'DocumentPart')
    OcrModel = apps.get_model('core', 'OcrModel')
    Transcription = apps.get_model('core', 'Transcription')

    # load model
    try:
        model = OcrModel.objects.get(pk=model_pk)
    except OcrModel.DoesNotExist:
        model = None

    # load transcription
    transcription = Transcription.objects.get(pk=transcription_pk)

    # load user & quota‐check
    user = None
    if user_pk:
        try:
            user = User.objects.get(pk=user_pk)
            if not settings.DISABLE_QUOTAS and user.cpu_minutes_limit() is not None:
                assert user.has_free_cpu_minutes(), f"User {user.id} doesn't have any CPU minutes left"
        except User.DoesNotExist:
            user = None

    for pk in instance_pks:
        # fetch part
        try:
            part = DocumentPart.objects.get(pk=pk)
        except DocumentPart.DoesNotExist:
            logger.error('Trying to transcribe non-existent DocumentPart : %s', pk)
            continue

        # actual transcription call
        try:
            part.transcribe(model, transcription, user=user)
        except Exception as e:
            # on failure, rollback state & notify
            if user:
                user.notify(
                    _("Something went wrong during the transcription!"),
                    id="transcription-error",
                    level='danger'
                )
            part.workflow_state = part.WORKFLOW_STATE_SEGMENTED
            part.save()
            send_event(
                "document", part.document.pk, "part:workflow",
                {
                    "id": part.pk,
                    "process": "transcribe",
                    "status": "canceled",
                    "task_id": self.request.id,
                }
            )
            logger.exception(e)
            raise
        else:
            # on success, notify & send done event
            if user:
                user.notify(
                    _("Transcription done!"),
                    id="transcription-success",
                    level='success'
                )
            send_event(
                "document", part.document.pk, "part:workflow",
                {
                    "id": part.pk,
                    "process": "transcribe",
                    "status": "done",
                    "task_id": self.request.id,
                }
            )


@shared_task(autoretry_for=(MemoryError,), default_retry_delay=60)
def recalculate_masks(instance_pk=None, user_pk=None, only=None, **kwargs):
    if user_pk:
        try:
            user = User.objects.get(pk=user_pk)
            # If quotas are enforced, assert that the user still has free CPU minutes
            if not settings.DISABLE_QUOTAS and user.cpu_minutes_limit() is not None:
                assert user.has_free_cpu_minutes(), f"User {user.id} doesn't have any CPU minutes left"
        except User.DoesNotExist:
            user = None

    try:
        DocumentPart = apps.get_model('core', 'DocumentPart')
        part = DocumentPart.objects.get(pk=instance_pk)
    except DocumentPart.DoesNotExist:
        logger.error('Trying to recalculate masks of non-existent DocumentPart : %d', instance_pk)
        return

    result = part.make_masks(only=only)
    send_event('document', part.document.pk, "part:mask", {
        "id": part.pk,
        "lines": [{'pk': line.pk, 'mask': line.mask} for line in result]
    })


def train_(qs, document, transcription, model=None, user=None):
    # # Note hack to circumvent AssertionError: daemonic processes are not allowed to have children
    from multiprocessing import current_process
    current_process().daemon = False

    # try to minimize what is loaded in memory for large datasets
    ground_truth = list(qs.values('content',
                                  baseline=F('line__baseline'),
                                  mask=F('line__mask'),
                                  image=F('line__document_part__image')))

    # shuffle ground truth lines
    np.random.default_rng(241960353267317949653744176059648850006).shuffle(ground_truth)
    partition = int(len(ground_truth) / 10)

    LOAD_THREADS = getattr(settings, 'KRAKEN_TRAINING_LOAD_THREADS', 0)

    AMP_MODE = getattr(settings, 'KRAKEN_TRAINING_PRECISION', '32')

    RECOGNITION_HYPER_PARAMS['batch_size'] = getattr(settings,
                                                     'KRAKEN_TRAINING_BATCH_SIZE',
                                                     RECOGNITION_HYPER_PARAMS['batch_size'])
    
    # 🔥 Phase 1: Enable built-in Kraken augmentation
    RECOGNITION_HYPER_PARAMS['augment'] = getattr(settings,
                                                   'KRAKEN_TRAINING_AUGMENT',
                                                   True)
    
    # 🎨 Phase 2: Custom augmentation level for Hebrew/Arabic
    custom_augment_level = getattr(settings, 'KRAKEN_TRAINING_AUGMENT_LEVEL', 'medium')
    
    # Log augmentation status
    if RECOGNITION_HYPER_PARAMS['augment']:
        logger.info('✨ Data augmentation (Phase 1) is ENABLED - Kraken built-in augmentation')
        if custom_augment_level != 'off':
            logger.info(f'🎨 Custom augmentation (Phase 2) level: "{custom_augment_level}" - '
                       f'Hebrew/Arabic manuscript optimization')
        else:
            logger.info('Custom augmentation (Phase 2) is disabled')
    else:
        logger.info('Data augmentation is disabled')

    with tempfile.TemporaryDirectory() as tmp_dir:

        train_dir = Path(tmp_dir)

        logger.info(f'Compiling training dataset to {train_dir}/train.arrow')
        train_segs = make_recognition_segmentation(ground_truth[partition:])
        build_binary_dataset(train_segs,
                             output_file=str(train_dir / 'train.arrow'),
                             num_workers=LOAD_THREADS,
                             format_type=None)

        logger.info(f'Compiling validation dataset to {train_dir}/val.arrow')
        val_segs = make_recognition_segmentation(ground_truth[:partition])
        build_binary_dataset(val_segs,
                             output_file=str(train_dir / 'val.arrow'),
                             num_workers=LOAD_THREADS,
                             format_type=None)

        load = None
        try:
            load = model.file.path
        except ValueError:  # model is empty
            filename = slugify(model.name) + '.mlmodel'
            model.file = model.file.field.upload_to(model, filename)
            model.save()

        model_dir = os.path.join(settings.MEDIA_ROOT, os.path.split(model.file.path)[0])

        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        accelerator, device = _to_ptl_device(getattr(settings, 'KRAKEN_TRAINING_DEVICE', 'cpu'))

        if (document.main_script
            and (document.main_script.text_direction == 'horizontal-rl'
                 or document.main_script.text_direction == 'vertical-rl')):
            reorder = 'R'
        else:
            reorder = 'L'

        logger.info(f'Starting recognition training on {accelerator}/{device} '
                    f'(precision: {AMP_MODE}, batch_size {RECOGNITION_HYPER_PARAMS["batch_size"]} '
                    f', workers: {LOAD_THREADS}) with {len(ground_truth[partition:])} lines')

        kraken_model = RecognitionModel(hyper_params=RECOGNITION_HYPER_PARAMS,
                                        output=os.path.join(model_dir, 'version'),
                                        model=load,
                                        reorder=reorder,
                                        format_type='binary',
                                        training_data=[str(train_dir / 'train.arrow')],
                                        evaluation_data=[str(train_dir / 'val.arrow')],
                                        partition=partition,
                                        num_workers=LOAD_THREADS,
                                        load_hyper_parameters=True,
                                        resize='union')

        trainer = KrakenTrainer(accelerator=accelerator,
                                devices=device,
                                precision=AMP_MODE,
                                enable_summary=False,
                                enable_progress_bar=False,
                                val_check_interval=1.0,
                                callbacks=[FrontendFeedback(model, model_dir, document.pk)])

        trainer.fit(kraken_model)

    if kraken_model.best_epoch == -1:
        logger.info(f'Model {os.path.split(model.file.path)[0]} did not improve.')
        raise DidNotConverge
    else:
        best_version = os.path.join(model_dir, kraken_model.best_model)
        logger.info(f'Moving best model {best_version} (accuracy: {kraken_model.best_metric}) to {model.file.path}.')
        shutil.copy(best_version, model.file.path)
        model.training_accuracy = kraken_model.best_metric


# ============================================================================
# 🔥 TESSERACT TRAINING SUPPORT - UB-Mannheim Integration
# Added: 30 אוקטובר 2025
# ============================================================================

def train_tesseract(qs, document, transcription, model=None, user=None, expert_settings=None):
    """
    Train a Tesseract OCR model using ground truth data.
    
    This function implements the full Tesseract training pipeline:
    1. Prepares LSTMF ground truth files
    2. Splits data into training/evaluation sets
    3. Runs lstmtraining subprocess
    4. Monitors progress and creates model versions
    5. Sends real-time updates via WebSocket
    
    Requirements:
    - Modified Tesseract with LSTMF writer support (JKamlah fork)
    - tesserocr Python bindings
    - BeautifulSoup4 for downloading langdata files
    
    Args:
        qs: QuerySet of LineTranscription objects (ground truth)
        document: Document instance
        transcription: Transcription instance
        model: OcrModel instance (can be None for new model)
        user: User instance for notifications
        expert_settings: Optional ExpertSettings for advanced parameters
    """
    # Note hack to circumvent AssertionError: daemonic processes are not allowed to have children
    from collections import Counter
    from multiprocessing import current_process
    from hashlib import sha256
    import fcntl
    from datetime import date
    import subprocess
    import shlex
    import time
    import pickle

    from PIL import Image
    from tesserocr import PyTessBaseAPI
    from bs4 import BeautifulSoup
    from urllib.request import urlopen

    def clean_old_ground_truth(gt_path, expiration_timedelta_days=7):
        """Clean old LSTMF files that are no longer in use."""
        locked_files = subprocess.run(shlex.split(f"lsof +D {gt_path.resolve()}"), stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL).stdout
        locked_files = ['/' + line.split(b' /')[-1].decode('utf-8') for line in locked_files.split(b'\n') if
                        line.startswith(b'python')]
        for gt_file in gt_path.glob('*.lstmf'):
            if str(gt_file.resolve()) not in locked_files:
                if (time.time() - gt_file.stat().st_atime) > expiration_timedelta_days * 86400:
                    gt_file.unlink()
            elif (time.time() - gt_file.stat().st_atime) > 180 * 86400:
                gt_file.unlink()
        return

    def unlock_files(locked_files):
        """Release file locks on LSTMF files."""
        while locked_files:
            locked_file = locked_files.pop()
            fcntl.flock(locked_file, fcntl.LOCK_UN)
            locked_file.close()
        return

    # Note: Expert Settings functionality removed - not needed for current implementation
    # Ground truth cropping settings can be added in future versions if needed

    # Currently just checking if the model is trainable (best model)
    # TODO: Convert model from fast to best instead and than train with that
    if model.file.path:
        logger.info(f"Checking if model is trainable: {model.file.file.name}")
        model_info = subprocess.check_output(shlex.split(f"combine_tessdata -l {model.file.file.name}"),
                                             stderr=subprocess.STDOUT)
        if b'int_mode=1' in model_info:
            if user:
                user.notify(_("Tesseract model is not trainable! Please use a best model!"),
                            id="training-error", level='danger')
                raise TypeError("The tesseract model has the wrong type. Please use only best model!")

    current_process().daemon = False
    # try to minimize what is loaded in memory for large datasets
    ground_truth = list(qs.values('content',
                                  baseline=F('line__baseline'),
                                  external_id=F('line__external_id'),
                                  script=F('line__document_part__document__main_script__text_direction'),
                                  mask=F('line__mask'),
                                  image=F('line__document_part__image')))
    # TODO: Automatically recalculating the mask if baseline exists
    ground_truth = [lt for lt in ground_truth if lt['mask'] is not None]
    if not ground_truth:
        raise ValueError('No ground truth provided.')

    trainings_dir = Path(settings.MEDIA_ROOT).joinpath(f"training/tesseract/")
    trainingsdata_dir = trainings_dir.joinpath('data')
    trainingsdata_dir.mkdir(parents=True, exist_ok=True)
    trainingsgt_dir = trainings_dir.joinpath('gt')
    trainingsgt_dir.mkdir(parents=True, exist_ok=True)
    locked_files = []
    
    try:
        imagepath = ""
        image = Image.Image()
        gt_list = []
        rtl_cnt = 0
        
        # Create LSTMF files from ground truth
        with PyTessBaseAPI(path=os.path.dirname(model.file.path),
                           lang=os.path.basename(model.file.path).rsplit('.', 1)[0],
                           psm=13) as api:
            for lt in ground_truth:
                filepath = trainingsgt_dir.joinpath(f"{lt['external_id']}_"
                                                 f"{sha256(lt['content'].encode('utf-8')).hexdigest()}.lstmf")
                gt_list.append(str(filepath.resolve()))
                if filepath.exists():
                    filepath.touch(mode=0o666, exist_ok=True)
                else:
                    if imagepath != os.path.join(settings.MEDIA_ROOT, lt['image']):
                        imagepath = os.path.join(settings.MEDIA_ROOT, lt['image'])
                        image = Image.open(imagepath)
                    vertical = 'vertical' in lt['script']
                    rtl_cnt += 'rl' in lt['script']
                    
                    # Extract line cutout from mask (polygon crop)
                    # Use simple bounding box crop - mask is polygon coordinates
                    from PIL import ImageDraw
                    mask_polygon = lt['mask']
                    # Get bounding box
                    xs = [p[0] for p in mask_polygon]
                    ys = [p[1] for p in mask_polygon]
                    min_x, max_x = min(xs), max(xs)
                    min_y, max_y = min(ys), max(ys)
                    cutout = image.crop((min_x, min_y, max_x, max_y))
                    
                    api.WriteLSTMFLineData(filepath.with_suffix('').name, str(filepath.parent.resolve()), cutout,
                                       lt['content'], vertical)
                locked_files.append(filepath.open('r'))
                fcntl.flock(locked_files[-1], fcntl.LOCK_SH)
        image.close()

        # Delete old gt files
        clean_old_ground_truth(trainingsgt_dir)

        rtl = True if rtl_cnt > (len(gt_list)/2.25) else False
        # Randomize gt
        np.random.default_rng(241960353267317949653744176059648850006).shuffle(gt_list)

        # Calculate splitting point for training and evaluation set
        partition = int(len(ground_truth) / 10) if len(ground_truth) > 9 else 1

        # Get train and eval list
        eval_list = gt_list[:partition]
        train_list = gt_list[partition:]

        # Generate trainings id (startmodel_evallist_trainlist)
        model_dir = trainings_dir.joinpath('jobs').\
            joinpath(f"{slugify(model.name)}_{sha256(pickle.dumps(eval_list+train_list)).hexdigest()}").\
            joinpath(model.name)
        model_dir.mkdir(parents=True, exist_ok=True)

        evaluationlist_fpath = model_dir.joinpath('list.eval')
        evaluationlist_fpath.open('w').write('\n'.join(eval_list))
        trainingslist_fpath = model_dir.joinpath('list.train')
        trainingslist_fpath.open('w').write('\n'.join(train_list))

        # Get chars and occurences for train and eval files
        np.random.default_rng(241960353267317949653744176059648850005).shuffle(ground_truth)
        eval_cc = Counter('\n'.join([lt['content'] for lt in ground_truth[:partition]]))
        train_cc = Counter('\n'.join([lt['content'] for lt in ground_truth[partition:]]))
        avg_char_per_iteration = int(sum(train_cc.values())/(len(ground_truth)-partition))
        all_unicodes_fpath = model_dir.joinpath('all_unicodes')
        all_unicodes_fpath.open('w').write('\n'.join(train_cc.keys()))

        # Find difference in eval and train chars
        miss_trainingschar = set(eval_cc.keys()).difference(set(train_cc.keys()))
        miss_evaluationchar = set(train_cc.keys()).difference(set(eval_cc.keys()))

        if user:
            if any(miss_trainingschar):
                user.notify(_("There are chars in the evaluation set, which are not in the trainings set!"),
                            id="training-tesseract", level='warning')
            if any(miss_evaluationchar):
                user.notify(_("There are chars in the trainings set, which are not in the evaluation set!"),
                            id="training-tesseract", level='warning')

    except RuntimeError as e:
        logger.error(f"Error preparing ground truth: {e}")
        unlock_files(locked_files)
        raise

    def store_checkpoint_as_model(ckpt_path, model_path, start_model_path):
        """Convert LSTM checkpoint to final traineddata model."""
        try:
            logger.info(f"Converting checkpoint to model: {ckpt_path.relative_to(settings.MEDIA_ROOT)} "
                        f"-> {model_path.relative_to(settings.MEDIA_ROOT)}")
            subprocess.run(shlex.split(f"lstmtraining --stop_training "
                                       f"--continue_from {str(ckpt_path.absolute())} "
                                       f"--traineddata {str(start_model_path.absolute())} "
                                       f"--model_output {str(model_path.absolute())}"),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Clean checkpoints
            ckpt_path.unlink()
        except Exception as e:
            logger.error(f"Could not store checkpoint as model: {e}")

    def get_necessary_datafiles(data_dir):
        """Download Tesseract langdata files needed for training."""
        url = "https://github.com/tesseract-ocr/langdata_lstm/"
        with urlopen(url) as response:
            soup = BeautifulSoup(response.read(), "html.parser")

        datafiles = []
        for el in soup.find_all("a", class_="js-navigation-open Link--primary"):
            if '.' in el.text:
                datafiles.append(el.text)

        # Download necessary files
        for datafile in datafiles:
            subprocess.run(shlex.split(f"wget -P {str(data_dir.absolute())} "
                                       f"'https://github.com/tesseract-ocr/langdata_lstm/raw/main/{datafile}'"),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Inherited unicharset (not included in the official tesseract trainingsdata)
        data_dir.joinpath('Inherited.unicharset').open('w').write("""53
NULL 0 Common 0
̀ 0 202,248,238,255,1,66,0,71,0,173 Inherited 1168 17 1168 ̀	# ̀ [300 ]
́ 0 174,197,216,232,17,29,0,0,0,0 Inherited 4 17 4 ́	# ́ [301 ]
̂ 0 174,197,214,232,12,23,0,0,0,0 Inherited 5 17 5 ̂	# ̂ [302 ]
̃ 0 179,202,206,227,22,32,0,0,0,0 Inherited 6 17 6 ̃	# ̃ [303 ]
̄ 0 183,205,197,222,15,27,0,0,0,0 Inherited 7 17 7 ̄	# ̄ [304 ]
̅ 0 186,205,200,224,30,33,0,0,0,0 Inherited 8 17 8 ̅	# ̅ [305 ]
̆ 0 174,198,213,229,21,32,0,0,0,0 Inherited 9 17 9 ̆	# ̆ [306 ]
̇ 0 202,202,227,227,8,8,0,0,0,0 Inherited 10 17 10 ̇	# ̇ [307 ]
̈ 0 177,202,202,227,17,27,0,0,0,0 Inherited 11 17 11 ̈	# ̈ [308 ]
̉ 0 176,176,227,227,21,21,0,0,0,0 Inherited 12 17 12 ̉	# ̉ [309 ]
̊ 0 174,195,221,236,5,15,0,0,0,0 Inherited 13 17 13 ̊	# ̊ [30a ]
̋ 0 174,197,216,232,3,39,0,0,0,0 Inherited 14 17 14 ̋	# ̋ [30b ]
̌ 0 174,174,214,214,22,22,0,0,0,0 Inherited 15 17 15 ̌	# ̌ [30c ]
̍ 0 177,177,225,225,14,14,0,0,0,0 Inherited 16 17 16 ̍	# ̍ [30d ]
̎ 0 177,177,225,225,29,29,0,0,0,0 Inherited 17 17 17 ̎	# ̎ [30e ]
̏ 0 177,197,220,232,3,40,0,0,0,0 Inherited 18 17 18 ̏	# ̏ [30f ]
̐ 0 177,177,228,228,38,38,0,0,0,0 Inherited 19 17 19 ̐	# ̐ [310 ]
̑ 0 177,198,216,229,28,32,0,0,0,0 Inherited 20 17 20 ̑	# ̑ [311 ]
̒ 0 181,181,234,234,28,28,0,0,0,0 Inherited 21 17 21 ̒	# ̒ [312 ]
̔ 0 195,195,232,232,30,30,104,104,0,0 Inherited 22 17 22 ̔	# ̔ [314 ]
̚ 0 177,177,234,234,38,38,0,0,0,0 Inherited 23 17 23 ̚	# ̚ [31a ]
̛ 0 137,162,193,212,1,15,0,0,0,0 Inherited 24 17 24 ̛	# ̛ [31b ]
̡ 0 7,7,72,72,12,12,0,0,0,0 Inherited 25 17 25 ̡	# ̡ [321 ]
̢ 0 7,7,72,72,21,21,0,0,0,0 Inherited 26 17 26 ̢	# ̢ [322 ]
̦ 0 0,0,44,44,20,20,53,53,126,126 Inherited 27 17 27 ̦	# ̦ [326 ]
̲ 0 25,25,42,42,30,30,0,0,0,0 Inherited 28 17 28 ̲	# ̲ [332 ]
̳ 0 0,0,42,42,30,30,0,0,0,0 Inherited 29 17 29 ̳	# ̳ [333 ]
̴ 0 125,125,151,151,5,21,0,0,0,0 Inherited 30 17 30 ̴	# ̴ [334 ]
̶ 0 106,106,118,118,7,7,0,0,0,0 Inherited 31 17 31 ̶	# ̶ [336 ]
̷ 0 85,85,139,139,10,10,0,0,0,0 Inherited 32 17 32 ̷	# ̷ [337 ]
̸ 0 71,71,153,153,5,5,0,0,0,0 Inherited 33 17 33 ̸	# ̸ [338 ]
̽ 0 177,177,234,234,35,35,0,0,0,0 Inherited 34 17 34 ̽	# ̽ [33d ]
̾ 0 174,174,235,235,22,22,0,0,0,0 Inherited 35 17 35 ̾	# ̾ [33e ]
̿ 0 186,186,227,227,40,40,0,0,0,0 Inherited 36 17 36 ̿	# ̿ [33f ]
́ 0 222,222,255,255,1,1,0,0,0,0 Inherited 37 17 37 ́	# ́ [341 ]
͂ 0 199,199,223,223,19,19,0,0,0,0 Inherited 38 17 38 ͂	# ͂ [342 ]
͠ 0 176,176,221,225,99,124,0,0,0,0 Inherited 39 17 39 ͠	# ͠ [360 ]
͡ 0 176,214,221,246,92,143,0,0,0,0 Inherited 40 17 40 ͡	# ͡ [361 ]
҅ 0 177,192,209,244,67,85,0,27,85,123 Inherited 41 17 41 ҅	# ҅ [485 ]
҆ 0 177,192,209,244,67,85,0,27,85,123 Inherited 42 17 42 ҆	# ҆ [486 ]
ً 0 178,178,232,232,70,70,29,29,0,0 Inherited 43 17 43 ً	# ً [64b ]
ٌ 0 178,178,235,235,94,94,29,29,0,0 Inherited 44 17 44 ٌ	# ٌ [64c ]
ٍ 0 0,22,38,66,39,70,7,29,0,58 Inherited 45 17 45 ٍ	# ٍ [64d ]
َ 0 178,178,207,207,70,70,29,29,0,0 Inherited 46 17 46 َ	# َ [64e ]
ُ 0 178,178,238,238,74,74,29,29,0,0 Inherited 47 17 47 ُ	# ُ [64f ]
ِ 0 0,22,15,50,39,70,7,29,0,58 Inherited 48 17 48 ِ	# ِ [650 ]
ّ 0 178,178,238,238,74,74,29,29,0,0 Inherited 49 17 49 ّ	# ّ [651 ]
ْ 0 178,178,238,238,53,53,29,29,0,0 Inherited 50 17 50 ْ	# ْ [652 ]
ٰ 0 178,178,227,227,12,12,29,29,0,0 Inherited 51 17 51 ٰ	# ٰ [670 ]
॒ 0 12,25,24,109,1,5,0,0,0,2 Inherited 52 17 52 ॒	# ॒ [952 ]
⃝ 0 57,57,225,225,170,170,7,7,184,184 Inherited 53 17 53 ⃝	# ⃝ [20dd ]
゙ 0 210,221,228,230,43,46,133,157,193,205 Inherited 54 17 54 ゙	# ゙ [3099 ]""")
        return

    def _train_tesseract(*, learning_rate=0.0001, max_iterations=10000, max_model_timedelta=10000,
                         min_target_error_rate=1.0, target_error_rate=0.01, norm_mode=2,
                        net_spec="[1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx192 O1c\#\#\#]"):
        """Inner training function - runs preprocessing and tesseract training with subprocess."""

        def _print_eval(ckpt_path, epoch="0", accuracy="0", chars=0, error=0, val_metric=0):
            logger.info(f"Wrote checkpoint:   {ckpt_path}\n"
                        f"Current iterations: {epoch}\n"
                        f"Current accuracy:   {accuracy}")

        # Radical stroke (for proto model creation)
        radical_stroke = trainingsdata_dir.joinpath("radical-stroke.txt")
        if not radical_stroke.exists():
            get_necessary_datafiles(trainingsdata_dir)

        proto_model = Path(model_dir.joinpath(model.name + '.traineddata'))
        model_dir.joinpath('checkpoints').mkdir(exist_ok=True)
        training_cmd = f"lstmtraining " \
                       f"--debug_interval 0 " \
                       f"--traineddata {str(proto_model.absolute())} " \
                       f"--learning_rate {learning_rate} " \
                       f"--model_output {str(model_dir.absolute())} " \
                       f"--train_listfile {str(trainingslist_fpath.absolute())} " \
                       f"--eval_listfile {str(evaluationlist_fpath.absolute())} " \
                       f"--max_iterations {max_iterations} " \
                       f"--target_error_rate {target_error_rate} "

        if model.file:
            # Finetune a start model
            # unpack start model
            if not model_dir.joinpath(model.name + '.lstm').exists():
                subprocess.run(shlex.split(f"combine_tessdata "
                                               f"-u {model.file.file.name} "
                                               f"{str(model_dir.joinpath(model.name).absolute())}"),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )

            # create unicharset
            if not model_dir.joinpath('my.unicharset').exists():
                subprocess.run(shlex.split(f"unicharset_extractor "
                                           f"--output_unicharset "
                                           f"{str(model_dir.joinpath('my.unicharset').absolute())} "
                                           f"--norm_mode "
                                           f"{norm_mode} {str(all_unicodes_fpath.absolute())}"),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(shlex.split(f"merge_unicharsets "
                                           f"{str(model_dir.joinpath(model.name + '.lstm-unicharset').absolute())} "
                                           f"{str(model_dir.joinpath('my.unicharset').absolute())} "
                                           f"{str(model_dir.joinpath('unicharset').absolute())}"),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Training cmd
            training_cmd = training_cmd + f"--old_traineddata " \
                                          f"{model.file.file.name} " \
                                          f"--continue_from " \
                                          f"{str(model_dir.joinpath(model.name + '.lstm').absolute())}"

        else:
            # Create a placeholder model
            filename = slugify(model.name) + '.traineddata'
            model.file = model.file.field.upload_to(model, filename)
            model.save()

            # Create new model
            subprocess.run(shlex.split(f"unicharset_extractor "
                                       f"--output_unicharset "
                                       f"{str(model_dir.joinpath('my.unicharset').absolute())} "
                                       f"--norm_mode "
                                       f"{norm_mode} {str(all_unicodes_fpath.absolute())}"),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            net_spec = net_spec.replace('\#\#\#', str(len(train_cc)))
            training_cmd = training_cmd + f"--net_spec {net_spec})"

        # Create proto model (neural net not included)
        if not proto_model.exists():
            proto_cmd = "combine_lang_model "
            proto_cmd += "--lang_is_rtl " if rtl else ""
            proto_cmd += "--pass_through_recoder " if norm_mode > 2 else ""
            proto_cmd += f"--input_unicharset " \
                         f"{str(model_dir.joinpath('unicharset').absolute())} " \
                         f"--lang {model.name} " \
                         f"--script_dir {str(trainingsdata_dir.absolute())} " \
                         f'--version_str "Trained at {date.today()} with eScriptorium." ' \
                         f"--output_dir {str(model_dir.parent.absolute())}"
            subprocess.run(shlex.split(proto_cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Start training
        logger.info(f"Starting Tesseract training: {training_cmd}")
        process = subprocess.Popen(shlex.split(training_cmd), stderr=subprocess.PIPE)

        # Read process output on the fly and create new models automatically
        ckpt_path, current_bestmodel_path = Path(), Path()
        time_last_model = time.time()
        for c in iter(lambda: process.stderr.readline(), b""):
            text = c.decode()
            logger.info(text)
            if "wrote best model" in text:
                # Delete second last checkpoint if it exists
                if ckpt_path.name.endswith('checkpoint') and ckpt_path.exists() and current_bestmodel_path.exists():
                    ckpt_path.resolve().unlink()
                ckpt_path = Path(text.split('best model:')[1].split(' ', 1)[0])
                accuracy = text.split('=')[3].split(',', 1)[0]
                iterations = text.split('/', 2)[2].split(',', 1)[0]
                _print_eval(str(ckpt_path), iterations, accuracy, 0, 0)
                
                # Convert checkpoint to best model and save it
                epoch = int(int(iterations)/100)
                current_bestmodel_path = Path(model.file.path).parent.joinpath(f'version_{epoch}.traineddata')
                current_bestmodel_relpath = current_bestmodel_path.relative_to(settings.MEDIA_ROOT)
                store_checkpoint_as_model(ckpt_path,
                                  current_bestmodel_path,
                                  Path(model.file.file.name))
                
                # Add model to eScriptorium database
                model.refresh_from_db()
                model.training_epoch = epoch
                model.training_accuracy = (100.0-float(accuracy[:-1]))/100
                model.training_total = avg_char_per_iteration*int(iterations)
                model.training_errors = int((1-model.training_accuracy)*model.training_total)
                model.new_version(file=str(current_bestmodel_relpath))
                model.save()
                
                # Send WebSocket event to frontend
                send_event('document', document.pk, "training:eval", {
                    'id': model.pk,
                    'versions': model.versions,
                    'epoch': epoch,
                    'accuracy': model.training_accuracy,
                    'chars': model.training_total,
                    'error': model.training_errors})
                
                if (1-model.training_accuracy)*100 < min_target_error_rate:
                    if max_model_timedelta > 0 and time_last_model < time.time()+max_model_timedelta:
                        process.kill()
                        return
                time_last_model = time.time()
                
            if "is an integer (fast) model, cannot continue training" in text:
                if user:
                    user.notify(_("Only tesseracts best models can be trained!"),
                                id="training-tesseract", level='warning')
                process.kill()
                # Delete stuff
                Path(model.file.file.name).unlink()
                model.delete()
                raise ValueError("Fast model cannot be trained")
    
    try:
        _train_tesseract(learning_rate=0.0001, max_iterations=10000, max_model_timedelta=10,
                         min_target_error_rate=0.0, target_error_rate=0.01, norm_mode=2,
                         net_spec="[1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx192 O1c\#\#\#]")
    except Exception as e:
        logger.error(f"Tesseract training failed: {e}")
        raise
    finally:
        unlock_files(locked_files)


@shared_task(autoretry_for=(MemoryError,), default_retry_delay=60 * 60)
def train(transcription_pk=None, model_pk=None, task_group_pk=None,
          part_pks=None, user_pk=None, **kwargs):
    if user_pk:
        try:
            user = User.objects.get(pk=user_pk)
            # If quotas are enforced, assert that the user still has free CPU minutes, GPU minutes and disk storage
            if not settings.DISABLE_QUOTAS:
                if user.cpu_minutes_limit() is not None:
                    assert user.has_free_cpu_minutes(), f"User {user.id} doesn't have any CPU minutes left"
                if user.gpu_minutes_limit() is not None:
                    assert user.has_free_gpu_minutes(), f"User {user.id} doesn't have any GPU minutes left"
                if user.disk_storage_limit() is not None:
                    assert user.has_free_disk_storage(), f"User {user.id} doesn't have any disk storage left"
        except User.DoesNotExist:
            user = None
    else:
        user = None

    Transcription = apps.get_model('core', 'Transcription')
    LineTranscription = apps.get_model('core', 'LineTranscription')
    OcrModel = apps.get_model('core', 'OcrModel')

    try:
        model = OcrModel.objects.get(pk=model_pk)
        model.training = True
        model.save()
        transcription = Transcription.objects.get(pk=transcription_pk)
        document = transcription.document
        send_event('document', document.pk, "training:start", {
            "id": model.pk,
        })
        qs = (LineTranscription.objects
              .filter(transcription=transcription,
                      line__document_part__pk__in=part_pks)
              .exclude(Q(content='') | Q(content=None)))
        
        # 🔥 ROUTE TO CORRECT TRAINING FUNCTION BY ENGINE
        # Detect if model is Tesseract (.traineddata) or Kraken (.mlmodel)
        if model.file and model.file.name.endswith('.traineddata'):
            # Tesseract model - use train_tesseract()
            logger.info(f"Training Tesseract model: {model.name}")
            train_tesseract(qs, document, transcription, model=model, user=user)
        else:
            # Kraken model or no extension - use train_() (default)
            logger.info(f"Training Kraken model: {model.name}")
            train_(qs, document, transcription, model=model, user=user)
    except DidNotConverge:
        send_event('document', document.pk, "training:error", {
            "id": model.pk,
        })
        user.notify(_("The model did not converge, probably because of lack of data."),
                    id="training-warning", level='warning')
        model.delete()

    except Exception as e:
        send_event('document', document.pk, "training:error", {
            "id": model.pk,
        })
        if user:
            user.notify(_("Something went wrong during the training process!"),
                        id="training-error", level='danger')
        logger.exception(e)
    else:
        model.file_size = model.file.size

        if user:
            user.notify(_("Training finished!"),
                        id="training-success",
                        level='success')
    finally:
        model.training = False
        model.save()

        send_event('document', document.pk, "training:done", {
            "id": model.pk,
        })


@shared_task(autoretry_for=(MemoryError,), default_retry_delay=10 * 60)
def forced_align(instance_pk=None, model_pk=None, transcription_pk=None,
                 part_pk=None, user_pk=None, **kwargs):

    from kraken.align import forced_align as kraken_forced_align
    from kraken.lib import models as kraken_models

    OcrModel = apps.get_model('core', 'OcrModel')
    DocumentPart = apps.get_model('core', 'DocumentPart')
    Transcription = apps.get_model('core', 'Transcription')
    LineTranscription = apps.get_model('core', 'LineTranscription')

    ocrmodel = OcrModel.objects.get(pk=model_pk)
    model = kraken_models.load_any(ocrmodel.file.path)
    transcription = Transcription.objects.get(pk=transcription_pk)

    part = DocumentPart.objects.get(pk=instance_pk)
    document = part.document

    text_direction = (
        (document.main_script and document.main_script.text_direction)
        or "horizontal-lr"
    )

    linetrans = LineTranscription.objects.filter(
        line__document_part=part,
        transcription=transcription
    ).select_related('line')

    for lt in linetrans:
        data = {
            'image': part.image,
            "lines": [{
                "text": lt.content,
                "baseline": lt.line.baseline,
                "boundary": lt.line.mask,
                "text_direction": text_direction,
                "tags": {'type': lt.line.typology and lt.line.typology.name or 'default'},
            }],
            "type": "baselines"
        }

        records = kraken_forced_align(data, model)  # base_dir = L,R
        for pred in records:
            # lt.content = pred.prediction
            if text_direction == 'horizontal-rl' or text_direction == 'vertical-rl':
                reorder = 'R'
            else:
                reorder = 'L'
            pred = pred.logical_order(reorder)
            lt.graphs = [{
                'c': letter,
                'poly': poly,
                'confidence': float(confidence)
            } for letter, poly, confidence in zip(
                pred.prediction, pred.cuts, pred.confidences)]
            lt.save()


@shared_task(bind=True, autoretry_for=(MemoryError,), default_retry_delay=10 * 60)
def align(
    task,
    document_pk=None,
    part_pks=[],
    user_pk=None,
    task_group_pk=None,
    transcription_pk=None,
    witness_pk=None,
    n_gram=25,
    max_offset=0,
    merge=False,
    full_doc=True,
    threshold=0.8,
    region_types=["Orphan", "Undefined"],
    layer_name=None,
    beam_size=20,
    gap=600,
    **kwargs
):
    """Start document alignment on the passed parts, using the passed settings"""
    try:
        Document = apps.get_model('core', 'Document')
        doc = Document.objects.get(pk=document_pk)
    except Document.DoesNotExist:
        logger.error('Trying to align text on non-existent Document: %d', document_pk)
        return

    if user_pk:
        try:
            user = get_user_model().objects.get(pk=user_pk)
            # If quotas are enforced, assert that the user still has free CPU minutes
            if not settings.DISABLE_QUOTAS and user.cpu_minutes_limit() is not None:
                assert user.has_free_cpu_minutes(), f"User {user.id} doesn't have any CPU minutes left"
        except User.DoesNotExist:
            user = None
    else:
        user = None

    try:
        doc.align(
            part_pks,
            transcription_pk,
            witness_pk,
            n_gram,
            max_offset,
            merge,
            full_doc,
            threshold,
            region_types,
            layer_name,
            beam_size,
            gap,
        )
    except Exception as e:
        if user:
            user.notify(_("Something went wrong during the alignment!"),
                        id="alignment-error", level='danger')
        DocumentPart = apps.get_model('core', 'DocumentPart')
        parts = DocumentPart.objects.filter(pk__in=part_pks)
        for part in parts:
            part.workflow_state = part.WORKFLOW_STATE_TRANSCRIBING
            send_event("document", document_pk, "part:workflow", {
                "id": part.pk,
                "process": "align",
                "status": "canceled",
                "task_id": task.request.id,
            })
            reports = part.reports.filter(method="core.tasks.align")
            if reports.exists():
                reports.last().cancel(None)

        DocumentPart.objects.bulk_update(parts, ["workflow_state"])
        logger.exception(e)
        raise e
    else:
        if user:
            user.notify(_("Alignment done!"),
                        id="alignment-success",
                        level='success')


@shared_task(bind=True, autoretry_for=(MemoryError,), default_retry_delay=10 * 60)
def replace_line_transcriptions_text(
    task, mode, find_terms, replace_term, project_pk=None, document_pk=None, transcription_pk=None, part_pk=None, user_pk=None, **kwargs
):
    import time
    LineTranscription = apps.get_model('core', 'LineTranscription')

    # Get the associated TaskReport
    TaskReport = apps.get_model('reporting', 'TaskReport')
    try:
        report = TaskReport.objects.get(task_id=task.request.id)
    except TaskReport.MultipleObjectsReturned:
        report = TaskReport.objects.filter(task_id=task.request.id).order_by('-started_at').first()
    except TaskReport.DoesNotExist:
        report = None

    user = User.objects.get(pk=user_pk)
    user.notify(_('Your replacements are being applied...'), links=[{'text': 'Report', 'src': report.uri}], id='find-replace-running', level='info')

    # Find line transcriptions to update
    search_method = search_content_psql_word
    if mode == REGEX_SEARCH_MODE:
        search_method = search_content_psql_regex

    search_results = search_method(
        find_terms,
        user,
        'text-danger',
        project_id=project_pk,
        document_id=document_pk,
        transcription_id=transcription_pk,
        part_id=part_pk,
    )

    if mode == WORD_BY_WORD_SEARCH_MODE:
        find_terms = '|'.join(find_terms.split(' '))

    # Apply the replacement on the found line transcriptions
    total = search_results.count()
    errors = 0
    updated = []
    
    # 🆕 Progress tracking variables
    processed = 0
    start_time = time.time()
    
    # 🆕 Send initial progress event
    if document_pk:
        send_event('document', document_pk, 'replace:start', {
            'task_id': task.request.id,
            'total': total,
            'started_at': start_time,
        })
    
    for result in search_results.iterator(chunk_size=5000):
        try:
            report.append(f'Applying the replacement on the transcription from the line {result.line}', logger_fct=logger.info)
            # Replace on the highlighted content and then remove the highlighting tags
            result.content = strip_tags(build_highlighted_replacement_psql(mode, find_terms, replace_term, result.highlighted_content))
        except Exception as e:
            errors += 1
            report.append(f'Failed to apply the replacement on the transcription from the line {result.line}: {e}', logger_fct=logger.error)
            continue

        updated.append(result)
        processed += 1
        
        # 🆕 Send progress update every 2,500 lines (half-second intervals!)
        if document_pk and processed % 2500 == 0:
            elapsed = time.time() - start_time
            speed = processed / elapsed if elapsed > 0 else 0
            remaining_time = (total - processed) / speed if speed > 0 else 0
            
            send_event('document', document_pk, 'replace:progress', {
                'task_id': task.request.id,
                'total': total,
                'processed': processed,
                'errors': errors,
                'percent': int((processed / total) * 100) if total > 0 else 0,
                'elapsed_time': int(elapsed),
                'estimated_remaining': int(remaining_time),
                'speed': round(speed, 2)
            })

        # Once we have 1000 line transcriptions to update, we do it and clear the list
        if len(updated) >= 1000:
            LineTranscription.objects.bulk_update(updated, fields=['content'])
            updated = []

    # We don't forget to update the remaining line transcriptions
    if updated:
        LineTranscription.objects.bulk_update(updated, fields=['content'])
    
    # 🆕 Send completion event
    if document_pk:
        total_time = time.time() - start_time
        send_event('document', document_pk, 'replace:done', {
            'task_id': task.request.id,
            'total': total,
            'processed': processed,
            'errors': errors,
            'total_time': int(total_time)
        })

    # Alert the user
    if total and errors == total:
        user.notify(_('All replacements failed'), links=[{'text': 'Report', 'src': report.uri}], id='find-replace-error', level='danger')
    elif errors:
        user.notify(_('Replacements applied with some errors'), links=[{'text': 'Report', 'src': report.uri}], id='find-replace-warning', level='warning')
    else:
        user.notify(_('Replacements applied!'), links=[{'text': 'Report', 'src': report.uri}], id='find-replace-success', level='success')


# ============================================================================
# 🔍 Elasticsearch Indexing Tasks
# Created: 20 אוקטובר 2025
# ============================================================================

@shared_task
def index_transcription_to_es(line_transcription_id):
    """
    אינדקס תמלול בודד ל-Elasticsearch
    נקרא אוטומטית כש-LineTranscription נשמר
    """
    from core.search import get_es_service
    
    try:
        LineTranscription = apps.get_model('core', 'LineTranscription')
        line_trans = LineTranscription.objects.select_related(
            'line__document_part__document__project',
            'transcription'
        ).get(pk=line_transcription_id)
        
        es_service = get_es_service()
        success = es_service.index_transcription(line_trans)
        
        if success:
            logger.info(f"✅ Indexed transcription {line_transcription_id} to ES")
        else:
            logger.warning(f"⚠️ ES indexing disabled or failed for {line_transcription_id}")
            
        return success
    except Exception as e:
        logger.error(f"❌ Error indexing transcription {line_transcription_id}: {e}")
        return False


@shared_task
def delete_transcription_from_es(line_transcription_id):
    """
    מחק תמלול מ-Elasticsearch
    נקרא אוטומטית כש-LineTranscription נמחק
    """
    from core.search import get_es_service
    
    try:
        es_service = get_es_service()
        success = es_service.delete_transcription(line_transcription_id)
        
        if success:
            logger.info(f"✅ Deleted transcription {line_transcription_id} from ES")
        
        return success
    except Exception as e:
        logger.error(f"❌ Error deleting transcription {line_transcription_id}: {e}")
        return False


@shared_task
def bulk_index_document_to_es(document_id, transcription_id, user_pk=None):
    """
    אינדקס כל התמלולים של מסמך בבת אחת
    שימושי לאחר OCR או import
    """
    from core.search import get_es_service
    
    try:
        Document = apps.get_model('core', 'Document')
        document = Document.objects.get(pk=document_id)
        
        es_service = get_es_service()
        if not es_service.enabled:
            logger.warning("⚠️ Elasticsearch is disabled, skipping bulk index")
            return {"success": 0, "failed": 0, "message": "ES disabled"}
        
        # אינדקס בבת אחת
        LineTranscription = apps.get_model('core', 'LineTranscription')
        lines = LineTranscription.objects.filter(
            line__document_part__document_id=document_id,
            transcription_id=transcription_id
        ).select_related(
            'line__document_part__document__project',
            'transcription'
        )
        
        success = 0
        failed = 0
        
        for line_trans in lines:
            if line_trans.content:  # רק שורות עם תוכן
                if es_service.index_transcription(line_trans):
                    success += 1
                else:
                    failed += 1
        
        logger.info(f"✅ Bulk indexed document {document_id}: {success} success, {failed} failed")
        
        # שלח הודעה למשתמש
        if user_pk:
            try:
                user = User.objects.get(pk=user_pk)
                user.notify(
                    _('Document indexed to search: {success} lines').format(success=success),
                    id='es-index-complete',
                    level='success'
                )
            except User.DoesNotExist:
                pass
        
        return {"success": success, "failed": failed}
        
    except Exception as e:
        logger.error(f"❌ Error bulk indexing document {document_id}: {e}")
        return {"success": 0, "failed": 0, "error": str(e)}


@shared_task
def rebuild_es_index(user_pk=None):
    """
    בנה מחדש את כל ה-index של Elasticsearch
    משימה כבדה - להרצה ידנית בלבד!
    """
    from core.search import get_es_service
    
    try:
        es_service = get_es_service()
        if not es_service.enabled:
            return {"error": "Elasticsearch is disabled"}
        
        # מחק index קיים
        if es_service.es.indices.exists(index=es_service.index_name):
            es_service.es.indices.delete(index=es_service.index_name)
            logger.info(f"🗑️ Deleted old index: {es_service.index_name}")
        
        # צור index חדש
        es_service._ensure_index_exists()
        logger.info(f"✅ Created new index: {es_service.index_name}")
        
        # אינדקס את כל התמלולים
        LineTranscription = apps.get_model('core', 'LineTranscription')
        total = LineTranscription.objects.count()
        
        logger.info(f"📊 Starting to index {total} transcriptions...")
        
        success = 0
        failed = 0
        batch_size = 1000
        
        for i in range(0, total, batch_size):
            lines = LineTranscription.objects.select_related(
                'line__document_part__document__project',
                'transcription'
            )[i:i+batch_size]
            
            for line_trans in lines:
                if line_trans.content:
                    if es_service.index_transcription(line_trans):
                        success += 1
                    else:
                        failed += 1
            
            # עדכון progress
            progress = int((i + batch_size) / total * 100)
            logger.info(f"📈 Progress: {progress}% ({success} indexed)")
        
        logger.info(f"✅ Rebuild complete: {success} success, {failed} failed")
        
        # הודעה למשתמש
        if user_pk:
            try:
                user = User.objects.get(pk=user_pk)
                user.notify(
                    _('Search index rebuilt: {total} documents indexed').format(total=success),
                    id='es-rebuild-complete',
                    level='success'
                )
            except User.DoesNotExist:
                pass
        
        return {
            "success": success,
            "failed": failed,
            "total": total
        }
        
    except Exception as e:
        logger.error(f"❌ Error rebuilding ES index: {e}")
        return {"error": str(e)}


# ============================================================================
# ERROR DETECTION TASKS - BiblIA Enhancement
# ============================================================================


@shared_task
def detect_errors_in_line(line_transcription_id):
    """
    זיהוי שגיאות בשורת תמלול בודדת
    Detect errors in a single line transcription
    
    Runs all three detection engines:
    1. SpellChecker - spelling errors
    2. ErrorPatternDetector - OCR pattern errors
    3. ConfidenceAnalyzer - low confidence issues
    """
    from core.spell_checker import get_spell_checker
    from core.error_patterns import get_pattern_detector
    from core.confidence_analyzer import get_confidence_analyzer
    from core.models import DetectedError
    
    try:
        LineTranscription = apps.get_model('core', 'LineTranscription')
        line_trans = LineTranscription.objects.get(pk=line_transcription_id)
        
        if not line_trans.content:
            return {"status": "skipped", "reason": "empty content"}
        
        # Delete old errors for this line
        DetectedError.objects.filter(line=line_trans).delete()
        
        errors_created = 0
        
        # 1. Spell checking
        spell_checker = get_spell_checker()
        spell_errors = spell_checker.check_line(line_trans.content, language='he')
        
        for error in spell_errors:
            DetectedError.objects.create(
                line=line_trans,
                error_type='spelling',
                text=error['word'],
                start_pos=error['position'],
                end_pos=error['position'] + len(error['word']),
                suggestions=error.get('suggestions', []),
                severity='medium',
                confidence_score=0.0
            )
            errors_created += 1
        
        # 2. Pattern detection
        pattern_detector = get_pattern_detector()
        pattern_errors = pattern_detector.analyze_line(
            line_trans.content,
            line_id=line_transcription_id
        )
        
        for error in pattern_errors:
            DetectedError.objects.create(
                line=line_trans,
                error_type='pattern',
                text=error['text'],
                start_pos=error['start_pos'],
                end_pos=error['end_pos'],
                suggestions=error.get('suggestions', []),
                severity=error['severity'],
                confidence_score=0.0,
                pattern_name=error.get('pattern_name', '')
            )
            errors_created += 1
        
        # 3. Confidence analysis (if available)
        if hasattr(line_trans.line, 'confidences') and line_trans.line.confidences:
            confidence_analyzer = get_confidence_analyzer()
            conf_errors = confidence_analyzer.analyze_line(
                line_trans.content,
                confidences=line_trans.line.confidences,
                line_id=line_transcription_id
            )
            
            for error in conf_errors:
                DetectedError.objects.create(
                    line=line_trans,
                    error_type='confidence',
                    text=error['text'],
                    start_pos=error['start_pos'],
                    end_pos=error['end_pos'],
                    suggestions=error.get('suggestions', []),
                    severity=error['severity'],
                    confidence_score=error.get('confidence', 0.0)
                )
                errors_created += 1
        
        logger.info(f"✓ Detected {errors_created} errors in line {line_transcription_id}")
        
        return {
            "status": "success",
            "line_id": line_transcription_id,
            "errors_found": errors_created
        }
        
    except LineTranscription.DoesNotExist:
        logger.error(f"Line transcription {line_transcription_id} not found")
        return {"status": "error", "reason": "not found"}
    except Exception as e:
        logger.error(f"Error detecting errors in line {line_transcription_id}: {e}")
        return {"status": "error", "reason": str(e)}


@shared_task
def scan_new_transcriptions(hours=24):
    """
    סרוק תמלולים חדשים לזיהוי שגיאות
    Scan recent transcriptions for errors
    
    Args:
        hours: Scan transcriptions from last N hours (default: 24)
    """
    from datetime import timedelta
    from django.utils import timezone
    
    try:
        LineTranscription = apps.get_model('core', 'LineTranscription')
        
        since = timezone.now() - timedelta(hours=hours)
        new_lines = LineTranscription.objects.filter(
            updated_at__gte=since,
            content__isnull=False
        ).exclude(content='')
        
        total = new_lines.count()
        logger.info(f"📊 Scanning {total} new transcriptions from last {hours}h")
        
        processed = 0
        errors_found = 0
        
        for line_trans in new_lines:
            result = detect_errors_in_line(line_trans.pk)
            if result.get('status') == 'success':
                processed += 1
                errors_found += result.get('errors_found', 0)
        
        logger.info(f"✅ Scan complete: {processed}/{total} processed, {errors_found} errors found")
        
        return {
            "status": "success",
            "total": total,
            "processed": processed,
            "errors_found": errors_found
        }
        
    except Exception as e:
        logger.error(f"❌ Error scanning new transcriptions: {e}")
        return {"status": "error", "reason": str(e)}


@shared_task
def learn_from_corrections(min_frequency=3):
    """
    למד דפוסי שגיאות מתיקוני משתמשים
    Learn error patterns from user corrections
    
    Creates/updates ErrorPattern records based on ErrorCorrection data.
    
    Args:
        min_frequency: Minimum occurrences to create a pattern (default: 3)
    """
    from core.models import ErrorCorrection, ErrorPattern
    from collections import Counter
    
    try:
        # Get all corrections
        corrections = ErrorCorrection.objects.select_related('error').all()
        
        # Group by (original_text → corrected_text)
        pattern_counts = Counter()
        pattern_data = {}
        
        for correction in corrections:
            if not correction.error or not correction.corrected_text:
                continue
            
            original = correction.error.text
            corrected = correction.corrected_text
            
            # Skip if same
            if original == corrected:
                continue
            
            key = (original, corrected)
            pattern_counts[key] += 1
            
            # Track if from suggestion and success
            if key not in pattern_data:
                pattern_data[key] = {
                    'from_suggestion': 0,
                    'total': 0
                }
            
            pattern_data[key]['total'] += 1
            if correction.was_from_suggestion:
                pattern_data[key]['from_suggestion'] += 1
        
        # Create/update patterns
        patterns_created = 0
        patterns_updated = 0
        
        for (pattern_from, pattern_to), count in pattern_counts.items():
            if count < min_frequency:
                continue
            
            # Calculate confidence based on usage
            data = pattern_data[(pattern_from, pattern_to)]
            success_rate = data['from_suggestion'] / data['total'] if data['total'] > 0 else 0.5
            
            # Try to get existing pattern
            pattern, created = ErrorPattern.objects.get_or_create(
                pattern_from=pattern_from,
                pattern_to=pattern_to,
                defaults={
                    'language': 'he',
                    'frequency': count,
                    'confidence': success_rate,
                    'success_rate': success_rate
                }
            )
            
            if created:
                patterns_created += 1
                logger.info(f"✓ Created pattern: '{pattern_from}' → '{pattern_to}' (freq: {count})")
            else:
                # Update existing pattern
                pattern.frequency = count
                pattern.success_rate = success_rate
                pattern.save()
                patterns_updated += 1
        
        logger.info(f"✅ Learning complete: {patterns_created} created, {patterns_updated} updated")
        
        return {
            "status": "success",
            "patterns_created": patterns_created,
            "patterns_updated": patterns_updated,
            "total_corrections": corrections.count()
        }
        
    except Exception as e:
        logger.error(f"❌ Error learning from corrections: {e}")
        return {"status": "error", "reason": str(e)}
