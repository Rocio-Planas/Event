from django.contrib import admin
from .models import Event, EventStateHistory


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin personalizado para gestionar Eventos (RF-01)
    Permite a los administradores revisar y aprobar eventos
    """
    list_display = ('title', 'organizer', 'status', 'start_date', 'capacity', 'created_at')
    list_filter = ('status', 'visibility', 'category', 'created_at')
    search_fields = ('title', 'description', 'organizer__email')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'slug', 'description', 'category', 'organizer')
        }),
        ('Ubicación y Capacidad', {
            'fields': ('location', 'capacity')
        }),
        ('Fechas y Horarios', {
            'fields': ('start_date', 'end_date')
        }),
        ('Configuración', {
            'fields': ('status', 'visibility', 'image', 'is_active')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_events', 'reject_events', 'mark_as_active', 'mark_as_inactive']
    
    def approve_events(self, request, queryset):
        """Acción para aprobar eventos seleccionados"""
        updated = 0
        for event in queryset:
            if event.status == Event.Status.PENDIENTE:
                event.status = Event.Status.APROBADO
                event.save()
                # Registrar en el historial
                EventStateHistory.objects.create(
                    event=event,
                    old_status=Event.Status.PENDIENTE,
                    new_status=Event.Status.APROBADO,
                    changed_by=request.user,
                    notes="Aprobado por administrador"
                )
                updated += 1
        self.message_user(request, f"{updated} evento(s) aprobado(s) exitosamente")
    approve_events.short_description = "Aprobar eventos seleccionados"
    
    def reject_events(self, request, queryset):
        """Acción para rechazar (cancelar) eventos seleccionados"""
        updated = 0
        for event in queryset:
            if event.status != Event.Status.FINALIZADO:
                old_status = event.status
                event.status = Event.Status.CANCELADO
                event.save()
                EventStateHistory.objects.create(
                    event=event,
                    old_status=old_status,
                    new_status=Event.Status.CANCELADO,
                    changed_by=request.user,
                    notes="Cancelado por administrador"
                )
                updated += 1
        self.message_user(request, f"{updated} evento(s) cancelado(s)")
    reject_events.short_description = "Cancelar eventos seleccionados"
    
    def mark_as_active(self, request, queryset):
        """Activar eventos"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} evento(s) activado(s)")
    mark_as_active.short_description = "Activar eventos seleccionados"
    
    def mark_as_inactive(self, request, queryset):
        """Desactivar eventos"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} evento(s) desactivado(s)")
    mark_as_inactive.short_description = "Desactivar eventos seleccionados"


@admin.register(EventStateHistory)
class EventStateHistoryAdmin(admin.ModelAdmin):
    """
    Admin para ver el historial de cambios de estado de eventos (RF-12)
    Solo lectura para auditoría
    """
    list_display = ('event', 'old_status', 'new_status', 'changed_by', 'change_date')
    list_filter = ('new_status', 'change_date')
    search_fields = ('event__title', 'changed_by__email')
    readonly_fields = ('event', 'old_status', 'new_status', 'changed_by', 'change_date', 'notes')
    
    def has_add_permission(self, request):
        """No permitir agregar manualmente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar (es auditoría)"""
        return False
