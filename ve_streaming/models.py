from django.db import models
from virtualEvent.models import VirtualEvent


# Create your models here.
class StreamingRoom(models.Model):
    event = models.OneToOneField(VirtualEvent, on_delete=models.CASCADE, related_name='streaming_room')
    is_active = models.BooleanField(default=False)
    # No necesitas access_link, usaremos event.unique_link
    # Pero puedes mantenerlo si quieres, pero lo mejor es usar el unique_link del evento

    def __str__(self):
        return f"Sala de {self.event.title}"
