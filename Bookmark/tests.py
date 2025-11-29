import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from Event.models import Event
from .models import Bookmark
import uuid

try:
    from Event.models import Event
except ImportError:
    print("Peringatan: Model Event tidak ditemukan. "
          "Tes ini memerlukan app 'Event' dengan model 'Event'.")
    from django.db import models
    class Event(models.Model):
        name = models.CharField(max_length=100)

        
from .models import Bookmark

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
        
        # URL untuk toggle event 1 (yang sudah di-bookmark user1)
        self.toggle_url_event1 = reverse(
            'Bookmark:toggle_bookmark', 
            args=[self.event1.id]
        )
        # URL untuk toggle event 2 (yang belum di-bookmark user1)
        self.toggle_url_event2 = reverse(
            'Bookmark:toggle_bookmark', 
            args=[self.event2.id]
        )
        # URL untuk toggle event yang tidak ada
        self.toggle_url_invalid = reverse(
            'Bookmark:toggle_bookmark', 
            args=[uuid.uuid4()]
        ) 
        
        # Asumsi URL login dari app Authenticate Anda
        try:
            self.login_url = reverse('Authenticate:login')
        except:
            # Fallback jika URL login tidak ditemukan
            self.login_url = '/login/' # Ganti dengan URL login Anda

    # --- Tes untuk view show_bookmark ---

    def test_show_bookmark_not_logged_in(self):
        """
        Tes: Pengguna belum login tidak bisa melihat halaman bookmark.
        Harus redirect ke halaman login.
        """
        response = self.client.get(self.show_url)
        self.assertEqual(response.status_code, 302) # 302 = Redirect
        self.assertRedirects(response, f'{self.login_url}?next={self.show_url}')

    def test_show_bookmark_logged_in_no_bookmarks(self):
        """
        Tes: Pengguna (user2) sudah login tapi tidak punya bookmark.
        Konteks 'events' dan 'bookmarked_ids' harus kosong.
        """
        # Login sebagai user2 (yang tidak punya bookmark)
        self.client.login(username='user2', password='testpassword123')
        
        response = self.client.get(self.show_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookmark.html')
        self.assertQuerysetEqual(response.context['events'], [])
        self.assertEqual(response.context['bookmarked_ids'], [])

    def test_show_bookmark_logged_in_with_bookmarks(self):
        """
        Tes: Pengguna (user1) sudah login dan punya 1 bookmark.
        Konteks 'events' dan 'bookmarked_ids' harus berisi data.
        """
        # Login sebagai user1 (yang punya 1 bookmark)
        self.client.login(username='user1', password='testpassword123')
        
        response = self.client.get(self.show_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookmark.html')
        
        # Cek konteks berisi event yang benar
        self.assertIn(self.event1, response.context['events'])
        # Cek konteks tidak berisi event yang tidak di-bookmark
        self.assertNotIn(self.event2, response.context['events'])
        # Cek konteks berisi ID yang benar
        self.assertIn(self.event1.id, response.context['bookmarked_ids'])


    # --- Tes untuk view toggle_bookmark ---

    def test_toggle_bookmark_not_logged_in(self):
        """
        Tes: Pengguna belum login tidak bisa toggle bookmark.
        Harus redirect ke halaman login.
        """
        response = self.client.post(self.toggle_url_event1) # Pakai POST
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.login_url}?next={self.toggle_url_event1}')

    def test_toggle_bookmark_invalid_event(self):
        """
        Tes: Toggle bookmark untuk event_id yang tidak ada.
        Harus mengembalikan 404 Not Found.
        """
        self.client.login(username='user1', password='testpassword123')
        response = self.client.post(self.toggle_url_invalid)
        self.assertEqual(response.status_code, 404)

    def test_toggle_bookmark_add(self):
        """
        Tes: Menambah bookmark baru (status 'added').
        """
        self.client.login(username='user1', password='testpassword123')
        
        # Pastikan user1 belum bookmark event2
        bookmark_exists_before = Bookmark.objects.filter(
            user=self.user1, 
            event=self.event2
        ).exists()
        self.assertFalse(bookmark_exists_before)

        # Lakukan POST request untuk menambah bookmark
        response = self.client.post(self.toggle_url_event2)
        
        # Cek respons JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'added'})

        # Pastikan bookmark sekarang ada di database
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
        
        # Pastikan user1 sudah bookmark event1 (dari setUp)
        bookmark_exists_before = Bookmark.objects.filter(
            user=self.user1, 
            event=self.event1
        ).exists()
        self.assertTrue(bookmark_exists_before)

        # Lakukan POST request untuk menghapus bookmark
        response = self.client.post(self.toggle_url_event1)
        
        # Cek respons JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'removed'})

        # Pastikan bookmark sekarang sudah tidak ada di database
        bookmark_exists_after = Bookmark.objects.filter(
            user=self.user1, 
            event=self.event1
        ).exists()
        self.assertFalse(bookmark_exists_after)