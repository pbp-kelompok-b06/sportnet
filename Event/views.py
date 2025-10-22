from django.shortcuts import render, redirect
from .forms import EventForm

def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            # setelah berhasil simpan, balik lagi ke halaman create (atau ganti ke list/detail kalau sudah ada)
            return redirect("Event:create_event")
    else:
        form = EventForm()

    return render(request, "create_event.html", {"form": form})
