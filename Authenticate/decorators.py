
from django.contrib.auth.decorators import login_required

def hybrid_login_required(view_func):
    return login_required(view_func)
from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages

def login_and_profile_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('Authenticate:login')

        has_participant = hasattr(request.user, 'participant_profile')
        has_organizer = hasattr(request.user, 'organizer_profile')

        if not has_participant and not has_organizer and not request.user.is_superuser:
            messages.warning(request, "You must create a profile first to access this feature!")
            return redirect('profile:create_profile')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def hybrid_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        wants_json = request.headers.get('Content-Type') == 'application/json' or \
                     'application/json' in request.headers.get('Accept', '')

        if not request.user.is_authenticated:
            if wants_json:
                return JsonResponse({"status": "error", "message": "Login required"}, status=401)
            else:
                return redirect('Authenticate:login')
            
        has_participant = hasattr(request.user, 'participant_profile')
        has_organizer = hasattr(request.user, 'organizer_profile')
        
        if not has_participant and not has_organizer and not request.user.is_superuser:
            if wants_json:
                return JsonResponse({"status": "error", "message": "Profile setup required"}, status=403)
            else:
                messages.warning(request, "Lengkapi profil dulu sebelum follow!")
                return redirect('profile:create_profile')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
