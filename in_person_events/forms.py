import json

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

    # Campo adicional para invitaciones por email
    invitations = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control ev-input py-3 px-4 rounded-3',
            'rows': 3,
            'placeholder': 'Ingresa direcciones de email separadas por comas...'
        }),
        required=False,
        help_text="Emails de invitados separados por comas (solo para eventos privados)"
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
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select ev-input py-3 px-4 rounded-3 cursor-pointer',
            'required': 'required'
        })
    )

    visibility = forms.ChoiceField(
        choices=Event.Visibility.choices,
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
            'id': 'visibilityRadio'
        }),
        initial=Event.Visibility.PUBLICO,
        label='Visibilidad'
    )

    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'ev-file-input position-absolute w-100 h-100 opacity-0 cursor-pointer',
            'id': 'evImageInput',
            'id': 'fileInput'
        })
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_date', 'end_date', 'category',
            'location', 'capacity', 'image', 'visibility'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control ev-input py-3 px-4 rounded-3',
                'placeholder': 'Ej: Conferencia Tech 2024',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control ev-input py-3 px-4 rounded-3',
                'rows': 4,
                'placeholder': 'Describe de qué trata tu evento...',
                'required': 'required'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control ev-input py-3 px-4 rounded-3',
                'type': 'datetime-local',
                'required': 'required'
            }, format='%Y-%m-%dT%H:%M'),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control ev-input py-3 px-4 rounded-3',
                'type': 'datetime-local',
                'required': 'required'
            }, format='%Y-%m-%dT%H:%M'),
            'location': forms.TextInput(attrs={
                'class': 'form-control ev-input py-3 px-4 rounded-3',
                'placeholder': 'Busca una ubicación o dirección...',
                'required': 'required'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control ev-input py-3 px-4 rounded-3',
                'type': 'number',
                'min': 1,
                'max': 2000,
                'step': 1,
                'placeholder': 'Capacidad máxima',
                'required': 'required'
            }),
            'visibility': forms.RadioSelect(attrs={
                'class': 'form-check-input',
                'id': 'visibilityRadio'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # En creación, establecer fecha mínima a hoy
        if not self.instance.pk:
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%dT%H:%M')
            self.fields['start_date'].widget.attrs['min'] = today
            self.fields['end_date'].widget.attrs['min'] = today

        # En edición no es obligatorio volver a subir la imagen si ya existe
        if self.instance and self.instance.pk:
            self.fields['image'].required = False
            self.fields['visibility'].initial = self.instance.visibility

        # Asegurar formato compatible con datetime-local
        if 'start_date' in self.fields:
            self.fields['start_date'].input_formats = ['%Y-%m-%dT%H:%M']
        if 'end_date' in self.fields:
            self.fields['end_date'].input_formats = ['%Y-%m-%dT%H:%M']
        
        # Marcar los campos con errores para mostrar el estilo de error
        for field_name in self.errors:
            if field_name in self.fields:
                widget = self.fields[field_name].widget
                existing_class = widget.attrs.get('class', '')
                if 'is-invalid' not in existing_class:
                    widget.attrs['class'] = (existing_class + ' is-invalid').strip()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        capacity = cleaned_data.get('capacity')
        visibility = cleaned_data.get('visibility')
        invitations = cleaned_data.get('invitations', '').strip()
        tickets_json = cleaned_data.get('tickets_data', '[]')

        now = timezone.now()
        
        # Solo validar fechas futuras en creación, no en edición
        if not self.instance.pk:
            if start_date and start_date < now:
                raise forms.ValidationError("La fecha de inicio no puede ser en el pasado.")
            if end_date and end_date < now:
                raise forms.ValidationError("La fecha de finalización no puede ser en el pasado.")

        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("La fecha de finalización debe ser posterior a la fecha de inicio.")

        if capacity is None or capacity <= 0:
            self.add_error('capacity', "La capacidad debe ser mayor que cero.")

        if visibility == Event.Visibility.PRIVADO and not invitations:
            self.add_error('invitations', "Debes ingresar al menos un email para eventos privados.")

        try:
            if not tickets_json:
                ticket_list = []
            else:
                ticket_list = json.loads(tickets_json)
        except json.JSONDecodeError:
            raise forms.ValidationError("La información de las entradas es inválida.")

        invalid_ticket = False
        for ticket in ticket_list:
            name = str(ticket.get('name', '')).strip()
            price = ticket.get('price', 0)
            if not name:
                invalid_ticket = True
            if price is None or price < 0:
                invalid_ticket = True

        if invalid_ticket:
            raise forms.ValidationError("Los tickets deben tener nombre y precio válidos.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.organizer = self.user
        instance.visibility = self.cleaned_data.get('visibility', Event.Visibility.PUBLICO)
        if commit:
            instance.save()
        return instance