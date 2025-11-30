"""
API Tests for Language Detection Endpoint

Tests for DocumentLanguageDetectionView (/api/documents/{id}/detect-language/)
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from core.models import Document, DocumentPart, Project, Transcription, LineTranscription
from users.models import User, Team
from core.language_utils import ScriptType


class DocumentLanguageDetectionAPITest(APITestCase):
    """
    Test suite for Document Language Detection API endpoint
    
    Endpoint: GET /api/documents/{document_id}/detect-language/
    View: DocumentLanguageDetectionView
    """
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test users
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
        )
        
        # Create test project
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.owner
        )
        
        # Create test document
        self.document = Document.objects.create(
            name='Test Document',
            project=self.project,
            owner=self.owner
        )
        
        # Create document parts with transcriptions
        self.part = DocumentPart.objects.create(
            document=self.document,
            order=1,
            image=None  # Simplified for testing
        )
        
        # Create transcription
        self.transcription = Transcription.objects.create(
            name='Test Transcription',
            document=self.document
        )
        
        # API client
        self.client = APIClient()
        
    def test_endpoint_url_pattern(self):
        """Test that the URL pattern is correctly configured"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(url)
        # Should not return 404 (endpoint exists)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_authentication_required(self):
        """Test that authentication is required to access the endpoint"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_owner_can_access(self):
        """Test that document owner can access language detection"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            mock_detect.return_value = {
                'script': 'hebrew',
                'direction': 'rtl',
                'confidence': 0.95,
                'has_nikud': False,
                'has_tashkeel': False,
                'recommendations': {
                    'script': 'hebrew',
                    'recommended_engine': 'kraken',
                    'model_hint': 'hebrew_best',
                    'preprocessing': ['normalize_hebrew']
                }
            }
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_detect.assert_called_once()
    
    def test_staff_can_access(self):
        """Test that staff users can access any document's language detection"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.staff_user)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            mock_detect.return_value = {
                'script': 'arabic',
                'direction': 'rtl',
                'confidence': 0.88,
                'has_nikud': False,
                'has_tashkeel': True,
                'recommendations': {
                    'script': 'arabic',
                    'recommended_engine': 'kraken',
                    'model_hint': 'arabic_generalized',
                    'preprocessing': ['normalize_arabic', 'remove_tashkeel']
                }
            }
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthorized_user_denied(self):
        """Test that users without permission cannot access the endpoint"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_project_member_can_access(self):
        """Test that project members can access document language detection"""
        # Add other_user to project
        self.project.users.add(self.other_user)
        
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.other_user)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            mock_detect.return_value = {
                'script': 'latin',
                'direction': 'ltr',
                'confidence': 0.92,
                'has_nikud': False,
                'has_tashkeel': False,
                'recommendations': {
                    'script': 'latin',
                    'recommended_engine': 'tesseract',
                    'model_hint': 'eng',
                    'preprocessing': ['normalize_unicode']
                }
            }
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_nonexistent_document_returns_404(self):
        """Test that requesting a non-existent document returns 404"""
        url = '/api/documents/99999/detect-language/'
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_response_structure(self):
        """Test that the response has the correct JSON structure"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            mock_detect.return_value = {
                'script': 'hebrew',
                'direction': 'rtl',
                'confidence': 0.95,
                'has_nikud': True,
                'has_tashkeel': False,
                'recommendations': {
                    'script': 'hebrew',
                    'recommended_engine': 'kraken',
                    'model_hint': 'hebrew_best',
                    'preprocessing': ['normalize_hebrew', 'remove_nikud']
                }
            }
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Validate response structure
            data = response.json()
            self.assertIn('script', data)
            self.assertIn('direction', data)
            self.assertIn('confidence', data)
            self.assertIn('has_nikud', data)
            self.assertIn('has_tashkeel', data)
            self.assertIn('recommendations', data)
            
            # Validate recommendations structure
            recs = data['recommendations']
            self.assertIn('script', recs)
            self.assertIn('recommended_engine', recs)
            self.assertIn('model_hint', recs)
            self.assertIn('preprocessing', recs)
    
    def test_sample_size_parameter(self):
        """Test that sample_size query parameter is passed correctly"""
        url = f'/api/documents/{self.document.pk}/detect-language/?sample_size=1000'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            mock_detect.return_value = {
                'script': 'hebrew',
                'direction': 'rtl',
                'confidence': 0.95,
                'has_nikud': False,
                'has_tashkeel': False,
                'recommendations': {}
            }
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify sample_size was passed to the model method
            mock_detect.assert_called_once_with(sample_size=1000)
    
    def test_default_sample_size(self):
        """Test that default sample_size is 500 if not specified"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            mock_detect.return_value = {
                'script': 'arabic',
                'direction': 'rtl',
                'confidence': 0.88,
                'has_nikud': False,
                'has_tashkeel': True,
                'recommendations': {}
            }
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify default sample_size=500
            mock_detect.assert_called_once_with(sample_size=500)
    
    def test_invalid_sample_size(self):
        """Test that invalid sample_size parameter returns error"""
        url = f'/api/documents/{self.document.pk}/detect-language/?sample_size=invalid'
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_auto_set_direction_parameter(self):
        """Test that auto_set_direction parameter works correctly"""
        url = f'/api/documents/{self.document.pk}/detect-language/?auto_set_direction=true'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect, \
             patch.object(Document, 'auto_detect_and_set_direction') as mock_auto:
            
            mock_detect.return_value = {
                'script': 'hebrew',
                'direction': 'rtl',
                'confidence': 0.95,
                'has_nikud': False,
                'has_tashkeel': False,
                'recommendations': {}
            }
            mock_auto.return_value = True
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify auto_detect_and_set_direction was called
            mock_auto.assert_called_once()
            
            # Verify response includes direction_updated
            data = response.json()
            self.assertIn('direction_updated', data)
            self.assertTrue(data['direction_updated'])
    
    def test_auto_set_direction_false_by_default(self):
        """Test that auto_set_direction is false by default"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect, \
             patch.object(Document, 'auto_detect_and_set_direction') as mock_auto:
            
            mock_detect.return_value = {
                'script': 'arabic',
                'direction': 'rtl',
                'confidence': 0.88,
                'has_nikud': False,
                'has_tashkeel': True,
                'recommendations': {}
            }
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # auto_detect_and_set_direction should NOT be called
            mock_auto.assert_not_called()
    
    def test_error_handling_with_exception(self):
        """Test that exceptions are handled gracefully"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            mock_detect.side_effect = Exception("Test error")
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            data = response.json()
            self.assertIn('error', data)
    
    def test_empty_document_no_text(self):
        """Test detection on document with no transcribed text"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            # Simulate empty text scenario
            mock_detect.return_value = {
                'script': 'unknown',
                'direction': 'ltr',
                'confidence': 0.0,
                'has_nikud': False,
                'has_tashkeel': False,
                'recommendations': {
                    'script': 'unknown',
                    'recommended_engine': 'kraken',
                    'model_hint': None,
                    'preprocessing': []
                }
            }
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            data = response.json()
            self.assertEqual(data['script'], 'unknown')
            self.assertEqual(data['confidence'], 0.0)
    
    def test_mixed_script_detection(self):
        """Test detection of mixed script documents"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            mock_detect.return_value = {
                'script': 'mixed',
                'direction': 'rtl',  # Dominant direction
                'confidence': 0.65,  # Lower confidence for mixed
                'has_nikud': True,
                'has_tashkeel': True,
                'recommendations': {
                    'script': 'mixed',
                    'recommended_engine': 'kraken',
                    'model_hint': 'multilingual',
                    'preprocessing': ['normalize_unicode']
                }
            }
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            data = response.json()
            self.assertEqual(data['script'], 'mixed')
            self.assertTrue(data['has_nikud'])
            self.assertTrue(data['has_tashkeel'])
    
    def test_http_methods_only_get_allowed(self):
        """Test that only GET method is allowed"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        
        # POST should not be allowed
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # PUT should not be allowed
        response = self.client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # DELETE should not be allowed
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # PATCH should not be allowed
        response = self.client.patch(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_content_type_json(self):
        """Test that response content type is JSON"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            mock_detect.return_value = {
                'script': 'hebrew',
                'direction': 'rtl',
                'confidence': 0.95,
                'has_nikud': False,
                'has_tashkeel': False,
                'recommendations': {}
            }
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_confidence_score_range(self):
        """Test that confidence score is within valid range [0, 1]"""
        url = f'/api/documents/{self.document.pk}/detect-language/'
        self.client.force_authenticate(user=self.owner)
        
        with patch.object(Document, 'detect_language_and_recommend_model') as mock_detect:
            mock_detect.return_value = {
                'script': 'hebrew',
                'direction': 'rtl',
                'confidence': 0.95,
                'has_nikud': False,
                'has_tashkeel': False,
                'recommendations': {}
            }
            
            response = self.client.get(url)
            data = response.json()
            
            confidence = data['confidence']
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
            self.assertIsInstance(confidence, float)
