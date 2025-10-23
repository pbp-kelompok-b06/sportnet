from django.db import models
from Authenticate.models import Participant
from Event.models import Event


# Create your models here.
class Notifications(models.Model):
    user = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='user_tujuan')
    title = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_tujuan")
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    def read(self):
        self.is_read = True
        self.save()
    
    