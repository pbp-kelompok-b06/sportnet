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
            "organizer",
            "start_time",
            "end_time",
            "location",
            "address",
            "sports_category",
            "activity_category",
            "price",
            "currency",
        ]
        widgets = {
            "start_time": forms.TextInput(attrs={
                "class": "datetimepicker",
                "placeholder": "Select start date and time"
            }),
            "end_time": forms.TextInput(attrs={
                "class": "datetimepicker",
                "placeholder": "Select end date and time"
            }),
        }
        
    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        return strip_tags(name)

    def clean_description(self):
        desc = self.cleaned_data.get("description", "")
        return strip_tags(desc)
