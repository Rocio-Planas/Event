from django.contrib import admin
from .models import VirtualEvent


class VirtualEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'unique_link', 'created_by', 'start_datetime')
    readonly_fields = ('unique_link',)  # Solo lectura, no editable
    fields = ('title', 'description', 'created_by', 'start_datetime', 'duration_minutes', 'settings')
    # 'unique_link' no va en fields, solo en readonly_fields


admin.site.register(VirtualEvent, VirtualEventAdmin)
