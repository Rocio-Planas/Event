from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Usuario, PreferenciaUsuario
from core.models import CategoriaEvento

class RegistroForm(UserCreationForm):
    # ... (todo igual que antes, no cambia)
    first_name = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    last_name = forms.CharField(
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    sexo = forms.ChoiceField(
        choices=Usuario.SEXOS,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    categorias = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento',
                  'sexo', 'password1', 'password2', 'categorias')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Este email ya está registrado')
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Las contraseñas no coinciden')
        return p2

    def clean_categorias(self):
        data = self.cleaned_data.get('categorias')
        if not data:
            raise ValidationError('Debes seleccionar al menos 3 categorías.')
        ids = data.split(',')
        if len(ids) < 3:
            raise ValidationError('Debes seleccionar al menos 3 categorías.')
        categorias_qs = CategoriaEvento.objects.filter(id__in=ids, activo=True)
        if categorias_qs.count() != len(ids):
            raise ValidationError('Alguna categoría seleccionada no es válida.')
        return categorias_qs

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.rol = 'espectador'
        if commit:
            user.save()
            categorias = self.cleaned_data['categorias']
            for cat in categorias:
                PreferenciaUsuario.objects.create(usuario=user, categoria=cat)
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    remember_me = forms.BooleanField(label='Recordarme', required=False)


class RecuperacionPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Email registrado',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not Usuario.objects.filter(email=email).exists():
            raise ValidationError('No existe una cuenta con este email')
        return email


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'telefono', 'avatar', 'fecha_nacimiento', 'sexo',
            'direccion', 'biografia', 'website', 'twitter', 'instagram', 'linkedin',
            'recibir_notificaciones', 'recibir_newsletter'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
                'placeholder': 'Tu nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
                'placeholder': 'Tu apellido'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
                'placeholder': '+34 123 456 789'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
            }),
            'sexo': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
            }),
            'direccion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
                'placeholder': 'Calle, número, ciudad, código postal'
            }),
            'biografia': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
                'placeholder': 'Cuéntanos algo sobre ti...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
                'placeholder': 'https://tusitio.com'
            }),
            'twitter': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
                'placeholder': '@usuario'
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
                'placeholder': '@usuario'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all',
                'placeholder': 'https://linkedin.com/in/usuario'
            }),
            'recibir_notificaciones': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary rounded focus:ring-primary'
            }),
            'recibir_newsletter': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary rounded focus:ring-primary'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False


class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )
    nueva_password = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        }),
        min_length=8
    )
    confirmar_password = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/20 focus:ring-4 focus:ring-primary-fixed-dim/30 focus:border-primary outline-none transition-all'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get('nueva_password')
        confirmar = cleaned_data.get('confirmar_password')
        if nueva and confirmar and nueva != confirmar:
            self.add_error('confirmar_password', 'Las contraseñas no coinciden')
        return cleaned_data


# Formulario para editar preferencias (CORREGIDO)
class PreferenciasForm(forms.Form):
    categorias = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user.is_authenticated:
            # Inicializar con los IDs de las categorías actuales del usuario
            initial_ids = ','.join(str(c.id) for c in user.preferencias.all())
            self.fields['categorias'].initial = initial_ids

    def clean_categorias(self):
        data = self.cleaned_data.get('categorias')
        if not data:
            raise ValidationError('Debes seleccionar al menos 3 categorías.')
        ids = data.split(',')
        if len(ids) < 3:
            raise ValidationError('Debes seleccionar al menos 3 categorías.')
        categorias = CategoriaEvento.objects.filter(id__in=ids, activo=True)
        if categorias.count() != len(ids):
            raise ValidationError('Alguna categoría seleccionada no es válida.')
        return categorias

    def save(self):
        categorias = self.cleaned_data['categorias']
        self.user.preferencias.set(categorias)