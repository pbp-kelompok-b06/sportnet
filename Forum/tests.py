from django.test import TestCase
from .models import ForumPost
from Authenticate.models import Participant
from Event.models import Event
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


# Test untuk memastikan halaman forum menampilkan post yang dibuat
class ForumTests(TestCase):
	def test_forum_page_shows_posts(self):
		# Buat user dan participant
		username = 'testuser'
		password = 'testpass123'
		user = User.objects.create_user(username=username, password=password)
		participant = Participant.objects.create(
			user=user,
			full_name='Test User',
			location='Jakarta',
			username=username,
			password=password
		)

		# Buat event (organizer boleh None)
		start = timezone.now() + timedelta(days=1)
		end = start + timedelta(hours=2)
		event = Event.objects.create(
			name='Test Event',
			description='Desc',
			start_time=start,
			end_time=end,
			location='Somewhere',
			sports_category='running',
			activity_category='fun_run_ride',
		)

		# Buat forum post
		post = ForumPost.objects.create(
			event=event,
			profile=participant,
			content='Ini adalah isi post forum untuk pengujian.'
		)

		# Login dan akses halaman forum
		logged = self.client.login(username=username, password=password)
		self.assertTrue(logged, 'Login should succeed for test user')

		url = reverse('Forum:forum_page', args=[str(event.id)])
		response = self.client.get(url)

		# Pastikan berhasil dan mengandung konten post
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, post.content)

