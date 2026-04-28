import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import Item, StandAssignment
from in_person_events.models import Event


@method_decorator(login_required, name='dispatch')
class InventoryDashboardView(TemplateView):
    """
    Vista principal del dashboard de inventario.
    RF-06: Control de Recursos Básicos.
    
    Inyecta todos los datos necesarios para el frontend.
    """
    template_name = 'pe_inventory/inventory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        event_id = self.kwargs.get('event_id')
        
        # Obtener el evento
        event = get_object_or_404(Event, id=event_id)
        
        # Obtener todos los items con propiedades calculadas
        items = Item.objects.all()
        
        items_data = []
        for item in items:
            items_data.append({
                'id': item.id,
                'name': item.name,
                'sku': item.sku,
                'category': item.category,
                'total_stock': item.total_stock,
                'used_stock': item.used_stock,
                'available_stock': item.available_stock,
                'status': item.status,
                'image': item.image.url if item.image else None,
                'notes': item.notes,
            })
        
        # Calcular estadísticas globales
        total_in_stock = sum(1 for i in items_data if i['status'] == 'En Stock')
        total_low_stock = sum(1 for i in items_data if i['status'] == 'Stock Bajo')
        total_no_stock = sum(1 for i in items_data if i['status'] == 'Sin Stock')
        
        context['items_json'] = json.dumps(items_data)
        context['items'] = items
        context['total_items'] = len(items_data)
        context['total_in_stock'] = total_in_stock
        context['total_low_stock'] = total_low_stock
        context['total_no_stock'] = total_no_stock
        context['event'] = event
        context['event_id'] = event_id
        context['active_page'] = 'inventario'
        
        return context


@login_required
def create_item(request, event_id):
    """
    API para crear un nuevo recurso.
    POST /inventario/<event_id>/create/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Validar campos requeridos
        name = request.POST.get('name', '').strip()
        sku = request.POST.get('sku', '').strip()
        category = request.POST.get('category', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        if not name:
            return JsonResponse({'error': 'El nombre del artículo es requerido'}, status=400)
        if not sku:
            return JsonResponse({'error': 'El SKU es requerido'}, status=400)
        if not category:
            return JsonResponse({'error': 'La categoría es requerida'}, status=400)
        
        # Validar stock total
        try:
            total_stock = int(request.POST.get('total_stock', 0))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'El stock total debe ser un número válido'}, status=400)
        
        if total_stock < 1:
            return JsonResponse({'error': 'El stock total debe ser mayor a 0'}, status=400)
        
        item = Item(
            name=name,
            sku=sku,
            category=category,
            total_stock=total_stock,
            image=request.FILES.get('image') if request.FILES else None,
            notes=notes,
        )
        item.full_clean()
        item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Recurso creado correctamente',
            'item': {
                'id': item.id,
                'name': item.name,
                'sku': item.sku,
                'category': item.category,
                'total_stock': item.total_stock,
                'used_stock': item.used_stock,
                'available_stock': item.available_stock,
                'status': item.status,
                'image': item.image.url if item.image else None,
                'notes': item.notes,
            }
        })
    
    except ValidationError as e:
        return JsonResponse({'error': 'Error de validación: ' + str(e.message if hasattr(e, 'message') else e)}, status=400)
    except IntegrityError:
        return JsonResponse({'error': 'El SKU ya existe en el sistema'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Error al crear el recurso: {str(e)}'}, status=500)


@login_required
def update_item(request, event_id, item_id):
    """
    API para actualizar un recurso existente.
    POST /inventario/<event_id>/update/<item_id>/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    item = get_object_or_404(Item, id=item_id)
    
    try:
        if 'name' in request.POST:
            name = request.POST['name'].strip()
            if not name:
                return JsonResponse({'error': 'El nombre no puede estar vacío'}, status=400)
            item.name = name
        
        if 'sku' in request.POST:
            sku = request.POST['sku'].strip()
            if not sku:
                return JsonResponse({'error': 'El SKU no puede estar vacío'}, status=400)
            # Verificar que el nuevo SKU no esté en uso por otro item
            if Item.objects.exclude(id=item_id).filter(sku=sku).exists():
                return JsonResponse({'error': 'El SKU ya está en uso por otro recurso'}, status=400)
            item.sku = sku
        
        if 'category' in request.POST:
            category = request.POST['category'].strip()
            if not category:
                return JsonResponse({'error': 'La categoría no puede estar vacía'}, status=400)
            item.category = category
        
        if 'total_stock' in request.POST:
            try:
                total_stock = int(request.POST['total_stock'])
            except (ValueError, TypeError):
                return JsonResponse({'error': 'El stock total debe ser un número válido'}, status=400)
            if total_stock < 1:
                return JsonResponse({'error': 'El stock total debe ser mayor a 0'}, status=400)
            item.total_stock = total_stock
        
        if 'notes' in request.POST:
            item.notes = request.POST['notes'].strip()
        
        if 'image' in request.FILES:
            item.image = request.FILES['image']
        
        item.full_clean()
        item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Recurso actualizado correctamente',
            'item': {
                'id': item.id,
                'name': item.name,
                'sku': item.sku,
                'category': item.category,
                'total_stock': item.total_stock,
                'used_stock': item.used_stock,
                'available_stock': item.available_stock,
                'status': item.status,
                'image': item.image.url if item.image else None,
                'notes': item.notes,
            }
        })
    
    except ValidationError as e:
        return JsonResponse({'error': 'Error de validación: ' + str(e.message if hasattr(e, 'message') else e)}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Error al actualizar el recurso: {str(e)}'}, status=500)


@login_required
def delete_item(request, event_id, item_id):
    """
    API para eliminar un recurso.
    POST /inventario/<event_id>/delete/<item_id>/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    item = get_object_or_404(Item, id=item_id)
    
    try:
        item_name = item.name
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Recurso "{item_name}" eliminado correctamente'
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Error al eliminar el recurso: {str(e)}'}, status=500)


@login_required
def get_items(request, event_id):
    """
    API para obtener todos los recursos.
    GET /inventario/<event_id>/items/
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        items = Item.objects.all().order_by('name')
        items_data = []
        
        for item in items:
            items_data.append({
                'id': item.id,
                'name': item.name,
                'sku': item.sku,
                'category': item.category,
                'total_stock': item.total_stock,
                'used_stock': item.used_stock,
                'available_stock': item.available_stock,
                'status': item.status,
                'image': item.image.url if item.image else None,
                'notes': item.notes,
            })
        
        return JsonResponse({
            'success': True,
            'items': items_data
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Error al obtener los recursos: {str(e)}'}, status=500)