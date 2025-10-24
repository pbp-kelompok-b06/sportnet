from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from Notification.models import Notifications as Notif
from Event.models import Event
from Authenticate.models import Participant

@login_required
def show_all(request):
    """
    Render a page with all notifications for the logged-in participant.
    If the user does not have a participant profile, show an empty list.
    """
    try:
        participant = request.user.participant_profile
        notifications = Notif.objects.filter(user=participant).order_by('-timestamp')
    except Exception:
        # user has no participant profile or other issue; return empty queryset
        notifications = Notif.objects.none()

    context = {
        'notif': notifications,
    }
    return render(request, 'all_notif.html', context)

def show_detail(request):
    return render(request, 'show_detail.html')

def create_event_notification(event, title, message):
    """
    Creates notifications for all participants of an event
    Args:
        event (Event): The event object
        title (str): Title of the notification
        message (str): Message content of the notification
    Returns:
        list: List of created notification objects
    """
    # Get all participants of the event
    participants = event.attendee.all()
    
    # Create notifications for each participant
    notifications = []
    for participant in participants:
        notification = Notif.objects.create(
            user=participant,
            title=title,
            message=message,
            event=event
        )
        notifications.append(notification)
    
    return notifications

def send_event_notification(request, event_id, title, message):
    """
    API endpoint to send notifications to all participants of an event
    Args:
        request: HTTP request object
        event_id (uuid): UUID of the event
        title (str): Title of the notification
        message (str): Message content of the notification
    Returns:
        JsonResponse: Response with status and message
    """
    try:
        event = Event.objects.get(id=event_id)
        notifications = create_event_notification(event, title, message)
        return JsonResponse({
            'status': 'success',
            'message': f'Notifications sent to {len(notifications)} participants',
        })
    except Event.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Event not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)