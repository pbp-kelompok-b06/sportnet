from django.db import models
from events.models import Event 
from authenticate.models import Profile

class ForumPost(models.Model):
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='forum_posts'
    )
    profile = models.ForeignKey(
        Profile, 
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
        return f'Post by {self.profile.nama} on {self.event.nama_kegiatan}'