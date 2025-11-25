from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from Event.models import Event
from Authenticate.models import Participant

# Import model & form HANYA untuk Review
from .models import Review
from .forms import ReviewForm


@login_required
def review_page_view(request, event_id):
    authen = True
    event = get_object_or_404(Event, id=event_id)
    participant = get_object_or_404(Participant, user=request.user)
    reviews = Review.objects.filter(event=event).order_by("-created_at")

    if Review.objects.filter(event=event, participant=participant).exists():
        authen = False
    
    if request.method == "POST" and authen:
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
        "form": form,
        "reviews": reviews,
        "participant": participant,
        "authen": authen,
    })

@login_required
def edit_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Cek author
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
        "review": review
    })

@login_required
def delete_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Cek author
    if review.participant.user != request.user:
        return HttpResponseForbidden("You cannot delete this review.")

    event_id = review.event.id
    review.delete()

    return redirect("Review:review_page", event_id=event_id)

