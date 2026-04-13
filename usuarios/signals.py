# usuarios/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def auto_set_admin_role(sender, instance, **kwargs):
    """
    Si el usuario es staff o superusuario, su rol se convierte en 'administrador'.
    Si se le quitan esos permisos, su rol vuelve a 'espectador' (opcional).
    """
    updated = False
    
    # Si es staff o superusuario, forzar rol = administrador
    if instance.is_staff or instance.is_superuser:
        if instance.rol != 'administrador':
            instance.rol = 'administrador'
            updated = True
    else:
        # Opcional: si no es staff y su rol era administrador, cambiarlo a espectador
        # (comenta esta parte si no quieres que se modifique automáticamente)
        if instance.rol == 'administrador':
            instance.rol = 'espectador'
            updated = True
    
    if updated:
        # Guardar sin entrar en un bucle infinito (evitamos llamar a save() de nuevo con señal)
        instance.save(update_fields=['rol'])