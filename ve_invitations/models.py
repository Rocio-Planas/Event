from django.db import models
from virtualEvent.models import VirtualEvent
from django.conf import settings

class Invitation(models.Model):
    """Invitaciones para eventos privados."""

    event = models.ForeignKey(
        VirtualEvent, on_delete=models.CASCADE, related_name="invitations"
    )
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)  
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invitación para {self.email} a {self.event.title}"


class EventFollower(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followed_events",
    )
    event = models.ForeignKey(
        VirtualEvent, on_delete=models.CASCADE, related_name="followers"
    )
    followed_at = models.DateTimeField(auto_now_add=True)
    receive_reminders = models.BooleanField(default=True) 

    class Meta:
        unique_together = ("user", "event") 

    def __str__(self):
        return f"{self.user.email} sigue {self.event.title}"
