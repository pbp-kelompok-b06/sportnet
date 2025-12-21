from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from Authenticate.decorators import login_and_profile_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from Event.models import Event
from .models import Bookmark
import json

def json_login_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required"}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped

@login_and_profile_required
@csrf_exempt
def toggle_bookmark(request, event_id):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    event = get_object_or_404(Event, id=event_id)
    user = request.user

    # Baca JSON body dulu, kalau gagal baru coba POST form
    raw_note = ""
    if request.body:
        try:
            body = json.loads(request.body.decode("utf-8"))
            raw_note = body.get("note") or ""
        except Exception:
            pass

    if not raw_note:
        raw_note = request.POST.get("note") or ""

    clean_note = strip_tags(raw_note).strip()

    bookmark, created = Bookmark.objects.get_or_create(
        user=user,
        event=event,
        defaults={"note": clean_note},
    )

    if not created:
        # udah ada, berarti remove
        bookmark.delete()
        status = "removed"
    else:
        status = "added"

    return JsonResponse({"status": status})

@login_and_profile_required
def show_bookmark(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related("event")
    bookmarked_ids = [b.event.id for b in bookmarks]
    return render(
        request,
        "bookmark.html",
        {
            "bookmarks": bookmarks,
            "bookmarked_ids": bookmarked_ids,
        },
    )


@login_and_profile_required
@csrf_exempt
def update_note(request, event_id):
    if request.method != "POST":
        return redirect("Bookmark:show_bookmark")

    event = get_object_or_404(Event, id=event_id)
    bookmark = get_object_or_404(Bookmark, user=request.user, event=event)

    raw_note = request.POST.get("note") or ""
    clean_note = strip_tags(raw_note).strip()
    bookmark.note = clean_note
    try:
        bookmark.save()
    except ValidationError as e:
        errors = []
        if hasattr(e, "message_dict"):
            for field_errors in e.message_dict.values():
                errors.extend(field_errors)
        else:
            errors.extend(e.messages)

    return redirect("Bookmark:show_bookmark")


@csrf_exempt
@json_login_required
def api_list_bookmarks(request):
    """
    GET: list semua bookmark user dalam bentuk JSON
    untuk dikonsumsi Flutter.
    """
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    bookmarks = Bookmark.objects.filter(user=request.user).select_related("event")

    data = []
    for b in bookmarks:
        event = b.event
        data.append(
            {
                # PK UUID -> kirim sebagai string
                "event_id": str(event.id),
                "event_name": event.name,
                "thumbnail": event.thumbnail,
                "start_time": event.start_time.isoformat()
                if event.start_time
                else None,
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "location": event.location,
                "sports_category": event.sports_category,
                "activity_category": event.activity_category,
                "fee": str(event.fee) if event.fee is not None else None,
                "note": b.note or "",
            }
        )

    return JsonResponse({"bookmarks": data})

@csrf_exempt
@json_login_required
def api_update_note(request, event_id):
    """
    POST: update note bookmark (JSON) untuk konsumsi Flutter.
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    event = get_object_or_404(Event, id=event_id)
    bookmark = get_object_or_404(Bookmark, user=request.user, event=event)

    raw_note = ""
    if request.body:
        try:
            body = json.loads(request.body.decode("utf-8"))
            raw_note = body.get("note") or ""
        except Exception:
            pass
    if not raw_note:
        raw_note = request.POST.get("note") or ""

    clean_note = strip_tags(raw_note).strip()
    bookmark.note = clean_note

    try:
        bookmark.save()
        return JsonResponse({"status": "ok", "note": bookmark.note})
    except ValidationError as e:
        errors = []
        if hasattr(e, "message_dict"):
            for field_errors in e.message_dict.values():
                errors.extend(field_errors)
        else:
            errors.extend(e.messages)
        return JsonResponse({"status": "error", "errors": errors}, status=400)
    
@csrf_exempt
@json_login_required
def api_toggle_bookmark(request, event_id):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    event = get_object_or_404(Event, id=event_id)
    user = request.user

    # ambil note dari JSON body (atau fallback form)
    raw_note = ""
    if request.body:
        try:
            body = json.loads(request.body.decode("utf-8"))
            raw_note = body.get("note") or ""
        except Exception:
            raw_note = ""
    if not raw_note:
        raw_note = request.POST.get("note") or ""

    clean_note = strip_tags(raw_note).strip()

    bookmark = Bookmark.objects.filter(user=user, event=event).first()
    if bookmark:
        bookmark.delete()
        return JsonResponse({"status": "removed"})
    else:
        Bookmark.objects.create(user=user, event=event, note=clean_note)
        return JsonResponse({"status": "added", "note": clean_note})