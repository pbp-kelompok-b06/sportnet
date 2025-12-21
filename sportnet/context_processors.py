from Event.models import Event
import re

def current_or_latest_event(request):
    """
    Mengambil event yang sedang dilihat dari URL (kalau ada),
    kalau tidak ada — fallback ke event terbaru (global fallback untuk navbar).
    """
    event = None

    try:
        # Coba ambil ID event dari URL (misalnya /event/<uuid>/ atau /forum/<uuid>/)
        match = re.search(r"/(event|forum|review)/([0-9a-fA-F-]+)/", request.path)
        if match:
            event_id = match.group(2)
            event = Event.objects.filter(id=event_id).first()

        # Kalau tidak sedang di URL yang terkait event, ambil event terbaru
        if not event:
            event = Event.objects.order_by('-id').first()

    except Exception:
        event = None

    return {"event": event}
