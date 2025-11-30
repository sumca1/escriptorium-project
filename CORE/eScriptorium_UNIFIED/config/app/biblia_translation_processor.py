# BiblIA Custom Translation Context Processor
# Hebrew translations for hardcoded strings in eScriptorium templates

from django.conf import settings
from django.utils.translation import get_language

def biblia_translations(request):
    """
    Context processor שמוסיף תרגומים לעברית עבור מחרוזות קשות
    """
    
    # פעל רק כאשר השפה היא עברית
    if get_language() != 'he':
        return {}
    
    # מילון תרגומים עבור מחרוזות קשות
    hebrew_translations = {
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
        
        # Contributors page (if exists)
        'Core Project Team': 'צוות הפרויקט הליבה',
        'Steering Committee': 'ועד ההיגוי',
        'Former Committee Members': 'חברי ועד לשעבר',
        
        # Technical terms
        'Python': 'Python',
        'Django': 'Django',
        'Vue.js': 'Vue.js',
        
        # BiblIA specific
        'BiblIA Dataset Project': 'פרויקט מאגר BiblIA',
        'Hebrew OCR & HTR Research Initiative': 'יוזמת המחקר לזיהוי תווים עבריים',
    }
    
    return {
        'BIBLIA_TRANSLATIONS': hebrew_translations,
    }