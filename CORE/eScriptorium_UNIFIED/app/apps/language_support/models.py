from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import OcrModel


class ModelLanguageAnalysis(models.Model):
    """
    נפרד לחלוטין מ-core! כלל #2: No Core Modifications
    מודל זה שומר ניתוח שפה עבור מודלי OCR בלי לגעת בליבה
    """
    
    # ForeignKey ל-OcrModel - חיבור חיצוני בלי לשנות את הליבה
    ocr_model = models.OneToOneField(
        OcrModel, 
        on_delete=models.CASCADE,
        related_name='language_analysis',
        help_text="חיבור למודל OCR מהליבה (בלי לשנות אותה!)"
    )
    
    # שדות ניתוח השפה
    hebrew_support = models.CharField(
        max_length=20,
        choices=[
            ('full', 'תמיכה מלאה'),
            ('partial', 'תמיכה חלקית'),
            ('none', 'ללא תמיכה'),
            ('unknown', 'לא נבדק'),
        ],
        default='unknown',
        help_text="רמת תמיכת עברית במודל"
    )
    
    hebrew_charset_score = models.FloatField(
        null=True, blank=True,
        help_text="ניקוד איכות charset עברי (0-1)"
    )
    
    confidence_score = models.FloatField(
        null=True, blank=True,
        help_text="ניקוד ודאות כללי (0-1)"
    )
    
    analysis_date = models.DateTimeField(auto_now=True)
    analysis_details = models.JSONField(
        default=dict, blank=True,
        help_text="פרטי ניתוח מלאים (charset, דוגמאות, וכו')"
    )
    
    class Meta:
        verbose_name = _("OCR Model Language Analysis")
        verbose_name_plural = _("OCR Model Language Analyses")
    
    def __str__(self):
        return f"{self.ocr_model.name} - {self.get_hebrew_support_display()}"
    
    def analyze_model_hebrew_support(self):
        """
        מבצע ניתוח Hebrew support למודל OCR
        מבוסס על escriptorium_model_checker.py
        """
        from .utils import analyze_hebrew_support
        
        try:
            result = analyze_hebrew_support(self.ocr_model)
            
            self.hebrew_support = result.get('hebrew_support', 'unknown')
            self.confidence_score = result.get('confidence_score', 0.0)
            self.hebrew_charset_score = result.get('confidence_score', 0.0)  # backwards compatibility
            self.analysis_details = result
            self.save()
            
            return result
            
        except Exception as e:
            self.hebrew_support = 'unknown'
            self.hebrew_charset_score = 0.0
            self.analysis_details = {'error': str(e)}
            self.save()
            return None