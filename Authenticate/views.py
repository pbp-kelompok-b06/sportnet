import json
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Organizer, Participant
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
import datetime
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
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

@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                role = "unknown"
                if hasattr(user, 'participant_profile'):
                    role = 'participant'
                elif hasattr(user, 'organizer_profile'):
                    role = 'organizer'

                return JsonResponse({
                    "status": "success",
                    "message": "Login berhasil",
                    "username": user.username,
                    "role": role,
                    "id": user.id,
                }, status=200)
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Username atau password salah."
                }, status=401)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def register_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            username = data.get('username')
            password = data.get('password')
            role = data.get('role')
            email = data.get('email', '')

            if not username or not password or not role:
                return JsonResponse({"status": "error", "message": "Field utama tidak boleh kosong!"}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({"status": "error", "message": "Username sudah digunakan!"}, status=400)
            
            #create user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # create profile
            if role == 'participant':
                # ambil data dari json
                full_name = data.get('full_name', username)
                location = data.get('location', '-')
                interests = data.get('interests', '-')
                about = data.get('about', '-')
                birth_date = data.get('birth_date')
                if birth_date == "": 
                    birth_date = None

                Participant.objects.create(
                    user=user,
                    full_name=full_name,
                    location=location,
                    interests=interests,
                    about=about,
                    birth_date=birth_date,
                    username=username, 
                    password=password
                )
            elif role == "organizer":
                organizer_name = data.get('organizer_name', username)
                contact_email = data.get('contact_email', email)
                contact_phone = data.get('contact_phone', '-')
                about = data.get('about', '-')

                Organizer.objects.create(
                    user=user,
                    organizer_name=organizer_name,
                    contact_email=contact_email,
                    contact_phone=contact_phone,
                    about=about,
                    username=username,
                    password=password
                )
            else:
                user.delete()
                return JsonResponse({"status": "error", "message": "Role tidak valid!"}, status=400)
            return JsonResponse({"status": "success", "message": "Registrasi berhasil! Silakan login."}, status=200)
        
        except Exception as e:
            if 'user' in locals():
                user.delete()
            return JsonResponse({"status": "error", "message": f"Terjadi kesalahan: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def logout_api(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({"status": "success", "message": "Logout berhasil"}, status=200)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)