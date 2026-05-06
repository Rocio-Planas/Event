import json
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import models
from django.apps import apps
from django.middleware.csrf import get_token

from .models import Stand, StandStaff, StandActivity
from in_person_events.models import Event
from pe_staff.models import StaffMember
from django.contrib.auth import get_user_model

User = get_user_model()


def is_unassigned_zone(location):
    return not location or str(location).strip().lower() in ['no asignada', 'sin asignar', 'sin asignada', 'unassigned']


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
        
        # Zonas activas = zonas con al menos una actividad asignada
        active_zones = StandActivity.objects.filter(
            stand__event_id=event_id
        ).values('stand_id').distinct().count()
        
        # Integración con pe_inventory para obtener recursos asignados
        total_alerts = 0
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
                
                # Alerta: si hay recursos asignados y al menos uno está en estado crítico
                if total_assigned > 0 and has_critical:
                    total_alerts += 1
                
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
        context['active_zones'] = active_zones
        context['total_alerts'] = total_alerts
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
        
        # Obtener personal del stand (con user del modelo User)
        staff = StandStaff.objects.filter(stand=stand).select_related('user')
        
        # Obtener IDs de staff ya asignados a este stand
        assigned_user_ids = set(staff.values_list('user_id', flat=True))
        
        # Obtener todo el staff del evento (para añadir al stand)
        all_event_staff = StaffMember.objects.filter(
            event=event,
            user_type='staff'  # Solo staff, no ponentes
        ).select_related('user').order_by('-role')  # Líderes primero por role
        
        # Organizar: líderes primero, luego otros
        leaders = []
        others = []
        for member in all_event_staff:
            if member.role == 'LIDER_ZONA':
                leaders.append(member)
            else:
                others.append(member)
        
        # Combinar para tener líderes al inicio
        available_staff = leaders + others
        
        # Obtener IDs de staff ya asignados a este stand (ahora es una lista de objetos StandStaff con .user)
        assigned_user_ids = set(s.user.id for s in staff if s.user)
        
        # Filtrar solo usuarios no asignados Y con usuario válido
        not_assigned_staff = [s for s in available_staff if s.user and s.user.id not in assigned_user_ids]
        
        # Obtener actividades del stand con sus detalles completos
        from pe_agenda.models import Activity
        stand_activities_rel = StandActivity.objects.filter(stand=stand).values_list('activity_id', flat=True)
        assigned_activity_ids = set(stand_activities_rel)
        
        # Obtener los objetos Activity reales para las actividades asignadas
        activities = Activity.objects.filter(
            event=event,
            id__in=assigned_activity_ids
        ).order_by('start_time')
        
        # Obtener actividades del evento que aún no tienen zona asignada
        event_activities = Activity.objects.filter(event=event).filter(
            models.Q(location='') |
            models.Q(location__isnull=True) |
            models.Q(location__iexact='No asignada') |
            models.Q(location__iexact='Sin asignar')
        ).order_by('start_time')
        available_activities = list(event_activities)

        # Obtener otros stands del evento para mover actividades entre stands
        event_stands = Stand.objects.filter(event=event).exclude(id=stand.id).order_by('name')
        
        # Integración profunda con pe_inventory
        try:
            StandAssignment = apps.get_model('pe_inventory', 'StandAssignment')
            Item = apps.get_model('pe_inventory', 'Item')
            
            # Obtener todos los recursos asignados a este stand
            assignments = StandAssignment.objects.filter(
                stand=stand
            ).select_related('item')
            
# Cargar catálogo de recursos disponible para el evento
            items = Item.objects.all().order_by('name')
            assignment_map = {assignment.item_id: assignment for assignment in assignments}

            resources_data = []
            assigned_lookup = {}
            for item in items:
                assigned = assignment_map.get(item.id)
                qty = assigned.quantity if assigned else 0
                assigned_lookup[item.id] = qty
                resources_data.append({
                    'item_id': item.id,
                    'name': item.name,
                    'image_url': item.image.url if item.image else None,
                    'category': item.category,
                    'status': item.status,
                    'available_stock': item.available_stock,
                    'total_stock': item.total_stock,
                    'assigned_quantity': qty,
                    'is_assigned': bool(assigned),
                })
            
            available_resources = [r for r in resources_data if not r['is_assigned']]
            
            context['resources_json'] = json.dumps(resources_data)
            context['assignments'] = assignments
            context['available_resources'] = available_resources
            context['assigned_lookup'] = assigned_lookup
            
        except ImportError:
            context['resources_json'] = json.dumps([])
            context['assignments'] = []
            context['available_resources'] = []
            context['assigned_lookup'] = {}
        
        context['stand'] = stand
        context['event'] = event
        context['event_id'] = event_id
        context['staff'] = staff
        context['activities'] = activities
        context['available_activities'] = available_activities
        context['available_staff'] = not_assigned_staff
        context['event_stands'] = event_stands
        context['active_page'] = 'stands'
        context['csrf_token'] = get_token(self.request)
        
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
    POST /stands/<stand_id>/update-resource/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        StandAssignment = apps.get_model('pe_inventory', 'StandAssignment')
        
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        quantity = data.get('quantity')
        required_quantity = data.get('required_quantity')
        details = data.get('details')
        
        if not assignment_id:
            return JsonResponse({'error': 'ID de asignación requerido'}, status=400)
        
        assignment = get_object_or_404(StandAssignment, id=assignment_id, stand_id=stand_id)
        
        if quantity is not None:
            assignment.quantity = quantity
        if required_quantity is not None:
            assignment.required_quantity = required_quantity
        if details is not None:
            assignment.details = details[:100]  # Max 100 chars
        
        assignment.full_clean()
        assignment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Recurso actualizado correctamente',
            'assignment': {
                'id': assignment.id,
                'quantity': assignment.quantity,
                'required_quantity': assignment.required_quantity,
                'details': assignment.details,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def add_resources(request, stand_id):
    """
    API para asignar uno o varios recursos a un stand.
    POST /api/stands/<stand_id>/add-resources/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        StandAssignment = apps.get_model('pe_inventory', 'StandAssignment')
        Item = apps.get_model('pe_inventory', 'Item')

        data = json.loads(request.body)
        item_ids = data.get('item_ids', [])

        if not item_ids:
            return JsonResponse({'error': 'Selecciona al menos un recurso'}, status=400)

        stand = get_object_or_404(Stand, id=stand_id)
        added_items = []

        for item_id in item_ids:
            item = get_object_or_404(Item, id=item_id)
            
            assignment, created = StandAssignment.objects.get_or_create(
                stand=stand,
                item=item,
                defaults={'quantity': 0, 'required_quantity': 0}
            )

            added_items.append(item.name)

        if not added_items:
            return JsonResponse({'success': False, 'error': 'No se pudieron asignar recursos'}, status=400)

        return JsonResponse({
            'success': True,
            'message': 'Recursos agregados correctamente',
            'added_items': added_items,
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


@login_required
def add_staff_to_stand(request, stand_id):
    """
    API para añadir personal del evento a un stand.
    POST /api/stands/<stand_id>/add-staff/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    # Mapeo de roles de pe_staff a nombres legibles
    role_mapping = {
        'LIDER_ZONA': 'Líder de Zona',
        'SOPORTE': 'Soporte Técnico',
        'RECEPCION': 'Recepción',
        'SEGURIDAD': 'Seguridad',
        'MONTAJE': 'Montaje',
        'CATERING': 'Catering',
        'ATENCION': 'Atención al Público',
        'ponente': 'Ponente',
        'staff': 'Staff',
    }
    
    try:
        data = json.loads(request.body)
        users = data.get('users', [])
        
        if not users:
            return JsonResponse({'error': 'Usuarios requeridos'}, status=400)
        
        stand = get_object_or_404(Stand, id=stand_id)
        
        added = []
        errors = []
        
        for user_data in users:
            user_id = int(user_data.get('user_id'))
            pe_role = user_data.get('role', 'Otro')
            
            # Mapear rol de pe_staff a StandStaff
            stand_role = role_mapping.get(pe_role, 'Otro')
            
            # Obtener el objeto User
            user = get_object_or_404(User, id=user_id)
            
            # Verificar que no esté ya asignado
            if StandStaff.objects.filter(stand=stand, user=user).exists():
                errors.append(f'Usuario {user_id} ya está asignado')
                continue
            
            # Crear la asignación en StandStaff
            staff_member = StandStaff(
                stand=stand,
                user=user,
                role=stand_role
            )
            try:
                staff_member.full_clean()
                staff_member.save()
                added.append(user_id)
                
                # También actualizar el campo zone en StaffMember si existe
                from pe_staff.models import StaffMember
                staff_member_obj = StaffMember.objects.filter(
                    event_id=stand.event_id,
                    user_id=user_id
                ).first()
                if staff_member_obj:
                    staff_member_obj.zone = stand.name
                    staff_member_obj.save(update_fields=['zone'])
                    
            except Exception as e:
                errors.append(f'Error saving: {str(e)}')
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'{len(added)} personal añadido correctamente',
            'added': added,
            'errors': errors
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()}, status=500)


@login_required
def remove_staff_from_stand(request, stand_id):
    """
    API para quitar personal de un stand.
    DELETE /stands/api/<stand_id>/remove-staff/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({'error': 'user_id requerido'}, status=400)
        
        stand = get_object_or_404(Stand, id=stand_id)
        
        staff_member = StandStaff.objects.filter(stand=stand, user_id=user_id).first()
        if not staff_member:
            return JsonResponse({'error': 'Personal no encontrado en este stand'}, status=404)
        
        staff_member.delete()
        
        try:
            from pe_staff.models import StaffMember
            staff_member_obj = StaffMember.objects.filter(
                event_id=stand.event_id,
                user_id=user_id
            ).first()
            if staff_member_obj:
                staff_member_obj.zone = None
                staff_member_obj.save(update_fields=['zone'])
        except:
            pass
        
        return JsonResponse({
            'success': True,
            'message': 'Personal removido correctamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def move_activity_in_stand(request, stand_id):
    """
    API para mover una actividad asignada de un stand a otro.
    POST /stands/api/<stand_id>/move-activity/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        activity_id = data.get('activity_id')
        target_stand_id = data.get('target_stand_id')

        if not activity_id or not target_stand_id:
            return JsonResponse({'error': 'activity_id y target_stand_id son requeridos'}, status=400)

        stand = get_object_or_404(Stand, id=stand_id)
        target_stand = get_object_or_404(Stand, id=target_stand_id, event=stand.event)

        if target_stand.id == stand.id:
            return JsonResponse({'error': 'El stand destino debe ser diferente'}, status=400)

        stand_activity = get_object_or_404(StandActivity, stand=stand, activity_id=activity_id)
        stand_activity.stand = target_stand
        stand_activity.save()

        from pe_agenda.models import Activity
        try:
            activity = Activity.objects.get(id=activity_id)
            activity.location = target_stand.location
            activity.save(update_fields=['location'])
        except Activity.DoesNotExist:
            pass

        return JsonResponse({'success': True, 'message': 'Actividad movida correctamente'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()}, status=500)


@login_required
def remove_activity_from_stand(request, stand_id):
    """
    API para eliminar una actividad de un stand y borrar su ubicación.
    POST /stands/api/<stand_id>/remove-activity/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        activity_id = data.get('activity_id')

        if not activity_id:
            return JsonResponse({'error': 'activity_id es requerido'}, status=400)

        stand = get_object_or_404(Stand, id=stand_id)
        stand_activity = get_object_or_404(StandActivity, stand=stand, activity_id=activity_id)

        from pe_agenda.models import Activity
        try:
            activity = Activity.objects.get(id=activity_id)
            activity.location = ''
            activity.save(update_fields=['location'])
        except Activity.DoesNotExist:
            pass

        stand_activity.delete()

        return JsonResponse({'success': True, 'message': 'Actividad eliminada del stand y zona borrada'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()}, status=500)

@login_required
def add_activities_to_stand(request, stand_id):
    """
    API para añadir actividades del evento a un stand.
    POST /api/stands/<stand_id>/add-activities/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        activities = data.get('activities', [])
        
        if not activities:
            return JsonResponse({'error': 'Actividades requeridas'}, status=400)
        
        stand = get_object_or_404(Stand, id=stand_id)
        
        added = []
        errors = []
        
        for activity_data in activities:
            activity_id = int(activity_data.get('activity_id'))
            
            # Verificar que no esté ya asignada
            if StandActivity.objects.filter(stand=stand, activity_id=activity_id).exists():
                errors.append(f'Actividad {activity_id} ya está asignada')
                continue
            
            # Obtener la actividad del evento
            from pe_agenda.models import Activity
            try:
                activity = Activity.objects.get(id=activity_id)
            except Activity.DoesNotExist:
                errors.append(f'Actividad {activity_id} no existe')
                continue

            if activity.location and not is_unassigned_zone(activity.location):
                errors.append(f'Actividad {activity_id} ya tiene zona asignada')
                continue

            if StandActivity.objects.filter(activity_id=activity_id).exists():
                errors.append(f'Actividad {activity_id} ya está asignada a otro stand')
                continue
            
            # Crear la asignación y actualizar zona
            stand_activity = StandActivity(
                stand=stand,
                activity_id=activity_id,
                scheduled_time=activity.start_time
            )
            try:
                stand_activity.full_clean()
                stand_activity.save()
                activity.location = stand.location
                activity.save(update_fields=['location'])
                added.append(activity_id)
            except Exception as e:
                errors.append(f'Error saving: {str(e)}')
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'{len(added)} actividad(es) añadida(s) correctamente',
            'added': added,
            'errors': errors
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()}, status=500)