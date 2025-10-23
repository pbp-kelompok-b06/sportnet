from django.shortcuts import render
from django.http import JsonResponse
from Homepage.models import CardEvent
from Event.models import Event
from datetime import datetime

# Fungsi pembantu untuk membuat objek event menjadi format dictionary yang rapi
def serialize_event(card_event):
    # Mengambil data dari parent_event yang terhubung
    event = card_event.parent_event
    
    date_str = event.start_time.strftime("%d %B %Y") if event.start_time else ""
    price_str = f"Rp {int(event.fee):,}".replace(",", ".") if event.fee is not None else "Gratis"
    
    # NOTE: Ini adalah struktur data yang dikirim ke JavaScript.
    # JavaScript di homepage.html mengharapkan field seperti 'name', 'date', dll.
    return {
        'pk': event.pk,
        'name': event.name,
        'date': date_str,
        'location': event.location,
        'description': event.description,
        'image': event.thumbnail,
        'price_display': price_str,
        'category': event.sports_category
    }

# Tampilan utama kini hanya merender template.
def show_main(request):

    # NOTE: Kode ini hanya untuk demonstrasi membuat dummy event.
    # Sebaiknya, Anda memiliki cara untuk membuat Event nyata (misal, dari form).
    # get_or_create mencegah duplikat setiap kali halaman di-refresh.
    
    events = Event.objects.all()
    for event in events:
        CardEvent.objects.get_or_create(parent_event=event)
        
    # Membuat CardEvent yang terhubung dengan dummy_event di atas.
    # Ini juga menggunakan get_or_create untuk menghindari duplikat.
    # CardEvent.objects.get_or_create(parent_event=dummy_event)

    return render(request, 'homepage.html')

# Tampilan baru untuk menyediakan data event dalam JSON
def get_event_data_json(request):
    # Mengambil semua object CardEvent
    events = CardEvent.objects.all()
    
    # Menggunakan serialize_event untuk memformat data sebelum dikirim sebagai JSON
    event_list = [serialize_event(event) for event in events]
    
    return JsonResponse(event_list, safe=False)