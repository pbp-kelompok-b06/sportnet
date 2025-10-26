from django import forms
from .models import Review  

class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select-rating',
            }),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Write your review about this event',
                'rows': 4,
                'class': 'form-textarea-review',
            })
        }