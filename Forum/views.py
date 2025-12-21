from django.shortcuts import render, redirect, get_object_or_404
from Authenticate.decorators import hybrid_login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from Event.models import Event
from Authenticate.models import Participant, Organizer
from .models import ForumPost
from .forms import ForumPostForm

# HELPER AND SERIALIZE POST + REPLIES (RECURSIVE)
def serialize_post(post):
    return {
        "id": post.id,
        "username": post.participant.username,
        "content": post.content,
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
        "replies": [
            serialize_post(reply)
            for reply in post.children.all().order_by("created_at")
        ],
    }

# WEB PAGE
@hybrid_login_required
def forum_page_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    participant = None
    organizer = None

    if hasattr(request.user, "participant_profile"):
        participant = request.user.participant_profile

    elif hasattr(request.user, "organizer_profile"):
        organizer = request.user.organizer_profile

        if event.organizer != organizer:
            return HttpResponseForbidden(
                "Organizer can only access forum of their own event."
            )

        participant, _ = Participant.objects.get_or_create(
            user=request.user,
            defaults={
                "full_name": organizer.organizer_name,
                "location": "-",
                "username": request.user.username,
                "password": request.user.password,
                "about": "Organizer account",
            },
        )
    else:
        return HttpResponseForbidden("Unauthorized user.")

    # HANDLE POST / REPLY
    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.event = event
            post.participant = participant

            parent_id = request.POST.get("parent_id")
            if parent_id:
                parent = ForumPost.objects.filter(id=parent_id).first()
                if parent:
                    post.parent = parent

            post.save()
            return redirect("Forum:forum_page", event_id=event.id)
    else:
        form = ForumPostForm()

    posts = ForumPost.objects.filter(
        event=event, parent=None
    ).order_by("-created_at")

    return render(
        request,
        "forum/forum_page.html",
        {
            "event": event,
            "posts": posts,
            "form": form,
            "participant": participant,
            "organizer": organizer,
        },
    )

# EDIT & DELETE
@hybrid_login_required
def edit_post_view(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)

    if post.participant.user != request.user:
        return HttpResponseForbidden("You cannot edit this post.")

    if request.method == "POST":
        form = ForumPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("Forum:forum_page", event_id=post.event.id)
    else:
        form = ForumPostForm(instance=post)

    return render(
        request,
        "forum/edit_post.html",
        {"form": form, "post": post},
    )


@hybrid_login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)

    if post.participant.user != request.user:
        return HttpResponseForbidden("You cannot delete this post.")

    event_id = post.event.id
    post.delete()
    return redirect("Forum:forum_page", event_id=event_id)

# API LIST (FLUTTER)
@csrf_exempt
@hybrid_login_required
def forum_api_add(request, event_id):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    event = get_object_or_404(Event, id=event_id)
    content = request.POST.get("content")

    if not content:
        return JsonResponse({"success": False, "error": "Empty content"}, status=400)

    # ROLE RESOLUTION (INI KUNCI)
    participant = getattr(request.user, "participant_profile", None)
    organizer = getattr(request.user, "organizer_profile", None)

    if not participant and not organizer:
        return JsonResponse(
            {"success": False, "error": "User has no role"},
            status=403
        )

    ForumPost.objects.create(
        event=event,
        participant=participant,
        organizer=organizer,
        content=content,
    )

    return JsonResponse({"success": True})

@hybrid_login_required
def forum_api_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    posts = ForumPost.objects.filter(
        event=event,
        parent__isnull=True
    ).order_by("-created_at")

    data = []
    for post in posts:
        if post.participant:
            username = post.participant.full_name
        elif post.organizer:
            username = f"{post.organizer.organizer_name} (Organizer)"
        else:
            username = "Anonymous"

        is_owner = False
        if post.participant and post.participant.user == request.user:
            is_owner = True
        elif post.organizer and post.organizer.user == request.user:
            is_owner = True

        data.append({
            "id": post.id,
            "username": username,
            "content": post.content,
            "created_at": post.created_at.isoformat(),
            "is_owner": is_owner,
        })

    return JsonResponse({"data": data}, safe=False)


@csrf_exempt
@hybrid_login_required
def forum_api_edit(request, post_id):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    post = get_object_or_404(ForumPost, id=post_id)
    
    is_owner = False
    if post.participant and post.participant.user == request.user:
        is_owner = True
    elif post.organizer and post.organizer.user == request.user:
        is_owner = True
        
    if not is_owner:
        return JsonResponse({"success": False, "error": "You cannot edit this post."}, status=403)

    content = request.POST.get("content")
    if not content:
        return JsonResponse({"success": False, "error": "Empty content"}, status=400)
        
    post.content = content
    post.save()
    
    return JsonResponse({"success": True})


@csrf_exempt
@hybrid_login_required
def forum_api_delete(request, post_id):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    post = get_object_or_404(ForumPost, id=post_id)
    
    is_owner = False
    if post.participant and post.participant.user == request.user:
        is_owner = True
    elif post.organizer and post.organizer.user == request.user:
        is_owner = True
        
    if not is_owner:
        return JsonResponse({"success": False, "error": "You cannot delete this post."}, status=403)
        
    post.delete()
    return JsonResponse({"success": True})


