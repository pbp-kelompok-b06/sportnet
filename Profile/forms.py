from django.db import ModelForm
from Authenticate.models import Organizer, Participant

class ProfileFormOrganizer(ModelForm):
    class Meta:
        model = Organizer
        fields =["profile_picture","organizer_name", "username", "about", "contact_email", "contact_phone"]

class ProfileFormParticipant(ModelForm):
    class Meta:
        model = Participant
        fields = ["profile_picture", "username", "about","location", "interests", "birth_date"]