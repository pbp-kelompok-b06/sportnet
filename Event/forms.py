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
            "price",
            "currency",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "field",
            }),
            "description": forms.Textarea(attrs={
                "class": "field h-[100px]",
            }),
            "thumbnail": forms.URLInput(attrs={
                "class": "field",
            }),
            "start_time": forms.TextInput(attrs={
                "class": "field datetimepicker w-[150px]",
                "placeholder": "Start"
            }),
            "end_time": forms.TextInput(attrs={
                "class": "field datetimepicker w-[150px]",
                "placeholder": "End"
            }),
            "location": forms.TextInput(attrs={
                "class": "field",
            }),
            "address": forms.Textarea(attrs={
                "class": "field h-[100px]",
            }),
            "sports_category": forms.Select(attrs={
                "class": "field w-[140px]",
            }),
            "activity_category": forms.Select(attrs={
                "class": "field w-[140px]",
            }),
            "price": forms.NumberInput(attrs={
                "class": "field w-[150px]",
            }),
            "currency": forms.TextInput(attrs={
                "class": "field w-[30px]",
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        return strip_tags(name)

    def clean_description(self):
        desc = self.cleaned_data.get("description", "")
        return strip_tags(desc)
