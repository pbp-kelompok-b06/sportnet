from django.shortcuts import render

# Create your views here.
def show_bookmark(request):
    return render(request, 'bookmark.html')