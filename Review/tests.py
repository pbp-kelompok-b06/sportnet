from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Import Models
from Event.models import Event
from Authenticate.models import Participant, Organizer
from .models import Review

class ReviewViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.org_user = User.objects.create_user(username='organizer', password='password')
        self.org_profile = Organizer.objects.create(
            user=self.org_user,
            organizer_name='Organizer Test'
        )

        self.user1 = User.objects.create_user(username='user1', password='password')
        self.part1 = Participant.objects.create(
            user=self.user1,
            full_name='Participant Satu',
            username='user1'
        )

        self.user2 = User.objects.create_user(username='user2', password='password')
        self.part2 = Participant.objects.create(
            user=self.user2,
            full_name='Participant Dua',
            username='user2'
        )


        self.event = Event.objects.create(
            organizer=self.org_profile,
            name='Event Keren',
            description='Deskripsi',
            start_time=timezone.now() + timedelta(days=1),
            location='Jakarta',
            sports_category='running',
            activity_category='fun_run_ride'
        )

        self.review = Review.objects.create(
            event=self.event,
            participant=self.part1,
            rating=5,
            comment="Event sangat bagus!"
        )


        self.review_page_url = reverse('Review:review_page', args=[self.event.id])
        self.edit_url = reverse('Review:edit_review', args=[self.review.id])
        self.delete_url = reverse('Review:delete_review', args=[self.review.id])
        self.login_url = '/authenticate/login/' 

    def test_review_page_access_not_logged_in(self):
        """Akses halaman review tanpa login -> Redirect"""
        response = self.client.get(self.review_page_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    def test_review_page_get_success(self):
        """User login melihat halaman review -> 200 OK"""
        self.client.login(username='user2', password='password') # User 2 belum review
        response = self.client.get(self.review_page_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/review_page.html')
        self.assertTrue(response.context['authen'])
        self.assertIn(self.review, response.context['reviews'])

    def test_create_review_success(self):
        """User 2 membuat review baru -> Sukses"""
        self.client.login(username='user2', password='password')
        
        data = {
            'rating': 4,
            'comment': 'Lumayan seru'
        }
        response = self.client.post(self.review_page_url, data)
        
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, self.review_page_url)
        
 
        self.assertTrue(Review.objects.filter(participant=self.part2, event=self.event).exists())

    def test_create_review_already_reviewed(self):
        """User 1 mencoba review lagi (padahal sudah) -> Gagal/Diabaikan"""
        self.client.login(username='user1', password='password')

        response_get = self.client.get(self.review_page_url)
        self.assertFalse(response_get.context['authen'])

        count_before = Review.objects.filter(participant=self.part1).count()
        data = {'rating': 1, 'comment': 'Spam review'}
        response = self.client.post(self.review_page_url, data)
        
        self.assertEqual(response.status_code, 200) 
        
        self.assertEqual(Review.objects.filter(participant=self.part1).count(), count_before)

    def test_create_review_invalid_form(self):
        """Submit form kosong/invalid"""
        self.client.login(username='user2', password='password')
        data = {'rating': '', 'comment': ''} # Invalid
        
        response = self.client.post(self.review_page_url, data)
        
        self.assertEqual(response.status_code, 200) # Render ulang dengan error
        self.assertFalse(Review.objects.filter(participant=self.part2).exists())

    def test_edit_review_get(self):
        """Owner membuka halaman edit -> 200 OK"""
        self.client.login(username='user1', password='password')
        response = self.client.get(self.edit_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/edit_review.html')

    def test_edit_review_post_success(self):
        """Owner update review -> Sukses"""
        self.client.login(username='user1', password='password')
        data = {'rating': 3, 'comment': 'Diedit jadi bintang 3'}
        
        response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 302)
        
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)
        self.assertEqual(self.review.comment, 'Diedit jadi bintang 3')

    def test_edit_review_forbidden(self):
        """Orang lain (User 2) coba edit review punya User 1 -> 403 Forbidden"""
        self.client.login(username='user2', password='password')
        
        response = self.client.post(self.edit_url, {'rating': 1, 'comment': 'HACKED'})
        
        self.assertEqual(response.status_code, 403)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)

    def test_edit_review_not_found(self):
        """Edit review ID gaib -> 404"""
        self.client.login(username='user1', password='password')
        url = reverse('Review:edit_review', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_review_success(self):
        """Owner hapus review -> Sukses"""
        self.client.login(username='user1', password='password')
        
        response = self.client.post(self.delete_url)
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_forbidden(self):
        """Orang lain coba hapus review -> 403 Forbidden"""
        self.client.login(username='user2', password='password')
        
        response = self.client.post(self.delete_url)
        
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())