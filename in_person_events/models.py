import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class Event(models.Model):
    # Opciones para el estado del evento (RF-01)
    class Status(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        PENDIENTE = 'pendiente', 'Pendiente Aprobación'
        APROBADO = 'aprobado', 'Aprobado'
        EN_CURSO = 'en_curso', 'En Curso'
        FINALIZADO = 'finalizado', 'Finalizado'
        CANCELADO = 'cancelado', 'Cancelado'

    # Opciones de visibilidad
    class Visibility(models.TextChoices):
        PUBLICO = 'publico', 'Público'
        PRIVADO = 'privado', 'Privado'

    # Campos principales
    title = models.CharField(max_length=200, verbose_name="Título del Evento")
    slug = models.SlugField(blank=True)
    description = models.TextField(verbose_name="Descripción")
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='organized_events',
        verbose_name="Organizador"
    )

    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDIENTE,
        verbose_name="Estado"
    )
    category = models.CharField(max_length=100, verbose_name="Categoría")
    visibility = models.CharField(
        max_length=10, 
        choices=Visibility.choices, 
        default=Visibility.PUBLICO
    )

    location = models.CharField(max_length=255, verbose_name="Ubicación/Dirección")
    capacity = models.PositiveIntegerField(verbose_name="Capacidad Máxima")
    start_date = models.DateTimeField(verbose_name="Fecha de Inicio")
    end_date = models.DateTimeField(verbose_name="Fecha de Fin")
    image = models.ImageField(upload_to='events/banners/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    show_attendee_count = models.BooleanField(default=False, verbose_name="Mostrar recuento de asistentes")

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-start_date']

    def __str__(self):
        return self.title
    
    # No edita si está finalizado
    def can_be_edited(self):
        return self.status != self.Status.FINALIZADO


class EventStateHistory(models.Model):
    """
    Tabla para auditoría: rastrea quién cambió el estado y cuándo.
    Útil para el reporte post-evento (RF-12).
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='state_history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    change_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Historial de Estado"
        verbose_name_plural = "Historiales de Estados"


class EventResource(models.Model):
    """Archivos digitales asociados a un evento para asistentes."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255, blank=True, verbose_name="Título del Recurso")
    file = models.FileField(upload_to='event_resources/', verbose_name="Archivo")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de subida")

    class Meta:
        verbose_name = "Recurso de Evento"
        verbose_name_plural = "Recursos de Evento"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or self.file.name.split('/')[-1]