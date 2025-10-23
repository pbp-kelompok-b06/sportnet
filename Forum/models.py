from django.db import models
from Event.models import Event 
from Authenticate.models import Participant

class ForumPost(models.Model):
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='forum_posts'
    )
    participant = models.ForeignKey(
        Participant, 
        on_delete=models.CASCADE, 
        related_name='forum_posts'
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

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Post by {self.participant.full_name} on {self.event.name}'
