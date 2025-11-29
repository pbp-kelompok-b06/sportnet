from django.shortcuts import render
from django.http import JsonResponse
from Homepage.models import CardEvent
from Event.models import Event
from django.db.models import Q
from datetime import datetime
from Bookmark.models import Bookmark
from Notification.views import handleD_1, handleNow
from django.template.loader import render_to_string
from django.http import HttpResponse

# Fungsi pembantu untuk membuat objek event menjadi format dictionary yang rapi
def serialize_event(card_event):
    # Mengambil data dari parent_event yang terhubung
    event = card_event.parent_event
    
    date_str = event.start_time.strftime("%d %B %Y") if event.start_time else ""
    price_str = f"Rp {int(event.fee):,}".replace(",", ".") if event.fee is not None else "Gratis"
    
    # Ini adalah struktur data yang dikirim ke JavaScript.
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
    # Read search and filter parameters from GET
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    free = request.GET.get('free', '')  # expect '1' for free events

    events = Event.objects.all().order_by('-start_time')

    # Apply search filter (search in name, description, location)
    if q:
        events = events.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(location__icontains=q)
        )

    # Filter by sports category
    if category:
        events = events.filter(sports_category=category.strip())
        print(f"Filtering by category: {category}")
        print(f"Events count after category filter: {events.count()}")

    # Filter free events (fee is null or zero)
    if free == '1':
        events = events.filter(Q(fee__isnull=True) | Q(fee=0))

    bookmarked_ids = []
    if request.user.is_authenticated:
        bookmarked_ids = list(
            Bookmark.objects.filter(user=request.user)
            .values_list("event_id", flat=True)
        )

    # Prepare choices for category select
    categories = [c for c, _label in Event.SPORTS_CATEGORY_CHOICES]

    context = {
        'events': events,
        'bookmarked_ids': bookmarked_ids,
        'categories': Event.SPORTS_CATEGORY_CHOICES,
        'filter_q': q,
        'filter_category': category,
        'filter_free': free,
    }
    
    handleD_1()
    handleNow()
    
    return render(request, 'homepage.html', context)

# Tampilan baru untuk menyediakan data event dalam JSON
def get_event_data_json(request):
    # Mengambil semua object CardEvent
    events = CardEvent.objects.all()
    
    # Menggunakan serialize_event untuk memformat data sebelum dikirim sebagai JSON
    event_list = [serialize_event(event) for event in events]

    return JsonResponse(event_list, safe=False)