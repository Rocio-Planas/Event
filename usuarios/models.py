from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from datetime import date

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('rol', 'administrador')  # superusuario es administrador
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractUser):
    username = None
    email = models.EmailField('Email', unique=True)

    ROLES = (
        ('administrador', 'Administrador'),
        ('organizador', 'Organizador'),
        ('expositor', 'Expositor'),
        ('espectador', 'Espectador'),
    )

    SEXOS = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no decirlo'),
    )

    rol = models.CharField('Rol', max_length=20, choices=ROLES, default='espectador')
    telefono = models.CharField('Teléfono', max_length=15, blank=True)
    avatar = avatar = models.ImageField('Avatar', upload_to='avatars/', blank=True, null=True, default=None)
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    sexo = models.CharField('Sexo', max_length=1, choices=SEXOS, blank=True, null=True)
    direccion = models.TextField('Dirección', blank=True)
    biografia = models.TextField('Biografía', blank=True, max_length=500)
    website = models.URLField('Sitio Web', blank=True)
    twitter = models.CharField('Twitter', max_length=50, blank=True)
    instagram = models.CharField('Instagram', max_length=50, blank=True)
    linkedin = models.URLField('LinkedIn', blank=True)

    eventos_asistidos = models.PositiveIntegerField('Eventos Asistidos', default=0)
    eventos_organizados = models.PositiveIntegerField('Eventos Organizados', default=0)

    preferencias = models.ManyToManyField('core.CategoriaEvento', through='PreferenciaUsuario', blank=True, related_name='usuarios_prefieren')

    recibir_notificaciones = models.BooleanField('Recibir Notificaciones', default=True)
    recibir_newsletter = models.BooleanField('Recibir Newsletter', default=True)

    ultima_actividad = models.DateTimeField('Última Actividad', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UsuarioManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def get_edad(self):
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None

    def get_eventos_presenciales(self):
        # Placeholder para integrar con apps de compañeras
        return []

    def get_eventos_virtuales(self):
        return []


class PreferenciaUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    categoria = models.ForeignKey('core.CategoriaEvento', on_delete=models.CASCADE)
    fecha_seleccion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'categoria')
        verbose_name = 'Preferencia de Usuario'
        verbose_name_plural = 'Preferencias de Usuarios'

    def __str__(self):
        return f"{self.usuario.email} prefiere {self.categoria.nombre}"