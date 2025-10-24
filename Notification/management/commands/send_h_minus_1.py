from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from Event.models import Event

class Command(BaseCommand):
    help = 'Send H-1 reminders to event participants for events happening tomorrow'

    def handle(self, *args, **options):
        now = timezone.now()
        tomorrow = (now + timedelta(days=1)).date()

        events = Event.objects.filter(start_time__date=tomorrow)
        total = 0
        for event in events:
            attendees = event.attendee.all()
            for participant in attendees:
                # create a reminder notification if not already created
                title = f"Reminder: {event.name} will start tomorrow"
                message = f"Don't forget, event '{event.name}' will start on {event.start_time.strftime('%d %b %Y, %H:%M')}."
                try:
                    from Notification.models import Notifications as Notif
                    exists = Notif.objects.filter(user=participant, event=event, title=title).exists()
                    if not exists:
                        Notif.objects.create(user=participant, title=title, message=message, event=event)
                        total += 1
                except Exception as e:
                    # log to stdout but continue
                    self.stdout.write(self.style.WARNING(f'Failed to create notification for participant {participant}: {e}'))
                    continue

       
        self.stdout.write(self.style.SUCCESS(f'Sent {total} reminder notifications for events on {tomorrow}'))
    def handleNow(self, *args, **options):
        now = timezone.now().date()

        events = Event.objects.filter(start_time__date=now)
        total = 0
        for event in events:
            attendees = event.attendee.all()
            for participant in attendees:
                # create a reminder notification if not already created
                title = f"Reminder: {event.name} is happening today"
                message = f"Head to the venue, '{event.name}' is happening today on {event.start_time.strftime('%d %b %Y, %H:%M')}."
                try:
                    from Notification.models import Notifications as Notif
                    exists = Notif.objects.filter(user=participant, event=event, title=title).exists()
                    if not exists:
                        Notif.objects.create(user=participant, title=title, message=message, event=event)
                        total += 1
                except Exception as e:
                    # log to stdout but continue
                    self.stdout.write(self.style.WARNING(f'Failed to create notification for participant {participant}: {e}'))
                    continue

        self.stdout.write(self.style.SUCCESS(f'Sent {total} reminder notifications for events on {now}'))
