from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
import os
from itertools import chain

from ve_invitations.models import EventFollower
from virtualEvent.models import VirtualEvent
from in_person_events.models import Event
from .forms import RegistroForm, LoginForm, RecuperacionPasswordForm, PerfilForm, CambiarPasswordForm, PreferenciasForm
from .models import Usuario
from core.models import CategoriaEvento, FavoritoPresencial, Suscripcion, Consulta, Resena
from .decorators import role_required
from core.models import Favorito
from in_person_events.models import Event as EventoPresencial


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

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido/a, {user.first_name}!')
            return redirect('usuarios:dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistroForm()
    categorias = CategoriaEvento.objects.filter(activo=True)
    return render(request, 'usuarios/registro.html', {'form': form, 'categorias': categorias})

@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            messages.success(request, f'¡Bienvenido/a de nuevo, {user.first_name}!')
            return redirect('usuarios:dashboard')
        else:
            messages.error(request, 'Email o contraseña incorrectos')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('usuarios:login')

def recuperar_password_view(request):
    if request.method == 'POST':
        form = RecuperacionPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Simular envío de email
            messages.success(request, f'Se ha enviado un enlace de recuperación a {email}')
            return redirect('usuarios:login')  # Corregido con namespace
    else:
        form = RecuperacionPasswordForm()
    return render(request, 'usuarios/recuperar_password.html', {'form': form})

@login_required
def perfil_view(request):
    user = request.user

    # Eventos virtuales que el usuario organiza
    eventos_organizados_virtuales = VirtualEvent.objects.filter(created_by=user).order_by('-start_datetime')

    # Eventos presenciales que el usuario organiza (aprobados o no? se muestran todos)
    eventos_organizados_presenciales = EventoPresencial.objects.filter(organizer=user).order_by('-start_date')

    # Suscripciones a eventos virtuales (EventFollower)
    suscripciones_virtuales = EventFollower.objects.filter(user=user).select_related('event')

    # Suscripciones a eventos presenciales (usando tu modelo Suscripcion con tipo_evento='presencial')
    suscripciones_presenciales = Suscripcion.objects.filter(usuario=user, tipo_evento='presencial').order_by('-fecha_suscripcion')

    # Favoritos (asumiendo que solo son virtuales, pero puedes adaptar)
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
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            user = authenticate(request, email=request.user.email, password=form.cleaned_data['password_actual'])
            if user:
                user.set_password(form.cleaned_data['nueva_password'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Contraseña cambiada correctamente.')
                return redirect('usuarios:perfil')
            else:
                form.add_error('password_actual', 'La contraseña actual es incorrecta')
    else:
        form = CambiarPasswordForm()
    return render(request, 'usuarios/cambiar_password.html', {'form': form})

@login_required
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

def contacto_view(request):
    # Esta vista está en core, pero la mantenemos aquí si quieres, o la movemos a core.views
    # Por simplicidad, la dejamos aquí y redirigimos a core:contacto
    return redirect('core:contacto')


@login_required
def editar_preferencias(request):
    if request.method == 'POST':
        # 1. Crea el formulario con los datos POST
        form = PreferenciasForm(request.user, request.POST)
        
        if form.is_valid():
            # 2. Guarda el formulario. Como estás usando una relación ManyToManyField
            #    con un modelo intermedio (through='PreferenciaUsuario'), Django
            #    se encarga de crear las instancias en la tabla intermedia
            #    automáticamente.
            form.save()
            
            # 3. Mensaje de éxito
            messages.success(request, 'Tus preferencias se han actualizado correctamente.')
            
            # 4. Redirige al perfil del usuario
            return redirect('usuarios:perfil')
        else:
            # Si el formulario no es válido, muestra los errores
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        # GET request: muestra el formulario con las preferencias actuales
        form = PreferenciasForm(request.user)
    
    # Obtén todas las categorías activas para mostrarlas en la plantilla
    categorias = CategoriaEvento.objects.filter(activo=True).order_by('orden')
    
    return render(request, 'usuarios/editar_preferencias.html', {
        'form': form,
        'categorias': categorias
    })

@login_required
def dashboard_unificado(request):
    user = request.user
    
    # Eventos virtuales que el usuario organiza
    eventos_virtuales_organizados = VirtualEvent.objects.filter(created_by=user).order_by('-start_datetime')
    # Eventos presenciales que el usuario organiza
    eventos_presenciales_organizados = Event.objects.filter(organizer=user).order_by('-start_date')
    
    # Combinar ambos tipos de eventos para la sección "Eventos que organizo"
    eventos_organizados = sorted(
        chain(eventos_virtuales_organizados, eventos_presenciales_organizados),
        key=lambda x: getattr(x, 'start_datetime', None) or getattr(x, 'start_date', None) or x.created_at,
        reverse=True
    )
    
    suscripciones_virtuales = EventFollower.objects.filter(user=user).select_related('event')
    suscripciones_presenciales = Suscripcion.objects.filter(usuario=user).order_by('-fecha_suscripcion')
    
    context = {
        'user': user,
        'eventos_organizados': eventos_organizados,
        'suscripciones_virtuales': suscripciones_virtuales,
        'suscripciones_presenciales': suscripciones_presenciales,
    }
    return render(request, 'usuarios/dashboard_unificado.html', context)
