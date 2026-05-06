from django.contrib import admin
from .models import TicketType, Registration, EventWaitlist


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'price', 'quantity_available']
    list_filter = ['event']
    search_fields = ['name']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'ticket_type', 'status', 'registration_date']
    list_filter = ['event', 'status']
    search_fields = ['user__username', 'user__email', 'event__title']
    raw_id_fields = ['user']
    fields = ['user', 'event', 'ticket_type', 'status', 'registration_date']


@admin.register(EventWaitlist)
class EventWaitlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'created_at']
    list_filter = ['event']
    search_fields = ['user__username', 'user__email', 'event__title']
    raw_id_fields = ['user', 'event']