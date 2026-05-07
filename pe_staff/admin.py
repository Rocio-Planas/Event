from django.contrib import admin
from django.utils import timezone
from django import forms
from django.apps import apps
from .models import StaffInvitation, StaffMember


class StaffMemberAdminForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        event = None
        
        if self.instance and self.instance.pk:
            try:
                event = self.instance.event
            except Exception:
                pass
        
        if not event:
            event_id = self.initial.get('event')
            if event_id:
                try:
                    from in_person_events.models import Event
                    event = Event.objects.get(id=event_id)
                except Exception:
                    pass
        
        # Cargar actividades para ponentes
        if 'activity' in self.fields:
            try:
                Activity = apps.get_model('pe_agenda', 'Activity')
                self.fields['activity'].queryset = Activity.objects.filter(event=event)
            except Exception:
                self.fields['activity'].queryset = []
        
        # Cargar zonas para staff
        if 'zone' in self.fields:
            if event:
                all_zones = []
                
                # Intentar desde pe_stand
                try:
                    from pe_stand.models import Stand
                    stands = Stand.objects.filter(event=event).values_list('name', flat=True)
                    all_zones = list(stands)
                except Exception:
                    pass
                
                # Desde StaffMember existentes
                try:
                    existing_zones = StaffMember.objects.filter(
                        event=event, 
                        zone__isnull=False
                    ).exclude(zone='').values_list('zone', flat=True)
                    for z in existing_zones:
                        if z and z not in all_zones:
                            all_zones.append(z)
                except Exception:
                    pass
                
                all_zones = sorted(set(all_zones))
                if all_zones:
                    choices = [(z, z) for z in all_zones]
                    choices.insert(0, ('', '--- Seleccionar Zona ---'))
                else:
                    choices = [('', '--- No hay zonas disponibles ---')]
            else:
                choices = [('', '--- Seleccione un evento primero ---')]
            
            self.fields['zone'].choices = choices


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
    form = StaffMemberAdminForm
    list_display = ('user', 'event', 'user_type', 'role', 'zone', 'activity', 'assigned_at')
    list_filter = ('user_type', 'role', 'zone', 'event')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'event__title')
    readonly_fields = ('assigned_at',)
    ordering = ('-assigned_at',)
    actions = ['remove_from_team']

    fieldsets = (
        (None, {
            'fields': ('event', 'user', 'user_type')
        }),
        ('Staff - Zona Asignada', {
            'fields': ('zone', 'role'),
            'classes': ('staff_fields',),
        }),
        ('Ponente - Actividad Asignada', {
            'fields': ('activity',),
            'classes': ('ponente_fields',),
        }),
        ('Información', {
            'fields': ('assigned_at',)
        }),
    )

    class Media:
        js = ('pe_staff/admin.js',)

    def get_fieldsets(self, request, obj=None):
        if obj:
            if obj.user_type == 'ponente':
                return (
                    (None, {
                        'fields': ('event', 'user', 'user_type')
                    }),
                    ('Ponente - Actividad Asignada', {
                        'fields': ('activity',),
                    }),
                    ('Información', {
                        'fields': ('assigned_at',)
                    }),
                )
            else:
                return (
                    (None, {
                        'fields': ('event', 'user', 'user_type')
                    }),
                    ('Staff - Zona Asignada', {
                        'fields': ('zone', 'role'),
                    }),
                    ('Información', {
                        'fields': ('assigned_at',)
                    }),
                )
        return super().get_fieldsets(request, obj)

    def remove_from_team(self, request, queryset):
        updated = queryset.count()
        queryset.delete()
        self.message_user(request, f'{updated} member(s) removed from team.')
    remove_from_team.short_description = 'Remove selected members from team'