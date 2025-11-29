import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Participant, Organizer 
from django.contrib.messages import get_messages

# Helper function untuk mengekstrak pesan
def get_messages_list(response):
    """Mengekstrak pesan dari response."""
    return [str(m) for m in get_messages(response.wsgi_request)]

class AuthenticateViewsTest(TestCase):

    def setUp(self):
        """Setup awal untuk semua tes."""
        self.client = Client()
        
        # Buat user yang sudah ada untuk tes login dan tes "username exists"
        self.existing_user = User.objects.create_user(
            username='existinguser',
            password='testpassword123'
        )
        
        # URLs
        self.login_url = reverse('Authenticate:login')
        self.logout_url = reverse('Authenticate:logout')
        self.role_select_url = reverse('Authenticate:register_role_selection')
        self.p_step1_url = reverse('Authenticate:register_participant_step1')
        self.p_step2_url = reverse('Authenticate:register_participant_step2')
        self.o_step1_url = reverse('Authenticate:register_organizer_step1')
        self.o_step2_url = reverse('Authenticate:register_organizer_step2')
        
        try:
            self.homepage_url = reverse('Homepage:show_main')
        except:
            self.homepage_url = '/' 

        # --- Data untuk POST requests ---
        
        # Data untuk AuthStep1Form
        self.step1_data_valid = {
            'username': 'newuser',
            'password_1': 'StrongP@ss123',
            'password_2': 'StrongP@ss123'
        }
        self.step1_data_mismatch = {
            'username': 'newuser',
            'password_1': 'StrongP@ss123',
            'password_2': 'WrongP@ss123'
        }
        self.step1_data_existing = {
            'username': 'existinguser', # Username ini sudah ada
            'password_1': 'StrongP@ss123',
            'password_2': 'StrongP@ss123'
        }
        
        
        # Data untuk ParticipantStep2Form
        self.p_step2_data_valid = {
            'full_name': 'New Participant',
            'email': 'participant@example.com' ,
            'location': 'Jakarta, Indonesia', 
            'username': 'newuser',             
            'password': 'StrongP@ss123',
            # Tambahkan field lain yang wajib untuk model Participant di sini
        }
        
        # Data untuk OrganizerStep2Form
        self.o_step2_data_valid = {
            'organizer_name': 'New Organizer',
            'phone_number': '08123456789', 
            'username': 'newuser',            
            'password': 'StrongP@ss123'
            # Tambahkan field lain yang wajib untuk model Organizer di sini
        }
        # --- Selesai Data ---

    # === Tes log_in ===
    
    def test_login_get(self):
        """Tes halaman login (GET)"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_post_success(self):
        """Tes login (POST) berhasil"""
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302) # Redirect
        self.assertRedirects(response, self.homepage_url)
        self.assertIn('_auth_user_id', self.client.session) # Cek session
        self.assertEqual(self.client.session['_auth_user_id'], str(self.existing_user.id))
        self.assertIn('last_login', response.cookies) # Cek cookie

    def test_login_post_fail(self):
        """Tes login (POST) gagal (password salah)"""
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200) # Render ulang
        self.assertTemplateUsed(response, 'login.html')
        self.assertNotIn('_auth_user_id', self.client.session)
        messages = get_messages_list(response)
        self.assertIn('Username atau password salah. Silakan coba lagi.', messages)

    # === Tes log_out ===
    
    def test_logout(self):
        """Tes logout"""
        # Login dulu
        self.client.login(username='existinguser', password='testpassword123')
        self.assertIn('_auth_user_id', self.client.session)
        
        # Logout
        response = self.client.get(self.logout_url) # GET atau POST bisa karena @csrf_exempt
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.homepage_url)
        self.assertNotIn('_auth_user_id', self.client.session)
        # Cek cookie dihapus (max-age=0)
        self.assertEqual(response.cookies['last_login']['max-age'], 0)

    # === Tes register_role_selection ===
    
    def test_role_selection_get(self):
        """Tes halaman pemilihan role (GET)"""
        response = self.client.get(self.role_select_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
    
    def test_role_selection_post_participant(self):
        """Tes pemilihan role (POST) sebagai participant"""
        response = self.client.post(self.role_select_url, {'role': 'participant'})
        self.assertRedirects(response, self.p_step1_url)

    def test_role_selection_post_organizer(self):
        """Tes pemilihan role (POST) sebagai organizer"""
        response = self.client.post(self.role_select_url, {'role': 'organizer'})
        self.assertRedirects(response, self.o_step1_url)

    def test_role_selection_post_invalid(self):
        """Tes pemilihan role (POST) tidak valid"""
        response = self.client.post(self.role_select_url, {'role': 'invalid_role'})
        self.assertEqual(response.status_code, 200) # Render ulang
        self.assertTemplateUsed(response, 'register.html')
        messages = get_messages_list(response)
        self.assertIn('Silakan pilih role yang valid.', messages)

    # === Tes Alur Registrasi Participant ===
    
    def test_p_step1_get(self):
        """Tes halaman registrasi participant step 1 (GET)"""
        response = self.client.get(self.p_step1_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_participant_step1.html')

    def test_p_step1_post_success(self):
        """Tes registrasi participant step 1 (POST) berhasil"""
        response = self.client.post(self.p_step1_url, self.step1_data_valid)
        self.assertRedirects(response, self.p_step2_url)
        self.assertIn('participant_step1_data', self.client.session)
        self.assertEqual(self.client.session['participant_step1_data']['username'], 'newuser')

    def test_p_step1_post_user_exists(self):
        """Tes registrasi participant step 1 (POST) gagal (username sudah ada)"""
        response = self.client.post(self.p_step1_url, self.step1_data_existing)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_participant_step1.html')
        messages = get_messages_list(response)
        self.assertIn('Username sudah ada. Silahkan gunakan username lain.', messages)
        self.assertNotIn('participant_step1_data', self.client.session)

    def test_p_step1_post_invalid_form(self):
        """Tes registrasi participant step 1 (POST) gagal (form tidak valid)"""
        response = self.client.post(self.p_step1_url, self.step1_data_mismatch)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_participant_step1.html')
        self.assertNotIn('participant_step1_data', self.client.session)

    def test_p_step2_get_no_session(self):
        """Tes halaman registrasi participant step 2 (GET) tanpa sesi"""
        response = self.client.get(self.p_step2_url)
        self.assertRedirects(response, self.p_step1_url)

    def test_p_step2_get_with_session(self):
        """Tes halaman registrasi participant step 2 (GET) dengan sesi"""
        session = self.client.session
        session['participant_step1_data'] = self.step1_data_valid
        session.save()
        
        response = self.client.get(self.p_step2_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_participant_step2.html')

    def test_p_step2_post_success(self):
        """Tes registrasi participant step 2 (POST) berhasil"""
        session = self.client.session
        session['participant_step1_data'] = self.step1_data_valid
        session.save()
        
        user_count_before = User.objects.count()
        participant_count_before = Participant.objects.count()

        response = self.client.post(self.p_step2_url, self.p_step2_data_valid)

        self.assertRedirects(response, self.login_url)
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertEqual(Participant.objects.count(), participant_count_before + 1)
        
        # Verifikasi user dan participant dibuat
        new_user = User.objects.get(username='newuser')
        new_participant = Participant.objects.get(user=new_user)
        self.assertIsNotNone(new_participant)
        
        self.assertNotIn('participant_step1_data', self.client.session) # Sesi dihapus
        messages = get_messages_list(response)
        self.assertIn('Akun berhasil dibuat! Silahkan login.', messages)

    def test_p_step2_post_invalid_form(self):
        """Tes registrasi participant step 2 (POST) gagal (form tidak valid)"""
        session = self.client.session
        session['participant_step1_data'] = self.step1_data_valid
        session.save()

        # Asumsikan 'email' wajib ada
        invalid_data = self.p_step2_data_valid.copy()
        invalid_data['email'] = 'bukan-email' # Data tidak valid
        
        response = self.client.post(self.p_step2_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_participant_step2.html')
        self.assertIn('participant_step1_data', self.client.session) # Sesi tidak dihapus

    def test_p_step2_post_no_session(self):
        """Tes registrasi participant step 2 (POST) gagal (tidak ada sesi)"""
        response = self.client.post(self.p_step2_url, self.p_step2_data_valid)
        self.assertRedirects(response, self.p_step1_url)

    # === Tes Alur Registrasi Organizer ===
    # (Tes ini identik dengan participant, hanya beda URL, key session, dan template)

    def test_o_step1_get(self):
        """Tes halaman registrasi organizer step 1 (GET)"""
        response = self.client.get(self.o_step1_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_organizer_step1.html')

    def test_o_step1_post_success(self):
        """Tes registrasi organizer step 1 (POST) berhasil"""
        response = self.client.post(self.o_step1_url, self.step1_data_valid)
        self.assertRedirects(response, self.o_step2_url)
        self.assertIn('organizer_step1_data', self.client.session)
        self.assertEqual(self.client.session['organizer_step1_data']['username'], 'newuser')

    def test_o_step1_post_user_exists(self):
        """Tes registrasi organizer step 1 (POST) gagal (username sudah ada)"""
        response = self.client.post(self.o_step1_url, self.step1_data_existing)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_organizer_step1.html')
        messages = get_messages_list(response)
        self.assertIn('Username sudah ada. Silahkan gunakan username lain.', messages)
        self.assertNotIn('organizer_step1_data', self.client.session)

    def test_o_step1_post_invalid_form(self):
        """Tes registrasi organizer step 1 (POST) gagal (form tidak valid)"""
        response = self.client.post(self.o_step1_url, self.step1_data_mismatch)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_organizer_step1.html')
        self.assertNotIn('organizer_step1_data', self.client.session)

    def test_o_step2_get_no_session(self):
        """Tes halaman registrasi organizer step 2 (GET) tanpa sesi"""
        response = self.client.get(self.o_step2_url)
        self.assertRedirects(response, self.o_step1_url)

    def test_o_step2_get_with_session(self):
        """Tes halaman registrasi organizer step 2 (GET) dengan sesi"""
        session = self.client.session
        session['organizer_step1_data'] = self.step1_data_valid
        session.save()
        
        response = self.client.get(self.o_step2_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_organizer_step2.html')

    def test_o_step2_post_success(self):
        """Tes registrasi organizer step 2 (POST) berhasil"""
        session = self.client.session
        session['organizer_step1_data'] = self.step1_data_valid
        session.save()
        
        user_count_before = User.objects.count()
        organizer_count_before = Organizer.objects.count()

        response = self.client.post(self.o_step2_url, self.o_step2_data_valid)

        self.assertRedirects(response, self.login_url)
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertEqual(Organizer.objects.count(), organizer_count_before + 1)
        
        new_user = User.objects.get(username='newuser')
        new_organizer = Organizer.objects.get(user=new_user)
        self.assertIsNotNone(new_organizer)
        
        self.assertNotIn('organizer_step1_data', self.client.session)
        messages = get_messages_list(response)
        self.assertIn('Akun berhasil dibuat! Silahkan login.', messages)

    def test_o_step2_post_invalid_form(self):
        """Tes registrasi organizer step 2 (POST) gagal (form tidak valid)"""
        session = self.client.session
        session['organizer_step1_data'] = self.step1_data_valid
        session.save()

        # Asumsikan 'organizer_name' wajib ada
        invalid_data = self.o_step2_data_valid.copy()
        del invalid_data['organizer_name'] # Hapus data wajib
        
        response = self.client.post(self.o_step2_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_organizer_step2.html')
        self.assertIn('organizer_step1_data', self.client.session)

    def test_o_step2_post_no_session(self):
        """Tes registrasi organizer step 2 (POST) gagal (tidak ada sesi)"""
        response = self.client.post(self.o_step2_url, self.o_step2_data_valid)
        self.assertRedirects(response, self.o_step1_url)
