from django import forms
from django.contrib.auth.models import User
from .models import Organizer, Participant

class OrganizerRegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())

    class Meta:
        model = Organizer
        fields = ['organizer_name', 'contact_email', 'contact_phone', 'bio', 'profile_picture', 'location']

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Password tidak sesuai!")
        
class ParticipantRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())

    class Meta:
        model = Participant
        fields = ['full_name', 'location', 'interests', 'bio', 'age']

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Password tidak sesuai!")

