from django.db import models
from django.conf import settings

# from datetime import timedelta
import uuid


class VirtualEvent(models.Model):
    PRIVACY_CHOICES = [
        ("public", "Público"),
        ("private", "Privado (por invitación)"),
    ]

    PREDEFINED_CATEGORIES = [
        ("Seminario", "Seminario"),
        ("Conferencia", "Conferencia"),
        ("Taller", "Taller"),
    ]

    title = models.CharField(max_length=200, verbose_name="Nombre del evento")
    description = models.TextField(verbose_name="Descripción")
    category = models.CharField(max_length=100, verbose_name="Categoría")
    custom_category = models.CharField(
        max_length=100, blank=True, verbose_name="Categoría personalizada"
    )
    image = models.ImageField(
        upload_to="event_images/", blank=True, null=True, verbose_name="Imagen"
    )
    start_datetime = models.DateTimeField(verbose_name="Fecha y hora de inicio")
    duration_minutes = models.PositiveIntegerField(
        default=60, verbose_name="Duración (minutos)"
    )
    privacy = models.CharField(
        max_length=10,
        choices=PRIVACY_CHOICES,
        default="public",
        verbose_name="Privacidad",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="virtual_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    settings = models.JSONField(default=dict, blank=True)
    materials = models.JSONField(default=dict, blank=True, verbose_name="Material post-evento")

    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente de aprobación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado de aprobación"
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de aprobación")

    def aprobar(self):
        """Aprueba el evento, guarda fecha y envía notificación (señal)."""
        from django.utils import timezone
        self.estado = 'aprobado'
        self.fecha_aprobacion = timezone.now()
        self.save()

    def rechazar(self):
        """Rechaza el evento."""
        self.estado = 'rechazado'
        self.save()


    # Enlace único para acceso (para RF-04)
    unique_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ["-start_datetime"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("virtualEvents:event_detail", args=[self.pk])


class EventAnalytics(models.Model):
    """Métricas acumuladas de un evento (actualizadas por señales)."""

    event = models.OneToOneField(
        VirtualEvent, on_delete=models.CASCADE, related_name="analytics"
    )
    total_messages = models.PositiveIntegerField(default=0)
    total_hands = models.PositiveIntegerField(default=0)
    total_poll_votes = models.PositiveIntegerField(default=0)
    unique_viewers = models.PositiveIntegerField(default=0)
    average_watch_time = models.FloatField(
        default=0.0, help_text="Minutos promedio por espectador"
    )
    average_satisfaction = models.FloatField(default=0.0, help_text="Promedio de 1 a 5")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics: {self.event.title}"


class OnlineViewer(models.Model):
    """Espectador activo (heartbeat)."""

    event = models.ForeignKey(
        VirtualEvent, on_delete=models.CASCADE, related_name="online_viewers"
    )
    session_key = models.CharField(max_length=40, db_index=True)
    ip_address = models.GenericIPAddressField()
    last_heartbeat = models.DateTimeField(auto_now=True)
    entered_at = models.DateTimeField(
        auto_now_add=True
    )  # para calcular tiempo de visualización

    class Meta:
        unique_together = ("event", "session_key")


class EventView(models.Model):
    """Registro de visita única (para contar espectadores únicos)."""

    event = models.ForeignKey(
        VirtualEvent, on_delete=models.CASCADE, related_name="views"
    )
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "session_key")
