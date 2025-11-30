from django.contrib import admin
from .models import ModelLanguageAnalysis


@admin.register(ModelLanguageAnalysis)
class ModelLanguageAnalysisAdmin(admin.ModelAdmin):
    """
    Admin interface for managing language analysis of OCR models
    Completely separate from core - follows "No Core Modifications" rule
    """
    
    list_display = [
        'ocr_model_name',
        'hebrew_support',
        'confidence_score_display',
        'analysis_score_display',
        'size_mb_display',
        'model_complexity_display',
        'charset_type_display',
        'analysis_date_short'
    ]
    
    list_filter = [
        'hebrew_support',
        'analysis_date',
    ]
    
    search_fields = [
        'ocr_model__name',
    ]
    
    readonly_fields = [
        'analysis_date',
        'confidence_score',
        'detailed_analysis_display',
    ]
    
    actions = ['run_hebrew_analysis']
    
    def ocr_model_name(self, obj):
        """Display OCR model name"""
        return obj.ocr_model.name
    ocr_model_name.short_description = 'שם המודל'
    
    def confidence_score_display(self, obj):
        """Display confidence score in a readable format"""
        if obj.confidence_score:
            return f"{obj.confidence_score:.1%}"
        return "לא זמין"
    confidence_score_display.short_description = 'ודאות'
    
    def analysis_score_display(self, obj):
        """Display analysis score from details"""
        try:
            details = obj.analysis_details
            if isinstance(details, dict):
                hebrew_data = details.get('hebrew_detection', {})
                score = hebrew_data.get('score', 0)
                return f"{score}/70" if score else "0"
        except:
            pass
        return "לא זמין"
    analysis_score_display.short_description = 'ניקוד'
    
    def size_mb_display(self, obj):
        """Display model size"""
        try:
            details = obj.analysis_details
            if isinstance(details, dict):
                basic_info = details.get('basic_info', {})
                size = basic_info.get('size_mb', 0)
                return f"{size:.1f}MB" if size else "לא ידוע"
        except:
            pass
        return "לא ידוע"
    size_mb_display.short_description = 'גודל'
    
    def analysis_date_short(self, obj):
        """Display short date format"""
        if obj.analysis_date:
            return obj.analysis_date.strftime("%d/%m %H:%M")
        return "לא ידוע"
    analysis_date_short.short_description = 'תאריך ניתוח'
    
    def model_complexity_display(self, obj):
        """Display model complexity from advanced analysis"""
        try:
            details = obj.analysis_details
            if isinstance(details, dict):
                training_insights = details.get('training_insights', {})
                file_analysis = training_insights.get('file_analysis', {})
                complexity = file_analysis.get('complexity_estimate', 'לא ידוע')
                return complexity
        except:
            pass
        return "לא ידוע"
    model_complexity_display.short_description = 'מורכבות'
    
    def charset_type_display(self, obj):
        """Display charset type from advanced analysis"""
        try:
            details = obj.analysis_details
            if isinstance(details, dict):
                advanced = details.get('advanced_analysis', {})
                dataset_clues = advanced.get('dataset_clues', {})
                script_detection = dataset_clues.get('script_detection', {})
                primary_script = script_detection.get('primary_script', 'לא ידוע')
                
                if primary_script == 'hebrew':
                    hebrew_cov = script_detection.get('hebrew_coverage', 0)
                    return f"עברית ({hebrew_cov:.1f}%)"
                elif primary_script == 'latin':
                    latin_cov = script_detection.get('latin_coverage', 0)
                    return f"לטינית ({latin_cov:.1f}%)"
                elif primary_script == 'mixed':
                    return "מעורב"
                else:
                    return primary_script
        except:
            pass
        return "לא ידוע"
    charset_type_display.short_description = 'סוג תווים'
    
    def detailed_analysis_display(self, obj):
        """Display organized analysis details instead of raw JSON - with advanced features"""
        if not obj.analysis_details:
            return "אין נתונים"
        
        try:
            details = obj.analysis_details
            html = "<div style='font-family: monospace; direction: rtl;'>"
            
            # Hebrew detection summary
            hebrew_data = details.get('hebrew_detection', {})
            html += f"<h3>🔤 זיהוי עברית:</h3>"
            html += f"<p><strong>ניקוד:</strong> {hebrew_data.get('score', 0)}/70</p>"
            html += f"<p><strong>ודאות:</strong> {hebrew_data.get('confidence', 'לא ידוע')}</p>"
            html += f"<p><strong>מבוסס charset:</strong> {'כן' if hebrew_data.get('charset_based') else 'לא'}</p>"
            html += f"<p><strong>נימוק:</strong> {hebrew_data.get('reasoning', 'לא זמין')}</p>"
            
            # Advanced Analysis (NEW!)
            advanced = details.get('advanced_analysis', {})
            if advanced:
                html += f"<h3>🔬 ניתוח מתקדם:</h3>"
                
                # Model Architecture
                arch = advanced.get('model_architecture', {})
                if arch:
                    html += f"<p><strong>ארכיטקטורה:</strong> {arch.get('type', 'לא ידוע')}</p>"
                    if 'parameters_millions' in arch:
                        html += f"<p><strong>פרמטרים:</strong> {arch['parameters_millions']}M</p>"
                    if 'model_size_estimate_mb' in arch:
                        html += f"<p><strong>הערכת גודל:</strong> {arch['model_size_estimate_mb']:.1f}MB</p>"
                
                # Dataset Clues
                dataset = advanced.get('dataset_clues', {})
                if dataset:
                    script_detection = dataset.get('script_detection', {})
                    if script_detection:
                        html += f"<p><strong>זיהוי סקריפט:</strong> {script_detection.get('primary_script', 'לא ידוע')}</p>"
                        if script_detection.get('hebrew_coverage', 0) > 0:
                            html += f"<p><strong>כיסוי עברית:</strong> {script_detection['hebrew_coverage']:.1f}%</p>"
                        if script_detection.get('is_multilingual'):
                            html += f"<p><strong>רב-לשוני:</strong> כן</p>"
                    
                    # Special patterns
                    patterns = dataset.get('special_patterns', [])
                    if patterns:
                        html += f"<p><strong>דפוסים מיוחדים:</strong> {', '.join(patterns[:3])}</p>"
                    
                    # Text type hints
                    hints = dataset.get('text_type_hints', [])
                    if hints:
                        html += f"<p><strong>סוג טקסט:</strong> {', '.join(hints[:2])}</p>"
            
            # Training Insights (NEW!)
            training = details.get('training_insights', {})
            if training:
                html += f"<h3>📊 תובנות אימון:</h3>"
                
                dataset_hints = training.get('dataset_hints', [])
                if dataset_hints:
                    html += f"<p><strong>רמזי דאטאסט:</strong> {', '.join(dataset_hints[:2])}</p>"
                
                quality_signs = training.get('training_quality_signs', [])
                if quality_signs:
                    html += f"<p><strong>סימני איכות:</strong> {', '.join(quality_signs[:2])}</p>"
                
                file_analysis = training.get('file_analysis', {})
                if file_analysis:
                    html += f"<p><strong>קטגוריית גודל:</strong> {file_analysis.get('size_category', 'לא ידוע')}</p>"
                    html += f"<p><strong>מורכבות:</strong> {file_analysis.get('complexity_estimate', 'לא ידוע')}</p>"
            
            # Performance Metrics (NEW!)
            performance = details.get('performance_metrics', {})
            if performance:
                accuracy = performance.get('expected_accuracy_range', {})
                if accuracy:
                    html += f"<h3>⚡ ביצועים צפויים:</h3>"
                    html += f"<p><strong>דיוק צפוי:</strong> {accuracy.get('typical', 'לא ידוע')}% (טווח: {accuracy.get('min', 0)}-{accuracy.get('max', 0)}%)</p>"
                
                suitability = performance.get('use_case_suitability', [])
                if suitability:
                    html += f"<p><strong>מתאים עבור:</strong> {', '.join(suitability[:3])}</p>"
            
            # Basic info
            basic_info = details.get('basic_info', {})
            html += f"<h3>📁 מידע בסיסי:</h3>"
            html += f"<p><strong>גודל:</strong> {basic_info.get('size_mb', 0):.1f}MB</p>"
            html += f"<p><strong>סוג קובץ:</strong> {basic_info.get('file_type', 'לא ידוע')}</p>"
            
            # Quality estimate
            quality = details.get('quality_estimate', {})
            html += f"<h3>⭐ הערכת איכות:</h3>"
            html += f"<p><strong>רמה:</strong> {quality.get('level', 'לא ידוע')}</p>"
            html += f"<p><strong>ניקוד:</strong> {quality.get('score', 0)}/{quality.get('max_possible', 70)}</p>"
            
            # Charset info (if available)
            charset = details.get('charset_info', {})
            if charset.get('success'):
                html += f"<h3>🔤 charset:</h3>"
                html += f"<p><strong>סה\"כ תווים:</strong> {charset.get('charset_size', 0)}</p>"
                html += f"<p><strong>תווים עבריים:</strong> {charset.get('hebrew_chars_count', 0)}</p>"
                html += f"<p><strong>אחוז עברי:</strong> {charset.get('hebrew_percentage', 0):.1f}%</p>"
            
            html += "</div>"
            return html
        except Exception as e:
            return f"שגיאה בהצגת הנתונים: {e}"
    
    detailed_analysis_display.short_description = 'פרטי ניתוח'
    detailed_analysis_display.allow_tags = True
    
    def run_hebrew_analysis(self, request, queryset):
        """Admin action to run Hebrew analysis on selected models"""
        count = 0
        for analysis in queryset:
            try:
                analysis.analyze_model_hebrew_support()
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"שגיאה בניתוח {analysis.ocr_model.name}: {e}",
                    level='ERROR'
                )
        
        self.message_user(
            request,
            f"הושלם ניתוח עברית עבור {count} מודלים",
            level='SUCCESS'
        )
    
    run_hebrew_analysis.short_description = "הפעל ניתוח עברית למודלים נבחרים"