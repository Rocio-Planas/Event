from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from virtualEvent.models import VirtualEvent
from ve_invitations.models import EventFollower, Invitation


class Command(BaseCommand):
    help = "Envía recordatorios de eventos virtuales que comienzan en 1 hora"

    def handle(self, *args, **options):
        now = timezone.now()
        inicio = now + timezone.timedelta(minutes=55)
        fin = now + timezone.timedelta(minutes=65)
        events = VirtualEvent.objects.filter(
            start_datetime__gte=inicio, start_datetime__lte=fin
        )

        for event in events:
            emails = set()
            for f in EventFollower.objects.filter(event=event, receive_reminders=True):
                emails.add(f.user.email)
            for inv in Invitation.objects.filter(event=event):
                emails.add(inv.email)

            if not emails:
                self.stdout.write(f"No hay destinatarios para {event.title}")
                continue

            # 🔥 Construir el enlace de la misma forma que el dashboard (pero sin request)
            # Primero obtenemos la ruta relativa: /streaming/sala/<uuid>/
            relative_path = reverse(
                "ve_streaming:waiting_room", args=[event.unique_link]
            )
            # Luego la combinamos con BASE_URL (asegúrate de que BASE_URL no tenga barra al final)
            base = settings.BASE_URL.rstrip("/")
            link = f"{base}{relative_path}"

            # Verificación: imprime el enlace en la consola para que lo copies si quieres
            self.stdout.write(
                f"\n🔗 Enviando recordatorio para {event.title}: {link}\n"
            )

            context = {"event": event, "link": link}
            subject = f"Recordatorio: {event.title} comienza pronto"
            html_message = render_to_string(
                "ve_invitations/email/reminder.html", context
            )
            plain_message = (
                f"El evento {event.title} comienza en 1 hora. Accede: {link}"
            )
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                list(emails),
                html_message=html_message,
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Recordatorios enviados para {event.title} a {len(emails)} destinatarios"
                )
            )
