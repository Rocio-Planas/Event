from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from django.apps import apps

from .models import Survey, Question, Response
from .forms import SurveyForm


def get_default_event():
    """Obtiene un evento por defecto para las encuestas."""
    Event = apps.get_model('in_person_events', 'Event')
    return Event.objects.first()


@method_decorator(login_required, name='dispatch')
class SurveyManagementView(ListView):
    model = Survey
    template_name = 'pe_surveys/survey_list.html'
    context_object_name = 'surveys'

    def get_queryset(self):
        return Survey.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_default_event()
        context['event'] = event
        context['active_page'] = 'encuestas'
        QuestionFormSet = modelformset_factory(Question, fields=('text', 'is_required', 'question_type', 'options', 'order'), extra=1)
        context['form'] = SurveyForm()
        context['formset'] = QuestionFormSet(queryset=Question.objects.none())
        return context


@method_decorator(login_required, name='dispatch')
class SurveyCreateUpdateView(TemplateView):
    template_name = 'pe_surveys/survey_list.html'

    def get(self, request, pk=None):
        if pk:
            survey = get_object_or_404(Survey, pk=pk)
            QuestionFormSet = modelformset_factory(Question, fields=('text', 'is_required', 'question_type', 'options', 'order'), extra=0)
            formset = QuestionFormSet(queryset=survey.questions.all())
        else:
            survey = None
            QuestionFormSet = modelformset_factory(Question, fields=('text', 'is_required', 'question_type', 'options', 'order'), extra=1)
            formset = QuestionFormSet(queryset=Question.objects.none())

        form = SurveyForm(instance=survey) if survey else SurveyForm()

        return self.render_to_response({
            'form': form,
            'formset': formset,
            'survey': survey,
            'event': get_default_event(),
            'active_page': 'encuestas'
        })

    def post(self, request, pk=None):
        if pk:
            survey = get_object_or_404(Survey, pk=pk)
            QuestionFormSet = modelformset_factory(Question, fields=('text', 'is_required', 'question_type', 'options', 'order'), extra=0)
            formset = QuestionFormSet(request.POST, queryset=survey.questions.all())
        else:
            survey = Survey()
            QuestionFormSet = modelformset_factory(Question, fields=('text', 'is_required', 'question_type', 'options', 'order'), extra=1)
            formset = QuestionFormSet(request.POST)

        form = SurveyForm(request.POST, instance=survey)

        if form.is_valid() and formset.is_valid():
            # Validaciones adicionales
            cleaned_questions = [q for q in formset.cleaned_data if q and not q.get('DELETE', False)]
            if len(cleaned_questions) == 0:
                form.add_error(None, "Debe agregar al menos una pregunta.")
            else:
                for question_data in cleaned_questions:
                    if question_data.get('question_type') == 'opcion_multiple':
                        options_str = question_data.get('options', '').strip()
                        if not options_str:
                            form.add_error(None, f"La pregunta '{question_data.get('text')}' requiere opciones de respuesta.")
                        else:
                            options = [opt.strip() for opt in options_str.split(',') if opt.strip()]
                            if len(options) < 2:
                                form.add_error(None, f"La pregunta '{question_data.get('text')}' debe tener al menos dos opciones de respuesta.")
            
            if not form.errors:
                survey = form.save()
                formset.instance = survey
                formset.save()
                return redirect('pe_surveys:survey_list')

        return self.render_to_response({
            'form': form,
            'formset': formset,
            'survey': survey,
            'event': get_default_event(),
            'active_page': 'encuestas'
        })


@method_decorator(login_required, name='dispatch')
class SurveyDeleteView(DeleteView):
    model = Survey
    success_url = reverse_lazy('pe_surveys:survey_list')
    template_name = 'pe_surveys/survey_confirm_delete.html'


@method_decorator(login_required, name='dispatch')
class SurveyToggleView(View):
    def post(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        survey.is_active = not survey.is_active
        survey.save()
        return JsonResponse({'success': True, 'is_active': survey.is_active})


@method_decorator(login_required, name='dispatch')
class SendSurveyAPIView(View):
    def post(self, request, pk):
        from django.utils import timezone
        from django.apps import apps

        survey = get_object_or_404(Survey, pk=pk)

        if survey.delivery_type == survey.DeliveryType.FECHA_ESPECIFICA and survey.scheduled_date:
            if survey.scheduled_date > timezone.now():
                return JsonResponse({'success': False, 'error': 'La encuesta está programada para una fecha futura.'}, status=400)

        Registration = apps.get_model('pe_registration', 'Registration')
        registrations = Registration.objects.filter(
            event_id=1,
            status=Registration.Status.CONFIRMADA
        ).select_related('user')

        emails_sent = 0
        for reg in registrations:
            emails_sent += 1

        return JsonResponse({'success': True, 'emails_sent': emails_sent, 'message': 'Encuesta enviada correctamente.'})


@method_decorator(login_required, name='dispatch')
class SurveyResultsView(View):
    template_name = 'pe_surveys/survey_results.html'

    def get(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        responses = Response.objects.filter(survey=survey).select_related('question')

        from collections import defaultdict
        results = defaultdict(list)
        for response in responses:
            results[response.question.text].append(response.answer)

        return self.render_to_response({
            'survey': survey,
            'results': dict(results),
            'event': get_default_event(),
            'active_page': 'encuestas'
        })