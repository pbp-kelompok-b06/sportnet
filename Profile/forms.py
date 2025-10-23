from django import forms
from Authenticate.models import Organizer, Participant

default_attrs = {
    'class': 'w-full rounded-full border border-gray-300 bg-gray-50 pl-12 pr-6 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-400 text-sm',
}

textarea_attrs = default_attrs.copy()
textarea_attrs['class'] ='w-full rounded-2xl border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-400 text-sm h-28'

class ProfileFormParticipant(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['full_name', 'location', 'birth_date', 'about', 'interests', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={**default_attrs, 'placeholder': 'Your Full Name'}),
            'location': forms.TextInput(attrs={**default_attrs, 'placeholder': 'Your City'}),
            'birth_date': forms.DateInput(attrs={**default_attrs, 'type': 'date'}),
            'about': forms.Textarea(attrs={**textarea_attrs, 'placeholder': 'Tell us about yourself...'}),
            'interests': forms.TextInput(attrs={**default_attrs, 'placeholder': 'e.g., Running, Padel, Yoga'}),
            'profile_picture': forms.FileInput(attrs={'class': 'mt-2'}),
        }

class ProfileFormOrganizer(forms.ModelForm):
    class Meta:
        model = Organizer
        fields = ['organizer_name', 'contact_email', 'contact_phone', 'about', 'profile_picture']
        widgets = {
            'organizer_name': forms.TextInput(attrs={**default_attrs, 'placeholder': 'Your Organizer Name'}),
            'contact_email': forms.EmailInput(attrs={**default_attrs, 'placeholder': 'Contact Email'}),
            'contact_phone': forms.TextInput(attrs={**default_attrs, 'placeholder': 'Ex: +62 812-3456-7890'}),
            'about': forms.Textarea(attrs={**textarea_attrs, 'placeholder': 'Tell us about your organization...'}),
            'profile_picture': forms.FileInput(attrs={'class': 'mt-2'}),
        }