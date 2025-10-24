from django.shortcuts import render
from django.http import JsonResponse
from Homepage.models import CardEvent
from Event.models import Event
from datetime import datetime
from Bookmark.models import Bookmark

# Fungsi pembantu untuk membuat objek event menjadi format dictionary yang rapi
def serialize_event(card_event):
    # Mengambil data dari parent_event yang terhubung
    event = card_event.parent_event
    
    date_str = event.start_time.strftime("%d %B %Y") if event.start_time else ""
    price_str = f"Rp {int(event.fee):,}".replace(",", ".") if event.fee is not None else "Gratis"
    
    # NOTE: Ini adalah struktur data yang dikirim ke JavaScript.
    # JavaScript di homepage.html mengharapkan field seperti 'name', 'date', dll.
    return {
        'id': str(event.id),
        'name': event.name,
        'date': date_str,
        'location': event.location,
        'description': event.description,
        'image': event.thumbnail,
        'price_display': price_str,
        'category': event.sports_category
    }

def show_main(request):
    events = Event.objects.all().order_by('-start_time')

    bookmarked_ids = []
    if request.user.is_authenticated:
        bookmarked_ids = list(
            Bookmark.objects.filter(user=request.user)
            .values_list("event_id", flat=True)
        )

    context = {'events': events, 'bookmarked_ids': bookmarked_ids}
    return render(request, 'homepage.html', context)

# Tampilan baru untuk menyediakan data event dalam JSON
def get_event_data_json(request):
    # Mengambil semua object CardEvent
    events = CardEvent.objects.all()
    
    # Menggunakan serialize_event untuk memformat data sebelum dikirim sebagai JSON
    event_list = [serialize_event(event) for event in events]

    return JsonResponse(event_list, safe=False)