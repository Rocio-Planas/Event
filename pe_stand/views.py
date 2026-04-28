import json
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import models
from django.apps import apps

from .models import Stand, StandStaff, StandActivity
from in_person_events.models import Event


@method_decorator(login_required, name='dispatch')
class StandDashboardView(TemplateView):
    """
    Vista principal del dashboard de stands.
    Lista todos los stands y calcula estadísticas.
    """
    template_name = 'pe_stand/stands.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        event_id = self.kwargs.get('event_id')
        
        # Obtener el evento
        event = get_object_or_404(Event, id=event_id)
        
        # Obtener todos los stands
        stands = Stand.objects.filter(event_id=event_id).prefetch_related('staff', 'activities')
        
        # Calcular estadísticas globales
        total_stands = stands.count()
        total_capacity = sum(stand.capacity for stand in stands)
        
        # Integración con pe_inventory para obtener recursos asignados
        try:
            StandAssignment = apps.get_model('pe_inventory', 'StandAssignment')
            Item = apps.get_model('pe_inventory', 'Item')
            
            # Obtener asignaciones por stand
            assignments_by_stand = {}
            for assignment in StandAssignment.objects.select_related('item').all():
                stand_id = assignment.stand_id
                if stand_id not in assignments_by_stand:
                    assignments_by_stand[stand_id] = []
                assignments_by_stand[stand_id].append(assignment)
            
            # Preparar datos de stands con recursos
            stands_data = []
            for stand in stands:
                stand_assignments = assignments_by_stand.get(stand.id, [])
                
                # Calcular recursos asignados y detectar estado crítico
                total_assigned = sum(a.quantity for a in stand_assignments)
                has_critical = any(
                    a.item.status in ['Sin Stock', 'Stock Bajo'] 
                    for a in stand_assignments 
                    if hasattr(a.item, 'status')
                )
                
                stands_data.append({
                    'id': stand.id,
                    'name': stand.name,
                    'location': stand.location,
                    'capacity': stand.capacity,
                    'total_assigned': total_assigned,
                    'has_critical': has_critical,
                    'resource_count': len(stand_assignments),
                })
            
            context['stands_json'] = json.dumps(stands_data)
            
        except ImportError:
            # Si pe_inventory no está disponible
            context['stands_json'] = json.dumps([])
        
        context['stands'] = stands
        context['total_stands'] = total_stands
        context['total_capacity'] = total_capacity
        context['event'] = event
        context['event_id'] = event_id
        context['active_page'] = 'zona'
        
        return context


@method_decorator(login_required, name='dispatch')
class StandDetailView(TemplateView):
    """
    Vista de detalle de un stand específico.
    Muestra el stand, su personal y sus actividades.
    """
    template_name = 'pe_stand/info_stands.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        event_id = self.kwargs.get('event_id')
        stand_id = self.kwargs.get('pk')
        
        # Obtener el evento
        event = get_object_or_404(Event, id=event_id)
        stand = get_object_or_404(Stand, id=stand_id, event=event)
        
        # Obtener personal del stand
        staff = StandStaff.objects.filter(stand=stand)
        
        # Obtener actividades del stand
        activities = StandActivity.objects.filter(stand=stand).order_by('scheduled_time')
        
        # Integración profunda con pe_inventory
        try:
            StandAssignment = apps.get_model('pe_inventory', 'StandAssignment')
            Item = apps.get_model('pe_inventory', 'Item')
            
            # Obtener todos los recursos asignados a este stand
            assignments = StandAssignment.objects.filter(
                stand=stand
            ).select_related('item')
            
            # Preparar datos para el frontend
            # assigned_val: cantidad asignada
            # required_val: cantidad requerida (simulada por ahora)
            # target_label: destino dentro del stand
            resources_data = []
            for assignment in assignments:
                item = assignment.item
                resources_data.append({
                    'id': assignment.id,
                    'item_id': item.id,
                    'item_name': item.name,
                    'assigned_val': assignment.quantity,
                    'required_val': item.total_stock,  # stock total como requerido
                    'target_label': f"{item.category} - {item.sku}",
                    'status': item.status,
                })
            
            context['resources_json'] = json.dumps(resources_data)
            context['assignments'] = assignments
            
        except ImportError:
            context['resources_json'] = json.dumps([])
            context['assignments'] = []
        
        context['stand'] = stand
        context['event'] = event
        context['event_id'] = event_id
        context['staff'] = staff
        context['activities'] = activities
        context['active_page'] = 'stands'
        
        return context


@login_required
def create_stand(request, event_id):
    """
    API para crear un nuevo stand.
    POST /stands/api/<event_id>/create-stand/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name')
        location = data.get('location')
        capacity = data.get('capacity')
        
        if not all([name, location, capacity]):
            return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)
        
        # Obtener el evento
        event = get_object_or_404(Event, id=event_id)
        
        # Crear el stand
        stand = Stand(
            event=event,
            name=name,
            location=location,
            capacity=int(capacity)
        )
        stand.full_clean()
        stand.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Stand creado correctamente',
            'stand': {
                'id': stand.id,
                'name': stand.name,
                'location': stand.location,
                'capacity': stand.capacity,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@login_required
def update_resource(request, stand_id):
    """
    API para actualizar un recurso asignado.
    POST /api/stands/<stand_id>/update-resource/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        StandAssignment = apps.get_model('pe_inventory', 'StandAssignment')
        
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        quantity = data.get('quantity')
        
        if not assignment_id:
            return JsonResponse({'error': 'ID de asignación requerido'}, status=400)
        
        assignment = get_object_or_404(StandAssignment, id=assignment_id, stand_id=stand_id)
        
        if quantity is not None:
            assignment.quantity = quantity
            assignment.full_clean()
            assignment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Recurso actualizado correctamente',
            'assignment': {
                'id': assignment.id,
                'quantity': assignment.quantity,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delete_resource(request, stand_id):
    """
    API para eliminar un recurso asignado.
    POST /api/stands/<stand_id>/delete-resource/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        StandAssignment = apps.get_model('pe_inventory', 'StandAssignment')
        
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        
        if not assignment_id:
            return JsonResponse({'error': 'ID de asignación requerido'}, status=400)
        
        assignment = get_object_or_404(StandAssignment, id=assignment_id, stand_id=stand_id)
        assignment.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Recurso eliminado correctamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)