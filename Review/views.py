from django.shortcuts import render, redirect, get_object_or_404
from Authenticate.decorators import *
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from Event.models import Event
from Authenticate.models import Participant
from .models import Review
from .forms import ReviewForm

# =========================
# WEB VIEW (HTML)
# =========================

@hybrid_login_required
def review_page_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    reviews = Review.objects.filter(event=event).order_by("-created_at")

    participant = None
    authen = False

    if hasattr(request.user, "participant_profile"):
        participant = request.user.participant_profile
        if not Review.objects.filter(event=event, participant=participant).exists():
            authen = True

    if request.method == "POST":
        if not participant or not authen:
            return HttpResponseForbidden("Not allowed")

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.event = event
            review.participant = participant
            review.save()
            return redirect("Review:review_page", event_id=event.id)
    else:
        form = ReviewForm()

    return render(
        request,
        "review/review_page.html",
        {
            "event": event,
            "reviews": reviews,
            "form": form,
            "participant": participant,
            "authen": authen,
        },
    )


@hybrid_login_required
def edit_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if not hasattr(request.user, "participant_profile"):
        return HttpResponseForbidden("Only participant can edit review")

    if review.participant.user != request.user:
        return HttpResponseForbidden("You cannot edit this review")

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("Review:review_page", event_id=review.event.id)
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "review/edit_review.html",
        {
            "form": form,
            "review": review,
        },
    )


@hybrid_login_required
def delete_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if not hasattr(request.user, "participant_profile"):
        return HttpResponseForbidden("Only participant can delete review")

    if review.participant.user != request.user:
        return HttpResponseForbidden("You cannot delete this review")

    event_id = review.event.id
    review.delete()
    return redirect("Review:review_page", event_id=event_id)


# =========================
# API (FLUTTER)
# =========================

@csrf_exempt
@hybrid_login_required
def review_api_add(request, event_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

    event = get_object_or_404(Event, id=event_id)

    if not hasattr(request.user, "participant_profile"):
        return JsonResponse(
            {"success": False, "error": "Only participant allowed"},
            status=403,
        )

    participant = request.user.participant_profile

    if Review.objects.filter(event=event, participant=participant).exists():
        return JsonResponse(
            {"success": False, "error": "Already reviewed"},
            status=400,
        )

    rating = request.POST.get("rating")
    comment = request.POST.get("comment")

    if not rating or not comment:
        return JsonResponse(
            {"success": False, "error": "Invalid data"},
            status=400,
        )

    Review.objects.create(
        event=event,
        participant=participant,
        rating=int(rating),
        comment=comment,
    )

    return JsonResponse({"success": True})

def review_api_list(request, event_id):
    if request.method != "GET":
        return JsonResponse(
            {"success": False, "error": "Invalid method"},
            status=405
        )

    event = get_object_or_404(Event, id=event_id)

    reviews = Review.objects.filter(event=event).order_by("-created_at")

    data = []
    for review in reviews:
        data.append({
            "id": review.id,
            "username": review.participant.username,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    return JsonResponse(data, safe=False)
