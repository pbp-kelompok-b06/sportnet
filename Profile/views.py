from django.contrib.auth import logout
import json
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from Authenticate.decorators import login_and_profile_required
from django.contrib import messages
from Authenticate.models import Organizer, Participant
from django.contrib.auth.models import User
from Profile.forms import *
from django.views.decorators.csrf import csrf_exempt
import base64
from django.core.files.base import ContentFile
from django.utils import timezone
from Follow.models import Follow

@csrf_exempt
@login_and_profile_required
def profile_api(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Not authenticated"}, status=401)
        profile_user = request.user
    
    is_me = (request.user.is_authenticated and request.user == profile_user)
    data = {}
    role = ""

    followers_count = Follow.objects.filter(user_to=profile_user).count()
    following_count = Follow.objects.filter(user_from=profile_user).count()

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(user_from=request.user, user_to=profile_user).exists()
    
    try:
        participant_profile = Participant.objects.get(user=profile_user)
        role = "participant"
        
        booked_data = None
        following_people = []

        if is_me:
            now = timezone.now()
            all_booked = participant_profile.events_joined.all().order_by('start_time')
            upcoming = all_booked.filter(start_time__gte=now)
            past = all_booked.filter(start_time__lt=now).order_by('-start_time')

            booked_data = {
                "upcoming": [
                    {
                        "id": event.id,
                        "name": event.name,
                        "start_time": event.start_time.strftime("%Y-%m-%d %H:%M"),
                        "thumbnail": event.thumbnail if event.thumbnail else None, 
                    } for event in upcoming
                ],
                "past": [
                    {
                        "id": event.id,
                        "name": event.name,
                        "start_time": event.start_time.strftime("%Y-%m-%d %H:%M"),
                        "thumbnail": event.thumbnail if event.thumbnail else None,
                    } for event in past
                ]
            }
            my_follows = Follow.objects.filter(user_from=profile_user).select_related('user_to')
            
            for follow in my_follows:
                organizer_user = follow.user_to
                if hasattr(organizer_user, 'organizer_profile'):
                    org_profile = organizer_user.organizer_profile
                    following_people.append({
                        "username": organizer_user.username,
                        "organizer_name": org_profile.organizer_name,
                        "profile_picture": org_profile.profile_picture.url if org_profile.profile_picture else None
                    })

        profile_data = {
            "full_name": participant_profile.full_name,
            "location": participant_profile.location,
            "interests": participant_profile.interests,
            "birth_date": participant_profile.birth_date.strftime("%Y-%m-%d") if participant_profile.birth_date else None,
            "about": participant_profile.about,
            "profile_picture": participant_profile.profile_picture.url if participant_profile.profile_picture else None,
            "stats": {
                "following_count": following_count, 
                "followers_count": 0,

                "following_list": following_people 
            },
            "booked_events": booked_data
        }

    except Participant.DoesNotExist:
        try:
            organizer_profile = Organizer.objects.get(user=profile_user)
            role = "organizer"
            
            my_events_query = organizer_profile.owned_events.all().order_by('-start_time')
            
            my_events_list = [
                {
                    "id": event.id,
                    "name": event.name,
                    "start_time": event.start_time.strftime("%Y-%m-%d %H:%M"),
                    "thumbnail": event.thumbnail if event.thumbnail else None, 
                    "location": event.location,
                    "sports_category": event.get_sports_category_display(), 
                } for event in my_events_query
            ]

            profile_data = {
                "organizer_name": organizer_profile.organizer_name,
                "contact_email": organizer_profile.contact_email,
                "contact_phone": organizer_profile.contact_phone,
                "about": organizer_profile.about,
                "profile_picture": organizer_profile.profile_picture.url if organizer_profile.profile_picture else None,
                "stats": {
                    "followers_count": followers_count,
                    "following_count": 0 
                },
                "organized_events": my_events_list 
            }
        except Organizer.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Profile not found"}, status=404)
        
    response_data = {
        "status": "success",
        "user": {
            "id": profile_user.id,
            "username": profile_user.username,
            "role": role,
            "is_me": is_me, 
        },
        "profile": profile_data,
        "is_following": is_following,
    }
    return JsonResponse(response_data)


@login_and_profile_required
def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        if not request.user.is_authenticated:
            return redirect('Authenticate:login')
        profile_user = request.user

    context = {}
    
    is_following = False
    followers_count = 0

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(user_from=request.user, user_to=profile_user).exists()
    

    try:
        participant_profile = Participant.objects.get(user=profile_user)
        
        all_booked_events = participant_profile.events_joined.order_by('start_time')
        now = timezone.now()

        upcoming_events = all_booked_events.filter(start_time__gte=now)
        past_events = all_booked_events.filter(start_time__lt=now).order_by('-start_time')

        following_list = Follow.objects.filter(user_from=profile_user).select_related('user_to')
        following_count = following_list.count()

        context = {
            'profile_user': profile_user,
            'participant': participant_profile,
            'upcoming_events': upcoming_events,
            'past_events': past_events,
            'following_list': following_list, 
            'following_count': following_count,
        }

    except Participant.DoesNotExist:
        try:
            organizer_profile = Organizer.objects.get(user=profile_user)
            
            my_events = organizer_profile.owned_events.all().order_by('-start_time')

            
            followers_list = Follow.objects.filter(user_to=profile_user).select_related('user_from')
            followers_count = followers_list.count()
            context = {
                'profile_user': profile_user, 
                'organizer': organizer_profile,
                'my_events': my_events,
                'is_following': is_following,   # untuk button follow / unfollow
                'followers_count': followers_count,
                'followers_list': followers_list,
            }
        except Organizer.DoesNotExist:
            messages.error(request, 'Profil tidak ditemukan.')
            return redirect('Homepage:show_main')

    return render(request, 'profile.html', context)

@csrf_exempt
@login_and_profile_required
def edit_profile(request):
    user = request.user
    ProfileForm = None
    profile_instance = None

    if hasattr(user, 'participant_profile'):
        ProfileForm = ProfileFormParticipant
        profile_instance = user.participant_profile
    elif hasattr(user, 'organizer_profile'):
        ProfileForm = ProfileFormOrganizer
        profile_instance = user.organizer_profile
    else:
        messages.error(request, "Profile tidak ditemukan untuk diedit")
        return redirect('Homepage:show_main')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile berhasil diperbarui!')
            return redirect('profile:profile_view')
    else:
        form = ProfileForm(instance=profile_instance)
    
    return render(request, 'edit_profile.html', {'form': form})

@csrf_exempt
@login_and_profile_required
def edit_profile_api(request):
    if request.method == 'POST':
        try:
            # mengambil data JSON dari body request
            data = json.loads(request.body.decode('utf-8'))
            user = request.user
            profile = None
            
            profile_picture_base64 = data.get("profile_picture_base64", None)
            profile_picture_file = None

            # menangani gambar profile base64
            if profile_picture_base64 and profile_picture_base64 != "":
                try:
                    if ";base64," in profile_picture_base64:
                        format, imgstr = profile_picture_base64.split(';base64,')
                        ext = format.split('/')[-1]
                    else:
                        imgstr = profile_picture_base64
                        ext = "jpeg" 
                        
                    profile_picture_file = ContentFile(
                        base64.b64decode(imgstr), 
                        name=f"profile_{user.id}_{user.username}.{ext}"
                    )
                except Exception as e:
                    return JsonResponse({"status": "error", "message": f"Invalid image format: {e}"}, status=400)

            # Cek Role User
            if hasattr(user, 'participant_profile'):
                profile = user.participant_profile
                
                if 'full_name' in data:
                    profile.full_name = data.get('full_name')
                if 'location' in data:
                    profile.location = data.get('location')
                if 'about' in data:
                    profile.about = data.get('about')
                if 'interests' in data:
                    profile.interests = data.get('interests')
                if 'birth_date' in data and data.get('birth_date'):
                    profile.birth_date = data.get('birth_date')
                    
                # Update Gambar
                if profile_picture_file:
                    profile.profile_picture = profile_picture_file

                profile.save()

            elif hasattr(user, 'organizer_profile'):
                profile = user.organizer_profile
                
                if 'organizer_name' in data:
                    profile.organizer_name = data.get('organizer_name')
                if 'contact_email' in data:
                    profile.contact_email = data.get('contact_email')
                if 'contact_phone' in data:
                    profile.contact_phone = data.get('contact_phone')
                if 'about' in data:
                    profile.about = data.get('about')
                    
                if profile_picture_file:
                    profile.profile_picture = profile_picture_file
                    
                profile.save()
            
            else:
                return JsonResponse({"status": "error", "message": "Profile not found"}, status=404)

            return JsonResponse({"status": "success", "message": "Profil berhasil diupdate"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            print(f"Error update profile: {e}") 
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
@login_and_profile_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        messages.success(request, "Akun Anda telah berhasil dihapus.")
        return redirect('Homepage:show_main')
    return redirect('profile:profile_view')

@csrf_exempt
def delete_account_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": "error",
            "message": "Anda belum login."
        }, status=401)

    if request.method == 'POST' or request.method == 'DELETE':
        try:
            user = request.user
            user.delete()
            logout(request)
            
            return JsonResponse({
                "status": "success",
                "message": "Akun berhasil dihapus."
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Gagal menghapus akun: {str(e)}"
            }, status=500)

    return JsonResponse({
        "status": "error",
        "message": "Method not allowed. Gunakan POST atau DELETE."
    }, status=405)

@login_and_profile_required
def delete_Profilepict(request):
    if request.method == 'POST':
        profile = None
        if hasattr(request.user, 'participant_profile'):
            profile = request.user.participant_profile
        elif hasattr(request.user, 'organizer_profile'):
            profile = request.user.organizer_profile

        if profile and profile.profile_picture:
            profile.profile_picture.delete(save=True)
            messages.success(request, 'Foto profil berhasil dihapus.')
        else:
            messages.error(request, 'Tidak ada foto profil untuk dihapus.')
        
        return redirect('profile:edit_profile')
    
    return redirect('profile:edit_profile')

@csrf_exempt
def create_profile(request):
    user = request.user

    if hasattr(user, 'participant_profile') or hasattr(user, 'organizer_profile'):
        return redirect('Homepage:show_main')

    role = request.session.get('registration_role')

    if not role:
        messages.error(request, "Sesi habis, silakan pilih role kembali.")
        return redirect('Homepage:show_main') 

    if role == 'participant':
        form = CreateParticipantForm(request.POST or None)

        if request.method == 'POST' and form.is_valid():
            Participant.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                location=form.cleaned_data['location'],
                birth_date=form.cleaned_data['birth_date'],
                username=user.username,
                password=user.password,
                about="-",
                interests="-"
            )

            if 'registration_role' in request.session:
                del request.session['registration_role']
                
            messages.success(request, "Profil Participant berhasil dibuat!")
            return redirect('Homepage:show_main')
        
        return render(request, 'create_profile.html', {'form': form, 'role': 'participant'})

    elif role == 'organizer':
        form = CreateOrganizerForm(request.POST or None)

        if request.method == 'POST' and form.is_valid():
            Organizer.objects.create(
                user=user,
                organizer_name=form.cleaned_data['organizer_name'],
                contact_email=form.cleaned_data['contact_email'],
                username=user.username,
                password=user.password,
                contact_phone="-",
                about="-"
            )
            
            if 'registration_role' in request.session:
                del request.session['registration_role']

            messages.success(request, "Profil Organizer BERHASIL DIBUAT!")
            return redirect('Homepage:show_main')

        return render(request, 'create_profile.html', {'form': form, 'role': 'organizer'})

    return redirect('Homepage:show_main')
    
@csrf_exempt
def create_profile_flutter(request):
    if request.method == 'POST':
        try:
            if not request.user.is_authenticated:
                return JsonResponse({
                    "status": "error", 
                    "message": "User not authenticated."
                }, status=401)

            user = request.user

            if hasattr(user, 'participant_profile') or hasattr(user, 'organizer_profile'):
                return JsonResponse({
                    "status": "error", 
                    "message": "Profile already exists for this user."
                }, status=409)

            data = json.loads(request.body)
            role = data.get('role') 

            if not role:
                return JsonResponse({
                    "status": "error", 
                    "message": "Role is required."
                }, status=400)

            if role == 'participant':
                full_name = data.get('full_name')
                location = data.get('location')
                birth_date = data.get('birth_date') 

                if not full_name or not location or not birth_date:
                    return JsonResponse({"status": "error", "message": "Full Name, Location, and Birth Date are required."}, status=400)

                Participant.objects.create(
                    user=user,
                    full_name=full_name,
                    location=location,
                    birth_date=birth_date,
                    username=user.username,
                    password=user.password,
                    about=data.get('about', "-"),
                    interests=data.get('interests', "-")
                )
                
                return JsonResponse({"status": "success", "message": "Participant Profile created successfully!"}, status=200)

            elif role == 'organizer':
                organizer_name = data.get('organizer_name')
                contact_email = data.get('contact_email')

                if not organizer_name or not contact_email:
                    return JsonResponse({"status": "error", "message": "Organizer Name and Email are required."}, status=400)

                Organizer.objects.create(
                    user=user,
                    organizer_name=organizer_name,
                    contact_email=contact_email,
                    username=user.username,
                    password=user.password,
                    contact_phone=data.get('contact_phone', "-"),
                    about=data.get('about', "-")
                )

                return JsonResponse({"status": "success", "message": "Organizer Profile created successfully!"}, status=200)

            else:
                return JsonResponse({"status": "error", "message": "Invalid role specified."}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def show_xml_Organizer(request):
    data = Organizer.objects.all()
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

@csrf_exempt
def show_xml_Participant(request):
    data = Participant.objects.all()
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

@csrf_exempt
def show_json_Organizer(request):
    data = Organizer.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

@csrf_exempt
def show_json_Participant(request):
    data = Participant.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")