from django.contrib.auth import logout
import json
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError
from Authenticate.models import Organizer, Participant
from django.contrib.auth.models import User
from Profile.forms import ProfileFormOrganizer, ProfileFormParticipant
from django.views.decorators.csrf import csrf_exempt
import base64
from django.core.files.base import ContentFile
from django.utils import timezone
from Follow.models import Follow

@csrf_exempt
@login_required(login_url='Authenticate:login')
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


@login_required(login_url='Authenticate:login')
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
@login_required(login_url='Authenticate:login')
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
@login_required(login_url='Authenticate:login')
def edit_profile_api(request):
    if request.method == 'POST':
        user = request.user

        data = request.POST
        files = request.FILES
        
        try:
            # Cek Role User
            if hasattr(user, 'participant_profile'):
                profile = user.participant_profile
                
                # Update Text Fields
                if 'full_name' in data:
                    profile.full_name = data['full_name']
                if 'location' in data:
                    profile.location = data['location']
                if 'about' in data:
                    profile.about = data['about']
                if 'interests' in data:
                    profile.interests = data['interests']
                if 'birth_date' in data and data['birth_date']:
                    profile.birth_date = data['birth_date']

                if 'profile_picture' in files:
                    profile.profile_picture = files['profile_picture']
                
                profile.save()

            elif hasattr(user, 'organizer_profile'):
                profile = user.organizer_profile
                
                if 'organizer_name' in data:
                    profile.organizer_name = data['organizer_name']
                if 'contact_email' in data:
                    profile.contact_email = data['contact_email']
                if 'contact_phone' in data:
                    profile.contact_phone = data['contact_phone']
                if 'about' in data:
                    profile.about = data['about']
                
                if 'profile_picture' in files:
                    profile.profile_picture = files['profile_picture']
                
                profile.save()
            
            else:
                return JsonResponse({"status": "error", "message": "Profile not found"}, status=404)

            return JsonResponse({"status": "success", "message": "Profil berhasil diupdate"}, status=200)

        except Exception as e:
            print(f"Error update profile: {e}") 
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
@login_required(login_url='Authenticate:login')
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

@login_required(login_url='Authenticate:login')
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