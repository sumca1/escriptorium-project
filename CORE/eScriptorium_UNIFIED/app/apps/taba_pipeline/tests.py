"""
TABA Pipeline Tests
Tests for models, views, and executor
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json

from apps.taba_pipeline.models import (
    GroundTruthCorpus,
    GroundTruthText,
    AlignmentJob,
    AlignmentResult
)
from apps.taba_pipeline.executor import TABAPipelineExecutor
from core.models import Document, Transcription

User = get_user_model()


class GroundTruthCorpusModelTests(TestCase):
    """Test GroundTruthCorpus model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        
    def test_create_corpus(self):
        """Test creating a GT corpus"""
        corpus = GroundTruthCorpus.objects.create(
            name='Test Corpus',
            description='Test description',
            language='he',
            source_type='sefaria',
            owner=self.user
        )
        
        self.assertEqual(corpus.name, 'Test Corpus')
        self.assertEqual(corpus.language, 'he')
        self.assertEqual(corpus.text_count, 0)
        self.assertEqual(corpus.total_characters, 0)
        
    def test_corpus_statistics(self):
        """Test corpus statistics calculation"""
        corpus = GroundTruthCorpus.objects.create(
            name='Test Corpus',
            owner=self.user
        )
        
        # Add texts
        GroundTruthText.objects.create(
            corpus=corpus,
            title='Text 1',
            content='שלום עולם',
            character_count=10
        )
        GroundTruthText.objects.create(
            corpus=corpus,
            title='Text 2',
            content='בוקר טוב',
            character_count=8
        )
        
        # Check statistics
        self.assertEqual(corpus.text_count, 2)
        self.assertEqual(corpus.total_characters, 18)


class GroundTruthTextModelTests(TestCase):
    """Test GroundTruthText model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.corpus = GroundTruthCorpus.objects.create(
            name='Test Corpus',
            owner=self.user
        )
        
    def test_create_text(self):
        """Test creating a GT text"""
        text = GroundTruthText.objects.create(
            corpus=self.corpus,
            title='Genesis 1:1',
            filename='genesis_1_1.txt',
            content='בראשית ברא אלהים',
            language='he',
            character_count=17
        )
        
        self.assertEqual(text.title, 'Genesis 1:1')
        self.assertEqual(text.language, 'he')
        self.assertEqual(text.character_count, 17)
        
    def test_character_count_auto(self):
        """Test automatic character count"""
        text = GroundTruthText.objects.create(
            corpus=self.corpus,
            title='Test',
            content='שלום'
        )
        
        # Should auto-calculate
        self.assertEqual(text.character_count, 4)


class AlignmentJobModelTests(TestCase):
    """Test AlignmentJob model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.corpus = GroundTruthCorpus.objects.create(
            name='Test Corpus',
            owner=self.user
        )
        # Mock document and transcription would be needed
        
    def test_job_status_choices(self):
        """Test job status transitions"""
        # This would need actual Document/Transcription objects
        pass


class TABAPipelineExecutorTests(TestCase):
    """Test TABAPipelineExecutor"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.corpus = GroundTruthCorpus.objects.create(
            name='Test Corpus',
            owner=self.user
        )
        
    @patch('apps.taba_pipeline.executor.os.path.exists')
    @patch('apps.taba_pipeline.executor.subprocess.Popen')
    def test_validate_setup(self, mock_popen, mock_exists):
        """Test TABA setup validation"""
        # Mock TABA pipeline exists
        mock_exists.return_value = True
        
        # Create mock job
        job = MagicMock()
        job.pk = 1
        
        executor = TABAPipelineExecutor(job)
        executor.taba_path = '/fake/taba/path'
        
        valid, error = executor.validate_setup()
        
        self.assertTrue(valid)
        self.assertIsNone(error)
        
    def test_prepare_workspace(self):
        """Test workspace preparation"""
        job = MagicMock()
        job.pk = 1
        
        executor = TABAPipelineExecutor(job)
        
        with patch('apps.taba_pipeline.executor.os.makedirs'):
            paths = executor.prepare_workspace()
            
            self.assertIn('work', paths)
            self.assertIn('output', paths)
            self.assertIn('ocr', paths)
            self.assertIn('gt', paths)
            self.assertIn('results', paths)


class TABAViewTests(TestCase):
    """Test TABA views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='testuser', password='testpass')
        
    def test_dashboard_view(self):
        """Test TABA dashboard loads"""
        response = self.client.get(reverse('taba:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TABA Pipeline')
        
    def test_corpus_list_view(self):
        """Test corpus list view"""
        corpus = GroundTruthCorpus.objects.create(
            name='Test Corpus',
            owner=self.user
        )
        
        response = self.client.get(reverse('taba:corpus-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Corpus')
        
    def test_corpus_detail_view(self):
        """Test corpus detail view"""
        corpus = GroundTruthCorpus.objects.create(
            name='Test Corpus',
            owner=self.user
        )
        
        GroundTruthText.objects.create(
            corpus=corpus,
            title='Text 1',
            content='שלום'
        )
        
        response = self.client.get(
            reverse('taba:corpus-detail', kwargs={'pk': corpus.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Corpus')
        self.assertContains(response, 'Text 1')


class IntegrationTests(TestCase):
    """Integration tests for TABA pipeline"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        
    @patch('apps.taba_pipeline.executor.subprocess.Popen')
    def test_full_pipeline_flow(self, mock_popen):
        """Test complete TABA pipeline execution flow"""
        # Create corpus with texts
        corpus = GroundTruthCorpus.objects.create(
            name='Test Corpus',
            owner=self.user
        )
        
        GroundTruthText.objects.create(
            corpus=corpus,
            title='Test Text',
            content='שלום עולם',
            character_count=10
        )
        
        # Mock TABA execution
        mock_process = MagicMock()
        mock_process.stdout = iter(['Progress: 50%\n', 'Progress: 100%\n'])
        mock_process.stderr = iter([])
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Would need to create actual job and run executor
        # This is a skeleton for full integration test
        pass
