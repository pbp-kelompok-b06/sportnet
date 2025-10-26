import os
import json
import uuid
import re
from datetime import datetime
from Event.models import Event
from Authenticate.models import Organizer
from django.contrib.auth.models import User


# Tentukan path absolut dari file ini
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR,"static", "dataset", "dataset_event_sportnet.json")


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


    count = 0
    for item in data:
        try:
            if User.objects.filter(username=item.get("organizer")).exists():
                userCreate = User.objects.get(username=item.get("organizer"))
                organizer = Organizer.objects.get(user=userCreate)
            else:
                userCreate = User.objects.create(username=item.get("organizer"))
                organizer = Organizer.objects.create(
                    user=userCreate,
                    organizer_name=item.get("organizer", "Untitled Organizer"),
                    contact_email=item.get("contact_email", ""),
                    contact_phone=item.get("contact_phone", ""),
                    about=item.get("about", ""),
                    profile_picture=item.get("profile_picture", ""),
                    username=item.get("organizer", ""),
                    password=item.get("password", ""),
                )
            Event.objects.get_or_create(
                name=item.get("name", "Untitled Event"),
                defaults={
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
                    "id": item.get("id", uuid.uuid4()),
                },
            )
            count += 1
        except Exception as e:
            print(f"Gagal menambah event: {item.get('name')} karena {e}")

    print(f"{count} data event berhasil diimport.")

def delete_all_events():
    deleted_count, _ = Event.objects.all().delete()
    print(f"Deleted {deleted_count} events from the database.")