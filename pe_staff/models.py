from django.db import models
from django.conf import settings
import uuid


class StaffRole(models.TextChoices):
    LIDER_ZONA = 'LIDER_ZONA', 'Líder de Zona'
    SOPORTE = 'SOPORTE', 'Soporte Técnico'
    RECEPCION = 'RECEPCION', 'Recepción'
    SEGURIDAD = 'SEGURIDAD', 'Seguridad'
    MONTAJE = 'MONTAJE', 'Montaje'
    CATERING = 'CATERING', 'Catering'
    ATENCION = 'ATENCION', 'Atención al Público'


class InvitationStatus(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    ACEPTADA = 'aceptada', 'Aceptada'
    RECHAZADA = 'rechazada', 'Rechazada'


class StaffInvitation(models.Model):
    """
    Invitaciones para unirse al equipo de un evento.
    """
    class UserType(models.TextChoices):
        PONENTE = 'ponente', 'Ponente'
        STAFF = 'staff', 'Staff'

    event = models.ForeignKey(
        'in_person_events.Event',
        on_delete=models.CASCADE,
        related_name='staff_invitations',
        verbose_name='Evento'
    )
    email = models.EmailField(
        verbose_name='Correo Electrónico'
    )
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.STAFF,
        verbose_name='Tipo de Usuario'
    )
    role = models.CharField(
        max_length=50,
        choices=StaffRole.choices,
        null=True,
        blank=True,
        verbose_name='Rol (solo para Staff)'
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name='Token de Invitación'
    )
    status = models.CharField(
        max_length=20,
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDIENTE,
        verbose_name='Estado'
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Envío'
    )
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Aceptación'
    )
    expires_at = models.DateTimeField(
        verbose_name='Fecha de Expiración'
    )

    class Meta:
        verbose_name = 'Invitación de Staff'
        verbose_name_plural = 'Invitaciones de Staff'
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.email} - {self.event.title} ({self.role})"

    def generate_token(self):
        """Genera un nuevo token."""
        self.token = uuid.uuid4()
        self.save()


class StaffMember(models.Model):
    """
    Miembros del equipo de un evento.
    """
    event = models.ForeignKey(
        'in_person_events.Event',
        on_delete=models.CASCADE,
        related_name='staff_members',
        verbose_name='Evento'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_events',
        verbose_name='Usuario'
    )
    role = models.CharField(
        max_length=50,
        choices=StaffRole.choices,
        verbose_name='Rol'
    )
    zone = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Zona Asignada'
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Asignación'
    )

    class Meta:
        verbose_name = 'Miembro del Staff'
        verbose_name_plural = 'Miembros del Staff'
        ordering = ['role', 'zone']
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} - {self.event.title} ({self.role})"