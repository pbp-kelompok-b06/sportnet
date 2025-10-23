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
from .forms import OrganizerRegisterForm, ParticipantRegistrationForm

@csrf_exempt
def register_participant(request):
    if request.method == 'POST':
        form = ParticipantRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            if User.objects.filter(username=username).exists:
                messages.error(request, "Username sudah ada. Silahkan gunakan username lain.")
                return render(request, 'register_participant.html', {'form': form})
            else:
                user = User.objects.create_user(username=username, password=password)
                participant = form.save(commit=False)
                participant.user = user
                participant.save()
                messages.success(request, "Akun berhasil dibuat! Silahkan login.")
                return redirect('Authenticate:login')
        else:
            return render(request, 'register_participant.html', {'form': form})
    else:
        form = ParticipantRegistrationForm()
        return render(request, 'register_participant.html', {'form': form})

@csrf_exempt
def register_organizer(request):
    if request.method == 'POST':
        form = OrganizerRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username sudah ada. Silahkan gunakan username lain.")
                return render(request, 'register_organizer.html', {'form': form})
            else:
                user = User.objects.create_user(username=username, password=form.cleaned_data['password1'])
                organizer = form.save(commit=False)
                organizer.user = user
                organizer.save()
                messages.success(request, "Akun berhasil dibuat! Silahkan login.")
                return redirect('Authenticate:login')
        else:
            form = OrganizerRegisterForm()
        return render(request, 'register_organizer.html', {'form': form})
    else:
        form = OrganizerRegisterForm()
        return render(request, 'register_organizer.html', {'form': form})

def register_role_selection(request):
    if request.method == 'POST':
        selected_role = request.POST.get('role')
        if(selected_role == 'participant'):
            return redirect('Authenticate:register_participant')
        elif(selected_role == 'organizer'):
            return redirect('Authenticate:register_organizer')
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