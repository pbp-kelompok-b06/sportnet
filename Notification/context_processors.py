from Notification.models import Notifications

def notification_count(request):
    
    if request.user.is_authenticated and hasattr(request.user, 'participant_profile'):
        unread_count = Notifications.objects.filter(
            user=request.user.participant_profile,
            is_read=False
        ).count()
        return {'unread_notification_count': unread_count}
    return {'unread_notification_count': 0}