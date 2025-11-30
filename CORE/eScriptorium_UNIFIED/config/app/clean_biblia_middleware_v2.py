"""
Clean BiblIA Translation and RTL Middleware - Version 2 (SAFE)
Enhanced version that safely translates HTML without breaking JavaScript/CSS

✅ SAFE VERSION: Only translates visible HTML text
❌ AVOIDS: <script>, <style>, JSON data, attributes

Key Improvements:
1. Parses HTML properly instead of string replacement
2. Only translates text nodes (visible content)
3. Skips <script>, <style>, and <noscript> tags
4. Preserves attributes, data-*, and JSON intact
5. Uses BeautifulSoup for safe HTML manipulation

Usage in settings.py:
    'clean_biblia_middleware_v2.CleanBibliaMiddlewareV2',
"""

import re
import json
from django.utils.translation import get_language
from bs4 import BeautifulSoup, NavigableString, Comment


class CleanBibliaMiddlewareV2:
    """
    Safe middleware for BiblIA Hebrew/Arabic support
    Uses proper HTML parsing to avoid breaking JavaScript/CSS
    """

    def __init__(self, get_response):
        self.get_response = get_response
        
        # RTL CSS injection
        self.rtl_css = '''
<style>
body.rtl {
    direction: rtl !important;
    text-align: right !important;
}
body.rtl .navbar-brand {
    margin-right: 0;
    margin-left: 1rem;
}
body.rtl .ml-auto {
    margin-left: 0 !important;
    margin-right: auto !important;
}
</style>
'''
        
        # Translation map - MINIMAL FALLBACK ONLY
        # Most translations should be in django.po, not here!
        self.translation_map = {
            # Transcription names and export formats (unique to middleware - can't be in django.po)
            'manual': 'ידני',
            'ALTO': 'ALTO',
            'OpenITI mARkdown': 'OpenITI mARkdown',
            'OpenITI TEI XML': 'OpenITI TEI XML',
            
            # NOTE: Typologies (Title, Main, etc.) are handled by typology_translations_he.py
            # NOTE: UI strings (Save, Delete, etc.) should be in django.po
            # This middleware is only for FALLBACK translations and RTL support
        }

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only process HTML responses
        content_type = response.get('Content-Type', '')
        if not content_type.startswith('text/html'):
            return response
            
        if not hasattr(response, 'content'):
            return response
        
        current_language = get_language()
        
        # Debug logging
        print(f"🔍 CleanBibliaMiddlewareV2: current_language = {current_language}")
        
        # Apply RTL and translations ONLY for Hebrew and Arabic
        # Other languages (like French) use standard Django i18n
        if current_language not in ['he', 'ar']:
            print(f"✅ Using standard Django i18n for {current_language}")
            return response
        
        print(f"✅ Applying Hebrew/Arabic RTL transformations...")
        
        try:
            content = response.content.decode('utf-8')
            
            print(f"📄 Processing HTML ({len(content)} bytes)...")
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. Inject RTL CSS into <head>
            head = soup.find('head')
            if head:
                rtl_style = soup.new_tag('style')
                rtl_style.string = '''
body.rtl {
    direction: rtl !important;
    text-align: right !important;
}
body.rtl .navbar-brand {
    margin-right: 0;
    margin-left: 1rem;
}
body.rtl .ml-auto {
    margin-left: 0 !important;
    margin-right: auto !important;
}
'''
                head.append(rtl_style)
            
            # 2. Add RTL class to <body>
            body = soup.find('body')
            if body:
                existing_classes = body.get('class', [])
                if isinstance(existing_classes, str):
                    existing_classes = existing_classes.split()
                if 'rtl' not in existing_classes:
                    existing_classes.append('rtl')
                body['class'] = existing_classes
            
            # 3. Translate text nodes (SAFELY - only visible text)
            self._translate_text_nodes(soup)
            
            # 4. Update response content
            # Use formatter=None to preserve emojis and special characters
            response.content = str(soup).encode('utf-8', errors='replace')
            response['Content-Length'] = len(response.content)
            
            print(f"✅ Translation completed! New size: {len(response.content)} bytes")
            
        except Exception as e:
            # If parsing fails, return original response
            print(f"❌ CleanBibliaMiddlewareV2 error: {e}")
            import traceback
            traceback.print_exc()
            pass
        
        return response
    
    def _translate_text_nodes(self, soup):
        """
        Safely translate only text nodes in HTML
        Skips: <script>, <style>, <noscript>, comments, attributes
        """
        # Tags to skip (don't translate their content)
        skip_tags = {'script', 'style', 'noscript', 'code', 'pre'}
        
        def translate_element(element):
            """Recursively translate text in element"""
            # Skip if it's a tag we should ignore
            if hasattr(element, 'name') and element.name in skip_tags:
                return
            
            # Skip comments
            if isinstance(element, Comment):
                return
            
            # If it's a text node (NavigableString)
            if isinstance(element, NavigableString):
                if isinstance(element, Comment):
                    return
                    
                # Get the text
                text = str(element).strip()
                if not text:
                    return
                
                # Translate each word while preserving structure
                translated = self._translate_text(text)
                if translated != text:
                    element.replace_with(translated)
                return
            
            # Recursively process children
            if hasattr(element, 'children'):
                # Process children (make a list to avoid modification during iteration)
                for child in list(element.children):
                    translate_element(child)
        
        # Start translation from body or entire soup
        body = soup.find('body')
        if body:
            translate_element(body)
        else:
            translate_element(soup)
    
    def _translate_text(self, text):
        """
        Translate text while preserving whitespace and structure
        Only translates whole words, not partial matches
        """
        result = text
        
        # Sort by length (longer phrases first) to avoid partial replacements
        sorted_translations = sorted(
            self.translation_map.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
        
        for english, hebrew in sorted_translations:
            # Use word boundaries to match whole words only
            # Pattern: word boundary + english + word boundary
            pattern = rf'\b{re.escape(english)}\b'
            result = re.sub(pattern, hebrew, result, flags=re.IGNORECASE)
        
        return result
