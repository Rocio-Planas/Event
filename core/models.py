from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class CategoriaEvento(models.Model):
    nombre = models.CharField(_('nombre'), max_length=100, unique=True)
    descripcion = models.TextField(_('descripción'), blank=True)
    icono = models.CharField(_('icono'), max_length=50, default='bi-calendar')
    color = models.CharField(_('color'), max_length=7, default='#4861A2')
    activo = models.BooleanField(_('activo'), default=True)
    orden = models.PositiveIntegerField(_('orden'), default=0)

    class Meta:
        verbose_name = _('Categoría de Evento')
        verbose_name_plural = _('Categorías de Eventos')
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

class Suscripcion(models.Model):
    TIPO_EVENTO = (
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suscripciones')
    evento_id = models.PositiveIntegerField(help_text="ID del evento en el sistema de la compañera")
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO, default='presencial')
    titulo_evento = models.CharField(max_length=200, blank=True)
    fecha_evento = models.DateTimeField(null=True, blank=True)
    imagen_evento = models.URLField(blank=True)
    fecha_suscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'evento_id', 'tipo_evento')
        ordering = ['-fecha_suscripcion']

    def __str__(self):
        return f"{self.usuario.email} -> {self.titulo_evento} (ID:{self.evento_id})"

class Resena(models.Model):
    CALIFICACION_CHOICES = [(i, str(i)) for i in range(1, 6)]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resenas')
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    evento_id = models.PositiveIntegerField(help_text="ID del evento (del sistema de compañeras)")
    evento_titulo = models.CharField(max_length=200, blank=True)
    calificacion = models.IntegerField(choices=CALIFICACION_CHOICES)
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.evento_titulo} ({self.calificacion}★)"

class Consulta(models.Model):
    TIPO_CONSULTA = (
        ('consulta', 'Consulta general'),
        ('soporte', 'Soporte técnico'),
        ('sugerencia', 'Sugerencia'),
        ('otro', 'Otro'),
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultas')
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    tipo = models.CharField(max_length=20, choices=TIPO_CONSULTA, default='consulta')
    evento_id = models.PositiveIntegerField(null=True, blank=True, help_text="ID del evento relacionado (opcional)")
    evento_titulo = models.CharField(max_length=200, blank=True)
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    respondido = models.BooleanField(default=False)
    respuesta = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.asunto} - {self.nombre}"