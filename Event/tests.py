import json
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.utils import timezone
from datetime import timedelta
from django.contrib.messages import get_messages


from .models import Event
from Authenticate.models import Organizer, Participant
from Bookmark.models import Bookmark
from .views import is_organizer 

try:
    from Notification.models import Notifications as Notif
    NOTIF_APP_AVAILABLE = True
except ImportError:
    NOTIF_APP_AVAILABLE = False



class TestIsOrganizerFunction(TestCase):
    """Tes terisolasi khusus untuk helper function is_organizer."""
    
    def setUp(self):
        self.anon_user = AnonymousUser()
        self.superuser = User.objects.create_superuser('super', 'super@test.com', 'pass')
        self.regular_user = User.objects.create_user('regular', 'reg@test.com', 'pass')
        
        self.org_user = User.objects.create_user('organizer', 'org@test.com', 'pass')
        Organizer.objects.create(user=self.org_user, organizer_name='Test Org')
        
        self.part_user = User.objects.create_user('participant', 'part@test.com', 'pass')
        Participant.objects.create(user=self.part_user, full_name='Test Part', location='Loc')

    def test_is_organizer_anonymous(self):
        self.assertFalse(is_organizer(self.anon_user))

    def test_is_organizer_superuser(self):
        self.assertTrue(is_organizer(self.superuser))
        
    def test_is_organizer_regular_user(self):
        self.assertFalse(is_organizer(self.regular_user))

    def test_is_organizer_participant(self):
        self.assertFalse(is_organizer(self.part_user))

    def test_is_organizer_organizer(self):
        self.assertTrue(is_organizer(self.org_user))


class EventViewsTest(TestCase):

    def setUp(self):
        """Setup data dummy untuk semua tes."""
        self.client = Client()
        self.now = timezone.now()

        self.organizer_user = User.objects.create_user('organizer1', 'org@test.com', 'pass')
        self.organizer_profile = Organizer.objects.create(
            user=self.organizer_user, organizer_name='Event Organizer 1'
        )
        
        self.other_organizer_user = User.objects.create_user('organizer2', 'org2@test.com', 'pass')
        self.other_organizer_profile = Organizer.objects.create(
            user=self.other_organizer_user, organizer_name='Event Organizer 2'
        )

        self.participant_user = User.objects.create_user('participant1', 'part@test.com', 'pass')
        self.participant_profile = Participant.objects.create(
            user=self.participant_user, full_name='Test Participant', location='Test Location'
        )
        
        self.superuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')

        self.event1 = Event.objects.create(
            organizer=self.organizer_profile,
            name='Event 1 (Fee 125.5K)',
            description='Deskripsi Event 1',
            start_time=self.now + timedelta(days=5),
            location='Lokasi 1',
            sports_category='running',
            activity_category='fun_run_ride',
            fee=125500
        )
        self.event1.attendee.add(self.participant_profile) 

        self.event2_free = Event.objects.create(
            organizer=self.organizer_profile,
            name='Event 2 (Free)',
            description='Deskripsi Event 2',
            start_time=self.now + timedelta(days=10),
            location='Lokasi 2',
            sports_category='yoga',
            activity_category='workshop',
            fee=None # Test case fee=None
        )

        self.event3_other_org = Event.objects.create(
            organizer=self.other_organizer_profile, # Milik organizer lain
            name='Event 3 (Fee 1K)',
            description='Deskripsi Event 3',
            start_time=self.now + timedelta(days=7),
            location='Lokasi 3',
            sports_category='padel',
            activity_category='tournament',
            fee=1000
        )
        
        self.event4_fee_500 = Event.objects.create(
            organizer=self.organizer_profile,
            name='Event 4 (Fee 500)',
            description='Deskripsi Event 4',
            start_time=self.now + timedelta(days=1),
            location='Lokasi 4',
            sports_category='football',
            activity_category='friendly_match',
            fee=500
        )
        
        self.event5_fee_round = Event.objects.create(
            organizer=self.organizer_profile,
            name='Event 5 (Fee 125.4K)',
            description='Deskripsi Event 5',
            start_time=self.now + timedelta(days=2),
            location='Lokasi 5',
            sports_category='cycling',
            activity_category='fun_run_ride',
            fee=125449 # Test rounding logic
        )

        Bookmark.objects.create(user=self.participant_user, event=self.event3_other_org)

        self.valid_event_data = {
            'name': 'Event Baru Keren',
            'description': 'Deskripsi event baru.',
            'start_time': (self.now + timedelta(days=20)).strftime('%Y-%m-%dT%H:%M'),
            'end_time': (self.now + timedelta(days=20, hours=3)).strftime('%Y-%m-%dT%H:%M'),
            'location': 'Lokasi Baru',
            'address': 'Alamat Lengkap Baru',
            'sports_category': 'fitness',
            'activity_category': 'course',
            'fee': 100000,
            'capacity': 50,
        }

        self.create_url = reverse('Event:create_event')
        self.detail_url_1 = reverse('Event:event_detail', args=[self.event1.id])
        self.detail_url_2 = reverse('Event:event_detail', args=[self.event2_free.id])
        self.detail_url_3 = reverse('Event:event_detail', args=[self.event3_other_org.id])
        self.detail_url_4 = reverse('Event:event_detail', args=[self.event4_fee_500.id])
        self.detail_url_5 = reverse('Event:event_detail', args=[self.event5_fee_round.id])
        self.detail_url_invalid = reverse('Event:event_detail', args=[uuid.uuid4()])
        
        self.join_url_1 = reverse('Event:join', args=[self.event1.id])
        self.join_url_2 = reverse('Event:join', args=[self.event2_free.id])
        self.join_url_invalid = reverse('Event:join', args=[uuid.uuid4()])
        
        self.edit_url_1 = reverse('Event:edit_event', args=[self.event1.id])
        self.edit_url_other = reverse('Event:edit_event', args=[self.event3_other_org.id])
        self.edit_url_invalid = reverse('Event:edit_event', args=[uuid.uuid4()])

        self.login_url = reverse('Authenticate:login')
        self.dashboard_url = reverse('dashboard:show')
        self.homepage_url = reverse('Homepage:show_main')

    def test_create_event_get_not_organizer(self):
        """Tes: GET /create_event/ (sbg participant) -> redirect ke homepage"""
        self.client.login(username='participant1', password='pass')
        response = self.client.get(self.create_url)
        self.assertRedirects(response, self.homepage_url)

    def test_create_event_get_as_organizer(self):
        """Tes: GET /create_event/ (sbg organizer) -> OK"""
        self.client.login(username='organizer1', password='pass')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_event.html')
        self.assertIn('form', response.context)

    def test_create_event_post_invalid_form(self):
        """Tes: POST /create_event/ (data tidak valid) -> re-render form"""
        self.client.login(username='organizer1', password='pass')
        event_count_before = Event.objects.count()
        # Post data kosong, pasti tidak valid
        response = self.client.post(self.create_url, {}) 
        
        self.assertEqual(response.status_code, 200) # Re-render
        self.assertTemplateUsed(response, 'create_event.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors) # Cek ada error di form
        self.assertEqual(Event.objects.count(), event_count_before) # Pastikan event tdk dibuat

    def test_create_event_post_valid_form(self):
        """Tes: POST /create_event/ (data valid) -> redirect ke dashboard"""
        self.client.login(username='organizer1', password='pass')
        event_count_before = Event.objects.count()
        response = self.client.post(self.create_url, self.valid_event_data)
        
        self.assertRedirects(response, self.dashboard_url)
        self.assertEqual(Event.objects.count(), event_count_before + 1)
        
        # Cek event baru
        new_event = Event.objects.latest('start_time')
        self.assertEqual(new_event.name, 'Event Baru Keren')
        self.assertEqual(new_event.organizer, self.organizer_profile)

    def test_event_detail_not_found(self):
        """Tes: GET /event/detail/<invalid_uuid>/ -> 404"""
        response = self.client.get(self.detail_url_invalid)
        self.assertEqual(response.status_code, 404)

    def test_event_detail_anonymous(self):
        """Tes: GET /event/detail/... (sbg anonymous) -> OK"""
        response = self.client.get(self.detail_url_1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_detail.html')
        self.assertEqual(response.context['event'], self.event1)
        self.assertFalse(response.context['is_bookmarked'])
        self.assertFalse(response.context['is_participant'])

    def test_event_detail_participant_not_bookmarked(self):
        """Tes: GET /event/detail/... (sbg participant, belum bookmark) -> OK"""
        self.client.login(username='participant1', password='pass')
        response = self.client.get(self.detail_url_1) # Event 1
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_bookmarked'])
        self.assertTrue(response.context['is_participant'])
        
    def test_event_detail_participant_bookmarked(self):
        """Tes: GET /event/detail/... (sbg participant, sudah bookmark) -> OK"""
        self.client.login(username='participant1', password='pass')
        response = self.client.get(self.detail_url_3) 
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_bookmarked'])
        self.assertTrue(response.context['is_participant'])

    def test_event_detail_as_organizer(self):
        """Tes: GET /event/detail/... (sbg organizer) -> OK"""
        self.client.login(username='organizer1', password='pass')
        response = self.client.get(self.detail_url_1)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_bookmarked'])
        self.assertFalse(response.context['is_participant'])

    def test_event_detail_fee_formatting(self):
        """Tes: Logika formatting fee di event_detail"""
        response = self.client.get(self.detail_url_1)
        self.assertEqual(response.context['formatted_fee'], '125.5K')

        response = self.client.get(self.detail_url_2)
        self.assertEqual(response.context['formatted_fee'], '0')

        response = self.client.get(self.detail_url_3)
        self.assertEqual(response.context['formatted_fee'], '1K')

        response = self.client.get(self.detail_url_4)
        self.assertEqual(response.context['formatted_fee'], '500')

        response = self.client.get(self.detail_url_5)
        self.assertEqual(response.context['formatted_fee'], '125.4K')


    def test_join_not_logged_in(self):
        """Tes: POST /join/... (belum login) -> redirect ke login"""
        response = self.client.post(self.join_url_1)
        self.assertRedirects(response, self.login_url)

    def test_join_get_method(self):
        """Tes: GET /join/... -> 405 Method Not Allowed"""
        self.client.login(username='participant1', password='pass')
        response = self.client.get(self.join_url_1)
        self.assertEqual(response.status_code, 405) # Karena @require_POST

    def test_join_not_found(self):
        """Tes: POST /join/<invalid_uuid>/ -> 404"""
        self.client.login(username='participant1', password='pass')
        response = self.client.post(self.join_url_invalid)
        self.assertEqual(response.status_code, 404)

    def test_join_as_organizer(self):
        """Tes: POST /join/... (sbg organizer) -> 403"""
        self.client.login(username='organizer1', password='pass')
        response = self.client.post(self.join_url_2)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'Kamu bukan participant.')

    def test_join_already_joined(self):
        """Tes: POST /join/... (participant sudah join) -> 400"""
        self.client.login(username='participant1', password='pass')
        response = self.client.post(self.join_url_1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Kamu sudah join event ini.')

    def test_join_success_and_notif(self):
        """Tes: POST /join/... (sukses) -> 200 OK dan Notif terbuat"""
        if not NOTIF_APP_AVAILABLE:
            self.skipTest("Aplikasi Notifikasi (Notification) tidak ditemukan.")

        self.client.login(username='participant1', password='pass')
        
        attendee_count_before = self.event2_free.attendee.count()
        notif_count_before = Notif.objects.count()

        response = self.client.post(self.join_url_2)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])

        self.event2_free.refresh_from_db()
        self.assertEqual(self.event2_free.attendee.count(), attendee_count_before + 1)
        self.assertTrue(self.event2_free.attendee.filter(id=self.participant_profile.id).exists())

        
        notif_count_after = Notif.objects.count()
        self.assertEqual(notif_count_after, notif_count_before + 1)

    def test_edit_event_get_not_organizer(self):
        """Tes: GET /edit_event/... (sbg participant) -> redirect ke homepage"""
        self.client.login(username='participant1', password='pass')
        response = self.client.get(self.edit_url_1)
        self.assertRedirects(response, self.homepage_url)

    def test_edit_event_get_not_found(self):
        """Tes: GET /edit_event/<invalid_uuid>/ (sbg organizer) -> 404"""
        self.client.login(username='organizer1', password='pass')
        response = self.client.get(self.edit_url_invalid)
        self.assertEqual(response.status_code, 404)

    def test_edit_event_get_not_owner(self):
        """Tes: GET /edit_event/... (sbg organizer, tapi bukan pemilik) -> 403"""
        self.client.login(username='organizer1', password='pass')
        response = self.client.get(self.edit_url_other) 
        self.assertEqual(response.status_code, 403) 
        
    def test_edit_event_get_owner(self):
        """Tes: GET /edit_event/... (sbg organizer pemilik) -> OK"""
        self.client.login(username='organizer1', password='pass')
        response = self.client.get(self.edit_url_1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_event.html')
        self.assertEqual(response.context['event'], self.event1)
        self.assertEqual(response.context['form'].instance, self.event1)

    def test_edit_event_post_not_owner(self):
        """Tes: POST /edit_event/... (sbg organizer, tapi bukan pemilik) -> 403"""
        self.client.login(username='organizer1', password='pass')
        response = self.client.post(self.edit_url_other, self.valid_event_data)
        self.assertEqual(response.status_code, 403)

        self.event3_other_org.refresh_from_db()
        self.assertNotEqual(self.event3_other_org.name, self.valid_event_data['name'])
        
    def test_edit_event_post_invalid_form(self):
        """Tes: POST /edit_event/... (sbg owner, data tidak valid) -> re-render"""
        self.client.login(username='organizer1', password='pass')
        invalid_data = self.valid_event_data.copy()
        invalid_data['name'] = '' 
        
        response = self.client.post(self.edit_url_1, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_event.html')
        self.assertTrue(response.context['form'].errors)
        
        self.event1.refresh_from_db()
        self.assertNotEqual(self.event1.name, '') 

    def test_edit_event_post_owner_success(self):
        """Tes: POST /edit_event/... (sbg owner, data valid) -> redirect"""
        self.client.login(username='organizer1', password='pass')
        
        post_data = self.valid_event_data.copy()
        post_data['name'] = 'NAMA EVENT SUDAH DIUPDATE'
        
        response = self.client.post(self.edit_url_1, post_data)
        self.assertRedirects(response, self.dashboard_url)

        self.event1.refresh_from_db()
        self.assertEqual(self.event1.name, 'NAMA EVENT SUDAH DIUPDATE')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Event berhasil diupdate!")

    def test_edit_event_post_superuser_not_owner_success(self):
        """Tes: POST /edit_event/... (sbg SUPERUSER, bukan pemilik) -> OK"""
        self.client.login(username='admin', password='pass')
        
        post_data = self.valid_event_data.copy()
        post_data['name'] = 'NAMA DIUPDATE OLEH ADMIN'
    
        response = self.client.post(self.edit_url_other, post_data)
        self.assertRedirects(response, self.homepage_url)

        self.event3_other_org.refresh_from_db()
        self.assertEqual(self.event3_other_org.name, 'NAMA DIUPDATE OLEH ADMIN')