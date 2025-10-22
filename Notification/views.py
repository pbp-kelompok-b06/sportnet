from django.shortcuts import render
from Notification.models import Notifications as Notif

# Create your views here.
def show_all(request):
    notif = Notif.objects.all()
    context = {
        'notif': notif,
    }
    return render(request, 'all_notif.html', context)

def show_detail(request):
    return render(request, 'show_detail.html')