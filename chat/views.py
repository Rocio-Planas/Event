from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Conversacion, Mensaje
from usuarios.decorators import role_required
import logging

logger = logging.getLogger(__name__)

def is_chat_available():
    now = timezone.localtime(timezone.now())
    if now.weekday() >= 5: return False
    start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end = now.replace(hour=18, minute=0, second=0, microsecond=0)
    return start <= now <= end


@login_required
def obtener_conversacion_usuario(request):
    """Obtiene o crea la conversación del usuario autenticado."""
    conversacion, created = Conversacion.objects.get_or_create(usuario=request.user)
    logger.info(f"Conversación {'creada' if created else 'obtenida'} para {request.user.email}")
    return JsonResponse({'conversacion_id': conversacion.id})

@login_required
def obtener_mensajes(request, conversacion_id):
    """Obtiene los mensajes de una conversación (solo el propietario o staff)."""
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
            'es_admin': m.remitente.is_staff,
            'es_propio': m.remitente == request.user,
            'username': m.remitente.get_full_name() or m.remitente.email,
        })
    return JsonResponse({'mensajes': data})

@csrf_exempt
@login_required
def enviar_mensaje(request, conversacion_id):
    """Envía un mensaje del usuario a su conversación."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    if not request.user.is_staff and conversacion.usuario != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    texto = request.POST.get('texto', '').strip()
    if not texto:
        return JsonResponse({'error': 'Mensaje vacío'}, status=400)

    mensaje = Mensaje.objects.create(
        conversacion=conversacion,
        remitente=request.user,
        texto=texto
    )
    conversacion.ultimo_mensaje = timezone.now()
    conversacion.save(update_fields=['ultimo_mensaje'])

    logger.info(f"Mensaje enviado por {request.user.email} en conversación {conversacion_id}")

    return JsonResponse({
        'status': 'ok',
        'mensaje': {
            'id': mensaje.id,
            'texto': mensaje.texto,
            'fecha': mensaje.fecha.strftime("%H:%M"),
            'es_admin': request.user.is_staff,
            'es_propio': True,
            'username': request.user.get_full_name() or request.user.email,
        }
    })

# Vistas del administrador
@login_required
@role_required(['administrador'])
def admin_chat_inbox(request):
    
    conversaciones = Conversacion.objects.prefetch_related('mensajes').order_by('-ultimo_mensaje')
    return render(request, 'chat/admin_inbox.html', {'conversaciones': conversaciones})
    
@login_required
@role_required(['administrador'])
def admin_chat_conversacion(request, conversacion_id):
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    
    # Marcar SOLO los mensajes de ESTA conversación como leídos
    Mensaje.objects.filter(conversacion=conversacion, leido_por_admin=False).update(leido_por_admin=True)
    
    if request.method == 'POST':
        texto = request.POST.get('mensaje', '').strip()
        if texto:
            Mensaje.objects.create(
                conversacion=conversacion,
                remitente=request.user,
                texto=texto
            )
            conversacion.ultimo_mensaje = timezone.now()
            conversacion.save(update_fields=['ultimo_mensaje'])
            messages.success(request, 'Mensaje enviado.')
        return redirect('chat:admin_conversacion', conversacion_id=conversacion.id)
    
    mensajes = conversacion.mensajes.select_related('remitente').order_by('fecha')
    return render(request, 'chat/admin_conversacion.html', {
        'conversacion': conversacion,
        'mensajes': mensajes
    })

@login_required
def contar_mensajes_no_leidos(request):
    """Cuenta los mensajes enviados por clientes que el administrador aún no ha leído."""
    if not hasattr(request.user, 'rol') or request.user.rol != 'administrador':
        return JsonResponse({'count': 0})
    try:
        count = Mensaje.objects.filter(
            leido_por_admin=False
        ).exclude(
            remitente__rol='administrador'
        ).count()
    except Exception:
        count = 0
    return JsonResponse({'count': count})

@login_required
def obtener_mensajes_chat(request):
    """Alternativa para obtener mensajes sin conocer el ID de conversación."""
    conversacion, _ = Conversacion.objects.get_or_create(usuario=request.user)
    last_id = request.GET.get('last_id', 0)
    mensajes = conversacion.mensajes.filter(id__gt=last_id).order_by('fecha')
    data = []
    for m in mensajes:
        data.append({
            'id': m.id,
            'message': m.texto,
            'username': m.remitente.get_full_name() or m.remitente.email,
            'timestamp': m.fecha.strftime("%H:%M"),
            'is_owner': m.remitente == request.user,
        })
    return JsonResponse({'messages': data})

@login_required
def enviar_mensaje_chat(request):
    """Alternativa para enviar mensajes sin conocer el ID de conversación."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    conversacion, _ = Conversacion.objects.get_or_create(usuario=request.user)
    texto = request.POST.get('message', '').strip()
    
    if texto:
        Mensaje.objects.create(
            conversacion=conversacion,
            remitente=request.user,
            texto=texto
        )
        conversacion.ultimo_mensaje = timezone.now()
        conversacion.save(update_fields=['ultimo_mensaje'])
    
    return JsonResponse({'status': 'ok'})