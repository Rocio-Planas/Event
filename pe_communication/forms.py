from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ManualNotificationForm(forms.Form):
    """
    Formulario para que el organizador envíe notificaciones manuales.
    """
    AUDIENCE_CHOICES = [
        ('all', 'Todos los Usuarios'),
        ('attendees', 'Solo Asistentes'),
    ]

    audience = forms.ChoiceField(
        label='Destinatarios',
        choices=AUDIENCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    title = forms.CharField(
        label='Título',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título de la notificación'
        })
    )
    message = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Escribe el mensaje...'
        })
    )
