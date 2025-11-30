"""
Enhanced BiblIA Translation and RTL Middleware
Combines the best of both approaches while preserving core file integrity
"""

import re
from django.utils.translation import get_language

class EnhancedBibliaMiddleware:
    """
    Enhanced middleware that provides:
    1. Complete translation mapping (from CLEAN version)
    2. Advanced RTL CSS injection (from original version)
    3. Dynamic HTML modifications without touching core files
    4. Context-aware dropdown positioning and navigation
    5. Israeli flag replacement for Hebrew language interface
    """

    def __init__(self, get_response):
        self.get_response = get_response
        
        # Extended translation map from CLEAN + additional terms
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
            'Please be aware that the epoch versions are different and might affect training.': 'אנא שים לב שגרסאות ה-epoch שונות ועלולות להשפיע על האימון.',
            'If left empty the name will automatically be {typology+index number}': 'אם נשאר ריק השם יהיה אוטומטית {טיפולוגיה+מספר אינדקס}',
            
            # Additional Vue components and modals
            'Transcriptions management': 'ניהול תמלולים',
            'Transcription management': 'ניהול תמלול',
            'Compare': 'השווה',
            'Delete': 'מחק',
            'manual': 'ידני',
            'Close': 'סגור',
            '×': '×',  # Close button symbol - keep as is
            
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
            'Please wait...': 'אנא המתן...',
            'Error': 'שגיאה',
            'Warning': 'אזהרה',
            'Success': 'הצלחה',
            'Info': 'מידע',
            
            # Common UI elements
            'Show': 'הצג',
            'Hide': 'הסתר',
            'Expand': 'הרחב',
            'Collapse': 'צמצם',
            'More': 'עוד',
            'Less': 'פחות',
            'View': 'תצוגה',
            'Edit': 'ערוך',
            'Copy': 'העתק',
            'Paste': 'הדבק',
            'Cut': 'גזור',
            'Undo': 'בטל',
            'Redo': 'בצע שוב',
            
            # Tooltip and hover messages
            'Click to edit': 'לחץ לעריכה',
            'Click to delete': 'לחץ למחיקה',
            'Click to select': 'לחץ לבחירה',
            'Click to expand': 'לחץ להרחבה',
            'Double click to edit': 'לחיצה כפולה לעריכה',
            'Right click for options': 'לחיצה ימנית לאפשרויות',
            'Drag to reorder': 'גרור לסידור מחדש',
            'Hold Shift and click': 'החזק Shift ולחץ',
            'Hold Ctrl and click': 'החזק Ctrl ולחץ',
            'Press Enter to confirm': 'לחץ Enter לאישור',
            'Press Escape to cancel': 'לחץ Escape לביטול',
            
            # Missing translations found in coverage check
            'Or': 'או',
            'The document pointed to by the given uri doesn\'t seem to be valid json.': 'המסמך המצביע על ידי ה-URI הנתון לא נראה כ-JSON תקף.',
            'The document pointed to by the given uri doesn\'t seem to be valid json.': 'המסמך המצויין ב-URI הנתון לא נראה כ-JSON תקין.',
            
            # Status messages
            'Ready': 'מוכן',
            'Processing': 'מעבד',
            'Completed': 'הושלם',
            'Failed': 'נכשל',
            'Cancelled': 'בוטל',
            'Pending': 'ממתין',
            'In progress': 'בתהליך',
            'Draft': 'טיוטה',
            'Published': 'פורסם',
            'Active': 'פעיל',
            'Inactive': 'לא פעיל',
            'Available': 'זמין',
            'Unavailable': 'לא זמין',
            
            # Transcription related
            'Manage transcriptions': 'נהל תמלולים',
            'Create new transcription': 'צור תמלול חדש',
            'Edit transcription': 'ערוך תמלול',
            'Delete transcription': 'מחק תמלול',
            'Compare transcriptions': 'השווה תמלולים',
            'Export transcription': 'יצא תמלול',
            'Import transcription': 'יבא תמלול',
            
# Long help messages temporarily removed for debugging
            
            # Additional UI terms that might appear
            'en masse': 'בקבוצה',
            'control point': 'נקודת בקרה',
            'control points': 'נקודות בקרה',
            'lasso selection': 'בחירת לאסו',
            'free drawing': 'ציור חופשי',
            'region mode': 'מצב אזורים',
            'cut mode': 'מצב חיתוך',
            'rectangular region': 'אזור מלבני',
            'segmentation': 'פילוח',
            'masks': 'מסכות',
            'Only masks': 'רק מסכות',
            'reverse': 'היפוך',
            'linked': 'מקושר',
            'unlinked': 'מנותק',
            'join': 'חיבור',
            'split': 'פיצול',
            'undo': 'בטל',
            'redo': 'בצע שוב',
            'Submit': 'שלח',
            'Reset': 'איפס',
            'Clear': 'נקה',
            
            # Advanced features from original version
            'Task Monitoring & Reports': 'מעקב משימות ודוחות',
            'Built-in Task Reports': 'דוחות משימות מובנים',
            'Monitoring Dashboard': 'לוח בקרה לניטור',
            'Flower Dashboard': 'לוח בקרה Flower',
            'System Maintenance': 'תחזוקת מערכת',
            'Tasks monitoring': 'מעקב משימות',
            'Leaderboard': 'לוח מובילים',
            
            # Additional UI elements
            'Language': 'שפה',
            'English': 'אנגלית',
            'Hebrew': 'עברית',
            'French': 'צרפתית', 
            'German': 'גרמנית',
            
            # Status and actions
            'Active': 'פעיל',
            'Inactive': 'לא פעיל',
            'Pending': 'ממתין',
            'Complete': 'הושלם',
            'Failed': 'נכשל',
            'Processing': 'מעבד',
            'Ready': 'מוכן',
            'Error': 'שגיאה',
            'Success': 'הצלחה',
            'Warning': 'אזהרה',
            'Info': 'מידע',
        }
        
        # Advanced RTL CSS - based on original version but enhanced
        self.enhanced_rtl_css = '''
<style>
/* Enhanced RTL Support - Based on original but improved */
.rtl {
    direction: rtl;
    text-align: right;
}

/* Navigation and dropdowns - enhanced from original */
.rtl .navbar-nav {
    direction: rtl;
}

.rtl .dropdown-menu-left {
    right: 0 !important;
    left: auto !important;
}

.rtl .dropdown-menu-right {
    right: auto !important;
    left: 0 !important;
}

/* Modal and dialog improvements */
#trans-modal .modal-body.rtl #trans-input {
    transform-origin: top right;
    text-align: right;
}

/* Table and list alignments */
.rtl .d-table .d-table-cell {
    text-align: right;
}

.rtl .trans-box span {
    transform-origin: top right;
}

/* Line and region borders - from original */
.rtl .line-order, .rtl .line-region{
    border-right: 0;
    border-left: 1px solid lightgrey;
}

/* Diplomatic lines formatting - enhanced */
.rtl #diplomatic-lines div {
    text-align: right;
    margin-left: .5rem;
    padding-right: 50px;
    direction: rtl;
}

.rtl #diplomatic-lines div:before {
    margin-right: -50px;
    margin-left: .5rem;
    border-left: 1px solid #ddd;
    border-right: none;
}

/* Form controls RTL */
.rtl .form-control {
    text-align: right;
    direction: rtl;
}

.rtl .form-group label {
    text-align: right;
    display: block;
}

/* Button groups RTL */
.rtl .btn-group {
    direction: rtl;
}

.rtl .btn-group > .btn:first-child {
    border-top-right-radius: .25rem;
    border-bottom-right-radius: .25rem;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
}

.rtl .btn-group > .btn:last-child {
    border-top-left-radius: .25rem;
    border-bottom-left-radius: .25rem;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
}

/* Enhanced navigation spacing */
.rtl .nav-link {
    padding-right: 1rem;
    padding-left: 1rem;
    text-align: right;
}

/* Breadcrumb RTL */
.rtl .breadcrumb {
    direction: rtl;
}

.rtl .breadcrumb-item + .breadcrumb-item::before {
    content: "\\";
    float: right;
    padding-right: 0;
    padding-left: .5rem;
}

/* Card components RTL */
.rtl .card-header {
    text-align: right;
}

.rtl .card-body {
    text-align: right;
}

/* Alert components RTL */
.rtl .alert {
    text-align: right;
}

/* List group RTL */
.rtl .list-group-item {
    text-align: right;
}

/* Pagination RTL */
.rtl .pagination {
    direction: rtl;
}

/* Enhanced font support */
.rtl {
    font-family: 'Arial', 'Tahoma', 'David', 'Times New Roman', sans-serif;
}

/* Sidebar and panels RTL */
.rtl .sidebar {
    direction: rtl;
    text-align: right;
}

.rtl .panel {
    direction: rtl;
    text-align: right;
}

/* Toast notifications RTL */
.rtl .toast {
    direction: rtl;
    text-align: right;
}

/* Enhanced for Hebrew text rendering */
.rtl p, .rtl div, .rtl span {
    direction: rtl;
    text-align: right;
    unicode-bidi: embed;
}

/* Special handling for mixed content */
.rtl .mixed-content {
    direction: rtl;
    text-align: right;
    unicode-bidi: plaintext;
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
                
                # 1. Inject enhanced RTL CSS into head
                if '<head>' in content:
                    content = content.replace('<head>', f'<head>{self.enhanced_rtl_css}')
                
                # 2. Add RTL class to body dynamically
                if '<body' in content and 'class=' in content:
                    # Find existing class attribute and add rtl
                    content = re.sub(
                        r'<body([^>]*class=")([^"]*)"',
                        r'<body\1\2 rtl"',
                        content
                    )
                elif '<body' in content:
                    # Add class attribute with rtl
                    content = re.sub(
                        r'<body([^>]*)>',
                        r'<body\1 class="rtl">',
                        content
                    )
                
                # 3. Fix dropdown positioning for RTL
                content = content.replace(
                    'dropdown-menu-right',
                    'dropdown-menu-left'
                )
                
                # 4. Add RTL attributes to language selector dropdowns
                content = re.sub(
                    r'(<ul class="dropdown-menu[^"]*"[^>]*)(>)',
                    r'\1 style="left: 0; right: auto;"\2',
                    content
                )
                
                # 5. Apply translations
                for english, hebrew in self.translation_map.items():
                    # More sophisticated replacement that avoids replacing within attributes
                    content = re.sub(
                        rf'(?<=>)([^<]*?{re.escape(english)}[^<]*?)(?=<)',
                        lambda m: m.group(1).replace(english, hebrew),
                        content
                    )
                
                # 6. Add Hebrew language metadata
                if '<html' in content:
                    content = re.sub(
                        r'<html([^>]*?)>',
                        r'<html\1 lang="he" dir="rtl">',
                        content
                    )
                
                # 7. Replace flags with Israeli flag for Hebrew
                if current_language == 'he':
                    # Replace flag images with Israeli flag
                    content = re.sub(
                        r'(<img[^>]*flag-icon[^>]*flag-icon-)(gb|us|en)([^>]*>)',
                        r'\1il\3',
                        content,
                        flags=re.IGNORECASE
                    )
                    
                    # Replace CSS flag classes with Israeli flag
                    content = re.sub(
                        r'(flag-icon-)(gb|us|en)(\b)',
                        r'\1il\3',
                        content,
                        flags=re.IGNORECASE
                    )
                    
                    # Replace any span elements with flag classes
                    content = re.sub(
                        r'(<span[^>]*class="[^"]*flag[^"]*)(gb|us|en)([^"]*"[^>]*>)',
                        r'\1il\3',
                        content,
                        flags=re.IGNORECASE
                    )
                
                # Add client-side JavaScript for Vue component translation
                import json
                try:
                    translations_json = json.dumps(self.translation_map, ensure_ascii=False)
                except Exception as e:
                    print(f"JSON serialization error: {e}")
                    translations_json = '{}'
                
                js_translation_script = f'''
                <script>
                // BiblIA Client-side Translation for Vue Components
                try {{
                    window.BiblIATranslations = {translations_json};
                }} catch(e) {{
                    console.error('Translation data error:', e);
                    window.BiblIATranslations = {{}};
                }}
                
                window.translateText = function(text) {{
                    if (typeof text === 'string') {{
                        text = text.trim();
                        if (window.BiblIATranslations[text]) {{
                            return window.BiblIATranslations[text];
                        }}
                    }}
                    return text;
                }};
                
                // Add Vue prototype method for translation
                if (typeof Vue !== 'undefined') {{
                    Vue.prototype.$t = function(text) {{
                        return window.translateText(text);
                    }};
                }}
                
                window.translateElements = function() {{
                    // Translate Vue component labels
                    document.querySelectorAll('label').forEach(function(label) {{
                        if (label.textContent && label.textContent.trim() && !label.hasAttribute('data-translated')) {{
                            const original = label.textContent.trim();
                            const translated = window.translateText(original);
                            if (translated !== original) {{
                                label.textContent = translated;
                                label.setAttribute('data-translated', 'true');
                            }}
                        }}
                    }});
                    
                    // Translate options in select elements
                    document.querySelectorAll('option').forEach(function(option) {{
                        if (option.textContent && option.textContent.trim() && !option.hasAttribute('data-translated')) {{
                            const original = option.textContent.trim();
                            const translated = window.translateText(original);
                            if (translated !== original) {{
                                option.textContent = translated;
                                option.setAttribute('data-translated', 'true');
                            }}
                        }}
                    }});
                    
                    // Translate small text elements
                    document.querySelectorAll('small').forEach(function(small) {{
                        if (small.textContent && small.textContent.trim() && !small.hasAttribute('data-translated')) {{
                            const original = small.textContent.trim();
                            const translated = window.translateText(original);
                            if (translated !== original) {{
                                small.textContent = translated;
                                small.setAttribute('data-translated', 'true');
                            }}
                        }}
                    }});
                    
                    // Translate placeholder attributes
                    document.querySelectorAll('[placeholder]').forEach(function(element) {{
                        if (element.placeholder && element.placeholder.trim() && !element.hasAttribute('data-placeholder-translated')) {{
                            const original = element.placeholder.trim();
                            const translated = window.translateText(original);
                            if (translated !== original) {{
                                element.placeholder = translated;
                                element.setAttribute('data-placeholder-translated', 'true');
                            }}
                        }}
                    }});
                    
                    // Translate titles attributes
                    document.querySelectorAll('[title]').forEach(function(element) {{
                        if (element.title && element.title.trim() && !element.hasAttribute('data-title-translated')) {{
                            const original = element.title.trim();
                            const translated = window.translateText(original);
                            if (translated !== original) {{
                                element.title = translated;
                                element.setAttribute('data-title-translated', 'true');
                            }}
                        }}
                    }});
                    
                    // Translate aria-label attributes  
                    document.querySelectorAll('[aria-label]').forEach(function(element) {{
                        if (element.getAttribute('aria-label') && element.getAttribute('aria-label').trim() && !element.hasAttribute('data-aria-translated')) {{
                            const original = element.getAttribute('aria-label').trim();
                            const translated = window.translateText(original);
                            if (translated !== original) {{
                                element.setAttribute('aria-label', translated);
                                element.setAttribute('data-aria-translated', 'true');
                            }}
                        }}
                    }});
                    
                    // Translate data-original-title attributes (Bootstrap tooltips)
                    document.querySelectorAll('[data-original-title]').forEach(function(element) {{
                        if (element.getAttribute('data-original-title') && element.getAttribute('data-original-title').trim() && !element.hasAttribute('data-tooltip-translated')) {{
                            const original = element.getAttribute('data-original-title').trim();
                            const translated = window.translateText(original);
                            if (translated !== original) {{
                                element.setAttribute('data-original-title', translated);
                                element.setAttribute('data-tooltip-translated', 'true');
                            }}
                        }}
                    }});
                    
                    // Translate Bootstrap tooltip titles
                    document.querySelectorAll('[data-toggle="tooltip"]').forEach(function(element) {{
                        if (element.getAttribute('data-original-title') && !element.hasAttribute('data-bs-tooltip-translated')) {{
                            const original = element.getAttribute('data-original-title').trim();
                            const translated = window.translateText(original);
                            if (translated !== original) {{
                                element.setAttribute('data-original-title', translated);
                                element.setAttribute('data-bs-tooltip-translated', 'true');
                            }}
                        }}
                    }});
                    
                    // Translate button text
                    document.querySelectorAll('button').forEach(function(button) {{
                        if (button.textContent && button.textContent.trim() && !button.hasAttribute('data-translated')) {{
                            const original = button.textContent.trim();
                            const translated = window.translateText(original);
                            if (translated !== original) {{
                                button.textContent = translated;
                                button.setAttribute('data-translated', 'true');
                            }}
                        }}
                    }});
                }};
                
                // Initial translation
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', function() {{
                        setTimeout(window.translateElements, 500); // Delay for Vue to mount
                    }});
                }} else {{
                    setTimeout(window.translateElements, 500);
                }}
                
                // Re-translate on Vue component updates with throttling
                let translationTimer = null;
                const observer = new MutationObserver(function(mutations) {{
                    let shouldTranslate = false;
                    mutations.forEach(function(mutation) {{
                        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {{
                            shouldTranslate = true;
                        }}
                    }});
                    if (shouldTranslate) {{
                        clearTimeout(translationTimer);
                        translationTimer = setTimeout(window.translateElements, 300);
                    }}
                }});
                
                observer.observe(document.body, {{
                    childList: true,
                    subtree: true
                }});
                
                // Re-translate every 2 seconds for Vue updates
                setInterval(window.translateElements, 2000);
                </script>
                '''
                
                # Insert the script before closing body tag
                if '</body>' in content:
                    content = content.replace('</body>', js_translation_script + '\n</body>')
                
                response.content = content.encode('utf-8')
                response['Content-Length'] = len(response.content)
        
        return response
        
        return response