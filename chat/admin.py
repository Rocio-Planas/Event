from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Conversacion, Mensaje

User = get_user_model()

class MensajeInline(admin.TabularInline):
    model = Mensaje
    extra = 1
    fields = ('remitente', 'texto', 'fecha', 'leido')
    readonly_fields = ('fecha',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Restringir el campo 'remitente' a solo usuarios con is_staff=True
        if db_field.name == 'remitente':
            kwargs['queryset'] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ultimo_mensaje')
    search_fields = ('usuario__email', 'usuario__first_name', 'usuario__last_name')
    inlines = [MensajeInline]

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('conversacion', 'remitente', 'texto_preview', 'fecha', 'leido')
    list_filter = ('leido', 'fecha')
    search_fields = ('conversacion__usuario__email', 'texto')
    raw_id_fields = ('conversacion', 'remitente')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # También aquí restringimos el remitente a solo staff
        if db_field.name == 'remitente':
            kwargs['queryset'] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def texto_preview(self, obj):
        return obj.texto[:50] + ('...' if len(obj.texto) > 50 else '')
    texto_preview.short_description = 'Mensaje'