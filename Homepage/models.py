from django.db import models
from Event.models import Event


# Create your models here.
class CardEvent(models.Model):
    parent_event = models.OneToOneField(Event, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.date} - {self.location} - {self.price}"