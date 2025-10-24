from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from Authenticate.models import Participant, Organizer, User
from Event.models import Event
from .models import Notifications
import uuid

class NotificationTest(TestCase):
    def setUp(self):
        # Create test user for participant
        self.user1 = User.objects.create_user(
            username='testparticipant1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testparticipant2',
            password='testpass123'
        )
        
        # Create test organizer
        self.organizer_user = User.objects.create_user(
            username='testorganizer',
            password='testpass123'
        )
        self.organizer = Organizer.objects.create(
            user=self.organizer_user,
            organizer_name="Test Organizer",
            contact_phone="1234567890",
            contact_email="test@test.com",
            username="testorganizer",
            password="testpass123"
        )
        
        # Create test participants
        self.participant1 = Participant.objects.create(
            user=self.user1,
            full_name="Test Participant 1",
            username="testparticipant1",
            password="testpass123",
            location="Test Location"
        )
        self.participant2 = Participant.objects.create(
            user=self.user2,
            full_name="Test Participant 2",
            username="testparticipant2",
            password="testpass123",
            location="Test Location"
        )
        
        # Create test event
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Description",
            start_time=timezone.now(),
            location="Test Location",
            sports_category="running",
            activity_category="marathon",
            organizer=self.organizer,
            capacity=10
        )
        
        # Add participants to event
        self.event.attendee.add(self.participant1, self.participant2)
        
        # Initialize the test client
        self.client = Client()

    def test_create_event_notification(self):
        """Test creating notifications for event participants"""
        from .views import create_event_notification
        
        notifications = create_event_notification(
            self.event,
            "Test Notification",
            "Test Message"
        )
        
        # Check if notifications were created for all participants
        self.assertEqual(len(notifications), 2)
        self.assertEqual(
            Notifications.objects.filter(event=self.event).count(),
            2
        )

    def test_send_event_notification_endpoint(self):
        """Test the notification sending endpoint"""
        url = reverse('Notification:send_event_notification', kwargs={
            'event_id': self.event.id,
            'title': 'Test Title',
            'message': 'Test Message'
        })
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check response content
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(
            response.json()['message'],
            'Notifications sent to 2 participants'
        )

    def test_send_event_notification_invalid_event(self):
        """Test sending notification to non-existent event"""
        invalid_uuid = uuid.uuid4()
        url = reverse('Notification:send_event_notification', kwargs={
            'event_id': invalid_uuid,
            'title': 'Test Title',
            'message': 'Test Message'
        })
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['status'], 'error')
        self.assertEqual(response.json()['message'], 'Event not found')

    def test_notification_read_status(self):
        """Test notification read/unread status"""
        from .views import create_event_notification
        
        notifications = create_event_notification(
            self.event,
            "Test Notification",
            "Test Message"
        )
        
        # Check initial unread status
        notification = notifications[0]
        self.assertFalse(notification.is_read)
        
        # Test marking as read
        notification.read()
        self.assertTrue(notification.is_read)

    def test_mark_notification_read_endpoint_success(self):
        # create notifications
        from .views import create_event_notification
        notifications = create_event_notification(self.event, 'Title', 'Msg')
        notif = notifications[0]

        # login as the owner of notif
        self.client.login(username='testparticipant1', password='testpass123')

        url = reverse('Notification:mark_notification_read', kwargs={'notif_id': notif.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_mark_notification_read_forbidden(self):
        from .views import create_event_notification
        notifications = create_event_notification(self.event, 'Title', 'Msg')
        notif = notifications[0]

        # login as a different participant
        self.client.login(username='testparticipant2', password='testpass123')
        url = reverse('Notification:mark_notification_read', kwargs={'notif_id': notif.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

        notif.refresh_from_db()
        self.assertFalse(notif.is_read)

    def test_mark_all_read_endpoint(self):
        from .views import create_event_notification
        notifications = create_event_notification(self.event, 'Title', 'Msg')

        # login as participant1
        self.client.login(username='testparticipant1', password='testpass123')
        url = reverse('Notification:mark_all_read')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')

        # ensure notifications for participant1 are read
        for n in Notifications.objects.filter(user=self.participant1):
            self.assertTrue(n.is_read)

    def test_event_deletion_notification(self):
        """Test notifications are created when an event is deleted"""
        # Create notifications for event deletion
        from .views import create_event_notification
        
        # Store event info before deletion
        event_name = self.event.name
        attendees = list(self.event.attendee.all())
        
        # Create pre-delete notifications
        notifications = create_event_notification(
            self.event,
            "Event Dibatalkan",
            f"Event {event_name} telah dibatalkan oleh penyelenggara"
        )
        
        # Delete the event
        self.event.delete()
        
        # Verify notifications were created for all attendees
        for participant in attendees:
            notifs = Notifications.objects.filter(
                user=participant,
                title="Event Dibatalkan"
            )
            self.assertTrue(notifs.exists())
            self.assertIn(event_name, notifs.first().message)
