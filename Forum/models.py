from django.db import models
from Event.models import Event
from Authenticate.models import Participant

class ForumPost(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='posts')
    profile = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant.full_name} - {self.event.nama_kegiatan[:20]}"
