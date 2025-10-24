from django.contrib import admin
from Authenticate.models import Participant, Organizer

# Register your models here.
admin.site.register(Participant)
admin.site.register(Organizer)