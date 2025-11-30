# Spell Checker Module - BiblIA Enhancement
# Created: 2025-10-20
# Purpose: Hebrew spell checking with Hunspell integration
# Focus: Hebrew text (Arabic only for confusion character patterns)

import logging
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Try to import hunspell - CyHunspell implementation
try:
    from hunspell import Hunspell
    HUNSPELL_AVAILABLE = True
except ImportError:
    logger.warning("Hunspell not available - spell checking disabled")
    HUNSPELL_AVAILABLE = False

# Fallback language detection
try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    logger.warning("langdetect not available - using fallback")
    LANGDETECT_AVAILABLE = False


class SpellChecker:
    """
    בודק איות לעברית עם תמיכה בתבניות שגיאה
    Hebrew spell checker with error pattern support
    
    Focus: Hebrew text accuracy for OCR error detection
    """
    
    def __init__(self):
        """Initialize spell checker with Hebrew dictionary"""
        self.checkers = {}
        self.custom_words = set()
        
        if HUNSPELL_AVAILABLE:
            try:
                # Initialize Hebrew checker with CyHunspell
                self.checkers['he'] = Hunspell(
                    'he_IL', 
                    hunspell_data_dir='/usr/share/hunspell'
                )
                logger.info("Hebrew spell checker initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Hebrew spell checker: {e}")
        
        # Load custom dictionary from database
        self._load_custom_dictionary()
    
    def check_line(self, text: str, language: str = 'he') -> List[Dict]:
        """
        בודק שורת טקסט ומחזיר רשימת שגיאות
        Check a line of text and return list of errors
        
        Args:
            text: Text to check
            language: Language code (default: 'he' for Hebrew)
        
        Returns:
            List of error dictionaries:
            [{'word': 'שגוי', 'position': 3, 'suggestions': ['נכון', ...]}, ...]
        """
        if not HUNSPELL_AVAILABLE:
            logger.warning("Hunspell not available - cannot check spelling")
            return []
        
        if not text or not text.strip():
            return []
        
        # Auto-detect language if not specified
        if language is None:
            language = self._detect_language(text)
        
        checker = self.checkers.get(language)
        if not checker:
            logger.warning(f"No spell checker available for language: {language}")
            return []
        
        errors = []
        words = self._tokenize(text, language)
        
        for i, word_info in enumerate(words):
            word = word_info['word']
            position = word_info['position']
            
            # Skip custom dictionary words
            if word.lower() in self.custom_words:
                continue
            
            # Skip very short words (likely punctuation or artifacts)
            if len(word) < 2:
                continue
            
            # Check spelling
            try:
                if not checker.spell(word):
                    suggestions = checker.suggest(word)[:5]  # Top 5 suggestions
                    errors.append({
                        'word': word,
                        'position': position,
                        'suggestions': suggestions,
                        'error_type': 'spelling'
                    })
            except Exception as e:
                logger.error(f"Error checking word '{word}': {e}")
        
        return errors
    
    def _detect_language(self, text: str) -> str:
        """
        זיהוי שפה אוטומטי
        Auto-detect language from text
        
        Args:
            text: Text to analyze
        
        Returns:
            Language code ('he', 'ar', 'en')
        """
        if not LANGDETECT_AVAILABLE:
            # Fallback: check for Hebrew characters
            if re.search(r'[\u0590-\u05FF]', text):
                return 'he'
            return 'he'  # Default to Hebrew for BiblIA
        
        try:
            lang = detect(text)
            # Map detected language to our supported languages
            if lang in ['he', 'iw']:  # iw is old Hebrew code
                return 'he'
            elif lang == 'ar':
                return 'ar'
            elif lang == 'en':
                return 'en'
            else:
                return 'he'  # Default to Hebrew
        except Exception as e:
            logger.warning(f"Language detection failed: {e}, defaulting to Hebrew")
            return 'he'
    
    def _tokenize(self, text: str, language: str = 'he') -> List[Dict]:
        """
        פיצול טקסט למילים עם מיקומים
        Split text into words with positions
        
        Args:
            text: Text to tokenize
            language: Language code
        
        Returns:
            List of {'word': str, 'position': int}
        """
        words = []
        
        if language == 'he':
            # Hebrew tokenization - includes Hebrew letters and מקף (hyphen)
            pattern = r'[\u0590-\u05FF\u05F0-\u05F4]+'  # Hebrew block + ligatures
        elif language == 'ar':
            # Arabic tokenization
            pattern = r'[\u0600-\u06FF\u0750-\u077F]+'  # Arabic blocks
        else:
            # Default/English tokenization
            pattern = r'\b[a-zA-Z]+\b'
        
        for match in re.finditer(pattern, text):
            words.append({
                'word': match.group(),
                'position': match.start()
            })
        
        return words
    
    def _load_custom_dictionary(self):
        """
        טוען מילון מותאם אישית מהדאטה-בייס
        Load custom dictionary from database
        """
        try:
            from core.models_errors import CustomDictionaryWord
            custom_words = CustomDictionaryWord.objects.values_list('word', flat=True)
            self.custom_words = set(word.lower() for word in custom_words)
            logger.info(f"Loaded {len(self.custom_words)} custom dictionary words")
        except Exception as e:
            logger.warning(f"Could not load custom dictionary: {e}")
            self.custom_words = set()
    
    def add_to_custom_dictionary(self, word: str, language: str = 'he', user=None):
        """
        הוספת מילה למילון מותאם אישית
        Add word to custom dictionary
        
        Args:
            word: Word to add
            language: Language code
            user: User who added the word (optional)
        """
        try:
            from core.models_errors import CustomDictionaryWord
            obj, created = CustomDictionaryWord.objects.get_or_create(
                word=word.lower(),
                defaults={
                    'language': language,
                    'added_by': user
                }
            )
            if created:
                self.custom_words.add(word.lower())
                logger.info(f"Added '{word}' to custom dictionary")
            else:
                obj.increment_usage()
                logger.info(f"Word '{word}' already in custom dictionary, incremented usage")
        except Exception as e:
            logger.error(f"Failed to add word to custom dictionary: {e}")
    
    def reload_custom_dictionary(self):
        """
        טוען מחדש את המילון המותאם אישית
        Reload custom dictionary from database
        """
        self._load_custom_dictionary()


# Singleton instance
_spell_checker_instance = None


def get_spell_checker() -> SpellChecker:
    """
    קבל מופע יחיד של בודק האיות
    Get singleton spell checker instance
    
    Returns:
        SpellChecker instance
    """
    global _spell_checker_instance
    if _spell_checker_instance is None:
        _spell_checker_instance = SpellChecker()
    return _spell_checker_instance
