# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.apps import apps
from Authenticate.models import Organizer
from .forms import EventForm
from .models import Event

# Ambil model Organizer dari app Authenticate tanpa hard import
Organizer = apps.get_model('Authenticate', 'Organizer')

def is_organizer(user) -> bool:
    # Aman untuk semua kondisi (login / tidak, superuser, dll)
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    # Cek existence via query biar gak kena DoesNotExist
    return Organizer.objects.filter(user=user).exists()

def organizer_required(view_func):
    @login_required(login_url='Authenticate:login')
    def _wrapped(request, *args, **kwargs):
        if not is_organizer(request.user):
            # Pilih salah satu:
            # 1) arahkan ke halaman "jadi organizer"
            messages.error(request, "Kamu belum terdaftar sebagai Organizer.")
            return redirect('Authenticate:be_organizer')  # ganti ke url kamu sendiri
            # 2) atau balikin 403:
            # from django.http import HttpResponseForbidden
            # return HttpResponseForbidden("Kamu bukan Organizer.")
        return view_func(request, *args, **kwargs)
    return _wrapped

@organizer_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            # dapatkan organizer yang terkait user (aman krn sudah lulus decorator)
            organizer = Organizer.objects.get(user=request.user)
            event = form.save(commit=False)
            event.organizer = organizer
            event.save()
            messages.success(request, "Event created 🎉")
           
            return redirect("dashboard:show")
    else:
        form = EventForm()
    return render(request, "create_event.html", {"form": form})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "event_detail.html", {"event": event})
