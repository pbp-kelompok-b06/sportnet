from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from Event.models import Event
from Authenticate.models import Participant
from .models import ForumPost
from .forms import ForumPostForm


@login_required
def forum_page_view(request, event_id):
    """
    Menampilkan halaman forum untuk satu event + menambah post/balasan
    """
    event = get_object_or_404(Event, id=event_id)
    participant = get_object_or_404(Participant, user=request.user)

    # POST = kirim posting atau balasan
    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.event = event
            new_post.profile = participant  # GANTI dari profile → participant

            parent_id = request.POST.get("parent_id")
            if parent_id:
                parent_post = ForumPost.objects.filter(id=parent_id).first()
                if parent_post:
                    new_post.parent = parent_post

            new_post.save()
            return redirect("Forum:forum_page", event_id=event.id)
    else:
        form = ForumPostForm()

    # ambil semua post utama (tanpa parent)
    posts = ForumPost.objects.filter(event=event, parent=None).order_by("-created_at")

    context = {
        "event": event,
        "posts": posts,
        "form": form,
        "participant": participant,
    }

    return render(request, "forum/forum_page.html", context)
