import json
import logging
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string

from pe_staff.models import StaffInvitation, StaffMember, StaffRole, InvitationStatus
from pe_communication.models import EmailTemplate, EmailLog


logger = logging.getLogger(__name__)


def get_or_create_template(template_type):
    """Obtiene o crea una plantilla por defecto."""
    template, created = EmailTemplate.objects.get_or_create(
        template_type=template_type,
        defaults={
            'name': f'{template_type}_default',
            'subject': 'Invitación a Equipo de Evento',
            'body_html': '<h1>Estás invitar a unirte a nuestro equipo</h1><p>Haz clic en el botón para aceptar.</p>',
            'body_text': 'Estás invitado a unirte a nuestro equipo. Ingresa para aceptar.',
        }
    )
    return template


def send_email_notification(recipient_email, subject, body_html, body_text, template_type=None):
    """
    Envía un email y registra el log.
    """
    template_obj = None
    if template_type:
        template_obj = get_or_create_template(template_type)
    
    email_log = EmailLog.objects.create(
        recipient=recipient_email,
        subject=subject,
        template=template_obj,
        status=EmailLog.Status.PENDIENTE,
    )
    
    try:
        send_mail(
            subject=subject,
            message=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=body_html,
            fail_silently=False,
        )
        
        email_log.status = EmailLog.Status.ENVIADO
        email_log.sent_at = timezone.now()
        email_log.save()
        
        logger.info(f'Email enviado a {recipient_email}')
        return {'success': True, 'log_id': email_log.id}
        
    except Exception as e:
        email_log.status = EmailLog.Status.FALLIDO
        email_log.error_message = str(e)
        email_log.save()
        
        logger.error(f'Error al enviar email a {recipient_email}: {e}')
        return {'success': False, 'error': str(e)}


def send_staff_invitation_email(invitation):
    """
    Envía email de invitación de staff.
    """
    from django.urls import reverse
    
    # Construir URL de aceptación
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    accept_url = f"{site_url}/equipo/accept/{invitation.token}/"
    
    # Obtener o crear plantilla
    template = get_or_create_template(EmailTemplate.TemplateType.STAFF_INVITATION)
    
    # Renderizar contenido
    context = {
        'invitation': invitation,
        'accept_url': accept_url,
        'event': invitation.event,
    }
    
    body_html = render_to_string('pe_communication/emails/staff_invitation.html', context)
    body_text = f"Estás invitado a unirte al equipo del evento {invitation.event.title} como {invitation.get_role_display()}. Para aceptar, visita: {accept_url}"
    
    return send_email_notification(
        recipient_email=invitation.email,
        subject=f"Invitación al equipo: {invitation.event.title}",
        body_html=body_html,
        body_text=body_text,
        template_type=EmailTemplate.TemplateType.STAFF_INVITATION,
    )


def send_staff_confirmation_email(member):
    """
    Envía email de confirmación cuando staff acepta invitación.
    """
    template = get_or_create_template(EmailTemplate.TemplateType.STAFF_ACCEPTED)
    
    context = {
        'member': member,
        'event': member.event,
    }
    
    body_html = render_to_string('pe_communication/emails/staff_confirmed.html', context)
    body_text = f"¡Bienvenido al equipo! Has aceptado la invitación para {member.event.title} como {member.get_role_display()}."
    
    return send_email_notification(
        recipient_email=member.user.email,
        subject=f"Confirmación: Team {member.event.title}",
        body_html=body_html,
        body_text=body_text,
        template_type=EmailTemplate.TemplateType.STAFF_ACCEPTED,
    )


def send_zone_assignment_email(member, zone_name):
    """
    Envía email cuando se asigna zona al staff.
    """
    template = get_or_create_template(EmailTemplate.TemplateType.STAFF_ASSIGNED)
    
    context = {
        'member': member,
        'event': member.event,
        'zone': zone_name,
    }
    
    body_html = render_to_string('pe_communication/emails/zone_assigned.html', context)
    body_text = f"Has sido asignado a la zona: {zone_name} para el evento {member.event.title}."
    
    return send_email_notification(
        recipient_email=member.user.email,
        subject=f"Zona Asignada: {member.event.title}",
        body_html=body_html,
        body_text=body_text,
        template_type=EmailTemplate.TemplateType.STAFF_ASSIGNED,
    )


@method_decorator(login_required, name='dispatch')
class EmailTemplatesView(TemplateView):
    """Vista para gestionar plantillas de email."""
    template_name = 'pe_communication/templates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['templates'] = EmailTemplate.objects.all()
        return context