from django.db import transaction
from django.db.models import signals
from django.apps import apps


def promote_from_waitlist(sender, **kwargs):
    """
    Signal para promover automáticamente al primer usuario en lista de espera
    cuando se cancela una inscripción.
    """
    if not kwargs.get('instance'):
        return
    
    registration = kwargs['instance']
    event = registration.event
    user = registration.user
    
    from pe_registration.models import EventWaitlist
    
    with transaction.atomic():
        next_in_line = EventWaitlist.objects.select_for_update(nowait=False).filter(
            event=event
        ).order_by('created_at').first()
        
        if next_in_line:
            Registration = apps.get_model('pe_registration', 'Registration')
            TicketType = apps.get_model('pe_registration', 'TicketType')
            
            default_ticket = TicketType.objects.filter(event=event).first()
            
            new_registration = Registration.objects.create(
                event=event,
                user=next_in_line.user,
                ticket_type=default_ticket,
                status=Registration.Status.CONFIRMADA,
                payment_status='pendiente'
            )
            
            next_in_line.delete()
            
            send_waitlist_notification(event, next_in_line.user)


def send_waitlist_notification(event, user):
    """
    Crea una notificación para el usuario promociones.
    """
    try:
        Notification = apps.get_model('pe_communication', 'Notification')
        Notification.objects.create(
            user=user,
            title=f"¡Tienes un espacio en {event.title}!",
            message=f"Felicitaciones! Se ha liberado un cupo y has sido promovido de la lista de espera al evento {event.title}. Tu inscripción ha sido confirmada.",
            notification_type='success'
        )
    except Exception:
        pass


def register_signal(sender, **kwargs):
    """
    Registra el signal post_delete para Promotion.
    """
    Registration = sender
    signals.post_delete.connect(promote_from_waitlist, sender=Registration)