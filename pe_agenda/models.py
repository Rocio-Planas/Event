from django.db import models
from in_person_events.models import Event
from django.utils import timezone


class Activity(models.Model):
    """
    Modelo para gestionar las actividades de un evento presencial.
    Cada actividad pertenece a un evento específico.
    """
    
    class Status(models.TextChoices):
        PROGRAMADA = 'programada', 'Programada'
        EN_CURSO = 'en_curso', 'En Curso'
        COMPLETADA = 'completada', 'Completada'
        CANCELADA = 'cancelada', 'Cancelada'
    
    # Relación con el evento
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="Evento"
    )
    
    # Información básica de la actividad
    title = models.CharField(
        max_length=200,
        verbose_name="Título de la Actividad"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )
    
    # Horario
    start_time = models.DateTimeField(
        verbose_name="Hora de Inicio"
    )
    end_time = models.DateTimeField(
        verbose_name="Hora de Finalización"
    )
    
    # Ubicación/Zona
    location = models.CharField(
        max_length=255,
        verbose_name="Zona/Ubicación"
    )
    
    # Ponente/Responsable
    speaker_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nombre del Ponente"
    )
    speaker_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email del Ponente"
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROGRAMADA,
        verbose_name="Estado"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['event', 'start_time']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.event.title}"
    
    def get_duration(self):
        """Retorna la duración de la actividad en minutos"""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    def is_ongoing(self):
        """Verifica si la actividad está en curso"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    def get_availability_percentage(self):
        """Retorna el porcentaje de disponibilidad"""
        if self.capacity == 0:
            return 0
        return int((self.attendees_count / self.capacity) * 100)
