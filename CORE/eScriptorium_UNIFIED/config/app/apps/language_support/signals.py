"""
Django Signals for Language Support App
Automatically analyzes new OCR models for Hebrew support
Without modifying core eScriptorium!
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import OcrModel
from .models import ModelLanguageAnalysis
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=OcrModel)
def create_language_analysis_for_new_model(sender, instance, created, **kwargs):
    """
    כשנוצר מודל OCR חדש, יוצר אוטומטית ניתוח שפה
    זה לא משנה את הליבה - רק מוסיף אובייקט נפרד!
    """
    if created:  # רק עבור מודלים חדשים
        try:
            # יצירת ניתוח שפה חדש
            analysis, created = ModelLanguageAnalysis.objects.get_or_create(
                ocr_model=instance,
                defaults={'hebrew_support': 'unknown'}
            )
            
            if created:
                logger.info(f"Created language analysis for new OCR model: {instance.name}")
                
                # הפעלת ניתוח אוטומטי (אופציונלי - יכול לקחת זמן)
                # analysis.analyze_model_hebrew_support()
                
        except Exception as e:
            logger.error(f"Failed to create language analysis for {instance.name}: {e}")


@receiver(post_save, sender=OcrModel) 
def update_analysis_on_model_change(sender, instance, created, **kwargs):
    """
    כשמודל OCR מתעדכן (לא נוצר חדש), מעדכן את ניתוח השפה אם קיים
    """
    if not created:  # רק עבור עדכונים
        try:
            analysis = ModelLanguageAnalysis.objects.filter(ocr_model=instance).first()
            if analysis and analysis.hebrew_support != 'unknown':
                # אפשר לבחור האם להריץ ניתוח מחדש או לא
                # analysis.analyze_model_hebrew_support()
                logger.debug(f"Model {instance.name} updated - analysis exists")
        except Exception as e:
            logger.error(f"Error handling model update for {instance.name}: {e}")