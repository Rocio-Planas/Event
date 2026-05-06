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
from pe_stand.models import Stand
from .models import Activity
from .forms import ActivityForm
import json


def _refresh_activity_status(activity):
    if activity.status != Activity.Status.CANCELADA:
        activity.status = activity.get_current_status()
    return activity


def is_unassigned_location(location):
    return not location or str(location).strip().lower() in ['no asignada', 'sin asignar', 'sin asignada', 'unassigned']


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

    for activity in activities_list:
        _refresh_activity_status(activity)

    event_zones = Stand.objects.filter(event=event).exclude(name='').values_list('name', flat=True).distinct().order_by('name')

    context = {
        'event': event,
        'activities': activities_list,
        'active_page': 'actividades',
        'total_activities': activities_list.count(),
        'form': ActivityForm(),
        'confirmed_ponentes': event.staff_members.filter(user_type='ponente'),
        'ponente_profiles': {m.user.id: m.user for m in event.staff_members.filter(user_type='ponente')},
        'event_zones': event_zones,
    }
    
    return render(request, 'activities.html', context)


@login_required
def create_activity(request, event_id):
    """
    Vista para crear una nueva actividad en un evento.
    """
    from datetime import datetime

    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    if request.method == 'GET':
        return redirect('pe_agenda:activities', event_id=event.id)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        location = request.POST.get('location', '').strip()
        speaker_name = request.POST.get('speaker_name', '').strip()
        speaker_email = request.POST.get('speaker_email', '').strip()
        
        start_time_str = request.POST.get('start_time', '')
        end_time_str = request.POST.get('end_time', '')
        
        if not title:
            messages.error(request, 'El título es obligatorio')
            return redirect('pe_agenda:activities', event_id=event.id)
        
        if not start_time_str or not end_time_str:
            messages.error(request, 'Las horas de inicio y fin son obligatorias')
            return redirect('pe_agenda:activities', event_id=event.id)
        
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('T', ' '))
            end_time = datetime.fromisoformat(end_time_str.replace('T', ' '))
        except ValueError as e:
            messages.error(request, f'Formato de fecha inválido: {str(e)}')
            return redirect('pe_agenda:activities', event_id=event.id)
        
        activity = Activity.objects.create(
            event=event,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            speaker_name=speaker_name,
            speaker_email=speaker_email,
            status='programada'
        )
        
        messages.success(request, 'Actividad creada exitosamente')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Actividad creada exitosamente'})
        return redirect('pe_agenda:activities', event_id=event.id)


@login_required
def edit_activity(request, event_id, activity_id):
    from datetime import datetime

    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    activity = get_object_or_404(Activity, id=activity_id, event=event)
    
    if request.method == 'POST':
        activity.title = request.POST.get('title', '').strip()
        activity.description = request.POST.get('description', '').strip()
        activity.location = request.POST.get('location', '').strip()
        activity.speaker_name = request.POST.get('speaker_name', '').strip()
        activity.speaker_email = request.POST.get('speaker_email', '').strip()
        
        start_time_str = request.POST.get('start_time', '')
        end_time_str = request.POST.get('end_time', '')
        
        if start_time_str:
            activity.start_time = datetime.fromisoformat(start_time_str.replace('T', ' '))
        if end_time_str:
            activity.end_time = datetime.fromisoformat(end_time_str.replace('T', ' '))
        
        activity.save()

        if is_unassigned_location(activity.location):
            from pe_stand.models import StandActivity
            StandActivity.objects.filter(activity_id=activity.id).delete()

        messages.success(request, 'Actividad actualizada exitosamente')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Actividad actualizada exitosamente'})
        return redirect('pe_agenda:activities', event_id=event.id)


@login_required
@require_http_methods(["GET"])
def get_activities_json(request, event_id):
    """
    API endpoint para obtener las actividades en formato JSON.
    Para cargar datos dinámicamente en el frontend.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    activities_qs = Activity.objects.filter(event=event).order_by('start_time')
    activities_data = []
    for activity in activities_qs:
        _refresh_activity_status(activity)
        activities_data.append({
            'id': activity.id,
            'title': activity.title,
            'start_time': activity.start_time.isoformat() if activity.start_time else None,
            'end_time': activity.end_time.isoformat() if activity.end_time else None,
            'location': activity.location,
            'speaker_name': activity.speaker_name,
            'status': activity.status,
        })
    
    return JsonResponse({
        'success': True,
        'activities': activities_data,
        'count': len(activities_data)
    })


@login_required
@require_http_methods(["POST"])
def cancel_activity(request, event_id, activity_id):
    """
    Cancela una actividad existente.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    activity = get_object_or_404(Activity, id=activity_id, event=event)
    
    activity.status = 'cancelada'
    activity.save()
    messages.success(request, 'Actividad cancelada correctamente.')
    
    return redirect('pe_agenda:activities', event_id=event.id)


@login_required
@require_http_methods(["POST"])
def delete_activity(request, event_id, activity_id):
    """
    Elimina una actividad existente. Solo se puede eliminar si está cancelada.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    activity = get_object_or_404(Activity, id=activity_id, event=event)
    
    if activity.status != 'cancelada':
        messages.error(request, 'Solo puedes eliminar actividades canceladas.')
        return redirect('pe_agenda:activities', event_id=event.id)
    
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
    _refresh_activity_status(activity)
    
    context = {
        'event': event,
        'activity': activity,
        'active_page': 'actividades'
    }
    
    return render(request, 'activity_detail.html', context)


@login_required
def info_activity(request, event_id, activity_id):
    """
    Vista para mostrar información detallada de una actividad para asistentes.
    """
    event = get_object_or_404(Event, id=event_id)
    
    # TEMPORALMENTE DESACTIVADO PARA TESTING
    # Verificar que el usuario esté inscrito al evento
    # if not request.user.suscripciones.filter(evento_id=event_id, tipo_evento='presencial').exists():
    #     messages.error(request, 'No estás inscrito a este evento.')
    #     return redirect('usuarios:dashboard')
    
    activity = get_object_or_404(Activity, id=activity_id, event=event)
    _refresh_activity_status(activity)

    speaker_user = None
    if activity.speaker_email:
        speaker_member = event.staff_members.filter(user__email=activity.speaker_email).select_related('user').first()
        if speaker_member:
            speaker_user = speaker_member.user

    context = {
        'event': event,
        'activity': activity,
        'speaker_user': speaker_user,
    }

    return render(request, 'info_activity.html', context)


@login_required
def chronogram_assistant(request, event_id):
    """
    Vista para mostrar el cronograma completo del evento para asistentes.
    """
    event = get_object_or_404(Event, id=event_id)
    
    # TEMPORALMENTE DESACTIVADO PARA TESTING
    # Verificar que el usuario esté inscrito al evento
    # if not request.user.suscripciones.filter(evento_id=event_id, tipo_evento='presencial').exists():
    #     messages.error(request, 'No estás inscrito a este evento.')
    #     return redirect('usuarios:dashboard')
    
    activities = Activity.objects.filter(event=event).order_by('start_time')
    for activity in activities:
        _refresh_activity_status(activity)
    
    # Obtener categorías únicas para los filtros
    categories = list({activity.status for activity in activities})
    
    # Marcar actividades en las que el usuario está inscrito (si hay sistema de inscripción)
    # Por ahora, asumimos que no hay sistema de inscripción individual a actividades
    for activity in activities:
        activity.user_inscribed = False  # Placeholder
    
    context = {
        'event': event,
        'activities': activities,
        'categories': categories,
    }
    
    return render(request, 'chronogram_assistant.html', context)


@login_required
@require_http_methods(["GET"])
def get_activity_json(request, event_id, activity_id):
    """
    Obtiene los datos de una actividad específica en JSON.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    activity = get_object_or_404(Activity, id=activity_id, event=event)
    _refresh_activity_status(activity)
    
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
