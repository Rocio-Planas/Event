from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Event
from pe_registration.models import TicketType

class EventForm(forms.ModelForm):
    """Formulario para crear eventos"""

    # Campo adicional para tickets (no está en el modelo Event)
    tickets_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        help_text="JSON con la información de los tickets"
    )

    # Campos con choices personalizados
    category = forms.ChoiceField(
        choices=[
            ('conference', 'Conferencia'),
            ('workshop', 'Taller'),
            ('networking', 'Networking'),
            ('concert', 'Concierto'),
            ('other', 'Otro'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select form-control-custom'
        })
    )

    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'fileInput'
        })
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_date', 'end_date', 'category',
            'location', 'capacity', 'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-custom',
                'placeholder': 'Ej: Conferencia Tech 2024'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-custom',
                'rows': 4,
                'placeholder': 'Describe de qué trata tu evento...'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control form-control-custom',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control form-control-custom',
                'type': 'datetime-local'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control form-control-custom',
                'placeholder': 'Busca una ubicación o dirección...'
            }),
            'capacity': forms.NumberInput(attrs={
                'id': 'capacitySlider',
                'class': 'form-control form-control-custom',
                'type': 'range',
                'min': 0,
                'max': 2000,
                'step': 10,
            }),
            'visibility': forms.RadioSelect(attrs={
                'class': 'form-check-input',
                'id': 'visibilityRadio'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Establecer la fecha mínima a hoy (formato correcto para datetime-local)
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%dT%H:%M')
        self.fields['start_date'].widget.attrs['min'] = today
        self.fields['end_date'].widget.attrs['min'] = today

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Validar que las fechas no sean en el pasado
        now = timezone.now()
        if start_date and start_date < now:
            raise forms.ValidationError("La fecha de inicio no puede ser en el pasado.")
        
        # Validar que la fecha de fin sea después de la fecha de inicio
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("La fecha de finalización debe ser posterior a la fecha de inicio.")
        
        if end_date and end_date < now:
            raise forms.ValidationError("La fecha de finalización no puede ser en el pasado.")
        
        # Validar que end_date sea posterior a start_date
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("La fecha de finalización debe ser posterior a la fecha de inicio.")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.organizer = self.user
        if commit:
            instance.save()
        return instance