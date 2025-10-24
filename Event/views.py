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
           
            return redirect("dashboard:show")
    else:
        form = EventForm()
    return render(request, "create_event.html", {"form": form})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # --- format fee jadi "K" ---
    fee_val = event.fee if event.fee is not None else 0

    try:
        fee_val = int(fee_val)
    except (TypeError, ValueError):
        fee_val = 0

    # fee udah divalidasi kelipatan 100 dan max 9,999,999 (info dari kamu)
    # aturan:
    # 125000  -> 125K
    # 125500  -> 125.5K
    fee_val = int(event.fee or 0)   
    fee_val = round(fee_val / 100) * 100

    if fee_val < 1000:
        formatted_fee = str(fee_val)
    else:
        ribu = fee_val / 1000  # float

        if fee_val % 1000 == 0:
            # contoh 125000 -> 125.0 -> 125K
            formatted_fee = f"{int(ribu)}K"
        else:
            # contoh 125500 -> 125.5K
            formatted_fee = f"{ribu:.1f}K"
    return render(request, "event_detail.html", {"event": event, "formatted_fee": formatted_fee,})

