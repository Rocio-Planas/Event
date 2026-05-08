from django import forms
from django.forms import inlineformset_factory
from .models import Survey, SurveyOption


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'is_multiple_choice', 'is_active', 'delivery_type', 'scheduled_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control border-0 py-2', 'style': 'background-color: var(--surface-container-high);', 'placeholder': 'Título de la encuesta'}),
            'is_multiple_choice': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'delivery_type': forms.Select(attrs={'class': 'form-select border-0 py-2', 'style': 'background-color: var(--surface-container-high);'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control border-0 py-2', 'style': 'background-color: var(--surface-container-high);', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        input_formats = {
            'scheduled_date': ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        }


class SurveyOptionForm(forms.ModelForm):
    class Meta:
        model = SurveyOption
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control border-0 py-2', 'style': 'background-color: var(--surface-container-high);', 'placeholder': 'Texto de la opción'}),
        }


SurveyOptionFormSet = inlineformset_factory(
    Survey,
    SurveyOption,
    form=SurveyOptionForm,
    extra=2,
    can_delete=True,
    min_num=2,
    validate_min=True,
)