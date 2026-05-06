from django.db import models
from django.conf import settings
from in_person_events.models import Event
from django.db.models import Sum


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
    
    def get_leaders(self):
        """Retorna los nombres de los líderes separados por coma."""
        # Filtrar por rol de líder (acepta ambos valores: LIDER_ZONA o Líder de Zona)
        leaders = self.staff.filter(role__in=['LIDER_ZONA', 'Líder de Zona']).select_related('user')
        if not leaders.exists():
            return None
        names = []
        for s in leaders:
            if s.user:
                name = s.user.get_full_name()
                if not name:
                    name = s.user.email
                if name:
                    names.append(name)
        if not names:
            return None
        return ', '.join(names)
    
    def get_resource_count(self):
        """Retorna la cantidad total de recursos asignados."""
        from django.apps import apps
        try:
            StandAssignment = apps.get_model('pe_inventory', 'StandAssignment')
            return StandAssignment.objects.filter(stand=self).aggregate(
                total=Sum('quantity')
            )['total'] or 0
        except:
            return 0


class StandStaff(models.Model):
    """
    Modelo para representar el personal asignado a un stand.
    """
    stand = models.ForeignKey(
        Stand,
        on_delete=models.CASCADE,
        related_name='staff',
        verbose_name='Stand'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stand_staff',
        null=True,
        blank=True,
        verbose_name='Usuario'
    )
    role = models.CharField(
        max_length=50,
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