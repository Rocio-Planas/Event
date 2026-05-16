from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from pe_surveys.models import Survey
from pe_registration.models import Registration
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send scheduled surveys that are due'

    def handle(self, *args, **options):
        surveys = Survey.objects.filter(
            delivery_type='programado',
            scheduled_date__lte=timezone.now(),
            is_active=True,
            sent_at__isnull=True
        )
        
        sent_count = 0
        
        for survey in surveys:
            try:
                # Build survey link
                try:
                    site = Site.objects.get_current()
                    survey_link = f"{site.domain}/encuestas/{survey.event_id}/responder/{survey.pk}/"
                except Exception:
                    survey_link = f"{settings.BASE_URL}/encuestas/{survey.event_id}/responder/{survey.pk}/"
                
                # Get confirmed registrations
                registrations = Registration.objects.filter(
                    event_id=survey.event_id,
                    status=Registration.Status.CONFIRMADA
                ).select_related('user')
                
                emails_sent = 0
                for reg in registrations:
                    if reg.user and reg.user.email:
                        try:
                            send_mail(
                                subject=f"Encuesta: {survey.title}",
                                message=f"Por favor, responde la encuesta '{survey.title}'.\nSigue este enlace: {survey_link}\nGracias por tu participación.",
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[reg.user.email],
                                fail_silently=False,
                            )
                            emails_sent += 1
                        except Exception as e:
                            logger.error(f"Error sending email to {reg.user.email}: {e}")
                
                # Update sent_at
                survey.sent_at = timezone.now()
                survey.save(update_fields=['sent_at'])
                
                self.stdout.write(f'Sent survey {survey.id} ({survey.title}) - {emails_sent} emails')
                sent_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error sending survey {survey.id}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Processed {surveys.count()} scheduled surveys, sent {sent_count}'))