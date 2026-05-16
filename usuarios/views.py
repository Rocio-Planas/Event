# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import os
import logging
from itertools import chain
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ve_invitations.models import EventFollower
from virtualEvent.models import VirtualEvent
from in_person_events.models import Event
from .forms import RegistroForm, LoginForm, RecuperacionPasswordForm, PerfilForm, CambiarPasswordForm, PreferenciasForm
from .models import Usuario, PreferenciaUsuario
from core.models import CategoriaEvento, FavoritoPresencial, Suscripcion, Consulta, Resena, Favorito
from .decorators import role_required
from in_person_events.models import Event as EventoPresencial
from pe_staff.models import StaffMember

logger = logging.getLogger(__name__)


# ==================== FUNCIONES AUXILIARES DE EMAIL ====================

def enviar_email_confirmacion(request, user, token):
    """Envía email de confirmación de cuenta al registrarse"""
    current_site = get_current_site(request)
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'
    
    confirm_url = reverse('usuarios:confirmar_email', args=[token])
    full_url = f"{protocol}://{domain}{confirm_url}"
    
    context = {
        'user': user,
        'nombre': user.get_full_name() or user.email,
        'confirm_url': full_url,
        'domain': domain,
        'site_name': 'EventPulse',
        'expiry_hours': 24,
    }
    
    html_content = render_to_string('usuarios/email/confirmacion_registro.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject='Confirma tu cuenta en EventPulse',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        logger.info(f"Email de confirmación enviado a {user.email}")
        return True
    except Exception as e:
        logger.error(f"Error enviando email de confirmación a {user.email}: {str(e)}")
        return False


def enviar_email_recuperacion(request, user, token):
    """Envía email de recuperación de contraseña"""
    current_site = get_current_site(request)
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'
    
    reset_url = reverse('usuarios:reset_password', args=[token])
    full_url = f"{protocol}://{domain}{reset_url}"
    
    context = {
        'user': user,
        'nombre': user.get_full_name() or user.email,
        'reset_url': full_url,
        'domain': domain,
        'site_name': 'EventPulse',
        'expiry_hours': 24,
    }
    
    html_content = render_to_string('usuarios/email/recuperacion_password.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject='Recupera tu contraseña en EventPulse',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        logger.info(f"Email de recuperación enviado a {user.email}")
        return True
    except Exception as e:
        logger.error(f"Error enviando email de recuperación a {user.email}: {str(e)}")
        return False


def enviar_notificacion_cambio_password(user, ip_address=None, user_agent=None):
    """Envía notificación de que la contraseña fue cambiada"""
    context = {
        'user': user,
        'nombre': user.get_full_name() or user.email,
        'site_name': 'EventPulse',
        'ip_address': ip_address,
        'user_agent': user_agent,
        'fecha': timezone.now(),
    }
    
    html_content = render_to_string('usuarios/email/cambio_password_notificacion.html', context)
    text_content = strip_tags(html_content)
    
    try:
        send_mail(
            subject='Tu contraseña ha sido cambiada - EventPulse',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando notificación de cambio de password a {user.email}: {str(e)}")
        return False


# ==================== GENERADORES DE TOKENS ====================

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Generador de tokens para activación de cuenta"""
    
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + 
            six.text_type(timestamp) + 
            six.text_type(user.is_active)
        )
    
    def check_token(self, user, token):
        if not super().check_token(user, token):
            return False
        if user.is_active:
            return False
        return True

account_activation_token = AccountActivationTokenGenerator()
password_reset_token = PasswordResetTokenGenerator()


# ==================== VISTAS ====================

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            # Crear usuario pero INACTIVO hasta confirmar email
            user = form.save(commit=False)
            user.is_active = False
            user.rol = 'espectador'
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Guardar categorías
            categorias = form.cleaned_data['categorias']
            for cat in categorias:
                PreferenciaUsuario.objects.create(usuario=user, categoria=cat)
            
            # Generar token y enviar email de confirmación
            token = account_activation_token.make_token(user)
            email_enviado = enviar_email_confirmacion(request, user, token)
            
            # En lugar de redirect a login, muestra la página de confirmación
            if email_enviado:
                return render(request, 'usuarios/registro_confirmacion.html', {
                    'user_email': user.email
            })
            else:
                messages.warning(request, 
                    'No pudimos enviar el email de confirmación. Por favor, contacta con soporte o intenta registrarte nuevamente.')
                user.delete()
                return redirect('usuarios:registro')
            
            return redirect('usuarios:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistroForm()
    
    categorias = CategoriaEvento.objects.filter(activo=True)
    return render(request, 'usuarios/registro.html', {'form': form, 'categorias': categorias})


def confirmar_email_view(request, token):
    """Verifica el token y activa la cuenta del usuario"""
    for user in Usuario.objects.filter(is_active=False):
        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            
            # ✅ Iniciar sesión automáticamente
            login(request, user)
            
            # ✅ Renderizar página de éxito con usuario autenticado
            return render(request, 'usuarios/email_confirmado.html', {
                'user': user
            })
    
    # Si el token es inválido, mostrar página de error
    return render(request, 'usuarios/enlace_invalido.html', {
        'tipo': 'confirmacion',
        'mensaje': 'El enlace de confirmación es inválido o ha expirado.'
    })


@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Verificar si la cuenta está activa (email confirmado)
            if not user.is_active:
                messages.warning(request, 
                    'Tu cuenta no ha sido confirmada. Por favor, revisa tu email para activar tu cuenta.')
                return redirect('usuarios:login')
            
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            messages.success(request, f'¡Bienvenido/a de nuevo, {user.first_name}!')
            
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('usuarios:dashboard')
        else:
            messages.error(request, 'Email o contraseña incorrectos')
    else:
        form = LoginForm()
    
    next_url = request.GET.get('next', '')
    return render(request, 'usuarios/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('usuarios:login')


def recuperar_password_view(request):
    if request.method == 'POST':
        form = RecuperacionPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Usuario.objects.get(email=email, is_active=True)
                token = password_reset_token.make_token(user)
                email_enviado = enviar_email_recuperacion(request, user, token)
                
                if email_enviado:
                    # ✅ Mostrar página de éxito en lugar de redirect
                    return render(request, 'usuarios/recuperacion_enviado.html', {
                        'email': email
                    })
                else:
                    messages.warning(request, 'Hubo un problema al enviar el email.')
            except Usuario.DoesNotExist:
                # Por seguridad, mostramos la misma página de éxito
                return render(request, 'usuarios/recuperacion_enviado.html', {
                    'email': email
                })
    else:
        form = RecuperacionPasswordForm()
    
    return render(request, 'usuarios/recuperar_password.html', {'form': form})


def reset_password_view(request, token):
    """Muestra formulario para nueva contraseña usando token"""
    # Encontrar usuario por token
    user = None
    for u in Usuario.objects.filter(is_active=True):
        if password_reset_token.check_token(u, token):
            user = u
            break
    
    if not user:
        return render(request, 'usuarios/enlace_invalido.html', {
            'tipo': 'recuperacion',
            'mensaje': 'El enlace de recuperación es inválido o ha expirado.'
        })
    
    if request.method == 'POST':
        nueva_password = request.POST.get('nueva_password')
        confirmar_password = request.POST.get('confirmar_password')
        
        if not nueva_password or len(nueva_password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
        elif nueva_password != confirmar_password:
            messages.error(request, 'Las contraseñas no coinciden.')
        else:
            user.set_password(nueva_password)
            user.save()
            
            # Enviar notificación de cambio de contraseña
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            enviar_notificacion_cambio_password(user, ip_address, user_agent)
            
            # ✅ Mostrar página de éxito
            return render(request, 'usuarios/restablecer_confirmacion.html')
    
    return render(request, 'usuarios/reset_password.html', {'token': token})

@require_http_methods(["POST"])
@csrf_exempt
def reenviar_recuperacion(request):
    """Reenvía el enlace de recuperación de contraseña"""
    import json
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'error': 'Email no proporcionado'}, status=400)
        
        try:
            user = Usuario.objects.get(email=email, is_active=True)
            token = password_reset_token.make_token(user)
            email_enviado = enviar_email_recuperacion(request, user, token)
            
            if email_enviado:
                return JsonResponse({'success': True, 'message': 'Enlace reenviado exitosamente'})
            else:
                return JsonResponse({'success': False, 'error': 'Error al enviar el email'}, status=500)
        except Usuario.DoesNotExist:
            # Por seguridad, no revelamos si el email existe
            return JsonResponse({'success': True, 'message': 'Si el email está registrado, recibirás un nuevo enlace'})
            
    except Exception as e:
        logger.error(f"Error en reenviar_recuperacion: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Error interno del servidor'}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def reenviar_confirmacion(request):
    """Reenvía el email de confirmación de cuenta"""
    import json
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'error': 'Email no proporcionado'}, status=400)
        
        try:
            user = Usuario.objects.get(email=email, is_active=False)
            token = account_activation_token.make_token(user)
            email_enviado = enviar_email_confirmacion(request, user, token)
            
            if email_enviado:
                return JsonResponse({'success': True, 'message': 'Email de confirmación reenviado'})
            else:
                return JsonResponse({'success': False, 'error': 'Error al enviar el email'}, status=500)
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No hay cuenta pendiente de confirmación con este email'}, status=404)
            
    except Exception as e:
        logger.error(f"Error en reenviar_confirmacion: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Error interno del servidor'}, status=500)


@login_required
def perfil_view(request):
    user = request.user

    eventos_organizados_virtuales = VirtualEvent.objects.filter(created_by=user).order_by('-start_datetime')
    eventos_organizados_presenciales = EventoPresencial.objects.filter(organizer=user).order_by('-start_date')
    suscripciones_virtuales = EventFollower.objects.filter(user=user).select_related('event')
    suscripciones_presenciales = Suscripcion.objects.filter(usuario=user, tipo_evento='presencial').order_by('-fecha_suscripcion')
    favoritos = Favorito.objects.filter(usuario=user).select_related('evento')
    favoritos_presenciales = FavoritoPresencial.objects.filter(usuario=user).select_related('evento')

    context = {
        'user': user,
        'eventos_organizados_virtuales': eventos_organizados_virtuales,
        'eventos_organizados_presenciales': eventos_organizados_presenciales,
        'suscripciones_virtuales': suscripciones_virtuales,
        'suscripciones_presenciales': suscripciones_presenciales,
        'favoritos': favoritos,
        'favoritos_presenciales': favoritos_presenciales,
    }
    return render(request, 'usuarios/perfil.html', context)


@login_required
def editar_perfil_view(request):
    usuario = request.user
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            if 'avatar' in request.FILES and usuario.avatar and usuario.avatar.name != 'avatars/default.png':
                old_path = usuario.avatar.path
                if os.path.exists(old_path):
                    os.remove(old_path)
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = PerfilForm(instance=usuario)
    return render(request, 'usuarios/editar_perfil.html', {'form': form, 'usuario': usuario})


@login_required
def cambiar_password_view(request):
    """Cambio de contraseña desde el perfil - TEMPLATE EXISTENTE SE MANTIENE"""
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['password_actual']):
                form.add_error('password_actual', 'La contraseña actual es incorrecta')
            else:
                nueva_password = form.cleaned_data['nueva_password']
                request.user.set_password(nueva_password)
                request.user.save()
                
                update_session_auth_hash(request, request.user)
                
                ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                enviar_notificacion_cambio_password(request.user, ip_address, user_agent)
                
                messages.success(request, 'Contraseña cambiada correctamente. Se ha enviado una notificación a tu email.')
                return redirect('usuarios:perfil')
    else:
        form = CambiarPasswordForm()
    
    return render(request, 'usuarios/cambiar_password.html', {'form': form})


def dashboard_redirect(request):
    if not request.user.rol:
        request.user.rol = 'espectador'
        request.user.save()
    rol = request.user.rol
    if rol == 'administrador':
        return redirect('usuarios:dashboard_admin')
    elif rol == 'organizador':
        return redirect('usuarios:dashboard_organizador')
    elif rol == 'expositor':
        return redirect('usuarios:dashboard_expositor')
    else:
        return redirect('usuarios:dashboard_espectador')


@login_required
@role_required(['administrador'])
def dashboard_admin(request):
    return render(request, 'usuarios/dashboard_admin.html', {'user': request.user})


@login_required
@role_required(['organizador'])
def dashboard_organizador(request):
    return render(request, 'usuarios/dashboard_organizador.html', {'user': request.user})


@login_required
@role_required(['expositor'])
def dashboard_expositor(request):
    return render(request, 'usuarios/dashboard_expositor.html', {'user': request.user})


@login_required
@role_required(['espectador'])
def dashboard_espectador(request):
    return render(request, 'usuarios/dashboard_espectador.html', {'user': request.user})


@login_required
@role_required(['administrador'])
def dashboard_metrics(request):
    total_usuarios = Usuario.objects.count()
    total_suscripciones = Suscripcion.objects.count()
    total_resenas_aprobadas = Resena.objects.filter(aprobada=True).count()
    total_consultas = Consulta.objects.count()
    context = {
        'total_usuarios': total_usuarios,
        'total_suscripciones': total_suscripciones,
        'total_resenas_aprobadas': total_resenas_aprobadas,
        'total_consultas': total_consultas,
    }
    return render(request, 'usuarios/dashboard_metrics.html', context)


def contacto_view(request):
    return redirect('core:contacto')


@login_required
def editar_preferencias(request):
    if request.method == 'POST':
        form = PreferenciasForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tus preferencias se han actualizado correctamente.')
            return redirect('usuarios:perfil')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = PreferenciasForm(request.user)
    
    categorias = CategoriaEvento.objects.filter(activo=True).order_by('orden')
    return render(request, 'usuarios/editar_preferencias.html', {
        'form': form,
        'categorias': categorias
    })


@login_required
def dashboard_unificado(request):
    user = request.user
    
    eventos_virtuales_organizados = VirtualEvent.objects.filter(created_by=user).order_by('-start_datetime')
    eventos_presenciales_organizados = Event.objects.filter(organizer=user).order_by('-start_date')
    
    eventos_organizados = sorted(
        chain(eventos_virtuales_organizados, eventos_presenciales_organizados),
        key=lambda x: getattr(x, 'start_datetime', None) or getattr(x, 'start_date', None) or getattr(x, 'created_at', timezone.now()),
        reverse=True
    )
    
    suscripciones_virtuales = EventFollower.objects.filter(user=user).select_related('event')
    suscripciones_presenciales = Suscripcion.objects.filter(usuario=user).order_by('-fecha_suscripcion')
    asignaciones_staff = StaffMember.objects.filter(user=user).select_related('event')
    
    context = {
        'user': user,
        'eventos_organizados': eventos_organizados,
        'suscripciones_virtuales': suscripciones_virtuales,
        'suscripciones_presenciales': suscripciones_presenciales,
        'asignaciones_staff': asignaciones_staff,
    }
    return render(request, 'usuarios/dashboard_unificado.html', context)