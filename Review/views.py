from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from events.models import Event
from authenticate.models import Profile

# Import model & form HANYA untuk Review
from .models import Review
from .forms import ReviewForm

@login_required
def add_review_view(request, event_id):
    
    # Hanya izinkan method POST
    if request.method != 'POST':
        return HttpResponseForbidden("Metode tidak diizinkan")

    # ambil data Event dan Profile
    try:
        event = get_object_or_404(Event, id=event_id)
        profile = get_object_or_404(Profile, user=request.user)
    except Exception as e:
        return render(request, 'review/error_dependency.html', {'error': str(e)})

    # cek apa user sudah pernah review (mencegah duplikat)
    if Review.objects.filter(event=event, profile=profile).exists():
        # (Nanti bisa diganti dengan 'messages' framework Django)
        print("Anda sudah pernah memberikan review untuk event ini.")
        return redirect('event_detail', event_id=event.id) # <--- ASUMSI aja ini mH

    # Proses form yang dikirim
    form = ReviewForm(request.POST)
    if form.is_valid():
        new_review = form.save(commit=False)
        new_review.event = event
        new_review.profile = profile
        new_review.save()
    else:
        print("Form review tidak valid:", form.errors)

    # Kembalikan user ke halaman detail event
    return redirect('event_detail', event_id=event.id)