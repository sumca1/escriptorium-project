#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BiblIA Translation Loader - טוען תרגומים מקובץ מאוחד
=======================================================

מטרה: לספק גישה פשוטה לכל התרגומים מקובץ אחד מרכזי.

שימוש:
    from translations.translation_loader import t
    
    # שימוש פשוט
    text = t('Home')  # → 'בית'
    text = t('ui.Close')  # → 'סגור' (עם קטגוריה)
    
    # עם placeholders
    text = t('Project shared with {count} users', count=5)
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

class TranslationLoader:
    """טוען תרגומים פשוט וי עיל"""
    
    _instance: Optional['TranslationLoader'] = None
    _translations: Dict[str, Any] = {}
    _flat_cache: Dict[str, str] = {}  # מטמון שטוח לחיפוש מהיר
    
    def __new__(cls):
        """Singleton - instance יחיד"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load()
        return cls._instance
    
    def load(self, lang: str = 'he') -> None:
        """טוען תרגומים מ-JSON"""
        translation_file = Path(__file__).parent / f'unified_{lang}.json'
        
        try:
            with open(translation_file, 'r', encoding='utf-8') as f:
                self._translations = json.load(f)
            
            # בונה מטמון שטוח לחיפוש מהיר
            self._build_flat_cache()
            
        except FileNotFoundError:
            print(f"⚠️  Warning: {translation_file} not found")
            self._translations = {}
            self._flat_cache = {}
    
    def _build_flat_cache(self) -> None:
        """בונה מטמון שטוח מהמבנה המקונן
        
        מאפשר חיפוש מהיר:
        - 'Home' → 'בית'
        - 'ui.Home' → 'בית'
        """
        self._flat_cache = {}
        
        for category, translations in self._translations.items():
            if isinstance(translations, dict):
                for key, value in translations.items():
                    # הוספה ללא קטגוריה
                    if key not in self._flat_cache:
                        self._flat_cache[key] = value
                    
                    # הוספה עם קטגוריה
                    full_key = f"{category}.{key}"
                    self._flat_cache[full_key] = value
    
    def get(self, key: str, **kwargs) -> str:
        """מחזיר תרגום
        
        Args:
            key: מפתח (עם או בלי קטגוריה)
            **kwargs: פרמטרים להחלפה
        
        Returns:
            התרגום או המפתח אם לא נמצא
        
        דוגמאות:
            >>> t.get('Home')
            'בית'
            
            >>> t.get('ui.Close')
            'סגור'
            
            >>> t.get('shared with {count} users', count=5)
            'משותף עם 5 משתמשים'
        """
        # חיפוש במטמון
        translation = self._flat_cache.get(key, key)
        
        # החלפת placeholders
        if kwargs and '{' in translation:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return translation
    
    def __call__(self, key: str, **kwargs) -> str:
        """מאפשר שימוש ישיר: t('Home')"""
        return self.get(key, **kwargs)
    
    def exists(self, key: str) -> bool:
        """בודק אם תרגום קיים"""
        return key in self._flat_cache
    
    def get_category(self, category: str) -> Dict[str, str]:
        """מחזיר את כל התרגומים בקטגוריה"""
        return self._translations.get(category, {})
    
    def search(self, search_term: str, limit: int = 20) -> list:
        """מחפש תרגומים
        
        Args:
            search_term: מה לחפש
            limit: מקסימום תוצאות
        
        Returns:
            רשימת (key, value) שמתאימים
        """
        results = []
        search_lower = search_term.lower()
        
        for key, value in self._flat_cache.items():
            if (search_lower in key.lower() or 
                search_lower in value.lower()):
                results.append((key, value))
                
                if len(results) >= limit:
                    break
        
        return results

# Instance גלובלי
_loader = TranslationLoader()

# פונקציה גלובלית לשימוש קל
def t(key: str, **kwargs) -> str:
    """פונקציה גלובלית לתרגום
    
    שימוש:
        from translations.translation_loader import t
        text = t('Home')
    """
    return _loader.get(key, **kwargs)

# Django template tag (אופציונלי)
try:
    from django import template
    from django.utils.safestring import mark_safe
    
    register = template.Library()
    
    @register.simple_tag
    def trans(key: str, **kwargs) -> str:
        """Django template tag
        
        שימוש:
            {% load translation_loader %}
            {% trans 'Home' %}
        """
        return t(key, **kwargs)
    
    @register.filter
    def translate(key: str) -> str:
        """Django filter
        
        שימוש:
            {{ 'Home'|translate }}
        """
        return t(key)
        
except ImportError:
    pass  # Django לא מותקן
