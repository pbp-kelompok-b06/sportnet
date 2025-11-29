from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.contrib import messages
import datetime
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Organizer, Participant
from .forms import AuthStep1Form, ParticipantStep2Form, OrganizerStep2Form

@csrf_exempt
def register_participant_step1(request):
    if request.method == 'POST':
        form = AuthStep1Form(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, "Username sudah ada. Silahkan gunakan username lain.")
            else:
                request.session['participant_step1_data'] = form.cleaned_data
                return redirect('Authenticate:register_participant_step2') # Arahkan ke URL step 2
    else:
        form = AuthStep1Form()
    return render(request, 'register_participant_step1.html', {'form': form})

def register_participant_step2(request):
    step1_data = request.session.get('participant_step1_data')
    if not step1_data:
        return redirect('Authenticate:register_participant_step1')
    

    if request.method == 'POST':
        form = ParticipantStep2Form(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=step1_data['username'],
                password=step1_data['password_1'] # Gunakan 'password_1'
            )
            participant = form.save(commit=False)
            participant.user = user
            participant.save()
            del request.session['participant_step1_data']
            messages.success(request, "Akun berhasil dibuat! Silahkan login.")
            return redirect('Authenticate:login')
    else:
        form = ParticipantStep2Form()
    return render(request, 'register_participant_step2.html', {'form': form})

@csrf_exempt
def register_organizer_step1(request):
    if request.method == 'POST':
        form = AuthStep1Form(request.POST) # Gunakan AuthStep1Form
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, "Username sudah ada. Silahkan gunakan username lain.")
            else:
                request.session['organizer_step1_data'] = form.cleaned_data
                return redirect('Authenticate:register_organizer_step2') # Arahkan ke URL step 2
    else:
        form = AuthStep1Form() # Gunakan AuthStep1Form
    return render(request, 'register_organizer_step1.html', {'form': form})
    
def register_organizer_step2(request):
    step1_data = request.session.get('organizer_step1_data')
    if not step1_data:
        return redirect('Authenticate:register_organizer_step1')

    if request.method == 'POST':
        form = OrganizerStep2Form(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=step1_data['username'],
                password=step1_data['password_1'] # Gunakan 'password_1'
            )
            organizer = form.save(commit=False)
            organizer.user = user
            organizer.save()
            del request.session['organizer_step1_data']
            messages.success(request, "Akun berhasil dibuat! Silahkan login.")
            return redirect('Authenticate:login')
    else:
        form = OrganizerStep2Form()
    return render(request, 'register_organizer_step2.html', {'form': form})

def register_role_selection(request):
    if request.method == 'POST':
        selected_role = request.POST.get('role')
        if(selected_role == 'participant'):
            return redirect('Authenticate:register_participant_step1')
        elif(selected_role == 'organizer'):
            return redirect('Authenticate:register_organizer_step1')
        else:
            messages.error(request, "Silakan pilih role yang valid.")
    return render(request, 'register.html')

@csrf_exempt
def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            response = HttpResponseRedirect(reverse("Homepage:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            messages.error(request, 'Username atau password salah. Silakan coba lagi.')
    return render(request, 'login.html')

@csrf_exempt
def log_out(request):
    logout(request)
    response = HttpResponseRedirect(reverse('Homepage:show_main'))
    response.delete_cookie('last_login')
    return response