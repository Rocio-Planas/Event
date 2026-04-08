from django import forms
from .models import Resena, Consulta

class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['nombre', 'email', 'evento_id', 'evento_titulo', 'calificacion', 'comentario']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'evento_id': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all', 'placeholder': 'ID del evento (opcional)'}),
            'evento_titulo': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all', 'placeholder': 'Título del evento'}),
            'calificacion': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'comentario': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all', 'placeholder': 'Cuéntanos tu experiencia...'}),
        }

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['nombre', 'email', 'tipo', 'evento_id', 'evento_titulo', 'asunto', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'tipo': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'evento_id': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all', 'placeholder': 'ID del evento (opcional)'}),
            'evento_titulo': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all', 'placeholder': 'Título del evento (opcional)'}),
            'asunto': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
            'mensaje': forms.Textarea(attrs={'rows': 5, 'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'}),
        }