from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from in_person_events.models import Event
from in_person_events.forms import EventForm
from pe_registration.models import TicketType
from .models import Activity
from .forms import ActivityForm
import json


@login_required
def activities(request, event_id):
    """
    Vista para mostrar todas las actividades de un evento presencial.
    """
    # Obtener el evento y verificar que el usuario sea el organizador
    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    activities_list = Activity.objects.filter(event=event).order_by('start_time')
    
    # Filtrado (si se envía por GET)
    search_query = request.GET.get('search', '')
    zone_filter = request.GET.get('zone', 'all')
    day_filter = request.GET.get('day', 'all')
    speaker_filter = request.GET.get('speaker', 'all')
    
    if search_query:
        activities_list = activities_list.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if zone_filter != 'all':
        activities_list = activities_list.filter(location=zone_filter)
    
    if day_filter != 'all':
        # Filtrar por día (asumiendo que day_filter es un formato de fecha)
        activities_list = activities_list.filter(start_time__date=day_filter)
    
    if speaker_filter != 'all':
        activities_list = activities_list.filter(speaker_name=speaker_filter)
    
    context = {
        'event': event,
        'activities': activities_list,
        'active_page': 'actividades',
        'total_activities': activities_list.count(),
        'form': ActivityForm(),  # Agregar formulario para el modal
    }
    
    return render(request, 'activities.html', context)


@login_required
def create_activity(request, event_id):
    """
    Vista para crear una nueva actividad en un evento.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    if request.method == 'GET':
        # Si se accede directamente a la URL de creación, redirige a la lista de actividades
        # ya que el formulario de creación se maneja como un modal dentro de `activities`.
        return redirect('pe_agenda:activities', event_id=event.id)
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.event = event
            activity.save()
            messages.success(request, 'Actividad creada exitosamente')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Actividad creada exitosamente'})
            return redirect('pe_agenda:activities', event_id=event.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect(f"{reverse('pe_agenda:activities', args=[event.id])}?modal=create")
    else:
        form = ActivityForm()
    
    context = {
        'event': event,
        'form': form,
        'active_page': 'actividades'
    }
    
    return render(request, 'create_activity_form.html', context)


@login_required
def edit_activity(request, event_id, activity_id):
    """
    Vista para editar una actividad existente.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    activity = get_object_or_404(Activity, id=activity_id, event=event)
    
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Actividad actualizada exitosamente')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Actividad actualizada exitosamente'})
            return redirect('pe_agenda:activities', event_id=event.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ActivityForm(instance=activity)
    
    context = {
        'event': event,
        'activity': activity,
        'form': form,
        'active_page': 'actividades'
    }
    
    return render(request, 'create_activity_form.html', context)


@login_required
@require_http_methods(["GET"])
def get_activities_json(request, event_id):
    """
    API endpoint para obtener las actividades en formato JSON.
    Para cargar datos dinámicamente en el frontend.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    activities_list = Activity.objects.filter(event=event).values(
        'id',
        'title',
        'start_time',
        'end_time',
        'location',
        'speaker_name',
        'status',
    ).order_by('start_time')
    
    # Convertir a lista para JSON
    activities_data = list(activities_list)
    
    return JsonResponse({
        'success': True,
        'activities': activities_data,
        'count': len(activities_data)
    })


@login_required
@require_http_methods(["POST"])
def delete_activity(request, event_id, activity_id):
    """
    Elimina una actividad existente.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    activity = get_object_or_404(Activity, id=activity_id, event=event)
    
    activity_title = activity.title
    activity.delete()
    messages.success(request, 'Actividad eliminada correctamente.')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'Actividad "{activity_title}" eliminada correctamente.'})
    
    return redirect('pe_agenda:activities', event_id=event.id)


@login_required
def view_activity(request, event_id, activity_id):
    """
    Vista para ver los detalles de una actividad.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    activity = get_object_or_404(Activity, id=activity_id, event=event)
    
    context = {
        'event': event,
        'activity': activity,
        'active_page': 'actividades'
    }
    
    return render(request, 'activity_detail.html', context)


@login_required
def info_activity(request, event_id, activity_id):
    """
    Vista para mostrar la información completa de una actividad.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    activity = get_object_or_404(Activity, id=activity_id, event=event)

    context = {
        'event': event,
        'activity': activity,
        'active_page': 'actividades'
    }

    return render(request, 'info_activity.html', context)


@login_required
@require_http_methods(["GET"])
def get_activity_json(request, event_id, activity_id):
    """
    Obtiene los datos de una actividad específica en JSON.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    activity = get_object_or_404(Activity, id=activity_id, event=event)
    
    activity_data = {
        'id': activity.id,
        'title': activity.title,
        'description': activity.description,
        'start_time': activity.start_time.isoformat() if activity.start_time else None,
        'end_time': activity.end_time.isoformat() if activity.end_time else None,
        'location': activity.location,
        'speaker_name': activity.speaker_name,
        'speaker_email': activity.speaker_email,
        'status': activity.status,
    }
    
    return JsonResponse({
        'success': True,
        'activity': activity_data
    })
