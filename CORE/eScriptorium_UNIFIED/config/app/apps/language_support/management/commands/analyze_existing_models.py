from django.core.management.base import BaseCommand
from apps.core.models import OcrModel
from apps.language_support.models import ModelLanguageAnalysis
from apps.language_support.utils import analyze_hebrew_support


class Command(BaseCommand):
    help = 'Analyze existing OCR models for Hebrew support'

    def handle(self, *args, **options):
        self.stdout.write("=== Analyzing Existing OCR Models ===")
        
        ocr_models = OcrModel.objects.all()
        self.stdout.write(f"Found {ocr_models.count()} OCR models")
        
        analyses_created = 0
        
        for ocr_model in ocr_models:
            self.stdout.write(f"Analyzing model: {ocr_model.name}")
            
            # Check if analysis already exists
            if ModelLanguageAnalysis.objects.filter(ocr_model=ocr_model).exists():
                self.stdout.write(f"  - Analysis already exists, skipping")
                continue
            
            # Create new analysis
            try:
                analysis_result = analyze_hebrew_support(ocr_model)
                
                analysis = ModelLanguageAnalysis.objects.create(
                    ocr_model=ocr_model,
                    hebrew_support=analysis_result['hebrew_support'],
                    confidence_score=analysis_result['confidence_score'],
                    analysis_notes=analysis_result['notes']
                )
                
                self.stdout.write(f"  - Created analysis: {analysis.hebrew_support} (confidence: {analysis.confidence_score})")
                analyses_created += 1
                
            except Exception as e:
                self.stdout.write(f"  - Error analyzing model: {str(e)}")
        
        self.stdout.write(f"\nCompleted! Created {analyses_created} new analyses")
        
        # Show summary
        total_analyses = ModelLanguageAnalysis.objects.count()
        self.stdout.write(f"Total analyses in system: {total_analyses}")