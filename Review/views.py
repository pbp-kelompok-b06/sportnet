from django.shortcuts import render, redirect, get_object_or_404
from Authenticate.decorators import login_and_profile_required
from django.http import HttpResponseForbidden

from Event.models import Event
from Authenticate.models import Participant, Organizer
from .models import Review
from .forms import ReviewForm


@login_and_profile_required
def review_page_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    reviews = Review.objects.filter(event=event).order_by("-created_at")

    participant = None
    organizer = None
    authen = False  # apakah user boleh bikin review

    # === ROLE CHECK ===
    if hasattr(request.user, "participant_profile"):
        participant = request.user.participant_profile

        # participant hanya boleh 1 review per event
        if not Review.objects.filter(event=event, participant=participant).exists():
            authen = True

    elif hasattr(request.user, "organizer_profile"):
        organizer = request.user.organizer_profile
        # organizer hanya boleh lihat, authen tetap False

    else:
        return HttpResponseForbidden("Unauthorized user.")

    # === HANDLE CREATE REVIEW (PARTICIPANT ONLY) ===
    if request.method == "POST":
        if not participant:
            return HttpResponseForbidden("Only participants can create reviews.")

        if not authen:
            return HttpResponseForbidden("You have already reviewed this event.")

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.event = event
            review.participant = participant
            review.save()
            return redirect("Review:review_page", event_id=event.id)

    else:
        form = ReviewForm()

    return render(request, "review/review_page.html", {
        "event": event,
        "reviews": reviews,
        "form": form,
        "participant": participant,
        "organizer": organizer,
        "authen": authen,
    })


@login_and_profile_required
def edit_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # hanya participant pemilik review
    if not hasattr(request.user, "participant_profile"):
        return HttpResponseForbidden("Only participants can edit reviews.")

    if review.participant.user != request.user:
        return HttpResponseForbidden("You cannot edit this review.")

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("Review:review_page", event_id=review.event.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, "review/edit_review.html", {
        "form": form,
        "review": review,
    })


@login_and_profile_required
def delete_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # hanya participant pemilik review
    if not hasattr(request.user, "participant_profile"):
        return HttpResponseForbidden("Only participants can delete reviews.")

    if review.participant.user != request.user:
        return HttpResponseForbidden("You cannot delete this review.")

    event_id = review.event.id
    review.delete()
    return redirect("Review:review_page", event_id=event_id)
