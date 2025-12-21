from django.shortcuts import render,get_object_or_404,redirect
from Authenticate.decorators import login_and_profile_required
from django.http import JsonResponse
from Event.models import Event
from django.db import transaction
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from .models import PinnedEvent
from django.core.exceptions import ValidationError

@login_and_profile_required
def show(request):
    if not hasattr(request.user, 'organizer_profile'):
        return redirect('Homepage:show_main')
    return render(request, 'dashboard.html')

@login_and_profile_required
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

@login_and_profile_required
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

def json_login_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required"}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped

def json_organizer_required(view_func):
    @json_login_required
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request.user, "organizer_profile"):
            return JsonResponse({"detail": "Organizer profile required"}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped

@csrf_exempt
@json_organizer_required
def api_list_pins(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    organizer_profile = request.user.organizer_profile

    pins = (
        PinnedEvent.objects
        .filter(user=request.user, event__organizer=organizer_profile)
        .select_related("event")
        .order_by("position", "created_at")
    )

    data = []
    for p in pins:
        e = p.event
        data.append({
            "pin_id": str(p.id),
            "position": p.position,
            "event": {
                "id": str(e.id),
                "name": e.name,
                "thumbnail": e.thumbnail,
                "start_time": e.start_time.isoformat() if e.start_time else None,
                "end_time": e.end_time.isoformat() if e.end_time else None,
                "location": e.location,
                "address": e.address,
                "sports_category": e.sports_category,
                "activity_category": e.activity_category,
                "fee": str(e.fee) if e.fee is not None else "Free",
                "capacity": e.capacity,
                "attendee_count": e.attendee.count(),
            }
        })

    return JsonResponse({"pins": data, "max_pinned": PinnedEvent.MAX_PINNED})

def _normalize_pin_positions(user, organizer_profile):
    pins = (
        PinnedEvent.objects
        .filter(user=user, event__organizer=organizer_profile)
        .order_by("position", "created_at")
    )
    with transaction.atomic():
        for idx, p in enumerate(pins, start=1):
            if p.position != idx:
                PinnedEvent.objects.filter(pk=p.pk).update(position=idx)

@csrf_exempt
@json_organizer_required
def api_toggle_pin(request, event_id):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    organizer_profile = request.user.organizer_profile
    event = get_object_or_404(Event, id=event_id, organizer=organizer_profile)

    existing = PinnedEvent.objects.filter(
        user=request.user,
        event=event,
    ).first()

    if existing:
        existing.delete()
        _normalize_pin_positions(request.user, organizer_profile)
        return JsonResponse({"status": "unpinned"})

    used_positions = set(
        PinnedEvent.objects
        .filter(user=request.user, event__organizer=organizer_profile)
        .values_list("position", flat=True)
    )

    next_pos = None
    for pos in range(1, PinnedEvent.MAX_PINNED + 1):
        if pos not in used_positions:
            next_pos = pos
            break

    if next_pos is None:
        return JsonResponse({"detail": "You can only pin 3 events"}, status=409)

    try:
        pin = PinnedEvent.objects.create(
            user=request.user,
            event=event,
            position=next_pos,
        )
        _normalize_pin_positions(request.user, organizer_profile)
        return JsonResponse({"status": "pinned", "pin_id": str(pin.id), "position": pin.position})
    except ValidationError as e:
        msg = e.messages[0] if getattr(e, "messages", None) else "Unable to pin event."
        return JsonResponse({"status": "error", "detail": msg}, status=409)
    
@csrf_exempt
@json_organizer_required
def api_move_pin(request, event_id):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        body = {}

    direction = body.get("direction")
    if direction not in ("left", "right"):
        return JsonResponse({"detail": "Invalid direction"}, status=400)

    organizer_profile = request.user.organizer_profile

    pin = (
        PinnedEvent.objects
        .filter(user=request.user, event_id=event_id, event__organizer=organizer_profile)
        .select_related("event")
        .first()
    )
    if not pin:
        return JsonResponse({"detail": "Pin not found"}, status=404)

    with transaction.atomic():
        if direction == "left":
            target = (
                PinnedEvent.objects
                .filter(user=request.user, event__organizer=organizer_profile, position__lt=pin.position)
                .order_by("-position")
                .first()
            )
        else:
            target = (
                PinnedEvent.objects
                .filter(user=request.user, event__organizer=organizer_profile, position__gt=pin.position)
                .order_by("position")
                .first()
            )

        if not target:
            return JsonResponse({"status": "noop", "position": pin.position})

        pin_pos = pin.position
        target_pos = target.position

        # swap
        PinnedEvent.objects.filter(pk=pin.pk).update(position=target_pos)
        PinnedEvent.objects.filter(pk=target.pk).update(position=pin_pos)

    return JsonResponse({"status": "ok"})