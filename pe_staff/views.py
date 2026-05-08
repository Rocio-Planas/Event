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
        member_emails = [m.user.email for m in members]
        accepted_without_user = invitations.filter(status=InvitationStatus.ACEPTADA).exclude(email__in=member_emails)
        
        # Confirmados: members (con usuario) + aceptados sin usuario
        confirmed = members.count() + accepted_without_user.count()
        # Pendientes: invitaciones pendientes
        pending = invitations.filter(status=InvitationStatus.PENDIENTE).count()
        # Total miembros = confirmados + pendientes
        total_members = confirmed + pending
        active_members = confirmed
        pending_invitations = pending
        
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
            'role', 'zone', 'assigned_at', 'user__telefono', 'user_type'
        ))
        invitations_values = list(invitations.values(
            'id', 'email', 'role', 'status', 'sent_at', 'accepted_at'
        ))
        
        # Obtener actividades del evento para ponentes
        try:
            Activity = apps.get_model('pe_agenda', 'Activity')
            activities = list(Activity.objects.filter(
                event_id=event_id
            ).values('id', 'title', 'start_time', 'end_time', 'location'))
            for activity in activities:
                start = activity.get('start_time')
                end = activity.get('end_time')
                activity['start_time'] = start.isoformat() if start else None
                activity['end_time'] = end.isoformat() if end else None
        except LookupError:
            activities = []
        
        context['activities_json'] = json.dumps(activities)
        
        for member_data in members_values:
            assigned_at = member_data.get('assigned_at')
            member_data['assigned_at'] = assigned_at.isoformat() if assigned_at else None
            member_data['phone'] = member_data.get('user__telefono', '')

        for invitation_data in invitations_values:
            sent_at = invitation_data.get('sent_at')
            accepted_at = invitation_data.get('accepted_at')
            invitation_data['sent_at'] = sent_at.isoformat() if sent_at else None
            invitation_data['accepted_at'] = accepted_at.isoformat() if accepted_at else None

        context['members_json'] = json.dumps(members_values)
        context['invitations_json'] = json.dumps(invitations_values)
        context['activities_json'] = json.dumps(activities)
        context['members'] = members
        context['invitations'] = invitations
        context['pending_invitations_list'] = invitations.filter(status=InvitationStatus.PENDIENTE).order_by('-sent_at')
        context['accepted_invitations_list'] = invitations.filter(status=InvitationStatus.ACEPTADA).order_by('-accepted_at')
        context['rejected_invitations_list'] = invitations.filter(status=InvitationStatus.RECHAZADA).order_by('-sent_at')

        member_emails = [m.user.email for m in members]
        accepted_without_user = context['accepted_invitations_list'].exclude(email__in=member_emails)

        user_names = {
            user.email: user.get_full_name() or user.email
            for user in User.objects.filter(email__in=[inv.email for inv in accepted_without_user])
        }
        context['accepted_invitations_with_name'] = [
            {
                'id': inv.id,
                'email': inv.email,
                'full_name': user_names.get(inv.email, inv.email),
                'role': inv.role,
                'status': inv.status,
                'sent_at': inv.sent_at,
                'accepted_at': inv.accepted_at,
                'user_type': inv.user_type,
                'phone': None,
            }
            for inv in accepted_without_user
        ]

        context['total_members'] = total_members
        context['active_members'] = active_members
        context['pending_invitations'] = pending_invitations
        context['members_by_role'] = members_by_role
        context['members_by_zone'] = members_by_zone
        context['statuses'] = ['pendiente', 'rechazado', 'confirmado']
        context['event_id'] = event_id
        context['event'] = event
        context['active_page'] = 'equipo'
        
        return context


@method_decorator(login_required, name='dispatch')
class StaffDashboardReadOnlyView(TemplateView):
    """Dashboard de solo lectura para staff - vista del miembro del equipo."""
    template_name = 'pe_staff/dashboard_staff.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get('event_id')
        
        from in_person_events.models import Event
        event = get_object_or_404(Event, id=event_id)
        
        my_assignment = get_object_or_404(
            StaffMember,
            event_id=event_id,
            user=self.request.user
        )
        
        try:
            Activity = apps.get_model('pe_agenda', 'Activity')
            activities = Activity.objects.filter(
                event_id=event_id
            ).order_by('start_time')

            if my_assignment.user_type == StaffMember.UserType.PONENTE and not my_assignment.activity:
                fallback_activity = Activity.objects.filter(
                    event_id=event_id,
                    speaker_email__iexact=self.request.user.email
                ).order_by('start_time').first()
                if not fallback_activity:
                    fallback_activity = Activity.objects.filter(
                        event_id=event_id,
                        speaker_name__iexact=self.request.user.get_full_name() or self.request.user.email
                    ).order_by('start_time').first()
                if fallback_activity:
                    my_assignment.activity = fallback_activity
        except LookupError:
            activities = []
        
        zone_stand = None
        if my_assignment.zone:
            try:
                Stand = apps.get_model('pe_stand', 'Stand')
                zone_stand = Stand.objects.filter(
                    event_id=event_id,
                    name=my_assignment.zone
                ).first()
            except LookupError:
                pass
        
        context['event'] = event
        context['event_id'] = event_id
        context['my_assignment'] = my_assignment
        context['activities'] = activities
        context['zone_stand'] = zone_stand
        
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
        
        # Verificar que no sea già miembro del equipo (cualquier tipo)
        if StaffMember.objects.filter(event_id=event_id, user__email=email).exists():
            return JsonResponse({'error': 'El usuario ya es miembro del equipo'}, status=400)
        
        # Verificar invitación pendiente o aceptada (no invitar dos veces)
        if StaffInvitation.objects.filter(event_id=event_id, email=email, status__in=[InvitationStatus.PENDIENTE, InvitationStatus.ACEPTADA]).exists():
            return JsonResponse({'error': 'Ya existe una invitación activa para este correo'}, status=400)
        
        # Crear invitación
        expiration = timezone.now() + timedelta(days=7)
        invitation = StaffInvitation.objects.create(
            event_id=event_id,
            email=email,
            user_type=user_type,
            role=role if user_type == 'staff' else None,
            expires_at=expiration,
        )
        
        # Enviar correo de invitación directamente
        try:
            from django.conf import settings
            site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
            accept_url = f"{site_url}/equipo/accept/{invitation.token}/"
            
            if user_type == 'ponente':
                role_text = 'Ponente'
            elif role:
                role_text = role
            else:
                role_text = 'Staff'
            
            from django.core.mail import send_mail
            send_mail(
                subject=f'Invitación como {role_text} - {invitation.event.title}',
                message=f'Hola,\n\n'
                       f'Has sido invitado a participar como {role_text} en el evento "{invitation.event.title}".\n\n'
                       f'Fecha: {invitation.event.start_date}\n\n'
                       f'Para confirmar tu participación, visita el siguiente enlace:\n'
                       f'{accept_url}\n\n'
                       f'El equipo de EventPulse',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f'Email de invitación enviado a {email}')
        except Exception as e:
            logger.error(f'Error al enviar email de invitación: {e}')
        
        return JsonResponse({
            'success': True,
            'message': 'Invitación enviada correctamente',
            'invitation': {
                'id': invitation.id,
                'email': invitation.email,
                'user_type': invitation.user_type,
                'role': invitation.role,
                'status': invitation.status,
                'token': str(invitation.token),
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
    """Cancela una invitación (pasar a rechazada)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    invitation = get_object_or_404(StaffInvitation, id=invitation_id, event_id=event_id)
    invitation.status = InvitationStatus.RECHAZADA
    invitation.save()
    
    return JsonResponse({'success': True, 'message': 'Invitación cancelada'})


@login_required
def delete_invitation(request, event_id, invitation_id):
    """Elimina una invitación de la base de datos."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    invitation = get_object_or_404(StaffInvitation, id=invitation_id, event_id=event_id)
    invitation.delete()
    
    return JsonResponse({'success': True, 'message': 'Invitación eliminada'})


@login_required
def accept_invitation(request, token):
    """Acepta una invitación (público)."""
    logger.info(f"Buscando invitación con token: {token}")
    print(f"DEBUG: Buscando token = {token}")
    
    try:
        invitation = StaffInvitation.objects.get(token=token)
        logger.info(f"Invitación encontrada: {invitation.id}, status: {invitation.status}, email: {invitation.email}")
        print(f"DEBUG: Invitación encontrada - ID: {invitation.id}, Status: {invitation.status}")
    except StaffInvitation.DoesNotExist:
        print(f"DEBUG: Token no encontrado, mostrando error")
        print(f"DEBUG: Buscando en base de datos...")
        from django.db import connection
        print(f"DEBUG: Total invitaciones: {StaffInvitation.objects.count()}")
        for inv in StaffInvitation.objects.all()[:5]:
            print(f"  - ID: {inv.id}, Token: {inv.token}, Email: {inv.email}, Status: {inv.status}")
        
        logger.warning(f"No se encontró invitación con token: {token}")
        return render(request, 'pe_staff/invitation_invalid.html', {'error': 'Invitación no encontrada. Puede que ya haya sido procesada o el enlace haya expirado.'})
    
    if invitation.status == InvitationStatus.ACEPTADA:
        logger.info(f"Invitación ya aceptada, redirigiendo al dashboard: {invitation.event_id}")
        return redirect('pe_staff:dashboard_staff', event_id=invitation.event_id)
    
    if invitation.status == InvitationStatus.RECHAZADA:
        return render(request, 'pe_staff/invitation_invalid.html', {'error': 'Invitación rechazada'})
    
    if invitation.expires_at < timezone.now():
        return render(request, 'pe_staff/invitation_expired.html', {'invitation': invitation})
    
    if request.user.is_authenticated:
        if request.user.email.lower() != invitation.email.lower():
            return render(request, 'pe_staff/invitation_invalid_email.html', {
                'invitation': invitation,
                'user_email': request.user.email
            })
        
        member, created = StaffMember.objects.get_or_create(
            event=invitation.event,
            user=request.user,
            defaults={
                'role': invitation.role,
                'user_type': invitation.user_type
            }
        )
        
        if created:
            invitation.status = InvitationStatus.ACEPTADA
            invitation.accepted_at = timezone.now()
            invitation.save()
            
            send_staff_confirmation_email(member)
            
            return redirect('pe_staff:dashboard_staff', event_id=invitation.event_id)
        else:
            return redirect('pe_staff:dashboard_staff', event_id=invitation.event_id)
    else:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=invitation.email)
            if user:
                return redirect(f'/usuarios/login/?next=/pe_staff/accept/{token}/')
        except User.DoesNotExist:
            pass
        return render(request, 'pe_staff/invitation_login_required.html', {'invitation': invitation})


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


def get_event_stands(request, event_id):
    """Obtiene los stands/zonas disponibles del evento (API)."""
    try:
        from pe_stand.models import Stand
        from in_person_events.models import Event
        
        logger.info(f"Solicitando stands para evento {event_id}")
        
        event = get_object_or_404(Event, id=event_id)
        stands = Stand.objects.filter(event=event).values('id', 'name', 'location', 'capacity')
        
        logger.info(f"Stands encontrados: {len(list(stands))}")
        
        return JsonResponse({
            'success': True,
            'stands': list(stands)
        })
    except Exception as e:
        logger.error(f"Error en get_event_stands: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def assign_zone(request, event_id, member_id):
    """Asigna una zona a un miembro."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    member = get_object_or_404(StaffMember, id=member_id, event_id=event_id)
    
    try:
        from pe_stand.models import Stand, StandStaff
        
        data = json.loads(request.body)
        stand_id = data.get('stand_id')
        
        if not stand_id:
            return JsonResponse({'error': 'ID de stand requerido'}, status=400)
        
        # Validar que el stand existe y pertenece al mismo evento
        stand = get_object_or_404(Stand, id=stand_id, event_id=event_id)
        
        # Guardar el nombre del stand en el campo zone (para mantener compatibilidad)
        member.zone = stand.name
        member.save()
        
        # Also create StandStaff entry if not already assigned
        if not StandStaff.objects.filter(stand=stand, user=member.user).exists():
            stand_staff = StandStaff(
                stand=stand,
                user=member.user,
                role=member.role
            )
            stand_staff.save()
        
        # Enviar notificación y email al staff
        try:
            from pe_communication.models import Notification
            from django.conf import settings
            from django.core.mail import send_mail
            
            Notification.objects.create(
                user=member.user,
                title=f'Zona asignada: {stand.name}',
                message=f'Se te ha asignado la zona "{stand.name}" en el evento "{member.event.title}".',
                notification_type=Notification.Type.MANUAL_ALERT
            )
            
            send_mail(
                subject=f'Zona asignada - {member.event.title}',
                message=f'Hola {member.user.get_full_name() or member.user.email},\n\n'
                       f'Se te ha asignado la zona "{stand.name}" en el evento "{member.event.title}".\n\n'
                       f'El equipo de EventPulse',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member.user.email],
                fail_silently=False,
            )
            logger.info(f'Notificación de zona enviada a {member.user.email}')
        except Exception as e:
            logger.error(f'Error al enviar notificación de zona: {e}')
        
        return JsonResponse({
            'success': True,
            'message': f'Zona "{stand.name}" asignada correctamente',
            'member': {
                'id': member.id,
                'zone': member.zone,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def assign_activity(request, event_id, member_id):
    """Asigna una actividad a un ponente."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    member = get_object_or_404(StaffMember, id=member_id, event_id=event_id)
    
    if member.user_type != StaffMember.UserType.PONENTE:
        return JsonResponse({'error': 'Solo los ponentes pueden tener actividades asignadas'}, status=400)
    
    try:
        Activity = apps.get_model('pe_agenda', 'Activity')
        
        data = json.loads(request.body)
        activity_id = data.get('activity_id')
        
        # Si activity_id es None o vacío, desasignar
        if not activity_id:
            if member.activity:
                # Limpiar el speaker de la actividad anterior
                member.activity.speaker_name = None
                member.activity.speaker_email = None
                member.activity.save(update_fields=['speaker_name', 'speaker_email'])
            member.activity = None
            member.save(update_fields=['activity'])
            return JsonResponse({
                'success': True,
                'message': 'Actividad desasignada correctamente',
                'member': {
                    'id': member.id,
                    'activity': None,
                    'zone': member.zone,
                }
            })
        
        try:
            activity_id = int(activity_id)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'ID de actividad inválido'}, status=400)
        
        activity = get_object_or_404(Activity, id=activity_id, event_id=event_id)
        
        # Si hay una actividad anterior diferente, limpiar su speaker
        if member.activity and member.activity != activity:
            member.activity.speaker_name = None
            member.activity.speaker_email = None
            member.activity.save(update_fields=['speaker_name', 'speaker_email'])
        
        # Asignar la nueva actividad
        member.activity = activity
        member.save(update_fields=['activity'])
        
        # Actualizar el speaker de la actividad
        activity.speaker_name = member.user.get_full_name() or member.user.email
        activity.speaker_email = member.user.email
        activity.save(update_fields=['speaker_name', 'speaker_email'])
        
        # Enviar notificación y email al ponente
        try:
            from pe_communication.models import Notification
            from django.conf import settings
            from django.core.mail import send_mail
            
            Notification.objects.create(
                user=member.user,
                title=f'Actividad asignada: {activity.title}',
                message=f'Se te ha asignado la actividad "{activity.title}" en el evento "{member.event.title}". '
                        f'Horario: {activity.start_time.strftime("%d/%m/%Y %H:%M")} - {activity.end_time.strftime("%H:%M")}.',
                notification_type=Notification.Type.MANUAL_ALERT
            )
            
            send_mail(
                subject=f'Actividad asignada - {activity.title}',
                message=f'Hola {member.user.get_full_name() or member.user.email},\n\n'
                       f'Se te ha asignado la actividad "{activity.title}" en el evento "{member.event.title}".\n'
                       f'Horario: {activity.start_time.strftime("%d/%m/%Y %H:%M")} - {activity.end_time.strftime("%H:%M")}\n\n'
                       f'El equipo de EventPulse',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member.user.email],
                fail_silently=False,
            )
            logger.info(f'Notificación de asignación de actividad enviada a {member.user.email}')
        except Exception as e:
            logger.error(f'Error al enviar notificación de actividad: {e}')
        
        return JsonResponse({
            'success': True,
            'message': f'Actividad "{activity.title}" asignada correctamente',
            'member': {
                'id': member.id,
                'activity': activity.title,
                'zone': member.zone,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        logger.error(f"Error assigning activity: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def send_message_to_organizer(request, event_id):
    """Envía un mensaje al organizador del evento."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    from in_person_events.models import Event
    event = get_object_or_404(Event, id=event_id)
    
    # Verificar que el usuario sea staff del evento
    if not StaffMember.objects.filter(event=event, user=request.user).exists():
        return JsonResponse({'error': 'No tienes permisos para enviar mensajes en este evento'}, status=403)
    
    message = request.POST.get('message', '').strip()
    if not message:
        return JsonResponse({'error': 'El mensaje no puede estar vacío'}, status=400)
    
    # Crear notificación
    Notification = apps.get_model('pe_communication', 'Notification')
    notification = Notification.objects.create(
        user=event.organizer,
        sender=request.user,
        title=f'Mensaje de staff: {request.user.get_full_name() or request.user.email}',
        message=message,
        notification_type=Notification.Type.MANUAL_ALERT
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Mensaje enviado correctamente al organizador'
    })


@login_required
def remove_member(request, event_id, member_id):
    """Elimina un miembro del equipo."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    member = get_object_or_404(StaffMember, id=member_id, event_id=event_id)
    
    # Si el miembro tiene una actividad asignada, limpiar el speaker
    if member.activity:
        member.activity.speaker_name = None
        member.activity.speaker_email = None
        member.activity.save(update_fields=['speaker_name', 'speaker_email'])
    
    member.delete()
    
    return JsonResponse({'success': True, 'message': 'Miembro eliminado del equipo'})