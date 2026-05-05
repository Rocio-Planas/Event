from in_person_events.models import Event
from django.db import models
from django.conf import settings
from django.utils import timezone


class TicketType(models.Model):
    """
    Tabla para definir los tipos de entrada disponibles en la creación.
    """
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='ticket_types'
    )
    name = models.CharField(max_length=100, verbose_name='Nombre del Ticket')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    quantity_available = models.PositiveIntegerField(verbose_name='Cantidad Disponible', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.event.title}"


class Registration(models.Model):
    """
    Inscripciones de usuarios a eventos.
    """
    class Status(models.TextChoices):
        CONFIRMADA = 'confirmada', 'Confirmada'
        PENDIENTE = 'pendiente', 'Pendiente'
        CANCELADA = 'cancelada', 'Cancelada'

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Evento'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Usuario'
    )
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registrations',
        verbose_name='Tipo de Ticket'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMADA,
        verbose_name='Estado'
    )
    registration_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Inscripción'
    )
    payment_status = models.CharField(
        max_length=20,
        default='pendiente',
        verbose_name='Estado del Pago'
    )
    notes = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        ordering = ['-registration_date']
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.email} - {self.event.title}"


class EventWaitlist(models.Model):
    """
    Lista de espera para eventos llenos.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='waitlist_entries',
        verbose_name='Usuario'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='waitlist',
        verbose_name='Evento'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Entrada')

    class Meta:
        verbose_name = 'Lista de Espera'
        verbose_name_plural = 'Lista de Espera'
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'user'],
                name='unique_waitlist_per_event'
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.event.title} (Lista de Espera)"