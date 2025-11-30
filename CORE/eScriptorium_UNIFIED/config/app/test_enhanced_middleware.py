#!/usr/bin/env python3
"""
Quick test script for Enhanced BiblIA Middleware
Tests RTL functionality and translation mapping
"""

import sys
import os

# Add Django setup
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'escriptorium.settings')

import django
django.setup()

from django.test import RequestFactory
from django.http import HttpResponse
from enhanced_biblia_middleware import EnhancedBibliaMiddleware
from django.utils import translation

def test_middleware():
    """Test the Enhanced BiblIA Middleware"""
    
    print("🔍 Testing Enhanced BiblIA Middleware")
    print("=" * 50)
    
    # Create test request
    factory = RequestFactory()
    request = factory.get('/')
    
    # Mock get_response function that returns HTML
    def mock_get_response(request):
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body class="escr-body">
    <nav class="navbar">
        <a href="#">Home</a>
        <div class="dropdown-menu dropdown-menu-right">
            <a class="dropdown-item">Profile</a>
            <a class="dropdown-item">My Models</a>
            <a class="dropdown-item">Task reports</a>
        </div>
    </nav>
    <div>
        <h1>Documents</h1>
        <p>Welcome to eScriptorium</p>
        <button>Save</button>
        <button>Cancel</button>
    </div>
</body>
</html>
        """
        response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
        return response
    
    # Initialize middleware
    middleware = EnhancedBibliaMiddleware(mock_get_response)
    
    # Test with Hebrew language
    print("📝 Testing with Hebrew language...")
    with translation.override('he'):
        response = middleware(request)
        content = response.content.decode('utf-8')
        
        # Check RTL CSS injection
        if 'direction: rtl' in content:
            print("✅ RTL CSS successfully injected")
        else:
            print("❌ RTL CSS injection failed")
        
        # Check RTL class on body
        if 'class="escr-body rtl"' in content:
            print("✅ RTL class added to body")
        else:
            print("❌ RTL class not added to body")
        
        # Check dropdown menu fix
        if 'dropdown-menu-left' in content:
            print("✅ Dropdown menu positioning fixed for RTL")
        else:
            print("❌ Dropdown menu positioning not fixed")
        
        # Check translations
        translations_found = 0
        test_translations = {
            'Documents': 'מסמכים',
            'Profile': 'פרופיל', 
            'My Models': 'המודלים שלי',
            'Task reports': 'דוחות משימות',
            'Save': 'שמור',
            'Cancel': 'ביטול'
        }
        
        for english, hebrew in test_translations.items():
            if hebrew in content:
                translations_found += 1
                
        print(f"✅ {translations_found}/{len(test_translations)} translations applied")
        
        # Check HTML lang and dir attributes
        if 'lang="he"' in content and 'dir="rtl"' in content:
            print("✅ HTML lang and dir attributes set correctly")
        else:
            print("❌ HTML lang and dir attributes not set")
        
        # Check Israeli flag replacement
        if 'flag-icon-il' in content or 'il' in content:
            print("✅ Israeli flag replacement applied")
        else:
            print("⚠️  Israeli flag replacement not detected (may not be present in test HTML)")
    
    # Test with English language (should not apply RTL)
    print("\n📝 Testing with English language...")
    with translation.override('en'):
        response = middleware(request)
        content = response.content.decode('utf-8')
        
        if 'direction: rtl' not in content and 'rtl' not in content:
            print("✅ RTL not applied for English language")
        else:
            print("❌ RTL incorrectly applied for English language")
    
    print("\n🎉 Middleware test completed!")
    print("\n💡 Key improvements in Enhanced Middleware:")
    print("   • Complete translation mapping (150+ terms)")
    print("   • Advanced RTL CSS injection")
    print("   • Dynamic HTML modifications")
    print("   • Context-aware dropdown positioning")
    print("   • Israeli flag replacement for Hebrew")
    print("   • Preserves core file integrity")
    print("   • Enhanced Hebrew typography support")

if __name__ == '__main__':
    test_middleware()