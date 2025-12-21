import uuid
from django.db import models
from django.conf import settings
from Event.models import Event
from django.core.exceptions import ValidationError

class PinnedEvent(models.Model):
    MAX_PINNED = 3
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # organizer login user (yang punya organizer_profile)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_pins"
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="pinned_in_dashboard"
    )

    # urutan pin (buat drag reorder)
    position = models.PositiveSmallIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")
        ordering = ["position", "created_at"]
        indexes = [
            models.Index(fields=["user", "position"]),
            models.Index(fields=["user", "event"]),
        ]

    def clean(self):
        if self.position is None or self.position < 1 or self.position > self.MAX_PINNED:
            raise ValidationError(f"You can only pin 3 events.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} pinned {self.event} @pos {self.position}"