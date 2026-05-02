import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Sum
from django.utils.text import slugify

# Importamos tus modelos y el formulario
from .models import Event
from pe_registration.models import TicketType, Registration
from .forms import EventForm
from pe_communication.views import send_event_invitation_email

@login_required
def create_event_form(request):
    """
    Vista para crear eventos (create_event_form.html).
    Maneja el formulario de Django y la creación dinámica de tickets vía JSON.
    """
    if request.method == 'GET':
        # Consumir mensajes existentes para evitar que se muestren en cargas posteriores
        list(messages.get_messages(request))
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            try:
                event = form.save(commit=False)
                event.organizer = request.user
                event.save()

                tickets_json = request.POST.get('tickets_data', '[]')
                try:
                    tickets_list = json.loads(tickets_json) if tickets_json else []
                except json.JSONDecodeError:
                    messages.error(request, 'Error al procesar los tickets.')
                    return render(request, 'create_event_form.html', {'form': form})

                created_ticket_type = None
                for t_data in tickets_list:
                    ticket_type = TicketType.objects.create(
                        event=event,
                        name=t_data.get('name', 'Entrada General'),
                        price=t_data.get('price', 0)
                    )
                    if created_ticket_type is None:
                        created_ticket_type = ticket_type

                if created_ticket_type is None:
                    created_ticket_type = TicketType.objects.create(
                        event=event,
                        name='Entrada General',
                        price=25,
                    )

                if event.visibility == Event.Visibility.PRIVADO:
                    invitations_text = form.cleaned_data.get('invitations', '').strip()
                    if invitations_text:
                        invitations_text = invitations_text.replace(';', ',').replace('\n', ',').replace('\r', ',')
                        invitations_list = [email.strip() for email in invitations_text.split(',') if email.strip()]
                        invitations_list = list(dict.fromkeys(invitations_list))

                        organizer_name = request.user.get_full_name() or request.user.email
                        User = get_user_model()

                        for email in invitations_list:
                            try:
                                validate_email(email)
                            except ValidationError:
                                messages.warning(request, f'Email inválido omitido: {email}')
                                continue

                            result = send_event_invitation_email(
                                recipient_email=email,
                                event=event,
                                organizer_name=organizer_name,
                                custom_message=None,
                            )
                            if not result.get('success'):
                                messages.warning(request, f'No se pudo enviar invitación a {email}: {result.get("error")}')

                            invited_user = User.objects.filter(email__iexact=email).first()
                            if invited_user:
                                # Invitados enviados desde el formulario de evento privado quedan como pendientes
                                Registration.objects.get_or_create(
                                    event=event,
                                    user=invited_user,
                                    defaults={
                                        'ticket_type': created_ticket_type,
                                        'status': Registration.Status.PENDIENTE,
                                        'payment_status': 'pendiente',
                                    }
                                )

                return redirect('in_person_events:success_page', event_id=event.id)

            except json.JSONDecodeError:
                messages.error(request, 'Error al procesar los tickets.')
            except Exception as e:
                messages.error(request, f'Error al procesar el evento: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = EventForm(user=request.user)

    return render(request, 'create_event_form.html', {
        'form': form
    })


@login_required
def success_page(request, event_id):
    """Página de éxito luego de crear un evento."""
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    return render(request, 'success_page.html', {
        'event': event
    })


@login_required
def dashboard_organizer(request, event_id):
    """Dashboard para el organizador."""
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    ticket_types = event.ticket_types.all()
    registrations = event.registrations.select_related('ticket_type').all()
    total_attendees = registrations.count()
    ticket_type_counts = registrations.values('ticket_type__name').annotate(count=Count('id')).order_by('ticket_type__name')
    total_revenue = registrations.aggregate(total=Sum('ticket_type__price'))['total'] or 0
    return render(request, 'dashboard_organizer.html', {
        'event': event,
        'ticket_types': ticket_types,
        'total_attendees': total_attendees,
        'ticket_type_counts': ticket_type_counts,
        'total_revenue': total_revenue,
        'active_page': 'resumen'
    })


@login_required
def dashboard_assistant(request, event_id):
    """Dashboard del asistente para un evento presencial inscrito."""
    event = get_object_or_404(Event, id=event_id)
    activities = event.activities.order_by('start_time')[:5]
    ticket_types = event.ticket_types.all()
    resources = event.resources.all()
    return render(request, 'dashboard_assistant.html', {
        'event': event,
        'activities': activities,
        'ticket_types': ticket_types,
        'resources': resources,
    })


@login_required
def edit_event(request, event_id):
    """Vista para editar un evento existente."""
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    tickets_json = '[]'

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event, user=request.user)
        
        if form.is_valid():
            try:
                event = form.save(commit=False)
                event.save()
                
                # Procesar tickets siempre
                tickets_json = request.POST.get('tickets_data', '[]')
                try:
                    tickets_list = json.loads(tickets_json) if tickets_json else []
                    # Verificar si hay registros antes de eliminar tickets
                    if event.registrations.exists():
                        messages.warning(request, 'Los tickets no se pudieron modificar porque el evento ya tiene registros.')
                    else:
                        # Limpiar tickets antiguos y crear nuevos
                        event.ticket_types.all().delete()
                        for t_data in tickets_list:
                            TicketType.objects.create(
                                event=event,
                                name=t_data.get('name', 'Entrada General'),
                                price=t_data.get('price', 0)
                            )
                except json.JSONDecodeError as e:
                    messages.error(request, f'Error al procesar los tickets: {str(e)}')
                    # Re-renderizar con los datos que fueron enviados
                    return render(request, 'edit_event_form.html', {
                        'form': form,
                        'event': event,
                        'ticket_types': event.ticket_types.all(),
                        'tickets_json': tickets_json,
                    })
                
                messages.success(request, 'Evento actualizado correctamente.')
                return redirect('in_person_events:dashboard_organizer', event_id=event.id)
            
            except Exception as e:
                messages.error(request, f'Error al actualizar el evento: {str(e)}')
                tickets_json = request.POST.get('tickets_data', '[]')
        else:
            # Si el formulario no es válido, mostramos los errores pero re-renderizamos con los datos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            tickets_json = request.POST.get('tickets_data', '[]')
    else:
        form = EventForm(instance=event, user=request.user)
        # Verificar si la imagen existe, si no, limpiarla
        import os
        if event.image and not os.path.exists(event.image.path):
            event.image = None
            event.save()
        tickets_json = json.dumps([
            {'name': t.name, 'price': float(t.price)}
            for t in event.ticket_types.all()
        ]) if event.ticket_types.exists() else '[]'
    
    ticket_types = event.ticket_types.all()
    return render(request, 'edit_event_form.html', {
        'form': form,
        'event': event,
        'ticket_types': ticket_types,
        'tickets_json': tickets_json,
    })


def configure_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    return render(request, 'configure_event.html', {
        'event': event,
        'active_page': 'configuracion'
    })
    
@login_required
@require_POST
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    deleted_event = {
        'title': event.title,
        'id': event.id,
        'image': event.image.url if event.image else None,
        'category': event.category,
        'start_date': event.start_date.isoformat() if event.start_date else None,
    }
    
    event.delete()
    
    request.session['deleted_event'] = deleted_event
    
    return redirect('in_person_events:delete_page')


@login_required
def delete_page(request):
    """Página de confirmación después de eliminar un evento."""
    deleted_event = request.session.pop('deleted_event', None)
    
    if not deleted_event:
        return redirect('in_person_events:create_event_form')
    
    return render(request, 'delete_page.html', {
        'deleted_event': deleted_event
    })
