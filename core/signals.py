from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from virtualEvent.models import VirtualEvent
from .models import Resena, Consulta

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