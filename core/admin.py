from django.contrib import admin
from .models import CategoriaEvento, Suscripcion, Resena, Consulta

@admin.register(CategoriaEvento)
class CategoriaEventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'orden', 'icono', 'color')
    list_editable = ('activo', 'orden')
    search_fields = ('nombre',)
    list_filter = ('activo',)
    ordering = ('orden', 'nombre')

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'titulo_evento', 'tipo_evento', 'fecha_evento', 'fecha_suscripcion')
    list_filter = ('tipo_evento', 'fecha_suscripcion')
    search_fields = ('usuario__email', 'usuario__first_name', 'usuario__last_name', 'titulo_evento')
    raw_id_fields = ('usuario',)
    readonly_fields = ('fecha_suscripcion',)

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'evento', 'calificacion', 'aprobada', 'fecha_creacion')
    list_filter = ('calificacion', 'aprobada', 'fecha_creacion')
    search_fields = ('nombre', 'email', 'evento__title', 'comentario')
    raw_id_fields = ('evento',)
    actions = ['aprobar_resenas']

    def aprobar_resenas(self, request, queryset):
        queryset.update(aprobada=True)
    aprobar_resenas.short_description = "Aprobar reseñas seleccionadas"

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('asunto', 'nombre', 'email', 'tipo', 'fecha_creacion', 'leido', 'respondido')
    list_filter = ('tipo', 'leido', 'respondido', 'fecha_creacion')
    search_fields = ('nombre', 'email', 'asunto', 'mensaje')
    readonly_fields = ('fecha_creacion',)