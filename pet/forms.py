from django import forms
from .models import Pet


class PetForm(forms.ModelForm):
    """Form for creating and customizing a virtual pet."""

    class Meta:
        model = Pet
        fields = ['name', 'pet_type', 'personality']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your pet’s name (e.g. Coco, Luna, Mochi)',
                'autocomplete': 'off',
                'required': True,
                'maxlength': 60,
                'id': 'pet-name-input',
            }),
            'pet_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'pet-type-select',
            }),
            'personality': forms.Select(attrs={
                'class': 'form-select',
                'id': 'pet-personality-select',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Please provide a name for your virtual pet.")
        return name


class ChatMessageForm(forms.Form):
    """Form for sending a chat message to the virtual pet."""

    message = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'chat-input-field',
            'placeholder': 'Ask Coco something... (e.g., "Are you hungry?", "Let\'s play!")',
            'autocomplete': 'off',
            'required': True,
            'id': 'chat-user-message-input',
        })
    )
