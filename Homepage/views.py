from django.shortcuts import render
from Homepage.models import CardEvent

# Create your views here.
def show_main(request):
    events = CardEvent.objects.all()
    return render(request, 'homepage.html', {'events': events})