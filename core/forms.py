from django import forms
from .models import Resena, Consulta
from virtualEvent.models import VirtualEvent

class ResenaForm(forms.ModelForm):
    evento = forms.ModelChoiceField(
        queryset=VirtualEvent.objects.all(),  # ← sin filtro 'activo' (ese campo no existe)
        empty_label="Seleccione un evento",
        required=True,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'})
    )

    class Meta:
        model = Resena
        fields = ['nombre', 'email', 'evento', 'calificacion', 'comentario']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'calificacion': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'comentario': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
        }


class ConsultaForm(forms.ModelForm):
    evento = forms.ModelChoiceField(
        queryset=VirtualEvent.objects.all(),
        required=False,
        empty_label="Seleccione un evento (opcional)",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'})
    )

    class Meta:
        model = Consulta
        fields = ['nombre', 'email', 'tipo', 'evento', 'asunto', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'tipo': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'asunto': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'mensaje': forms.Textarea(attrs={'rows': 5, 'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
        }
    