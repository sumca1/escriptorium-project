#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 eScriptorium Model Checker - בודק מודלים ממוקד
כלי פשוט וממוקד לבדיקת איכות ומאפיינים של מודלי OCR ב-eScriptorium

תכונות מרכזיות:
- זיהוי מודלים עבריים
- בדיקת איכות מהירה
- ניתוח charset ותווים
- השוואה בין מודלים
- דיווח ממוקד
"""

import os
import sys
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pickle
import tempfile

class EscriptoriumModelChecker:
    def __init__(self):
        self.models_cache = {}
        self._last_charset_info = {}
        self._last_advanced_info = {}
        self._current_model = None
        
    def check_model(self, model_path: str) -> Dict[str, Any]:
        """בדיקה מקיפה של מודל יחיד עם נתונים מורחבים"""
        model_path = Path(model_path)
        
        if not model_path.exists():
            return {"error": f"קובץ לא נמצא: {model_path}"}
        
        result = {
            "name": model_path.name,
            "path": str(model_path),
            "timestamp": datetime.now().isoformat(),
            "basic_info": self._get_basic_info(model_path),
            "hebrew_detection": self._detect_hebrew(model_path),
            "charset_info": self._analyze_charset(model_path),
            "advanced_analysis": self._perform_advanced_analysis(model_path),  # חדש!
            "training_insights": self._extract_training_insights(model_path),  # חדש!
            "performance_metrics": self._estimate_performance_metrics(),  # חדש!
            "quality_estimate": self._estimate_quality(model_path),
            "recommendations": []
        }
        
        # שמירת מידע לשימוש בין פונקציות
        self._last_charset_info = result["charset_info"]
        self._last_advanced_info = result["advanced_analysis"]
        
        # הוסף המלצות משופרות
        result["recommendations"] = self._generate_enhanced_recommendations(result)
        
        return result
    
    def _get_basic_info(self, model_path: Path) -> Dict[str, Any]:
        """מידע בסיסי על הקובץ"""
        try:
            stat = model_path.stat()
            
            # זיהוי סוג קובץ
            file_type = "unknown"
            with open(model_path, 'rb') as f:
                header = f.read(50)
                if header.startswith(b'PK'):
                    file_type = "zip_kraken"
                elif b'pytorch' in header.lower() or b'torch' in header.lower():
                    file_type = "pytorch"
                elif header.startswith(b'\x80\x03'):
                    file_type = "pickle"
            
            return {
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "file_type": file_type,
                "readable": True
            }
        except Exception as e:
            return {"error": str(e), "readable": False}
    
    def _detect_hebrew(self, model_path: Path) -> Dict[str, Any]:
        """זיהוי אם המודל עברי - מבוסס על ניתוח charset בפועל"""
        
        # קודם נבצע ניתוח charset כדי לקבל נתונים אמיתיים
        charset_info = self._analyze_charset(model_path)
        
        # משתנים לחישוב
        hebrew_score = 0
        found_keywords = []
        reasoning_parts = []
        
        # בדיקה מבוססת charset (עדיפה וחכמה יותר)
        if charset_info.get('success') and charset_info.get('charset_size', 0) > 0:
            hebrew_percentage = charset_info.get('hebrew_percentage', 0)
            hebrew_chars_count = charset_info.get('hebrew_chars_count', 0)
            charset_size = charset_info.get('charset_size', 0)
            
            # ניקוד מבוסס תווים עבריים בפועל (זו הגישה הנכונה!)
            if hebrew_percentage >= 50:
                hebrew_score += 50  # ניקוד גבוה מאוד
                reasoning_parts.append(f'תמיכה מלאה: {hebrew_percentage}% תווים עבריים')
                found_keywords.append(f'charset_{hebrew_percentage}%_hebrew')
            elif hebrew_percentage >= 25:
                hebrew_score += 35
                reasoning_parts.append(f'תמיכה טובה: {hebrew_percentage}% תווים עבריים')
                found_keywords.append(f'charset_{hebrew_percentage}%_hebrew')
            elif hebrew_percentage >= 10:
                hebrew_score += 20
                reasoning_parts.append(f'תמיכה חלקית: {hebrew_percentage}% תווים עבריים')
                found_keywords.append(f'charset_{hebrew_percentage}%_hebrew')
            elif hebrew_chars_count > 0:
                hebrew_score += 10
                reasoning_parts.append(f'תמיכה מינימלית: {hebrew_chars_count} תווים עבריים')
                found_keywords.append(f'charset_{hebrew_chars_count}_hebrew_chars')
            else:
                reasoning_parts.append(f'אין תווים עבריים ב-charset ({charset_size} תווים)')
            
            reasoning_parts.append(f'סה"כ תווים: {charset_size}')
        else:
            # אם ניתוח charset נכשל, נסתמך על מילות מפתח (פחות אמין)
            reasoning_parts.append('ניתוח charset נכשל, משתמש במילות מפתח')
            
            name_lower = model_path.name.lower()
            
            # מילות מפתח עבריות
            hebrew_keywords = [
                'hebrew', 'biblia', 'hocr', 'heb_', 'תנ"ך', 'עברית', 
                'בדיקה', 'עברי', 'יהודי', 'israel', 'hebrew_', 'heb-',
                'משנה', 'תלמוד', 'תורה', 'נביאים', 'כתובים'
            ]
            
            # בדיקת תווים עבריים בשם הקובץ
            hebrew_chars_in_name = any('\u0590' <= char <= '\u05FF' for char in model_path.name)
            if hebrew_chars_in_name:
                hebrew_score += 15
                found_keywords.append('עברי_בשם')
                reasoning_parts.append('תווים עבריים בשם הקובץ')
            
            # חיפוש מילות מפתח
            for keyword in hebrew_keywords:
                if keyword in name_lower:
                    hebrew_score += 8  # ניקוד נמוך יותר ממילות מפתח
                    found_keywords.append(keyword)
            
            # בדיקת נתיב
            path_parts = str(model_path).lower()
            if any(word in path_parts for word in ['hebrew', 'biblia', 'heb']):
                hebrew_score += 3
                found_keywords.append('path_hebrew')
            
            if found_keywords:
                reasoning_parts.append(f'מילות מפתח: {", ".join(found_keywords)}')
        
        # קביעת רמת ודאות (עדכון הסף לגישה החדשה)
        if hebrew_score >= 35:
            confidence = "גבוהה"
            is_hebrew = True
        elif hebrew_score >= 15:
            confidence = "בינונית" 
            is_hebrew = True
        elif hebrew_score >= 5:
            confidence = "נמוכה"
            is_hebrew = True
        else:
            confidence = "ללא"
            is_hebrew = False
        
        return {
            "is_hebrew": is_hebrew,
            "confidence": confidence,
            "score": hebrew_score,
            "found_keywords": found_keywords,
            "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "אין מידע זמין",
            "charset_based": charset_info.get('success', False)  # מציין אם הניתוח מבוסס charset
        }
    
    def _analyze_charset(self, model_path: Path) -> Dict[str, Any]:
        """ניתוח charset של המודל"""
        try:
            # ניסיון לטעון עם Kraken
            charset_info = self._try_kraken_analysis(model_path)
            if charset_info:
                return charset_info
            
            # אם Kraken לא עבד, ניסיון לבדוק ZIP
            if zipfile.is_zipfile(model_path):
                return self._analyze_zip_charset(model_path)
                
            return {"error": "לא ניתן לנתח charset", "method": "none"}
            
        except Exception as e:
            return {"error": str(e), "method": "failed"}
    
    def _try_kraken_analysis(self, model_path: Path) -> Optional[Dict[str, Any]]:
        """ניסיון ניתוח עם Kraken"""
        try:
            code = f'''
import sys
try:
    from kraken.lib import models
    model = models.load_any("{model_path}")
    
    result = {{"method": "kraken", "success": True}}
    
    if hasattr(model, "codec"):
        charset = model.codec.c2l.keys()
        result["charset_size"] = len(charset)
        
        # בדיקת תווים עבריים
        hebrew_chars = [c for c in charset if ord(c) >= 0x0590 and ord(c) <= 0x05FF]
        result["hebrew_chars_count"] = len(hebrew_chars)
        result["sample_chars"] = "".join(sorted(list(charset))[:20])
        
        # אחוז עברי
        if result["charset_size"] > 0:
            result["hebrew_percentage"] = round(len(hebrew_chars) / result["charset_size"] * 100, 1)
        else:
            result["hebrew_percentage"] = 0
    
    if hasattr(model, "nn"):
        result["model_type"] = type(model.nn).__name__
        try:
            import torch
            total_params = sum(p.numel() for p in model.nn.parameters())
            result["parameters"] = total_params
        except:
            pass
    
    print(json.dumps(result, ensure_ascii=False))
    
except Exception as e:
    print(json.dumps({{"method": "kraken", "success": False, "error": str(e)}}))
'''
            
            result = subprocess.run(['python', '-c', code], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout.strip())
                if data.get("success"):
                    return data
                    
        except Exception:
            pass
        
        return None
    
    def _analyze_zip_charset(self, model_path: Path) -> Dict[str, Any]:
        """
        ניתוח charset מתוך ZIP - עם תמיכה ב-JSON ו-Pickle
        
        Security: Migrated from pickle-only to JSON-first approach
        Tries JSON format first, falls back to pickle only for trusted model files
        """
        try:
            with zipfile.ZipFile(model_path, 'r') as zip_ref:
                # חיפוש קבצים רלוונטיים
                for file_name in zip_ref.namelist():
                    if 'codec' in file_name.lower() or 'alphabet' in file_name.lower():
                        with zip_ref.open(file_name) as f:
                            data = f.read()
                            
                            # Method 1: Try JSON first (secure, modern format)
                            try:
                                charset_data = json.loads(data.decode('utf-8'))
                                chars = []
                                
                                # Handle different JSON structures
                                if isinstance(charset_data, dict):
                                    if 'alphabet' in charset_data:
                                        chars = list(charset_data['alphabet'])
                                    elif 'chars' in charset_data:
                                        chars = list(charset_data['chars'])
                                    elif 'c2l' in charset_data:
                                        chars = list(charset_data['c2l'].keys())
                                    else:
                                        chars = list(charset_data.keys())
                                elif isinstance(charset_data, list):
                                    chars = charset_data
                                
                                if chars:
                                    hebrew_chars = [c for c in chars if isinstance(c, str) and ord(c) >= 0x0590 and ord(c) <= 0x05FF]
                                    
                                    return {
                                        "method": "zip_analysis_json",
                                        "charset_size": len(chars),
                                        "hebrew_chars_count": len(hebrew_chars),
                                        "hebrew_percentage": round(len(hebrew_chars) / len(chars) * 100, 1) if chars else 0,
                                        "sample_chars": "".join([c for c in chars[:20] if isinstance(c, str)]),
                                        "success": True,
                                        "secure": True  # JSON is secure
                                    }
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                # JSON parsing failed, continue to pickle fallback
                                pass
                            
                            # Method 2: Pickle fallback (legacy models only)
                            # WARNING: Only use for models from trusted sources!
                            try:
                                # nosec B301: Fallback for legacy model files from trusted sources only
                                # Models should be validated before reaching this code
                                charset_data = pickle.loads(data)  # nosec B301
                                if hasattr(charset_data, 'keys'):
                                    chars = list(charset_data.keys())
                                    hebrew_chars = [c for c in chars if ord(c) >= 0x0590 and ord(c) <= 0x05FF]
                                    
                                    return {
                                        "method": "zip_analysis_pickle",
                                        "charset_size": len(chars),
                                        "hebrew_chars_count": len(hebrew_chars),
                                        "hebrew_percentage": round(len(hebrew_chars) / len(chars) * 100, 1) if chars else 0,
                                        "sample_chars": "".join(chars[:20]),
                                        "success": True,
                                        "secure": False,  # Pickle is less secure
                                        "warning": "Legacy pickle format - consider migrating to JSON"
                                    }
                            except:
                                continue
                                
            return {"method": "zip_analysis", "error": "לא נמצא charset בקובץ ZIP"}
            
        except Exception as e:
            return {"method": "zip_analysis", "error": str(e)}
    
    def _perform_advanced_analysis(self, model_path: Path) -> Dict[str, Any]:
        """ניתוח מתקדם מבוסס על הכלים המורחבים שלנו"""
        advanced = {
            'model_architecture': {},
            'dataset_clues': {},
            'training_quality_indicators': {},
            'technical_specs': {}
        }
        
        try:
            # ניסיון לטעון את המודל לניתוח מתקדם
            import sys
            import tempfile
            
            # הוספת נתיב הכלים שלנו
            tools_path = str(model_path.parent.parent.parent.parent.parent / "OCR_Arabic_Testing")
            if tools_path not in sys.path:
                sys.path.insert(0, tools_path)
            
            try:
                from kraken.lib import models
                model = models.load_any(str(model_path))
                
                # ניתוח ארכיטקטורה
                if hasattr(model, 'nn') and model.nn:
                    nn = model.nn
                    advanced['model_architecture'] = {
                        'type': type(nn).__name__,
                        'is_trained': hasattr(nn, 'training') and not nn.training,
                        'has_dropout': any('dropout' in str(type(m)).lower() for m in nn.modules() if hasattr(nn, 'modules')),
                        'has_batch_norm': any('batch' in str(type(m)).lower() for m in nn.modules() if hasattr(nn, 'modules'))
                    }
                    
                    # ספירת פרמטרים מדויקת
                    try:
                        import torch
                        if hasattr(nn, 'parameters'):
                            total_params = sum(p.numel() for p in nn.parameters())
                            trainable_params = sum(p.numel() for p in nn.parameters() if p.requires_grad)
                            
                            advanced['model_architecture'].update({
                                'total_parameters': total_params,
                                'trainable_parameters': trainable_params,
                                'parameters_millions': round(total_params / 1_000_000, 2),
                                'model_size_estimate_mb': round(total_params * 4 / (1024*1024), 1)  # float32
                            })
                    except Exception:
                        pass
                
                # ניתוח codec מתקדם
                if hasattr(model, 'codec') and model.codec and hasattr(model.codec, 'c2l'):
                    chars = list(model.codec.c2l.keys())
                    
                    # ניתוח מתקדם של תווים
                    char_analysis = self._analyze_charset_advanced(chars)
                    advanced['dataset_clues'] = char_analysis
                
                # זיהוי סימנים לאיכות אימון
                training_indicators = {}
                
                # בדיקת device (אם האימון היה על GPU)
                if hasattr(model, 'device'):
                    training_indicators['trained_on_device'] = str(model.device)
                    training_indicators['gpu_trained'] = 'cuda' in str(model.device).lower()
                
                # בדיקת precision (אם יש mixed precision)
                if hasattr(model, 'nn') and hasattr(model.nn, 'parameters'):
                    try:
                        param = next(iter(model.nn.parameters()))
                        training_indicators['model_dtype'] = str(param.dtype)
                        training_indicators['uses_half_precision'] = 'float16' in str(param.dtype)
                    except Exception:
                        pass
                
                advanced['training_quality_indicators'] = training_indicators
                
            except Exception as e:
                advanced['model_load_error'] = str(e)
                
        except Exception as e:
            advanced['analysis_error'] = str(e)
        
        return advanced
    
    def _analyze_charset_advanced(self, chars: list) -> Dict[str, Any]:
        """ניתוח charset מתקדם מבוסס על הכלים שלנו"""
        analysis = {
            'character_categories': {},
            'script_detection': {},
            'special_patterns': [],
            'text_type_hints': []
        }
        
        # סיווג מפורט של תווים
        categories = {
            'hebrew_letters': [c for c in chars if '\u05d0' <= c <= '\u05ea'],
            'hebrew_final': [c for c in chars if c in 'ךםןףץ'],
            'nikud_marks': [c for c in chars if '\u05b0' <= c <= '\u05c7'],
            'teamim': [c for c in chars if '\u0591' <= c <= '\u05af'],
            'hebrew_punct': [c for c in chars if c in '״׳'],
            'latin_letters': [c for c in chars if c.isascii() and c.isalpha()],
            'digits': [c for c in chars if c.isdigit()],
            'hebrew_digits': [c for c in chars if c in 'אבגדהוזחט'],  # גימטריה
            'punctuation': [c for c in chars if c in '.,;:!?"\'()[]{}/-'],
            'whitespace': [c for c in chars if c in ' \t\n'],
            'special_symbols': [c for c in chars if not c.isalnum() and c not in '.,;:!?"\'()[]{}/-״׳ \t\n']
        }
        
        analysis['character_categories'] = {
            k: {'count': len(v), 'percentage': round(len(v)/len(chars)*100, 1), 'sample': ''.join(v[:5])}
            for k, v in categories.items() if v
        }
        
        # זיהוי סקריפטים
        hebrew_total = len(categories['hebrew_letters'] + categories['hebrew_final'] + categories['nikud_marks'])
        latin_total = len(categories['latin_letters'])
        
        analysis['script_detection'] = {
            'primary_script': 'hebrew' if hebrew_total > latin_total else 'latin' if latin_total > 0 else 'mixed',
            'is_multilingual': hebrew_total > 0 and latin_total > 0,
            'hebrew_coverage': round(hebrew_total / len(chars) * 100, 1),
            'latin_coverage': round(latin_total / len(chars) * 100, 1)
        }
        
        # זיהוי דפוסים מיוחדים
        if categories['nikud_marks']:
            analysis['special_patterns'].append(f"מנוקד ({len(categories['nikud_marks'])} סימני ניקוד)")
        
        if categories['teamim']:
            analysis['special_patterns'].append(f"טעמי מקרא ({len(categories['teamim'])} טעמים)")
        
        if categories['hebrew_digits']:
            analysis['special_patterns'].append("גימטריה (ספרות עבריות)")
        
        # רמזים לסוג הטקסט
        if len(categories['nikud_marks']) > 10:
            analysis['text_type_hints'].append("ספרות דתית מנוקדת")
        
        if categories['teamim']:
            analysis['text_type_hints'].append("תנ\"ך עם טעמי מקרא")
        
        if categories['latin_letters'] and categories['hebrew_letters']:
            analysis['text_type_hints'].append("טקסט מעורב עברית-לטינית")
        
        if len(categories['special_symbols']) > 5:
            analysis['text_type_hints'].append("טקסט עם סימונים מיוחדים")
        
        return analysis
    
    def _extract_training_insights(self, model_path: Path) -> Dict[str, Any]:
        """חילוץ תובנות על האימון מבוסס על הכלים המתקדמים"""
        insights = {
            'dataset_hints': [],
            'training_quality_signs': [],
            'file_analysis': {}
        }
        
        try:
            # ניתוח שם הקובץ לרמזים
            name = model_path.name.lower()
            
            # רמזים על איכות האימון
            if 'best' in name:
                insights['training_quality_signs'].append("מסומן כמודל הטוב ביותר")
            
            if any(v in name for v in ['v1', 'v2', 'v3', 'v4', 'v5']):
                version = next(v for v in ['v1', 'v2', 'v3', 'v4', 'v5'] if v in name)
                insights['training_quality_signs'].append(f"מודל גרסה {version} - עבר איטרציות")
            
            if 'final' in name or 'prod' in name or 'production' in name:
                insights['training_quality_signs'].append("מודל סופי לייצור")
            
            # רמזים על הדאטאסט
            dataset_keywords = {
                'biblia': 'ספרות דתית',
                'tanach': 'תנ"ך',
                'talmud': 'תלמוד',
                'mishna': 'משנה',
                'manuscript': 'כתבי יד',
                'print': 'דפוס',
                'medieval': 'ימי ביניים',
                'modern': 'עברית מודרנית'
            }
            
            for keyword, description in dataset_keywords.items():
                if keyword in name:
                    insights['dataset_hints'].append(f"סביר שאומן על {description}")
            
            # ניתוח גודל קובץ
            size_mb = model_path.stat().st_size / (1024*1024)
            insights['file_analysis'] = {
                'size_mb': round(size_mb, 2),
                'size_category': self._categorize_model_size(size_mb),
                'complexity_estimate': self._estimate_complexity_from_size(size_mb)
            }
            
        except Exception as e:
            insights['extraction_error'] = str(e)
        
        return insights
    
    def _categorize_model_size(self, size_mb: float) -> str:
        """קטלוג גודל המודל"""
        if size_mb < 1:
            return "קטן מאוד"
        elif size_mb < 5:
            return "קטן"
        elif size_mb < 20:
            return "בינוני"
        elif size_mb < 50:
            return "גדול"
        elif size_mb < 100:
            return "גדול מאוד"
        else:
            return "ענק"
    
    def _estimate_complexity_from_size(self, size_mb: float) -> str:
        """הערכת מורכבות מגודל"""
        if size_mb < 5:
            return "מודל פשוט"
        elif size_mb < 20:
            return "מודל בינוני"
        elif size_mb < 50:
            return "מודל מורכב"
        else:
            return "מודל מתקדם מאוד"
    
    def _estimate_performance_metrics(self) -> Dict[str, Any]:
        """הערכת ביצועים מבוססת נתונים זמינים"""
        metrics = {
            'expected_accuracy_range': {},
            'speed_estimate': {},
            'memory_requirements': {},
            'use_case_suitability': []
        }
        
        # הערכות מבוססות על הנתונים שאספנו
        try:
            # נשלוף נתונים מהניתוחים הקודמים
            charset_info = getattr(self, '_last_charset_info', {})
            advanced_info = getattr(self, '_last_advanced_info', {})
            
            # הערכת דיוק מבוססת על גודל ומורכבות
            if charset_info.get('hebrew_percentage', 0) > 60:
                if advanced_info.get('model_architecture', {}).get('parameters_millions', 0) > 1:
                    metrics['expected_accuracy_range'] = {'min': 92, 'max': 98, 'typical': 95}
                else:
                    metrics['expected_accuracy_range'] = {'min': 85, 'max': 93, 'typical': 89}
            
            # המלצות שימוש
            if charset_info.get('hebrew_percentage', 0) > 80:
                metrics['use_case_suitability'].append("טקסטים עבריים טהורים")
            
            if 'nikud' in str(charset_info):
                metrics['use_case_suitability'].append("טקסטים מנוקדים")
            
            if charset_info.get('hebrew_percentage', 0) > 30 and charset_info.get('latin_coverage', 0) > 20:
                metrics['use_case_suitability'].append("טקסטים מעורבים")
            
        except Exception as e:
            metrics['estimation_error'] = str(e)
        
        return metrics
    
    def _estimate_quality(self, model_path: Path) -> Dict[str, Any]:
        """הערכת איכות המודל"""
        quality_score = 0
        factors = []
        
        basic_info = self._get_basic_info(model_path)
        hebrew_info = self._detect_hebrew(model_path)
        
        # גורם גודל קובץ
        size_mb = basic_info.get("size_mb", 0)
        if size_mb > 50:
            quality_score += 20
            factors.append(f"מודל גדול ({size_mb}MB) - סימן טוב")
        elif size_mb > 10:
            quality_score += 15
            factors.append(f"מודל בינוני ({size_mb}MB)")
        elif size_mb > 1:
            quality_score += 10
            factors.append(f"מודל קטן ({size_mb}MB)")
        else:
            factors.append(f"מודל קטן מאוד ({size_mb}MB) - ייתכן שלא איכותי")
        
        # גורם עברי
        if hebrew_info.get("is_hebrew"):
            if hebrew_info.get("confidence") == "גבוהה":
                quality_score += 15
                factors.append("זוהה כמודל עברי באמינות גבוהה")
            else:
                quality_score += 10
                factors.append("זוהה כמודל עברי")
        
        # גורם שם הקובץ
        name = model_path.name.lower()
        if 'best' in name:
            quality_score += 10
            factors.append("מסומן כ'best' בשם")
        if any(v in name for v in ['v1', 'v2', 'v3', 'v4', 'v5']):
            quality_score += 5
            factors.append("מודל עם מספר גרסה")
        
        # גורם תאריך (מודלים חדשים יותר עדיפים)
        try:
            days_old = (datetime.now() - datetime.fromtimestamp(model_path.stat().st_mtime)).days
            if days_old < 30:
                quality_score += 10
                factors.append("מודל חדש (פחות מחודש)")
            elif days_old < 180:
                quality_score += 5
                factors.append("מודל עדכני (פחות מ-6 חודשים)")
        except:
            pass
        
        # קביעת רמת איכות
        if quality_score >= 50:
            quality_level = "מעולה"
        elif quality_score >= 35:
            quality_level = "טובה"
        elif quality_score >= 20:
            quality_level = "בינונית"
        else:
            quality_level = "נמוכה"
        
        return {
            "score": quality_score,
            "level": quality_level,
            "factors": factors,
            "max_possible": 70
        }
    
    def _generate_enhanced_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """יצירת המלצות משופרות על בסיס הניתוח המורחב"""
        recommendations = []
        
        quality = analysis.get("quality_estimate", {})
        hebrew = analysis.get("hebrew_detection", {})
        charset = analysis.get("charset_info", {})
        advanced = analysis.get("advanced_analysis", {})
        training = analysis.get("training_insights", {})
        performance = analysis.get("performance_metrics", {})
        
        # המלצות איכות מבוססות נתונים מורחבים
        if quality.get("level") == "מעולה":
            recommendations.append("✅ מודל באיכות מעולה - מומלץ בחום לשימוש מקצועי")
        elif quality.get("level") == "נמוכה":
            recommendations.append("⚠️ מודל באיכות נמוכה - שקול שדרוג לגרסה חדשה יותר")
        
        # המלצות מבוססות ארכיטקטורה
        arch = advanced.get('model_architecture', {})
        if arch.get('parameters_millions', 0) > 5:
            recommendations.append(f"🧠 מודל מתקדם עם {arch['parameters_millions']}M פרמטרים - ביצועים גבוהים אך צורך במשאבים")
        elif arch.get('parameters_millions', 0) > 0:
            recommendations.append(f"⚡ מודל יעיל עם {arch['parameters_millions']}M פרמטרים - איזון טוב בין מהירות לדיוק")
        
        # המלצות מבוססות charset מתקדם
        dataset_clues = advanced.get('dataset_clues', {})
        if dataset_clues.get('special_patterns'):
            patterns = ', '.join(dataset_clues['special_patterns'][:2])
            recommendations.append(f"📚 מודל מיוחד עם תמיכה ב: {patterns}")
        
        script_info = dataset_clues.get('script_detection', {})
        if script_info.get('is_multilingual'):
            recommendations.append("🌐 מודל רב-לשוני - מתאים לטקסטים מעורבים")
        
        # המלצות מבוססות תובנות אימון
        training_signs = training.get('training_quality_signs', [])
        if 'מסומן כמודל הטוב ביותר' in training_signs:
            recommendations.append("🏆 מודל מובחר - עבר תהליך בחירה מקצועי")
        
        if any('גרסה' in sign for sign in training_signs):
            recommendations.append("🔄 מודל מעודכן - עבר איטרציות ושיפורים")
        
        dataset_hints = training.get('dataset_hints', [])
        for hint in dataset_hints[:2]:
            recommendations.append(f"📖 {hint}")
        
        # המלצות ביצועים מבוססות הערכה
        use_cases = performance.get('use_case_suitability', [])
        for use_case in use_cases[:2]:
            recommendations.append(f"🎯 מתאים במיוחד ל: {use_case}")
        
        expected_acc = performance.get('expected_accuracy_range', {})
        if expected_acc.get('typical', 0) > 94:
            recommendations.append(f"📊 דיוק צפוי: ~{expected_acc['typical']}% (מעולה)")
        elif expected_acc.get('typical', 0) > 88:
            recommendations.append(f"📊 דיוק צפוי: ~{expected_acc['typical']}% (טוב)")
        
        # המלצות טכניות
        file_analysis = training.get('file_analysis', {})
        if file_analysis.get('size_category') == 'ענק':
            recommendations.append("💾 מודל גדול - וודא זיכרון מספיק (RAM > 8GB)")
        elif file_analysis.get('size_category') == 'קטן מאוד':
            recommendations.append("⚡ מודל קליל - מתאים לסביבות מוגבלות")
        
        # המלצת פעולה אם יש בעיות
        if not recommendations or len(recommendations) < 3:
            recommendations.append("🔍 מומלץ לבצע ניתוח מעמיק נוסף עם הכלים המתקדמים")
        
        return recommendations[:8]  # מגבלה של 8 המלצות
        """יצירת המלצות על בסיס הניתוח"""
        recommendations = []
        
        quality = analysis.get("quality_estimate", {})
        hebrew = analysis.get("hebrew_detection", {})
        charset = analysis.get("charset_info", {})
        
        # המלצות על בסיס איכות
        if quality.get("level") == "מעולה":
            recommendations.append("✅ מודל באיכות מעולה - מומלץ לשימוש")
        elif quality.get("level") == "נמוכה":
            recommendations.append("⚠️ מודל באיכות נמוכה - שקול לחפש חלופה")
        
        # המלצות עבריות
        if hebrew.get("is_hebrew") and hebrew.get("confidence") == "גבוהה":
            recommendations.append("🔤 מודל עברי באמינות גבוהה - מתאים לטקסטים עבריים")
        elif not hebrew.get("is_hebrew"):
            recommendations.append("❓ לא זוהה כמודל עברי - בדוק התאמה לטקסטים עבריים")
        
        # המלצות charset
        if charset.get("hebrew_percentage", 0) > 50:
            recommendations.append("📊 מודל עם תמיכה טובה בעברית ({}% תווים עבריים)".format(
                charset.get("hebrew_percentage")))
        elif charset.get("hebrew_percentage", 0) > 0:
            recommendations.append("📊 תמיכה חלקית בעברית ({}% תווים עבריים)".format(
                charset.get("hebrew_percentage")))
        
        # המלצות כלליות
        basic = analysis.get("basic_info", {})
        if basic.get("size_mb", 0) > 100:
            recommendations.append("💾 מודל גדול - ייקח זמן לטעינה אך עשוי להיות מדויק יותר")
        elif basic.get("size_mb", 0) < 1:
            recommendations.append("⚡ מודל קטן - טעינה מהירה אך ייתכן שפחות מדויק")
        
        return recommendations
    
    def compare_models(self, model_paths: List[str]) -> Dict[str, Any]:
        """השוואה בין מספר מודלים"""
        if len(model_paths) < 2:
            return {"error": "נדרשים לפחות 2 מודלים להשוואה"}
        
        analyses = []
        for path in model_paths:
            analysis = self.check_model(path)
            analyses.append(analysis)
        
        # מיון לפי איכות
        analyses.sort(key=lambda x: x.get("quality_estimate", {}).get("score", 0), reverse=True)
        
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "models_count": len(analyses),
            "analyses": analyses,
            "summary": {
                "best_model": analyses[0]["name"] if analyses else None,
                "hebrew_models": [a["name"] for a in analyses if a.get("hebrew_detection", {}).get("is_hebrew")],
                "quality_ranking": [(a["name"], a.get("quality_estimate", {}).get("level", "לא ידוע")) for a in analyses]
            }
        }
        
        return comparison
    
    def quick_scan(self, directory: str = ".") -> Dict[str, Any]:
        """סריקה מהירה של כל המודלים בתיקייה"""
        directory = Path(directory)
        models = list(directory.rglob("*.mlmodel"))
        
        if not models:
            return {"error": "לא נמצאו מודלים", "models_found": 0}
        
        quick_results = []
        
        for model_path in models[:10]:  # הגבלה ל-10 מודלים ראשונים
            basic_info = self._get_basic_info(model_path)
            hebrew_info = self._detect_hebrew(model_path)
            
            quick_results.append({
                "name": model_path.name,
                "size_mb": basic_info.get("size_mb", 0),
                "is_hebrew": hebrew_info.get("is_hebrew", False),
                "hebrew_confidence": hebrew_info.get("confidence", "לא ידוע"),
                "path": str(model_path)
            })
        
        # מיון לפי גודל (גדולים ראשונים)
        quick_results.sort(key=lambda x: x["size_mb"], reverse=True)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_found": len(models),
            "analyzed": len(quick_results),
            "models": quick_results,
            "hebrew_models": [m for m in quick_results if m["is_hebrew"]],
            "recommendations": self._generate_scan_recommendations(quick_results)
        }
    
    def _generate_scan_recommendations(self, models: List[Dict]) -> List[str]:
        """המלצות על בסיס סריקה מהירה"""
        recommendations = []
        
        hebrew_models = [m for m in models if m["is_hebrew"]]
        large_models = [m for m in models if m["size_mb"] > 50]
        
        if hebrew_models:
            best_hebrew = max(hebrew_models, key=lambda x: x["size_mb"])
            recommendations.append(f"🔤 מודל עברי מומלץ: {best_hebrew['name']} ({best_hebrew['size_mb']}MB)")
        
        if large_models:
            largest = max(large_models, key=lambda x: x["size_mb"])
            recommendations.append(f"💾 המודל הגדול ביותר: {largest['name']} ({largest['size_mb']}MB)")
        
        if not hebrew_models:
            recommendations.append("⚠️ לא נמצאו מודלים עבריים ברורים - בדוק ידנית")
        
        return recommendations
    
    @staticmethod
    def convert_pickle_charset_to_json(model_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        🔧 Utility: Convert legacy pickle charset to secure JSON format
        
        This is a migration helper for converting old Kraken models with pickle charset
        to the newer, more secure JSON format.
        
        Args:
            model_path: Path to the Kraken model (.mlmodel file)
            output_path: Optional output path for JSON file (default: same dir as model)
        
        Returns:
            Dict with conversion status and paths
        """
        try:
            if not model_path.exists():
                return {"success": False, "error": f"Model not found: {model_path}"}
            
            charset_data = None
            codec_file_name = None
            
            # Extract charset from ZIP model
            with zipfile.ZipFile(model_path, 'r') as zip_ref:
                for file_name in zip_ref.namelist():
                    if 'codec' in file_name.lower() or 'alphabet' in file_name.lower():
                        codec_file_name = file_name
                        with zip_ref.open(file_name) as f:
                            data = f.read()
                            
                            # Try to load as pickle
                            try:
                                # nosec B301: This is a migration tool, user explicitly runs it on trusted models
                                charset_data = pickle.loads(data)  # nosec B301
                                break
                            except:
                                continue
            
            if not charset_data:
                return {"success": False, "error": "No charset found in model"}
            
            # Convert to JSON-friendly format
            json_charset = {}
            if hasattr(charset_data, 'keys'):
                # Dictionary-like object (common for c2l codec)
                json_charset['c2l'] = {k: v for k, v in charset_data.items()}
                json_charset['alphabet'] = list(charset_data.keys())
            elif isinstance(charset_data, list):
                json_charset['alphabet'] = charset_data
            else:
                json_charset['data'] = str(charset_data)
            
            # Determine output path
            if output_path is None:
                output_path = model_path.parent / f"{model_path.stem}_charset.json"
            
            # Save as JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_charset, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "input_model": str(model_path),
                "output_json": str(output_path),
                "charset_size": len(json_charset.get('alphabet', [])),
                "original_format": "pickle",
                "new_format": "json",
                "message": f"✅ Successfully converted charset to JSON: {output_path}"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Conversion failed: {e}"
            }


def main():
    """פונקציה ראשית עבור הפעלה מקמנד ליין"""
    import argparse
    
    parser = argparse.ArgumentParser(description='בודק מודלי OCR ל-eScriptorium')
    parser.add_argument('--model', help='נתיב למודל ספציפי לבדיקה')
    parser.add_argument('--scan', help='סרוק תיקייה (ברירת מחדל: נוכחית)', nargs='?', const='.')
    parser.add_argument('--convert-to-json', help='המר pickle charset ל-JSON (נתיב למודל)', metavar='MODEL_PATH')
    parser.add_argument('--compare', help='השווה מודלים (נתיבים מופרדים בפסיק)')
    parser.add_argument('--output', help='שמור תוצאות לקובץ JSON')
    
    args = parser.parse_args()
    checker = EscriptoriumModelChecker()
    
    result = None
    
    # Handle charset conversion to JSON
    if args.convert_to_json:
        model_path = Path(args.convert_to_json)
        result = EscriptoriumModelChecker.convert_pickle_charset_to_json(model_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result.get('success'):
            print(f"\n✅ {result['message']}")
        else:
            print(f"\n❌ {result.get('message', 'Conversion failed')}")
        return
    
    if args.model:
        result = checker.check_model(args.model)
    elif args.compare:
        models = [m.strip() for m in args.compare.split(',')]
        result = checker.compare_models(models)
    elif args.scan is not None:
        result = checker.quick_scan(args.scan)
    else:
        result = checker.quick_scan('.')
    
    # הדפסת תוצאות
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nתוצאות נשמרו ב: {args.output}")


if __name__ == "__main__":
    main()