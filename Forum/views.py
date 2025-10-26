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
    
    try:
        event = get_object_or_404(Event, id=event_id)
        participant = get_object_or_404(Participant, user=request.user)
        print("Fetched event and participant successfully." + str(event) + " " + str(participant))
    except Exception as e:
        print("Error fetching event or participant:", str(e))
        return HttpResponseForbidden("error fetching event or participant.")

    # POST = kirim posting atau balasan
    try:
        print("Request method:", request.method)
        if request.method == "POST":
            form = ForumPostForm(request.POST)
            if form.is_valid():
                new_post = form.save(commit=False)
                new_post.event = event
                new_post.participant = participant  # GANTI dari profile → participant
                print("New post participant =", new_post.participant.id)

                parent_id = request.POST.get("parent_id")
                if parent_id:
                    parent_post = ForumPost.objects.filter(id=parent_id).first()
                    if parent_post:
                        new_post.parent = parent_post
                
                print("Saving new post:", new_post)
                new_post.save()


                return redirect("Forum:forum_page", event_id=event.id)
        else:
            form = ForumPostForm()
    except Exception as e:
        print("Error handling POST request:", str(e))
        return HttpResponseForbidden("error handling POST request.")

    # ambil semua post utama (tanpa parent)
    try:
        posts = ForumPost.objects.filter(event=event, parent=None).order_by("-created_at")
        print(posts)
    except Exception as e:
        posts = []
        print("No posts found OR error fetching posts:", str(e))
        return HttpResponseForbidden("No posts found for this event.")

    context = {
        "event": event,
        "posts": posts,
        "form": form,
        "participant": participant,
    }
    

    print("Rendering forum page for event:", event.name)
    return render(request, "forum/forum_page.html", context)
