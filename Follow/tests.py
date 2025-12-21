import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from Authenticate.models import Participant, Organizer
from .models import Follow

class FollowViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.user_participant = User.objects.create_user(username='participant', password='password')
        self.profile_participant = Participant.objects.create(
            user=self.user_participant,
            full_name='Participant Test',
            location='Jakarta',
            username='participant'
        )
        self.user_organizer = User.objects.create_user(username='organizer', password='password')
        self.profile_organizer = Organizer.objects.create(
            user=self.user_organizer,
            organizer_name='Organizer Keren',
            contact_email='org@test.com',
            username='organizer'
        )

        self.user_participant_2 = User.objects.create_user(username='participant2', password='password')
        self.profile_participant_2 = Participant.objects.create(
            user=self.user_participant_2,
            full_name='Participant Dua',
            username='participant2'
        )
        self.user_ghost = User.objects.create_user(username='ghost', password='password')

        self.follow_url = reverse('follow:follow_organizer', args=[self.user_organizer.id])
        self.unfollow_url = reverse('follow:unfollow_organizer', args=[self.user_organizer.id])
        self.show_following_url = reverse('follow:show_following')
        self.show_followers_url = reverse('follow:show_followers')
        self.check_status_url = reverse('follow:check_status', args=[self.user_organizer.id])

        self.login_url = '/authenticate/login/' 

    # --- TEST FOLLOW ORGANIZER ---

    def test_follow_success(self):
        """Test participant follow organizer berhasil (201 Created)"""
        self.client.login(username='participant', password='password')
        
        response = self.client.post(self.follow_url)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Follow.objects.filter(user_from=self.user_participant, user_to=self.user_organizer).exists())
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(response.json()['is_following'])

    def test_follow_already_followed(self):
        """Test follow user yang sudah difollow (200 OK)"""

        Follow.objects.create(user_from=self.user_participant, user_to=self.user_organizer)
        
        self.client.login(username='participant', password='password')
        response = self.client.post(self.follow_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'info')
        self.assertEqual(Follow.objects.count(), 1)

    def test_follow_self(self):
        """Test organizer mencoba follow diri sendiri (400 Bad Request)"""
        self.client.login(username='organizer', password='password')
        url = reverse('follow:follow_organizer', args=[self.user_organizer.id])
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], "Anda tidak bisa follow diri sendiri.")

    def test_follow_non_organizer(self):
        """Test mencoba follow user yang bukan organizer (403 Forbidden)"""
        self.client.login(username='participant', password='password')
        url = reverse('follow:follow_organizer', args=[self.user_participant_2.id])
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 403)
        self.assertIn("Hanya bisa follow akun Organizer", response.json()['message'])

    def test_follow_user_not_found(self):
        """Test follow user ID yang tidak ada (404 Not Found)"""
        self.client.login(username='participant', password='password')
        url = reverse('follow:follow_organizer', args=[99999]) # ID Ngawur
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)

    def test_follow_invalid_method(self):
        """Test pakai GET di endpoint POST (405 Method Not Allowed)"""
        self.client.login(username='participant', password='password')
        response = self.client.get(self.follow_url)
        self.assertEqual(response.status_code, 405)

    def test_unfollow_success(self):
        """Test unfollow berhasil (200 OK)"""
        Follow.objects.create(user_from=self.user_participant, user_to=self.user_organizer)
        
        self.client.login(username='participant', password='password')
        response = self.client.post(self.unfollow_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Follow.objects.filter(user_from=self.user_participant, user_to=self.user_organizer).exists())
        self.assertFalse(response.json()['is_following'])

    def test_unfollow_not_following(self):
        """Test unfollow padahal belum follow (404 Not Found - Custom Message)"""
        self.client.login(username='participant', password='password')
        response = self.client.post(self.unfollow_url)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], "Anda belum mem-follow user ini.")

    def test_unfollow_user_does_not_exist(self):
        """Test unfollow user ID gaib (404 Not Found - Django Generic)"""
        self.client.login(username='participant', password='password')
        url = reverse('follow:unfollow_organizer', args=[99999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404) # get_object_or_404 trigger

    def test_unfollow_invalid_method(self):
        """Test pakai GET (405)"""
        self.client.login(username='participant', password='password')
        response = self.client.get(self.unfollow_url)
        self.assertEqual(response.status_code, 405)

    def test_show_following(self):
        """Test melihat siapa yang saya follow"""
        # Participant follow Organizer
        Follow.objects.create(user_from=self.user_participant, user_to=self.user_organizer)
        
        self.client.login(username='participant', password='password')
        response = self.client.get(self.show_following_url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'organizer')
        self.assertEqual(data[0]['organizer_name'], 'Organizer Keren')

    def test_show_followers(self):
        """Test melihat siapa yang follow saya"""
        # Participant follow Organizer
        Follow.objects.create(user_from=self.user_participant, user_to=self.user_organizer)
        
        # Login sebagai Organizer untuk lihat followers
        self.client.login(username='organizer', password='password')
        response = self.client.get(self.show_followers_url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'participant')
        self.assertEqual(data[0]['full_name'], 'Participant Test')

    def test_check_follow_status_true(self):
        Follow.objects.create(user_from=self.user_participant, user_to=self.user_organizer)
        self.client.login(username='participant', password='password')
        response = self.client.get(self.check_status_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_following'])

    def test_check_follow_status_false(self):
        self.client.login(username='participant', password='password')
        response = self.client.get(self.check_status_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_following'])

    def test_ghost_user_access(self):
        """Test user login tapi tidak punya profile -> harusnya redirect/error"""
        self.client.login(username='ghost', password='password')
        
        response = self.client.post(self.follow_url)
        
        self.assertEqual(response.status_code, 302)

    def test_not_logged_in_access(self):
        """Test akses tanpa login"""
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, 302) # Redirect ke login page
