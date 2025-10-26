from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from Event.models import Event
from Authenticate.models import Participant, Organizer
from .models import ForumPost
from .forms import ForumPostForm


@login_required
def forum_page_view(request, event_id):
    """
    Menampilkan halaman forum untuk satu event.
    Participant bisa posting.
    Organizer bisa posting hanya untuk event miliknya.
    """
    event = get_object_or_404(Event, id=event_id)

    participant = None
    organizer = None
    poster_type = None  # buat tracking apakah participant atau organizer

    # Cek tipe user
    if hasattr(request.user, "participant_profile"):
        participant = request.user.participant_profile
        poster_type = "participant"
    elif hasattr(request.user, "organizer_profile"):
        organizer = request.user.organizer_profile
        poster_type = "organizer"
    else:
        return HttpResponseForbidden("User tidak terdaftar sebagai participant atau organizer.")

    # Handle POST
    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.event = event

            if participant:
                # Participant bisa post ke semua event
                new_post.participant = participant
            elif organizer:
                # Organizer hanya boleh post kalau event miliknya
                if event.organizer == organizer:
                    new_post.organizer = organizer
                else:
                    return HttpResponseForbidden("Organizer can only post on their own event.")
            else:
                return HttpResponseForbidden("No access.")
            
            parent_id = request.POST.get("parent_id")
            if parent_id:
                parent_post = ForumPost.objects.filter(id=parent_id).first()
                if parent_post:
                    new_post.parent = parent_post

            new_post.save()
            return redirect("Forum:forum_page", event_id=event.id)
    else:
        form = ForumPostForm()

    posts = ForumPost.objects.filter(event=event, parent=None).order_by("-created_at")

    context = {
        "event": event,
        "posts": posts,
        "form": form,
        "participant": participant,
        "organizer": organizer,
        "poster_type": poster_type,
    }

    return render(request, "forum/forum_page.html", context)