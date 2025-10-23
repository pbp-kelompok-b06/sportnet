from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Event(models.Model):
    SPORTS_CATEGORY_CHOICES = [
        ('running', 'Running'),
        ('padel', 'Padel'),
        ('football', 'Football'),
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('badminton', 'Badminton'),
        ('fitness', 'Fitness'),
        ('cycling', 'Cycling'),
        ('poundfit', 'Poundfit'),
    ]

    ACTIVITY_CATEGORY_CHOICES  = [
        ('fun_run_ride', 'Fun Run/Ride'),
        ('marathon', 'Marathon'),
        ('friendly_match', 'Friendly Match'),
        ('course', 'Course'),
        ('tournament', 'Tournament'),
        ('open_play', 'Open Play'),
        ('workshop', 'Workshop'),
    ]
    # Identitas
    name = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    organizer = models.ForeignKey('Authenticate.Organizer', on_delete=models.CASCADE, related_name="owned_events", null=True)

    # Date Time
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    
    # Location
    location = models.CharField(max_length=120)
    address = models.TextField(blank=True, null=True)
    
    # Category
    sports_category = models.CharField(max_length=20, choices=SPORTS_CATEGORY_CHOICES)
    activity_category = models.CharField(max_length=20, choices=ACTIVITY_CATEGORY_CHOICES)
    
    # Price
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="IDR", blank=True, null=True)

    # Kapasitas
    capacity = models.PositiveSmallIntegerField(default=0)
    attendee = models.ManyToManyField('Authenticate.Participant', related_name="events_joined", blank=True, null=True)


    @property
    def attendee_count(self):
        return self.attendee.count()
    

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['start_time']
