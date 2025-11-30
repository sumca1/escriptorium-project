"""
Django management command to test CERberus API
"""
from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from core.models import Document, Transcription
import json


User = get_user_model()


class Command(BaseCommand):
    help = 'Test CERberus API endpoints'

    def handle(self, *args, **options):
        self.stdout.write("\n🌐 CERberus API Tests\n")
        
        # Setup test data
        self.stdout.write("Setting up test data...")
        test_data = self.setup_test_data()
        
        if not test_data:
            return
        
        # Create client
        client = Client()
        
        # Run tests
        analysis_id = self.test_create_analysis(
            client,
            test_data['token'],
            test_data['gt_id'],
            test_data['hyp_id']
        )
        
        self.test_list_analyses(client, test_data['token'])
        self.test_get_analysis(client, test_data['token'], analysis_id)
        
        if analysis_id:
            self.test_confusion_matrix(client, test_data['token'], analysis_id)
            self.test_export_json(client, test_data['token'], analysis_id)
        
        self.stdout.write(self.style.SUCCESS("\n✅ API TESTS COMPLETED!\n"))

    def setup_test_data(self):
        """Create test user and transcriptions"""
        # Get or create user
        user, _ = User.objects.get_or_create(
            username='test_cer',
            defaults={'email': 'test_cer@example.com'}
        )
        if not user.password:
            user.set_password('testpass123')
            user.save()
        
        # Get or create token
        token, _ = Token.objects.get_or_create(user=user)
        
        # Use existing transcriptions from database
        gt_trans = Transcription.objects.first()
        hyp_trans = Transcription.objects.last()
        
        if not gt_trans or not hyp_trans:
            self.stdout.write(self.style.ERROR("❌ No transcriptions found in database!"))
            self.stdout.write("Please create some documents and transcriptions first.")
            return None
        
        self.stdout.write(f"✅ User: {user.username}")
        self.stdout.write(f"✅ Token: {token.key}")
        self.stdout.write(f"✅ GT Transcription ID: {gt_trans.id} ({gt_trans.name})")
        self.stdout.write(f"✅ Hyp Transcription ID: {hyp_trans.id} ({hyp_trans.name})\n")
        
        return {
            'user': user,
            'token': token.key,
            'gt_id': gt_trans.id,
            'hyp_id': hyp_trans.id
        }

    def test_create_analysis(self, client, token, gt_id, hyp_id):
        """Test POST /api/cerberus/analyses/"""
        self.stdout.write("=" * 60)
        self.stdout.write("Test 1: Create CER Analysis")
        self.stdout.write("=" * 60)
        
        response = client.post(
            '/api/cerberus/analyses/',
            data=json.dumps({
                'ground_truth_transcription_id': gt_id,
                'hypothesis_transcription_id': hyp_id,
                'ignore_case': False,
                'ignore_punctuation': False,
                'analyze_unicode_blocks': True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.stdout.write(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            self.stdout.write(self.style.SUCCESS(f"✅ Analysis created!"))
            self.stdout.write(f"  ID: {data.get('id')}")
            self.stdout.write(f"  CER: {data.get('cer_value')}%")
            self.stdout.write(f"  Accuracy: {data.get('accuracy')}%")
            self.stdout.write(f"  Total Characters: {data.get('total_characters')}\n")
            return data.get('id')
        else:
            self.stdout.write(self.style.ERROR(f"❌ Failed: {response.content.decode()}\n"))
            return None

    def test_list_analyses(self, client, token):
        """Test GET /api/cerberus/analyses/"""
        self.stdout.write("=" * 60)
        self.stdout.write("Test 2: List Analyses")
        self.stdout.write("=" * 60)
        
        response = client.get(
            '/api/cerberus/analyses/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.stdout.write(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            self.stdout.write(self.style.SUCCESS(f"✅ Found {len(results)} analyses"))
            for item in results[:3]:
                self.stdout.write(f"  - ID {item['id']}: CER {item['cer_value']}%")
            self.stdout.write("")
        else:
            self.stdout.write(self.style.ERROR(f"❌ Failed: {response.content.decode()}\n"))

    def test_get_analysis(self, client, token, analysis_id):
        """Test GET /api/cerberus/analyses/{id}/"""
        if not analysis_id:
            self.stdout.write("⏭️  Skipping test (no analysis ID)\n")
            return
        
        self.stdout.write("=" * 60)
        self.stdout.write("Test 3: Get Analysis Detail")
        self.stdout.write("=" * 60)
        
        response = client.get(
            f'/api/cerberus/analyses/{analysis_id}/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.stdout.write(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.stdout.write(self.style.SUCCESS(f"✅ Analysis {analysis_id}:"))
            self.stdout.write(f"  CER: {data.get('cer_value')}%")
            self.stdout.write(f"  Correct: {data.get('num_correct')}")
            self.stdout.write(f"  Substitutions: {data.get('num_substitutions')}")
            self.stdout.write(f"  Insertions: {data.get('num_insertions')}")
            self.stdout.write(f"  Deletions: {data.get('num_deletions')}")
            
            if data.get('character_statistics'):
                self.stdout.write(f"  Character Stats: {len(data['character_statistics'])} characters")
            if data.get('confusion_statistics'):
                self.stdout.write(f"  Confusion Stats: {len(data['confusion_statistics'])} confusions")
            self.stdout.write("")
        else:
            self.stdout.write(self.style.ERROR(f"❌ Failed: {response.content.decode()}\n"))

    def test_confusion_matrix(self, client, token, analysis_id):
        """Test GET /api/cerberus/analyses/{id}/confusion_matrix/"""
        self.stdout.write("=" * 60)
        self.stdout.write("Test 4: Confusion Matrix")
        self.stdout.write("=" * 60)
        
        response = client.get(
            f'/api/cerberus/analyses/{analysis_id}/confusion_matrix/?limit=10',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.stdout.write(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            confusions = data.get('confusions', [])
            self.stdout.write(self.style.SUCCESS(f"✅ Endpoint works! ({len(confusions)} confusions)\n"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Failed: {response.content.decode()}\n"))

    def test_export_json(self, client, token, analysis_id):
        """Test GET /api/cerberus/analyses/{id}/export/?format=json"""
        self.stdout.write("=" * 60)
        self.stdout.write("Test 5: Export JSON")
        self.stdout.write("=" * 60)
        
        response = client.get(
            f'/api/cerberus/analyses/{analysis_id}/export/?format=json',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.stdout.write(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS(f"✅ JSON export successful"))
            self.stdout.write(f"  Size: {len(response.content)} bytes\n")
        else:
            self.stdout.write(self.style.ERROR(f"❌ Failed: {response.content.decode()}\n"))
