import json
import base64
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

# Import Models
from Authenticate.models import Participant, Organizer
from Follow.models import Follow

try:
    from Event.models import Event
    EVENT_AVAILABLE = True
except ImportError:
    Event = None
    EVENT_AVAILABLE = False

class ProfileViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.user_part = User.objects.create_user(username='participant', password='password')
        self.part_profile = Participant.objects.create(
            user=self.user_part,
            full_name='Participant Test',
            location='Jakarta',
            username='participant',
            birth_date=timezone.now().date(),
            about="Suka lari"
        )

        self.user_org = User.objects.create_user(username='organizer', password='password')
        self.org_profile = Organizer.objects.create(
            user=self.user_org,
            organizer_name='Organizer Test',
            contact_email='org@test.com',
            username='organizer',
            about="Kami EO terbaik"
        )

        self.user_ghost = User.objects.create_user(username='ghost', password='password')

        Follow.objects.create(user_from=self.user_part, user_to=self.user_org)

        if EVENT_AVAILABLE:
            now = timezone.now()
            self.event_future = Event.objects.create(
                organizer=self.org_profile,
                name="Future Event",
                start_time=now + timedelta(days=5),
                location="GBK",
                sports_category="running",
                activity_category="competition"
            )
            self.event_past = Event.objects.create(
                organizer=self.org_profile,
                name="Past Event",
                start_time=now - timedelta(days=5),
                location="Monas",
                sports_category="yoga",
                activity_category="workshop"
            )
            # Add attendee
            if hasattr(self.event_future, 'attendee'):
                self.event_future.attendee.add(self.part_profile)
                self.event_past.attendee.add(self.part_profile)

        self.profile_api_me_url = reverse('profile:profile_api_me')
        self.profile_view_url = reverse('profile:profile_view')
        self.edit_profile_url = reverse('profile:edit_profile')
        self.edit_profile_api_url = reverse('profile:edit_profile_api')
        self.create_profile_url = reverse('profile:create_profile')
        self.delete_account_flutter_url = reverse('profile:delete_account_flutter')
        self.delete_account_web_url = reverse('profile:delete_account')
        self.delete_picture_url = reverse('profile:delete_Profilepict')
        
        self.base64_img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

    def test_profile_api_unauthenticated(self):
        response = self.client.get(self.profile_api_me_url)
        if response.status_code == 302:
            self.assertTrue(True)
        else:
            self.assertEqual(response.status_code, 401)

    def test_profile_api_me_participant(self):
        self.client.login(username='participant', password='password')
        response = self.client.get(self.profile_api_me_url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['user']['role'], 'participant')
        self.assertTrue(data['user']['is_me'])
        
        if EVENT_AVAILABLE:
            self.assertIn('upcoming', data['profile']['booked_events'])

    def test_profile_api_me_organizer(self):
        self.client.login(username='organizer', password='password')
        response = self.client.get(self.profile_api_me_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['user']['role'], 'organizer')

    def test_profile_api_view_other_user(self):
        self.client.login(username='participant', password='password')
        url = reverse('profile:profile_api_user', args=['organizer']) 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['user']['is_me'])

    def test_profile_api_not_found(self):
        self.client.login(username='participant', password='password')
        url = reverse('profile:profile_api_user', args=['ngawur'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_profile_view_participant(self):
        self.client.login(username='participant', password='password')
        response = self.client.get(self.profile_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_profile_view_organizer(self):
        self.client.login(username='organizer', password='password')
        response = self.client.get(self.profile_view_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_view_other(self):
        self.client.login(username='participant', password='password')
        url = reverse('profile:profile_view_user', args=['organizer'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_view_unauthenticated(self):
        response = self.client.get(self.profile_view_url)
        self.assertEqual(response.status_code, 302) 

    def test_edit_profile_get(self):
        self.client.login(username='participant', password='password')
        response = self.client.get(self.edit_profile_url)
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_post_participant(self):
        self.client.login(username='participant', password='password')
        data = {'full_name': 'Updated', 'location': 'Bdg', 'birth_date': '2000-01-01', 'about': 'new'}
        response = self.client.post(self.edit_profile_url, data)
        self.assertEqual(response.status_code, 302)
        self.part_profile.refresh_from_db()
        self.assertEqual(self.part_profile.full_name, 'Updated')

    def test_edit_profile_post_organizer(self):
        self.client.login(username='organizer', password='password')
        data = {'organizer_name': 'Updated Org', 'contact_email': 'a@a.com', 'about': 'new'}
        response = self.client.post(self.edit_profile_url, data)
        self.assertEqual(response.status_code, 302)
        self.org_profile.refresh_from_db()
        self.assertEqual(self.org_profile.organizer_name, 'Updated Org')

    def test_edit_api_success_participant(self):
        self.client.login(username='participant', password='password')
        data = {'full_name': 'API Upd', 'profile_picture_base64': self.base64_img}
        response = self.client.post(self.edit_profile_api_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_edit_api_invalid_json(self):
        self.client.login(username='participant', password='password')
        response = self.client.post(self.edit_profile_api_url, "bad json", content_type="application/json")
        self.assertEqual(response.status_code, 400)

        
    def test_create_profile_redirect(self):
        """Sudah punya profile -> redirect"""
        self.client.login(username='participant', password='password')
        response = self.client.get(self.create_profile_url)
        self.assertEqual(response.status_code, 302)

    def test_create_profile_participant_success(self):
        self.client.login(username='ghost', password='password')
        session = self.client.session
        session['registration_role'] = 'participant'
        session.save()

        data = {'full_name': 'New Part', 'location': 'Loc', 'birth_date': '2000-01-01'}
        response = self.client.post(self.create_profile_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Participant.objects.filter(user=self.user_ghost).exists())

    def test_create_profile_organizer_success(self):
        user_new = User.objects.create_user(username='neworg', password='pw')

        self.client.login(username='neworg', password='pw')
        
        session = self.client.session
        session['registration_role'] = 'organizer'
        session.save()

        data = {'organizer_name': 'New Org', 'contact_email': 'o@o.com'}
        response = self.client.post(self.create_profile_url, data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Organizer.objects.filter(user=user_new).exists())

    def test_delete_account_web(self):
        self.client.login(username='participant', password='password')
        uid = self.user_part.id
        response = self.client.post(self.delete_account_web_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(id=uid).exists())

    def test_delete_account_flutter(self):
        self.client.login(username='organizer', password='password')
        uid = self.user_org.id
        response = self.client.post(self.delete_account_flutter_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(id=uid).exists())

    def test_delete_profile_picture(self):
        self.part_profile.profile_picture = SimpleUploadedFile("x.jpg", b"x", "image/jpeg")
        self.part_profile.save()
        self.client.login(username='participant', password='password')
        response = self.client.post(self.delete_picture_url)
        self.assertEqual(response.status_code, 302)
        self.part_profile.refresh_from_db()
        self.assertFalse(self.part_profile.profile_picture)

    def test_serializers(self):
        urls = [
            reverse('profile:show_xml_Organizer'),
            reverse('profile:show_xml_Participant'),
            reverse('profile:show_json_Organizer'),
            reverse('profile:show_json_Participant'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)