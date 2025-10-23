from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from Event.models import Event
from Authenticate.models import Participant

# Import model & form HANYA untuk Review
from .models import Review
from .forms import ReviewForm


@login_required
def add_review_view(request, event_id):
    # Hanya izinkan method POST
    if request.method != 'POST':
        return HttpResponseForbidden("Metode tidak diizinkan")

    # Ambil data Event dan Participant
    try:
        event = get_object_or_404(Event, id=event_id)
        participant = get_object_or_404(Participant, user=request.user)
    except Exception as e:
        return render(request, 'review/error_dependency.html', {'error': str(e)})

    # Cek apakah user sudah pernah memberikan review untuk event ini
    if Review.objects.filter(event=event, participant=participant).exists():
        print("Anda sudah pernah memberikan review untuk event ini.")
        return redirect('event_detail', event_id=event.id)

    # Proses form yang dikirim
    form = ReviewForm(request.POST)
    if form.is_valid():
        new_review = form.save(commit=False)
        new_review.event = event
        new_review.participant = participant
        new_review.save()
    else:
        print("Form review tidak valid:", form.errors)

    # Kembalikan user ke halaman detail event
    return redirect('event_detail', event_id=event.id)
