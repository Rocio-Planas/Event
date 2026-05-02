from django.db import models
from django.conf import settings


class EmailTemplate(models.Model):
    """
    Plantillas de email predefinidas.
    """
    class TemplateType(models.TextChoices):
        STAFF_INVITATION = 'staff_invitation', 'Invitación de Staff'
        STAFF_ACCEPTED = 'staff_accepted', 'Confirmación de Aceptación'
        STAFF_ASSIGNED = 'staff_assigned', 'Asignación de Zona'
        EVENT_INVITATION = 'event_invitation', 'Invitación de Evento'
        EVENT_CONFIRMATION = 'event_confirmation', 'Confirmación de Evento'
        EVENT_REMINDER = 'event_reminder', 'Recordatorio de Evento'

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre de Plantilla'
    )
    template_type = models.CharField(
        max_length=50,
        choices=TemplateType.choices,
        verbose_name='Tipo'
    )
    subject = models.CharField(
        max_length=200,
        verbose_name='Asunto'
    )
    body_html = models.TextField(
        verbose_name='Cuerpo HTML'
    )
    body_text = models.TextField(
        verbose_name='Cuerpo Texto Plano'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )

    class Meta:
        verbose_name = 'Plantilla de Email'
        verbose_name_plural = 'Plantillas de Email'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.template_type})"


class EmailLog(models.Model):
    """
    Registro de emails enviados.
    """
    class Status(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        ENVIADO = 'enviado', 'Enviado'
        FALLIDO = 'fallido', 'Fallido'

    recipient = models.EmailField(
        verbose_name='Destinatario'
    )
    subject = models.CharField(
        max_length=200,
        verbose_name='Asunto'
    )
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
        verbose_name='Plantilla Usada'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDIENTE,
        verbose_name='Estado'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Envío'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Registro de Email'
        verbose_name_plural = 'Registros de Email'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient} - {self.subject[:50]} ({self.status})"


class Notification(models.Model):
    """
    Modelo para almacenar notificaciones del sistema.
    """
    class Type(models.TextChoices):
        MANUAL_ALERT = 'manual_alert', 'Alerta Manual'
        SUBSCRIPTION = 'subscription', 'Suscripción'
        AGENDA_CHANGE = 'agenda_change', 'Cambio en Agenda'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Usuario'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name='Remitente'
    )
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensaje')
    notification_type = models.CharField(
        'Tipo',
        max_length=20,
        choices=Type.choices,
        default=Type.MANUAL_ALERT
    )
    is_read = models.BooleanField('Leída', default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        sender_name = self.sender.get_full_name() if self.sender else "Sistema"
        return f"{self.user.email} - {sender_name}: {self.title[:30]}"