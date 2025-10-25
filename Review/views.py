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
    event = get_object_or_404(Event, id=event_id)
    participant = get_object_or_404(Participant, user=request.user)
    reviews = Review.objects.filter(event=event).order_by("-created_at")

    if request.method == "POST":
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
    })
