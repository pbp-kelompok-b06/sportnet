from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from Event.models import Event
from Authenticate.models import Organizer


class HomepageSearchFilterTests(TestCase):
	def setUp(self):
		# create organizer required by Event
		user = User.objects.create_user(username='org1', password='pass')
		self.organizer = Organizer.objects.create(
			user=user,
			organizer_name='Org 1',
			username='org1',
			password='pass'
		)

		# Event 1: running, free, located in Jakarta
		self.event1 = Event.objects.create(
			name='Jakarta Fun Run',
			description='A fun run in Jakarta',
			start_time=timezone.now(),
			end_time=timezone.now(),
			location='Jakarta',
			sports_category='running',
			activity_category='fun_run_ride',
			organizer=self.organizer,
			fee=None,
			capacity=100
		)

		# Event 2: yoga, paid, located in Bandung
		self.event2 = Event.objects.create(
			name='Bandung Yoga Retreat',
			description='Relaxing yoga',
			start_time=timezone.now(),
			end_time=timezone.now(),
			location='Bandung',
			sports_category='yoga',
			activity_category='course',
			organizer=self.organizer,
			fee=50000,
			capacity=50
		)

		# Event 3: running, paid, located in Jakarta but different name
		self.event3 = Event.objects.create(
			name='Jakarta Marathon',
			description='Competitive marathon',
			start_time=timezone.now(),
			end_time=timezone.now(),
			location='Jakarta',
			sports_category='running',
			activity_category='marathon',
			organizer=self.organizer,
			fee=100000,
			capacity=300
		)

	def test_search_by_text_matches_name_description_location(self):
		# search 'marathon' should return event3 only
		resp = self.client.get(reverse('Homepage:show_main'), {'q': 'marathon'})
		content = resp.content.decode('utf-8')
		self.assertIn('Jakarta Marathon', content)
		self.assertNotIn('Jakarta Fun Run', content)
		self.assertNotIn('Bandung Yoga Retreat', content)

		# search 'Jakarta' should return event1 and event3
		resp = self.client.get(reverse('Homepage:show_main'), {'q': 'Jakarta'})
		content = resp.content.decode('utf-8')
		self.assertIn('Jakarta Fun Run', content)
		self.assertIn('Jakarta Marathon', content)
		self.assertNotIn('Bandung Yoga Retreat', content)

	def test_filter_by_category(self):
		# filter yoga should only show event2
		resp = self.client.get(reverse('Homepage:show_main'), {'category': 'yoga'})
		content = resp.content.decode('utf-8')
		self.assertIn('Bandung Yoga Retreat', content)
		self.assertNotIn('Jakarta Fun Run', content)
		self.assertNotIn('Jakarta Marathon', content)

	def test_filter_free_events(self):
		# free=1 should return only event1 (fee=None)
		resp = self.client.get(reverse('Homepage:show_main'), {'free': '1'})
		content = resp.content.decode('utf-8')
		self.assertIn('Jakarta Fun Run', content)
		self.assertNotIn('Bandung Yoga Retreat', content)
		self.assertNotIn('Jakarta Marathon', content)
