from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Conversacion, Mensaje

def is_chat_available():
    now = timezone.localtime(timezone.now())
    if now.weekday() >= 5: return False
    start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end = now.replace(hour=18, minute=0, second=0, microsecond=0)
    return start <= now <= end

@login_required
def obtener_conversacion_usuario(request):
    """Obtiene la conversación del usuario autenticado (la crea si no existe)."""
    conversacion, created = Conversacion.objects.get_or_create(usuario=request.user)
    return JsonResponse({'conversacion_id': conversacion.id})

@login_required
def obtener_mensajes(request, conversacion_id):
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    if not request.user.is_staff and conversacion.usuario != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    last_id = request.GET.get('last_id', 0)
    mensajes = conversacion.mensajes.filter(id__gt=last_id).order_by('fecha')
    data = []
    for m in mensajes:
        data.append({
            'id': m.id,
            'texto': m.texto,
            'fecha': m.fecha.strftime("%H:%M"),
            'es_admin': m.remitente.is_staff,        # True si el remitente es staff
            'es_propio': m.remitente == request.user, # True si es el mismo usuario
        })
    return JsonResponse({'mensajes': data})

@login_required
def enviar_mensaje(request, conversacion_id):
    """Envía un mensaje del usuario a su conversación."""
    if request.method != 'POST' or not is_chat_available():
        return JsonResponse({'error': 'No disponible'}, status=400)
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    if not request.user.is_staff and conversacion.usuario != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    texto = request.POST.get('texto')
    if texto:
        Mensaje.objects.create(conversacion=conversacion, remitente=request.user, texto=texto)
        conversacion.ultimo_mensaje = timezone.now()
        conversacion.save(update_fields=['ultimo_mensaje'])
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Mensaje vacío'}, status=400)