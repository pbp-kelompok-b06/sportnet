# authenticate/forms.py

from django import forms
from .models import Organizer, Participant

default_attrs = {
    'class': 'w-full rounded-full border border-gray-300 bg-gray-50 pl-12 pr-6 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-400 text-sm',
}

class RegisterForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={**default_attrs, 'placeholder': 'Enter your username'})
    )
    password_1 = forms.CharField( 
        label='Password', 
        widget=forms.PasswordInput(attrs={**default_attrs, 'placeholder': 'Choose a strong password'})
    )
    password_2 = forms.CharField( 
        label='Confirm Password', 
        widget=forms.PasswordInput(attrs={**default_attrs, 'placeholder': 'Confirm your password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password_1")
        pw2 = cleaned_data.get("password_2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Password tidak sesuai!")
        return cleaned_data
    