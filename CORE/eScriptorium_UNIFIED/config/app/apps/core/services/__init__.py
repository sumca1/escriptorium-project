# Core services package for OCR error detection and correction
from .spell_checker import (
    HebrewSpellChecker,
    ArabicSpellChecker,
    EnglishSpellChecker,
    MultilingualSpellChecker,
)
from .error_detector import OCRErrorDetector
from .auto_corrector import AutoCorrector

__all__ = [
    'HebrewSpellChecker',
    'ArabicSpellChecker',
    'EnglishSpellChecker',
    'MultilingualSpellChecker',
    'OCRErrorDetector',
    'AutoCorrector',
]
