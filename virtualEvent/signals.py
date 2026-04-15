from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from ve_chat.models import ChatMessage, HandRaise, PollVote, SatisfactionRating
from .models import EventAnalytics, VirtualEvent
from django.db.models import Avg


def update_event_analytics(event):
    """Actualiza las métricas agregadas para un evento."""
    analytics, _ = EventAnalytics.objects.get_or_create(event=event)
    if not hasattr(event, "streaming_room"):
        return
    room = event.streaming_room
    analytics.total_messages = ChatMessage.objects.filter(room=room).count()
    analytics.total_hands = HandRaise.objects.filter(room=room).count()
    analytics.total_poll_votes = PollVote.objects.filter(poll__room=room).count()
    avg_sat = (
        SatisfactionRating.objects.filter(room=room).aggregate(Avg("rating"))[
            "rating__avg"
        ]
        or 0
    )
    analytics.average_satisfaction = round(avg_sat, 1)
    analytics.save()


@receiver(post_save, sender=ChatMessage)
def update_on_message(sender, instance, **kwargs):
    update_event_analytics(instance.room.event)


@receiver(post_save, sender=HandRaise)
def update_on_hand(sender, instance, **kwargs):
    update_event_analytics(instance.room.event)


@receiver(post_save, sender=PollVote)
def update_on_vote(sender, instance, **kwargs):
    update_event_analytics(instance.poll.room.event)


@receiver(post_save, sender=SatisfactionRating)
def update_on_satisfaction(sender, instance, **kwargs):
    update_event_analytics(instance.room.event)


# ========== NUEVA SEÑAL PARA APROBACIÓN DE EVENTOS ==========
@receiver(pre_save, sender=VirtualEvent)
def notify_event_approval(sender, instance, **kwargs):
    """
    Cuando un evento cambia de estado a 'aprobado', envía un email al organizador.
    """
    if instance.pk:  # Solo si el evento ya existe (no es nuevo)
        try:
            old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        # Detectamos el cambio de estado a 'aprobado'
        if old.estado != 'aprobado' and instance.estado == 'aprobado':
            subject = f'Tu evento "{instance.title}" ha sido aprobado'
            message = f'''
Hola {instance.created_by.get_full_name() or instance.created_by.email},

¡Felicidades! Tu evento "{instance.title}" ha sido aprobado por el administrador.
Ya está visible para todos los usuarios en la plataforma.

Puedes verlo aquí: {settings.BASE_URL}/eventos/{instance.id}/

Si tienes dudas, contacta con soporte.

Saludos,
Equipo EventPulse
'''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.created_by.email],
                fail_silently=False,
            )