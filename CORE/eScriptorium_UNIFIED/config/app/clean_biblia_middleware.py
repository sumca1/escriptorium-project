"""
Clean BiblIA Translation and RTL Middleware
Simple and clean approach for Hebrew/Arabic support

⚠️ WARNING: This middleware is currently DISABLED in settings.py
REASON: The text replacement approach (lines 140-145) causes HTML corruption:
- Replaces text inside <script> tags, breaking JSON and JavaScript
- Replaces Vue.js component attributes, breaking reactivity
- Replaces data-* attributes, breaking client-side code
- Conflicts with Vue i18n system

PROBLEM CODE (lines 140-145):
    for english, hebrew in self.translation_map.items():
        content = re.sub(rf'\b{escaped_english}\b', hebrew, content)

This replaces words EVERYWHERE in HTML, including:
- Inside <script>...</script> tags → breaks JavaScript
- Inside JSON data → breaks parsing
- Inside Vue component props → breaks Vue.js
- Inside HTML attributes → breaks functionality

SOLUTION: Use Django i18n and Vue i18n instead:
- Backend: {% trans "Text" %} in templates, _("Text") in Python
- Frontend: $t('Text') in Vue components
- Both systems use locale files (django.po, he.json) which we fixed

See: MIDDLEWARE_PROBLEM_ANALYSIS.md for full details
"""

import re
import json
from django.utils.translation import get_language

class CleanBibliaMiddleware:
    """
    Clean middleware for BiblIA Hebrew/Arabic support
    """

    def __init__(self, get_response):
        self.get_response = get_response
        
        # Basic translation map
        self.translation_map = {
            # Core UI elements
            'Documents': 'מסמכים',
            'Projects': 'פרוייקטים', 
            'Models': 'מודלים',
            'My Models': 'המודלים שלי',
            'Profile': 'פרופיל',
            'Task reports': 'דוחות משימות',
            'Site administration': 'ניהול האתר',
            'Change password': 'שינוי סיסמה',
            'Logout': 'התנתק',
            'Login': 'התחבר',
            'Home': 'בית',
            'Settings': 'הגדרות',
            'Help': 'עזרה',
            'Search': 'חפש',
            'Upload': 'העלה',
            'Download': 'הורד',
            'Export': 'יצוא',
            'Import': 'יבוא',
            'Delete': 'מחק',
            'Edit': 'ערוך',
            'Create': 'צור',
            'Save': 'שמור',
            'Cancel': 'ביטול',
            'Back': 'חזור',
            'Next': 'הבא',
            'Previous': 'הקודם',
            
            # Vue component specific translations
            'Name': 'שם',
            'Typology': 'טיפולוגיה',
            'Element': 'אלמנט',
            'Comments': 'הערות',
            'Metadata': 'מטא-דטה',
            'Select': 'בחר',
            
            # Additional Vue components and modals
            'Transcriptions management': 'ניהול תמלולים',
            'Transcription management': 'ניהול תמלול',
            'Compare': 'השווה',
            'manual': 'ידני',
            'Close': 'סגור',
            
            # Modal and tooltip translations
            'Add': 'הוסף',
            'Remove': 'הסר',
            'Apply': 'החל',
            'Confirm': 'אשר',
            'OK': 'אישור',
            'Yes': 'כן',
            'No': 'לא',
            'Submit': 'שלח',
            'Reset': 'אפס',
            'Clear': 'נקה',
            'All': 'הכל',
            'None': 'ללא',
            'Loading...': 'טוען...',
            'Error': 'שגיאה',
            'Warning': 'אזהרה',
            'Success': 'הצלחה',
            'Info': 'מידע',
        }
        
        # Simple RTL CSS
        self.rtl_css = '''
<style>
.rtl {
    direction: rtl;
    text-align: right;
}
.rtl .navbar-nav {
    direction: rtl;
}
.rtl .dropdown-menu-left {
    right: 0 !important;
    left: auto !important;
}
.rtl .dropdown-menu-right {
    left: 0 !important;
    right: auto !important;
}
</style>'''

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only process HTML responses
        if (response.get('Content-Type', '').startswith('text/html') and 
            hasattr(response, 'content')):
            
            current_language = get_language()
            
            # Apply RTL and translations for Hebrew and Arabic
            if current_language in ['he', 'ar']:
                content = response.content.decode('utf-8')
                
                # 1. Inject RTL CSS
                if '<head>' in content:
                    content = content.replace('<head>', f'<head>{self.rtl_css}')
                
                # 2. Add RTL class to body (append if class attribute exists)
                def add_rtl(match):
                    attrs = match.group(1)
                    if 'class=' in attrs:
                        def append_rtl(m):
                            classes = m.group(1)
                            existing = classes.split()
                            if 'rtl' in existing:
                                return f'class="{classes}"'
                            return f'class="{classes} rtl"'
                        attrs_with_class = re.sub(r'class="([^"]*)"', append_rtl, attrs, count=1)
                        return f'<body{attrs_with_class}>'
                    return f'<body{attrs} class="rtl">'

                content = re.sub(r'<body([^>]*)>', add_rtl, content, count=1)
                
                # 3. Apply translations
                for english, hebrew in self.translation_map.items():
                    # Escape special regex characters
                    escaped_english = re.escape(english)
                    content = re.sub(rf'\b{escaped_english}\b', hebrew, content)
                
                # 4. Add client-side translation
                translations_json = json.dumps(self.translation_map, ensure_ascii=False)
                js_script = f'''
<script>
window.BiblIATranslations = {translations_json};
window.translateText = function(text) {{
    return window.BiblIATranslations[text.trim()] || text;
}};
window.translateElements = function() {{
    document.querySelectorAll('label, option, small, button').forEach(function(el) {{
        if (el.textContent && !el.hasAttribute('data-translated')) {{
            const translated = window.translateText(el.textContent.trim());
            if (translated !== el.textContent.trim()) {{
                el.textContent = translated;
                el.setAttribute('data-translated', 'true');
            }}
        }}
    }});
}};
if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', window.translateElements);
}} else {{
    window.translateElements();
}}
setInterval(window.translateElements, 2000);
</script>
'''
                
                # Insert script before closing body tag
                if '</body>' in content:
                    content = content.replace('</body>', js_script + '\n</body>')
                
                response.content = content.encode('utf-8')
                response['Content-Length'] = len(response.content)
        
        return response