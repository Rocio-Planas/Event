from django.core.management.base import BaseCommand
from django.utils import timezone
from pe_surveys.models import Survey


class Command(BaseCommand):
    help = 'Send scheduled surveys that are due'

    def handle(self, *args, **options):
        surveys = Survey.objects.filter(
            delivery_type='programado',
            scheduled_date__lte=timezone.now(),
            is_active=True
        )
        
        for survey in surveys:
            try:
                emails = survey.send_survey_emails()
                self.stdout.write(f'Sent survey {survey.id} ({survey.title}) - {emails} emails')
            except Exception as e:
                self.stdout.write(f'Error sending survey {survey.id}: {e}')
        
        self.stdout.write(self.style.SUCCESS(f'Processed {surveys.count()} scheduled surveys'))