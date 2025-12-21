# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Authenticate.decorators import login_and_profile_required
from django.apps import apps
from Authenticate.models import Organizer, Participant
from .forms import EventForm
import json
from django.utils.dateparse import parse_datetime
from .models import Event
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from Bookmark.models import Bookmark
from Notification.models import Notifications
from Follow.models import Follow
from Authenticate.models import Participant
from django.core.serializers import serialize


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
    @login_and_profile_required
    def _wrapped(request, *args, **kwargs):
        if not is_organizer(request.user):
            # Pilih salah satu:
            # 1) arahkan ke halaman "jadi organizer"
            return redirect('Homepage:show_main')
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
            print(request.POST)
            event.save()

            followers = Follow.objects.filter(user_to=organizer.user)
            for follower in followers:
                try:
                    participant = Participant.objects.get(user=follower.user_from)
                    Notifications.objects.create(
                        user=participant,
                        title="New Event from Organizer You Follow",
                        message=f"{organizer.user.username} has created a new event: {event.name}. Check it out!",
                        event=event
                    )
                    
                except Exception as e:
                    # if Notification app not available or any error, ignore to not block event creation
                    print("Failed to create notification for follower:", follower.user_from.user.username)
                    print("Error:", e)

           
            return redirect("dashboard:show")
    else:
        form = EventForm()
    return render(request, "create_event.html", {"form": form})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    is_bookmarked = False

    is_bookmarked = False

    # kalau user login, cek apakah event ini udah di-bookmark user
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, event=event).exists()


    is_participant = False
    if request.user.is_authenticated:
        is_participant = Participant.objects.filter(user=request.user).exists()

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
    return render(request, "event_detail.html", {"event": event, "formatted_fee": formatted_fee,"is_participant": is_participant, "is_bookmarked": is_bookmarked,})


Participant = apps.get_model('Authenticate', 'Participant')

@login_and_profile_required
@require_POST
def join_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # cek user-nya participant atau bukan
    try:
        participant = Participant.objects.get(user=request.user)
    except Participant.DoesNotExist:
        return JsonResponse({
            "ok": False,
            "error": "Kamu bukan participant."
        }, status=403)

    # kalau udah join sebelumnya
    if event.attendee.filter(id=participant.id).exists():
        return JsonResponse({
            "ok": False,
            "error": "Kamu sudah join event ini."
        }, status=400)

    # tambahin ke attendee
    event.attendee.add(participant)

    # create a notification for the participant to confirm join
    try:
        from Notification.models import Notifications as Notif
        Notif.objects.create(
            user=participant,
            title=f"Successfully Joined: {event.name}",
            message=f"You have successfully joined the event'{event.name}'. See event details for more information.",
            event=event
        )
    except Exception:
        # if Notification app not available or any error, ignore to not block join
        pass

    return JsonResponse({
        "ok": True,
        "joined_count": event.attendee.count(),
        "capacity": event.capacity,
    })

@organizer_required
def edit_event(request, event_id):
    # Ambil event yang mau diedit
    event = get_object_or_404(Event, id=event_id)

    # Pastikan ini event-nya organizer yang lagi login
    # (kalo beda owner, tolak aja biar aman)
    try:
        current_org = Organizer.objects.get(user=request.user)
    except Organizer.DoesNotExist:
        return redirect('Homepage:show_main')

    if event.organizer != current_org and not request.user.is_superuser:
        # ga boleh ngedit event orang lain
        return HttpResponseForbidden("Lu gak punya akses buat edit event ini.")

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            updated_event = form.save(commit=False)
            updated_event.organizer = current_org  # jaga-jaga aja, jangan sampe ke-unset
            updated_event.save()
            messages.success(request, "Event berhasil diupdate!")
            # setelah update mau kemana?
            # bisa balik ke dashboard atau ke detail event
            return redirect("dashboard:show")
            # atau:
            # return redirect("Event:event_detail", event_id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, "edit_event.html", {
        "form": form,
        "event": event,
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

@csrf_exempt
@require_POST
@csrf_exempt
@require_POST
def join_event_json(request, event_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "NOT_LOGGED_IN"},
            status=401
        )

    # --- PERBAIKAN MULAI DARI SINI ---
    # Import model Participant (pastikan path app-nya benar, misal 'Authenticate')
    from Authenticate.models import Participant
    
    try:
        # Cek apakah user ini terdaftar sebagai Participant
        participant = Participant.objects.get(user=request.user)
    except Participant.DoesNotExist:
        # Jika tidak ketemu, berarti bukan participant (bisa jadi Organizer atau Admin)
        return JsonResponse(
            {"status": "error", "message": "ONLY_PARTICIPANT_CAN_BOOK"},
            status=403
        )
    # --- PERBAIKAN SELESAI ---

    event = get_object_or_404(Event, id=event_id)

    # Cek apakah sudah join
    if event.attendee.filter(id=participant.id).exists():
        return JsonResponse(
            {"status": "error", "message": "ALREADY_JOINED"},
            status=409
        )

    # Join event
    try:
        event.attendee.add(participant)
        return JsonResponse(
            {"status": "success", "message": "JOINED"},
            status=200
        )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500
        )


def show_json(request):
    events = Event.objects.all()
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'thumbnail': event.thumbnail,
            'location': event.location,
            'address': event.address,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'sports_category': event.sports_category,
            'activity_category': event.activity_category,
            'fee': event.fee,
            'capacity': event.capacity,
            'organizer': event.organizer.user.username,

            'attendees_count': event.attendee.count(),
        })
    return JsonResponse({'status':'success','events': event_list}, safe=False)

def show_event_by_id_json(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    organizer_obj = event.organizer
    org_pic = ""
    if organizer_obj.profile_picture:
        org_pic = organizer_obj.profile_picture.name

    recent_attendees = event.attendee.all()[:3]
    attendees_avatars = []
    for participant in recent_attendees:
        if participant.profile_picture:
            attendees_avatars.append(participant.profile_picture.name)
        else:
            attendees_avatars.append("")

    is_joined = False
    if request.user.is_authenticated:
        if hasattr(request.user, 'participant_profile'):
            current_participant = request.user.participant_profile
            if event.attendee.filter(id=current_participant.id).exists():
                is_joined = True

    event_data = {
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'thumbnail': event.thumbnail if event.thumbnail else '', 
        'location': event.location,
        'address': event.address,
        'start_time': event.start_time,
        'end_time': event.end_time,
        'sports_category': event.sports_category,
        'activity_category': event.activity_category,
        'fee': event.fee,
        'capacity': event.capacity,

        'organizer': {
            'username': organizer_obj.user.username,
            'full_name': organizer_obj.organizer_name,
            'profile_picture': org_pic
        },
        'attendees': {
            'count': event.attendee.count(),
            'avatars': attendees_avatars
        },
        'is_joined': is_joined
    }
    
    return JsonResponse({'status':'success', 'event': event_data}, safe=False)

def get_event_attendees(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    all_participants = event.attendee.all()
    
    data_list = []
    
    for user in all_participants:
        full_name = user.username
        profile_picture = None
        if hasattr(user, 'participant_profile'):
            profile = user.participant_profile
            full_name = profile.full_name if profile.full_name else user.username
            
            if profile.profile_picture:
                profile_picture = profile.profile_picture.url
        
        data_list.append({
            'username': user.username,
            'full_name': full_name,
            'profile_picture': profile_picture
        })
        
    return JsonResponse({'status': 'success', 'data': data_list})

@csrf_exempt
@require_POST
def create_event_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Harus login dulu."}, status=401)

    if not is_organizer(request.user):
        return JsonResponse({"status": "error", "message": "Kamu bukan organizer."}, status=403)

    try:
        data = json.loads(request.body)
        user = request.user
        organizer = Organizer.objects.get(user=user)

        # Handle Fee logic: Kalau kosong/tidak dikirim, anggap 0
        fee_input = data.get("fee", "0")
        if not fee_input: 
            fee_input = "0"
            
        new_event = Event.objects.create(
            organizer=organizer,
            name=data["name"],
            description=data["description"],
            # Ambil thumbnail sebagai string URL sesuai form HTML
            thumbnail=data.get("thumbnail", ""), 
            location=data["location"],
            address=data["address"],
            start_time=parse_datetime(data["start_time"]),
            end_time=parse_datetime(data["end_time"]),
            sports_category=data["sports_category"],
            activity_category=data["activity_category"],
            fee=int(fee_input),
            capacity=int(data["capacity"]),
        )
        
        new_event.save()

        return JsonResponse({"status": "success", "message": "Event berhasil dibuat!"}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    

@csrf_exempt
@require_POST
def delete_event_flutter(request, event_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Harus login dulu."}, status=401)

    event = get_object_or_404(Event, id=event_id)

    # Pastikan yang menghapus adalah owner-nya
    if event.organizer.user != request.user:
        return JsonResponse({"status": "error", "message": "Bukan pemilik event."}, status=403)

    event.delete()
    return JsonResponse({"status": "success", "message": "Event berhasil dihapus!"})

@csrf_exempt
@require_POST
def edit_event_flutter(request, event_id): # Buat fungsi baru khusus edit
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Harus login dulu."}, status=401)

    event = get_object_or_404(Event, id=event_id)
    if event.organizer.user != request.user:
        return JsonResponse({"status": "error", "message": "Bukan pemilik event."}, status=403)

    try:
        data = json.loads(request.body)
        event.name = data["name"]
        event.description = data["description"]
        event.thumbnail = data.get("thumbnail", "")
        event.location = data["location"]
        event.address = data["address"]
        event.start_time = parse_datetime(data["start_time"])
        event.end_time = parse_datetime(data["end_time"])
        event.sports_category = data["sports_category"]
        event.activity_category = data["activity_category"]
        event.fee = int(data.get("fee", "0") or 0)
        event.capacity = int(data["capacity"])
        
        event.save()
        return JsonResponse({"status": "success", "message": "Event berhasil diupdate!"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
