import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Participant, Organizer

class AuthenticationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_role_url = reverse('Authenticate:register_role_selection')
        self.register_url = reverse('Authenticate:register')
        self.login_url = reverse('Authenticate:login') 
        self.logout_url = reverse('Authenticate:logout')
        
        self.login_api_url = reverse('Authenticate:login_api')
        self.register_api_url = reverse('Authenticate:register_api')
        self.logout_api_url = reverse('Authenticate:logout_api')

        self.password = 'password123'
        self.user = User.objects.create_user(username='testuser', password=self.password)
        
        Participant.objects.create(user=self.user, full_name='Test Participant', username='testuser', password=self.password)

    def test_register_role_selection_get(self):
        """Test GET halaman role selection"""
        response = self.client.get(self.register_role_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_role_selection.html')

    def test_register_role_selection_post_valid(self):
        """Test POST role valid menyimpan session dan redirect"""
        response = self.client.post(self.register_role_url, {'role': 'participant'})
        self.assertRedirects(response, self.register_url)
        self.assertEqual(self.client.session['registration_role'], 'participant')

    def test_register_role_selection_post_invalid(self):
        """Test POST role tidak valid menampilkan error"""
        response = self.client.post(self.register_role_url, {'role': 'alien'})
        self.assertEqual(response.status_code, 200) # Tetap di halaman sama
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), "Pilih role yang valid.")

    def test_register_view_no_session(self):
        """Test akses register tanpa session role melempar balik"""
        response = self.client.get(self.register_url)
        self.assertRedirects(response, self.register_role_url)

    def test_register_view_success(self):
        """Test register web sukses"""
        session = self.client.session
        session['registration_role'] = 'participant'
        session.save()

        response = self.client.post(self.register_url, {
            'username': 'webuser',
            'email': 'web@test.com',
            'password_1': 'pass123',
            'password_2': 'pass123'
        })
        self.assertRedirects(response, self.login_url)
        self.assertTrue(User.objects.filter(username='webuser').exists())

    def test_register_view_duplicate(self):
        """Test register web username kembar"""
        session = self.client.session
        session['registration_role'] = 'participant'
        session.save()

        response = self.client.post(self.register_url, {
            'username': 'testuser', 
            'password_1': 'pass123',
        })
        messages = list(response.context['messages'])
        self.assertTrue(any("Form tidak valid." in str(m) for m in messages))

    def test_register_view_invalid_form(self):
        """Test register web form tidak valid"""
        session = self.client.session
        session['registration_role'] = 'participant'
        session.save()

        response = self.client.post(self.register_url, {}) # Data kosong
        messages = list(response.context['messages'])
        self.assertTrue(any("Form tidak valid" in str(m) for m in messages))

    def test_login_view_success(self):
        """Test login web sukses"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': self.password
        })
        self.assertRedirects(response, reverse("Homepage:show_main"))
        self.assertIn('last_login', response.cookies)

    def test_login_view_fail(self):
        """Test login web gagal"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Username atau password salah" in str(m) for m in messages))

    def test_logout_view(self):
        """Test logout web"""
        self.client.login(username='testuser', password=self.password)
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse("Homepage:show_main"))
        
        self.assertEqual(response.cookies['last_login'].value, '')

    def test_login_api_success_participant(self):
        """
        Test API Login Sukses (Role Participant).
        PENTING: View menggunakan request.POST, jadi client.post default (form data).
        """
        response = self.client.post(self.login_api_url, {
            'username': 'testuser',
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['status'])
        self.assertEqual(data['role'], 'participant')
        self.assertTrue(data['profile_exists'])

    def test_login_api_success_organizer(self):
        """Test API Login Sukses (Role Organizer)"""
        # Create organizer user
        org_user = User.objects.create_user(username='orguser', password='password')
        Organizer.objects.create(user=org_user, organizer_name='Org Test', username='orguser', password='password')

        response = self.client.post(self.login_api_url, {
            'username': 'orguser',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['role'], 'organizer')

    def test_login_api_missing_fields(self):
        """Test login api tanpa username/pass"""
        response = self.client.post(self.login_api_url, {})
        self.assertEqual(response.status_code, 400)

    def test_login_api_inactive_user(self):
        """Test login api user yang tidak aktif (is_active=False)"""
        inactive_user = User.objects.create_user(username='inactive', password='password')
        inactive_user.is_active = False
        inactive_user.save()

        response = self.client.post(self.login_api_url, {
            'username': 'inactive',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 403) # View returns 403 on failure

    def test_login_api_wrong_credentials(self):
        """Test login api password salah"""
        response = self.client.post(self.login_api_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 403)

    def test_login_api_invalid_method(self):
        """Test login api method GET"""
        response = self.client.get(self.login_api_url)
        self.assertEqual(response.status_code, 400)

    def test_register_api_success(self):
        """
        Test API Register Sukses.
        PENTING: View menggunakan json.loads, jadi harus content_type='application/json'.
        """
        payload = {
            'username': 'apiuser',
            'password': 'apipassword',
            'email': 'api@test.com'
        }
        response = self.client.post(
            self.register_api_url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='apiuser').exists())

    def test_register_api_missing_fields(self):
        """Test API register field kurang"""
        payload = {'username': 'failuser'} # No password
        response = self.client.post(
            self.register_api_url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_register_api_duplicate(self):
        """Test API register username kembar"""
        payload = {'username': 'testuser', 'password': '123'}
        response = self.client.post(
            self.register_api_url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['message'], "Username already exists.")

    def test_register_api_invalid_json(self):
        """Test API register kirim string bukan JSON"""
        response = self.client.post(
            self.register_api_url, 
            data="Not a JSON", 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['message'], "Invalid JSON format.")

    def test_register_api_invalid_method(self):
        """Test API register method GET"""
        response = self.client.get(self.register_api_url)
        self.assertEqual(response.status_code, 400)

    def test_logout_api_success(self):
        """Test logout API sukses"""
        self.client.login(username='testuser', password=self.password)
        response = self.client.post(self.logout_api_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['status'])

    def test_logout_api_unauthenticated(self):
        """Test logout API tanpa login"""
        response = self.client.post(self.logout_api_url)
        self.assertEqual(response.status_code, 401)

    def test_logout_api_invalid_method(self):
        """Test logout API method GET"""
        response = self.client.get(self.logout_api_url)
        self.assertEqual(response.status_code, 405)