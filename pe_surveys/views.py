from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.forms import modelformset_factory
from django.apps import apps

from .models import Survey, SurveyOption, Response
from .forms import SurveyForm, SurveyOptionFormSet


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
        event_id = self.kwargs.get('event_id')
        queryset = Survey.objects.filter(event_id=event_id)
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get('event_id')
        Event = apps.get_model('in_person_events', 'Event')
        event = get_object_or_404(Event, id=event_id)
        context['event'] = event
        context['active_page'] = 'encuestas'
        context['form'] = SurveyForm()
        context['formset'] = SurveyOptionFormSet(prefix='options')
        return context


@method_decorator(login_required, name='dispatch')
class SurveyCreateUpdateView(TemplateView):
    template_name = 'pe_surveys/survey_list.html'

    def get(self, request, pk=None, **kwargs):
        event_id = self.kwargs.get('event_id')
        Event = apps.get_model('in_person_events', 'Event')
        event = get_object_or_404(Event, id=event_id)
        
        if pk:
            survey = get_object_or_404(Survey, pk=pk)
            formset = SurveyOptionFormSet(instance=survey, prefix='options')
        else:
            survey = Survey()
            formset = SurveyOptionFormSet(prefix='options')

        form = SurveyForm(instance=survey) if pk else SurveyForm()

        return self.render_to_response({
            'form': form,
            'formset': formset,
            'survey': survey,
            'event': event,
            'active_page': 'encuestas'
        })

    def post(self, request, pk=None, **kwargs):
        event_id = self.kwargs.get('event_id')
        Event = apps.get_model('in_person_events', 'Event')
        event = get_object_or_404(Event, id=event_id)
        
        if pk:
            survey = get_object_or_404(Survey, pk=pk)
            formset = SurveyOptionFormSet(request.POST, instance=survey, prefix='options')
        else:
            survey = Survey()
            formset = SurveyOptionFormSet(request.POST, prefix='options')

        form = SurveyForm(request.POST, instance=survey)

        if form.is_valid() and formset.is_valid():
            # Validaciones adicionales
            survey_type = form.cleaned_data.get('survey_type')
            valid_options_count = 0
            if survey_type == 'texto':
                # Contar opciones válidas (con texto y no eliminadas)
                for opt_form in formset:
                    if opt_form.cleaned_data:
                        is_deleted = opt_form.cleaned_data.get('DELETE', False)
                        opt_text = opt_form.cleaned_data.get('text', '').strip()
                        if not is_deleted and opt_text:
                            valid_options_count += 1
                
                if valid_options_count < 2:
                    form.add_error(None, "Las encuestas de tipo TEXTO deben tener al menos 2 opciones.")
            
            if not form.errors:
                survey = form.save(commit=False)
                survey.event_id = event_id
                is_new = not survey.pk
                survey.save()
                
                if survey_type == 'texto':
                    SurveyOption.objects.filter(survey=survey).delete()
                    for opt_form in formset:
                        if opt_form.cleaned_data:
                            is_deleted = opt_form.cleaned_data.get('DELETE', False)
                            opt_text = opt_form.cleaned_data.get('text', '').strip()
                            if not is_deleted and opt_text:
                                SurveyOption.objects.create(survey=survey, text=opt_text)
                else:
                    formset.instance = survey
                    formset.save()
                
                if is_new and survey.delivery_type == 'inmediato':
                    self.send_survey_emails(survey, event_id)
                
                return redirect('pe_surveys:survey_list', event_id=event_id)

        return self.render_to_response({
            'form': form,
            'formset': formset,
            'survey': survey,
            'event': event,
            'active_page': 'encuestas'
        })

    def send_survey_emails(self, survey, event_id):
        from django.conf import settings
        from django.core.mail import send_mail
        from django.apps import apps
        from django.urls import reverse

        Registration = apps.get_model('pe_registration', 'Registration')
        registrations = Registration.objects.filter(
            event_id=event_id,
            status=Registration.Status.CONFIRMADA
        ).select_related('user')

        survey_link = self.request.build_absolute_uri(reverse('pe_surveys:survey_answer', kwargs={'event_id': event_id, 'survey_id': survey.pk}))
        
        for reg in registrations:
            if reg.user.email:
                try:
                    send_mail(
                        subject=f"Encuesta: {survey.title}",
                        message=f"Por favor, responde la encuesta '{survey.title}'.\n\nSigue este enlace: {survey_link}\n\nGracias por tu participación.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[reg.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error sending email to {reg.user.email}: {e}")


@method_decorator(login_required, name='dispatch')
class SurveyDeleteView(DeleteView):
    model = Survey
    template_name = 'pe_surveys/survey_confirm_delete.html'
    
    def get_success_url(self):
        event_id = self.kwargs.get('event_id')
        return reverse('pe_surveys:survey_list', kwargs={'event_id': event_id})


@method_decorator(login_required, name='dispatch')
class SurveyToggleView(View):
    def post(self, request, pk, **kwargs):
        survey = get_object_or_404(Survey, pk=pk)
        survey.is_active = not survey.is_active
        survey.save()
        return JsonResponse({'success': True, 'is_active': survey.is_active})


@method_decorator(login_required, name='dispatch')
class SendSurveyAPIView(View):
    def post(self, request, pk, **kwargs):
        from django.utils import timezone
        from django.apps import apps
        from django.conf import settings
        from django.core.mail import send_mail
        import logging
        logger = logging.getLogger(__name__)

        try:
            event_id = self.kwargs.get('event_id')
            survey = get_object_or_404(Survey, pk=pk, event_id=event_id)

            if survey.delivery_type == 'programado' and survey.scheduled_date:
                if survey.scheduled_date > timezone.now():
                    return JsonResponse({'success': False, 'error': 'La encuesta está programada para una fecha futura.'}, status=400)

            Registration = apps.get_model('pe_registration', 'Registration')
            registrations = Registration.objects.filter(
                event_id=event_id,
                status=Registration.Status.CONFIRMADA
            ).select_related('user')

            survey_link = request.build_absolute_uri(reverse('pe_surveys:survey_answer', kwargs={'event_id': event_id, 'survey_id': survey.pk}))
            
            emails_sent = 0
            for reg in registrations:
                if reg.user.email:
                    try:
                        send_mail(
                            subject=f"Encuesta: {survey.title}",
                            message=f"Por favor, responde la encuesta '{survey.title}'.\n\nSigue este enlace: {survey_link}\n\nGracias por tu participación.",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[reg.user.email],
                            fail_silently=False,
                        )
                        emails_sent += 1
                    except Exception as e:
                        logger.error(f"Error sending email to {reg.user.email}: {e}")

            return JsonResponse({'success': True, 'emails_sent': emails_sent, 'message': 'Encuesta enviada correctamente.'})
        except Exception as e:
            logger.error(f"Error in SendSurveyAPIView: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator(login_required, name='dispatch')
class UpdateSurveyAPIView(View):
    def post(self, request, event_id, **kwargs):
        import json
        from django.http import JsonResponse
        
        data = json.loads(request.body)
        survey_id = data.get('survey_id')
        title = data.get('title')
        survey_type = data.get('survey_type')
        is_multiple_choice = data.get('is_multiple_choice', False)
        delivery_type = data.get('delivery_type')
        scheduled_date = data.get('scheduled_date')
        options = data.get('options', [])
        
        if not survey_id:
            return JsonResponse({'success': False, 'error': 'ID de encuesta requerido'}, status=400)
        
        survey = get_object_or_404(Survey, pk=survey_id)
        survey.title = title
        survey.survey_type = survey_type
        survey.is_multiple_choice = is_multiple_choice
        survey.delivery_type = delivery_type
        
        if scheduled_date:
            from django.utils.dateparse import parse_datetime
            survey.scheduled_date = parse_datetime(scheduled_date)
        else:
            survey.scheduled_date = None
        
        survey.save()
        
        if survey_type == 'texto':
            survey.options.all().delete()
            for opt_text in options:
                SurveyOption.objects.create(survey=survey, text=opt_text)
        
        return JsonResponse({'success': True, 'message': 'Encuesta actualizada correctamente'})


@method_decorator(login_required, name='dispatch')
class DeleteSurveyAPIView(View):
    def post(self, request, event_id, **kwargs):
        import json
        from django.http import JsonResponse
        
        data = json.loads(request.body)
        survey_id = data.get('survey_id')
        
        if not survey_id:
            return JsonResponse({'success': False, 'error': 'ID de encuesta requerido'}, status=400)
        
        survey = get_object_or_404(Survey, pk=survey_id)
        survey.delete()
        
        return JsonResponse({'success': True, 'message': 'Encuesta eliminada correctamente'})


@method_decorator(login_required, name='dispatch')
class SurveyResultsView(TemplateView):
    template_name = 'pe_surveys/survey_results.html'

    def get(self, request, pk, **kwargs):
        event_id = self.kwargs.get('event_id')
        Event = apps.get_model('in_person_events', 'Event')
        event = get_object_or_404(Event, id=event_id)
        
        survey = get_object_or_404(Survey, pk=pk, event_id=event_id)
        responses = Response.objects.filter(survey=survey)
        
        survey_options = {opt.pk: opt.text for opt in survey.options.all()}
        
        processed_responses = []
        for response in responses:
            answer_data = response.answer
            if isinstance(answer_data, dict):
                answer_val = answer_data.get('answer', '')
                comments = answer_data.get('comments', '')
            else:
                answer_val = answer_data
                comments = ''
            
            if isinstance(answer_val, list):
                option_names = []
                for opt_pk in answer_val:
                    opt_text = survey_options.get(opt_pk, str(opt_pk))
                    option_names.append(opt_text)
                answer_display = '; '.join(option_names)
            else:
                answer_display = survey_options.get(answer_val, str(answer_val))
            
            processed_responses.append({
                'answer_display': answer_display,
                'comments': comments,
                'created_at': response.created_at
            })

        from collections import defaultdict
        results = defaultdict(list)
        if survey.survey_type == 'escala':
            for response in responses:
                results['Escala 1-5'].append(response.answer)
        elif survey.survey_type == 'texto':
            for option in survey.options.all():
                results[option.text] = []
            for response in responses:
                answer_data = response.answer
                if isinstance(answer_data, dict):
                    answer_value = answer_data.get('answer')
                else:
                    answer_value = answer_data
                if isinstance(answer_value, list):
                    for opt_pk in answer_value:
                        opt_text = survey_options.get(opt_pk, f"Opción {opt_pk}")
                        if opt_text in results:
                            results[opt_text].append(1)
                else:
                    opt_text = survey_options.get(answer_value, f"Opción {answer_value}")
                    if opt_text in results:
                        results[opt_text].append(1)

        return self.render_to_response({
            'survey': survey,
            'results': dict(results),
            'responses': processed_responses,
            'event': event,
            'active_page': 'encuestas'
        })


class SurveyAnswerView(TemplateView):
    template_name = 'pe_surveys/survey_answer.html'

    def get(self, request, event_id, survey_id, **kwargs):
        survey = get_object_or_404(Survey, pk=survey_id, event_id=event_id, is_active=True)
        return self.render_to_response({
            'survey': survey,
            'event_id': event_id
        })


class SurveyResponseAPIView(View):
    def post(self, request, event_id, survey_id, **kwargs):
        import json
        from django.http import JsonResponse

        survey = get_object_or_404(Survey, pk=survey_id, event_id=event_id, is_active=True)
        
        data = json.loads(request.body)
        answer = data.get('answer')
        comments = data.get('comments', '')

        user_id = request.user.id if request.user.is_authenticated else None
        
        Response.objects.create(
            survey=survey,
            user_id=user_id,
            answer={'answer': answer, 'comments': comments}
        )

        return JsonResponse({'success': True, 'message': 'Respuesta guardada correctamente'})