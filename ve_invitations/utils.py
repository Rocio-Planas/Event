from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string


def send_invitation_email(email, event, token):
    invite_link = f"{settings.BASE_URL}{reverse('ve_invitations:accept_invitation', args=[token])}"
    context = {"event": event, "invite_link": invite_link}
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
