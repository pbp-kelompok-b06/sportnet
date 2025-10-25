import json
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import serializers

from Event.models import Event
from Authenticate.models import Organizer, Participant


class ProfileViewsTest(TestCase):

    def setUp(self):
        """Setup data dummy untuk semua tes."""
        self.client = Client()
        self.now = timezone.now()
        

        self.dummy_image = SimpleUploadedFile(
            name='test_pic.jpg',
            content=b'file_content', # Isi file (bisa apa saja)
            content_type='image/jpeg'
        )

        self.part_user = User.objects.create_user('participant1', 'part@test.com', 'pass')
        self.part_profile = Participant.objects.create(
            user=self.part_user, 
            full_name='Test Participant', 
            location='Test Location',
            profile_picture=self.dummy_image
        )

        # Organizer (tidak punya profile pic)
        self.org_user = User.objects.create_user('organizer1', 'org@test.com', 'pass')
        self.org_profile = Organizer.objects.create(
            user=self.org_user, 
            organizer_name='Test Organizer'
        )
        
        # User biasa (tidak punya profile)
        self.reg_user = User.objects.create_user('regularuser', 'reg@test.com', 'pass')


        self.past_event = Event.objects.create(
            organizer=self.org_profile,
            name='Event Lampau',
            description='Event yang sudah lewat',
            start_time=self.now - timedelta(days=5),
            location='Lokasi Lampau',
            sports_category='running',
            activity_category='fun_run_ride'
        )
        self.upcoming_event = Event.objects.create(
            organizer=self.org_profile,
            name='Event Akan Datang',
            description='Event yang akan datang',
            start_time=self.now + timedelta(days=5),
            location='Lokasi Akan Datang',
            sports_category='yoga',
            activity_category='workshop'
        )
        # Daftarkan participant ke kedua event
        self.part_profile.events_joined.add(self.past_event, self.upcoming_event)


        self.profile_view_own_url = reverse('profile:profile_view') 
        
        # URL untuk /profile/<username>/ (lihat profil orang lain)
        self.profile_view_other_url = reverse('profile:profile_view_user', args=[self.org_user.username]) 
        self.profile_view_404_url = reverse('profile:profile_view_user', args=['usernametidakada']) 
        
        # Sisa URL lainnya
        self.edit_url = reverse('profile:edit_profile')
        self.delete_pic_url = reverse('profile:delete_Profilepict')
        
        self.xml_org_url = reverse('profile:show_xml_Organizer')
        self.xml_part_url = reverse('profile:show_xml_Participant')
        
        # URL JSON yang tertukar (sesuai urls.py kamu)
        self.json_org_url_bug = reverse('profile:show_json_Organizer') 
        self.json_part_url_bug = reverse('profile:show_json_Participant')

        # 5. Redirect URLs
        self.login_url = '/authenticate' 
        self.homepage_url = reverse('Homepage:show_main') 

        # 6. Data untuk POST Form Edit
        self.valid_participant_data = {
            'full_name': 'Participant Updated',
            'location': 'Lokasi Baru',
            'about': 'Tentang saya update.'
        }
        self.valid_organizer_data = {
            'organizer_name': 'Organizer Updated',
            'contact_email': 'org@updated.com',
            'about': 'Tentang org update.'
        }

    # --- Tes untuk profile_view ---

    def test_profile_view_own_not_logged_in(self):
        """Tes: GET /profile/ (lihat profil sendiri, tapi belum login) -> redirect"""
        response = self.client.get(self.profile_view_own_url)
        self.assertEqual(response.status_code, 302)
        # Tes redirect ke URL hardcoded di decorator
        self.assertRedirects(response, f'{self.login_url}?next={self.profile_view_own_url}')

    def test_profile_view_other_username_exists(self):
        """Tes: GET /profile/organizer1/ (lihat profil org lain) -> OK"""
        # Login sebagai participant
        self.client.login(username='participant1', password='pass')
        response = self.client.get(self.profile_view_other_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertIn('organizer', response.context) # Cek konteks organizer
        self.assertEqual(response.context['organizer'], self.org_profile)
        self.assertNotIn('participant', response.context)

    def test_profile_view_own_participant_with_events(self):
        """Tes: GET /profile/ (lihat profil sendiri, sbg participant) -> OK"""
        self.client.login(username='participant1', password='pass')
        response = self.client.get(self.profile_view_own_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertIn('participant', response.context)
        self.assertEqual(response.context['participant'], self.part_profile)
        
        # Cek pemisahan event
        self.assertIn(self.upcoming_event, response.context['upcoming_events'])
        self.assertNotIn(self.past_event, response.context['upcoming_events'])
        self.assertIn(self.past_event, response.context['past_events'])
        self.assertNotIn(self.upcoming_event, response.context['past_events'])

    def test_profile_view_username_not_found(self):
        """Tes: GET /profile/usernametidakada/ -> 404"""
        self.client.login(username='participant1', password='pass')
        response = self.client.get(self.profile_view_404_url)
        self.assertEqual(response.status_code, 404)

    def test_profile_view_user_with_no_profile(self):
        """Tes: GET /profile/regularuser/ (user ada tapi profil tidak) -> redirect"""
        self.client.login(username='regularuser', password='pass')
        # Coba lihat profil orang lain (regularuser)
        response = self.client.get(reverse('profile:profile_view_user', args=[self.reg_user.username]))
        
        # Harus redirect ke homepage
        self.assertRedirects(response, self.homepage_url)
        
        # Cek message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Profil tidak ditemukan.')

    # --- Tes untuk edit_profile ---

    def test_edit_profile_get_not_logged_in(self):
        """Tes: GET /edit-profile/ (belum login) -> redirect"""
        response = self.client.get(self.edit_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.edit_url}')

    def test_edit_profile_get_participant(self):
        """Tes: GET /edit-profile/ (sbg participant) -> OK"""
        self.client.login(username='participant1', password='pass')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        self.assertIn('form', response.context)
        # Cek bahwa form yang dipakai adalah ProfileFormParticipant
        self.assertEqual(response.context['form'].instance, self.part_profile)

    def test_edit_profile_get_organizer(self):
        """Tes: GET /edit-profile/ (sbg organizer) -> OK"""
        self.client.login(username='organizer1', password='pass')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.org_profile)
    
    def test_edit_profile_get_no_profile(self):
        """Tes: GET /edit-profile/ (sbg user biasa) -> redirect"""
        self.client.login(username='regularuser', password='pass')
        response = self.client.get(self.edit_url)
        self.assertRedirects(response, self.homepage_url)

    def test_edit_profile_post_participant_valid(self):
        """Tes: POST /edit-profile/ (sbg participant, data valid) -> redirect"""
        self.client.login(username='participant1', password='pass')
        response = self.client.post(self.edit_url, self.valid_participant_data)
        
        self.assertRedirects(response, self.profile_view_own_url)
        self.part_profile.refresh_from_db()
        self.assertEqual(self.part_profile.full_name, 'Participant Updated')
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Profile berhasil diperbarui!')
        
    def test_edit_profile_post_organizer_invalid(self):
        """Tes: POST /edit-profile/ (sbg organizer, data invalid) -> re-render"""
        self.client.login(username='organizer1', password='pass')
        invalid_data = self.valid_organizer_data.copy()
        invalid_data['organizer_name'] = '' # Wajib diisi
        
        response = self.client.post(self.edit_url, invalid_data)
        self.assertEqual(response.status_code, 200) # Re-render
        self.assertTrue(response.context['form'].errors) # Ada error di form
        
        self.org_profile.refresh_from_db()
        self.assertNotEqual(self.org_profile.organizer_name, '') # Data tdk berubah

    # --- Tes untuk delete_Profilepict ---

    def test_delete_pic_get_request(self):
        """Tes: GET /delete-picture/ -> redirect"""
        self.client.login(username='participant1', password='pass')
        response = self.client.get(self.delete_pic_url)
        self.assertRedirects(response, self.edit_url)

    def test_delete_pic_participant_with_pic(self):
        """Tes: POST /delete-picture/ (participant punya pic) -> OK"""
        self.client.login(username='participant1', password='pass')
        
        # Pastikan pic ada
        self.assertTrue(self.part_profile.profile_picture)
        
        response = self.client.post(self.delete_pic_url)
        self.assertRedirects(response, self.edit_url)
        
        self.part_profile.refresh_from_db()
        self.assertFalse(self.part_profile.profile_picture) # Pic sudah kehapus
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Foto profil berhasil dihapus.')

    def test_delete_pic_organizer_no_pic(self):
        """Tes: POST /delete-picture/ (organizer tidak punya pic) -> OK"""
        self.client.login(username='organizer1', password='pass')
        
        self.assertFalse(self.org_profile.profile_picture) # Pastikan pic tdk ada
        
        response = self.client.post(self.delete_pic_url)
        self.assertRedirects(response, self.edit_url)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Tidak ada foto profil untuk dihapus.')
        
    # --- Tes untuk XML/JSON Views ---

    def test_show_xml_organizer(self):
        """Tes: GET /xml/Organizer/ -> OK"""
        response = self.client.get(self.xml_org_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        # Cek isi, pastikan modelnya benar
        self.assertContains(response, "<model>Authenticate.organizer</model>")

    def test_show_xml_participant(self):
        """Tes: GET /xml/Participant/ -> OK"""
        response = self.client.get(self.xml_part_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        self.assertContains(response, "<model>Authenticate.participant</model>")

    def test_show_json_organizer_url_shows_participant_data_bug(self):
        """Tes: GET /json/Organizer/ -> (BUG: Menampilkan data Participant)"""
        response = self.client.get(self.json_org_url_bug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertEqual(data[0]['model'], 'Authenticate.participant')

    def test_show_json_participant_url_shows_organizer_data_bug(self):
        """Tes: GET /json/Participant/ -> (BUG: Menampilkan data Organizer)"""
        response = self.client.get(self.json_part_url_bug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertEqual(data[0]['model'], 'Authenticate.organizer')