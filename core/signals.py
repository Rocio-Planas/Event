from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from virtualEvent.models import VirtualEvent
from .models import Resena, Consulta, Suscripcion
from pe_communication.models import Notification

# ✅ SEÑAL 1: Mantener (no envía email, solo cambia rol)
@receiver(post_save, sender=VirtualEvent)
def promover_a_organizador(sender, instance, created, **kwargs):
    """
    Cuando se crea un evento virtual, si el creador es espectador,
    se convierte automáticamente en organizador.
    """
    if created:
        user = instance.created_by
        if user.rol == 'espectador' and not user.is_staff:
            user.rol = 'organizador'
            user.save(update_fields=['rol'])
            print(f"✅ {user.email} ha sido promovido a organizador por crear el evento '{instance.title}'")

# ❌ SEÑAL 2: COMENTADA - Ya usas enviar_email_resena_aprobada en utils.py
# @receiver(post_save, sender=Resena)
# def notificar_resena_aprobada(sender, instance, created, **kwargs):
#     if not created and instance.aprobada:
#         if not hasattr(instance, '_email_sent'):
#             send_mail(...)

# ❌ SEÑAL 3: COMENTADA - Ya usas enviar_email_respuesta_consulta en utils.py
# @receiver(post_save, sender=Consulta)
# def notificar_consulta_respondida(sender, instance, created, **kwargs):
#     if not created and instance.respondido and instance.respuesta:
#         if not hasattr(instance, '_email_sent'):
#             send_mail(...)

# ✅ SEÑAL 4: Mantener (sincronización de registros, NO envía email directamente,
#            aunque dentro tiene send_mail. Decide si la quieres)
@receiver(post_save, sender=Suscripcion)
def sincronizar_suscripcion_presencial(sender, instance, created, **kwargs):
    """
    Cuando se crea una suscripción a un evento presencial,
    crea automáticamente un registro en pe_registration.Registration.
    """
    if created and instance.tipo_evento == 'presencial':
        try:
            from in_person_events.models import Event
            from pe_registration.models import Registration, TicketType, EventWaitlist
            
            event = Event.objects.get(id=instance.evento_id)
            
            current_registrations = Registration.objects.filter(
                event=event,
                status__in=[Registration.Status.CONFIRMADA, Registration.Status.PENDIENTE]
            ).count()
            
            existing_registration = Registration.objects.filter(
                event=event,
                user=instance.usuario,
                status__in=[Registration.Status.CONFIRMADA, Registration.Status.PENDIENTE]
            ).first()
            
            if existing_registration:
                return
            
            existing_waitlist = EventWaitlist.objects.filter(
                event=event,
                user=instance.usuario
            ).first()
            
            if existing_waitlist:
                return
            
            if current_registrations >= event.capacity:
                EventWaitlist.objects.create(
                    event=event,
                    user=instance.usuario
                )
                Notification.objects.create(
                    user=instance.usuario,
                    title='Agregado a lista de espera',
                    message=f'Has sido agregado a la lista de espera para el evento "{event.title}" porque está lleno. Te notificaremos si se libera un espacio.',
                    notification_type=Notification.Type.MANUAL_ALERT
                )
                return
            
            ticket_type = event.ticket_types.first()
            if not ticket_type:
                ticket_type = TicketType.objects.create(
                    event=event,
                    name='General',
                    price=0
                )
            
            registration, created_reg = Registration.objects.get_or_create(
                event=event,
                user=instance.usuario,
                defaults={
                    'ticket_type': ticket_type,
                    'status': Registration.Status.CONFIRMADA,
                    'payment_status': 'completado'
                }
            )
            
            if created_reg:
                print(f"✅ Registration creado para {instance.usuario.email} en evento {event.title}")
                
                Notification.objects.create(
                    user=instance.usuario,
                    title=f'Inscripción confirmada a {event.title}',
                    message=f'Te has inscrito al evento "{event.title}". ¡Nos vemos allí!',
                    notification_type=Notification.Type.MANUAL_ALERT
                )
                
                # ⚠️ Este send_mail también envía correo. Si quieres evitarlo, coméntalo
                # send_mail(
                #     subject=f'Confirmación de inscripción - {event.title}',
                #     message=...,
                #     from_email=settings.DEFAULT_FROM_EMAIL,
                #     recipient_list=[instance.usuario.email],
                #     fail_silently=False,
                # )
            
        except Exception as e:
            print(f"⚠️ Error sincronizando suscripción: {str(e)}")

# ✅ SEÑAL 5: Mantener (solo notificación interna, NO email)
@receiver(post_delete, sender=Suscripcion)
def notification_on_suscripcion_deleted(sender, instance, **kwargs):
    """
    Envía notificación cuando un usuario cancela su suscripción a un evento presencial.
    """
    try:
        Notification.objects.create(
            user=instance.usuario,
            title=f'Suscripción cancelada a {instance.titulo_evento}',
            message=f'Has cancelado tu suscripción a "{instance.titulo_evento}". Puedes volver a suscribirte cuando quieras.',
            notification_type=Notification.Type.MANUAL_ALERT
        )
        
        # ❌ Comentar el send_mail si no quieres email duplicado
        # send_mail(
        #     subject=f'Suscripción cancelada - {instance.titulo_evento}',
        #     message=...,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[instance.usuario.email],
        #     fail_silently=False,
        # )
    except Exception:
        pass

# ❌ SEÑAL 6: COMENTADA COMPLETAMENTE (envía email de suscripción virtual)
# @receiver(post_save, sender='ve_invitations.EventFollower')
# def notification_on_follow_created(sender, instance, created, **kwargs):
#     if not created:
#         return
#     try:
#         Notification.objects.create(...)
#         send_mail(...)  # Email duplicado
#     except Exception:
#         pass

# ❌ SEÑAL 7: COMENTADA COMPLETAMENTE (envía email de cancelación suscripción virtual)
# @receiver(post_delete, sender='ve_invitations.EventFollower')
# def notification_on_follow_deleted(sender, instance, **kwargs):
#     try:
#         Notification.objects.create(...)
#         send_mail(...)  # Email duplicado
#     except Exception:
#         pass