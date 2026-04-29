import json
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Q

from in_person_events.models import Event
from pe_registration.models import Registration, TicketType


def home(request):
    return HttpResponse("Página de registro de tickets")


@method_decorator(login_required, name='dispatch')
class AttendeesView(TemplateView):
    """Vista para listar los asistentes inscritos a un evento."""
    template_name = 'pe_registration/attendees.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        event_id = self.kwargs.get('event_id')
        # Verificar que el usuario sea el organizador del evento
        event = get_object_or_404(Event, id=event_id, organizer=self.request.user)
        
        # Obtener inscripciones confirmadas
        registrations = Registration.objects.filter(
            event_id=event_id,
            status=Registration.Status.CONFIRMADA
        ).select_related('user', 'ticket_type')
        
        # Obtener ticket types del evento
        ticket_types = TicketType.objects.filter(event_id=event_id)
        
        # Calcular estadísticas
        total_registered = registrations.count()
        total_confirmed = registrations.filter(payment_status='completado').count()
        total_pending = registrations.filter(payment_status='pendiente').count()
        
        # Preparar datos para JSON
        attendees_data = []
        for reg in registrations:
            attendees_data.append({
                'id': reg.id,
                'name': reg.user.get_full_name() or reg.user.email,
                'email': reg.user.email,
                'ticket_type': reg.ticket_type.name if reg.ticket_type else 'General',
                'status': reg.payment_status,
                'registration_date': reg.registration_date.isoformat(),
            })
        
        context['event'] = event
        context['registrations'] = registrations
        context['ticket_types'] = ticket_types
        context['attendees_json'] = json.dumps(attendees_data)
        context['total_registered'] = total_registered
        context['total_confirmed'] = total_confirmed
        context['total_pending'] = total_pending
        context['event_id'] = event_id
        context['active_page'] = 'asistentes'
        
        return context


@login_required
def get_attendees(request, event_id):
    """API para obtener los asistentes de un evento."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    ticket_filter = request.GET.get('ticket', 'all')
    
    registrations = Registration.objects.filter(
        event_id=event_id,
        status=Registration.Status.CONFIRMADA
    ).select_related('user', 'ticket_type')
    
    # Aplicar filtros
    if search:
        registrations = registrations.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    if status_filter != 'all':
        registrations = registrations.filter(payment_status=status_filter)
    
    if ticket_filter != 'all':
        registrations = registrations.filter(ticket_type_id=ticket_filter)
    
    attendees_data = []
    for reg in registrations:
        attendees_data.append({
            'id': reg.id,
            'name': reg.user.get_full_name() or reg.user.email,
            'email': reg.user.email,
            'ticket_type': reg.ticket_type.name if reg.ticket_type else 'General',
            'status': reg.payment_status,
            'registration_date': reg.registration_date.isoformat(),
        })
    
    return JsonResponse({
        'success': True,
        'attendees': attendees_data,
        'count': len(attendees_data)
    })


@login_required
def update_registration(request, event_id, registration_id):
    """API para actualizar el estado de una inscripción."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    registration = get_object_or_404(
        Registration, 
        id=registration_id, 
        event_id=event_id
    )
    
    import json
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status:
            registration.payment_status = new_status
            registration.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Estado actualizado correctamente'
            })
        else:
            return JsonResponse({'error': 'Estado requerido'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)