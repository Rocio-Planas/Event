from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """
    Admin personalizado para gestionar actividades de eventos presenciales
    """
    list_display = (
        'title',
        'event',
        'start_time',
        'end_time',
        'location',
        'speaker_name',
        'status',
    )
    
    list_filter = (
        'event',
        'status',
        'location',
        'created_at',
    )
    
    search_fields = (
        'title',
        'description',
        'speaker_name',
        'location'
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('event', 'title', 'description')
        }),
        ('Horario', {
            'fields': ('start_time', 'end_time')
        }),
        ('Ubicación', {
            'fields': ('location',)
        }),
        ('Ponente/Responsable', {
            'fields': ('speaker_name', 'speaker_email')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_completed', 'mark_as_cancelled', 'mark_as_ongoing']
    
    def mark_as_completed(self, request, queryset):
        """Marcar actividades como completadas"""
        updated = queryset.update(status=Activity.Status.COMPLETADA)
        self.message_user(request, f'{updated} actividad(es) marcada(s) como completada(s)')
    mark_as_completed.short_description = "Marcar como Completada"
    
    def mark_as_cancelled(self, request, queryset):
        """Marcar actividades como canceladas"""
        updated = queryset.update(status=Activity.Status.CANCELADA)
        self.message_user(request, f'{updated} actividad(es) cancelada(s)')
    mark_as_cancelled.short_description = "Marcar como Cancelada"
    
    def mark_as_ongoing(self, request, queryset):
        """Marcar actividades como en curso"""
        updated = queryset.update(status=Activity.Status.EN_CURSO)
        self.message_user(request, f'{updated} actividad(es) en curso')
    mark_as_ongoing.short_description = "Marcar como En Curso"
