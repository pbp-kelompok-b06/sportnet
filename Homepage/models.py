from django.db import models
from Event.models import Event


# Create your models here.
class CardEvent(models.Model):
    parent_event = models.OneToOneField(Event, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        if self.parent_event:
            return f"Card for {self.parent_event.name}"
        return "CardEvent (no parent)"