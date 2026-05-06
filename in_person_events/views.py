import base64
import io
import json
import qrcode
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
    registrations = event.registrations.select_related('ticket_type').filter(status=Registration.Status.CONFIRMADA)
    total_attendees = registrations.count()
    ticket_type_counts = registrations.values('ticket_type__name').annotate(count=Count('id')).order_by('ticket_type__name')
    total_revenue = registrations.aggregate(total=Sum('ticket_type__price'))['total']
    if total_revenue is None:
        total_revenue = float(0)
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
    total_attendees = event.registrations.filter(status=Registration.Status.CONFIRMADA).count()
    user_registration = Registration.objects.filter(
        event=event,
        user=request.user,
        status__in=[Registration.Status.CONFIRMADA, Registration.Status.PENDIENTE]
    ).select_related('ticket_type').first()
    selected_ticket_type = user_registration.ticket_type if user_registration else None

    ticket_holder_name = request.user.get_full_name() or request.user.email
    ticket_type_name = selected_ticket_type.name if selected_ticket_type else 'General'
    ticket_qr_data_url = None

    if user_registration:
        qr_payload = json.dumps({
            'event_id': event.id,
            'event_title': event.title,
            'registration_id': user_registration.id,
            'user_id': request.user.id,
            'user_name': ticket_holder_name,
            'ticket_type': ticket_type_name,
        }, ensure_ascii=False)

        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=8,
            border=3,
        )
        qr.add_data(qr_payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        ticket_qr_data_url = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    return render(request, 'dashboard_assistant.html', {
        'event': event,
        'activities': activities,
        'ticket_types': ticket_types,
        'resources': resources,
        'total_attendees': total_attendees,
        'user_registration': user_registration,
        'selected_ticket_type': selected_ticket_type,
        'ticket_holder_name': ticket_holder_name,
        'ticket_type_name': ticket_type_name,
        'ticket_qr_data_url': ticket_qr_data_url,
    })


@login_required
def select_ticket_type(request, event_id):
    """Permite al asistente cambiar el tipo de ticket asignado."""
    event = get_object_or_404(Event, id=event_id)
    if request.method != 'POST':
        return redirect('in_person_events:dashboard_assistant', event_id=event_id)

    ticket_type_id = request.POST.get('ticket_type_id')
    registration = Registration.objects.filter(
        event=event,
        user=request.user,
        status__in=[Registration.Status.CONFIRMADA, Registration.Status.PENDIENTE]
    ).select_related('ticket_type').first()

    if not registration:
        messages.error(request, 'No se encontró tu inscripción. No es posible cambiar el tipo de entrada.')
        return redirect('in_person_events:dashboard_assistant', event_id=event_id)

    ticket_type = event.ticket_types.filter(id=ticket_type_id).first()
    if not ticket_type:
        messages.error(request, 'Tipo de entrada inválido.')
        return redirect('in_person_events:dashboard_assistant', event_id=event_id)

    registration.ticket_type = ticket_type
    registration.save(update_fields=['ticket_type'])
    messages.success(request, 'Tu tipo de entrada se actualizó correctamente.')
    return redirect('in_person_events:dashboard_assistant', event_id=event_id)


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
            except Exception as e:
                messages.error(request, f'Error al guardar el evento: {str(e)}')
                return render(request, 'edit_event_form.html', {
                    'form': form,
                    'event': event,
                    'ticket_types': event.ticket_types.all(),
                    'tickets_json': request.POST.get('tickets_data', '[]'),
                })
            
            tickets_json = request.POST.get('tickets_data', '[]')
            try:
                tickets_list = json.loads(tickets_json) if tickets_json else []
                
                # Delete all old tickets
                event.ticket_types.all().delete()
                
                # Create new tickets
                for t_data in tickets_list:
                    TicketType.objects.create(
                        event=event,
                        name=t_data.get('name', 'Entrada General'),
                        price=t_data.get('price', 0)
                    )
                
                # Find default ticket (lowest price)
                default_ticket = event.ticket_types.order_by('price').first()
                
                # Reassign registrations with deleted ticket
                reassigned_count = 0
                if default_ticket:
                    current_ids = set(event.ticket_types.values_list('id', flat=True))
                    for reg in event.registrations.all():
                        if reg.ticket_type_id not in current_ids:
                            reg.ticket_type = default_ticket
                            reg.save(update_fields=['ticket_type'])
                            reassigned_count += 1
                
                return redirect('in_person_events:dashboard_organizer', event_id=event.id)
                
            except json.JSONDecodeError as e:
                messages.error(request, f'Error al procesar los tickets: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error al procesar los tickets: {str(e)}')
        
        # Si el formulario no es válido
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

    if request.method == 'POST':
        show_attendee_count = request.POST.get('show_attendee_count') == 'true'
        event.show_attendee_count = show_attendee_count
        event.save(update_fields=['show_attendee_count'])

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'show_attendee_count': event.show_attendee_count})

        messages.success(request, 'Configuración guardada correctamente.')
        return redirect('in_person_events:configure_event', event_id=event.id)

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


@login_required
def send_announcement(request, event_id):
    """Enviar un anuncio a todos los asistentes del evento."""
    from pe_communication.views import send_email_notification
    from pe_communication.models import Notification
    
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        
        if not title or not message:
            messages.error(request, 'El título y el mensaje son obligatorios.')
            return redirect('in_person_events:dashboard_organizer', event_id=event.id)
        
        registrations = event.registrations.filter(status=Registration.Status.CONFIRMADA).select_related('user')
        sent_count = 0
        
        for registration in registrations:
            if registration.user:
                Notification.objects.create(
                    user=registration.user,
                    sender=request.user,
                    title=f"{title} - {event.title}",
                    message=message,
                    notification_type=Notification.Type.MANUAL_ALERT
                )
                
                if registration.user.email:
                    try:
                        send_email_notification(
                            recipient_email=registration.user.email,
                            subject=f"{title} - {event.title}",
                            body_html=f"<p>{message}</p>",
                            body_text=message,
                        )
                    except Exception as e:
                        print(f"Error sending email to {registration.user.email}: {e}")
                
                sent_count += 1
        
        messages.success(request, f'Anuncio enviado a {sent_count} asistente(s).')
    
    return redirect('in_person_events:dashboard_organizer', event_id=event.id)
