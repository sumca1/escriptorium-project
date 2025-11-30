#!/usr/bin/env python3
"""
Quick manual test for Enhanced BiblIA Middleware
"""

# Test if the middleware imports correctly
print("🔍 Testing Enhanced BiblIA Middleware Import...")

try:
    from enhanced_biblia_middleware import EnhancedBibliaMiddleware
    print("✅ Enhanced middleware imported successfully")
    
    # Test basic instantiation
    def dummy_response(request):
        return "Test response"
    
    middleware = EnhancedBibliaMiddleware(dummy_response)
    print("✅ Middleware instantiated successfully")
    
    # Test translation map
    if hasattr(middleware, 'translation_map') and len(middleware.translation_map) > 0:
        print(f"✅ Translation map loaded with {len(middleware.translation_map)} entries")
    else:
        print("❌ Translation map not loaded properly")
    
    # Test RTL CSS
    if hasattr(middleware, 'enhanced_rtl_css') and 'direction: rtl' in middleware.enhanced_rtl_css:
        print("✅ RTL CSS loaded successfully")
    else:
        print("❌ RTL CSS not loaded properly")
    
    print("\n🎉 Basic middleware test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure enhanced_biblia_middleware.py is in the correct location")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\n" + "="*50)
print("Manual Test Instructions:")
print("1. Start the Django development server")
print("2. Navigate to a page in Hebrew")
print("3. Check browser dev tools for:")
print("   - RTL CSS injection in <head>")
print("   - class='rtl' on <body>")
print("   - Hebrew translations in UI")
print("   - Correct dropdown positioning")
print("="*50)