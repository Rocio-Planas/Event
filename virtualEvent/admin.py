from django.contrib import admin
from .models import VirtualEvent, EventAnalytics, OnlineViewer, EventView
from django.contrib import messages

def aprobar_eventos(modeladmin, request, queryset):
    for event in queryset:
        event.aprobar()
    messages.success(request, f'{queryset.count()} evento(s) aprobado(s).')
aprobar_eventos.short_description = "Aprobar eventos seleccionados"

def rechazar_eventos(modeladmin, request, queryset):
    for event in queryset:
        event.rechazar()
    messages.success(request, f'{queryset.count()} evento(s) rechazado(s).')
rechazar_eventos.short_description = "Rechazar eventos seleccionados"

@admin.register(VirtualEvent)
class VirtualEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'start_datetime', 'estado')
    list_filter = ('estado', 'created_by')
    search_fields = ('title', 'created_by__email')
    actions = [aprobar_eventos, rechazar_eventos]

# Registro de otros modelos (sin decorador, solo una vez)
admin.site.register(EventAnalytics)
admin.site.register(OnlineViewer)
admin.site.register(EventView)