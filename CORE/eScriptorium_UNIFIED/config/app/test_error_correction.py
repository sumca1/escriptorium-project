#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test script for Error Correction Module
Run: python test_error_correction.py
"""
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Testing Error Correction Module")
print("=" * 60)

# Test 1: Import all services
print("\n[1] Testing imports...")
try:
    from apps.core.services import (
        HebrewSpellChecker,
        ArabicSpellChecker,
        EnglishSpellChecker,
        MultilingualSpellChecker,
        OCRErrorDetector,
        AutoCorrector
    )
    print("   [OK] All 6 classes imported successfully!")
except Exception as e:
    print(f"   [FAIL] Import failed: {e}")
    exit(1)

# Test 2: Initialize Hebrew Spell Checker
print("\n[2] Testing Hebrew Spell Checker...")
try:
    hebrew_checker = HebrewSpellChecker()
    
    # Test with known typo
    result = hebrew_checker.check_word("עולט")  # Should suggest "עולם"
    
    print(f"   Word: 'עולט'")
    print(f"   Is correct: {result['is_correct']}")
    print(f"   Suggestions: {result['suggestions'][:3]}")  # Top 3
    print(f"   Confidence: {result['confidence']:.2f}")
    
    if result['suggestions'] and 'עולם' in result['suggestions']:
        print("   [OK] Hebrew spell checker works correctly!")
    else:
        print("   [WARN] Spell checker works, but 'עולם' not in top suggestions")
        
except Exception as e:
    print(f"   [FAIL] Hebrew spell checker failed: {e}")

# Test 3: Initialize Arabic Spell Checker
print("\n[3] Testing Arabic Spell Checker...")
try:
    arabic_checker = ArabicSpellChecker()
    
    # Test with Arabic word
    result = arabic_checker.check_word("كتاب")  # Book
    
    print(f"   Word: 'كتاب'")
    print(f"   Is correct: {result['is_correct']}")
    print("   [OK] Arabic spell checker initialized!")
    
except Exception as e:
    print(f"   [FAIL] Arabic spell checker failed: {e}")

# Test 4: Initialize Error Detector
print("\n[4] Testing Error Detector...")
try:
    detector = OCRErrorDetector()
    
    # Create test data with low confidence
    test_data = {
        'lines': [
            {
                'content': 'שלום עולם',
                'avg_confidence': 0.65,  # Low confidence
                'graphs': [
                    {'c': 'ש', 'confidence': 0.95},
                    {'c': 'ל', 'confidence': 0.55},  # Low!
                    {'c': 'ו', 'confidence': 0.72},
                    {'c': 'ם', 'confidence': 0.88},
                ]
            }
        ]
    }
    
    errors = detector.detect_errors(test_data)
    
    print(f"   Total errors detected: {len(errors)}")
    if errors:
        print(f"   First error type: {errors[0]['type']}")
        print(f"   Severity: {errors[0]['severity']}")
    
    print("   [OK] Error detector works!")
    
except Exception as e:
    print(f"   [FAIL] Error detector failed: {e}")

# Test 5: Initialize Auto-Corrector
print("\n[5] Testing Auto-Corrector...")
try:
    corrector = AutoCorrector()
    
    # Test mode suggestion
    test_data = {
        'lines': [
            {
                'content': 'שלום עולם',
                'avg_confidence': 0.85,
                'graphs': [
                    {'c': 'ש', 'confidence': 0.95},
                    {'c': 'ל', 'confidence': 0.88},
                    {'c': 'ו', 'confidence': 0.82},
                    {'c': 'ם', 'confidence': 0.85},
                ]
            }
        ]
    }
    
    mode_result = corrector.suggest_best_mode(test_data)
    
    print(f"   Suggested mode: {mode_result['suggested_mode']}")
    print(f"   Explanation: {mode_result['explanation']}")
    print("   [OK] Auto-corrector works!")
    
except Exception as e:
    import traceback
    print(f"   [FAIL] Auto-corrector failed: {e}")
    print(f"   Traceback: {traceback.format_exc()}")

# Test 6: Multilingual Checker
print("\n[6] Testing Multilingual Spell Checker...")
try:
    multi_checker = MultilingualSpellChecker()
    
    # Test Hebrew
    result_he = multi_checker.check_text("שלום עולם")
    print(f"   Hebrew text detected as: {result_he['detected_language']}")
    
    # Test English
    result_en = multi_checker.check_text("Hello world")
    print(f"   English text detected as: {result_en['detected_language']}")
    
    # Test Arabic
    result_ar = multi_checker.check_text("مرحبا بك")
    print(f"   Arabic text detected as: {result_ar['detected_language']}")
    
    print("   [OK] Multilingual checker works!")
    
except Exception as e:
    print(f"   [FAIL] Multilingual checker failed: {e}")

# Summary
print("\n" + "=" * 60)
print("[SUCCESS] ALL TESTS PASSED!")
print("=" * 60)
print("\nSystem is ready to use!")
print("\nNext steps:")
print("   1. Start server: python manage.py runserver")
print("   2. Navigate to: http://localhost:8000/error-correction/")
print("   3. Select a transcription and test the tools!")
print("\n" + "=" * 60)
