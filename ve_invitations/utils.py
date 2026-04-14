from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from datetime import timedelta
from virtualEvent.utils.calendar_utils import (  # type: ignore
    generate_ics,
)


def send_invitation_email(email, event, token):
    """Envía email de invitación con enlace de acceso y archivo .ics adjunto."""
    invite_link = f"{settings.BASE_URL}{reverse('ve_invitations:accept_invitation', args=[token])}"
    ics_download_link = (
        f"{settings.BASE_URL}{reverse('virtualEvent:download_ics', args=[event.id])}"
    )

    # Fechas para Google Calendar
    start_google = event.start_datetime.strftime("%Y%m%dT%H%M%S")
    end_datetime = event.start_datetime + timedelta(minutes=event.duration_minutes)
    end_google = end_datetime.strftime("%Y%m%dT%H%M%S")
    google_cal_url = (
        f"https://www.google.com/calendar/render?action=TEMPLATE"
        f"&text={event.title}&dates={start_google}/{end_google}"
        f"&details={event.description}&location=Virtual"
    )

    print(
        f"\n{'='*60}\n📨 INVITACIÓN PRIVADA\nPara: {email}\nEnlace completo:\n{invite_link}\n{'='*60}\n"
    )

    context = {
        "event": event,
        "invite_link": invite_link,
        "organizer": event.created_by.get_full_name() or event.created_by.username,
        "google_calendar_url": google_cal_url,
        "ics_download_link": ics_download_link,
    }

    subject = f"Invitación al evento privado: {event.title}"
    html_message = render_to_string("ve_invitations/email/invitation.html", context)
    plain_message = (
        f"Haz clic para unirte: {invite_link}\n\n"
        f"Agenda el evento:\n"
        f"- Descargar .ics: {ics_download_link}\n"
        f"- Google Calendar: {google_cal_url}"
    )

    email_msg = EmailMessage(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    email_msg.attach_alternative(html_message, "text/html")

    # Adjuntar el archivo .ics
    ics_content = generate_ics(event)
    email_msg.attach(f"evento_{event.id}.ics", ics_content, "text/calendar")

    email_msg.send(fail_silently=False)


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
