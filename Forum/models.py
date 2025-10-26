from django.db import models
from Event.models import Event
from Authenticate.models import Participant

class ForumPost(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='posts')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='posts',null=True, blank=True)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Use 'profile' (Participant) and event.nama_kegiatan property
        profile_name = getattr(self.participant, 'full_name', str(self.participant)) if self.participant else 'Unknown'
        event_name = getattr(self.event, 'nama_kegiatan', str(self.event)) if self.event else 'Unknown'
        return f"{profile_name} - {event_name[:20]} - {self.participant_id}"
