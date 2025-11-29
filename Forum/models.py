from django.db import models
from Authenticate.models import Participant, Organizer
from Event.models import Event

class ForumPost(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    participant = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forum_posts"
    )
    organizer = models.ForeignKey(
        Organizer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forum_posts"
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.participant:
            return f"{self.participant.full_name}"
        elif self.organizer:
            return f"{self.organizer.organizer_name} (Organizer)"
        return "Anonymous"
