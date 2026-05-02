from django.db import models
from django.core.exceptions import ValidationError


class Survey(models.Model):
    """
    Encuesta para eventos presenciales.
    """
    class DeliveryType(models.TextChoices):
        INMEDIATO = 'inmediato', 'Inmediato'
        FECHA_ESPECIFICA = 'fecha_especifica', 'Fecha Específica'

    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descripción', blank=True)
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
        if self.delivery_type == self.DeliveryType.FECHA_ESPECIFICA and not self.scheduled_date:
            raise ValidationError({'scheduled_date': 'La fecha programada es requerida paraenvíos programados.'})

    def send(self):
        """
        Lógica para enviar la encuesta a los participantes.
        """
        from pe_registration.models import Registration
        from pe_communication.models import EmailTemplate
        from django.utils import timezone
        
        registrations = Registration.objects.filter(
            event_id=1,
            status=Registration.Status.CONFIRMADA
        ).select_related('user')
        
        emails_sent = 0
        for reg in registrations:
            pass
        
        return emails_sent


class Question(models.Model):
    """
    Pregunta dentro de una encuesta.
    """
    class QuestionType(models.TextChoices):
        TEXTO = 'texto', 'Texto'
        ESCALA = 'escala', 'Escala 1-5'
        OPCION_MULTIPLE = 'opcion_multiple', 'Opción Múltiple'

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Encuesta'
    )
    text = models.CharField('Pregunta', max_length=500)
    is_required = models.BooleanField('Requerida', default=False)
    question_type = models.CharField(
        'Tipo de Pregunta',
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.TEXTO
    )
    options = models.JSONField('Opciones', default=list, blank=True)
    order = models.PositiveIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        ordering = ['order']

    def __str__(self):
        return f"{self.survey.title} - {self.text[:50]}"


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
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Pregunta'
    )
    answer = models.TextField('Respuesta')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
        ordering = ['-created_at']

    def __str__(self):
        return f"Usuario {self.user_id} - {self.survey.title}"