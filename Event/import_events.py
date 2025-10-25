import os
import json
import uuid
import re
from datetime import datetime
from Event.models import Event
from Authenticate.models import Organizer


# Tentukan path absolut dari file ini
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "dataset", "event", "events_v2.json")


def parse_time(value):
    """
    Memperbaiki format waktu yang tidak sesuai ISO:
    contoh: 2025-10-12T05.30.00+07:00 → 2025-10-12T05:30:00+07:00
    """
    if not value:
        return None
    # ubah titik (.) menjadi titik dua (:) hanya di bagian jam-menit-detik
    fixed = re.sub(r"(\d{2})\.(\d{2})\.(\d{2})", r"\1:\2:\3", value)
    try:
        return datetime.fromisoformat(fixed)
    except Exception as e:
        print(f"⚠️ Gagal parse waktu '{value}' → {e}")
        return None


def run():
    print(f"Membuka file dataset di: {DATA_PATH}")

    # Pastikan file-nya ada
    if not os.path.exists(DATA_PATH):
        print("File tidak ditemukan, pastikan path benar.")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    organizer = Organizer.objects.first()

    count = 0
    for item in data:
        try:
            event_id = uuid.UUID(item.get("id")) if item.get("id") else uuid.uuid4()
            Event.objects.get_or_create(
                id=event_id,
                defaults={
                    "name": item.get("name", "Untitled Event"),
                    "description": item.get("description", ""),
                    "thumbnail": item.get("thumbnail"),
                    "organizer": organizer,
                    "start_time": parse_time(item.get("start_time")),
                    "end_time": parse_time(item.get("end_time")),
                    "location": item.get("location", ""),
                    "address": item.get("address", ""),
                    "sports_category": item.get("sports_category", "running"),
                    "activity_category": item.get("activity_category", "fun_run_ride"),
                    "fee": item.get("fee", 0),
                    "capacity": item.get("capacity", 0),
                },
            )
            count += 1
        except Exception as e:
            print(f"Gagal menambah event: {item.get('name')} karena {e}")

    print(f"{count} data event berhasil diimport.")
