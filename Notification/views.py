from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from Notification.models import Notifications as Notif
from Event.models import Event
from Authenticate.models import Participant
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

@login_required
def check_new_notifications(request):
    """Check for new notifications in the last 30 seconds"""
    try:
        participant = request.user.participant_profile
        recent_time = timezone.now() - timedelta(seconds=30)
        has_new = Notif.objects.filter(
            user=participant,
            is_read=False,
            timestamp__gte=recent_time
        ).exists()
        return JsonResponse({'hasNew': has_new})
    except Exception:
        return JsonResponse({'hasNew': False})

@login_required
def show_all(request):
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


@login_required
@require_POST
def mark_notification_read(request, notif_id):
    
    notif = get_object_or_404(Notif, pk=notif_id)

    # Ensure the logged-in user is the owner of the notification
    try:
        participant = request.user.participant_profile
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'User has no participant profile'}, status=403)

    if notif.user != participant:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)

    notif.is_read = True
    notif.save()

    return JsonResponse({'status': 'success', 'message': 'Notification marked as read'})


@login_required
@require_POST
def mark_all_read(request):
    
    try:
        participant = request.user.participant_profile
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'User has no participant profile'}, status=403)

    qs = Notif.objects.filter(user=participant, is_read=False)
    updated = qs.update(is_read=True)

    return JsonResponse({'status': 'success', 'updated': updated})