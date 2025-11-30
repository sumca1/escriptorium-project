"""
Unit Tests for Language Detection Utilities
============================================

Comprehensive tests for language_utils.py including:
- Script detection (Hebrew, Arabic, Latin, Greek, Cyrillic)
- Nikud and tashkeel detection
- Text normalization
- OCR model recommendations
- Direction detection

Run with: pytest app/apps/core/tests/test_language_utils.py -v
"""

import pytest
from apps.core.language_utils import (
    detect_script,
    ScriptType,
    TextDirection,
    detect_text_direction,
    is_hebrew,
    is_arabic,
    is_rtl_script,
    has_hebrew_nikud,
    has_hebrew_teamim,
    remove_hebrew_nikud,
    normalize_hebrew_text,
    has_arabic_tashkeel,
    remove_arabic_tashkeel,
    normalize_arabic_text,
    normalize_text,
    recommend_ocr_model,
    get_script_statistics,
    compare_texts,
)


# =============================================================================
# SCRIPT DETECTION TESTS
# =============================================================================

class TestScriptDetection:
    """Test script detection functionality"""

    def test_detect_hebrew_script(self):
        """Test Hebrew script detection"""
        hebrew_texts = [
            "שלום עולם",
            "בראשית ברא אלהים",
            "תורה נביאים וכתובים",
            "ארץ ישראל",
        ]
        for text in hebrew_texts:
            assert detect_script(text) == ScriptType.HEBREW, f"Failed for: {text}"

    def test_detect_arabic_script(self):
        """Test Arabic script detection"""
        arabic_texts = [
            "مرحبا بالعالم",
            "القرآن الكريم",
            "بسم الله الرحمن الرحيم",
            "السلام عليكم",
        ]
        for text in arabic_texts:
            assert detect_script(text) == ScriptType.ARABIC, f"Failed for: {text}"

    def test_detect_latin_script(self):
        """Test Latin script detection"""
        latin_texts = [
            "Hello World",
            "Bonjour le monde",
            "Lorem ipsum dolor",
            "The quick brown fox",
        ]
        for text in latin_texts:
            assert detect_script(text) == ScriptType.LATIN, f"Failed for: {text}"

    def test_detect_greek_script(self):
        """Test Greek script detection"""
        greek_text = "Γεια σου κόσμε"
        assert detect_script(greek_text) == ScriptType.GREEK

    def test_detect_mixed_script(self):
        """Test mixed script detection"""
        mixed_texts = [
            "Hello שלום",
            "مرحبا World",
            "Hebrew עברית and English",
        ]
        for text in mixed_texts:
            assert detect_script(text) == ScriptType.MIXED, f"Failed for: {text}"

    def test_empty_text(self):
        """Test detection with empty text"""
        assert detect_script("") == ScriptType.UNKNOWN
        assert detect_script("   ") == ScriptType.UNKNOWN
        assert detect_script(None) == ScriptType.UNKNOWN

    def test_numbers_and_punctuation_only(self):
        """Test text with only numbers and punctuation"""
        assert detect_script("123.456") == ScriptType.UNKNOWN
        assert detect_script("!@#$%") == ScriptType.UNKNOWN


class TestScriptHelpers:
    """Test helper functions for script detection"""

    def test_is_hebrew(self):
        """Test is_hebrew helper"""
        assert is_hebrew("שלום") is True
        assert is_hebrew("Hello") is False
        assert is_hebrew("مرحبا") is False

    def test_is_arabic(self):
        """Test is_arabic helper"""
        assert is_arabic("مرحبا") is True
        assert is_arabic("Hello") is False
        assert is_arabic("שלום") is False

    def test_is_rtl_script(self):
        """Test RTL script detection"""
        assert is_rtl_script("שלום") is True  # Hebrew
        assert is_rtl_script("مرحبا") is True  # Arabic
        assert is_rtl_script("Hello") is False  # Latin


class TestScriptStatistics:
    """Test script statistics generation"""

    def test_get_script_statistics_hebrew(self):
        """Test statistics for Hebrew text"""
        text = "שלום עולם"
        stats = get_script_statistics(text)
        assert stats['hebrew'] > 0
        assert stats['arabic'] == 0
        assert stats['latin'] == 0

    def test_get_script_statistics_mixed(self):
        """Test statistics for mixed script"""
        text = "Hello שלום"
        stats = get_script_statistics(text)
        assert stats['hebrew'] > 0
        assert stats['latin'] > 0
        assert stats['arabic'] == 0

    def test_get_script_statistics_empty(self):
        """Test statistics for empty text"""
        stats = get_script_statistics("")
        assert all(count == 0 for count in stats.values())


# =============================================================================
# TEXT DIRECTION TESTS
# =============================================================================

class TestTextDirection:
    """Test text directionality detection"""

    def test_rtl_direction_hebrew(self):
        """Test RTL direction for Hebrew"""
        assert detect_text_direction("שלום") == TextDirection.RTL

    def test_rtl_direction_arabic(self):
        """Test RTL direction for Arabic"""
        assert detect_text_direction("مرحبا") == TextDirection.RTL

    def test_ltr_direction_latin(self):
        """Test LTR direction for Latin"""
        assert detect_text_direction("Hello") == TextDirection.LTR

    def test_mixed_direction(self):
        """Test mixed direction"""
        assert detect_text_direction("Hello שלום") == TextDirection.MIXED


# =============================================================================
# HEBREW NIKUD TESTS
# =============================================================================

class TestHebrewNikud:
    """Test Hebrew nikud (vowel points) handling"""

    def test_has_nikud_detection(self):
        """Test nikud detection"""
        with_nikud = "בְּרֵאשִׁית"
        without_nikud = "בראשית"
        
        assert has_hebrew_nikud(with_nikud) is True
        assert has_hebrew_nikud(without_nikud) is False

    def test_has_teamim_detection(self):
        """Test te'amim (cantillation marks) detection"""
        # Note: Would need text with actual te'amim for proper test
        text_no_teamim = "בראשית"
        assert has_hebrew_teamim(text_no_teamim) is False

    def test_remove_nikud(self):
        """Test nikud removal"""
        with_nikud = "בְּרֵאשִׁית בָּרָא"
        expected = "בראשית ברא"
        result = remove_hebrew_nikud(with_nikud)
        
        assert result == expected
        assert len(result) < len(with_nikud)

    def test_remove_nikud_keeps_text(self):
        """Test that removing nikud preserves base text"""
        text = "בְּרֵאשִׁית"
        result = remove_hebrew_nikud(text)
        
        # Should keep the base letters
        assert "ב" in result
        assert "ר" in result
        assert "א" in result
        assert "ש" in result
        assert "י" in result
        assert "ת" in result

    def test_normalize_hebrew_text(self):
        """Test Hebrew text normalization"""
        with_nikud = "בְּרֵאשִׁית"
        normalized = normalize_hebrew_text(with_nikud)
        
        assert has_hebrew_nikud(normalized) is False
        assert len(normalized) < len(with_nikud)


# =============================================================================
# ARABIC TASHKEEL TESTS
# =============================================================================

class TestArabicTashkeel:
    """Test Arabic tashkeel (diacritics) handling"""

    def test_has_tashkeel_detection(self):
        """Test tashkeel detection"""
        with_tashkeel = "بِسْمِ اللَّهِ"
        without_tashkeel = "بسم الله"
        
        assert has_arabic_tashkeel(with_tashkeel) is True
        assert has_arabic_tashkeel(without_tashkeel) is False

    def test_remove_tashkeel(self):
        """Test tashkeel removal"""
        with_tashkeel = "بِسْمِ اللَّهِ"
        result = remove_arabic_tashkeel(with_tashkeel)
        
        assert len(result) < len(with_tashkeel)
        assert has_arabic_tashkeel(result) is False

    def test_normalize_arabic_text(self):
        """Test Arabic text normalization"""
        with_tashkeel = "بِسْمِ اللَّهِ الرَّحْمَٰنِ"
        normalized = normalize_arabic_text(with_tashkeel)
        
        assert has_arabic_tashkeel(normalized) is False
        assert len(normalized) < len(with_tashkeel)


# =============================================================================
# GENERAL NORMALIZATION TESTS
# =============================================================================

class TestNormalization:
    """Test general text normalization"""

    def test_normalize_auto_detect_hebrew(self):
        """Test normalization with auto-detection (Hebrew)"""
        text = "בְּרֵאשִׁית"
        normalized = normalize_text(text)
        
        assert len(normalized) < len(text)
        assert has_hebrew_nikud(normalized) is False

    def test_normalize_auto_detect_arabic(self):
        """Test normalization with auto-detection (Arabic)"""
        text = "بِسْمِ اللَّهِ"
        normalized = normalize_text(text)
        
        assert len(normalized) < len(text)
        assert has_arabic_tashkeel(normalized) is False

    def test_normalize_explicit_script(self):
        """Test normalization with explicit script type"""
        text = "בְּרֵאשִׁית"
        normalized = normalize_text(text, script=ScriptType.HEBREW)
        
        assert has_hebrew_nikud(normalized) is False


# =============================================================================
# OCR RECOMMENDATIONS TESTS
# =============================================================================

class TestOCRRecommendations:
    """Test OCR model recommendation system"""

    def test_recommend_hebrew(self):
        """Test recommendations for Hebrew"""
        text = "שלום עולם"
        rec = recommend_ocr_model(text)
        
        assert rec['script'] == 'hebrew'
        assert rec['direction'] == 'rtl'
        assert rec['recommended_engine'] == 'kraken'
        assert 'hebrew' in rec['model_hint'].lower()

    def test_recommend_hebrew_with_nikud(self):
        """Test recommendations for Hebrew with nikud"""
        text = "בְּרֵאשִׁית"
        rec = recommend_ocr_model(text)
        
        assert rec['script'] == 'hebrew'
        assert rec['has_nikud'] is True
        assert 'binarization' in rec['preprocessing']

    def test_recommend_arabic(self):
        """Test recommendations for Arabic"""
        text = "مرحبا بالعالم"
        rec = recommend_ocr_model(text)
        
        assert rec['script'] == 'arabic'
        assert rec['direction'] == 'rtl'
        assert rec['recommended_engine'] == 'kraken'

    def test_recommend_arabic_with_tashkeel(self):
        """Test recommendations for Arabic with tashkeel"""
        text = "بِسْمِ اللَّهِ"
        rec = recommend_ocr_model(text)
        
        assert rec['script'] == 'arabic'
        assert rec['has_tashkeel'] is True

    def test_recommend_latin(self):
        """Test recommendations for Latin"""
        text = "Hello World"
        rec = recommend_ocr_model(text)
        
        assert rec['script'] == 'latin'
        assert rec['direction'] == 'ltr'
        assert rec['recommended_engine'] == 'tesseract'

    def test_recommend_preprocessing(self):
        """Test preprocessing recommendations"""
        hebrew_rec = recommend_ocr_model("שלום")
        arabic_rec = recommend_ocr_model("مرحبا")
        
        assert 'preprocessing' in hebrew_rec
        assert 'preprocessing' in arabic_rec
        assert isinstance(hebrew_rec['preprocessing'], list)
        assert len(hebrew_rec['preprocessing']) > 0


# =============================================================================
# TEXT COMPARISON TESTS
# =============================================================================

class TestTextComparison:
    """Test text comparison utilities"""

    def test_compare_hebrew_texts(self):
        """Test comparison of Hebrew texts"""
        original = "בְּרֵאשִׁית בָּרָא"
        normalized = "בראשית ברא"
        
        comparison = compare_texts(original, normalized)
        
        assert comparison['original_length'] > comparison['normalized_length']
        assert comparison['removed_chars'] > 0
        assert comparison['has_hebrew_nikud'] is True
        assert 0 < comparison['compression_ratio'] < 1

    def test_compare_arabic_texts(self):
        """Test comparison of Arabic texts"""
        original = "بِسْمِ اللَّهِ"
        normalized = remove_arabic_tashkeel(original)
        
        comparison = compare_texts(original, normalized)
        
        assert comparison['original_length'] > comparison['normalized_length']
        assert comparison['has_arabic_tashkeel'] is True

    def test_compare_identical_texts(self):
        """Test comparison of identical texts"""
        text = "Hello World"
        comparison = compare_texts(text, text)
        
        assert comparison['original_length'] == comparison['normalized_length']
        assert comparison['removed_chars'] == 0
        assert comparison['compression_ratio'] == 1.0


# =============================================================================
# EDGE CASES & ERROR HANDLING
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_none_input(self):
        """Test handling of None input"""
        assert detect_script(None) == ScriptType.UNKNOWN
        assert get_script_statistics(None) is not None

    def test_empty_string(self):
        """Test handling of empty string"""
        assert detect_script("") == ScriptType.UNKNOWN
        assert remove_hebrew_nikud("") == ""
        assert remove_arabic_tashkeel("") == ""

    def test_very_long_text(self):
        """Test with very long text"""
        long_text = "שלום " * 1000
        script = detect_script(long_text)
        assert script == ScriptType.HEBREW

    def test_special_characters(self):
        """Test with special characters"""
        text_with_special = "שלום! עולם?"
        script = detect_script(text_with_special)
        assert script == ScriptType.HEBREW

    def test_numbers_mixed_with_text(self):
        """Test numbers mixed with text"""
        text = "שלום 123 עולם 456"
        script = detect_script(text)
        assert script == ScriptType.HEBREW


# =============================================================================
# PYTEST FIXTURES
# =============================================================================

@pytest.fixture
def hebrew_samples():
    """Sample Hebrew texts for testing"""
    return {
        'simple': "שלום עולם",
        'with_nikud': "בְּרֵאשִׁית בָּרָא אֱלֹהִים",
        'no_nikud': "בראשית ברא אלהים",
        'mixed': "שלום Hello עולם",
    }


@pytest.fixture
def arabic_samples():
    """Sample Arabic texts for testing"""
    return {
        'simple': "مرحبا بالعالم",
        'with_tashkeel': "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        'no_tashkeel': "بسم الله الرحمن الرحيم",
        'mixed': "مرحبا Hello بالعالم",
    }


# =============================================================================
# PARAMETRIZED TESTS
# =============================================================================

@pytest.mark.parametrize("text,expected", [
    ("שלום", ScriptType.HEBREW),
    ("مرحبا", ScriptType.ARABIC),
    ("Hello", ScriptType.LATIN),
    ("Γεια", ScriptType.GREEK),
    ("Привет", ScriptType.CYRILLIC),
    ("Hello שלום", ScriptType.MIXED),
    ("", ScriptType.UNKNOWN),
])
def test_script_detection_parametrized(text, expected):
    """Parametrized test for script detection"""
    assert detect_script(text) == expected


@pytest.mark.parametrize("text,expected_rtl", [
    ("שלום", True),
    ("مرحبا", True),
    ("Hello", False),
    ("Bonjour", False),
])
def test_rtl_detection_parametrized(text, expected_rtl):
    """Parametrized test for RTL detection"""
    assert is_rtl_script(text) == expected_rtl


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
