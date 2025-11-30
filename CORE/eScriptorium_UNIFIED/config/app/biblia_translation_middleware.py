# BiblIA Translation Middleware
# Automatic Hebrew translation for hardcoded strings in eScriptorium
# This middleware intercepts HTTP responses and replaces English hardcoded strings with Hebrew

import re
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import get_language

class BibliaTranslationMiddleware(MiddlewareMixin):
    """
    Middleware שמחליף מחרוזות קשות באנגלית במקבילות העבריות
    עובד על כל תגובות ה-HTML ללא צורך לשנות קבצי ליבה
    """
    
    # מילון תרגומים עבור מחרוזות קשות
    TRANSLATION_MAP = {
        # Models page
        r'Please be aware that the epoch versions of the models will only be available for \{\{ MODELS_VERSION_RETENTION \}\} days\.':
            'אנא שימו לב שגרסאות האפוק של המודלים יהיו זמינות רק במשך {{ MODELS_VERSION_RETENTION }} ימים.',
        
        r'Please be aware that the epoch versions of the models will only be available for':
            'אנא שימו לב שגרסאות האפוק של המודלים יהיו זמינות רק במשך',
        'Please be aware that the epoch versions of the models will only be available for':
            'אנא שימו לב שגרסאות האפוק של המודלים יהיו זמינות רק במשך',

        # Added robust numeric pattern (in case template rendered to a concrete number like 30)
        # Example original: "Please be aware that the epoch versions of the models will only be available for 30 days." 
        # Use a capturing group for the number so it is preserved. Fixed to handle zero with \d* instead of \d+
        r'Please be aware that the epoch versions of the models will only be available for (\d*) days\.':
            r'אנא שימו לב שגרסאות האפוק של המודלים יהיו זמינות רק במשך \1 ימים.',
        
        # Common UI strings
        r'\bDigital Library\b': 'ספרייה דיגיטלית',
        r'\bTranscription\b': 'תמלול', 
        r'\bAll\b': 'הכל',
        r'\bgreen\b': 'ירוק',
        r'\bred\b': 'אדום', 
        r'\badditions\b': 'תוספות',
        r'\bdeletions\b': 'מחיקות',
        r'\bdays\b': 'ימים',
        
        # Legacy mode and system messages
        r'Legacy mode': 'מצב קלאסי',
        r'This page is not available in legacy mode\. Visit your user settings to disable legacy mode\.':
            'עמוד זה אינו זמין במצב קלאסי. בקר בהגדרות המשתמש שלך כדי לכבות את המצב הקלאסי.',
        
        # Project sharing messages (fixed to handle zero values with \d* instead of \d+)
        r'Project shared with (\d*) user': r'פרויקט משותף עם \1 משתמש',
        r'Project shared with (\d*) users': r'פרויקט משותף עם \1 משתמשים',
        r'Project shared with (\d*) group': r'פרויקט משותף עם \1 קבוצה',  
        r'Project shared with (\d*) groups': r'פרויקט משותף עם \1 קבוצות',
        
        # Explicit zero-value patterns for project sharing (backup safety)
        r'Project shared with 0 user': 'פרויקט משותף עם 0 משתמש',
        r'Project shared with 0 users': 'פרויקט משותף עם 0 משתמשים',
        r'Project shared with 0 group': 'פרויקט משותף עם 0 קבוצה',
        r'Project shared with 0 groups': 'פרויקט משותף עם 0 קבוצות',
        
        # Documents sharing messages (fixed to handle zero values with \d* instead of \d+)
        r'Documents shared with (\d*) user': r'מסמכים משותפים עם \1 משתמש',
        r'Documents shared with (\d*) users': r'מסמכים משותפים עם \1 משתמשים',
        r'Documents shared with (\d*) group': r'מסמכים משותפים עם \1 קבוצה',
        r'Documents shared with (\d*) groups': r'מסמכים משותפים עם \1 קבוצות',
        
        # Explicit zero-value patterns for document sharing (backup safety)
        r'Documents shared with 0 user': 'מסמכים משותפים עם 0 משתמש',
        r'Documents shared with 0 users': 'מסמכים משותפים עם 0 משתמשים',
        r'Documents shared with 0 group': 'מסמכים משותפים עם 0 קבוצה',
        r'Documents shared with 0 groups': 'מסמכים משותפים עם 0 קבוצות',
        
        # Additional sharing patterns that might appear
        r'shared with (\d*) user': r'משותף עם \1 משתמש',
        r'shared with (\d*) users': r'משותף עם \1 משתמשים',
        r'shared with (\d*) group': r'משותף עם \1 קבוצה',
        r'shared with (\d*) groups': r'משותף עם \1 קבוצות',
        r'shared with 0 user': 'משותף עם 0 משתמש',
        r'shared with 0 users': 'משותף עם 0 משתמשים',
        r'shared with 0 group': 'משותף עם 0 קבוצה',
        r'shared with 0 groups': 'משותף עם 0 קבוצות',
        
        # Email templates
        r'Hello escriptorium Admin': 'שלום מנהל eScriptorium',
        r'Sincerely, the eScriptorium team': 'בכבוד רב, צוות eScriptorium',
        r'You can find it': 'ניתן למצוא אותו',
        r'\bhere\b': 'כאן',
        
        # User interface 
        r'Into group': 'לקבוצה',
        r"You didn't send any invitations yet": 'לא שלחת עדיין הזמנות',
        r'Create a new Team': 'צור צוות חדש',
        r'\bCreate\b': 'צור',
        r'Pending Invitations': 'הזמנות ממתינות', 
        r'My Teams': 'הצוותים שלי',
        r'Invited to': 'הוזמן אל',
        r'\bby\b': 'על ידי',
        
        # Critical UI strings - Priority 1 (כפתורים וניווט קריטיים)
        r'\bHome\b': 'בית',
        r'\bClose\b': 'סגור',
        r'\bCancel\b': 'ביטול', 
        r'\bSave\b': 'שמור',
        r'\bDelete\b': 'מחק',
        r'\bEdit\b': 'ערוך',
        r'\bUpdate\b': 'עדכן',
        r'\bSubmit\b': 'שלח',
        r'\bConfirm\b': 'אישור',
        r'\bLogin\b': 'התחבר',
        r'\bLogout\b': 'התנתק',
        r'\bBack\b': 'חזרה',
        r'\bNext\b': 'הבא',
        r'\bPrevious\b': 'קודם',
        r'\bSign In\b': 'התחבר',
        r'Back to homepage': 'חזור לעמוד הבית',
        r'Profile Settings': 'הגדרות פרופיל',
        r'\bCredits\b': 'קרדיטים',
        
        # Process and actions (תהליכים ופעולות)
        r'\bSegmenter\b': 'מפלח',
        r'\bRecognizer\b': 'מזהה',
        r'\bExport\b': 'ייצוא',
        r'\bImport\b': 'ייבוא',
        r'\bUpload\b': 'העלאה',
        r'\bDownload\b': 'הורדה',
        r'\bSearch\b': 'חיפוש',
        r'\bFilter\b': 'סינון',
        r'\bSort\b': 'מיון',
        r'Start importing': 'התחל ייבוא',
        r'METS Import': 'ייבוא METS',
        r'Remove filter': 'הסר מסנן',
        r'Edit last updated Element': 'ערוך אלמנט מעודכן אחרון',
        
        # Status and states (סטטוסים ומצבים)
        r'\bActive\b': 'פעיל',
        r'\bDraft\b': 'טיוטה',
        r'\bPublished\b': 'פורסם',
        r'\bComplete\b': 'הושלם',
        r'\bError\b': 'שגיאה',
        r'\bWarning\b': 'אזהרה',
        r'\bSuccess\b': 'הצלחה',
        r'\bProcessing\b': 'מעבד',
        r'\bQueued\b': 'ממתין בתור',
        r'\bStarted\b': 'הוחל',
        r'\bStopped\b': 'הופסק',
        r'\bCanceled\b': 'בוטל',
        r'\bCancelled\b': 'בוטל',
        'Canceled': 'בוטל',
        'Cancelled': 'בוטל',
        r'\bCompressing\b': 'דוחס',
        'Compressing': 'דוחס',
        r'\bCrashed\b': 'קרס',
        'Crashed': 'קרס',
        r'\bCompare\b': 'השווה',
        'Compare': 'השווה',
        r'\bBaselines\b': 'קווי בסיס',
        'Baselines': 'קווי בסיס',
        r'\baccuracy\b': 'דיוק',
        'accuracy': 'דיוק',
        # System and maintenance (מערכת ותחזוקה)
        r'Check for available system updates': 'בדוק עדכוני מערכת זמינים',
        r'Create full database backup': 'צור גיבוי מלא של בסיס הנתונים',
        r'Auto Backup': 'גיבוי אוטומטי',
        r'autoBackup': 'גיבוי אוטומטי',
        r'realTimeUpdates': 'עדכונים בזמן אמת',
        r'Automatically backup before dangerous operations': 'גבה אוטומטית לפני פעולות מסוכנות',
        
        # Form elements and user input (אלמנטי טפסים וקלט משתמש)
        r'\bRequired\b': 'נדרש',
        r'\bOptional\b': 'אופציונלי',
        r'\bLoading\b': 'טוען',
        r'Please wait': 'אנא המתן',
        r'Region types': 'סוגי אזורים',
        r'Required field': 'שדה חובה',
        r'Invalid format': 'פורמט לא תקין',
        r'Field is required': 'השדה הוא חובה',
        r'Please enter a valid': 'אנא הזן ערך תקין',
        r'This field cannot be empty': 'שדה זה לא יכול להיות ריק',
        # Search and preview (חיפוש ותצוגה מקדימה)
        r'Image preview is not available for this search result': 'תצוגה מקדימה של תמונה אינה זמינה לתוצאת חיפוש זו',
        r'Go to document part editing page': 'עבור לעמוד עריכת חלק המסמך',
        
        # Time and updates (זמן ועדכונים)
        r'Last update on': 'עדכון אחרון ב',
        
        # Links and external (קישורים וחיצוניים)
        r'\bWiki\b': 'ויקי',
        r'Users mailing list': 'רשימת תפוצה למשתמשים',
        r'\bHelp\b': 'עזרה',
        r'\bAbout\b': 'אודות',
        r'\bContact\b': 'צור קשר',
        r'\bSettings\b': 'הגדרות',
        
        # UI elements and interactions (אלמנטי ממשק ואינטראקציות)
        r'btn help open': 'כפתור עזרה פתוח',
        r'hiddenSearchTrLevelInput': 'קלט רמת חיפוש מוסתר',
        
        # Common labels and descriptions (תוויות נפוצות)
        r'\bTranscription\b': 'תמלול',
        r'\beScriptorium\b': 'eScriptorium',
        r'Generic placeholder image': 'תמונת מציין מקום כללית',
        r'Flower Monitoring Dashboard': 'לוח בקרת ניטור Flower',
        
        # Tooltips and help text (טיפים וטקסט עזרה)
        r'You don\'t have permission': 'אין לך הרשאה',
        r'You don\'t': 'אין לך',
        r'Into group': 'לקבוצה',
        
        # Logo descriptions (תיאורי לוגואים) 
        r'EPHE logo': 'לוגו EPHE',
        r'Scripta PSL logo': 'לוגו Scripta PSL',
        r'Resilience logo': 'לוגו Resilience',
        r'ERC logo': 'לוגו ERC',
        r'Lectaurep logo': 'לוגו Lectaurep',
        r'PSL logo': 'לוגו PSL',
        r'European commission logo': 'לוגו הנציבות האירופית',
        r'PIA logo': 'לוגו PIA',
        r'MELLON logo': 'לוגו MELLON',
        r'MCC logo': 'לוגו MCC',
        r'DIM Region ile de france logo': 'לוגו DIM אזור איל דה פראנס',
        r'Teklia logo': 'לוגו Teklia',
        r'Inria logo': 'לוגו Inria',
        r'AOROC logo': 'לוגו AOROC',
        r'Almanach logo': 'לוגו Almanach',
        # Status messages (הודעות מצב)
        r'Task failed': 'המשימה נכשלה',
        r'Task status': 'מצב המשימה',
        r'Task completed': 'המשימה הושלמה',
        
        # Validation messages (הודעות אימות) - הסירו כפילויות
        # הערה: Required field, Invalid format וכו' כבר קיימים למעלה
        
        # Data grid headers (כותרות טבלת נתונים)
        r'Actions': 'פעולות',
        r'Created': 'נוצר',
        r'Modified': 'עודכן',
        r'Owner': 'בעלים',
        r'Status': 'מצב',
        r'Type': 'סוג',
        r'Size': 'גודל',
        r'Format': 'פורמט',
        r'Version': 'גרסה',
        r'Last modified': 'עודכן לאחרונה',
        
        # Time and date formats (פורמטים של תאריך ושעה)
        r'Today': 'היום',
        r'Yesterday': 'אתמול',
        r'Last week': 'השבוע שעבר',
        r'Last month': 'החודש שעבר',
        r'Last year': 'השנה שעברה',
        r'Never': 'אף פעם',
        # Permission and access control (בקרת הרשאות וגישה)  
        r'Access denied': 'הגישה נדחתה',
        r'Permission required': 'נדרשת הרשאה',
        r'Not authorized': 'לא מורשה',
        r'Login required': 'נדרש התחברות',
        r'Admin only': 'למנהלים בלבד',
        r'Public': 'ציבורי',
        r'Private': 'פרטי',
        r'Shared': 'משותף',
        r'Read only': 'קריאה בלבד',
        r'Read/Write': 'קריאה/כתיבה',
        
        # System notifications (התראות מערכת)
        r'System maintenance': 'תחזוקת מערכת',
        r'Service unavailable': 'השירות לא זמין',
        r'Connection lost': 'החיבור אבד',
        r'Reconnecting': 'מתחבר מחדש',
        r'Server error': 'שגיאת שרת',
        r'Network error': 'שגיאת רשת',
        r'Auto Backup': 'גיבוי אוטומטי',
        r'Automatically backup before dangerous operations': 'בצע גיבוי אוטומטי לפני פעולות מסוכנות',
        r'Remove filter': 'הסר מסנן',
        r'Image preview is not available for this search result': 'תצוגה מקדימה של תמונה אינה זמינה עבור תוצאת חיפוש זו',
        r'Go to document part editing page': 'עבור לעמוד עריכת חלק המסמך',
        r'Back to homepage': 'חזרה לעמוד הבית',
        r'Start importing': 'התחל בייבוא',
        r'METS Import': 'ייבוא METS',
        r'Last update on': 'עודכן לאחרונה ב',
        r'Profile Settings': 'הגדרות פרופיל',
        
        # Button labels (תוויות כפתורים)
        r'\bClose\b': 'סגור',
        r'\bCancel\b': 'בטל',
        r'\bConfirm\b': 'אשר',
        r'Sign In': 'התחבר',
        
        # Navigation links (קישורי ניווט)
        r'Segmenter': 'מפלח',
        r'Recognizer': 'מזהה',
        r'Wiki': 'ויקי',
        r'Users mailing list': 'רשימת תפוצה למשתמשים',
        
        # Forms and labels
        r'Email address': 'כתובת אימייל',
        r'Reset my password': 'אפס את הסיסמה שלי',
        r'Change your password': 'שנה את הסיסמה שלך',
        r'Forgotten your password\? Enter your email address below, and we\'ll email instructions for setting a new one\.':
            'שכחת את הסיסמה? הזן את כתובת האימייל שלך למטה, ואנחנו נשלח הוראות לקביעת סיסמה חדשה.',
        
        # Navigation
        r'First page': 'עמוד ראשון',
        r'Last page': 'עמוד אחרון',
        r'\bPrevious\b': 'קודם',
        r'\bNext\b': 'הבא',
        r'Toggle navigation': 'החלף ניווט',
        
        # Contributors page 
        r'Core Project Team': 'צוות הפרויקט הליבה',
        r'Steering Committee': 'ועד ההיגוי',
        r'Former Committee Members': 'חברי ועד לשעבר',
        
        # BiblIA specific
        r'BiblIA Dataset Project': 'פרויקט מאגר BiblIA',
        r'Hebrew OCR & HTR Research Initiative': 'יוזמת המחקר לזיהוי תווים עבריים',
        
        # Additional system strings (מחרוזות מערכת נוספות)
        r'Language Support for OCR Models': 'תמיכה בשפות למודלי זיהוי תווים',
        r'Contact message': 'הודעת קשר',
        r'Contact messages': 'הודעות קשר',
        r'Document imports': 'ייבוא מסמכים',  # למקרה שיופיע בעתיד
        r'System Maintenance Console': 'קונסולת תחזוקת מערכת',
        r'BiblIA Project Team': 'צוות פרויקט BiblIA',
        r'The BiblIA Dataset project focuses on advancing Hebrew OCR and HTR technology': 'פרויקט מאגר BiblIA מתמקד בקידום טכנולוגיית זיהוי תווים עבריים',
        r'through collaborative research and open-source development': 'באמצעות מחקר שיתופי ופיתוח קוד פתוח',

        # New UI strings discovered by extraction script (מחרוזות ממשק חדשות שנתגלו בסקריפט חילוץ)
        # Project management (ניהול פרויקטים)
        r'\bCreate Project\b': 'צור פרויקט',
        r'\bDelete Project\b': 'מחק פרויקט', 
        r'\bEdit Project\b': 'ערוך פרויקט',
        r'\bCreate New\b': 'צור חדש',
        r'\bManage\b': 'נהל',
        r'\bShare\b': 'שתף',
        r'\bPublish\b': 'פרסם',
        r'\bUnpublished\b': 'לא פורסם',
        
        # File operations (פעולות קבצים)
        r'\bFiles\b': 'קבצים',
        r'\bUpload file\b': 'העלה קובץ',
        r'\bDownload\b': 'הורד',
        r'Upload New': 'העלה חדש',
        r'Select Existing': 'בחר קיים',
        r'File Format': 'פורמט קובץ',
        r'Upload CSV file': 'העלה קובץ CSV',
        
        # Search and filtering (חיפוש וסינון)
        r'Search in projects': 'חפש בפרויקטים',
        r'Search in all your projects': 'חפש בכל הפרויקטים שלך',
        r'Filter by script': 'סנן לפי סקריפט',
        r'Find and Replace': 'מצא והחלף',
        r'Find and replace in projects': 'מצא והחלף בפרויקטים',
        r'Search text in projects': 'חפש טקסט בפרויקטים',
        r'Search Document': 'חפש מסמך',
        r'Search Project': 'חפש פרויקט',
        r'Replace all': 'החלף הכל',
        
        # Document operations (פעולות מסמכים)
        r'My Documents': 'המסמכים שלי',
        r'Create Document': 'צור מסמך',
        r'Update a Document': 'עדכן מסמך',
        r'Share this Document': 'שתף מסמך זה',
        r'Migrate': 'העבר',
        r'Migrate to another project': 'העבר לפרויקט אחר',
        
        # Model management (ניהול מודלים)
        r'My Models': 'המודלים שלי',
        r'New model': 'מודל חדש',
        r'Upload a model': 'העלה מודל',
        r'Share model': 'שתף מודל',
        r'Train Model': 'אמן מודל',
        r'Model name': 'שם מודל',
        r'Model script': 'סקריפט מודל',
        
        # Training and processing (אימון ועיבוד)
        r'\bTrain\b': 'אמן',
        r'\bSegment\b': 'פלח',
        r'\bTranscribe\b': 'תמלל',
        r'\bRecognition\b': 'זיהוי',
        r'\bSegmentation\b': 'פילוח',
        r'Train Recognizer Model': 'אמן מודל זיהוי',
        r'Train Segmenter Model': 'אמן מודל פילוח',
        r'Transcribed document parts': 'חלקי מסמך מתומללים',
        
        # Status and workflow (סטטוס ותהליך עבודה)
        r'\bQueued\b': 'ממתין בתור',
        r'\bRunning\b': 'רץ',
        r'\bFinished\b': 'הסתיים',
        r'\bInitiated\b': 'הוחל',
        r'Not initiated': 'לא הוחל',
        r'In Progress': 'בתהליך',
        r'Task state': 'מצב משימה',
        r'Training Status': 'מצב אימון',
        
        # User interface elements (אלמנטי ממשק משתמש)
        r'\bLoad More\b': 'טען עוד',
        r'\bSelect all\b': 'בחר הכל',
        r'Select None': 'בטל בחירה',
        r'Unselect all': 'בטל בחירת הכל',
        r'\bView All\b': 'הצג הכל',
        r'\bPreview\b': 'תצוגה מקדימה',
        r'Toggle navigation': 'החלף ניווט',
        
        # Teams and sharing (צוותים ושיתוף)
        r'Share this Project': 'שתף פרויקט זה',
        r'Share with': 'שתף עם',
        r'Shared with': 'משותף עם',
        r'Stop sharing': 'הפסק שיתוף',
        r'Invite Users': 'הזמן משתמשים',
        r'Send invitation': 'שלח הזמנה',
        r'Send Invitations': 'שלח הזמנות',
        
        # Time and dates (זמן ותאריכים)
        r'Last modified on': 'עודכן לאחרונה ב',
        r'Last update on': 'עדכון אחרון ב',
        r'Last day': 'יום אחרון',
        r'Last week': 'שבוע אחרון',
        r'Started at': 'הוחל ב',
        
        # Permissions and access (הרשאות וגישה)
        r'Transfer ownership': 'העבר בעלות',
        r'Remove from list': 'הסר מהרשימה',
        r'Remove user from group': 'הסר משתמש מקבוצה',
        
        # Navigation and pagination (ניווט וחלוקה לעמודים)
        r'First page': 'עמוד ראשון',
        r'Last page': 'עמוד אחרון',
        r'Next line': 'שורה הבאה',
        r'Previous line': 'שורה קודמת',
        
        # Data and statistics (נתונים וסטטיסטיקה)
        r'Image count': 'מספר תמונות',
        r'Total Characters': 'סך תווים',
        r'Total Images': 'סך תמונות',
        r'Total Lines': 'סך שורות',
        r'Total number of characters': 'מספר כולל של תווים',
        r'Total number of lines': 'מספר כולל של שורות',
        r'Total number of words': 'מספר כולל של מילים',
        
        # Interface modes and views (מצבי ממשק ותצוגות)
        r'Grid view': 'תצוגת רשת',
        r'List view': 'תצוגת רשימה',
        r'Toggle versions': 'החלף גרסאות',
        r'View Element Details': 'הצג פרטי אלמנט',
        
        # System messages (הודעות מערכת)
        r'Please Sign In': 'אנא התחבר',
        r'Register to eScriptorium': 'הירשם ל-eScriptorium',
        r'Reset my password': 'אפס את הסיסמה שלי',
        r'Reset your password': 'אפס את הסיסמה',
        
        # Help and information (עזרה ומידע)
        r'\bInformation\b': 'מידע',
        r'\bTutorial\b': 'מדריך',
        r'\bResources\b': 'משאבים',
        r'Legal mentions': 'אזכורים משפטיים',
        
        # Technical terms (מונחים טכניים)
        r'Text Direction': 'כיוון טקסט',
        r'Right to left': 'מימין לשמאל',
        r'Left to right': 'משמאל לימין',
        r'Line types': 'סוגי שורות',
        r'Region types': 'סוגי אזורים',
        
        # Additional UI strings - Entry and Input
        r'"Enter METS file URI"': '"הזן URI קובץ METS"',
        r'"Enter project name"': '"הזן שם פרויקט"',
        r'"Enter select range"': '"הזן טווח בחירה"',
        r'"Enter URL"': '"הזן כתובת אתר"',
        r'"Enter username of registered user"': '"הזן שם משתמש רשום"',
        
        # Import and export
        r'"Import images"': '"ייבא תמונות"',
        r'"Import Elements"': '"ייבא אלמנטים"',
        r'"From a remote METS file"': '"מקובץ METS מרוחק"',
        r'"Or from a local archive"': '"או מארכיון מקומי"',
        r'"Import images from a PDF document"': '"ייבא תמונות ממסמך PDF"',
        r'"Import images from IIIF"': '"ייבא תמונות מ-IIIF"',
        
        # Image and annotation
        r'"Image Annotation"': '"הערת תמונה"',
        r'"Image Annotations"': '"הערות תמונה"',
        r'"Image preview"': '"תצוגה מקדימה של תמונה"',
        
        # Text and search
        r'"Text to search"': '"טקסט לחיפוש"',
        r'"Search element name"': '"חפש שם אלמנט"',
        r'"Search to filter images by element name"': '"חפש לסינון תמונות לפי שם אלמנט"',
        r'"Find and replace text in projects"': '"מצא והחלף טקסט בפרויקטים"',
        
        # Actions and buttons
        r'"Move to bottom"': '"העבר לתחתית"',
        r'"Move to top"': '"העבר לחלק העליון"',
        r'"Join selected lines"': '"חבר שורות נבחרות"',
        r'"Reverse selected lines"': '"הפוך שורות נבחרות"',
        r'"Rotate Clockwise"': '"סובב עם כיוון השעון"',
        r'"Rotate Counterclockwise"': '"סובב נגד כיוון השעון"',
        r'"Reset zoom"': '"איפוס זום"',
        r'"Zoom in"': '"התקרב"',
        r'"Zoom out"': '"התרחק"',
        
        # Interface elements
        r'"Larger font"': '"גופן גדול יותר"',
        r'"Smaller font"': '"גופן קטן יותר"',
        r'"Toggle history"': '"הפעל/כבה היסטוריה"',
        r'"Toggle region labels"': '"הפעל/כבה תוויות אזור"',
        r'"Toggle transcription comparison"': '"הפעל/כבה השוואת תעתיקים"',
        
        # Status and workflow
        r'"Trained status"': '"סטטוס אימון"',
        r'"Is currently training"': '"כרגע מתאמן"',
        r'"Is done training"': '"האימון הושלם"',
        r'"Last task started"': '"המשימה האחרונה התחילה"',
        r'"Last Edited"': '"נערך לאחרונה"',
        r'"Last Update"': '"עדכון אחרון"',
        
        # Errors and warnings
        r'"Error calculating masks"': '"שגיאה בחישוב מסכות"',
        r'"Failed to fetch additional images"': '"נכשל בטעינת תמונות נוספות"',
        r'"Line not present in segmentation"': '"השורה לא קיימת בפילוח"',
        r'"Mask calculation queued"': '"חישוב מסכה ממתין בתור"',
        r'"Successfully calculated masks"': '"חושבו מסכות בהצלחה"',
        r'"There are no images to display"': '"אין תמונות להצגה"',
        
        # Navigation and pagination
        r'"Your Recent Images"': '"התמונות האחרונות שלך"',
        r'"No Components"': '"אין רכיבים"',
        r'"Load this state"': '"טען מצב זה"',
        
        # File operations
        r'"Gathering data"': '"אוסף נתונים"',
        r'"Importing"': '"מייבא"',
        r'Replacement preview': 'תצוגה מקדימה של החלפה',
        r'Filter results by this document': 'סנן תוצאות לפי המסמך הזה',
        r'Filter results by this part': 'סנן תוצאות לפי החלק הזה',
        
        # Reading directions
        r'"Horizontal Left to Right"': '"אופקי משמאל לימין"',
        r'"Horizontal Right to Left"': '"אופקי מימין לשמאל"',
        r'"Vertical Left to Right"': '"אנכי משמאל לימין"',
        r'"Vertical Right to Left"': '"אנכי מימין לשמאל"',
        
        # Workflow options
        r'"Line length threshold"': '"סף אורך שורה"',
        r'"Max offset"': '"היסט מרבי"',
        r'"Read Direction"': '"כיוון קריאה"',
        r'"Textual witness"': '"עד טקסטואלי"',
        r'"Layer Name"': '"שם שכבה"',
        
    # ------------------------------------------------------------------
    # Batch 1 - Newly mapped UI phrases (safe, user‑facing)
    # NOTE: We intentionally avoid translating Vue template directives
    # like "item in items", "component in components" to prevent
    # breaking v-for attributes. Only visible text strings included.
    # ------------------------------------------------------------------
    r'\bAccount Expired\b': 'תוקף החשבון פג',
    r'\bAdd group\b': 'הוסף קבוצה',
    r'\bAdd Group or User\b': 'הוסף קבוצה או משתמש',
    r'\bAdd invitation\b': 'הוסף הזמנה',
    r'\bAdd New\b': 'הוסף חדש',
    r'\bAdd user\b': 'הוסף משתמש',
    r'\bAdvanced Settings\b': 'הגדרות מתקדמות',
    r'\bAll levels\b': 'כל הרמות',
    r'\bAll time\b': 'כל הזמנים',
    r'\bAllowed Values\b': 'ערכים מותרים',
    r'\bAnnotations components\b': 'רכיבי הערות',
    r'\bAPI key\b': 'מפתח API',
    r'\bapply filter\b': 'החל מסנן',
    r'\bAssign tags\b': 'הקצה תגיות',
    r'\bAverage transcription confidence\b': 'ממוצע מהימנות התמלול',
    r'\bBack to document list\b': 'חזרה לרשימת המסמכים',
    r'\bBack to profile\b': 'חזרה לפרופיל',
    r'\bBackground Color\b': 'צבע רקע',
    r'\bBeam size\b': 'גודל Beam',
    r'\bBulk Invite\b': 'הזמנה מרוכזת',
    r'\bButton Text\b': 'טקסט כפתור',
    r'\bBy using the cut mode\b': 'באמצעות מצב החיתוך',
    r'\bcalculate masks\b': 'חשב מסכות',
    r'\bCalculated from your images and models\b': 'מחושב מהתמונות והמודלים שלך',
    r'\bCancel Task\b': 'בטל משימה',
    r'\bCancel tasks\b': 'בטל משימות',
    r'\bCancel training\b': 'בטל אימון',
    r'\bCancel Upload In Progress\b': 'בטל העלאה בתהליך',
    r'\bcannot undo this action\b': 'לא ניתן לבטל פעולה זו',
    r'\bChange my password\b': 'שנה את הסיסמה שלי',
    r'\bChange Panel\b': 'החלף פאנל',
    r'\bChange Password\b': 'שנה סיסמה',
    r'\bChange the visible transcription layer\b': 'החלף את שכבת התמלול הנראית',
    r'\bChange type\b': 'שנה סוג',
    r'\bClear All\b': 'נקה הכל',
    r'\bClear filter\b': 'נקה מסנן',
    r'\bClear search filter\b': 'נקה מסנן חיפוש',
    r'\bConfidence range scale\b': 'סולם טווח מהימנות',
    r'\bcontributors history\b': 'היסטוריית תורמים',
    r'\bContributors to Source Code\b': 'תורמי קוד המקור',
    r'\bCPU cost\b': 'עלות CPU',
    r'\bCPU minutes\b': 'דקות CPU',
    r'\bCPU usage over the last week\b': 'שימוש ב-CPU במהלך השבוע האחרון',
    r'\bCPU usage\b': 'שימוש ב-CPU',
    r'\bCreate a new Document\b': 'צור מסמך חדש',
    r'\bCreate a new Project\b': 'צור פרויקט חדש',
    r'\bCreate new Document\b': 'צור מסמך חדש',
    r'\bCreate new Project\b': 'צור פרויקט חדש',
    r'\bCreate a tag\b': 'צור תגית',
    r'\bCreated on\b': 'נוצר בתאריך',
    r'\bCurrent use of document tags\b': 'שימוש נוכחי בתגיות מסמך',
    r'\bCurrent use of lines type\b': 'שימוש נוכחי בסוגי שורות',
    r'\bCurrent use of part tags\b': 'שימוש נוכחי בתגיות חלקים',
    r'\bCurrent use of regions type\b': 'שימוש נוכחי בסוגי אזורים',
    r'\bcustom logo\b': 'לוגו מותאם',
    r'\bData metrics\b': 'מדדי נתונים',
    r'\bDate Created\b': 'תאריך יצירה',
    r'\bDefault Segmentation Model\b': 'מודל פילוח ברירת מחדל',
    r'\bDefault Transcription Level\b': 'רמת תמלול ברירת מחדל',
    r'\bDelete Component\b': 'מחק רכיב',
    r'\bDelete Document\b': 'מחק מסמך',
    r'\bDelete model\b': 'מחק מודל',
    r'\bDelete right\b': 'מחק הרשאה',
    r'\bDelete transcription\b': 'מחק תמלול',
    r'\bDisk storage\b': 'אחסון דיסק',
    r'\bDisk usage\b': 'ניצול דיסק',
    r'\bDjango Framework\b': 'מסגרת Django',
    r'\bDocument images\b': 'תמונות מסמך',
    r'\bDocument Models\b': 'מודלי מסמך',
    r'\bDocument name\b': 'שם מסמך',
    r'\bDocument Ontology\b': 'אונטולוגיית מסמך',
    r'\bDocument report\b': 'דוח מסמך',
    r'\bDocument Statistics\b': 'סטטיסטיקת מסמך',
    r'\bDocument Tags\b': 'תגיות מסמך',
    r'\bDone at\b': 'הושלם ב',
    r'\bDouble click\b': 'לחיצה כפולה',
    r'\bDownload full size image\b': 'הורד תמונה בגודל מלא',
    r'\bDownload model file\b': 'הורד קובץ מודל',
    r'\bDrag and drop files here\b': 'גרור ושחרר קבצים כאן',
    r'\bEdited on\b': 'נערך בתאריך',
    r'\bElement Details\b': 'פרטי אלמנט',
    r'\bEnter layer name\b': 'הזן שם שכבה',
    r'\bEnter METS file URI\b': 'הזן URI של קובץ METS',
    r'\bEnter project name\b': 'הזן שם פרויקט',
    r'\bEnter select range\b': 'הזן טווח בחירה',
    r'\bEnter URL\b': 'הזן כתובת URL',
    r'\bEnter username of registered user\b': 'הזן שם משתמש רשום',
    r'\bError calculating masks\b': 'שגיאה בחישוב מסכות',
    r'\beScriptorium Blog\b': 'בלוג eScriptorium',
    r'\beScriptorium open source code\b': 'קוד פתוח של eScriptorium',
    r'\bexpand task monitoring and usage menu\b': 'הרחב תפריט ניטור משימות ושימוש',
    r'\bexpand user profile menu\b': 'הרחב תפריט פרופיל משתמש',
    r'\bFailed to fetch additional images\b': 'נכשל בקבלת תמונות נוספות',
    r'\bFilter Tags\b': 'סינון תגיות',
    r'\bFind and replace text in projects\b': 'מצא והחלף טקסט בפרויקטים',
    r'\bFind tag\b': 'מצא תגית',
    r'\bFrom a remote METS file\b': 'מקובץ METS מרוחק',
    r'\bFull name or identifier\b': 'שם מלא או מזהה',
    r'\bGathering data\b': 'אוסף נתונים',
    r'\bglobal search\b': 'חיפוש גלובלי',
    r'\bGPU cost\b': 'עלות GPU',
    r'\bGPU usage over the last week\b': 'שימוש ב-GPU במהלך השבוע האחרון',
    r'\bGPU usage\b': 'שימוש ב-GPU',
    r'\bGroup identifier\b': 'מזהה קבוצה',
    r'\bGroup name\b': 'שם קבוצה',
    r'\bHorizontal Left to Right\b': 'אופקי משמאל לימין',
    r'\bHorizontal Right to Left\b': 'אופקי מימין לשמאל',
    r'\bIIIF Manifest URI\b': 'URI של מניפסט IIIF',
    r'\bImage Annotation\b': 'הערת תמונה',
    r'\bImage Annotations\b': 'הערות תמונה',
    r'\bImage preview\b': 'תצוגה מקדימה של תמונה',
    r'\bImport an ontology in this document\b': 'ייבא אונטולוגיה למסמך זה',
    r'\bImport Elements\b': 'ייבוא אלמנטים',
    r'\bImport images from a PDF document\b': 'ייבוא תמונות ממסמך PDF',
    r'\bImport images from IIIF\b': 'ייבוא תמונות מ-IIIF',
    r'\bImport images\b': 'ייבוא תמונות',
    r'\bin document\b': 'במסמך',
    r'\binclude images\b': 'כלול תמונות',
    r'\bInria Paris\b': 'Inria פריז',
    r'\bInvite mode\b': 'מצב הזמנה',
    r'\bIs currently training\b': 'באימון כרגע',
    r'\bIs done training\b': 'האימון הושלם',
    r'\bis inviting you to join\b': 'מזמין אותך להצטרף',
    r'\bJoin selected lines\b': 'חבר שורות נבחרות',
    r'\bKraken OCR Engine\b': 'מנוע Kraken OCR',
    r'\bLarger font\b': 'גופן גדול יותר',
    r'\bLast Edited\b': 'נערך לאחרונה',
    r'\bLast task started\b': 'המשימה האחרונה התחילה',
    r'\bLast Update\b': 'עדכון אחרון',
    r'\bLayer Name\b': 'שם שכבה',
    r'\bLeft click\b': 'לחיצה שמאלית',
    r'\bLine length threshold\b': 'סף אורך שורה',
    r'\bLine not present in segmentation\b': 'שורה לא קיימת בפילוח',
    r'\bLine Position\b': 'מיקום שורה',
    r'\bLine transcription\b': 'תמלול שורה',
    r'\bLink to Project Guidelines\b': 'קישור להנחיות הפרויקט',
    r'\bLoad this state\b': 'טען מצב זה',
    r'\blog in\b': 'התחבר',
    r'\bManage Ontology\b': 'נהל אונטולוגיה',
    r'\bManage tags\b': 'נהל תגיות',
    r'\bManage Transcriptions\b': 'נהל תמלולים',
    r'\bMarker Type\b': 'סוג סמן',
    r'\bMask calculation queued\b': 'חישוב מסכה בתור',
    r'\bMax offset\b': 'היסט מרבי',
    r'\bModel role\b': 'תפקיד מודל',
    r'\bMove to bottom\b': 'העבר לתחתית',
    r'\bMove to top\b': 'העבר לראש',
    r'\bMy Projects\b': 'הפרויקטים שלי',
    r'\bNo Components\b': 'אין רכיבים',
    r'\bNo type assigned\b': 'לא הוקצה סוג',
    r'\bOr from a local archive\b': 'או מארכיון מקומי',
    r'\bOr select an existing one\b': 'או בחר אחד קיים',
    r'\bOther Contributions\b': 'תרומות נוספות',
    r'\bOther Contributors\b': 'תורמים נוספים',
    r'\bParent from which the model was trained\b': 'הורה שממנו אומן המודל',
    r'\bPart types\b': 'סוגי חלקים',
    r'\bPowered by\b': 'מופעל על ידי',
    r'\bProject activity\b': 'פעילות פרויקט',
    r'\bProject reports\b': 'דוחות פרויקט',
    r'\bProject Tags\b': 'תגיות פרויקט',
    r'\bprojects list\b': 'רשימת פרויקטים',
    r'\bQuick Actions\b': 'פעולות מהירות',
    r'\branges separated by dashes\b': 'טווחים מופרדים במקפים',
    r'\bRead Direction\b': 'כיוון קריאה',
    
    # Help texts for form fields
    r'The read direction describes the overall order of elements/pages in the document; NOT the order of words in a line, which will be automatically determined by the script\.': 
        'כיוון הקריאה מתאר את הסדר הכולל של אלמנטים/עמודים במסמך; לא את סדר המילים בשורה, שייקבע אוטומטית על ידי הכתב.',
    r'The position of the line relative to the polygon\.':
        'מיקום הקו ביחס למצולע.',
    
    r'\bRecipient type\b': 'סוג נמען',
    r'\bRedraw Masks\b': 'חשב מחדש מסכות',
    r'\bReload vocabulary\b': 'טען מחדש אוצר מילים',
    r'\bRemote METS URI\b': 'URI של METS מרוחק',
    r'\bReorder line automatically\b': 'סדר מחדש שורה אוטומטית',
    r'\bReset zoom\b': 'אפס זום',
    r'\bReverse selected lines\b': 'הפוך שורות נבחרות',
    r'\bRight click\b': 'לחיצה ימנית',
    r'\bRotate Clockwise\b': 'סובב עם כיוון השעון',
    r'\bRotate Counterclockwise\b': 'סובב נגד כיוון השעון',
    r'\bSearch element name\b': 'חפש שם אלמנט',
    r'\bSearch score\b': 'ציון חיפוש',
    r'\bSearch to filter images by element name\b': 'חפש כדי לסנן תמונות לפי שם אלמנט',
    r'\bSegmentation Panel\b': 'פאנל פילוח',
    r'\bSelect a model\b': 'בחר מודל',
    r'\bSelect a transcription\b': 'בחר תמלול',
    r'\bselect color\b': 'בחר צבע',
    r'\bService hosted and maintained by\b': 'השירות מאוחסן ומתוחזק על ידי',
    r'\bService originally developed by\b': 'השירות פותח במקור על ידי',
    r'\bshift and drag\b': 'Shift וגרירה',
    r'\bSite administration\b': 'ניהול האתר',
    r'\bSmaller font\b': 'גופן קטן יותר',
    r'\bSource Panel\b': 'פאנל מקור',
    r'\bSuccessfully calculated masks\b': 'מסכות חושבו בהצלחה',
    r'\bswitch to light mode\b': 'העבר למצב בהיר',
    r'\bTask Monitoring\b': 'ניטור משימות',
    r'\bTask report\b': 'דוח משימה',
    r'\bTask reports\b': 'דוחות משימה',
    r'\bTask Usage\b': 'שימוש במשימות',
    r'\bTasks monitoring\b': 'ניטור משימות',
    r'\btext annotation\b': 'הערת טקסט',
    r'\bText Annotations\b': 'הערות טקסט',
    r'\bText Color\b': 'צבע טקסט',
    r'\bText Panel\b': 'פאנל טקסט',
    r'\bText to search\b': 'טקסט לחיפוש',
    r'\bTextual witness\b': 'עד טקסטואלי',
    r'\bThe load state button\b': 'כפתור טעינת המצב',
    r'\bThe red trash\b': 'האייקון האדום של האשפה',
    r'\bThe yellow trash button\b': 'כפתור האשפה הצהוב',
    r'\bThere are no images to display\b': 'אין תמונות להצגה',
    r'\bToggle history\b': 'הפעל/כבה היסטוריה',
    r'\bToggle region labels\b': 'הפעל/כבה תוויות אזור',
    r'\bToggle transcription comparison\b': 'הפעל/כבה השוואת תמלולים',
    r'\bTotal number of document parts\b': 'מספר כולל של חלקי מסמך',
    r'\bTotal number of regions\b': 'מספר כולל של אזורים',
    r'\bTrained from\b': 'אומן מתוך',
    r'\bTrained status\b': 'סטטוס אימון',
    r'\bTranscription comparison\b': 'השוואת תמלולים',
    r'\bTranscription history\b': 'היסטוריית תמלול',
    r'\bTranscription management\b': 'ניהול תמלול',
    r'\bTranscription name\b': 'שם תמלול',
    r'\bTranscription Status\b': 'סטטוס תמלול',
    r'\bType to add a tag\b': 'הקלד כדי להוסיף תגית',
    r'\bUnbind model from the document\b': 'נתק מודל מהמסמך',
    r'\bUpdate a Project\b': 'עדכן פרויקט',
    r'\bUpload or select a textual witness\b': 'העלה או בחר עד טקסטואלי',
    r'\bUser full name\b': 'שם מלא של המשתמש',
    r'\bUser ID\b': 'מזהה משתמש',
    r'\bVertical Left to Right\b': 'אנכי משמאל לימין',
    r'\bVertical Right to Left\b': 'אנכי מימין לשמאל',
    r'\bVisual Transcription Panel\b': 'פאנל תמלול חזותי',
    r'\bYou can go through your changes\b': 'ניתן לעבור על השינויים שלך',
    r'\bYour Recent Images\b': 'התמונות האחרונות שלך',
    r'\bZoom in\b': 'התקרב',
    r'\bZoom out\b': 'התרחק',
        
        # ------------------------------------------------------------------
        # Batch 2 - Residual UI strings (post regex classification)
        # NOTE: We exclude Vue structural directives like "item in items" from
        # translation to avoid breaking v-for loops. Only visual labels remain.
        # ------------------------------------------------------------------
        r'\bAdd Panel\b': 'הוסף פאנל',
        r'\bAdd right\b': 'הוסף הרשאה',
        r'\breorder lines\b': 'סדר שורות מחדש',
        r'\bopen menu\b': 'פתח תפריט',
        r'\boverflow toggle\b': 'החלף גלילת יתר',
        r'\bnew control point\b': 'נקודת בקרה חדשה',
        r'\bmodule aligned\b': 'מודול מיושר',
        r'\brow container\b': 'מיכל שורה',
        r'\brow marginless\b': 'שורה ללא שוליים',
        r'\bmodal fade\b': 'חלון קופץ',
        r'\bmodels list\b': 'רשימת מודלים',
        r'\bCourier New\b': 'Courier New',  # Font name left as-is
        r'\ben masse\b': 'במספר רב',
        r'\bAdd tag\b': 'הוסף תגית',
        r'\bAdd points\b': 'הוסף נקודות',
        r'\bAdd panel\b': 'הוסף פאנל',  # case variant safeguard
        
        # ------------------------------------------------------------------
        # Batch 3 - Form labels and field names (תוויות טפסים ושמות שדות)
        # Common form field labels that appear as standalone words
        # ------------------------------------------------------------------
        r'\bName\b': 'שם',
        r'\bTypology\b': 'טיפולוגיה',
        'Typology': 'טיפולוגיה',
        r'\bElement\b': 'אלמנט', 
        'Element': 'אלמנט',
        r'\bComments\b': 'הערות',
        'Comments': 'הערות',
        r'\bMetadata\b': 'מטא-נתונים',
        # Exact form field labels - כדי לתפוס במדויק מlabels
        'Select': 'בחר',
        '>Select<': '>בחר<',
        'Name': 'שם',
        '>Name<': '>שם<',
        'Element': 'אלמנט',
        '>Element<': '>אלמנט<',
        'Typology': 'טיפולוגיה', 
        '>Typology<': '>טיפולוגיה<',
        'Comments': 'הערות',
        '>Comments<': '>הערות<',
        'Metadata': 'מטא-נתונים',
        '>Metadata<': '>מטא-נתונים<',
        
        # Form help text and instructions
        r'If left empty the name will automatically be \{typology\+index number\}': 'אם יישאר ריק השם יהיה אוטומטית {טיפולוגיה+מספר אינדקס}',
        r'If left empty the name will automatically be {typology\+index number}': 'אם יישאר ריק השם יהיה אוטומטית {טיפולוגיה+מספר אינדקס}',
        r'If left empty the name will automatically be \{typology\\\+index number\}': 'אם יישאר ריק השם יהיה אוטומטית {טיפולוגיה+מספר אינדקס}',
        r'If left empty the name will automatically be {typology+index number}': 'אם יישאר ריק השם יהיה אוטומטית {טיפולוגיה+מספר אינדקס}',
        r'If left empty the name will automatically be': 'אם יישאר ריק השם יהיה אוטומטית',
        
        # ------------------------------------------------------------------
        # Batch 4 - Basic UI elements (אלמנטי ממשק בסיסיים)
        # Essential interface elements that users interact with frequently
        # ------------------------------------------------------------------
        r'\bHome\b': 'בית',
        r'\bHelp\b': 'עזרה', 
        r'\bSettings\b': 'הגדרות',
        r'\bProfile\b': 'פרופיל',
        r'\bSave\b': 'שמור',
        r'\bUpload\b': 'העלה',
        r'\bExport\b': 'ייצא',
        r'\bImport\b': 'יבא',
        r'\bSearch\b': 'חיפוש',
        r'\bFilter\b': 'סנן',
        r'\bLoading\b': 'טוען',
        r'\bSuccess\b': 'הצלחה',
        r'\bWarning\b': 'אזהרה',
        r'\bError\b': 'שגיאה',
        r'\bFind\b': 'חפש',
        r'\bView\b': 'הצג',
        r'\bEdit\b': 'ערוך',
        r'\bDelete\b': 'מחק',
        r'\bCancel\b': 'בטל',
        r'\bConfirm\b': 'אשר',
        r'\bSend\b': 'שלח',
        r'\bMove\b': 'העבר',
        r'\bCopy\b': 'העתק',
        r'\bSelect\b': 'בחר',
        r'\bUpdate\b': 'עדכן',
        r'\bRefresh\b': 'רענן',
        r'\bReload\b': 'טען מחדש',
        r'\bOpen\b': 'פתח',
        r'\bClose\b': 'סגור',
        r'\bNext\b': 'הבא',
        r'\bPrevious\b': 'הקודם',
        r'\bFinish\b': 'סיים',
        r'\bContinue\b': 'המשך',
        
        # Language and direction
        r'\bHebrew\b': 'עברית',
        r'\bEnglish\b': 'אנגלית',
        r'\bArabic\b': 'ערבית',
        
        # Common actions and statuses
        r'\bTraining\b': 'אימון',
        r'\bTrained\b': 'מאומן',
        r'\bPending\b': 'ממתין',
        r'\bActive\b': 'פעיל',
        r'\bInactive\b': 'לא פעיל',
        r'\bCompleted\b': 'הושלם',
        r'\bFailed\b': 'נכשל',
        r'\bRunning\b': 'רץ',
        r'\bStopped\b': 'עצור',
        
        # ------------------------------------------------------------------
        # Batch 5 - Interface navigation and structure (ניווט ומבנה ממשק)
        # ------------------------------------------------------------------
        r'\bEmail\b': 'דוא"ל',
        r'\bEnter\b': 'הכנס',
        r'\bEnter layer name\b': 'הכנס שם שכבה',
        r'\bEnter METS file URI\b': 'הכנס URI של קובץ METS',
        r'\bEnter project name\b': 'הכנס שם פרויקט',
        r'\bEnter select range\b': 'הכנס טווח בחירה',
        r'\bEnter URL\b': 'הכנס URL',
        r'\bEnter username of registered user\b': 'הכנס שם משתמש של משתמש רשום',
        r'\bErrors\b': 'שגיאות',
        r'\bEscape\b': 'מקש Escape',
        r'\beScriptorium\b': 'eScriptorium',
        r'\beScriptorium Blog\b': 'בלוג eScriptorium',
        r'\beScriptorium open source code\b': 'קוד מקור פתוח של eScriptorium',
        r'\bHello\b': 'שלום',
        r'\bHomepage\b': 'עמוד בית',
        r'\bHistory\b': 'היסטוריה',
        r'\bIcon\b': 'סמל',
        r'\bImage\b': 'תמונה',
        r'\bImage preview\b': 'תצוגה מקדימה של תמונה',
        r'\bImages\b': 'תמונות',
        r'\bImporting\b': 'מייבא',
        r'\bInvitations\b': 'הזמנות',
        r'\bInvite\b': 'הזמן',
        r'\bInvite mode\b': 'מצב הזמנה',
        r'\bLanguage\b': 'שפה',
        r'\bLogin\b': 'התחברות',
        r'\bLog in\b': 'התחבר',
        r'\bLogout\b': 'התנתקות',
        r'\bMenu\b': 'תפריט',
        r'\bModels\b': 'מודלים',
        r'\bNote\b': 'הערה',
        r'\bPassword\b': 'סיסמה',
        r'\bPost\b': 'פרסם',
        r'\bProfile\b': 'פרופיל',
        r'\bProgress\b': 'התקדמות',
        r'\bPublished\b': 'פורסם',
        r'\bQuery\b': 'שאילתה',
        r'\bQuotas\b': 'מכסות',
        r'\bRecipient\b': 'נמען',
        r'\bRecipient type\b': 'סוג נמען',
        r'\bReport\b': 'דוח',
        r'\bReports\b': 'דוחות',
        r'\bResults\b': 'תוצאות',
        r'\bRight\b': 'ימין',
        r'\bRuntime\b': 'זמן ריצה',
        r'\bScore\b': 'ציון',
        r'\bState\b': 'מצב',
        r'\bSignup\b': 'הרשמה',
        r'\bSite administration\b': 'ניהול אתר',
        r'\bStatistics\b': 'סטטיסטיקות',
        r'\bSubmit\b': 'שלח',
        r'\bTable\b': 'טבלה',
        r'\bTask\b': 'משימה',
        r'\bTasks\b': 'משימות',
        r'\bTask Monitoring\b': 'מעקב משימות',
        r'\bTask report\b': 'דוח משימה',
        r'\bTask reports\b': 'דוחות משימות',
        r'\bTask Usage\b': 'שימוש במשימות',
        r'\bTasks monitoring\b': 'מעקב משימות',
        r'\bTeam\b': 'צוות',
        r'\bTeams\b': 'צוותים',
        r'\bTotal\b': 'סה"כ',
        r'\bUser full name\b': 'שם מלא של משתמש',
        r'\bUser ID\b': 'מזהה משתמש',
        r'\bUsers\b': 'משתמשים',
        r'\bUsername\b': 'שם משתמש',
        r'\bValue\b': 'ערך',
        r'\bVertical\b': 'אנכי',
        r'\bVocabulary\b': 'אוצר מילים',
        
        # ------------------------------------------------------------------
        # Batch 6 - Document and project management (ניהול מסמכים ופרויקטים)
        # ------------------------------------------------------------------
        r'\bDocument\b': 'מסמך',
        r'\bDocuments\b': 'מסמכים',
        r'\bProject\b': 'פרויקט',
        r'\bProjects\b': 'פרויקטים',
        r'\bMy Projects\b': 'הפרויקטים שלי',
        r'\bProject activity\b': 'פעילות פרויקט',
        r'\bProject reports\b': 'דוחות פרויקט',
        r'\bProject Tags\b': 'תגיות פרויקט',
        r'\bCreate\b': 'צור',
        r'\bCreate a Project\b': 'צור פרויקט',
        r'\bUpdate a Project\b': 'עדכן פרויקט',
        r'\bShare\b': 'שתף',
        r'\bSharing\b': 'שיתוף',
        r'\bLeave\b': 'עזוב',
        r'\bJoin\b': 'הצטרף',
        r'\bManage\b': 'נהל',
        r'\bManage tags\b': 'נהל תגיות',
        r'\bManage Ontology\b': 'נהל אונטולוגיה',
        r'\bManage Transcriptions\b': 'נהל תמלילים',
        
        # Tags and metadata
        r'\bTag\b': 'תג',
        r'\bTags\b': 'תגים',
        r'\bFind tag\b': 'חפש תג',
        r'\bFilter Tags\b': 'סנן תגים',
        r'\bType to add a tag\b': 'הקלד כדי להוסיף תג',
        r'\bUntagged\b': 'לא מתויג',
        
        # File operations
        r'\bFile\b': 'קובץ',
        r'\bFiles\b': 'קבצים',
        r'\bFilename\b': 'שם קובץ',
        r'\bFrom a remote METS file\b': 'מקובץ METS מרוחק',
        r'\bOr from a local archive\b': 'או מארכיון מקומי',
        r'\bOr select an existing one\b': 'או בחר קיים',
        r'\bFull name or identifier\b': 'שם מלא או מזהה',
        r'\bGathering data\b': 'איסוף נתונים',
        
        # Import/Export operations
        r'\bImport Elements\b': 'יבא אלמנטים',
        r'\bImport images\b': 'יבא תמונות',
        r'\bImport images from a PDF document\b': 'יבא תמונות ממסמך PDF',
        r'\bImport images from IIIF\b': 'יבא תמונות מ-IIIF',
        r'\bImport an ontology in this document\b': 'יבא אונטולוגיה למסמך זה',
        r'\bInclude\b': 'כלול',
        r'\binclude images\b': 'כלול תמונות',
        
        # Status and workflow
        r'\bIs currently training\b': 'כרגע באימון',
        r'\bIs done training\b': 'סיים אימון',
        r'\bis inviting you to join\b': 'מזמין אותך להצטרף',
        r'\bLast Edited\b': 'נערך לאחרונה',
        r'\bLast task started\b': 'המשימה האחרונה התחילה',
        r'\bLast Update\b': 'עדכון אחרון',
        r'\bLeaderboard\b': 'לוח מובילים',
        
        # ------------------------------------------------------------------
        # Batch 7 - Advanced features and technical terms (תכונות מתקדמות ומונחים טכניים)
        # ------------------------------------------------------------------
        
        # Transcription and text processing
        r'\bTranscription\b': 'תמליל',
        r'\bTranscriptions\b': 'תמלילים',
        r'\bTranscription comparison\b': 'השוואת תמלילים',
        r'\bTranscription history\b': 'היסטוריית תמליל',
        r'\bTranscription management\b': 'ניהול תמלילים',
        r'\bTranscription name\b': 'שם תמליל',
        r'\bTranscription Status\b': 'סטטוס תמליל',
        r'\bToggle transcription comparison\b': 'הפעל/כבה השוואת תמלילים',
        r'\bLine transcription\b': 'תמליל שורה',
        r'\bSelect a transcription\b': 'בחר תמליל',
        
        # Segmentation and regions
        r'\bSegmentation\b': 'פילוח',
        r'\bSegmentation Panel\b': 'פאנל פילוח',
        r'\bRegion\b': 'אזור',
        r'\bRegions\b': 'אזורים',
        r'\bToggle region labels\b': 'הפעל/כבה תוויות אזורים',
        r'\bLine not present in segmentation\b': 'שורה לא קיימת בפילוח',
        r'\bTotal number of regions\b': 'מספר כולל של אזורים',
        
        # Lines and text elements
        r'\bLine\b': 'שורה',
        r'\bLines\b': 'שורות',
        r'\bLine Position\b': 'מיקום שורה',
        r'\bLine length threshold\b': 'סף אורך שורה',
        r'\bJoin selected lines\b': 'צרף שורות נבחרות',
        r'\bReverse selected lines\b': 'הפוך שורות נבחרות',
        r'\bReorder\b': 'סדר מחדש',
        r'\bReorder line automatically\b': 'סדר שורה אוטומטית',
        r'\breorder lines\b': 'סדר שורות מחדש',
        
        # Text direction and formatting
        r'\bRead Direction\b': 'כיוון קריאה',
        r'\bHorizontal Left to Right\b': 'אופקי משמאל לימין',
        r'\bHorizontal Right to Left\b': 'אופקי מימין לשמאל',
        r'\bVertical Left to Right\b': 'אנכי משמאל לימין',
        r'\bVertical Right to Left\b': 'אנכי מימין לשמאל',
        r'\bText Color\b': 'צבע טקסט',
        r'\bText Panel\b': 'פאנל טקסט',
        r'\bText to search\b': 'טקסט לחיפוש',
        r'\bText annotation\b': 'הערת טקסט',
        r'\bText Annotations\b': 'הערות טקסט',
        r'\bTextual witness\b': 'עד טקסטואלי',
        r'\bUpload or select a textual witness\b': 'העלה או בחר עד טקסטואלי',
        
        # Models and training
        r'\bModel\b': 'מודל',
        r'\bModel role\b': 'תפקיד מודל',
        r'\bSelect a model\b': 'בחר מודל',
        r'\bParent from which the model was trained\b': 'הורה שממנו אומן המודל',
        r'\bTrained from\b': 'אומן מתוך',
        r'\bTrained status\b': 'סטטוס אימון',
        r'\bUnbind model from the document\b': 'בטל קישור מודל מהמסמך',
        r'\bKraken OCR Engine\b': 'מנוע OCR של Kraken',
        
        # Images and visual elements
        r'\bImage Annotation\b': 'הערת תמונה',
        r'\bImage Annotations\b': 'הערות תמונות',
        r'\bThere are no images to display\b': 'אין תמונות להצגה',
        r'\bYour Recent Images\b': 'התמונות האחרונות שלך',
        r'\bFailed to fetch additional images\b': 'נכשל באחזור תמונות נוספות',
        r'\bTotal number of document parts\b': 'מספר כולל של חלקי מסמך',
        
        # Tools and actions
        r'\bQuick Actions\b': 'פעולות מהירות',
        r'\bToggle history\b': 'הפעל/כבה היסטוריה',
        r'\bLoad this state\b': 'טען מצב זה',
        r'\bYou can go through your changes\b': 'אתה יכול לעבור על השינויים שלך',
        r'\bZoom in\b': 'הגדל',
        r'\bZoom out\b': 'הקטן',
        r'\bReset zoom\b': 'אפס זום',
        r'\bRotate Clockwise\b': 'סובב עם כיוון השעון',
        r'\bRotate Counterclockwise\b': 'סובב נגד כיוון השעון',
        r'\bMove to top\b': 'העבר לראש',
        r'\bMove to bottom\b': 'העבר לתחתית',
        r'\bLarger font\b': 'גופן גדול יותר',
        r'\bSmaller font\b': 'גופן קטן יותר',
        
        # Shortcuts and interactions
        r'\bLeft click\b': 'לחיצה שמאלית',
        r'\bRight click\b': 'לחיצה ימנית',
        r'\bshift and drag\b': 'Shift וגרירה',
        r'\bHitting\b': 'לחיצה על',
        r'\bwhen in region mode\b': 'כשבמצב אזורים',
        r'\bnew control point\b': 'נקודת בקרה חדשה',
        
        # Layer and level management
        r'\bLayer Name\b': 'שם שכבה',
        r'\bMarker Type\b': 'סוג סמן',
        r'\bTopline\b': 'קו עליון',
        r'\bBaseline\b': 'קו בסיס',
        r'\bPolygon\b': 'מצולע',
        r'\bRectangle\b': 'מלבן',
        
        # Export formats and options
        r'\bPageXML\b': 'PageXML',
        r'\bOpenITI Markdown\b': 'OpenITI Markdown',
        r'\bOpenITI TEI XML\b': 'OpenITI TEI XML',
        
        # File types and protocols
        r'\bIIIF\b': 'IIIF',
        r'\bIIIF Manifest URI\b': 'URI מניפסט IIIF',
        r'\bRemote METS URI\b': 'URI METS מרוחק',
        r'\bPython\b': 'Python',
        
        # Advanced UI elements
        r'\bPagination\b': 'עימוד',
        r'\bBreadcrumbs\b': 'נתיב ניווט',
        r'\bSidebar\b': 'סרגל צד',
        r'\bToolbar\b': 'סרגל כלים',
        r'\bDropdown\b': 'תפריט נפתח',
        r'\bModal\b': 'חלון קופץ',
        r'\bTooltip\b': 'רמז כלי',
        r'\bOverlay\b': 'שכבת-על',
        
        # Measurements and thresholds
        r'\bThreshold\b': 'סף',
        r'\bMax offset\b': 'היסט מקסימלי',
        r'\bRatio\b': 'יחס',
        r'\bFrequency\b': 'תדירות',
        
        # Groups and sharing
        r'\bGroup\b': 'קבוצה',
        r'\bGroups\b': 'קבוצות',
        r'\bGroup identifier\b': 'מזהה קבוצה',
        r'\bGroup name\b': 'שם קבוצה',
        r'\bShares\b': 'שיתופים',
        r'\bRights\b': 'הרשאות',
        r'\bRole\b': 'תפקיד',
        
        # Technical specifications
        r'\bGPU cost\b': 'עלות GPU',
        r'\bGPU usage\b': 'שימוש ב-GPU',
        r'\bGPU usage over the last week\b': 'שימוש ב-GPU השבוע האחרון',
        
        # Services and hosting
        r'\bService hosted and maintained by\b': 'שירות מתארח ומתוחזק על ידי',
        r'\bService originally developed by\b': 'שירות פותח במקור על ידי',
        r'\bPowered by\b': 'מופעל על ידי',
        r'\bInria Paris\b': 'Inria Paris',
        r'\bOther Contributions\b': 'תרומות אחרות',
        r'\bOther Contributors\b': 'תורמים אחרים',
        
        # ------------------------------------------------------------------
        # Batch 8 - Final UI elements and messages (אלמנטי ממשק אחרונים והודעות)
        # ------------------------------------------------------------------
        
        # Search and filtering
        r'\bSearch element name\b': 'חפש שם אלמנט',
        r'\bSearch score\b': 'ציון חיפוש',
        r'\bSearch to filter images by element name\b': 'חפש כדי לסנן תמונות לפי שם אלמנט',
        r'\bglobal search\b': 'חיפוש גלובלי',
        r'\bFind and replace text in projects\b': 'חפש והחלף טקסט בפרויקטים',
        r'\bexpand task monitoring and usage menu\b': 'הרחב תפריט מעקב ושימוש במשימות',
        r'\bexpand user profile menu\b': 'הרחב תפריט פרופיל משתמש',
        r'\bopen menu\b': 'פתח תפריט',
        r'\bswitch to light mode\b': 'עבור למצב בהיר',
        
        # Error and status messages
        r'\bError calculating masks\b': 'שגיאה בחישוב מסכות',
        r'\bMask calculation queued\b': 'חישוב מסכה בתור',
        r'\bSuccessfully calculated masks\b': 'מסכות חושבו בהצלחה',
        r'\bRedraw Masks\b': 'צייר מחדש מסכות',
        r'\bOnly masks\b': 'רק מסכות',
        r'\brefreshSegmenter called with no image\b': 'refreshSegmenter נקרא ללא תמונה',
        
        # Form elements and validation
        r'\bRequired\b': 'נדרש',
        r'\bOptional\b': 'אופציונלי',
        r'\bInvalid\b': 'לא חוקי',
        r'\bPlaceholder\b': 'מקום להחזקה',
        r'\branges separated by dashes\b': 'טווחים מופרדים במקפים',
        
        # Interface modes and states
        r'\bNo Components\b': 'אין רכיבים',
        r'\bNo type assigned\b': 'לא הוקצה סוג',
        r'\ben masse\b': 'בקבוצה',
        
        # Colors and visual elements
        r'\bgreen\b': 'ירוק',
        r'\bgrey\b': 'אפור',
        r'\blightgrey\b': 'אפור בהיר',
        r'\bwhite\b': 'לבן',
        r'\bselect color\b': 'בחר צבע',
        
        # Typography and formatting
        r'\bItalic\b': 'נטוי',
        r'\bBold\b': 'מודגש',
        r'\bNormal\b': 'רגיל',
        r'\bStrong\b': 'חזק',
        
        # Part types and document structure
        r'\bPart types\b': 'סוגי חלקים',
        r'\bin document\b': 'במסמך',
        r'\bElement Details\b': 'פרטי אלמנט',
        
        # Workflow and processing
        r'\bWorkflow\b': 'זרימת עבודה',
        r'\bSegment\b': 'פלח',
        r'\bTranscribe\b': 'תמלל',
        r'\bTrain\b': 'אמן',
        r'\bAlign\b': 'יישר',
        
        # Completion and finishing
        r'\bfinish\b': 'סיים',
        r'\bDone\b': 'בוצע',
        r'\bCompleted\b': 'הושלם',
        r'\bReady\b': 'מוכן',
        
        # Various UI labels that were missed
        r'\bSingle\b': 'יחיד',
        r'\bMultiple\b': 'מרובה',
        r'\bAll\b': 'הכול',
        r'\bNone\b': 'אף אחד',
        r'\bOther\b': 'אחר',
        r'\bCustom\b': 'מותאם אישית',
        r'\bDefault\b': 'ברירת מחדל',
        r'\bAuto\b': 'אוטומטי',
        r'\bManual\b': 'ידני',
        
        # Final batch of common terms
        r'\bFormat\b': 'פורמט',
        r'\bType\b': 'סוג',
        r'\bCategory\b': 'קטגוריה',
        r'\bLevel\b': 'רמה',
        r'\bOrder\b': 'סדר',
        r'\bPosition\b': 'מיקום',
        r'\bSize\b': 'גודל',
        r'\bWidth\b': 'רוחב',
        r'\bHeight\b': 'גובה',
        r'\bLength\b': 'אורך',
        r'\bCount\b': 'מספר',
        r'\bNumber\b': 'מספר',
        r'\bIndex\b': 'אינדקס',
        r'\bRange\b': 'טווח',
        r'\bLimit\b': 'הגבלה',
        r'\bMaximum\b': 'מקסימום',
        r'\bMinimum\b': 'מינימום',
        
        # Final UI actions
        r'\bApply\b': 'החל',
        r'\bReset\b': 'אפס',
        r'\bUndo\b': 'בטל',
        r'\bRedo\b': 'בצע שוב',
        r'\bClear\b': 'נקה',
        r'\bRemove\b': 'הסר',
        r'\bAdd\b': 'הוסף',
        r'\bInsert\b': 'הכנס',
        r'\bReplace\b': 'החלף',
        r'\bModify\b': 'שנה',
        r'\bChange\b': 'שנה',
        r'\bSwitch\b': 'החלף',
        r'\bToggle\b': 'הפעל/כבה',
        r'\bEnable\b': 'הפעל',
        r'\bDisable\b': 'כבה',
        r'\bShow\b': 'הצג',
        r'\bHide\b': 'הסתר',
        r'\bExpand\b': 'הרחב',
        r'\bCollapse\b': 'כווץ',
        r'\bFold\b': 'קפל',
        r'\bUnfold\b': 'פרוש',
        
        # Status indicators
        r'\bOnline\b': 'מקוון',
        r'\bOffline\b': 'לא מקוון',
        r'\bConnected\b': 'מחובר',
        r'\bDisconnected\b': 'מנותק',
        r'\bAvailable\b': 'זמין',
        r'\bUnavailable\b': 'לא זמין',
        r'\bBusy\b': 'עסוק',
        r'\bIdle\b': 'בהמתנה',
        r'\bLoading\b': 'טוען',
        r'\bProcessing\b': 'מעבד',
        r'\bWaiting\b': 'ממתין',
        r'\bReady\b': 'מוכן',
        
        # ------------------------------------------------------------------
        # Batch 9 - Final critical UI strings (מחרוזות ממשק קריטיות אחרונות)
        # These are the most visible and important remaining UI strings
        # ------------------------------------------------------------------
        
        # The remaining critical ones we can definitively identify
        r'\ben masse\b': 'בקבוצה',
        r'\bescape\b': 'מקש Escape', 
        r'\bfinish\b': 'סיים',
        r'\bsingle\b': 'יחיד',
        r'\btable\b': 'טבלה',
        r'\bvertical\b': 'אנכי',
        r'\bmenu\b': 'תפריט',
        r'\bmain\b': 'ראשי',
        r'\bpost\b': 'פוסט',
        r'\bpage\b': 'עמוד',
        r'\bpages\b': 'עמודים',
        r'\bmodule\b': 'מודול',
        r'\bmodule aligned\b': 'מודול מיושר',
        r'\blead\b': 'מוביל',
        r'\bjumbotron\b': 'כותרת ענק',
        r'\bmain\b': 'עיקרי',
        r'\bmenu\b': 'תפריט',
        r'\btask\b': 'משימה',
        r'\bquery\b': 'שאילתה',
        r'\bsubmit\b': 'שלח',
        r'\bstylesheet\b': 'גיליון סגנון',
        r'\buse strict\b': 'השתמש במצב קפדני',
        
        # These are the user-visible interface elements that matter most
        r'\bmasonry\b': 'רשת דינמית',
        r'\bsearchbar\b': 'סרגל חיפוש',
        r'\bprogressbar\b': 'סרגל התקדמות',
        r'\btablist\b': 'רשימת לשוניות',
        r'\btabpanel\b': 'פאנל לשונית',
        r'\bviewport\b': 'חלון תצוגה',
        r'\brow container\b': 'מיכל שורה',
        
        # Most critical remaining messages and labels
        r'\bweeklyChart\b': 'תרשים שבועי',
        r'\bexampleModalLabel\b': 'תווית חלון דוגמה',
        r'\bimportOntologyModalLabel\b': 'תווית חלון יבוא אונטולוגיה',
        r'\bmigrateModalLabel\b': 'תווית חלון העברה',
        r'\bshareModalLabel\b': 'תווית חלון שיתוף',
        r'\btagsModalLabel\b': 'תווית חלון תגיות',
        r'\btagsManagementLabel\b': 'תווית ניהול תגיות',
        
        # Navigation elements
        r'\bnavbarDropdown\b': 'תפריט נפתח בסרגל',
        r'\bnavbarSupportedContent\b': 'תוכן נתמך בסרגל',
        
        # Really important workflow messages
        r'\bGathering data\b': 'איסוף נתונים',
        r'\bImporting\b': 'מייבא',
        r'\bprocessing\b': 'מעבד',
        r'\bwaiting\b': 'ממתין',
        r'\bbusy\b': 'עסוק',
        r'\bidle\b': 'במנוחה',
        r'\bongoing\b': 'מתמשך',
        
        # Essential error and info messages  
        r'\bThe load state button\b': 'כפתור טעינת מצב',
        r'\bThe red trash\b': 'הפח האדום',
        r'\bThe yellow trash button\b': 'כפתור הפח הצהוב',
        r'\bYou can go through your changes\b': 'אתה יכול לעבור על השינויים שלך',
        
        # Key workflow steps
        r'\bReload vocabulary\b': 'טען מחדש אוצר מילים',
        r'\blink to Project Guidelines\b': 'קישור להנחיות פרויקט',
        
        # Critical UI feedback
        r'\bMask calculation queued\b': 'חישוב מסכה בתור',
        r'\bSuccessfully calculated masks\b': 'מסכות חושבו בהצלחה',
        r'\bError calculating masks\b': 'שגיאה בחישוב מסכות',
        r'\bFailed to fetch additional images\b': 'נכשל באחזור תמונות נוספות',
        r'\bThere are no images to display\b': 'אין תמונות להצגה',
        r'\bLine not present in segmentation\b': 'שורה לא קיימת בפילוח',
        r'\brefreshSegmenter called with no image\b': 'refreshSegmenter נקרא ללא תמונה',
        
        # Essential form helpers
        r'\branges separated by dashes\b': 'טווחים מופרדים במקפים',
        r'\bselect color\b': 'בחר צבע',
        r'\bshift and drag\b': 'Shift וגרירה',
        r'\bwhen in region mode\b': 'כשבמצב אזורים',
        r'\bnew control point\b': 'נקודת בקרה חדשה',
        
        # Status and progress indicators
        r'\bis inviting you to join\b': 'מזמין אותך להצטרף',
        r'\bModule aligned\b': 'מודול מיושר',
        r'\bTotal number of document parts\b': 'מספר כולל של חלקי מסמך',
        r'\bTotal number of regions\b': 'מספר כולל של אזורים',
        r'\bParent from which the model was trained\b': 'הורה שממנו אומן המודל',
        r'\bUnbind model from the document\b': 'בטל קישור מודל מהמסמך',
        
        # Final critical UI elements
        r'\bService hosted and maintained by\b': 'שירות מתארח ומתוחזק על ידי',
        r'\bService originally developed by\b': 'שירות פותח במקור על ידי',
        r'\bOther Contributions\b': 'תרומות אחרות',
        r'\bOther Contributors\b': 'תורמים אחרים',
    }
    
    def process_response(self, request, response):
        """
        מעבד את תגובת ה-HTTP ומחליף מחרוזות אם השפה היא עברית
        ומוסיף תמיכה RTL מלאה
        """
        # פעל רק כאשר השפה היא עברית
        if get_language() != 'he':
            return response
        
        # פעל רק על תגובות HTML
        content_type = response.get('Content-Type', '')
        if not content_type.startswith('text/html'):
            return response
        
        try:
            # קבל את התוכן כ-string
            if hasattr(response, 'content'):
                html_content = response.content.decode('utf-8')
                
                # החלף כל המחרוזות הקשות
                for english_pattern, hebrew_text in self.TRANSLATION_MAP.items():
                    html_content = re.sub(
                        english_pattern, 
                        hebrew_text, 
                        html_content, 
                        flags=re.IGNORECASE
                    )
                
                # הוסף תמיכה RTL למסמך - כיוון מימין לשמאל
                html_content = self._add_rtl_support(html_content)
                
                # עדכן את התוכן
                response.content = html_content.encode('utf-8')
                
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            # במקרה של בעיות encoding, החזר את התגובה המקורית
            pass
        
        return response
    
    def _add_rtl_support(self, html_content):
        """
        מוסיף תמיכה RTL (מימין לשמאל) למסמך HTML
        """
        # הוסף dir="rtl" ו-lang="he" ל-html tag בכל מקרה
        if '<html' in html_content:
            if 'dir=' in html_content:
                # החלף כל dir קיים ב-rtl
                html_content = re.sub(
                    r'dir="[^"]*"',
                    'dir="rtl"',
                    html_content,
                    flags=re.IGNORECASE
                )
            else:
                # הוסף dir="rtl" חדש
                html_content = re.sub(
                    r'<html([^>]*)>',
                    r'<html\1 dir="rtl" lang="he">',
                    html_content,
                    flags=re.IGNORECASE
                )
            
            # וודא שיש גם lang="he"
            if 'lang=' not in html_content:
                html_content = re.sub(
                    r'<html([^>]*)>',
                    r'<html\1 lang="he">',
                    html_content,
                    flags=re.IGNORECASE
                )
        
        # הוסף dir="rtl" ל-body tag בכל מקרה
        if '<body' in html_content:
            if 'dir=' in html_content:
                # החלף כל dir קיים ב-rtl
                html_content = re.sub(
                    r'<body([^>]*?)dir="[^"]*"([^>]*?)>',
                    r'<body\1dir="rtl"\2>',
                    html_content,
                    flags=re.IGNORECASE
                )
            else:
                # הוסף dir="rtl" חדש
                html_content = re.sub(
                    r'<body([^>]*)>',
                    r'<body\1 dir="rtl">',
                    html_content,
                    flags=re.IGNORECASE
                )
        
        # הוסף CSS עבור RTL לפני סגירת head
        rtl_css = """
<style>
/* BiblIA RTL Support - כיוון עברית מימין לשמאל */
* {
    direction: rtl !important;
}

html, html[dir="rtl"], body, body[dir="rtl"] {
    direction: rtl !important;
    text-align: right !important;
}

/* תמיכה RTL כללית לכל האלמנטים */
div, span, p, h1, h2, h3, h4, h5, h6, label, input, textarea, select, button, a {
    direction: rtl !important;
    text-align: right !important;
}

/* תמיכה RTL לניווט Bootstrap */
.navbar, .navbar-nav, .navbar-brand {
    direction: rtl !important;
    text-align: right !important;
}

.nav, .nav-tabs, .nav-pills, .nav-link {
    direction: rtl !important;
    text-align: right !important;
}

/* תיקון סדר פריטי ניווט */
.navbar-nav {
    flex-direction: row-reverse !important;
}

.nav-tabs .nav-item {
    margin-left: 0 !important;
    margin-right: -1px !important;
}

/* תמיכה RTL לטפסים */
.form-control, .form-select, .form-group, .form-group label, .form-check-label {
    direction: rtl !important;
    text-align: right !important;
}

.form-check-input {
    margin-left: 0.25rem !important;
    margin-right: -1.25rem !important;
}

.input-group {
    flex-direction: row-reverse !important;
}

.input-group-text {
    text-align: right !important;
}

/* תמיכה RTL לכפתורים */
.btn, .btn-group, .btn-toolbar {
    direction: rtl !important;
    text-align: center !important;
}

.btn-group {
    flex-direction: row-reverse !important;
}

/* תמיכה RTL לטבלאות */
.table, .table th, .table td {
    direction: rtl !important;
    text-align: right !important;
}

.table-responsive {
    direction: rtl !important;
}

/* תמיכה RTL לדרופדאון */
.dropdown, .dropdown-menu, .dropdown-item {
    direction: rtl !important;
    text-align: right !important;
}

.dropdown-toggle::after {
    margin-left: 0 !important;
    margin-right: 0.255em !important;
}

/* תמיכה RTL למודלים */
.modal, .modal-dialog, .modal-content, .modal-body, .modal-header, .modal-footer {
    direction: rtl !important;
    text-align: right !important;
}

.modal-header .btn-close {
    margin: -0.5rem auto -0.5rem -0.5rem !important;
}

/* תמיכה RTL לכרטיסים */
.card, .card-header, .card-body, .card-footer {
    direction: rtl !important;
    text-align: right !important;
}

/* תמיכה RTL לרשימות */
.list-group, .list-group-item {
    direction: rtl !important;
    text-align: right !important;
}

/* תמיכה RTL לאלרטים */
.alert {
    direction: rtl !important;
    text-align: right !important;
}

.alert-dismissible .btn-close {
    position: absolute;
    top: 0;
    left: 0 !important;
    right: auto !important;
    z-index: 2;
    padding: 1.25rem 1rem;
}

/* תמיכה RTL לפעולות וכלי עבודה */
.toolbar, .btn-toolbar {
    direction: rtl !important;
    justify-content: flex-end !important;
}

/* תיקון כיוון לאלמנטים ספציפיים של eScriptorium */
.document-list, .project-list, .model-list {
    direction: rtl !important;
    text-align: right !important;
}

.breadcrumb {
    direction: rtl !important;
    flex-direction: row-reverse !important;
}

.breadcrumb-item + .breadcrumb-item::before {
    float: right !important;
    padding-right: 0 !important;
    padding-left: 0.5rem !important;
    content: "\\";
}

/* תמיכה RTL לפאנלים ואקורדיון */
.accordion, .collapse, .card-accordion {
    direction: rtl !important;
    text-align: right !important;
}

/* תמיכה RTL לפגינציה */
.pagination {
    direction: rtl !important;
    flex-direction: row-reverse !important;
}

/* תמיכה RTL לאלמנטים מותאמים של eScriptorium */
.document-viewer, .transcription-panel, .image-viewer {
    direction: rtl !important;
    text-align: right !important;
}

/* תיקון למחרוזות בעברית בתוך אלמנטים אנגליים */
[lang="he"], .hebrew-text {
    direction: rtl !important;
    text-align: right !important;
}

/* תמיכה RTL לסייד בר וניווט צדדי */
.sidebar, .sidebar-nav, .offcanvas {
    direction: rtl !important;
    text-align: right !important;
}

/* תיקון עמודות Bootstrap */
.col, .col-1, .col-2, .col-3, .col-4, .col-5, .col-6, .col-7, .col-8, .col-9, .col-10, .col-11, .col-12,
.col-sm, .col-md, .col-lg, .col-xl, .col-xxl {
    direction: rtl !important;
    text-align: right !important;
}

/* תמיכה RTL לטקסט באופן כללי */
.text-left { text-align: right !important; }
.text-right { text-align: left !important; }

/* תיקון floating elements */
.float-left { float: right !important; }
.float-right { float: left !important; }

/* תיקון margins ו-paddings */
.ml-auto { margin-left: 0 !important; margin-right: auto !important; }
.mr-auto { margin-right: 0 !important; margin-left: auto !important; }
.pl-3 { padding-left: 0 !important; padding-right: 1rem !important; }
.pr-3 { padding-right: 0 !important; padding-left: 1rem !important; }

/* תמיכה RTL לתוכן דינמי */
.content, .main-content, .page-content {
    direction: rtl !important;
    text-align: right !important;
}

/* וידוא שכל התוכן יהיה RTL */
body * {
    direction: rtl !important;
}

/* תיקון מיוחד לפילדים של Django */
.django-form-row, .form-row {
    direction: rtl !important;
    text-align: right !important;
}

.django-admin-form input, .django-admin-form select, .django-admin-form textarea {
    direction: rtl !important;
    text-align: right !important;
}
</style>
"""
        
        # הוסף CSS לפני סגירת head
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', rtl_css + '</head>')
        
        return html_content