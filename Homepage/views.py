from django.shortcuts import render
from Homepage.models import CardEvent

# Create your views here.
def show_main(request):
    create = CardEvent.objects.create(name='tester', date='2025-10-10',
                                      location='Jakarta', category='test',
                                      description='test', image='https://gelora-public-storage.s3-ap-southeast-1.amazonaws.com/upload/public-20240804083959.jpg',
                                      price=100000)
    create.save()
    events = CardEvent.objects.all()
    return render(request, 'homepage.html', {'events': events})