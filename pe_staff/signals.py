from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StaffInvitation, StaffMember, InvitationStatus


@receiver(post_save, sender=StaffInvitation)
def create_staff_member_on_accept(sender, instance, created, **kwargs):
    """Crea el miembro del staff cuando una invitación pasa a aceptada."""
    if instance.status != InvitationStatus.ACEPTADA:
        return

    User = get_user_model()
    try:
        user = User.objects.get(email__iexact=instance.email)
    except User.DoesNotExist:
        return

    role_value = instance.role
    if instance.user_type == 'ponente':
        role_value = 'ponente'

    if role_value is None and instance.user_type == 'ponente':
        role_value = 'ponente'

    StaffMember.objects.update_or_create(
        event=instance.event,
        user=user,
        defaults={
            'role': role_value,
            'user_type': instance.user_type,
            'zone': '',
        }
    )
