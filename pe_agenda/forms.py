from django import forms
from .models import Activity


class ActivityForm(forms.ModelForm):
    """
    Formulario para crear y editar actividades de un evento.
    """
    
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Fecha y hora de inicio'
        }),
        label='Hora de Inicio'
    )
    
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Fecha y hora de finalización'
        }),
        label='Hora de Finalización'
    )
    
    class Meta:
        model = Activity
        fields = ['title', 'description', 'start_time', 'end_time', 'location', 'speaker_name', 'speaker_email']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la actividad'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la actividad',
                'rows': 4
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Zona o ubicación'
            }),
            'speaker_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del ponente'
            }),
            'speaker_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email del ponente'
            }),
        }
