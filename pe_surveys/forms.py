from django import forms
from django.forms import inlineformset_factory
from .models import Survey, SurveyOption


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'survey_type', 'is_multiple_choice', 'is_active', 'delivery_type', 'scheduled_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la encuesta'}),
            'survey_type': forms.Select(attrs={'class': 'form-select survey-type-select'}),
            'is_multiple_choice': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'delivery_type': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        input_formats = {
            'scheduled_date': ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        }


class SurveyOptionForm(forms.ModelForm):
    class Meta:
        model = SurveyOption
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Texto de la opción'}),
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