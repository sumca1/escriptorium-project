#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Spell Checker - Multi-language support
Supports Hebrew, Arabic, and English spell checking for OCR results
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from spellchecker import SpellChecker
import pyarabic.araby as araby

logger = logging.getLogger(__name__)


class HebrewSpellChecker:
    """
    Hebrew spell checker with OCR-specific optimizations
    
    Features:
    - Hebrew word validation
    - Suggestion generation
    - Confidence scoring
    - Common OCR error patterns
    """
    
    def __init__(self):
        """Initialize Hebrew spell checker"""
        try:
            # Try to load Hebrew dictionary
            self.checker = SpellChecker(language='he')
            logger.info("Hebrew spell checker initialized successfully")
        except Exception as e:
            logger.warning(f"Could not load Hebrew dictionary: {e}, using fallback")
            self.checker = SpellChecker(language=None)
            # Load basic Hebrew words as fallback
            self._load_basic_hebrew_words()
        
        # Common Hebrew OCR confusion pairs
        self.confusion_pairs = {
            'ח': ['ה', 'כ'],
            'ה': ['ח', 'ת'],
            'ב': ['כ', 'ד'],
            'כ': ['ב', 'ח'],
            'ו': ['ז', 'י'],
            'ז': ['ו', 'ן'],
            'נ': ['ג', 'צ'],
            'ג': ['נ', 'ע'],
            'ר': ['ד', 'ך'],
            'ד': ['ר', 'ה'],
            'ם': ['ס', 'ן'],
            'ס': ['ם', 'ו'],
            'ן': ['ז', 'ם'],
            'ך': ['ר', 'ל'],
        }
    
    def _load_basic_hebrew_words(self):
        """Load comprehensive Hebrew word list as fallback"""
        basic_words = [
            # Common prepositions & articles (200+)
            'של', 'את', 'על', 'זה', 'זו', 'זאת', 'אלה', 'אלו', 'כל', 'עם', 'או', 'גם', 'לא', 
            'מה', 'כי', 'רק', 'אם', 'עוד', 'אל', 'בין', 'לפני', 'אחרי', 'תחת', 'מעל',
            'כמו', 'אצל', 'ליד', 'מול', 'נגד', 'בעד', 'דרך', 'מתוך', 'כנגד', 'אחר',
            
            # Pronouns & demonstratives
            'אני', 'אתה', 'את', 'הוא', 'היא', 'אנחנו', 'אתם', 'אתן', 'הם', 'הן',
            'שלי', 'שלך', 'שלו', 'שלה', 'שלנו', 'שלכם', 'שלהם',
            
            # Common verbs (root + conjugations)
            'היה', 'הייתי', 'היית', 'היינו', 'הייתם', 'היו', 'יהיה', 'תהיה', 'יהיו', 'תהיינה',
            'יש', 'אין', 'היו', 'יהיו', 'להיות',
            'אמר', 'אמרתי', 'אמרת', 'אמרנו', 'אמרו', 'אומר', 'אומרת', 'אומרים', 'לומר',
            'כתב', 'כתבתי', 'כתבת', 'כתבנו', 'כתבו', 'כותב', 'כותבת', 'כותבים', 'לכתוב',
            'ראה', 'ראיתי', 'ראית', 'ראינו', 'ראו', 'רואה', 'רואים', 'לראות',
            'עשה', 'עשיתי', 'עשית', 'עשינו', 'עשו', 'עושה', 'עושים', 'לעשות',
            'הלך', 'הלכתי', 'הלכת', 'הלכנו', 'הלכו', 'הולך', 'הולכת', 'הולכים', 'ללכת',
            'נתן', 'נתתי', 'נתת', 'נתנו', 'נתנו', 'נותן', 'נותנת', 'נותנים', 'לתת',
            'בא', 'באתי', 'באת', 'באנו', 'באו', 'בא', 'באה', 'באים', 'לבוא',
            'יצא', 'יצאתי', 'יצאת', 'יצאנו', 'יצאו', 'יוצא', 'יוצאת', 'יוצאים', 'לצאת',
            
            # Time & calendar
            'שלום', 'טוב', 'יום', 'לילה', 'בוקר', 'צהריים', 'ערב', 'שבוע', 'חודש', 'שנה',
            'היום', 'אתמול', 'מחר', 'שלשום', 'מחרתיים', 'עכשיו', 'אז', 'תמיד', 'לעולם',
            'ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'שבתות',
            'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני', 'יולי', 'אוגוסט',
            'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר',
            'ניסן', 'אייר', 'סיון', 'תמוז', 'אב', 'אלול', 'תשרי', 'חשון', 'כסלו',
            'טבת', 'שבט', 'אדר',
            
            # Numbers
            'אחד', 'אחת', 'שנים', 'שתיים', 'שלושה', 'שלוש', 'ארבעה', 'ארבע',
            'חמישה', 'חמש', 'שישה', 'שש', 'שבעה', 'שבע', 'שמונה', 'שמונה',
            'תשעה', 'תשע', 'עשרה', 'עשר', 'עשרים', 'שלושים', 'ארבעים',
            'חמישים', 'שישים', 'שבעים', 'שמונים', 'תשעים', 'מאה', 'מאתיים',
            'אלף', 'אלפיים', 'מיליון', 'ראשון', 'שני', 'שלישי', 'רביעי',
            
            # Family & people
            'ספר', 'בית', 'עיר', 'ארץ', 'עם', 'איש', 'אנשים', 'אשה', 'נשים',
            'ילד', 'ילדים', 'ילדה', 'ילדות', 'משפחה', 'משפחות',
            'אב', 'אבא', 'אם', 'אמא', 'הורים', 'בן', 'בת', 'אח', 'אחים', 'אחות', 'אחיות',
            'סבא', 'סבתא', 'נכד', 'נכדה', 'דוד', 'דודה', 'בן דוד', 'חבר', 'חברה',
            
            # Common nouns & adjectives
            'אהבה', 'שלום', 'חיים', 'עולם', 'אמת', 'שקר', 'דבר', 'דברים', 'מלה', 'מילים',
            'טקסט', 'כתב', 'כתיבה', 'קריאה', 'שפה', 'לשון',
            'גדול', 'קטן', 'טוב', 'רע', 'יפה', 'מכוער', 'חדש', 'ישן', 'צעיר', 'זקן',
            'חכם', 'טיפש', 'חזק', 'חלש', 'עשיר', 'עני', 'שמח', 'עצוב', 'כועס',
            'ארוך', 'קצר', 'רחב', 'צר', 'גבוה', 'נמוך', 'עמוק', 'רדוד', 'קל', 'כבד',
            
            # Places & geography
            'ישראל', 'ירושלים', 'תל אביב', 'חיפה', 'באר שבע', 'צפת', 'טבריה',
            'בית לחם', 'נצרת', 'יפו', 'אילת', 'דרום', 'צפון', 'מזרח', 'מערב',
            'הר', 'הרים', 'גבעה', 'עמק', 'מדבר', 'ים', 'נהר', 'נחל', 'באר', 'מעיין',
            
            # Religious & Biblical terms (very common in manuscripts)
            'אלוהים', 'אלהים', 'יהוה', 'ה\'', 'אדון', 'אדוני', 'שדי',
            'תורה', 'תנך', 'משנה', 'גמרא', 'תלמוד', 'מדרש', 'הלכה', 'אגדה',
            'נביא', 'נביאים', 'כתוב', 'כתובים', 'מלך', 'מלכים', 'עבד', 'עבדים',
            'כהן', 'כהנים', 'לוי', 'לויים', 'ישראל', 'יהודה', 'יהודי', 'יהודים',
            'מצוה', 'מצוות', 'ברכה', 'ברכות', 'תפילה', 'תפילות', 'קדוש', 'קדושה',
            'ברוך', 'הלל', 'הללו', 'הללויה', 'אמן', 'סלה',
            'שבת', 'פסח', 'שבועות', 'סוכות', 'ראש השנה', 'יום כיפור', 'חנוכה', 'פורים',
            'משיח', 'גאולה', 'ציון', 'בית המקדש', 'מזבח', 'קרבן', 'קרבנות',
            
            # Biblical names (very frequent)
            'אברהם', 'יצחק', 'יעקב', 'משה', 'אהרן', 'מרים', 'דוד', 'שלמה',
            'שאול', 'יונתן', 'שמואל', 'אליהו', 'אלישע', 'ישעיהו', 'ירמיהו',
            'יחזקאל', 'דניאל', 'עזרא', 'נחמיה', 'אסתר', 'רות', 'שרה', 'רבקה',
            'רחל', 'לאה', 'יוסף', 'בנימין', 'ראובן', 'שמעון', 'לוי', 'יהודה',
            'דן', 'נפתלי', 'גד', 'אשר', 'יששכר', 'זבולון', 'אפרים', 'מנשה',
            
            # Rabbinic literature (Talmud/Mishnah common)
            'רבי', 'רב', 'רבן', 'מרן', 'אמר', 'אומר', 'אמרו', 'אמרי',
            'דברי', 'הלכתא', 'תניא', 'תנן', 'מתניתין', 'ברייתא',
            'רש"י', 'תוספות', 'רמב"ם', 'רמב"ן', 'רשב"ם', 'רשב"א',
            
            # Academic & scholarly
            'מחקר', 'מחקרים', 'מאמר', 'מאמרים', 'מחבר', 'מחברים', 'עורך', 'עורכים',
            'הוצאה', 'הוצאות', 'דפוס', 'כתב יד', 'כתבי יד', 'כרך', 'כרכים',
            'פרק', 'פרקים', 'פסוק', 'פסוקים', 'דף', 'דפים', 'עמוד', 'עמודים',
            'שורה', 'שורות', 'מילה', 'מילים', 'אות', 'אותיות',
            
            # Common OCR context words
            'כתוב', 'נאמר', 'נכתב', 'נרשם', 'ראה', 'עיין', 'השווה', 'ביאור',
            'פירוש', 'פירושים', 'הערה', 'הערות', 'הגהה', 'הגהות', 'תיקון', 'תיקונים',
        ]
        self.checker.word_frequency.load_words(basic_words)
        logger.info(f"Loaded {len(basic_words)} comprehensive Hebrew words")
    
    def check_word(self, word: str) -> Dict[str, any]:
        """
        Check if a Hebrew word is spelled correctly
        
        Args:
            word: Hebrew word to check
            
        Returns:
            Dictionary with:
            - is_correct: bool
            - suggestions: List[str]
            - confidence: float (0-1)
            - error_type: str or None
        """
        # Clean the word
        cleaned_word = self._clean_word(word)
        
        if not cleaned_word:
            return {
                'is_correct': False,
                'suggestions': [],
                'confidence': 0.0,
                'error_type': 'empty'
            }
        
        # Check if word is in dictionary
        is_correct = cleaned_word in self.checker
        
        result = {
            'is_correct': is_correct,
            'suggestions': [],
            'confidence': 1.0 if is_correct else 0.0,
            'error_type': None if is_correct else 'unknown'
        }
        
        if not is_correct:
            # Generate suggestions
            suggestions = self.checker.candidates(cleaned_word)
            if suggestions:
                result['suggestions'] = list(suggestions)[:5]  # Top 5
                
                # Calculate confidence based on edit distance
                from Levenshtein import distance
                min_distance = min(
                    distance(cleaned_word, sug) for sug in result['suggestions']
                )
                
                # Confidence decreases with edit distance
                result['confidence'] = max(0.1, 1.0 - (min_distance * 0.2))
                
                # Determine error type
                if min_distance == 1:
                    result['error_type'] = 'typo'  # Single character error
                elif min_distance == 2:
                    result['error_type'] = 'confusion'  # Possible confusion
                else:
                    result['error_type'] = 'unknown'
            else:
                # No suggestions found - might be rare word or name
                result['error_type'] = 'rare_or_name'
                result['confidence'] = 0.3  # Medium-low confidence
        
        return result
    
    def check_text(self, text: str) -> List[Dict[str, any]]:
        """
        Check entire Hebrew text for spelling errors
        
        Args:
            text: Hebrew text to check
            
        Returns:
            List of dictionaries, one per misspelled word
        """
        errors = []
        words = self._tokenize(text)
        
        for word_info in words:
            word = word_info['word']
            check_result = self.check_word(word)
            
            if not check_result['is_correct']:
                errors.append({
                    'word': word,
                    'position': word_info['position'],
                    'line': word_info['line'],
                    **check_result
                })
        
        return errors
    
    def suggest_corrections(self, word: str, max_suggestions: int = 5) -> List[Tuple[str, float]]:
        """
        Get spelling suggestions with confidence scores
        
        Args:
            word: Word to get suggestions for
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of (suggestion, confidence) tuples
        """
        cleaned_word = self._clean_word(word)
        
        if not cleaned_word:
            return []
        
        # Get candidates
        candidates = self.checker.candidates(cleaned_word)
        
        if not candidates:
            return []
        
        # Score each candidate
        from Levenshtein import distance
        scored_suggestions = []
        
        for candidate in candidates:
            edit_dist = distance(cleaned_word, candidate)
            # Confidence decreases with edit distance
            confidence = max(0.1, 1.0 - (edit_dist * 0.15))
            
            # Boost confidence if it's a common confusion
            if self._is_common_confusion(cleaned_word, candidate):
                confidence = min(1.0, confidence + 0.2)
            
            scored_suggestions.append((candidate, confidence))
        
        # Sort by confidence (descending)
        scored_suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return scored_suggestions[:max_suggestions]
    
    def _is_common_confusion(self, word1: str, word2: str) -> bool:
        """Check if two words differ by common OCR confusion"""
        if len(word1) != len(word2):
            return False
        
        differences = sum(1 for c1, c2 in zip(word1, word2) if c1 != c2)
        
        if differences != 1:
            return False
        
        # Find the different character
        for c1, c2 in zip(word1, word2):
            if c1 != c2:
                return c2 in self.confusion_pairs.get(c1, [])
        
        return False
    
    def _clean_word(self, word: str) -> str:
        """Clean word from punctuation and nikud"""
        # Remove Hebrew nikud (vowel points)
        nikud_pattern = '[\u0591-\u05C7]'
        cleaned = re.sub(nikud_pattern, '', word)
        
        # Remove common punctuation
        cleaned = cleaned.strip('.,;:!?\"\'()[]{}')
        
        return cleaned
    
    def _tokenize(self, text: str) -> List[Dict[str, any]]:
        """
        Tokenize Hebrew text into words with metadata
        
        Returns:
            List of dicts with word, position, and line info
        """
        words = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Split by whitespace
            for match in re.finditer(r'\S+', line):
                word = match.group()
                # Only process Hebrew words (skip numbers, Latin, etc.)
                if re.search('[\u0590-\u05FF]', word):
                    words.append({
                        'word': word,
                        'position': match.start(),
                        'line': line_num
                    })
        
        return words


class ArabicSpellChecker:
    """
    Arabic spell checker with OCR-specific optimizations
    
    Features:
    - Arabic word validation
    - Diacritic handling
    - Common OCR patterns
    """
    
    def __init__(self):
        """Initialize Arabic spell checker"""
        try:
            self.checker = SpellChecker(language='ar')
            logger.info("Arabic spell checker initialized successfully")
        except Exception as e:
            logger.warning(f"Could not load Arabic dictionary: {e}, using fallback")
            self.checker = SpellChecker(language=None)
            self._load_basic_arabic_words()
        
        # Arabic confusion pairs (similar-looking letters)
        self.confusion_pairs = {
            'ب': ['ت', 'ث', 'ن', 'ي'],
            'ت': ['ب', 'ث', 'ن'],
            'ث': ['ب', 'ت', 'ن'],
            'ج': ['ح', 'خ'],
            'ح': ['ج', 'خ'],
            'خ': ['ج', 'ح'],
            'د': ['ذ'],
            'ذ': ['د'],
            'ر': ['ز'],
            'ز': ['ر'],
            'س': ['ش'],
            'ش': ['س'],
            'ص': ['ض'],
            'ض': ['ص'],
            'ط': ['ظ'],
            'ظ': ['ط'],
            'ع': ['غ'],
            'غ': ['ع'],
            'ف': ['ق'],
            'ق': ['ف'],
        }
    
    def _load_basic_arabic_words(self):
        """Load basic Arabic words as fallback"""
        basic_words = [
            # Common Arabic words
            'في', 'من', 'على', 'إلى', 'هذا', 'أن', 'كان', 'قال', 'هو', 'ما',
            'كل', 'مع', 'أو', 'هي', 'لا', 'ذلك', 'إن', 'قد', 'كما', 'عن',
            'السلام', 'عليكم', 'الله', 'محمد', 'كتاب', 'قرآن', 'حديث',
        ]
        self.checker.word_frequency.load_words(basic_words)
        logger.info(f"Loaded {len(basic_words)} basic Arabic words")
    
    def check_word(self, word: str) -> Dict[str, any]:
        """Check if an Arabic word is spelled correctly"""
        # Remove diacritics for checking
        cleaned_word = araby.strip_tashkeel(word)
        cleaned_word = cleaned_word.strip()
        
        if not cleaned_word:
            return {
                'is_correct': False,
                'suggestions': [],
                'confidence': 0.0,
                'error_type': 'empty'
            }
        
        is_correct = cleaned_word in self.checker
        
        result = {
            'is_correct': is_correct,
            'suggestions': [],
            'confidence': 1.0 if is_correct else 0.0,
            'error_type': None if is_correct else 'unknown'
        }
        
        if not is_correct:
            suggestions = self.checker.candidates(cleaned_word)
            if suggestions:
                result['suggestions'] = list(suggestions)[:5]
                
                from Levenshtein import distance
                min_distance = min(
                    distance(cleaned_word, sug) for sug in result['suggestions']
                )
                result['confidence'] = max(0.1, 1.0 - (min_distance * 0.2))
                
                if min_distance == 1:
                    result['error_type'] = 'typo'
                elif min_distance == 2:
                    result['error_type'] = 'confusion'
                else:
                    result['error_type'] = 'unknown'
        
        return result
    
    def check_text(self, text: str) -> List[Dict[str, any]]:
        """Check entire Arabic text for spelling errors"""
        errors = []
        
        # Tokenize Arabic text
        words = araby.tokenize(text)
        
        for i, word in enumerate(words):
            # Only check Arabic words
            if araby.is_arabicword(word):
                check_result = self.check_word(word)
                
                if not check_result['is_correct']:
                    errors.append({
                        'word': word,
                        'position': i,
                        **check_result
                    })
        
        return errors
    
    def suggest_corrections(self, word: str, max_suggestions: int = 5) -> List[Tuple[str, float]]:
        """Get spelling suggestions with confidence scores"""
        cleaned_word = araby.strip_tashkeel(word).strip()
        
        if not cleaned_word:
            return []
        
        candidates = self.checker.candidates(cleaned_word)
        
        if not candidates:
            return []
        
        from Levenshtein import distance
        scored_suggestions = []
        
        for candidate in candidates:
            edit_dist = distance(cleaned_word, candidate)
            confidence = max(0.1, 1.0 - (edit_dist * 0.15))
            scored_suggestions.append((candidate, confidence))
        
        scored_suggestions.sort(key=lambda x: x[1], reverse=True)
        return scored_suggestions[:max_suggestions]


class EnglishSpellChecker:
    """
    English spell checker for mixed-language documents
    """
    
    def __init__(self):
        """Initialize English spell checker"""
        self.checker = SpellChecker(language='en')
        logger.info("English spell checker initialized successfully")
    
    def check_word(self, word: str) -> Dict[str, any]:
        """Check if an English word is spelled correctly"""
        cleaned_word = word.lower().strip()
        
        if not cleaned_word:
            return {
                'is_correct': False,
                'suggestions': [],
                'confidence': 0.0,
                'error_type': 'empty'
            }
        
        is_correct = cleaned_word in self.checker
        
        result = {
            'is_correct': is_correct,
            'suggestions': [],
            'confidence': 1.0 if is_correct else 0.0,
            'error_type': None if is_correct else 'unknown'
        }
        
        if not is_correct:
            suggestions = self.checker.candidates(cleaned_word)
            if suggestions:
                result['suggestions'] = list(suggestions)[:5]
                
                from Levenshtein import distance
                min_distance = min(
                    distance(cleaned_word, sug) for sug in result['suggestions']
                )
                result['confidence'] = max(0.1, 1.0 - (min_distance * 0.2))
        
        return result
    
    def check_text(self, text: str) -> List[Dict[str, any]]:
        """Check entire English text for spelling errors"""
        errors = []
        words = text.split()
        
        for i, word in enumerate(words):
            # Only check words with Latin characters
            if re.match(r'^[A-Za-z]+$', word):
                check_result = self.check_word(word)
                
                if not check_result['is_correct']:
                    errors.append({
                        'word': word,
                        'position': i,
                        **check_result
                    })
        
        return errors


class MultilingualSpellChecker:
    """
    Automatic language detection and spell checking
    Supports Hebrew, Arabic, and English
    """
    
    def __init__(self):
        """Initialize all language checkers"""
        self.hebrew_checker = HebrewSpellChecker()
        self.arabic_checker = ArabicSpellChecker()
        self.english_checker = EnglishSpellChecker()
        logger.info("Multilingual spell checker initialized")
    
    def detect_language(self, text: str) -> str:
        """
        Detect primary language of text
        
        Returns:
            'hebrew', 'arabic', 'english', or 'mixed'
        """
        hebrew_chars = len(re.findall('[\u0590-\u05FF]', text))
        arabic_chars = len(re.findall('[\u0600-\u06FF]', text))
        latin_chars = len(re.findall('[A-Za-z]', text))
        
        total = hebrew_chars + arabic_chars + latin_chars
        
        if total == 0:
            return 'unknown'
        
        hebrew_ratio = hebrew_chars / total
        arabic_ratio = arabic_chars / total
        latin_ratio = latin_chars / total
        
        # If one language is >70%, it's primary
        if hebrew_ratio > 0.7:
            return 'hebrew'
        elif arabic_ratio > 0.7:
            return 'arabic'
        elif latin_ratio > 0.7:
            return 'english'
        else:
            return 'mixed'
    
    def check_text(self, text: str, language: Optional[str] = None) -> Dict[str, any]:
        """
        Check text with automatic language detection
        
        Args:
            text: Text to check
            language: Force specific language (optional)
            
        Returns:
            Dictionary with errors per language
        """
        if not language:
            language = self.detect_language(text)
        
        result = {
            'detected_language': language,
            'errors': [],
            'statistics': {
                'total_words': 0,
                'errors_found': 0,
                'error_rate': 0.0
            }
        }
        
        if language == 'hebrew':
            result['errors'] = self.hebrew_checker.check_text(text)
        elif language == 'arabic':
            result['errors'] = self.arabic_checker.check_text(text)
        elif language == 'english':
            result['errors'] = self.english_checker.check_text(text)
        elif language == 'mixed':
            # Check with all checkers
            hebrew_errors = self.hebrew_checker.check_text(text)
            arabic_errors = self.arabic_checker.check_text(text)
            english_errors = self.english_checker.check_text(text)
            
            result['errors'] = {
                'hebrew': hebrew_errors,
                'arabic': arabic_errors,
                'english': english_errors
            }
        
        # Calculate statistics
        if isinstance(result['errors'], list):
            result['statistics']['errors_found'] = len(result['errors'])
            result['statistics']['total_words'] = len(text.split())
            if result['statistics']['total_words'] > 0:
                result['statistics']['error_rate'] = (
                    result['statistics']['errors_found'] / 
                    result['statistics']['total_words']
                )
        
        return result
