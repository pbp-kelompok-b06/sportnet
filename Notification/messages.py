from django.utils.translation import gettext as _

# Event Join Notifications
EVENT_JOIN_TITLE = _("Berhasil Bergabung dengan Event")
EVENT_JOIN_MESSAGE = _("Anda telah berhasil bergabung dengan event {event_name}")

# Event Cancellation Notifications
EVENT_CANCELLED_TITLE = _("Event Dibatalkan")
EVENT_CANCELLED_MESSAGE = _("Event {event_name} telah dibatalkan oleh penyelenggara")

# H-1 Reminder Notifications
EVENT_REMINDER_TITLE = _("Pengingat Event Besok")
EVENT_REMINDER_MESSAGE = _("Event {event_name} akan berlangsung besok pada {event_time}")

# Read Status Messages
MARK_AS_READ_SUCCESS = _("Notifikasi telah ditandai sebagai dibaca")
MARK_ALL_READ_SUCCESS = _("Semua notifikasi telah ditandai sebagai dibaca")

# Error Messages
ERROR_NO_PARTICIPANT_PROFILE = _("Pengguna tidak memiliki profil peserta")
ERROR_FORBIDDEN = _("Anda tidak memiliki akses ke notifikasi ini")
ERROR_EVENT_NOT_FOUND = _("Event tidak ditemukan")