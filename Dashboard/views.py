from django.shortcuts import render

def show(request):
    return render(request, 'dashboard.html')
