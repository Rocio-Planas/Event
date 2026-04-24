import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.text import slugify

# Importamos tus modelos y el formulario
from .models import Event
from pe_registration.models import TicketType
from .forms import EventForm

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
                event.visibility = request.POST.get('visibility', 'publico')
                event.save()
                
                tickets_json = form.cleaned_data.get('tickets_data', '[]')
                tickets_list = json.loads(tickets_json)

                for t_data in tickets_list:
                    TicketType.objects.create(
                        event=event,
                        name=t_data.get('name', 'Entrada General'),
                        price=t_data.get('price', 0)
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
    return render(request, 'dashboard_organizer.html', {
        'event': event,
        'ticket_types': ticket_types,
        'active_page': 'resumen'
    })


@login_required
def edit_event(request, event_id):
    """Vista para editar un evento existente."""
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event, user=request.user)
        
        if form.is_valid():
            try:
                event = form.save(commit=False)
                event.visibility = request.POST.get('visibility', event.visibility)
                event.save()
                
                # Si hay nuevos tickets en los datos
                tickets_json = form.cleaned_data.get('tickets_data', '[]')
                if tickets_json and tickets_json != '[]':
                    tickets_list = json.loads(tickets_json)
                    # Limpiar tickets antiguos y crear nuevos
                    event.ticket_types.all().delete()
                    for t_data in tickets_list:
                        TicketType.objects.create(
                            event=event,
                            name=t_data.get('name', 'Entrada General'),
                            price=t_data.get('price', 0)
                        )
                
                messages.success(request, 'Evento actualizado correctamente.')
                return redirect('in_person_events:dashboard_organizer', event_id=event.id)
            
            except json.JSONDecodeError:
                messages.error(request, 'Error al procesar los tickets.')
            except Exception as e:
                messages.error(request, f'Error al actualizar el evento: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = EventForm(instance=event, user=request.user)
    
    ticket_types = event.ticket_types.all()
    return render(request, 'edit_event_form.html', {
        'form': form,
        'event': event,
        'ticket_types': ticket_types
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
