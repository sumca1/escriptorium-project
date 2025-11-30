"""
Test Language Support App
Django management command to test the language_support app functionality
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import OcrModel
from apps.language_support.models import ModelLanguageAnalysis


class Command(BaseCommand):
    help = 'Test the language_support app functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-analysis',
            action='store_true',
            help='Create language analysis for all OCR models without one'
        )
        
        parser.add_argument(
            '--run-analysis',
            action='store_true', 
            help='Run language analysis on all models (generic character-based detection)'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Limit number of models to analyze (default: 5, use 0 for no limit)'
        )
        
        parser.add_argument(
            '--target-language',
            type=str,
            choices=['hebrew', 'arabic', 'latin', 'auto'],
            default='auto',
            help='Target language for analysis (default: auto-detect)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Testing Language Support App...')
        )

        # Count existing models
        total_ocr_models = OcrModel.objects.count()
        total_analyses = ModelLanguageAnalysis.objects.count()
        
        self.stdout.write(f'Found {total_ocr_models} OCR models')
        self.stdout.write(f'Found {total_analyses} language analyses')

        if options['create_analysis']:
            self.create_missing_analyses()
        
        if options['run_analysis']:
            limit = options['limit'] if options['limit'] > 0 else None
            target_lang = options['target_language']
            self.run_language_analyses(limit, target_lang)
        
        # Test signals by showing recent activity
        self.show_recent_activity()

    def create_missing_analyses(self):
        """Create language analysis for OCR models without one"""
        self.stdout.write('Creating missing language analyses...')
        
        created_count = 0
        error_count = 0
        
        try:
            models_without_analysis = OcrModel.objects.exclude(
                id__in=ModelLanguageAnalysis.objects.values_list('ocr_model_id', flat=True)
            )
            
            total_to_create = models_without_analysis.count()
            self.stdout.write(f'Found {total_to_create} models without analysis')
            
            for ocr_model in models_without_analysis:
                try:
                    analysis, created = ModelLanguageAnalysis.objects.get_or_create(
                        ocr_model=ocr_model,
                        defaults={'hebrew_support': 'unknown'}
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(f'✓ Created analysis for: {ocr_model.name}')
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to create analysis for {ocr_model.name}: {e}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created {created_count} new analyses')
            )
            if error_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'{error_count} errors occurred')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Critical error in create_missing_analyses: {e}')
            )

    def run_language_analyses(self, limit=5, target_language='auto'):
        """Run language analysis on models with improved logic and safety"""
        self.stdout.write(f'Running language analyses (limit: {limit or "unlimited"}, target: {target_language})...')
        
        analyses_query = ModelLanguageAnalysis.objects.filter(
            hebrew_support='unknown'
        ).select_related('ocr_model')
        
        if limit:
            analyses_query = analyses_query[:limit]
        
        analyses = list(analyses_query)
        
        if not analyses:
            self.stdout.write(self.style.WARNING('No models require analysis'))
            return
        
        self.stdout.write(f'Found {len(analyses)} models to analyze')
        
        success_count = 0
        error_count = 0
        
        for i, analysis in enumerate(analyses, 1):
            try:
                self.stdout.write(f'[{i}/{len(analyses)}] Analyzing: {analysis.ocr_model.name}')
                
                # בדיקת בטיחות - וודא שהקובץ קיים
                if not analysis.ocr_model.file or not analysis.ocr_model.file.path:
                    self.stdout.write(self.style.WARNING(f'  ⚠️ No file path for model'))
                    continue
                
                # בדיקת קיום הקובץ
                import os
                if not os.path.exists(analysis.ocr_model.file.path):
                    self.stdout.write(self.style.WARNING(f'  ⚠️ Model file not found: {analysis.ocr_model.file.path}'))
                    continue
                
                # ריצת הניתוח עם timeout
                result = self._run_analysis_with_timeout(analysis, target_language)
                
                if result:
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Result: {analysis.hebrew_support} '
                            f'(score: {analysis.hebrew_charset_score or "N/A"})'
                        )
                    )
                else:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'  ✗ Analysis failed'))
                    
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\nAnalysis interrupted by user'))
                break
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Unexpected error: {e}'))
        
        # סיכום
        self.stdout.write(f'\n--- Analysis Summary ---')
        self.stdout.write(f'✓ Successful: {success_count}')
        self.stdout.write(f'✗ Errors: {error_count}')
        self.stdout.write(f'📊 Total processed: {success_count + error_count}')
    
    def _run_analysis_with_timeout(self, analysis, target_language='auto', timeout_seconds=30):
        """Run analysis with timeout and error handling"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Analysis timeout")
        
        try:
            # הגדרת timeout (רק ב-Unix systems)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)
            
            result = analysis.analyze_model_hebrew_support()
            
            # ביטול timeout
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            
            return result
            
        except TimeoutError:
            self.stdout.write(self.style.ERROR(f'  ⏰ Analysis timed out after {timeout_seconds}s'))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  💥 Analysis error: {e}'))
            return None
        finally:
            # וודא ביטול timeout במקרה של חריגה
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)

    def show_recent_activity(self):
        """Show recent language analysis activity"""
        self.stdout.write('\nRecent language analyses:')
        
        recent_analyses = ModelLanguageAnalysis.objects.order_by(
            '-analysis_date'
        )[:10]
        
        for analysis in recent_analyses:
            self.stdout.write(
                f'  {analysis.ocr_model.name}: {analysis.get_hebrew_support_display()} '
                f'({analysis.analysis_date.strftime("%Y-%m-%d %H:%M")})'
            )
        
        self.stdout.write(
            self.style.SUCCESS('Language Support App test completed!')
        )