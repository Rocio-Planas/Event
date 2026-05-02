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
    defaults = {
        'name': f'{template_type}_default',
        'subject': 'Invitación a Equipo de Evento',
        'body_html': '<h1>Estás invitado a unirte a nuestro equipo</h1><p>Haz clic en el botón para aceptar.</p>',
        'body_text': 'Estás invitado a unirte a nuestro equipo. Ingresa para aceptar.',
    }

    if template_type == EmailTemplate.TemplateType.EVENT_INVITATION:
        defaults = {
            'name': 'event_invitation_default',
            'subject': 'Invitación al evento',
            'body_html': '<h1>Has sido invitado a un evento</h1><p>Visita el enlace para ver los detalles del evento.</p>',
            'body_text': 'Has sido invitado a un evento. Visita el enlace para ver los detalles.',
        }

    template, created = EmailTemplate.objects.get_or_create(
        template_type=template_type,
        defaults=defaults
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


def send_event_invitation_email(recipient_email, event, organizer_name, custom_message=None):
    """
    Envía un email de invitación a un evento presencial.
    """
    from django.urls import reverse

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    event_url = f"{site_url}{reverse('core:detalle_evento', args=[event.id])}"

    template = get_or_create_template(EmailTemplate.TemplateType.EVENT_INVITATION)

    context = {
        'event': event,
        'organizer_name': organizer_name,
        'event_url': event_url,
        'custom_message': custom_message,
    }

    body_html = render_to_string('pe_communication/emails/event_invitation.html', context)
    body_text = f"Te invitamos al evento {event.title} organizado por {organizer_name}. Ver detalles: {event_url}"
    if custom_message:
        body_text += f"\n\nMensaje: {custom_message}"

    return send_email_notification(
        recipient_email=recipient_email,
        subject=f"Invitación al evento: {event.title}",
        body_html=body_html,
        body_text=body_text,
        template_type=EmailTemplate.TemplateType.EVENT_INVITATION,
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


@method_decorator(login_required, name='dispatch')
class SendManualNotificationView(View):
    """
    Vista para que el organizador envíe notificaciones manuales.
    """
    def post(self, request):
        from pe_communication.forms import ManualNotificationForm
        from pe_communication.models import Notification
        from django.contrib.auth import get_user_model

        User = get_user_model()
        form = ManualNotificationForm(request.POST)

        if not form.is_valid():
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        audience = form.cleaned_data['audience']
        title = form.cleaned_data['title']
        message = form.cleaned_data['message']

        if audience == 'all':
            users = User.objects.filter(is_active=True)
        elif audience == 'attendees':
            try:
                from pe_registration.models import Asistente
                attendees = Asistente.objects.values_list('user_id', flat=True)
                users = User.objects.filter(id__in=attendees, is_active=True)
            except Exception:
                users = User.objects.none()
        else:
            users = User.objects.none()

        if not users.exists():
            return JsonResponse({'success': False, 'error': 'No hay usuarios objetivo'}, status=400)

        notifications_to_create = [
            Notification(
                user=user,
                sender=request.user,
                title=title,
                message=message,
                notification_type=Notification.Type.MANUAL_ALERT
            )
            for user in users
        ]

        Notification.objects.bulk_create(notifications_to_create)

        return JsonResponse({
            'success': True,
            'message': f'Notificaciones enviadas a {len(notifications_to_create)} usuarios',
            'count': len(notifications_to_create)
        })


@login_required
def toggle_activity_subscription(request):
    """
    Endpoint API para suscribir/desuscribir al usuario de una actividad.
    """
    from pe_agenda.models import ActivitySubscription, Activity
    from django.apps import apps
    import logging

    logger = logging.getLogger(__name__)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    activity_id = request.POST.get('activity_id')
    if not activity_id:
        return JsonResponse({'success': False, 'error': 'activity_id requerido'}, status=400)

    try:
        Activity = apps.get_model('pe_agenda', 'Activity')
        activity = Activity.objects.get(pk=activity_id)
    except Activity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Actividad no encontrada'}, status=404)

    subscription, created = ActivitySubscription.objects.get_or_create(
        user=request.user,
        activity_id=activity_id
    )

    if created:
        subscription.activity_title = activity.title
        subscription.save()
        logger.info(f'Usuario {request.user.email} se suscribió a {activity.title}')
        return JsonResponse({
            'success': True,
            'action': 'subscribed',
            'activity_title': activity.title,
            'message': f'Te has suscrito a {activity.title}'
        })
    else:
        subscription.delete()
        logger.info(f'Usuario {request.user.email} se desuscribió de {activity.title}')
        return JsonResponse({
            'success': True,
            'action': 'unsubscribed',
            'message': f'Te has desuscrito de {activity.title}'
        })


@login_required
def get_unread_notifications(request):
    """
    Endpoint para obtener notificaciones no leídas del usuario.
    """
    from pe_communication.models import Notification

    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:10]

    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.notification_type,
        'sender': {
            'name': n.sender.get_full_name() if n.sender else 'Sistema',
            'username': n.sender.username if n.sender else None
        } if n.sender else {'name': 'Sistema', 'username': None},
        'created_at': n.created_at.isoformat(),
    } for n in notifications]

    return JsonResponse({
        'success': True,
        'notifications': data,
        'count': len(data)
    })


@login_required
def mark_notification_read(request):
    """
    Endpoint para marcar una notificación como leída.
    """
    from pe_communication.models import Notification

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    notification_id = request.POST.get('notification_id')
    if not notification_id:
        return JsonResponse({'success': False, 'error': 'notification_id requerido'}, status=400)

    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True, 'message': 'Notificación marcada como leída'})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notificación no encontrada'}, status=404)


@login_required
def delete_notification(request):
    """
    Endpoint para eliminar una notificación.
    """
    from pe_communication.models import Notification

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    notification_id = request.POST.get('notification_id')
    if not notification_id:
        return JsonResponse({'success': False, 'error': 'notification_id requerido'}, status=400)

    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.delete()
        return JsonResponse({'success': True, 'message': 'Notificación eliminada'})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notificación no encontrada'}, status=404)


@method_decorator(login_required, name='dispatch')
class NotificationListView(TemplateView):
    """
    Vista para mostrar todas las notificaciones del usuario.
    """
    template_name = 'pe_communication/notifications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from pe_communication.models import Notification

        # Obtener todas las notificaciones del usuario, ordenadas por fecha descendente
        notifications = Notification.objects.filter(user=self.request.user).order_by('-created_at')

        # Separar en leídas y no leídas para mostrar primero las no leídas
        unread_notifications = notifications.filter(is_read=False)
        read_notifications = notifications.filter(is_read=True)

        context['unread_notifications'] = unread_notifications
        context['read_notifications'] = read_notifications
        context['total_count'] = notifications.count()

        return context