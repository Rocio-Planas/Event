from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class Survey(models.Model):
    """
    Encuesta para eventos presenciales.
    """
    class SurveyType(models.TextChoices):
        ESCALA = 'escala', 'Escala 1-5'
        TEXTO = 'texto', 'Texto con Opciones'

    class DeliveryType(models.TextChoices):
        INMEDIATO = 'inmediato', 'Inmediato'
        PROGRAMADO = 'programado', 'Programado'

    event = models.ForeignKey(
        'in_person_events.Event',
        on_delete=models.CASCADE,
        related_name='surveys',
        verbose_name='Evento'
    )
    title = models.CharField('Título', max_length=200)
    survey_type = models.CharField(
        'Tipo de Encuesta',
        max_length=20,
        choices=SurveyType.choices,
        default=SurveyType.ESCALA
    )
    is_multiple_choice = models.BooleanField('Permitir Múltiples Opciones', default=False)
    is_active = models.BooleanField('Activa', default=True)
    delivery_type = models.CharField(
        'Tipo de Entrega',
        max_length=20,
        choices=DeliveryType.choices,
        default=DeliveryType.INMEDIATO
    )
    scheduled_date = models.DateTimeField('Fecha Programada', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Encuesta'
        verbose_name_plural = 'Encuestas'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        if self.delivery_type == self.DeliveryType.PROGRAMADO and not self.scheduled_date:
            raise ValidationError({'scheduled_date': 'La fecha programada es requerida para envíos programados.'})

    def send_survey_emails(self):
        """
        Envía emails de la encuesta a todos los asistentes confirmados.
        """
        from pe_registration.models import Registration
        from pe_communication.models import EmailTemplate
        from django.core.mail import send_mail
        from django.conf import settings
        
        registrations = Registration.objects.filter(
            event_id=1,  # Asumiendo event_id fijo, ajustar según contexto
            status=Registration.Status.CONFIRMADA
        ).select_related('user')
        
        emails_sent = 0
        for reg in registrations:
            # Lógica de envío de email
            # Usar EmailTemplate o send_mail
            send_mail(
                subject=f"Encuesta: {self.title}",
                message=f"Por favor, responde la encuesta: {self.title}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reg.user.email],
                fail_silently=False,
            )
            emails_sent += 1
        
        return emails_sent

    def should_send(self):
        """Check if survey should be sent based on delivery_type and scheduled_date."""
        if self.delivery_type == self.DeliveryType.INMEDIATO:
            return True
        if self.delivery_type == 'programado' and self.scheduled_date:
            from django.utils import timezone
            return self.scheduled_date <= timezone.now()
        return False


@receiver(post_save, sender=Survey)
def send_immediate_survey(sender, instance, created, **kwargs):
    if created and instance.delivery_type == Survey.DeliveryType.INMEDIATO:
        instance.send_survey_emails()


@receiver(post_save, sender=Survey)
def check_scheduled_survey(sender, instance, created, **kwargs):
    if not created and instance.delivery_type == 'programado' and instance.scheduled_date:
        from django.utils import timezone
        if instance.scheduled_date <= timezone.now():
            instance.send_survey_emails()


class SurveyOption(models.Model):
    """
    Opciones para encuestas de tipo TEXTO.
    """
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='Encuesta'
    )
    text = models.CharField('Opción', max_length=200)

    class Meta:
        verbose_name = 'Opción de Encuesta'
        verbose_name_plural = 'Opciones de Encuesta'

    def __str__(self):
        return f"{self.survey.title} - {self.text}"


class Response(models.Model):
    """
    Respuesta de un usuario a una encuesta.
    """
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Encuesta'
    )
    user_id = models.IntegerField('ID del Usuario')
    answer = models.JSONField('Respuesta')  # Para múltiples opciones si aplica
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
        ordering = ['-created_at']

    def __str__(self):
        return f"Usuario {self.user_id} - {self.survey.title}"