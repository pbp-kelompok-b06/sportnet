from django.db import models
from django.contrib.auth.models import User
from Event.models import Event
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

# Create your models here.
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    note = models.TextField(blank=True, default="", validators=[MaxLengthValidator(100)])

    class Meta:
        unique_together = ('user', 'event')
    
    def __str__(self):
        return f"{self.user.username} - {self.event.name}"
    
    def clean(self):
        # Sanitize HTML
        self.note = strip_tags(self.note or "").strip()

    def save(self, *args, **kwargs):
        # Trigger validation + clean() before saving
        self.full_clean()
        super().save(*args, **kwargs)