from django.db import models
from django.conf import settings
from django.utils import timezone

class Conversacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversaciones')
    ultimo_mensaje = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-ultimo_mensaje']

    def __str__(self):
        return f"Conversación con {self.usuario.email}"
    
    def tiene_mensajes_no_leidos(self):
        """Devuelve True si hay mensajes no leídos por el admin en esta conversación."""
        return self.mensajes.filter(leido_por_admin=False, remitente=self.usuario).exists()

class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    remitente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    leido = models.BooleanField(default=False)
    leido_por_admin = models.BooleanField(default=False)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f"{self.remitente.email}: {self.texto[:30]}"