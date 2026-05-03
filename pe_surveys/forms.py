from django import forms
from .models import Survey, Question


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'is_active', 'delivery_type', 'scheduled_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la encuesta'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción opcional'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'delivery_type': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'is_required', 'question_type', 'options', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Texto de la pregunta'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question_type': forms.Select(attrs={'class': 'form-select question-type-select'}),
            'options': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Opciones separadas por coma'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }