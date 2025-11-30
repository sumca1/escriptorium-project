"""
🔧 Django Management Command: process_document_with_surya

This command processes a document with Surya OCR from the command line.

Usage:
    python manage.py process_document_with_surya --document-id 1
    python manage.py process_document_with_surya --document-id 1 --language he ar
    python manage.py process_document_with_surya --batch --limit 10
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.core.models import Document, DocumentPart, LineTranscription
from escriptorium.ocr_engines.surya_engine import get_ocr_engine
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process documents with Surya OCR'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--document-id',
            type=int,
            help='Process a specific document by ID'
        )
        
        parser.add_argument(
            '--batch',
            action='store_true',
            help='Process all documents in batch'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Limit number of documents in batch mode'
        )
        
        parser.add_argument(
            '--language',
            nargs='+',
            default=['he', 'en', 'ar'],
            help='Languages to process'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Reprocess even if already has transcriptions'
        )
        
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip documents that already have transcriptions'
        )
    
    def handle(self, *args, **options):
        """Main handler."""
        
        # Get engine
        try:
            engine = get_ocr_engine()
            self.stdout.write("✅ Surya OCR engine loaded")
        except Exception as e:
            self.stdout.write(f"❌ Failed to load engine: {e}")
            return
        
        # Process
        if options['document_id']:
            self.process_single_document(
                options['document_id'],
                engine,
                options['force'],
                options['skip_existing']
            )
        elif options['batch']:
            self.process_batch(
                engine,
                options['limit'],
                options['force'],
                options['skip_existing']
            )
        else:
            self.stdout.write("❌ Specify --document-id or --batch")
    
    def process_single_document(self, doc_id, engine, force=False, skip_existing=False):
        """Process a single document."""
        try:
            doc = Document.objects.get(id=doc_id)
        except Document.DoesNotExist:
            self.stdout.write(f"❌ Document {doc_id} not found")
            return
        
        # Check existing transcriptions
        parts = doc.parts.all()
        existing_count = sum(
            p.lines.filter(transcriptions__isnull=False).count()
            for p in parts
        )
        
        if existing_count > 0 and not force and skip_existing:
            self.stdout.write(f"⏭️  Skipping document {doc.id} (already has transcriptions)")
            return
        
        self.stdout.write(f"\n📖 Processing document: {doc.title} (ID: {doc.id})")
        self.stdout.write(f"   Parts: {parts.count()}")
        
        # Get image paths
        image_paths = []
        for part in parts:
            if part.image:
                image_paths.append(str(part.image.path))
        
        if not image_paths:
            self.stdout.write("❌ No images found")
            return
        
        # Process
        self.stdout.write(f"🚀 Running Surya OCR on {len(image_paths)} pages...")
        results = engine.recognize_pages(image_paths)
        
        # Save results
        created = 0
        for part, result in zip(parts, results):
            if result.success:
                for line_idx, line in enumerate(result.lines):
                    LineTranscription.objects.create(
                        line=part,
                        transcription=line.text,
                        confidence=line.confidence,
                        bounding_box=line.polygon
                    )
                    created += 1
                
                self.stdout.write(f"  ✅ Part {part.id}: {len(result.lines)} lines")
            else:
                self.stdout.write(f"  ❌ Part {part.id}: {result.error_message}")
        
        self.stdout.write(f"\n✅ Complete! Created {created} transcriptions")
    
    def process_batch(self, engine, limit=10, force=False, skip_existing=False):
        """Process batch of documents."""
        
        # Get documents
        docs = Document.objects.all()[:limit]
        
        if skip_existing:
            # Filter out docs with existing transcriptions
            docs = [
                d for d in docs
                if d.parts.filter(lines__transcriptions__isnull=False).count() == 0
            ]
        
        self.stdout.write(f"\n📚 Processing batch of {len(docs)} documents")
        
        total_created = 0
        for doc in docs:
            try:
                self.process_single_document(doc.id, engine, force, False)
                total_created += 1
            except Exception as e:
                self.stdout.write(f"❌ Error processing document {doc.id}: {e}")
        
        self.stdout.write(f"\n✅ Batch complete! Processed {total_created} documents")
