from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from virtualEvent.models import VirtualEvent
from .models import Resena, Consulta, Suscripcion
from pe_communication.models import Notification

@receiver(post_save, sender=VirtualEvent)
def promover_a_organizador(sender, instance, created, **kwargs):
    """
    Cuando se crea un evento virtual, si el creador es espectador,
    se convierte automáticamente en organizador.
    """
    if created:
        user = instance.created_by
        # Solo si no es administrador ni organizador, y no es staff
        if user.rol == 'espectador' and not user.is_staff:
            user.rol = 'organizador'
            user.save(update_fields=['rol'])
            print(f"✅ {user.email} ha sido promovido a organizador por crear el evento '{instance.title}'")

@receiver(post_save, sender=Resena)
def notificar_resena_aprobada(sender, instance, created, **kwargs):
    # Solo enviar cuando la reseña se actualiza (no cuando se crea) y cambia a aprobada
    if not created and instance.aprobada:
        # Verificar si ya se había enviado antes (evitar duplicados)
        if not hasattr(instance, '_email_sent'):
            asunto = 'Tu reseña ha sido aprobada - EventPulse'
            mensaje = f"""
            Hola {instance.nombre},

            Tu reseña para el evento "{instance.evento.title}" ha sido aprobada y publicada en nuestra plataforma.

            Calificación: {instance.calificacion} estrellas
            Comentario: {instance.comentario}

            ¡Gracias por compartir tu experiencia!

            Saludos,
            El equipo de EventPulse
            """
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=False,
            )
            instance._email_sent = True

@receiver(post_save, sender=Consulta)
def notificar_consulta_respondida(sender, instance, created, **kwargs):
    # Enviar cuando se marca como respondido y tiene respuesta
    if not created and instance.respondido and instance.respuesta:
        if not hasattr(instance, '_email_sent'):
            asunto = 'Respuesta a tu consulta - EventPulse'
            mensaje = f"""
            Hola {instance.nombre},

            Tu consulta ha sido respondida por nuestro equipo:

            Tu mensaje: {instance.mensaje}

            Respuesta: {instance.respuesta}

            Si tienes más dudas, no dudes en contactarnos.

            Saludos,
            El equipo de EventPulse
            """
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=False,
            )
            instance._email_sent = True


@receiver(post_save, sender=Suscripcion)
def sincronizar_suscripcion_presencial(sender, instance, created, **kwargs):
    """
    Cuando se crea una suscripción a un evento presencial,
    crea automáticamente un registro en pe_registration.Registration.

    Nota de negocio:
    - Suscripciones desde la homepage deben ser confirmadas automáticamente.
    - Invitaciones privadas se manejan como pendientes en in_person_events.views.create_event_form.
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
                
                send_mail(
                    subject=f'Confirmación de inscripción - {event.title}',
                    message=f'Hola {instance.usuario.get_full_name() or instance.usuario.email},\n\n'
                           f'Te has inscrito al evento "{event.title}".\n'
                           f'Fecha: {event.start_date}\n'
                           f'Ubicación: {event.location}\n\n'
                           f'¡Nos vemos allí!\n\n'
                           f'El equipo de EventPulse',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.usuario.email],
                    fail_silently=False,
                )
            
        except Exception as e:
            print(f"⚠️ Error sincronizando suscripción: {str(e)}")


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
        
        send_mail(
            subject=f'Suscripción cancelada - {instance.titulo_evento}',
            message=f'Hola {instance.usuario.get_full_name() or instance.usuario.email},\n\n'
                   f'Has cancelado tu suscripción a "{instance.titulo_evento}".\n'
                   f'Puedes volver a suscribirte cuando quieras.\n\n'
                   f'El equipo de EventPulse',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.usuario.email],
            fail_silently=False,
        )
    except Exception:
        pass


@receiver(post_save, sender='ve_invitations.EventFollower')
def notification_on_follow_created(sender, instance, created, **kwargs):
    """
    Envía notificación cuando un usuario se suscribe a un evento virtual.
    """
    if not created:
        return
    
    try:
        Notification.objects.create(
            user=instance.user,
            title=f'Suscripción a evento virtual',
            message=f'Te has suscrito al evento virtual "{instance.event.title}".',
            notification_type=Notification.Type.MANUAL_ALERT
        )
        
        send_mail(
            subject=f'Confirmación de suscripción - {instance.event.title}',
            message=f'Hola {instance.user.get_full_name() or instance.user.email},\n\n'
                   f'Te has suscrito al evento virtual "{instance.event.title}".\n\n'
                   f'¡Nos vemos allí!\n\n'
                   f'El equipo de EventPulse',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
            fail_silently=False,
        )
    except Exception:
        pass


@receiver(post_delete, sender='ve_invitations.EventFollower')
def notification_on_follow_deleted(sender, instance, **kwargs):
    """
    Envía notificación cuando un usuario cancela su suscripción a un evento virtual.
    """
    try:
        event_title = instance.event.title
        
        Notification.objects.create(
            user=instance.user,
            title=f'Suscripción cancelada a evento virtual',
            message=f'Has cancelado tu suscripción al evento virtual "{event_title}".',
            notification_type=Notification.Type.MANUAL_ALERT
        )
        
        send_mail(
            subject=f'Suscripción cancelada - {event_title}',
            message=f'Hola {instance.user.get_full_name() or instance.user.email},\n\n'
                   f'Has cancelado tu suscripción al evento virtual "{event_title}".\n'
                   f'Puedes volver a suscribirte cuando quieras.\n\n'
                   f'El equipo de EventPulse',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
            fail_silently=False,
        )
    except Exception:
        pass