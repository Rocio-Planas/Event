from django.contrib import admin
from django.utils import timezone
from .models import StaffInvitation, StaffMember


@admin.register(StaffInvitation)
class StaffInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'event', 'user_type', 'role', 'status', 'sent_at', 'accepted_at')
    list_filter = ('status', 'user_type', 'role', 'event')
    search_fields = ('email', 'event__title')
    readonly_fields = ('token', 'sent_at', 'accepted_at', 'expires_at')
    ordering = ('-sent_at',)
    actions = ['accept_invitations', 'reject_invitations']

    fieldsets = (
        (None, {
            'fields': ('event', 'email', 'user_type', 'role')
        }),
        ('État de l\'invitation', {
            'fields': ('status', 'token', 'sent_at', 'accepted_at', 'expires_at')
        }),
    )

    def accept_invitations(self, request, queryset):
        from .models import InvitationStatus
        updated = 0
        for invitation in queryset:
            invitation.status = InvitationStatus.ACEPTADA
            invitation.accepted_at = timezone.now()
            invitation.save()
            updated += 1
        self.message_user(request, f'{updated} invitation(s) accepted.')
    accept_invitations.short_description = 'Accept selected invitations'

    def reject_invitations(self, request, queryset):
        from .models import InvitationStatus
        updated = queryset.update(status=InvitationStatus.RECHAZADA)
        self.message_user(request, f'{updated} invitation(s) rejected.')
    reject_invitations.short_description = 'Reject selected invitations'


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'user_type', 'role', 'zone', 'assigned_at')
    list_filter = ('user_type', 'role', 'zone', 'event')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'event__title')
    readonly_fields = ('assigned_at',)
    ordering = ('-assigned_at',)
    actions = ['remove_from_team']

    fieldsets = (
        (None, {
            'fields': ('event', 'user', 'user_type', 'role')
        }),
        ('Zone', {
            'fields': ('zone', 'assigned_at')
        }),
    )

    def remove_from_team(self, request, queryset):
        updated = queryset.count()
        queryset.delete()
        self.message_user(request, f'{updated} member(s) removed from team.')
    remove_from_team.short_description = 'Remove selected members from team'