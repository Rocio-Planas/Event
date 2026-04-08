from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PreferenciaUsuario
from core.models import Suscripcion   # importar el modelo de suscripción

class PreferenciaUsuarioInline(admin.TabularInline):
    model = PreferenciaUsuario
    extra = 1
    autocomplete_fields = ['categoria']

# Inline para mostrar suscripciones del usuario
class SuscripcionInline(admin.TabularInline):
    model = Suscripcion
    extra = 0
    fields = ('evento_id', 'titulo_evento', 'tipo_evento', 'fecha_evento', 'fecha_suscripcion')
    readonly_fields = ('fecha_suscripcion',)
    can_delete = True
    show_change_link = True

class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'rol', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff', 'sexo')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'telefono', 'avatar', 'fecha_nacimiento', 'sexo', 'direccion', 'biografia')}),
        ('Roles y permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Redes sociales', {'fields': ('website', 'twitter', 'instagram', 'linkedin')}),
        ('Estadísticas', {'fields': ('eventos_asistidos', 'eventos_organizados')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
        ('Preferencias de notificación', {'fields': ('recibir_notificaciones', 'recibir_newsletter')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'rol'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')
    inlines = [PreferenciaUsuarioInline, SuscripcionInline]   # agregamos el inline de suscripciones

admin.site.register(Usuario, UsuarioAdmin)

@admin.register(PreferenciaUsuario)
class PreferenciaUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'categoria', 'fecha_seleccion')
    list_filter = ('categoria', 'fecha_seleccion')
    search_fields = ('usuario__email', 'categoria__nombre')