import json
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Organizer, Participant
from django.shortcuts import render, redirect
from django.contrib import messages
import datetime
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .forms import RegisterForm

def register_role_selection(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['participant', 'organizer']:
            request.session['registration_role'] = role
            return redirect('Authenticate:register')
        else:
            messages.error(request, "Pilih role yang valid.")
            
    return render(request, 'register_role_selection.html')

@csrf_exempt
def register(request):
    role = request.session.get('registration_role')
    if not role:
        return redirect('Authenticate:register_role_selection')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password_1') 

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username telah digunakan.")
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                
                messages.success(request, 'Akun berhasil dibuat! Silakan login.')
                return redirect('Authenticate:login')
        else:
             messages.error(request, "Form tidak valid.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

@csrf_exempt
def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            response = HttpResponseRedirect(reverse("Homepage:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
            
        else:
            messages.error(request, 'Username atau password salah.')

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
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
             return JsonResponse({
                "status": False,
                "message": "Username and password are required."
            }, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                profile_exists = False
                role = "unknown"

                if hasattr(user, 'participant_profile'):
                    role = 'participant'
                    profile_exists = True
                elif hasattr(user, 'organizer_profile'):
                    role = 'organizer'
                    profile_exists = True
                elif user.is_superuser:
                    role = 'admin'
                    profile_exists = True

                return JsonResponse({
                    "status": True,
                    "message": "Login sukses!",
                    "username": user.username,
                    "role": role,
                    "profile_exists": profile_exists,
                }, status=200)
            else:
                return JsonResponse({
                    "status": False,
                    "message": "Login gagal, periksa username atau password."
                }, status=403)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login gagal, periksa username atau password."
            }, status=403)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=400)

@csrf_exempt
def register_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password') 

            if not username or not password:
                return JsonResponse({
                    "status": False,
                    "message": "Username and password are required."
                }, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    "status": False,
                    "message": "Username already exists."
                }, status=400)

            user = User.objects.create_user(username=username, password=password)
            user.save()
            
            return JsonResponse({
                "status": True,
                "message": "User created successfully!",
                "username": user.username
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"status": False, "message": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)}, status=500)
    
    return JsonResponse({"status": False, "message": "Invalid request method."}, status=400)

@csrf_exempt
def logout_api(request):
    if request.method != 'POST':
        return JsonResponse({
            "status": False,
            "message": "Method not allowed. Use POST."
        }, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({
            "status": False,
            "message": "User is not authenticated."
        }, status=401)

    try:
        username = request.user.username
        logout(request)
        return JsonResponse({
            "status": True,
            "message": "Logout successful!",
            "username": username
        }, status=200)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=500)