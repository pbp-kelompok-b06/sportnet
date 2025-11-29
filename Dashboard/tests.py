import json
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# --- Import Model yang Dibutuhkan ---
# Kita butuh model dari 3 app berbeda
from Event.models import Event
from Authenticate.models import Organizer, Participant

# Tes ini akan mencoba mengimpor model Notifikasi.
# Jika tidak ada, tes akan tetap jalan, tapi bagian notif di-skip.
try:
    from Notification.models import Notifications as Notif
    NOTIF_APP_AVAILABLE = True
except ImportError:
    NOTIF_APP_AVAILABLE = False


class DashboardViewsTest(TestCase):

    def setUp(self):
        """Setup data dummy untuk semua tes."""
        self.client = Client()
        self.now = timezone.now()

        # 1. Buat User & Profile Organizer (yang login)
        self.organizer_user = User.objects.create_user(
            username='organizer1',
            password='testpassword123'
        )
        # Asumsi Organizer HANYA butuh user & organizer_name
        self.organizer_profile = Organizer.objects.create(
            user=self.organizer_user,
            organizer_name='Event Organizer 1'
        )

        # 2. Buat User & Profile Organizer LAIN (untuk tes permission)
        self.other_organizer_user = User.objects.create_user(
            username='organizer2',
            password='testpassword123'
        )
        self.other_organizer_profile = Organizer.objects.create(
            user=self.other_organizer_user,
            organizer_name='Event Organizer 2'
        )

        # 3. Buat User & Profile Participant (untuk jadi attendee)
        self.participant_user = User.objects.create_user(
            username='participant1',
            password='testpassword123'
        )
        # Asumsi Participant HANYA butuh user, full_name, dan location
        self.participant_profile = Participant.objects.create(
            user=self.participant_user,
            full_name='Test Participant',
            location='Test Location'
        )

        # 4. Buat Events
        # Event 1: Punya attendee, fee, dan end_time
        self.event1_by_org1 = Event.objects.create(
            organizer=self.organizer_profile,
            name='Event 1 (Ada Attendee)',
            description='Deskripsi Event 1',
            start_time=self.now + timedelta(days=5),
            end_time=self.now + timedelta(days=5, hours=3),
            location='Lokasi Event 1',
            sports_category='running',
            activity_category='fun_run_ride',
            fee=50000
        )
        self.event1_by_org1.attendee.add(self.participant_profile)

        # Event 2: Tidak punya attendee, fee=None, end_time=None
        self.event2_by_org1 = Event.objects.create(
            organizer=self.organizer_profile,
            name='Event 2 (Kosong)',
            description='Deskripsi Event 2',
            start_time=self.now + timedelta(days=10),
            end_time=None, # Test case untuk end_time=None
            location='Lokasi Event 2',
            sports_category='yoga',
            activity_category='workshop',
            fee=None # Test case untuk fee=None
        )

        # Event 3: Milik organizer LAIN
        self.event3_by_org2 = Event.objects.create(
            organizer=self.other_organizer_profile,
            name='Event 3 (Bukan Milikku)',
            description='Deskripsi Event 3',
            start_time=self.now + timedelta(days=7),
            location='Lokasi Event 3',
            sports_category='padel',
            activity_category='tournament'
        )

        # 5. Definisikan URLs
        self.show_url = reverse('dashboard:show')
        self.get_json_url = reverse('dashboard:get_organizer_events_json')
        
        # URL Delete
        self.delete_url_event1 = reverse(
            'dashboard:delete_event', args=[self.event1_by_org1.id]
        )
        self.delete_url_event2 = reverse(
            'dashboard:delete_event', args=[self.event2_by_org1.id]
        )
        self.delete_url_event3_other = reverse( # Event milik org lain
            'dashboard:delete_event', args=[self.event3_by_org2.id]
        )
        self.delete_url_invalid = reverse( # Event tidak ada
            'dashboard:delete_event', args=[uuid.uuid4()]
        )

        # URL Redirect
        self.login_url = '/authenticate/' # Sesuai login_url di view
        self.homepage_url = reverse('Homepage:show_main') 

    # --- Tes untuk view show ---

    def test_show_not_logged_in(self):
        """Tes: GET /dashboard/ (belum login) -> redirect ke login"""
        response = self.client.get(self.show_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.login_url}?next={self.show_url}')

    def test_show_logged_in_as_participant(self):
        """Tes: GET /dashboard/ (login sbg participant) -> redirect ke homepage"""
        self.client.login(username='participant1', password='testpassword123')
        response = self.client.get(self.show_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.homepage_url)

    def test_show_logged_in_as_organizer(self):
        """Tes: GET /dashboard/ (login sbg organizer) -> OK"""
        self.client.login(username='organizer1', password='testpassword123')
        response = self.client.get(self.show_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    # --- Tes untuk view get_organizer_events_json ---

    def test_get_json_not_logged_in(self):
        """Tes: GET /dashboard/get-events/ (belum login) -> redirect"""
        response = self.client.get(self.get_json_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.login_url}?next={self.get_json_url}')

    def test_get_json_as_participant(self):
        """Tes: GET /dashboard/get-events/ (login sbg participant) -> error 500"""
        self.client.login(username='participant1', password='testpassword123')
        response = self.client.get(self.get_json_url)
        # View akan error 500 karena `request.user.organizer_profile` gagal
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['events'], [])
        self.assertIn('error', response.json())

    def test_get_json_as_organizer(self):
        """Tes: GET /dashboard/get-events/ (login sbg organizer) -> OK"""
        self.client.login(username='organizer1', password='testpassword123')
        response = self.client.get(self.get_json_url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('events', data)
        self.assertEqual(len(data['events']), 2) # Org 1 punya 2 event

        # Cek event 2 (yang fee=None dan end_time=None)
        # Event 2 muncul duluan karena di-order by '-start_time'
        event2_data = data['events'][0] 
        self.assertEqual(event2_data['id'], str(self.event2_by_org1.id))
        self.assertEqual(event2_data['fee'], 'Free')
        self.assertIsNone(event2_data['end_time'])
        self.assertEqual(event2_data['attendee_count'], 0)
        
        # Cek event 1 (yang lengkap)
        event1_data = data['events'][1]
        self.assertEqual(event1_data['id'], str(self.event1_by_org1.id))
        self.assertEqual(event1_data['fee'], '50000')
        self.assertIsNotNone(event1_data['end_time'])
        self.assertEqual(event1_data['attendee_count'], 1)

    # --- Tes untuk view delete_event ---

    def test_delete_event_not_logged_in(self):
        """Tes: POST /dashboard/delete/... (belum login) -> redirect"""
        response = self.client.post(self.delete_url_event1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.login_url}?next={self.delete_url_event1}')

    def test_delete_event_get_method(self):
        """Tes: GET /dashboard/delete/... (method salah) -> error 400"""
        self.client.login(username='organizer1', password='testpassword123')
        response = self.client.get(self.delete_url_event1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')

    def test_delete_event_not_found(self):
        """Tes: POST /dashboard/delete/... (event_id salah) -> error 404"""
        self.client.login(username='organizer1', password='testpassword123')
        response = self.client.post(self.delete_url_invalid)
        self.assertEqual(response.status_code, 404) # get_object_or_404

    def test_delete_event_not_owner(self):
        """Tes: POST /dashboard/delete/... (bukan pemilik) -> error 403"""
        self.client.login(username='organizer1', password='testpassword123')
        # Coba hapus event 3 (milik organizer2)
        event_count_before = Event.objects.count()
        response = self.client.post(self.delete_url_event3_other)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['status'], 'error')
        self.assertIn('izin', response.json()['message'])
        # Pastikan event tidak terhapus
        self.assertEqual(Event.objects.count(), event_count_before)

    def test_delete_event_success_no_attendee(self):
        """Tes: POST /dashboard/delete/... (sukses, tidak ada attendee)"""
        self.client.login(username='organizer1', password='testpassword123')
        
        # Hapus event 2 (tidak ada attendee)
        event_id = self.event2_by_org1.id
        self.assertTrue(Event.objects.filter(id=event_id).exists())
        notif_count_before = Notif.objects.count() if NOTIF_APP_AVAILABLE else 0

        response = self.client.post(self.delete_url_event2)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        # Pastikan event terhapus
        self.assertFalse(Event.objects.filter(id=event_id).exists())
        # Pastikan tidak ada notif baru
        if NOTIF_APP_AVAILABLE:
            self.assertEqual(Notif.objects.count(), notif_count_before)

    def test_delete_event_success_with_attendee_and_notif(self):
        """Tes: POST /dashboard/delete/... (sukses, kirim notif ke attendee)"""
        
        # Skip tes ini jika app Notifikasi tidak terinstall
        if not NOTIF_APP_AVAILABLE:
            self.skipTest("Aplikasi Notifikasi (Notification) tidak ditemukan.")

        self.client.login(username='organizer1', password='testpassword123')

        # Hapus event 1 (ada 1 attendee)
        event_id = self.event1_by_org1.id
        self.assertTrue(Event.objects.filter(id=event_id).exists())
        notif_count_before = Notif.objects.count()

        response = self.client.post(self.delete_url_event1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        # Pastikan event terhapus
        self.assertFalse(Event.objects.filter(id=event_id).exists())
        
        # --- Cek Notifikasi ---
        notif_count_after = Notif.objects.count()
        self.assertEqual(notif_count_after, notif_count_before + 1)
        
        # Cek notifnya benar
        new_notif = Notif.objects.latest('timestamp')
        self.assertEqual(new_notif.user, self.participant_profile.user)
        self.assertIn('dibatalkan', new_notif.title)
        self.assertEqual(new_notif.event, self.event1_by_org1)
