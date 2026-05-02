from django import forms
from .models import Resena, Consulta
from virtualEvent.models import VirtualEvent
from in_person_events.models import Event as EventoPresencial


class ResenaForm(forms.ModelForm):
    tipo_evento = forms.ChoiceField(
        choices=[('', 'Seleccione tipo'), ('virtual', 'Virtual'), ('presencial', 'Presencial')],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
            'id': 'id_tipo_evento_review',
            'onchange': 'updateEventoSelect(\'review\')'
        }),
        required=True
    )
    evento_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Resena
        fields = ['nombre', 'email', 'calificacion', 'comentario']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'calificacion': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'comentario': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_evento')
        evento_id = cleaned_data.get('evento_id')
        if not tipo:
            raise forms.ValidationError("Debes seleccionar un tipo de evento.")
        if not evento_id:
            raise forms.ValidationError("Debes seleccionar un evento.")
        if tipo == 'virtual':
            if not VirtualEvent.objects.filter(id=evento_id).exists():
                raise forms.ValidationError("El evento virtual seleccionado no existe.")
        elif tipo == 'presencial':
            if not EventoPresencial.objects.filter(id=evento_id).exists():
                raise forms.ValidationError("El evento presencial seleccionado no existe.")
        return cleaned_data


class ConsultaForm(forms.ModelForm):
    tipo_evento = forms.ChoiceField(
        choices=[('', 'Seleccione tipo (opcional)'), ('virtual', 'Virtual'), ('presencial', 'Presencial')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
            'id': 'id_tipo_evento_inquiry',
            'onchange': 'updateEventoSelect(\'inquiry\')'
        })
    )
    evento_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Consulta
        fields = ['nombre', 'email', 'tipo', 'asunto', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'tipo': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'asunto': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'mensaje': forms.Textarea(attrs={'rows': 5, 'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
        }