from django.db import models
from Event.models import Event
from Authenticate.models import Participant

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 - Buruk'),
        (2, '2 - Kurang'),
        (3, '3 - Cukup'),
        (4, '4 - Baik'),
        (5, '5 - Sangat Baik'),
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('event', 'participant') 

    def __str__(self):
        return f'Review {self.rating} stars by {self.participant.full_name} for {self.event.name}'