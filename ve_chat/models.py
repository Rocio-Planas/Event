from django.db import models
from django.conf import settings
from ve_streaming.models import StreamingRoom


class ChatMessage(models.Model):
    room = models.ForeignKey(
        StreamingRoom, on_delete=models.CASCADE, related_name="messages"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    anonymous = models.BooleanField(default=False)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)
    moderated = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        nombre = self.user.email if self.user and not self.anonymous else "Anónimo"
        return f"{nombre}: {self.content[:30]}"


class HandRaise(models.Model):
    room = models.ForeignKey(
        StreamingRoom, on_delete=models.CASCADE, related_name="hands"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ["room", "user"]


class Poll(models.Model):
    room = models.ForeignKey(
        StreamingRoom, on_delete=models.CASCADE, related_name="polls"
    )
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=100)


class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )  # Ya no permite nulos
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "poll",
            "user",
        ]  # Un usuario solo puede votar una vez por encuesta


class SatisfactionRating(models.Model):
    room = models.ForeignKey(
        StreamingRoom, on_delete=models.CASCADE, related_name="satisfaction_ratings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    rating = models.IntegerField()  # 1 a 5
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
