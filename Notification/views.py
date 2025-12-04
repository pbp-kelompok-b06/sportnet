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

def delete_notif(request, notif_id):
    notif = get_object_or_404(Notif, pk=notif_id)
    notif.delete()
    return redirect('Notification:show_all')

def handleD_1():
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
                    print(f'Failed to create notification for participant {participant}: {e}')
                    continue

       
        print(f'Sent {total} reminder notifications for events on {tomorrow}')
        
def handleNow():
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
                print(f'Failed to create notification for participant {participant}: {e}')
                continue
            
            print(f'Sent {total} reminder notifications for events on {now}')         
            
@login_required
def notif_json(request):
    try:
        participant = request.user.participant_profile
        notifications = Notif.objects.filter(user=participant).order_by('-timestamp')
    except Exception:
        notifications = Notif.objects.none()
    notif_list = []
    for notif in notifications:
        notif_list.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'is_read': notif.is_read,
            'timestamp': notif.timestamp.isoformat(),
            'event_id': notif.event.id if notif.event else None,
        })
    return JsonResponse({'notifications': notif_list})