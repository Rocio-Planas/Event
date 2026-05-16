from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from django.urls import reverse
import logging

from .models import StaffInvitation, StaffMember, InvitationStatus
from pe_communication.models import Notification
from pe_communication.views import send_staff_invitation_email, send_staff_confirmation_email, send_activity_assigned_email

logger = logging.getLogger(__name__)
User = get_user_model()


def resolve_actividad_zone(staff_member):
    """Convierte zonas con formato actividad:<id> en un assignment real de Activity."""
    if staff_member.user_type != StaffMember.UserType.PONENTE:
        return

    zone = staff_member.zone or ''
    if not zone.startswith('actividad:'):
        return

    try:
        activity_id = int(zone.split(':', 1)[1])
    except (ValueError, IndexError):
        return

    try:
        Activity = apps.get_model('pe_agenda', 'Activity')
        activity = Activity.objects.filter(id=activity_id, event=staff_member.event).first()
    except Exception:
        activity = None

    if activity:
        staff_member.activity = activity
        staff_member.zone = ''
        staff_member.save(update_fields=['activity', 'zone'])
        
        # Actualizar el speaker de la actividad
        activity.speaker_name = staff_member.user.get_full_name() or staff_member.user.email
        activity.speaker_email = staff_member.user.email
        activity.save(update_fields=['speaker_name', 'speaker_email'])


@receiver(post_save, sender=StaffInvitation)
def notification_on_invitation_created(sender, instance, created, **kwargs):
    """Envía notificación cuando se crea una invitación."""
    if not created:
        return
    
    # Solo enviar email si el usuario existe en la plataforma
    try:
        user = User.objects.get(email__iexact=instance.email)
        
        # Enviar email con plantilla HTML profesional
        try:
            send_staff_invitation_email(instance)
        except Exception as e:
            logger.error(f'Error al enviar email de invitación: {e}')
        
        # Crear notificación in-app
        if instance.user_type == StaffInvitation.UserType.PONENTE:
            role_text = 'Ponente'
        elif instance.role:
            role_text = instance.get_role_display()
        else:
            role_text = 'Staff'
        
        Notification.objects.create(
            user=user,
            title=f'Invitación como {role_text} para {instance.event.title}',
            message=f'Has sido invitado a participar como {role_text} en el evento "{instance.event.title}". '
                    f'Haz clic en el enlace del correo para confirmar tu participación.',
            notification_type=Notification.Type.MANUAL_ALERT
        )
    except User.DoesNotExist:
        logger.info(f'No se envió invitación a {instance.email}: usuario no existe en la plataforma')
    
    logger.info(f'Notificación de invitación enviada a {instance.email}')


@receiver(post_save, sender=StaffMember)
def notification_on_activity_assigned(sender, instance, created, **kwargs):
    """Envía notificación cuando se asigna actividad a un ponente."""
    if instance.user_type != StaffMember.UserType.PONENTE:
        return
    
    if not instance.activity:
        return
    
    if not created:
        try:
            old_instance = StaffMember.objects.get(pk=instance.pk)
            if old_instance.activity_id == instance.activity_id:
                return
        except StaffMember.DoesNotExist:
            return
    
    Notification.objects.create(
        user=instance.user,
        title=f'Actividad asignada: {instance.activity.title}',
        message=f'Se te ha asignado la actividad "{instance.activity.title}" en el evento "{instance.event.title}". '
                f'Horario: {instance.activity.start_time.strftime("%d/%m/%Y %H:%M")} - {instance.activity.end_time.strftime("%H:%M")}.',
        notification_type=Notification.Type.MANUAL_ALERT
    )
    
    try:
        send_activity_assigned_email(instance, instance.activity)
    except Exception as e:
        logger.error(f'Error al enviar email de actividad asignada: {e}')
    
    logger.info(f'Notificación de asignación de actividad enviada a {instance.user.email}')


@receiver(post_save, sender=StaffMember)
def notification_on_zone_assigned(sender, instance, created, **kwargs):
    """Envía notificación cuando se asigna zona a un miembro del staff (solo notificación, sin email)."""
    if instance.user_type != StaffMember.UserType.STAFF:
        return
    
    if not instance.zone:
        return
    
    if not created:
        try:
            old_instance = StaffMember.objects.get(pk=instance.pk)
            if old_instance.zone == instance.zone:
                return
        except StaffMember.DoesNotExist:
            return
    
    Notification.objects.create(
        user=instance.user,
        title=f'Zona asignada: {instance.zone}',
        message=f'Se te ha asignado la zona "{instance.zone}" en el evento "{instance.event.title}". ',
        notification_type=Notification.Type.MANUAL_ALERT
    )
    logger.info(f'Notificación de asignación de zona enviada a {instance.user.email}')


@receiver(post_save, sender=StaffInvitation)
def create_staff_member_on_accept(sender, instance, created, **kwargs):
    """Crea el miembro del staff cuando una invitación pasa a aceptada."""
    if instance.status != InvitationStatus.ACEPTADA:
        return

    User = get_user_model()
    try:
        user = User.objects.get(email__iexact=instance.email)
    except User.DoesNotExist:
        return

    role_value = instance.role
    if instance.user_type == 'ponente':
        role_value = 'ponente'

    if role_value is None and instance.user_type == 'ponente':
        role_value = 'ponente'

    member, _ = StaffMember.objects.update_or_create(
        event=instance.event,
        user=user,
        defaults={
            'role': role_value,
            'user_type': instance.user_type,
            'zone': '',
            'activity': None,
        }
    )

    resolve_actividad_zone(member)

    if user.rol != 'staff':
        user.rol = 'staff'
        user.save(update_fields=['rol'])


@receiver(post_delete, sender=StaffMember)
def clear_activity_speaker_on_delete(sender, instance, **kwargs):
    """Limpia el speaker de la actividad cuando se elimina un StaffMember."""
    if instance.activity:
        instance.activity.speaker_name = None
        instance.activity.speaker_email = None
        instance.activity.save(update_fields=['speaker_name', 'speaker_email'])


@receiver(pre_delete, sender=StaffMember)
def delete_related_invitation_on_member_delete(sender, instance, **kwargs):
    """Elimina la invitación relacionada cuando se elimina un StaffMember."""
    from .models import StaffInvitation
    StaffInvitation.objects.filter(
        event=instance.event,
        email=instance.user.email,
        status=InvitationStatus.ACEPTADA
    ).delete()
