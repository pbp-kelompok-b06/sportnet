from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Event.models import Event
from Authenticate.models import Organizer
import json

@login_required(login_url='authenticate/')
def show(request):
    if not hasattr(request.user, 'organizer_profile'):
        return redirect('Homepage:show_homepage')
    return render(request, 'dashboard.html')

@login_required(login_url='authenticate/')
def get_organizer_events_json(request):
    try:
        organizer_profile = request.user.organizer_profile
        events = organizer_profile.owned_events.all().order_by('-start_time')

        event_list =[]
        for event in events:
            event_list.append({
                'id' : str(event.id),
                'name' : event.name,
                'thumbnail' : event.thumbnail,
                'start_time' : event.start_time.strftime('%d %b %Y, %H:%M'),
                'end_time' : event.end_time.strftime('%d %b %Y, %H:%M') if event.end_time else None,
                'location' : event.location,
                'address' : event.address,
                "sports_category": event.get_sports_category_display(),
                "activity_category": event.get_activity_category_display(),
                'fee' : str(event.fee) if event.fee is not None else 'Free',
                'capacity' : event.capacity,
                'attendee_count': event.attendee.count(),
                'edit_url': f'/event/edit/{event.id}/',
            })

        return JsonResponse({'events' : event_list})
    except Exception as e:
        return JsonResponse({'error': str(e), 'events': []}, status=500)

@login_required(login_url='authenticate/')
def delete_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)

        if event.organizer == request.user.organizer_profile:
            # Notify all attendees before deleting the event
            try:
                from Notification.models import Notifications as Notif
                attendees = list(event.attendee.all())
                for participant in attendees:
                    try:
                        Notif.objects.create(
                            user=participant,
                            title=f"Event Cancelled: {event.name}",
                            message=f"Unfortunately, The event '{event.name}' has been cancelled by the organizer.",
                            event=None
                        )
                    except Exception:
                        # ignore individual failures
                        print(f'Failed to notify participant {participant} about event deletion.')
                        pass
            except Exception:
                # Notification app missing or other error; continue with deletion
                pass
            
            event.delete()
            return JsonResponse({'status': 'success', 'message': 'Event berhasil dihapus.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Anda tidak punya izin untuk menghapus event ini.'}, status=403)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)