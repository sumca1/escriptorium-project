"""
Language and Script Detection Utilities for BiblIA
===================================================

Provides automatic detection of script types (Hebrew, Arabic, Latin) and
language-specific text processing utilities including nikud/tashkeel handling.

Features:
- Script detection (Hebrew, Arabic, Latin, Mixed)
- Nikud (Hebrew vocalization) handling
- Tashkeel (Arabic diacritics) handling
- Character normalization
- Text directionality detection
- Language-specific recommendations

Author: BiblIA Project
Date: 30 October 2025
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum


class ScriptType(Enum):
    """Supported script types"""
    HEBREW = "hebrew"
    ARABIC = "arabic"
    LATIN = "latin"
    GREEK = "greek"
    CYRILLIC = "cyrillic"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class TextDirection(Enum):
    """Text directionality"""
    RTL = "rtl"  # Right-to-Left
    LTR = "ltr"  # Left-to-Right
    MIXED = "mixed"


# =============================================================================
# UNICODE RANGES
# =============================================================================

# Hebrew character ranges
HEBREW_LETTERS = range(0x0590, 0x05FF)  # Hebrew block
HEBREW_BASE = range(0x05D0, 0x05EB)  # Alef to Tav (no nikud)
HEBREW_NIKUD = range(0x05B0, 0x05C8)  # Vowel points
HEBREW_TEAMIM = range(0x0591, 0x05AF)  # Cantillation marks (טעמי המקרא)

# Arabic character ranges
ARABIC_LETTERS = range(0x0600, 0x06FF)  # Arabic block
ARABIC_BASE = range(0x0621, 0x064A)  # Arabic letters (no tashkeel)
ARABIC_TASHKEEL = range(0x064B, 0x0652)  # Diacritics (تشكيل)
ARABIC_EXTENDED = range(0x0750, 0x077F)  # Arabic Supplement

# Latin character ranges
LATIN_BASIC = range(0x0041, 0x007B)  # A-Z, a-z
LATIN_EXTENDED_A = range(0x0100, 0x017F)
LATIN_EXTENDED_B = range(0x0180, 0x024F)

# Greek character ranges
GREEK_LETTERS = range(0x0370, 0x03FF)

# Cyrillic character ranges
CYRILLIC_LETTERS = range(0x0400, 0x04FF)


# =============================================================================
# SCRIPT DETECTION
# =============================================================================

def detect_script(text: str, threshold: float = 0.3) -> ScriptType:
    """
    Detect the primary script type of the text.
    
    Args:
        text: Input text to analyze
        threshold: Minimum ratio to consider a script dominant (0.0-1.0)
        
    Returns:
        ScriptType enum value
        
    Examples:
        >>> detect_script("שלום עולם")
        ScriptType.HEBREW
        >>> detect_script("مرحبا بالعالم")
        ScriptType.ARABIC
        >>> detect_script("Hello world")
        ScriptType.LATIN
    """
    if not text or not text.strip():
        return ScriptType.UNKNOWN
    
    # Remove whitespace, digits, and common punctuation for analysis
    # Note: Python re doesn't support \p{P}, so we use explicit punctuation characters
    clean_text = re.sub(r'[\s\d.,;:!?\-\'"()\[\]{}]+', '', text)
    
    if not clean_text:
        return ScriptType.UNKNOWN
    
    # Count characters by script
    counts = get_script_statistics(text)
    total = sum(counts.values())
    
    if total == 0:
        return ScriptType.UNKNOWN
    
    # Calculate ratios
    ratios = {script: count / total for script, count in counts.items()}
    
    # Find dominant script
    max_script = max(ratios, key=ratios.get)
    max_ratio = ratios[max_script]
    
    # Check if we have a clear winner
    if max_ratio < threshold:
        return ScriptType.UNKNOWN
    
    # Check for mixed scripts (multiple scripts above threshold)
    significant_scripts = [s for s, r in ratios.items() if r >= threshold]
    if len(significant_scripts) > 1:
        return ScriptType.MIXED
    
    return ScriptType(max_script)


def get_script_statistics(text: str) -> Dict[str, int]:
    """
    Count characters by script type.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary with script names as keys and character counts as values
        
    Example:
        >>> get_script_statistics("Hello שלום")
        {'latin': 5, 'hebrew': 4, 'arabic': 0, ...}
    """
    counts = {
        'hebrew': 0,
        'arabic': 0,
        'latin': 0,
        'greek': 0,
        'cyrillic': 0,
    }
    
    for char in text:
        code = ord(char)
        
        if code in HEBREW_LETTERS:
            counts['hebrew'] += 1
        elif code in ARABIC_LETTERS or code in ARABIC_EXTENDED:
            counts['arabic'] += 1
        elif code in LATIN_BASIC or code in LATIN_EXTENDED_A or code in LATIN_EXTENDED_B:
            counts['latin'] += 1
        elif code in GREEK_LETTERS:
            counts['greek'] += 1
        elif code in CYRILLIC_LETTERS:
            counts['cyrillic'] += 1
    
    return counts


def is_hebrew(text: str) -> bool:
    """Check if text is primarily Hebrew"""
    return detect_script(text) == ScriptType.HEBREW


def is_arabic(text: str) -> bool:
    """Check if text is primarily Arabic"""
    return detect_script(text) == ScriptType.ARABIC


def is_rtl_script(text: str) -> bool:
    """Check if text uses Right-to-Left script (Hebrew or Arabic)"""
    script = detect_script(text)
    return script in [ScriptType.HEBREW, ScriptType.ARABIC]


def detect_text_direction(text: str) -> TextDirection:
    """
    Detect text directionality (RTL/LTR/Mixed).
    
    Args:
        text: Input text
        
    Returns:
        TextDirection enum value
    """
    script = detect_script(text)
    
    if script == ScriptType.MIXED:
        return TextDirection.MIXED
    elif script in [ScriptType.HEBREW, ScriptType.ARABIC]:
        return TextDirection.RTL
    elif script in [ScriptType.LATIN, ScriptType.GREEK, ScriptType.CYRILLIC]:
        return TextDirection.LTR
    else:
        return TextDirection.LTR  # Default


# =============================================================================
# HEBREW NIKUD HANDLING
# =============================================================================

def has_hebrew_nikud(text: str) -> bool:
    """
    Check if Hebrew text contains nikud (vowel points).
    
    Args:
        text: Hebrew text to check
        
    Returns:
        True if nikud is present
    """
    return any(ord(char) in HEBREW_NIKUD for char in text)


def has_hebrew_teamim(text: str) -> bool:
    """
    Check if Hebrew text contains te'amim (cantillation marks).
    
    Args:
        text: Hebrew text to check
        
    Returns:
        True if te'amim are present
    """
    return any(ord(char) in HEBREW_TEAMIM for char in text)


def remove_hebrew_nikud(text: str, keep_teamim: bool = False) -> str:
    """
    Remove Hebrew nikud (vowel points) from text.
    
    Args:
        text: Hebrew text with nikud
        keep_teamim: If True, keep cantillation marks (טעמי המקרא)
        
    Returns:
        Text without nikud
        
    Example:
        >>> remove_hebrew_nikud("בְּרֵאשִׁית")
        "בראשית"
    """
    result = []
    for char in text:
        code = ord(char)
        # Remove nikud but optionally keep teamim
        if code in HEBREW_NIKUD:
            continue
        if not keep_teamim and code in HEBREW_TEAMIM:
            continue
        result.append(char)
    return ''.join(result)


def normalize_hebrew_text(text: str, remove_nikud: bool = True, 
                         remove_teamim: bool = True) -> str:
    """
    Normalize Hebrew text by removing diacritics.
    
    Args:
        text: Hebrew text to normalize
        remove_nikud: Remove vowel points
        remove_teamim: Remove cantillation marks
        
    Returns:
        Normalized Hebrew text
    """
    if not remove_nikud and not remove_teamim:
        return text
    
    result = []
    for char in text:
        code = ord(char)
        if remove_nikud and code in HEBREW_NIKUD:
            continue
        if remove_teamim and code in HEBREW_TEAMIM:
            continue
        result.append(char)
    
    return ''.join(result)


# =============================================================================
# ARABIC TASHKEEL HANDLING
# =============================================================================

def has_arabic_tashkeel(text: str) -> bool:
    """
    Check if Arabic text contains tashkeel (diacritics).
    
    Args:
        text: Arabic text to check
        
    Returns:
        True if tashkeel is present
    """
    return any(ord(char) in ARABIC_TASHKEEL for char in text)


def remove_arabic_tashkeel(text: str) -> str:
    """
    Remove Arabic tashkeel (diacritics) from text.
    
    Args:
        text: Arabic text with tashkeel
        
    Returns:
        Text without tashkeel
        
    Example:
        >>> remove_arabic_tashkeel("بِسْمِ اللَّهِ")
        "بسم الله"
    """
    result = []
    for char in text:
        if ord(char) not in ARABIC_TASHKEEL:
            result.append(char)
    return ''.join(result)


def normalize_arabic_text(text: str, remove_tashkeel: bool = True) -> str:
    """
    Normalize Arabic text by removing diacritics.
    
    Args:
        text: Arabic text to normalize
        remove_tashkeel: Remove diacritical marks
        
    Returns:
        Normalized Arabic text
    """
    if not remove_tashkeel:
        return text
    
    return remove_arabic_tashkeel(text)


# =============================================================================
# GENERAL TEXT NORMALIZATION
# =============================================================================

def normalize_text(text: str, script: Optional[ScriptType] = None) -> str:
    """
    Normalize text based on its script type.
    
    Auto-detects script if not provided and applies appropriate normalization.
    
    Args:
        text: Text to normalize
        script: Script type (auto-detected if None)
        
    Returns:
        Normalized text
    """
    if script is None:
        script = detect_script(text)
    
    if script == ScriptType.HEBREW:
        return normalize_hebrew_text(text)
    elif script == ScriptType.ARABIC:
        return normalize_arabic_text(text)
    else:
        return text


# =============================================================================
# MODEL RECOMMENDATIONS
# =============================================================================

def recommend_ocr_model(text: str) -> Dict[str, str]:
    """
    Recommend OCR model based on text script.
    
    Args:
        text: Sample text or document language
        
    Returns:
        Dictionary with recommendations
        
    Example:
        >>> recommend_ocr_model("שלום")
        {
            'script': 'hebrew',
            'direction': 'rtl',
            'recommended_engine': 'kraken',
            'model_hint': 'hebrew_best.mlmodel',
            'preprocessing': ['binarization', 'deskew']
        }
    """
    script = detect_script(text)
    direction = detect_text_direction(text)
    
    recommendations = {
        'script': script.value,
        'direction': direction.value,
        'has_nikud': False,
        'has_tashkeel': False,
    }
    
    # Script-specific recommendations
    if script == ScriptType.HEBREW:
        recommendations.update({
            'recommended_engine': 'kraken',
            'model_hint': 'hebrew_best.mlmodel',
            'preprocessing': ['binarization', 'deskew', 'despeckle'],
            'has_nikud': has_hebrew_nikud(text),
            'has_teamim': has_hebrew_teamim(text),
        })
    elif script == ScriptType.ARABIC:
        recommendations.update({
            'recommended_engine': 'kraken',
            'model_hint': 'arabic_best.mlmodel',
            'preprocessing': ['binarization', 'deskew'],
            'has_tashkeel': has_arabic_tashkeel(text),
        })
    elif script == ScriptType.LATIN:
        recommendations.update({
            'recommended_engine': 'tesseract',  # Good for printed Latin
            'model_hint': 'eng.traineddata',
            'preprocessing': ['binarization'],
        })
    else:
        recommendations.update({
            'recommended_engine': 'kraken',  # Default
            'model_hint': None,
            'preprocessing': ['binarization', 'deskew'],
        })
    
    return recommendations


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_character_ranges_info(text: str) -> Dict[str, List[str]]:
    """
    Analyze text and return detailed character range information.
    
    Useful for debugging and analysis.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with character range details
    """
    info = {
        'hebrew_base': [],
        'hebrew_nikud': [],
        'hebrew_teamim': [],
        'arabic_base': [],
        'arabic_tashkeel': [],
        'latin': [],
        'other': [],
    }
    
    for char in text:
        code = ord(char)
        
        if code in HEBREW_BASE:
            info['hebrew_base'].append(char)
        elif code in HEBREW_NIKUD:
            info['hebrew_nikud'].append(char)
        elif code in HEBREW_TEAMIM:
            info['hebrew_teamim'].append(char)
        elif code in ARABIC_BASE:
            info['arabic_base'].append(char)
        elif code in ARABIC_TASHKEEL:
            info['arabic_tashkeel'].append(char)
        elif code in LATIN_BASIC or code in LATIN_EXTENDED_A:
            info['latin'].append(char)
        elif not char.isspace():
            info['other'].append(char)
    
    return info


def compare_texts(original: str, normalized: str) -> Dict[str, any]:
    """
    Compare original and normalized texts.
    
    Args:
        original: Original text with diacritics
        normalized: Normalized text without diacritics
        
    Returns:
        Comparison statistics
    """
    return {
        'original_length': len(original),
        'normalized_length': len(normalized),
        'removed_chars': len(original) - len(normalized),
        'compression_ratio': len(normalized) / len(original) if original else 0,
        'has_hebrew_nikud': has_hebrew_nikud(original),
        'has_arabic_tashkeel': has_arabic_tashkeel(original),
    }
