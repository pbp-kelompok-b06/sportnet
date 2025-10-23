from django.shortcuts import render, redirect, get_object_or_404
from .forms import EventForm
from .models import Event

def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            # setelah berhasil simpan, balik lagi ke halaman create (atau ganti ke list/detail kalau sudah ada)
            return redirect("Homepage:show_main")
    else:
        form = EventForm()

    return render(request, "create_event.html", {"form": form})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "event_detail.html", {"event": event})
