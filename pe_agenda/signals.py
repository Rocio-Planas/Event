from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import logging

from .models import Activity

logger = logging.getLogger(__name__)


@receiver(post_save, sender='pe_agenda.ActivitySubscription')
def notify_subscription_created(sender, instance, created, **kwargs):
    """
    Señal que genera una notificación cuando un usuario se suscribe a una actividad.
    """
    from pe_communication.models import Notification

    if created:
        Notification.objects.create(
            user=instance.user,
            title=f'Suscripción a "{instance.activity_title}"',
            message=f'Te has suscrito exitosamente a la actividad "{instance.activity_title}". '
                    f'Recibirás notificaciones cuando haya cambios en la agenda.',
            notification_type=Notification.Type.SUBSCRIPTION
        )
        
        send_mail(
            subject=f'Confirmación de suscripción - {instance.activity_title}',
            message=f'Hola {instance.user.get_full_name() or instance.user.email},\n\n'
                   f'Te has suscrito a la actividad "{instance.activity_title}".\n\n'
                   f'Recibirás notificaciones cuando haya cambios en la agenda.\n\n'
                   f'El equipo de EventPulse',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
            fail_silently=False,
        )
        logger.info(f'Notificación de suscripción enviada a {instance.user.email}')


@receiver(post_delete, sender='pe_agenda.ActivitySubscription')
def notify_subscription_deleted(sender, instance, **kwargs):
    """
    Señal que genera una notificación cuando un usuario se desuscribe de una actividad.
    """
    from pe_communication.models import Notification

    Notification.objects.create(
        user=instance.user,
        title=f'Desuscrito de "{instance.activity_title}"',
        message=f'Has cancelado tu suscripción a la actividad "{instance.activity_title}". '
                f'Ya no recibirás notificaciones de cambios.',
        notification_type=Notification.Type.SUBSCRIPTION
    )
    
    send_mail(
        subject=f'Suscripción cancelada - {instance.activity_title}',
        message=f'Hola {instance.user.get_full_name() or instance.user.email},\n\n'
               f'Has cancelado tu suscripción a la actividad "{instance.activity_title}".\n'
               f'Ya no recibirás notificaciones de cambios.\n\n'
               f'El equipo de EventPulse',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[instance.user.email],
        fail_silently=False,
    )
    logger.info(f'Notificación de desuscripción enviada a {instance.user.email}')


@receiver(post_save, sender='pe_agenda.Activity')
def notify_activity_changed(sender, instance, **kwargs):
    """
    Señal que genera notificaciones cuando una actividad se actualiza.
    Notifica a todos los suscriptores de esa actividad.
    """
    from pe_communication.models import Notification
    from django.apps import apps

    if instance.id is None:
        return

    created = kwargs.get('created', True)
    if created:
        return

    try:
        ActivitySubscription = apps.get_model('pe_agenda', 'ActivitySubscription')
    except Exception:
        logger.warning('Modelo ActivitySubscription no disponible')
        return

    subscriptions = ActivitySubscription.objects.filter(activity_id=instance.id)

    if not subscriptions.exists():
        return

    notifications_to_create = []
    emails_to_send = []
    for subscription in subscriptions:
        notifications_to_create.append(
            Notification(
                user=subscription.user,
                title=f'Cambio en "{instance.title}"',
                message=f'La actividad "{instance.title}" ha sido modificada. '
                        f'Nuevo horario: {instance.start_time.strftime("%d/%m/%Y %H:%M")} - '
                        f'{instance.end_time.strftime("%H:%M")}',
                notification_type=Notification.Type.AGENDA_CHANGE
            )
        )
        emails_to_send.append({
            'email': subscription.user.email,
            'name': subscription.user.get_full_name() or subscription.user.email,
        })

    if notifications_to_create:
        Notification.objects.bulk_create(notifications_to_create)
        logger.info(f'Notificaciones de cambio enviadas a {len(notifications_to_create)} usuarios')
        
        for em in emails_to_send:
            send_mail(
                subject=f'Cambio en actividad - {instance.title}',
                message=f'Hola {em["name"]},\n\n'
                       f'La actividad "{instance.title}" ha sido modificada.\n'
                       f'Nuevo horario: {instance.start_time.strftime("%d/%m/%Y %H:%M")} - {instance.end_time.strftime("%H:%M")}\n\n'
                       f'El equipo de EventPulse',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[em['email']],
                fail_silently=False,
            )


@receiver(post_save, sender='pe_agenda.Activity')
def notify_speaker_location_changed(sender, instance, created, **kwargs):
    """
    Señal que notifica al ponente cuando cambia el stand/location de su actividad.
    """
    from pe_communication.models import Notification
    from django.contrib.auth import get_user_model
    
    if created:
        return
    
    if not instance.speaker_email:
        return
    
    try:
        old_instance = Activity.objects.get(pk=instance.pk)
    except Activity.DoesNotExist:
        return
    
    if old_instance.location == instance.location:
        return
    
    User = get_user_model()
    try:
        user = User.objects.get(email__iexact=instance.speaker_email)
    except User.DoesNotExist:
        send_mail(
            subject=f'Cambio de stand - {instance.title}',
            message=f'Hola {instance.speaker_name or instance.speaker_email},\n\n'
                   f'El stand de tu actividad "{instance.title}" ha cambiado.\n'
                   f'Anterior: {old_instance.location}\n'
                   f'Nuevo: {instance.location}\n\n'
                   f'El equipo de EventPulse',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.speaker_email],
            fail_silently=False,
        )
        return
    
    Notification.objects.create(
        user=user,
        title=f'Cambio de stand - {instance.title}',
        message=f'El stand/location de tu actividad "{instance.title}" ha cambiado de "{old_instance.location}" a "{instance.location}".',
        notification_type=Notification.Type.MANUAL_ALERT
    )
    
    send_mail(
        subject=f'Cambio de stand - {instance.title}',
        message=f'Hola {instance.speaker_name or instance.speaker_email},\n\n'
               f'El stand de tu actividad "{instance.title}" ha cambiado.\n'
               f'Anterior: {old_instance.location}\n'
               f'Nuevo: {instance.location}\n\n'
               f'El equipo de EventPulse',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[instance.speaker_email],
        fail_silently=False,
    )
    logger.info(f'Notificación de cambio de stand enviada a {instance.speaker_email}')