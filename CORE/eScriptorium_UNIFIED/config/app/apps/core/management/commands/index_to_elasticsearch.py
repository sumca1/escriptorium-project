"""
Management command to index existing transcriptions to Elasticsearch
פקודת ניהול לאינדוקס התמלולים הקיימים ל-Elasticsearch

Usage:
    python manage.py index_to_elasticsearch
    python manage.py index_to_elasticsearch --rebuild  # מחיקה ובניה מחדש
    python manage.py index_to_elasticsearch --document=123  # מסמך ספציפי
"""

import logging
from django.core.management.base import BaseCommand
from django.apps import apps
from core.search import get_es_service
from core.models import Document, LineTranscription

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Index transcriptions to Elasticsearch / אינדקס תמלולים ל-Elasticsearch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='מחק index קיים ובנה מחדש'
        )
        parser.add_argument(
            '--document',
            type=int,
            help='אינדקס רק מסמך ספציפי (Document ID)'
        )
        parser.add_argument(
            '--transcription',
            type=int,
            help='אינדקס רק תמלול ספציפי (Transcription ID)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='גודל אצווה (default: 1000)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Starting Elasticsearch indexing...'))
        
        # קבל ES service
        es_service = get_es_service()
        
        if not es_service.enabled:
            self.stdout.write(self.style.ERROR('❌ Elasticsearch is disabled in settings'))
            self.stdout.write('Set DISABLE_ELASTICSEARCH=False in variables.env')
            return
        
        if not es_service.es:
            self.stdout.write(self.style.ERROR('❌ Cannot connect to Elasticsearch'))
            self.stdout.write(f'Check ELASTICSEARCH_URL: {es_service.index_name}')
            return
        
        # אופציית rebuild
        if options['rebuild']:
            self.stdout.write(self.style.WARNING('🗑️ Rebuilding index (deleting existing)...'))
            if es_service.es.indices.exists(index=es_service.index_name):
                es_service.es.indices.delete(index=es_service.index_name)
                self.stdout.write(self.style.SUCCESS(f'✅ Deleted index: {es_service.index_name}'))
            
            es_service._ensure_index_exists()
            self.stdout.write(self.style.SUCCESS(f'✅ Created new index: {es_service.index_name}'))
        
        # קבע query
        queryset = LineTranscription.objects.select_related(
            'line__document_part__document__project',
            'transcription'
        ).exclude(content__isnull=True).exclude(content='')
        
        # סינון לפי מסמך
        if options['document']:
            doc_id = options['document']
            queryset = queryset.filter(line__document_part__document_id=doc_id)
            self.stdout.write(f'📄 Filtering by document ID: {doc_id}')
        
        # סינון לפי תמלול
        if options['transcription']:
            trans_id = options['transcription']
            queryset = queryset.filter(transcription_id=trans_id)
            self.stdout.write(f'📝 Filtering by transcription ID: {trans_id}')
        
        total = queryset.count()
        self.stdout.write(f'📊 Total transcriptions to index: {total:,}')
        
        if total == 0:
            self.stdout.write(self.style.WARNING('⚠️ No transcriptions found to index'))
            return
        
        # אינדקס בצווים
        batch_size = options['batch_size']
        success = 0
        failed = 0
        
        self.stdout.write(f'⚙️ Batch size: {batch_size}')
        self.stdout.write(self.style.SUCCESS('🚀 Starting indexing...'))
        
        for i in range(0, total, batch_size):
            lines = queryset[i:i+batch_size]
            
            for line_trans in lines:
                try:
                    if es_service.index_transcription(line_trans):
                        success += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    logger.error(f'Error indexing {line_trans.id}: {e}')
            
            # עדכון progress
            progress = int((i + batch_size) / total * 100)
            self.stdout.write(
                f'📈 Progress: {progress}% | '
                f'✅ {success:,} success | '
                f'❌ {failed:,} failed',
                ending='\r'
            )
        
        self.stdout.write('')  # שורה חדשה
        
        # סיכום
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ Indexing Complete!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'📊 Total: {total:,}')
        self.stdout.write(self.style.SUCCESS(f'✅ Success: {success:,}'))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f'❌ Failed: {failed:,}'))
        
        # סטטיסטיקות ES
        try:
            stats = es_service.get_stats()
            self.stdout.write('\n📈 Elasticsearch Stats:')
            self.stdout.write(f'  • Index: {es_service.index_name}')
            self.stdout.write(f'  • Documents: {stats.get("total_documents", "N/A"):,}')
            self.stdout.write(f'  • Size: {stats.get("size_mb", "N/A")} MB')
        except Exception as e:
            logger.error(f'Error getting stats: {e}')
        
        self.stdout.write(self.style.SUCCESS('\n✨ Done!'))
