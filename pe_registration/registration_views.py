from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@require_POST
@login_required
def register_to_event(request, event_id):
    """
    Vista para registrar un usuario a un evento.
    Maneja la lógica de lista de espera cuando el evento está lleno.
    """
    from django.apps import apps
    Event = apps.get_model('in_person_events', 'Event')
    Registration = apps.get_model('pe_registration', 'Registration')
    TicketType = apps.get_model('pe_registration', 'TicketType')
    EventWaitlist = apps.get_model('pe_registration', 'EventWaitlist')
    
    try:
        ticket_type_id = request.POST.get('ticket_type_id')
        
        with transaction.atomic():
            event = Event.objects.select_for_update(nowait=False).filter(
                id=event_id,
                is_active=True
            ).first()
            
            if not event:
                return JsonResponse({'success': False, 'error': 'Evento no encontrado'}, status=404)
            
            # Contar registros confirmados
            current_registrations = Registration.objects.filter(
                event=event,
                status=Registration.Status.CONFIRMADA
            ).count()
            
            # Verificar si el usuario ya está registrado
            existing = Registration.objects.filter(
                event=event,
                user=request.user,
                status__in=[Registration.Status.CONFIRMADA, Registration.Status.PENDIENTE]
            ).first()
            
            if existing:
                return JsonResponse({
                    'success': False, 
                    'error': 'Ya estás registrado en este evento'
                }, status=400)
            
            # Verificar capacidad
            if current_registrations >= event.capacity:
                # Agregar a lista de espera
                waitlist_entry, created = EventWaitlist.objects.get_or_create(
                    event=event,
                    user=request.user,
                    defaults={'created_at': timezone.now()}
                )
                
                if created:
                    return JsonResponse({
                        'success': True,
                        'waitlist': True,
                        'message': 'El evento está lleno. Has sido agregado a la lista de espera.'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Ya estás en la lista de espera'
                    })
            
            # Crear inscripción
            ticket_type = None
            if ticket_type_id:
                ticket_type = TicketType.objects.filter(
                    id=ticket_type_id,
                    event=event
                ).first()
            
            registration = Registration.objects.create(
                event=event,
                user=request.user,
                ticket_type=ticket_type,
                status=Registration.Status.CONFIRMADA,
                payment_status='pendiente',
                registration_date=timezone.now()
            )
            
            return JsonResponse({
                'success': True,
                'registration_id': registration.id,
                'message': 'Te has registrado exitosamente'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)