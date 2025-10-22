from django.db import models
from django.contrib.auth.models import User

class Organizer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organizer_profile')
    organizer_name = models.CharField(max_length=100)
    contact_email = models.CharField(max_length=50,blank=True, null=True)
    contact_phone = models.CharField(max_length=15,blank=True,null=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255,blank=False,null=False)

    def lst_data(self):
        dictionary = {
            'id' : self.user.pk,
            'organizer_name' : self.organizer_name,
            'contact_email' : self.contact_email,
            'contact_phone' : self.contact_phone,
            'bio' : self.bio,
            'profile_picture' : self.profile_picture,
            'location' : self.location,
            'username' : self.username,
        }
        return dictionary
    
    def __str__(self):
        return self.organizer_name
    
class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='participant_profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    full_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255,blank=False,null=False)
    bio = models.TextField(blank=True)
    interests = models.CharField(max_length=255, blank=True, null=True)
    age = models.DateField(blank=True, null=True)

    def lst_data(self):
        dictionary = {
            'id' : self.user.pk,
            'profile_picture' : self.profile_picture,
            'full_name' : self.full_name,
            'location' : self.location,
            'username' : self.username,
            'password' : self.password,
            'bio' : self.bio,
            'interests' : self.interests,
            'age' : self.age,
        }
        return dictionary
        

    def __str__(self):
        return self.participant_name
    
