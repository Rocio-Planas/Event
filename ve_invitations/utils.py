from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


def send_invitation_email(email, event, token):
    link = f"{settings.BASE_URL}{reverse('ve_invitations:accept_invitation', args=[token])}"
    # O si tu waiting room usa el token directamente:
    # link = f"{settings.BASE_URL}{reverse('ve_streaming:waiting_room_with_token', args=[token])}"
    subject = f"Invitación al evento privado: {event.title}"
    message = f"Haz clic para unirte: {link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
