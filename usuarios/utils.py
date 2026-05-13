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