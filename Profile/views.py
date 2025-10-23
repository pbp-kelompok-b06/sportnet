from django.shortcuts import render

# Create your views here.
def show_main(request):
    return render(request, 'profile.html')

def edit_profile(request):
    return render(request, 'edit_profile.html')