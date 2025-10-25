from django.db import models
from Authenticate.models import Participant
from Event.models import Event
from django.utils import timezone

class Notifications(models.Model):
    user = models.ForeignKey(
        Participant, 
        on_delete=models.CASCADE, 
        related_name='user_tujuan', 
        null=True,  # tambahkan null=True agar aman migrasi pertama kali
        blank=True
    )
    title = models.CharField(max_length=255)
    message = models.TextField(null=True, blank=True, default="")
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None  # penting: biar tidak minta default manual
    )
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def read(self):
        self.is_read = True
        self.save()
