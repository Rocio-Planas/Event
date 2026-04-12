from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string


def send_invitation_email(email, event, token):
    """Envía email de invitación a evento privado (usa token para validación)."""
    invite_link = f"{settings.BASE_URL}{reverse('ve_invitations:accept_invitation', args=[token])}"

    # Imprime el enlace completo para evitar truncamiento al copiar
    print(
        f"\n{'='*60}\n📨 INVITACIÓN PRIVADA\nPara: {email}\nEnlace completo:\n{invite_link}\n{'='*60}\n"
    )

    context = {
        "event": event,
        "invite_link": invite_link,
        "organizer": event.created_by.get_full_name() or event.created_by.username,
    }
    subject = f"Invitación al evento privado: {event.title}"
    html_message = render_to_string("ve_invitations/email/invitation.html", context)
    plain_message = f"Haz clic para unirte: {invite_link}"
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=html_message,
        fail_silently=False,
    )


def send_material_notification(event):
    """Envía email a todos los seguidores del evento cuando hay nuevo material.
    Usa el unique_link del evento (mismo que aparece en el dashboard)."""
    from .models import EventFollower

    followers = EventFollower.objects.filter(
        event=event, receive_reminders=True
    ).select_related("user")
    emails = [f.user.email for f in followers]
    if not emails:
        return

    # Usar el mismo enlace que se muestra en el dashboard (waiting room)
    waiting_room_path = reverse("ve_streaming:waiting_room", args=[event.unique_link])
    link = f"{settings.BASE_URL}{waiting_room_path}"

    context = {
        "event": event,
        "materials": event.materials,
        "link": link,
    }
    subject = f"📁 Nuevo material disponible: {event.title}"
    html_message = render_to_string(
        "ve_invitations/email/material_available.html", context
    )
    plain_message = (
        f"El organizador ha subido material para {event.title}. Ver en: {link}"
    )
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        emails,
        html_message=html_message,
        fail_silently=False,
    )
