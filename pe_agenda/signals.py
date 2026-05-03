from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

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

    if notifications_to_create:
        Notification.objects.bulk_create(notifications_to_create)
        logger.info(f'Notificaciones de cambio enviadas a {len(notifications_to_create)} usuarios')