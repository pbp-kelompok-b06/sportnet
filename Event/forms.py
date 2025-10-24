from django import forms
from django.utils.html import strip_tags
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "name",
            "description",
            "thumbnail",
            "start_time",
            "end_time",
            "location",
            "address",
            "sports_category",
            "activity_category",
            "fee",
    
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
            }),
            "description": forms.Textarea(attrs={
                "class": " h-[100px] w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
            }),
            "thumbnail": forms.URLInput(attrs={
                "class": "w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
            }),
            "start_time": forms.DateTimeInput(attrs={
                "class": " w-[300px] w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
                "placeholder": "Start",
                "type": "datetime-local"
            }),
            "end_time": forms.DateTimeInput(attrs={
                "class": " w-[300px] w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
                "placeholder": "End",
                "type": "datetime-local" 
                
            }),
            "location": forms.TextInput(attrs={
                "class": "w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
            }),
            "address": forms.Textarea(attrs={
                "class": "h-[100px] w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
            }),
            "sports_category": forms.Select(attrs={
                "class": " w-[180px] w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
            }),
            "activity_category": forms.Select(attrs={
                "class": "w-[180px] w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
            }),
            "fee": forms.NumberInput(attrs={
                "class": "w-[150px] w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
            }),
            "currency": forms.TextInput(attrs={
                "class": "w-[50px] w-full rounded-full border border-gray-300 bg-gray-50 px-6 py-3 text-gray-800 placeholder:text-gray-[var(--color-text-200)] focus:outline-none focus:ring-2 focus:ring-orange-400",
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        return strip_tags(name)

    def clean_description(self):
        desc = self.cleaned_data.get("description", "")
        return strip_tags(desc)
