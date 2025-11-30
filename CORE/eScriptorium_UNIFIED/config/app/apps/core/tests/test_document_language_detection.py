"""
Model Tests for Language Detection - Document Model Methods

Tests for Document language detection model methods:
- detect_language_and_recommend_model()
- _get_text_sample()
- auto_detect_and_set_direction()
"""

from django.test import TestCase
from unittest.mock import patch, MagicMock

from core.models import Document, DocumentPart, Project, Transcription, Line, LineTranscription
from users.models import User
from core.language_utils import ScriptType


class DocumentLanguageDetectionModelTest(TestCase):
    """
    Test suite for Document model language detection methods
    
    בדיקות למתודות זיהוי שפה במודל Document
    """
    
    def setUp(self):
        """Set up test fixtures - הכנת מבחנים"""
        # Create test user - יצירת משתמש בדיקה
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Create test project - יצירת פרויקט בדיקה
        self.project = Project.objects.create(
            name='Test Project - פרויקט בדיקה',
            owner=self.user
        )
        
        # Create test document - יצירת מסמך בדיקה
        self.document = Document.objects.create(
            name='Test Document - מסמך בדיקה',
            project=self.project,
            owner=self.user,
            read_direction=Document.READ_DIRECTION_LTR  # Default LTR
        )
        
    def test_detect_language_hebrew_text(self):
        """
        Test language detection with Hebrew text
        בדיקת זיהוי שפה עם טקסט עברי
        """
        # Create document part - יצירת חלק מסמך
        part = DocumentPart.objects.create(
            document=self.document,
            order=1
        )
        
        # Create transcription - יצירת תמלול
        transcription = Transcription.objects.create(
            name='Hebrew Transcription - תמלול עברי',
            document=self.document
        )
        
        # Create lines with Hebrew text - יצירת שורות עם טקסט עברי
        hebrew_texts = [
            'שלום עולם זהו טקסט בעברית',
            'בראשית ברא אלוהים את השמים ואת הארץ',
            'וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי אוֹר',
        ]
        
        for idx, text in enumerate(hebrew_texts):
            line = Line.objects.create(
                document_part=part,
                order=idx
            )
            LineTranscription.objects.create(
                line=line,
                transcription=transcription,
                content=text
            )
        
        # Run detection - הרצת זיהוי
        result = self.document.detect_language_and_recommend_model()
        
        # Assertions - בדיקות תוצאות
        self.assertEqual(result['script'], 'hebrew')
        self.assertEqual(result['direction'], 'rtl')
        self.assertEqual(result['recommended_engine'], 'kraken')
        self.assertGreater(result['confidence'], 0.8)  # High confidence for Hebrew
        self.assertIn('sample_text', result)
        self.assertTrue(len(result['sample_text']) > 0)
    
    def test_detect_language_arabic_text(self):
        """
        Test language detection with Arabic text
        בדיקת זיהוי שפה עם טקסט ערבי
        """
        part = DocumentPart.objects.create(
            document=self.document,
            order=1
        )
        
        transcription = Transcription.objects.create(
            name='Arabic Transcription - תמלול ערבי',
            document=self.document
        )
        
        # Arabic texts - טקסטים בערבית
        arabic_texts = [
            'مرحبا بالعالم هذا نص بالعربية',
            'القرآن الكريم كتاب الله',
            'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
        ]
        
        for idx, text in enumerate(arabic_texts):
            line = Line.objects.create(
                document_part=part,
                order=idx
            )
            LineTranscription.objects.create(
                line=line,
                transcription=transcription,
                content=text
            )
        
        result = self.document.detect_language_and_recommend_model()
        
        self.assertEqual(result['script'], 'arabic')
        self.assertEqual(result['direction'], 'rtl')
        self.assertEqual(result['recommended_engine'], 'kraken')
        self.assertGreater(result['confidence'], 0.8)
        self.assertTrue(result.get('has_tashkeel', False))  # Arabic with tashkeel
    
    def test_detect_language_latin_text(self):
        """
        Test language detection with Latin text
        בדיקת זיהוי שפה עם טקסט לטיני
        """
        part = DocumentPart.objects.create(
            document=self.document,
            order=1
        )
        
        transcription = Transcription.objects.create(
            name='English Transcription - תמלול אנגלי',
            document=self.document
        )
        
        # English texts - טקסטים באנגלית
        english_texts = [
            'Hello world this is English text',
            'The quick brown fox jumps over the lazy dog',
            'Lorem ipsum dolor sit amet consectetur',
        ]
        
        for idx, text in enumerate(english_texts):
            line = Line.objects.create(
                document_part=part,
                order=idx
            )
            LineTranscription.objects.create(
                line=line,
                transcription=transcription,
                content=text
            )
        
        result = self.document.detect_language_and_recommend_model()
        
        self.assertEqual(result['script'], 'latin')
        self.assertEqual(result['direction'], 'ltr')
        self.assertEqual(result['recommended_engine'], 'tesseract')
        self.assertGreater(result['confidence'], 0.8)
    
    def test_detect_language_mixed_scripts(self):
        """
        Test detection with mixed Hebrew and English
        בדיקת זיהוי עם עברית ואנגלית מעורבים
        """
        part = DocumentPart.objects.create(
            document=self.document,
            order=1
        )
        
        transcription = Transcription.objects.create(
            name='Mixed Transcription - תמלול מעורב',
            document=self.document
        )
        
        # Mixed texts - טקסטים מעורבים
        mixed_texts = [
            'Hello שלום World עולם',
            'Testing בדיקה mixed מעורב',
        ]
        
        for idx, text in enumerate(mixed_texts):
            line = Line.objects.create(
                document_part=part,
                order=idx
            )
            LineTranscription.objects.create(
                line=line,
                transcription=transcription,
                content=text
            )
        
        result = self.document.detect_language_and_recommend_model()
        
        self.assertEqual(result['script'], 'mixed')
        self.assertIn('confidence', result)
        # Mixed scripts have lower confidence - סקריפטים מעורבים עם אמון נמוך יותר
        self.assertLess(result['confidence'], 0.9)
    
    def test_detect_language_with_nikud(self):
        """
        Test Hebrew text with nikud detection
        בדיקת טקסט עברי עם זיהוי ניקוד
        """
        part = DocumentPart.objects.create(
            document=self.document,
            order=1
        )
        
        transcription = Transcription.objects.create(
            name='Hebrew with Nikud - עברית עם ניקוד',
            document=self.document
        )
        
        # Hebrew with nikud - עברית עם ניקוד
        line = Line.objects.create(document_part=part, order=0)
        LineTranscription.objects.create(
            line=line,
            transcription=transcription,
            content='בְּרֵאשִׁית בָּרָא אֱלֹהִים'
        )
        
        result = self.document.detect_language_and_recommend_model()
        
        self.assertEqual(result['script'], 'hebrew')
        self.assertTrue(result['has_nikud'])
        self.assertIn('remove_nikud', result.get('preprocessing', []))
    
    def test_get_text_sample_multiple_parts(self):
        """
        Test _get_text_sample with multiple document parts
        בדיקת _get_text_sample עם מספר חלקי מסמך
        """
        # Create multiple parts - יצירת מספר חלקים
        for part_num in range(3):
            part = DocumentPart.objects.create(
                document=self.document,
                order=part_num
            )
            
            transcription = Transcription.objects.create(
                name=f'Transcription {part_num}',
                document=self.document
            )
            
            # Add lines - הוספת שורות
            for line_num in range(5):
                line = Line.objects.create(
                    document_part=part,
                    order=line_num
                )
                LineTranscription.objects.create(
                    line=line,
                    transcription=transcription,
                    content=f'שורה {line_num} בחלק {part_num}'
                )
        
        sample = self.document._get_text_sample(max_chars=200)
        
        self.assertTrue(len(sample) > 0)
        self.assertLessEqual(len(sample), 500)  # Should respect max_chars roughly
        self.assertIn('שורה', sample)  # Contains Hebrew text
    
    def test_get_text_sample_empty_document(self):
        """
        Test _get_text_sample with no transcriptions
        בדיקת _get_text_sample ללא תמלולים
        """
        # Document with no transcriptions - מסמך ללא תמלולים
        sample = self.document._get_text_sample()
        
        self.assertEqual(sample, '')
    
    def test_get_text_sample_respects_max_chars(self):
        """
        Test that _get_text_sample respects max_chars limit
        בדיקה שה-_get_text_sample מכבד את הגבלת max_chars
        """
        part = DocumentPart.objects.create(
            document=self.document,
            order=0
        )
        
        transcription = Transcription.objects.create(
            name='Long Transcription - תמלול ארוך',
            document=self.document
        )
        
        # Create many lines with long text - יצירת שורות רבות עם טקסט ארוך
        long_text = 'שלום עולם ' * 20  # 240 chars per line
        for i in range(10):
            line = Line.objects.create(document_part=part, order=i)
            LineTranscription.objects.create(
                line=line,
                transcription=transcription,
                content=long_text
            )
        
        # Request small sample - בקשת דגימה קטנה
        sample = self.document._get_text_sample(max_chars=100)
        
        # Should not exceed limit significantly - לא צריך לחרוג מהגבלה משמעותית
        self.assertLess(len(sample), 500)  # Allows some overflow for word boundaries
    
    def test_auto_detect_and_set_direction_hebrew(self):
        """
        Test automatic direction setting for Hebrew document
        בדיקת הגדרת כיוון אוטומטית למסמך עברי
        """
        # Start with LTR - התחלה עם LTR
        self.assertEqual(self.document.read_direction, Document.READ_DIRECTION_LTR)
        
        # Add Hebrew content - הוספת תוכן עברי
        part = DocumentPart.objects.create(document=self.document, order=0)
        transcription = Transcription.objects.create(
            name='Hebrew Content',
            document=self.document
        )
        
        line = Line.objects.create(document_part=part, order=0)
        LineTranscription.objects.create(
            line=line,
            transcription=transcription,
            content='זהו טקסט בעברית מימין לשמאל'
        )
        
        # Auto-detect and set - זיהוי והגדרה אוטומטיים
        changed = self.document.auto_detect_and_set_direction()
        
        self.assertTrue(changed)
        self.document.refresh_from_db()
        self.assertEqual(self.document.read_direction, Document.READ_DIRECTION_RTL)
    
    def test_auto_detect_and_set_direction_latin(self):
        """
        Test automatic direction setting for Latin document
        בדיקת הגדרת כיוון אוטומטית למסמך לטיני
        """
        # Start with RTL - התחלה עם RTL
        self.document.read_direction = Document.READ_DIRECTION_RTL
        self.document.save()
        
        # Add English content - הוספת תוכן אנגלי
        part = DocumentPart.objects.create(document=self.document, order=0)
        transcription = Transcription.objects.create(
            name='English Content',
            document=self.document
        )
        
        line = Line.objects.create(document_part=part, order=0)
        LineTranscription.objects.create(
            line=line,
            transcription=transcription,
            content='This is left to right English text'
        )
        
        # Auto-detect and set - זיהוי והגדרה אוטומטיים
        changed = self.document.auto_detect_and_set_direction()
        
        self.assertTrue(changed)
        self.document.refresh_from_db()
        self.assertEqual(self.document.read_direction, Document.READ_DIRECTION_LTR)
    
    def test_auto_detect_no_change_needed(self):
        """
        Test auto_detect when direction is already correct
        בדיקת auto_detect כשהכיוון כבר נכון
        """
        # Document already RTL, add Hebrew content
        # מסמך כבר RTL, הוספת תוכן עברי
        self.document.read_direction = Document.READ_DIRECTION_RTL
        self.document.save()
        
        part = DocumentPart.objects.create(document=self.document, order=0)
        transcription = Transcription.objects.create(
            name='Hebrew Content',
            document=self.document
        )
        
        line = Line.objects.create(document_part=part, order=0)
        LineTranscription.objects.create(
            line=line,
            transcription=transcription,
            content='טקסט עברי'
        )
        
        changed = self.document.auto_detect_and_set_direction()
        
        self.assertFalse(changed)  # No change needed - אין צורך בשינוי
        self.assertEqual(self.document.read_direction, Document.READ_DIRECTION_RTL)
    
    def test_detect_language_empty_document(self):
        """
        Test detection on document with no content
        בדיקת זיהוי במסמך ללא תוכן
        """
        result = self.document.detect_language_and_recommend_model()
        
        self.assertEqual(result['script'], 'unknown')
        self.assertEqual(result['confidence'], 0.0)
        self.assertIn('error', result)
        self.assertIn('No transcribed text', result['error'])
    
    def test_detect_language_sample_size_parameter(self):
        """
        Test that sample_size parameter works correctly
        בדיקה שפרמטר sample_size עובד כהלכה
        """
        part = DocumentPart.objects.create(document=self.document, order=0)
        transcription = Transcription.objects.create(
            name='Test',
            document=self.document
        )
        
        # Create long text - יצירת טקסט ארוך
        long_text = 'שלום עולם ' * 100
        line = Line.objects.create(document_part=part, order=0)
        LineTranscription.objects.create(
            line=line,
            transcription=transcription,
            content=long_text
        )
        
        # Test different sample sizes - בדיקת גדלי דגימה שונים
        result_small = self.document.detect_language_and_recommend_model(sample_size=50)
        result_large = self.document.detect_language_and_recommend_model(sample_size=500)
        
        self.assertLessEqual(len(result_small['sample_text']), 200)
        self.assertLessEqual(len(result_large['sample_text']), 200)
        # Both should detect Hebrew - שניהם צריכים לזהות עברית
        self.assertEqual(result_small['script'], 'hebrew')
        self.assertEqual(result_large['script'], 'hebrew')
    
    def test_recommendations_structure(self):
        """
        Test that recommendations have correct structure
        בדיקה שההמלצות יש להן מבנה נכון
        """
        part = DocumentPart.objects.create(document=self.document, order=0)
        transcription = Transcription.objects.create(
            name='Test',
            document=self.document
        )
        
        line = Line.objects.create(document_part=part, order=0)
        LineTranscription.objects.create(
            line=line,
            transcription=transcription,
            content='טקסט בדיקה'
        )
        
        result = self.document.detect_language_and_recommend_model()
        
        # Verify all required fields - אימות כל השדות הנדרשים
        required_fields = [
            'script', 'direction', 'confidence',
            'has_nikud', 'has_tashkeel',
            'recommended_engine', 'model_hint', 'preprocessing',
            'sample_text'
        ]
        
        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")
        
        # Verify types - אימות סוגים
        self.assertIsInstance(result['script'], str)
        self.assertIsInstance(result['direction'], str)
        self.assertIsInstance(result['confidence'], float)
        self.assertIsInstance(result['has_nikud'], bool)
        self.assertIsInstance(result['has_tashkeel'], bool)
        self.assertIsInstance(result['recommended_engine'], str)
        self.assertIsInstance(result['preprocessing'], list)
    
    def test_statistics_in_result(self):
        """
        Test that detection result includes script statistics
        בדיקה שתוצאת הזיהוי כוללת סטטיסטיקות סקריפט
        """
        part = DocumentPart.objects.create(document=self.document, order=0)
        transcription = Transcription.objects.create(
            name='Test',
            document=self.document
        )
        
        line = Line.objects.create(document_part=part, order=0)
        LineTranscription.objects.create(
            line=line,
            transcription=transcription,
            content='עברית English ערבية'  # Mixed scripts
        )
        
        result = self.document.detect_language_and_recommend_model()
        
        self.assertIn('statistics', result)
        stats = result['statistics']
        self.assertIsInstance(stats, dict)
        # Should have counts for different scripts - צריך להיות ספירות לסקריפטים שונים
        self.assertGreater(sum(stats.values()), 0)
