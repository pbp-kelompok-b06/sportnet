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

@login_required(login_url='/authenticate')
@csrf_exempt
def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        if not request.user.is_authenticated:
            return redirect('Authenticate:login')
        profile_user = request.user
    
    context = {}
    booked_events = None

    try:
        participant_profile = Participant.objects.get(user=profile_user)
        all_booked_events = participant_profile.events_joined.order_by('start_time')
        
        now = timezone.now()
        

        upcoming_events = all_booked_events.filter(start_time__gte=now)
        past_events = all_booked_events.filter(start_time__lt=now).order_by('-start_time') # Urutkan dari yang terbaru
        
        context = {
            'profile_user': profile_user, 
            'participant': participant_profile, 
            'upcoming_events': upcoming_events,
            'past_events': past_events,
        }
    except Participant.DoesNotExist:
        try:
            organizer_profile = Organizer.objects.get(user=profile_user)
            context = {'profile_user': profile_user, 'organizer':organizer_profile}
        except Organizer.DoesNotExist:
            messages.error(request, 'Profil tidak ditemukan.')
            return redirect('Homepage:show_homepage')
    return render(request, 'profile.html', context)

@login_required(login_url='/authenticate')
@csrf_exempt
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

@login_required(login_url='/authenticate')
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
