from django import forms
from .models import ForumPost  

class ForumPostForm(forms.ModelForm):
    """
    Formulir untuk membuat atau membalas post di forum.
    """
    class Meta:
        model = ForumPost
        fields = ['content']

        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Ketik pesan Anda...',
                'class': 'form-input-chat', 
                'autocomplete': 'off',
            })
        }

        labels = {
            'content': '',
        }