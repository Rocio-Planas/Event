from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from virtualEvent.models import VirtualEvent
from ve_invitations.models import EventFollower, Invitation


class Command(BaseCommand):
    help = "Envía recordatorios de eventos que comienzan en 1 hora"

    def handle(self, *args, **options):
        now = timezone.now()
        # Eventos que comienzan entre ahora+55 min y ahora+65 min (margen)
        start_range_lower = now + timezone.timedelta(minutes=55)
        start_range_upper = now + timezone.timedelta(minutes=65)
        events = VirtualEvent.objects.filter(
            start_datetime__gte=start_range_lower, start_datetime__lte=start_range_upper
        )

        for event in events:
            # 1. Seguidores que quieren recordatorios
            followers = EventFollower.objects.filter(
                event=event, receive_reminders=True
            ).select_related("user")
            emails_followers = [f.user.email for f in followers]

            # 2. Invitaciones a eventos privados (si el evento es privado, las invitaciones existen)
            # Enviamos a los emails que tienen invitación, sin importar si han aceptado o no
            invitations = Invitation.objects.filter(event=event)
            emails_invited = [inv.email for inv in invitations]

            # Combinar y eliminar duplicados
            all_emails = set(emails_followers + emails_invited)

            if not all_emails:
                continue

            # Renderizar plantilla HTML
            context = {
                "event": event,
                "start_time": event.start_datetime,
                "duration": event.duration_minutes,
                "link": f"{settings.BASE_URL}{event.get_absolute_url()}",  # o waiting room
            }
            html_message = render_to_string(
                "ve_invitations/email/reminder.html", context
            )
            plain_message = f"Recordatorio: El evento {event.title} comienza en 1 hora."

            send_mail(
                subject=f"Recordatorio: {event.title} comienza pronto",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(all_emails),
                html_message=html_message,
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Recordatorios enviados para {event.title} a {len(all_emails)} destinatarios"
                )
            )
