from django import forms
from django.contrib.auth.models import User
from .models import Organizer, Participant

default_attrs = {
    'class': 'w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-400',
}

class OrganizerRegisterForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            **default_attrs, 
            'placeholder': 'Enter your username'
        })
    )
    password1 = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={
            **default_attrs, 
            'placeholder': 'Choose a strong password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password', 
        widget=forms.PasswordInput(attrs={
            **default_attrs, 
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = Organizer
        fields = ['organizer_name', 'contact_email']

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Password tidak sesuai!")
        
class ParticipantRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            **default_attrs, 
            'placeholder': 'Enter your username'
        })
    )
    password1 = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={
            **default_attrs, 
            'placeholder': 'Choose a strong password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password', 
        widget=forms.PasswordInput(attrs={
            **default_attrs, 
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = Participant
        fields = ['full_name', 'location', 'birth_date']

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Password tidak sesuai!")

