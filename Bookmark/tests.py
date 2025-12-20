import json
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from Event.models import Event
from .models import Bookmark
from Authenticate.models import Participant 

class BookmarkViewsTest(TestCase):

    def setUp(self):
        """Setup data dummy untuk semua tes."""
        self.client = Client()

        self.user1 = User.objects.create_user(
            username='user1', 
            password='testpassword123'
        )
        self.user2 = User.objects.create_user(
            username='user2', 
            password='testpassword123'
        )

        self.participant1 = Participant.objects.create(
            user=self.user1,
            full_name="User Satu",
            location="Jakarta",
            username="user1"
        )
        self.participant2 = Participant.objects.create(
            user=self.user2,
            full_name="User Dua",
            location="Bandung",
            username="user2"
        )

        now = timezone.now()

        self.event1 = Event.objects.create(
            name='Event Test 1',
            description='Ini adalah deskripsi tes untuk event 1.',
            start_time=now,
            location='Lokasi Tes 1',
            sports_category='running',        
            activity_category='fun_run_ride'   
        )
        
        self.event2 = Event.objects.create(
            name='Event Test 2',
            description='Ini adalah deskripsi tes untuk event 2.',
            start_time=now,
            location='Lokasi Tes 2',
            sports_category='yoga',            
            activity_category='workshop'       
        )

        self.bookmark_user1_event1 = Bookmark.objects.create(
            user=self.user1, 
            event=self.event1
        )

        self.show_url = reverse('Bookmark:show_bookmark')
        
        self.toggle_url_event1 = reverse(
            'Bookmark:toggle_bookmark', 
            args=[self.event1.id]
        )

        self.toggle_url_event2 = reverse(
            'Bookmark:toggle_bookmark', 
            args=[self.event2.id]
        )
        # URL untuk toggle event yang tidak ada
        self.toggle_url_invalid = reverse(
            'Bookmark:toggle_bookmark', 
            args=[uuid.uuid4()]
        ) 
        
        self.login_url = '/authenticate/login/'
        
    def test_show_bookmark_not_logged_in(self):
        """
        Tes: Pengguna belum login tidak bisa melihat halaman bookmark.
        Harus redirect ke halaman login.
        """
        response = self.client.get(self.show_url)
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, self.login_url)

    def test_show_bookmark_logged_in_no_bookmarks(self):
        """
        Tes: Pengguna (user2) sudah login tapi tidak punya bookmark.
        """
        self.client.login(username='user2', password='testpassword123')
        
        response = self.client.get(self.show_url)
        

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookmark.html')
        self.assertEqual(list(response.context['bookmarks']), [])
        self.assertEqual(response.context['bookmarked_ids'], [])

    def test_show_bookmark_logged_in_with_bookmarks(self):
        """
        Tes: Pengguna (user1) sudah login dan punya 1 bookmark.
        """
        self.client.login(username='user1', password='testpassword123')
        
        response = self.client.get(self.show_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookmark.html')
        
        self.assertIn(self.bookmark_user1_event1, response.context['bookmarks'])
        self.assertIn(self.event1.id, response.context['bookmarked_ids'])


    def test_toggle_bookmark_not_logged_in(self):
        """
        Tes: Pengguna belum login tidak bisa toggle bookmark.
        """
        response = self.client.post(self.toggle_url_event1) 
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    def test_toggle_bookmark_invalid_event(self):
        """
        Tes: Toggle bookmark untuk event_id yang tidak ada.
        """
        self.client.login(username='user1', password='testpassword123')
        response = self.client.post(self.toggle_url_invalid)
        self.assertEqual(response.status_code, 404)

    def test_toggle_bookmark_add(self):
        """
        Tes: Menambah bookmark baru (status 'added').
        """
        self.client.login(username='user1', password='testpassword123')
        
        bookmark_exists_before = Bookmark.objects.filter(
            user=self.user1, 
            event=self.event2
        ).exists()
        self.assertFalse(bookmark_exists_before)

        response = self.client.post(self.toggle_url_event2)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'added'})

        bookmark_exists_after = Bookmark.objects.filter(
            user=self.user1, 
            event=self.event2
        ).exists()
        self.assertTrue(bookmark_exists_after)

    def test_toggle_bookmark_remove(self):
        """
        Tes: Menghapus bookmark yang sudah ada (status 'removed').
        """
        self.client.login(username='user1', password='testpassword123')
        
        bookmark_exists_before = Bookmark.objects.filter(
            user=self.user1, 
            event=self.event1
        ).exists()
        self.assertTrue(bookmark_exists_before)

        response = self.client.post(self.toggle_url_event1)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'removed'})

        bookmark_exists_after = Bookmark.objects.filter(
            user=self.user1, 
            event=self.event1
        ).exists()
        self.assertFalse(bookmark_exists_after)