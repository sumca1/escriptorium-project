# BiblIA Template Tags for Hebrew Translation
# Custom template tags for translating hardcoded strings

from django import template
from django.utils.translation import get_language
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()

# מילון תרגומים עבור מחרוזות קשות
HEBREW_TRANSLATIONS = {
    # Models page
    'Please be aware that the epoch versions of the models will only be available for': 
        'אנא שימו לב שגרסאות האפוק של המודלים יהיו זמינות רק במשך',
    
    'days': 'ימים',
    
    # Common UI strings
    'Digital Library': 'ספרייה דיגיטלית',
    'eScriptorium': 'eScriptorium',
    'Transcription': 'תמלול',
    'All': 'הכל',
    'green': 'ירוק',
    'red': 'אדום',
    'additions': 'תוספות',
    'deletions': 'מחיקות',
    
    # Email templates
    'Hello escriptorium Admin': 'שלום מנהל eScriptorium',
    'Sincerely, the eScriptorium team': 'בכבוד רב, צוות eScriptorium',
    'You can find it': 'ניתן למצוא אותו',
    'here': 'כאן',
    
    # User interface
    'Into group': 'לקבוצה',
    "You didn't send any invitations yet": 'לא שלחת עדיין הזמנות',
    'Create a new Team': 'צור צוות חדש',
    'Create': 'צור',
    'Pending Invitations': 'הזמנות ממתינות',
    'My Teams': 'הצוותים שלי',
    'Invited to': 'הוזמן אל',
    'by': 'על ידי',
    
    # Forms and labels
    'Email address': 'כתובת אימייל',
    'Reset my password': 'אפס את הסיסמה שלי',
    'Change your password': 'שנה את הסיסמה שלך',
    'Forgotten your password? Enter your email address below, and we\'ll email instructions for setting a new one.':
        'שכחת את הסיסמה? הזן את כתובת האימייל שלך למטה, ואנחנו נשלח הוראות לקביעת סיסמה חדשה.',
    
    # Navigation and common words
    'First page': 'עמוד ראשון',
    'Last page': 'עמוד אחרון',
    'Previous': 'קודם',
    'Next': 'הבא',
    'Toggle navigation': 'החלף ניווט',
    
    # Contributors page
    'Core Project Team': 'צוות הפרויקט הליבה',
    'Steering Committee': 'ועד ההיגוי',
    'Former Committee Members': 'חברי ועד לשעבר',
    
    # BiblIA specific
    'BiblIA Dataset Project': 'פרויקט מאגר BiblIA',
    'Hebrew OCR & HTR Research Initiative': 'יוזמת המחקר לזיהוי תווים עבריים',
}

@register.filter
def biblia_translate(value):
    """
    Template filter לתרגום אוטומטי של מחרוזות קשות לעברית
    
    Usage: {{ "Some English text"|biblia_translate }}
    """
    if get_language() != 'he':
        return value
    
    # נסה למצוא תרגום מדויק
    # Security: Only translate exact matches from hardcoded dictionary
    if str(value) in HEBREW_TRANSLATIONS:
        # nosec B308, B703: Translation comes from hardcoded HEBREW_TRANSLATIONS dict
        return mark_safe(HEBREW_TRANSLATIONS[str(value)])  # nosec B308 nosec B703
    
    # נסה למצוא תרגום חלקי (לתמיכה במשתנים)
    # Security: Escape user input before replacing, then mark translated parts safe
    str_value = str(value)
    for english, hebrew in HEBREW_TRANSLATIONS.items():
        if english in str_value:
            # Escape the entire string first to prevent XSS
            escaped_value = escape(str_value)
            # Now replace the known-safe English text with known-safe Hebrew
            translated = escaped_value.replace(escape(english), hebrew)
            # nosec B308, B703: Input is escaped, replacement values from hardcoded dict
            return mark_safe(translated)  # nosec B308 nosec B703
    
    return value

@register.simple_tag
def biblia_text(english_text):
    """
    Template tag לתרגום ישיר של מחרוזת
    
    Usage: {% biblia_text "Some English text" %}
    """
    if get_language() != 'he':
        return english_text
    
    # Security: Only return translations from hardcoded dictionary
    if english_text in HEBREW_TRANSLATIONS:
        # nosec B308, B703: Translation from hardcoded HEBREW_TRANSLATIONS dict
        return mark_safe(HEBREW_TRANSLATIONS[english_text])  # nosec B308 nosec B703
    
    return english_text

@register.inclusion_tag('biblia_templates/translated_message.html', takes_context=True)
def biblia_message(context, english_text, **kwargs):
    """
    Inclusion tag להצגת הודעות מתורגמות
    
    Usage: {% biblia_message "Please be aware that..." days=retention_days %}
    """
    if get_language() == 'he' and english_text in HEBREW_TRANSLATIONS:
        translated_text = HEBREW_TRANSLATIONS[english_text]
    else:
        translated_text = english_text
    
    context.update({
        'message_text': translated_text,
        **kwargs
    })
    
    return context


@register.simple_tag
def israel_flag(size=1):
    """
    Template tag להצגת דגל ישראל 🇮🇱 עבור עברית
    
    Usage: {% israel_flag 1 %}
    
    Args:
        size: גודל הדגל (1-3)
    """
    # דגל ישראל כ-emoji
    flag_emoji = '🇮🇱'
    
    # אפשרות להשתמש בתמונה במקום emoji
    # return mark_safe(f'<img src="/static/flags/il.png" alt="Israel" width="{size * 16}">')
    
    # nosec B308: Hardcoded emoji string, no user input
    return mark_safe(flag_emoji)  # nosec B308