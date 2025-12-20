from django.shortcuts import render
from django.http import JsonResponse
from Authenticate.decorators import login_and_profile_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect
from Event.models import Event
from .models import Bookmark
from django.utils.html import strip_tags
from django.contrib import messages
from django.core.exceptions import ValidationError


@login_and_profile_required
@csrf_exempt
def toggle_bookmark(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user
    raw_note = request.POST.get("note") or ""
    clean_note = strip_tags(raw_note).strip()

    bookmark, created = Bookmark.objects.get_or_create(user=user, event=event, defaults={"note": clean_note})

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
    return render(request, "bookmark.html", {
        "bookmarks": bookmarks,
        "bookmarked_ids": bookmarked_ids,
    })

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
