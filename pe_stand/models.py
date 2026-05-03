from django.db import models
from in_person_events.models import Event


class Stand(models.Model):
    """
    Modelo para representar un stand en un evento.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='stands',
        verbose_name='Evento',
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre del Stand'
    )
    location = models.CharField(
        max_length=200,
        verbose_name='Ubicación'
    )
    capacity = models.PositiveIntegerField(
        verbose_name='Capacidad'
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
        verbose_name = 'Stand'
        verbose_name_plural = 'Stands'
        ordering = ['name']

    def __str__(self):
        return self.name


class StandStaff(models.Model):
    """
    Modelo para representar el personal asignado a un stand.
    """
    class Role(models.TextChoices):
        LIDER = 'Líder de Stand', 'Líder de Stand'
        ESPECIALISTA_IT = 'Especialista IT', 'Especialista IT'
        SOPORTE = 'Soporte Técnico', 'Soporte Técnico'
        RECEPCION = 'Recepción', 'Recepción'
        OTRO = 'Otro', 'Otro'

    stand = models.ForeignKey(
        Stand,
        on_delete=models.CASCADE,
        related_name='staff',
        verbose_name='Stand'
    )
    # Referencia genérica a la app de usuarios (aún no existe)
    user_id = models.PositiveIntegerField(
        verbose_name='ID de Usuario'
    )
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        verbose_name='Rol'
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Asignación'
    )

    class Meta:
        verbose_name = 'Personal de Stand'
        verbose_name_plural = 'Personal de Stands'
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.stand.name} - {self.role}"


class StandActivity(models.Model):
    """
    Modelo para representar las actividades programadas en un stand.
    """
    stand = models.ForeignKey(
        Stand,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name='Stand'
    )
    # Referencia genérica a la app de actividades (aún no existe)
    activity_id = models.PositiveIntegerField(
        verbose_name='ID de Actividad'
    )
    scheduled_time = models.DateTimeField(
        verbose_name='Hora Programada'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Actividad de Stand'
        verbose_name_plural = 'Actividades de Stands'
        ordering = ['scheduled_time']

    def __str__(self):
        return f"{self.stand.name} - {self.scheduled_time}"