import json
import logging
from datetime import timedelta
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from django.apps import apps

from .models import StaffInvitation, StaffMember, StaffRole, InvitationStatus
from pe_communication.views import send_staff_invitation_email, send_staff_confirmation_email, send_zone_assignment_email

logger = logging.getLogger(__name__)
User = get_user_model()


@method_decorator(login_required, name='dispatch')
class StaffDashboardView(TemplateView):
    """Dashboard principal del staff."""
    template_name = 'pe_staff/staff.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get('event_id')
        
        # Obtener el evento
        from in_person_events.models import Event
        event = get_object_or_404(Event, id=event_id)
        
        # Obtener miembro del equipo
        members = StaffMember.objects.filter(event_id=event_id).select_related('user')
        invitations = StaffInvitation.objects.filter(event_id=event_id)
        
        # Calcular estadísticas
        total_members = members.count()
        active_members = members.exclude(zone__isnull=True).count()
        pending_invitations = invitations.filter(status=InvitationStatus.PENDIENTE).count()
        
        # Agrupar por rol
        members_by_role = {}
        for member in members:
            role = member.role
            if role not in members_by_role:
                members_by_role[role] = []
            members_by_role[role].append({
                'id': member.id,
                'name': member.user.get_full_name() or member.user.email,
                'email': member.user.email,
                'zone': member.zone,
                'assigned_at': member.assigned_at.isoformat() if member.assigned_at else None,
            })
        
        # Agrupar por zona
        members_by_zone = {}
        for member in members:
            zone = member.zone or 'Sin asignar'
            if zone not in members_by_zone:
                members_by_zone[zone] = []
            members_by_zone[zone].append({
                'id': member.id,
                'name': member.user.get_full_name() or member.user.email,
                'role': member.role,
            })
        
        members_values = list(members.values(
            'id', 'user__email', 'user__first_name', 'user__last_name',
            'role', 'zone', 'assigned_at'
        ))
        invitations_values = list(invitations.values(
            'id', 'email', 'role', 'status', 'sent_at', 'accepted_at'
        ))

        for member_data in members_values:
            assigned_at = member_data.get('assigned_at')
            member_data['assigned_at'] = assigned_at.isoformat() if assigned_at else None

        for invitation_data in invitations_values:
            sent_at = invitation_data.get('sent_at')
            accepted_at = invitation_data.get('accepted_at')
            invitation_data['sent_at'] = sent_at.isoformat() if sent_at else None
            invitation_data['accepted_at'] = accepted_at.isoformat() if accepted_at else None

        context['members_json'] = json.dumps(members_values)
        context['invitations_json'] = json.dumps(invitations_values)
        context['members'] = members
        context['invitations'] = invitations
        context['pending_invitations_list'] = invitations.filter(status=InvitationStatus.PENDIENTE).order_by('-sent_at')
        context['total_members'] = total_members
        context['active_members'] = active_members
        context['pending_invitations'] = pending_invitations
        context['members_by_role'] = members_by_role
        context['members_by_zone'] = members_by_zone
        context['event_id'] = event_id
        context['event'] = event
        context['active_page'] = 'equipo'
        
        return context


@method_decorator(login_required, name='dispatch')
class ZoneDetailView(TemplateView):
    """Detalle de una zona específica."""
    template_name = 'pe_staff/zone_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get('event_id')
        zone_name = self.kwargs.get('zone_name')
        
        members = StaffMember.objects.filter(
            event_id=event_id,
            zone=zone_name
        ).select_related('user')
        
        # Obtener actividades de la zona (desde pe_agenda)
        try:
            Activity = apps.get_model('pe_agenda', 'Activity')
            activities = Activity.objects.filter(
                event_id=event_id,
                location__icontains=zone_name
            )
        except ImportError:
            activities = []
        
        context['zone_name'] = zone_name
        context['members'] = members
        context['activities'] = activities
        context['event_id'] = event_id
        context['active_page'] = 'equipo'
        
        return context


@login_required
def invite_staff(request, event_id):
    """Invita a un usuario al equipo."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        user_type = data.get('user_type', 'staff')
        role = data.get('role')
        
        if not email or not user_type:
            return JsonResponse({'error': 'Email y tipo de usuario requeridos'}, status=400)
        
        # Verificar que el email está registrado
        if not User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'El correo no está registrado en la plataforma'}, status=400)
        
        # Verificar que no sea già miembro (solo para staff)
        if user_type == 'staff' and StaffMember.objects.filter(event_id=event_id, user__email=email).exists():
            return JsonResponse({'error': 'El usuario ya es miembro del equipo'}, status=400)
        
        # Verificar invitación pendiente
        if StaffInvitation.objects.filter(event_id=event_id, email=email, status=InvitationStatus.PENDIENTE).exists():
            return JsonResponse({'error': 'Ya existe una invitación pendiente para este correo'}, status=400)
        
        # Crear invitación
        expiration = timezone.now() + timedelta(days=7)
        invitation = StaffInvitation.objects.create(
            event_id=event_id,
            email=email,
            user_type=user_type,
            role=role if user_type == 'staff' else None,
            expires_at=expiration,
        )
        
        # Enviar email
        send_staff_invitation_email(invitation)
        
        return JsonResponse({
            'success': True,
            'message': 'Invitación enviada correctamente',
            'invitation': {
                'id': invitation.id,
                'email': invitation.email,
                'user_type': invitation.user_type,
                'role': invitation.role,
                'status': invitation.status,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        logger.error(f'Error al invitar staff: {e}')
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_invitations(request, event_id):
    """Obtiene las invitaciones de un evento."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    invitations = StaffInvitation.objects.filter(event_id=event_id)
    data = list(invitations.values('id', 'email', 'role', 'status', 'sent_at', 'accepted_at', 'expires_at'))
    
    return JsonResponse({'success': True, 'invitations': data})


@login_required
def cancel_invitation(request, event_id, invitation_id):
    """Cancela una invitación."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    invitation = get_object_or_404(StaffInvitation, id=invitation_id, event_id=event_id)
    invitation.status = InvitationStatus.RECHAZADA
    invitation.save()
    
    return JsonResponse({'success': True, 'message': 'Invitación cancelada'})


@login_required
def accept_invitation(request, token):
    """Acepta una invitación (público)."""
    invitation = get_object_or_404(StaffInvitation, token=token, status=InvitationStatus.PENDIENTE)
    
    if invitation.expires_at < timezone.now():
        return render(request, 'pe_staff/invitation_expired.html', {'invitation': invitation})
    
    if request.user.is_authenticated:
        # Verificar que el email coincide
        if request.user.email.lower() != invitation.email.lower():
            return JsonResponse({'error': 'El correo no coincide con la invitación'}, status=400)
        
        # Crear miembro
        member, created = StaffMember.objects.get_or_create(
            event=invitation.event,
            user=request.user,
            defaults={'role': invitation.role}
        )
        
        if created:
            invitation.status = InvitationStatus.ACEPTADA
            invitation.accepted_at = timezone.now()
            invitation.save()
            
            # Enviar confirmación
            send_staff_confirmation_email(member)
            
            return JsonResponse({
                'success': True,
                'message': '¡Bienvenido al equipo!',
                'member': {
                    'id': member.id,
                    'role': member.role,
                }
            })
        else:
            return JsonResponse({'error': 'Ya eres miembro del equipo'}, status=400)
    else:
        return redirect(f'/usuarios/login/?next=/pe_staff/accept/{token}/')


@login_required
def get_members(request, event_id):
    """Obtiene los miembros del equipo."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    members = StaffMember.objects.filter(event_id=event_id).select_related('user')
    data = list(members.values(
        'id', 'user__email', 'user__first_name', 'user__last_name',
        'role', 'zone', 'assigned_at'
    ))
    
    return JsonResponse({'success': True, 'members': data})


@login_required
def assign_zone(request, event_id, member_id):
    """Asigna una zona a un miembro."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    member = get_object_or_404(StaffMember, id=member_id, event_id=event_id)
    
    try:
        data = json.loads(request.body)
        zone_name = data.get('zone', '').strip()
        
        if not zone_name:
            return JsonResponse({'error': 'Nombre de zona requerido'}, status=400)
        
        member.zone = zone_name
        member.save()
        
        # Enviar email de notificación
        send_zone_assignment_email(member, zone_name)
        
        return JsonResponse({
            'success': True,
            'message': f'Zona "{zone_name}" asignada correctamente',
            'member': {
                'id': member.id,
                'zone': member.zone,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)


@login_required
def remove_member(request, event_id, member_id):
    """Elimina un miembro del equipo."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    member = get_object_or_404(StaffMember, id=member_id, event_id=event_id)
    member.delete()
    
    return JsonResponse({'success': True, 'message': 'Miembro eliminado del equipo'})