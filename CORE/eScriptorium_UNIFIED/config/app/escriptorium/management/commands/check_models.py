# ========================================
# eScriptorium Model Quality Checker
# כלי בדיקת איכות מודלים המשתלב עם Django
# ========================================

"""
Django Management Command לבדיקת איכות מודלים ב-eScriptorium

השימוש:
python manage.py check_models --scan          # סריקה כללית
python manage.py check_models --model MODEL  # בדיקת מודל ספציפי
python manage.py check_models --best         # חיפוש המודל הטוב ביותר
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json
import sys
from pathlib import Path

# הוספת הכלי שיצרנו לנתיב
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'tools'))

try:
    from escriptorium_model_checker import EscriptoriumModelChecker
except ImportError:
    print("❌ לא ניתן לטעון את כלי בדיקת המודלים")
    print("   ודא שהקובץ tools/escriptorium_model_checker.py קיים")
    sys.exit(1)


class Command(BaseCommand):
    help = 'בודק איכות ומאפיינים של מודלי OCR ב-eScriptorium'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--scan',
            action='store_true',
            help='סרוק את כל המודלים במערכת'
        )
        
        parser.add_argument(
            '--model',
            type=str,
            help='נתיב למודל ספציפי לבדיקה'
        )
        
        parser.add_argument(
            '--best',
            action='store_true',
            help='מצא את המודל הטוב ביותר למטרה עברית'
        )
        
        parser.add_argument(
            '--compare',
            nargs='+',
            help='השווה בין מודלים (רשימת נתיבים)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='שמור תוצאות לקובץ JSON'
        )
        
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='הפעלה שקטה (רק JSON)'
        )
    
    def handle(self, *args, **options):
        """הפונקציה הראשית של הפקודה"""
        
        if not options['quiet']:
            self.stdout.write(self.style.SUCCESS(
                '🔍 eScriptorium Model Quality Checker'
            ))
            self.stdout.write('=' * 50)
        
        checker = EscriptoriumModelChecker()
        
        try:
            if options['model']:
                result = self._check_single_model(checker, options['model'], options['quiet'])
                
            elif options['compare']:
                result = self._compare_models(checker, options['compare'], options['quiet'])
                
            elif options['best']:
                result = self._find_best_model(checker, options['quiet'])
                
            elif options['scan']:
                result = self._scan_models(checker, options['quiet'])
                
            else:
                # ברירת מחדל - סריקה מהירה
                result = self._quick_overview(checker, options['quiet'])
            
            # שמירת תוצאות
            if options['output']:
                self._save_results(result, options['output'], options['quiet'])
            
            # הדפסת JSON אם נדרש
            if options['quiet'] and result:
                self.stdout.write(json.dumps(result, indent=2, ensure_ascii=False))
                
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'❌ שגיאה: {e}')
            )
            return
    
    def _check_single_model(self, checker, model_path, quiet):
        """בדיקת מודל יחיד"""
        if not quiet:
            self.stdout.write(f'🔍 בודק מודל: {model_path}')
        
        result = checker.check_model(model_path)
        
        if not quiet:
            self._display_model_results(result)
        
        return result
    
    def _compare_models(self, checker, model_paths, quiet):
        """השוואה בין מודלים"""
        if not quiet:
            self.stdout.write(f'⚖️ משווה בין {len(model_paths)} מודלים')
        
        result = checker.compare_models(model_paths)
        
        if not quiet:
            self._display_comparison_results(result)
        
        return result
    
    def _find_best_model(self, checker, quiet):
        """חיפוש המודל הטוב ביותר"""
        if not quiet:
            self.stdout.write('🏆 מחפש את המודל הטוב ביותר...')
        
        # תחילה סריקה כללית
        scan_result = checker.quick_scan('.')
        
        if 'error' in scan_result:
            if not quiet:
                self.stderr.write(self.style.ERROR(f'❌ {scan_result["error"]}'))
            return scan_result
        
        # חיפוש המודל העברי הטוב ביותר
        hebrew_models = scan_result.get('hebrew_models', [])
        
        if hebrew_models:
            best_hebrew = max(hebrew_models, key=lambda x: x.get('size_mb', 0))
            
            if not quiet:
                self.stdout.write(self.style.SUCCESS(
                    f'🎯 נמצא מודל עברי מומלץ: {best_hebrew["name"]}'
                ))
            
            # בדיקה מפורטת
            detailed_result = checker.check_model(best_hebrew['path'])
            
            if not quiet:
                self._display_model_results(detailed_result)
            
            return {
                'scan_summary': scan_result,
                'best_model': detailed_result
            }
        else:
            if not quiet:
                self.stdout.write(self.style.WARNING(
                    '⚠️ לא נמצאו מודלים עבריים מובהקים'
                ))
                
                # הצג את הגדול ביותר
                if scan_result.get('models'):
                    largest = max(scan_result['models'], key=lambda x: x.get('size_mb', 0))
                    self.stdout.write(f'📊 המודל הגדול ביותר: {largest["name"]} ({largest["size_mb"]} MB)')
            
            return scan_result
    
    def _scan_models(self, checker, quiet):
        """סריקה מלאה"""
        if not quiet:
            self.stdout.write('📂 סורק מודלים...')
        
        result = checker.quick_scan('.')
        
        if not quiet:
            self._display_scan_results(result)
        
        return result
    
    def _quick_overview(self, checker, quiet):
        """סקירה מהירה"""
        if not quiet:
            self.stdout.write('⚡ סקירה מהירה של המודלים...')
        
        result = checker.quick_scan('.')
        
        if not quiet:
            if 'error' not in result:
                self.stdout.write(self.style.SUCCESS(
                    f'✅ נמצאו {result.get("total_found", 0)} מודלים'
                ))
                
                hebrew_count = len(result.get('hebrew_models', []))
                if hebrew_count > 0:
                    self.stdout.write(f'🔤 מתוכם {hebrew_count} מודלים עבריים')
                
                # הצג המלצות
                recommendations = result.get('recommendations', [])
                if recommendations:
                    self.stdout.write('\n💡 המלצות:')
                    for rec in recommendations:
                        self.stdout.write(f'   {rec}')
            else:
                self.stderr.write(self.style.ERROR(f'❌ {result["error"]}'))
        
        return result
    
    def _display_model_results(self, result):
        """הצגת תוצאות מודל יחיד"""
        if 'error' in result:
            self.stderr.write(self.style.ERROR(f'❌ {result["error"]}'))
            return
        
        self.stdout.write(f'\n📄 מודל: {result["name"]}')
        self.stdout.write('-' * 40)
        
        # מידע בסיסי
        basic = result.get('basic_info', {})
        if basic and 'error' not in basic:
            self.stdout.write(f'💾 גודל: {basic.get("size_mb", 0)} MB')
            self.stdout.write(f'📅 תאריך עדכון: {basic.get("modified", "לא ידוע")[:10]}')
        
        # זיהוי עברי
        hebrew = result.get('hebrew_detection', {})
        if hebrew:
            status = '🔤 עברי' if hebrew.get('is_hebrew') else '🌍 כללי'
            confidence = hebrew.get('confidence', 'לא ידוע')
            self.stdout.write(f'{status} (אמינות: {confidence})')
        
        # מידע charset
        charset = result.get('charset_info', {})
        if charset and 'error' not in charset:
            if 'charset_size' in charset:
                self.stdout.write(f'🔤 גודל charset: {charset["charset_size"]}')
            if 'hebrew_percentage' in charset:
                self.stdout.write(f'🔤 אחוז עברי: {charset["hebrew_percentage"]}%')
        
        # איכות
        quality = result.get('quality_estimate', {})
        if quality:
            level = quality.get('level', 'לא ידוע')
            score = quality.get('score', 0)
            self.stdout.write(f'⭐ איכות: {level} ({score} נקודות)')
        
        # המלצות
        recommendations = result.get('recommendations', [])
        if recommendations:
            self.stdout.write('\n💡 המלצות:')
            for rec in recommendations:
                self.stdout.write(f'   {rec}')
    
    def _display_scan_results(self, result):
        """הצגת תוצאות סריקה"""
        if 'error' in result:
            self.stderr.write(self.style.ERROR(f'❌ {result["error"]}'))
            return
        
        total = result.get('total_found', 0)
        analyzed = result.get('analyzed', 0)
        hebrew_count = len(result.get('hebrew_models', []))
        
        self.stdout.write(f'\n📊 תוצאות סריקה:')
        self.stdout.write(f'   📁 סך הכל: {total} מודלים')
        self.stdout.write(f'   🔍 נותחו: {analyzed}')
        self.stdout.write(f'   🔤 עבריים: {hebrew_count}')
        
        # הצג מודלים עבריים
        hebrew_models = result.get('hebrew_models', [])
        if hebrew_models:
            self.stdout.write('\n🔤 מודלים עבריים:')
            for model in hebrew_models[:5]:  # הראש 5
                confidence = model.get('hebrew_confidence', 'לא ידוע')
                size = model.get('size_mb', 0)
                self.stdout.write(f'   • {model["name"]} ({size} MB, {confidence})')
        
        # המלצות
        recommendations = result.get('recommendations', [])
        if recommendations:
            self.stdout.write('\n💡 המלצות:')
            for rec in recommendations:
                self.stdout.write(f'   {rec}')
    
    def _display_comparison_results(self, result):
        """הצגת תוצאות השוואה"""
        if 'error' in result:
            self.stderr.write(self.style.ERROR(f'❌ {result["error"]}'))
            return
        
        self.stdout.write(f'\n⚖️ השוואה בין {result.get("models_count", 0)} מודלים:')
        
        summary = result.get('summary', {})
        best = summary.get('best_model')
        if best:
            self.stdout.write(f'🏆 המודל הטוב ביותר: {best}')
        
        hebrew_models = summary.get('hebrew_models', [])
        if hebrew_models:
            self.stdout.write(f'🔤 מודלים עבריים: {", ".join(hebrew_models)}')
        
        ranking = summary.get('quality_ranking', [])
        if ranking:
            self.stdout.write('\n📊 דירוג איכות:')
            for i, (name, level) in enumerate(ranking[:5], 1):
                self.stdout.write(f'   {i}. {name} - {level}')
    
    def _save_results(self, result, output_path, quiet):
        """שמירת תוצאות לקובץ"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            if not quiet:
                self.stdout.write(self.style.SUCCESS(f'💾 תוצאות נשמרו ב: {output_path}'))
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ שגיאה בשמירה: {e}'))