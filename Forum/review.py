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
                'placeholder': 'Tulis review Anda tentang event ini...',
                'rows': 4,
                'class': 'form-textarea-review',
            })
        }