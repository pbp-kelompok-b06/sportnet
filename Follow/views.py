import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Authenticate.decorators import hybrid_login_required
from django.contrib.auth.models import User
from .models import Follow

@csrf_exempt
@hybrid_login_required
def follow_organizer(request, id_organizer):
    if request.method == 'POST':
        try:
            target_user = User.objects.get(pk=id_organizer)
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User tidak ditemukan"}, status=404)

        if request.user == target_user:
            return JsonResponse({"status": "error", "message": "Anda tidak bisa follow diri sendiri."}, status=400)

        if not hasattr(target_user, 'organizer_profile'):
            return JsonResponse({"status": "error", "message": "Hanya bisa follow akun Organizer."}, status=403)

        follow_instance, created = Follow.objects.get_or_create(
            user_from=request.user,
            user_to=target_user
        )

        if created:
            return JsonResponse({
                "status": "success", 
                "message": f"Berhasil follow {target_user.username}",
                "is_following": True
            }, status=201)
        else:
            return JsonResponse({
                "status": "info", 
                "message": "Anda sudah mem-follow organizer ini.",
                "is_following": True
            }, status=200)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
@hybrid_login_required
def unfollow_organizer(request, id_organizer):
    if request.method in ['POST', 'DELETE']:
        target_user = get_object_or_404(User, pk=id_organizer)

        follow_instance = Follow.objects.filter(
            user_from=request.user,
            user_to=target_user
        ).first()

        if follow_instance:
            follow_instance.delete()
            return JsonResponse({
                "status": "success", 
                "message": "Berhasil unfollow.",
                "is_following": False
            }, status=200)
        else:
            return JsonResponse({"status": "error", "message": "Anda belum mem-follow user ini."}, status=404)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@hybrid_login_required
def get_organizer_followers(request, username):
    organizer_user = get_object_or_404(User, username=username)
    if not hasattr(organizer_user, 'organizer_profile'):
         return JsonResponse({"status": "error", "message": "User ini bukan Organizer"}, status=400)

    followers_list = Follow.objects.filter(user_to=organizer_user)
    
    data = []
    for follow in followers_list:
        participant = follow.user_from

        if hasattr(participant, 'participant_profile'):
            profile = participant.participant_profile
            data.append({
                "user_id": participant.id,
                "full_name": profile.full_name,
                "username": participant.username,
                "profile_picture": profile.profile_picture.url if profile.profile_picture else None,
            })

    return JsonResponse({"status": "success", "data": data}, status=200)


@hybrid_login_required
def get_participant_following(request, username):
    participant_user = get_object_or_404(User, username=username)

    if not hasattr(participant_user, 'participant_profile'):
         return JsonResponse({"status": "error", "message": "User ini bukan Participant"}, status=400)

    following_list = Follow.objects.filter(user_from=participant_user)

    data = []
    for follow in following_list:
        organizer = follow.user_to
        
        if hasattr(organizer, 'organizer_profile'):
            profile = organizer.organizer_profile
            data.append({
                "user_id": organizer.id,
                "organizer_name": profile.organizer_name, 
                "username": organizer.username,
                "profile_picture": profile.profile_picture.url if profile.profile_picture else None,
            })

    return JsonResponse({"status": "success", "data": data}, status=200)

@hybrid_login_required
def check_follow_status(request, id_organizer):
    is_following = Follow.objects.filter(
        user_from=request.user, 
        user_to__id=id_organizer
    ).exists()

    return JsonResponse({"status": "success", "is_following": is_following}, status=200)