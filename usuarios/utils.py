# usuarios/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

def enviar_email_confirmacion(request, user, token):
    """Envía email de confirmación de cuenta al registrarse"""
    current_site = get_current_site(request)
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'
    
    # URL de confirmación
    confirm_url = reverse('usuarios:confirmar_email', args=[token])
    full_url = f"{protocol}://{domain}{confirm_url}"
    
    # Contexto para el template
    context = {
        'user': user,
        'nombre': user.get_full_name() or user.email,
        'confirm_url': full_url,
        'domain': domain,
        'site_name': 'EventPulse',
        'expiry_hours': 24,
    }
    
    # Renderizar HTML y texto plano
    html_content = render_to_string('usuarios/email/confirmacion_registro.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject='Confirma tu cuenta en EventPulse',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        logger.info(f"Email de confirmación enviado a {user.email}")
        return True
    except Exception as e:
        logger.error(f"Error enviando email de confirmación a {user.email}: {str(e)}")
        return False


def enviar_email_recuperacion(request, user, token):
    """Envía email de recuperación de contraseña"""
    current_site = get_current_site(request)
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'
    
    reset_url = reverse('usuarios:reset_password', args=[token])
    full_url = f"{protocol}://{domain}{reset_url}"
    
    context = {
        'user': user,
        'nombre': user.get_full_name() or user.email,
        'reset_url': full_url,
        'domain': domain,
        'site_name': 'EventPulse',
        'expiry_hours': 24,
    }
    
    html_content = render_to_string('usuarios/email/recuperacion_password.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject='Recupera tu contraseña en EventPulse',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        logger.info(f"Email de recuperación enviado a {user.email}")
        return True
    except Exception as e:
        logger.error(f"Error enviando email de recuperación a {user.email}: {str(e)}")
        return False


def enviar_notificacion_cambio_password(user, ip_address=None, user_agent=None):
    """Envía notificación de que la contraseña fue cambiada"""
    context = {
        'user': user,
        'nombre': user.get_full_name() or user.email,
        'site_name': 'EventPulse',
        'ip_address': ip_address,
        'user_agent': user_agent,
        'fecha': user.last_login,
    }
    
    html_content = render_to_string('usuarios/email/cambio_password_notificacion.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject='Tu contraseña ha sido cambiada - EventPulse',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando notificación de cambio de password a {user.email}: {str(e)}")
        return False
    
   

def enviar_email_aprobacion_evento(user, evento, tipo_evento):
    """Envía email cuando un evento es aprobado"""
    from django.urls import reverse
    
    # Construir URL según tipo de evento
    if tipo_evento == 'virtual':
        evento_url = reverse('virtualEvent:event_detail', args=[evento.id])
    else:
        evento_url = f"/eventos-presenciales/{evento.id}/"
    
    protocol = 'https' if settings.DEBUG is False else 'http'
    domain = 'event-jxok.onrender.com' if not settings.DEBUG else '127.0.0.1:8000'
    full_url = f"{protocol}://{domain}{evento_url}"
    
    context = {
        'user': user,
        'nombre': user.get_full_name() or user.email,
        'evento_titulo': evento.title,
        'evento_fecha': evento.start_datetime if hasattr(evento, 'start_datetime') else evento.start_date,
        'evento_tipo': 'virtual' if tipo_evento == 'virtual' else 'presencial',
        'evento_url': full_url,
        'site_name': 'EventPulse',
    }
    
    html_content = render_to_string('usuarios/email/evento_aprobado.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject=f'✅ Tu evento "{evento.title}" ha sido aprobado',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando email de aprobación a {user.email}: {str(e)}")
        return False


def enviar_email_rechazo_evento(user, evento, tipo_evento, motivo=None):
    """Envía email cuando un evento es rechazado"""
    context = {
        'user': user,
        'nombre': user.get_full_name() or user.email,
        'evento_titulo': evento.title,
        'evento_tipo': 'virtual' if tipo_evento == 'virtual' else 'presencial',
        'motivo': motivo or 'No cumple con nuestras políticas de contenido.',
        'site_name': 'EventPulse',
        'contacto_url': '/contacto/',
    }
    
    html_content = render_to_string('usuarios/email/evento_rechazado.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject=f'❌ Tu evento "{evento.title}" ha sido rechazado',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando email de rechazo a {user.email}: {str(e)}")
        return False


def enviar_email_resena_aprobada(resena):
    """Envía email cuando una reseña es aprobada"""
    evento = resena.evento_virtual or resena.evento_presencial
    evento_titulo = evento.title if evento else 'Evento'
    
    context = {
        'nombre': resena.nombre,
        'email': resena.email,
        'evento_titulo': evento_titulo,
        'calificacion': resena.calificacion,
        'comentario': resena.comentario,
        'site_name': 'EventPulse',
    }
    
    html_content = render_to_string('usuarios/email/resena_aprobada.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject='⭐ Tu reseña ha sido aprobada',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[resena.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando email de reseña aprobada a {resena.email}: {str(e)}")
        return False


def enviar_email_resena_rechazada(resena):
    """Envía email cuando una reseña es rechazada"""
    evento = resena.evento_virtual or resena.evento_presencial
    evento_titulo = evento.title if evento else 'Evento'
    
    context = {
        'nombre': resena.nombre,
        'email': resena.email,
        'evento_titulo': evento_titulo,
        'site_name': 'EventPulse',
        'contacto_url': '/contacto/',
    }
    
    html_content = render_to_string('usuarios/email/resena_rechazada.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject='ℹ️ Actualización sobre tu reseña',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[resena.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando email de reseña rechazada a {resena.email}: {str(e)}")
        return False


def enviar_email_respuesta_consulta(consulta):
    """Envía email cuando una consulta es respondida"""
    context = {
        'nombre': consulta.nombre,
        'email': consulta.email,
        'asunto': consulta.asunto,
        'mensaje': consulta.mensaje,
        'respuesta': consulta.respuesta,
        'site_name': 'EventPulse',
        'contacto_url': '/contacto/',
    }
    
    html_content = render_to_string('usuarios/email/consulta_respondida.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject=f'📩 Respuesta a tu consulta: {consulta.asunto}',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[consulta.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando respuesta de consulta a {consulta.email}: {str(e)}")
        return False


def enviar_email_suscripcion_evento(user, evento, tipo_evento):
    """Envía email cuando un usuario se suscribe a un evento"""
    context = {
        'user': user,
        'nombre': user.get_full_name() or user.email,
        'evento_titulo': evento.title,
        'evento_fecha': evento.start_datetime if hasattr(evento, 'start_datetime') else evento.start_date,
        'evento_tipo': 'virtual' if tipo_evento == 'virtual' else 'presencial',
        'site_name': 'EventPulse',
    }
    
    html_content = render_to_string('usuarios/email/suscripcion_exitosa.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject=f'🎉 Te has suscrito a "{evento.title}"',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando email de suscripción a {user.email}: {str(e)}")
        return False