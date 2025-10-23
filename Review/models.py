from django.db import models
from events.models import Event
from authenticate.models import Profile

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
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('event', 'profile')

    def __str__(self):
        return f'Review {self.rating} stars by {self.profile.nama} for {self.event.nama_kegiatan}'