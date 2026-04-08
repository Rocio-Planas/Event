from django.db.models.signals import post_save
from django.dispatch import receiver
from ve_chat.models import ChatMessage, HandRaise, PollVote, SatisfactionRating
from .models import EventAnalytics
from django.db.models import Avg


def update_event_analytics(event):
    """Actualiza las métricas agregadas para un evento."""
    analytics, _ = EventAnalytics.objects.get_or_create(event=event)
    if not hasattr(event, "streaming_room"):
        return  # No hay sala asociada, salir
    room = event.streaming_room  # OneToOne relation
    analytics.total_messages = ChatMessage.objects.filter(room=room).count()
    analytics.total_hands = HandRaise.objects.filter(room=room).count()
    analytics.total_poll_votes = PollVote.objects.filter(poll__room=room).count()
    # Satisfacción promedio
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
