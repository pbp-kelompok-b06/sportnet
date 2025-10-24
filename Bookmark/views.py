from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from Event.models import Event
from .models import Bookmark

# Create your views here.
def show_bookmark(request):
    return render(request, 'bookmark.html')

@login_required
@csrf_exempt
def toggle_bookmark(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user

    bookmark, created = Bookmark.objects.get_or_create(user=user, event=event)

    if not created:
        # udah ada, berarti remove
        bookmark.delete()
        status = "removed"
    else:
        status = "added"

    return JsonResponse({"status": status})

@login_required
def show_bookmark(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related("event")
    events = [b.event for b in bookmarks]
    bookmarked_ids = [b.event.id for b in bookmarks]

    return render(request, "bookmark.html", {
        "events": events,
        "bookmarked_ids": bookmarked_ids,
    })