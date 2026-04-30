from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from chat.views import is_chat_available
from config import settings
from usuarios.decorators import role_required
from .models import CategoriaEvento, Favorito, FavoritoPresencial, Suscripcion, Consulta, Resena
from .forms import ConsultaForm, ResenaForm
from virtualEvent.models import VirtualEvent
from ve_invitations.models import EventFollower
from in_person_events.models import Event as EventoPresencial
from usuarios.models import Usuario as UsuarioModel
from usuarios.forms import PerfilForm
from django import forms
import datetime   # <-- Añadida esta importación para timedelta

# ---------- FUNCIÓN AUXILIAR DE NORMALIZACIÓN ----------
def normalizar_categoria(categoria):
    """
    Normaliza y traduce categorías al español:
    - Traduce inglés → español.
    - Convierte singular a plural.
    - Elimina espacios extra.
    """
    if not categoria:
        return "Sin categoría"
    categoria = categoria.strip()
    # Traducciones inglés -> español
    traducciones = {
        'workshop': 'Taller',
        'conference': 'Conferencia',
        'concert': 'Concierto',
        'networking': 'Networking',
        'other': 'Otro',
        'seminar': 'Seminario',
        'webinar': 'Webinar',
        'seminars': 'Seminario',   # plural inglés
        'workshops': 'Taller',
        'conferences': 'Conferencia',
    }
    cat_lower = categoria.lower()
    if cat_lower in traducciones:
        categoria = traducciones[cat_lower]
    # Singular -> plural (para consistencia en el filtro)
    singular_plural = {
        'Conferencia': 'Conferencias',
        'Taller': 'Talleres',
        'Concierto': 'Conciertos',
        'Seminario': 'Seminarios',
        'Webinar': 'Webinars',
        'Networking': 'Networking',
        'Otro': 'Otros',
    }
    if categoria in singular_plural:
        categoria = singular_plural[categoria]
    return categoria


# ---------- VISTA HOME ----------
def home(request):
    # 1. Categorías predefinidas (normalizamos sus nombres para que coincidan con los eventos)
    categorias_predefinidas = CategoriaEvento.objects.filter(activo=True).order_by('orden', 'nombre')
    # Normalizar los nombres de las categorías predefinidas
    nombres_predefinidos = [normalizar_categoria(cat.nombre) for cat in categorias_predefinidas]

    # 2. Eventos virtuales (aprobados o del organizador)
    if request.user.is_authenticated and request.user.rol == 'organizador':
        virtuales_qs = VirtualEvent.objects.filter(
            Q(estado='aprobado') | Q(created_by=request.user)
        ).order_by('-start_datetime')
    else:
        virtuales_qs = VirtualEvent.objects.filter(estado='aprobado').order_by('-start_datetime')

    virtuales_qs = virtuales_qs.annotate(
        promedio_resenas=Avg('resenas__calificacion', filter=Q(resenas__aprobada=True)),
        total_resenas=Count('resenas', filter=Q(resenas__aprobada=True))
    )

    # 3. Eventos presenciales (solo aprobados)
    presenciales_qs = EventoPresencial.objects.filter(status='aprobado').order_by('-start_date')

    # 4. Suscripciones
    suscripciones_virtuales_ids = []
    suscripciones_presenciales_ids = []
    if request.user.is_authenticated:
        suscripciones_virtuales_ids = list(EventFollower.objects.filter(user=request.user).values_list('event_id', flat=True))
        suscripciones_presenciales_ids = list(Suscripcion.objects.filter(usuario=request.user, tipo_evento='presencial').values_list('evento_id', flat=True))

    # 5. Favoritos virtuales
    favoritos_virtuales_ids = []
    if request.user.is_authenticated:
        favoritos_virtuales_ids = list(request.user.favoritos.values_list('evento_id', flat=True))

    # 6. Favoritos presenciales
    favoritos_presenciales_ids = []
    if request.user.is_authenticated:
        favoritos_presenciales_ids = list(request.user.favoritos_presenciales.values_list('evento_id', flat=True))

    # 7. Construir lista unificada de eventos
    eventos = []

    # Virtuales
    for ev in virtuales_qs:
        eventos.append({
            'id': ev.id,
            'titulo': ev.title,
            'categoria': normalizar_categoria(ev.category),
            'imagen': ev.image.url if ev.image else 'https://via.placeholder.com/1200x400?text=Evento',
            'tipo': 'virtual',
            'fecha': ev.start_datetime.strftime('%Y-%m-%d'),
            'descripcion': ev.description,
            'creado_por': ev.created_by.id,
            'promedio': round(ev.promedio_resenas or 0, 1),
            'total_resenas': ev.total_resenas or 0,
            'ubicacion': None,
            'esta_suscrito': ev.id in suscripciones_virtuales_ids,
            'es_favorito': ev.id in favoritos_virtuales_ids,
            'url_detalle': reverse('virtualEvent:event_detail', args=[ev.id]),
        })

    # Presenciales
    for ev in presenciales_qs:
        eventos.append({
            'id': ev.id,
            'titulo': ev.title,
            'categoria': normalizar_categoria(ev.category),
            'imagen': ev.image.url if ev.image else 'https://via.placeholder.com/1200x400?text=Evento',
            'tipo': 'presencial',
            'fecha': ev.start_date.strftime('%Y-%m-%d'),
            'descripcion': ev.description,
            'creado_por': ev.organizer.id,
            'promedio': 0,
            'total_resenas': 0,
            'ubicacion': ev.location,
            'esta_suscrito': ev.id in suscripciones_presenciales_ids,
            'es_favorito': ev.id in favoritos_presenciales_ids,
            'url_detalle': f"/eventos-presenciales/{ev.id}/",
        })

    # 8. Filtros
    categoria_filtro = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda', '').strip()

    eventos_filtrados = eventos
    if categoria_filtro:
        filtro_norm = normalizar_categoria(categoria_filtro)
        eventos_filtrados = [e for e in eventos_filtrados if normalizar_categoria(e['categoria']) == filtro_norm]
    if busqueda:
        eventos_filtrados = [e for e in eventos_filtrados if busqueda.lower() in e['titulo'].lower() or busqueda.lower() in e['categoria'].lower()]

    # 9. Personalización por preferencias (solo sin filtros)
    if not categoria_filtro and not busqueda and request.user.is_authenticated:
        preferencias = list(request.user.preferencias.values_list('nombre', flat=True))
        if preferencias:
            categorias_pref_norm = [normalizar_categoria(c) for c in preferencias]
            eventos_preferidos = [e for e in eventos_filtrados if normalizar_categoria(e['categoria']) in categorias_pref_norm]
            if len(eventos_preferidos) < 3:
                otros_eventos = [e for e in eventos_filtrados if e not in eventos_preferidos]
                eventos_recomendados = eventos_preferidos + otros_eventos[:3 - len(eventos_preferidos)]
            else:
                eventos_recomendados = eventos_preferidos[:6]
            eventos_filtrados = eventos_recomendados

    # 10. Paginación
    paginator = Paginator(eventos_filtrados, 6)
    page = request.GET.get('page', 1)
    try:
        eventos_paginados = paginator.page(page)
    except PageNotAnInteger:
        eventos_paginados = paginator.page(1)
    except EmptyPage:
        eventos_paginados = paginator.page(paginator.num_pages)

    # 11. Lista de eventos presenciales para el mapa
    eventos_presenciales_mapa = []
    for evento in eventos_paginados:
        if evento.get('tipo') == 'presencial' and evento.get('ubicacion'):
            eventos_presenciales_mapa.append({
                'id': evento['id'],
                'titulo': evento['titulo'],
                'direccion': evento['ubicacion'],
                'fecha': evento['fecha'],
                'categoria': evento.get('categoria', 'Evento'),
                'imagen': evento.get('imagen', ''),
            })

    # 12. Construir categorías para el filtro (sin duplicados, todas normalizadas)
    categorias_unicas = set()
    for ev in virtuales_qs:
        if ev.category:
            categorias_unicas.add(normalizar_categoria(ev.category))
    for ev in presenciales_qs:
        if ev.category:
            categorias_unicas.add(normalizar_categoria(ev.category))

    # Combinar con predefinidas (ya normalizadas)
    categorias_combinadas = list(nombres_predefinidos)
    for cat in sorted(categorias_unicas):
        if cat not in categorias_combinadas:
            categorias_combinadas.append(cat)

    categorias_para_template = []
    for nombre in categorias_combinadas:
        # Buscar el icono de la categoría predefinida original (sin normalizar)
        predef_original = CategoriaEvento.objects.filter(activo=True).filter(nombre__iexact=nombre).first()
        if not predef_original:
            predef_original = categorias_predefinidas.filter(nombre=nombre).first()
        icono = predef_original.icono if predef_original else 'category'
        categorias_para_template.append({'nombre': nombre, 'icono': icono})

    context = {
        'categorias': categorias_para_template,
        'eventos': eventos_paginados,
        'categoria_seleccionada': categoria_filtro,
        'busqueda': busqueda,
        'user_authenticated': request.user.is_authenticated,
        'paginator': paginator,
        'page_obj': eventos_paginados,
        'eventos_presenciales_mapa': eventos_presenciales_mapa,
    }
    return render(request, 'homepage.html', context)


# ========== TOGGLE FAVORITOS (VIRTUALES) ==========
@login_required
@require_POST
def toggle_favorito(request):
    evento_id = request.POST.get('evento_id')
    if not evento_id:
        return JsonResponse({'error': 'ID requerido'}, status=400)
    try:
        evento = VirtualEvent.objects.get(id=evento_id)
    except VirtualEvent.DoesNotExist:
        return JsonResponse({'error': 'Evento no existe'}, status=404)
    favorito, created = Favorito.objects.get_or_create(usuario=request.user, evento=evento)
    if not created:
        favorito.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'evento_id': evento_id})


# ========== TOGGLE FAVORITOS (PRESENCIALES) ==========
@login_required
@require_POST
def toggle_favorito_presencial(request):
    evento_id = request.POST.get('evento_id')
    if not evento_id:
        return JsonResponse({'error': 'ID requerido'}, status=400)
    try:
        evento = EventoPresencial.objects.get(id=evento_id)
    except EventoPresencial.DoesNotExist:
        return JsonResponse({'error': 'Evento no existe'}, status=404)
    favorito, created = FavoritoPresencial.objects.get_or_create(usuario=request.user, evento=evento)
    if not created:
        favorito.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'evento_id': evento_id})


# ========== OTRAS VISTAS ==========
@login_required
def suscribirse(request):
    if request.method == 'POST':
        evento_id = request.POST.get('evento_id')
        tipo_evento = request.POST.get('tipo_evento')
        titulo = request.POST.get('titulo')
        fecha = request.POST.get('fecha') or None
        imagen = request.POST.get('imagen', '')

        if tipo_evento == 'virtual':
            try:
                event = VirtualEvent.objects.get(id=evento_id)
                if event.created_by == request.user:
                    messages.error(request, 'No puedes suscribirte a tu propio evento.')
                    return redirect('core:home')
                follow, created = EventFollower.objects.get_or_create(user=request.user, event=event)
                if created:
                    messages.success(request, f'✅ Te has suscrito al evento virtual "{titulo}"')
                else:
                    messages.info(request, f'ℹ️ Ya estabas suscrito a "{titulo}"')
            except VirtualEvent.DoesNotExist:
                messages.error(request, 'Evento virtual no encontrado')
        else:
            suscripcion, created = Suscripcion.objects.get_or_create(
                usuario=request.user,
                evento_id=evento_id,
                tipo_evento=tipo_evento,
                defaults={
                    'titulo_evento': titulo,
                    'fecha_evento': fecha,
                    'imagen_evento': imagen,
                }
            )
            if created:
                messages.success(request, f'✅ Te has suscrito a "{titulo}"')
            else:
                messages.info(request, f'ℹ️ Ya estabas suscrito a "{titulo}"')
    return redirect('core:home')


@login_required
def cancelar_suscripcion_virtual(request, evento_id):
    try:
        event = VirtualEvent.objects.get(id=evento_id)
        follow = EventFollower.objects.get(user=request.user, event=event)
        follow.delete()
        messages.success(request, f'❌ Has cancelado tu suscripción a "{event.title}"')
    except (VirtualEvent.DoesNotExist, EventFollower.DoesNotExist):
        messages.error(request, 'No estabas suscrito a este evento virtual')
    return redirect('usuarios:perfil')


@login_required
def cancelar_suscripcion(request, suscripcion_id):
    suscripcion = get_object_or_404(Suscripcion, id=suscripcion_id, usuario=request.user)
    titulo = suscripcion.titulo_evento
    suscripcion.delete()
    messages.success(request, f'❌ Has cancelado tu suscripción a "{titulo}"')
    return redirect('usuarios:perfil')


# ========== PANEL DE ADMINISTRACIÓN ==========
@login_required
@role_required(['administrador'])
def admin_panel(request):
    """Panel principal con tarjetas de resumen."""
    total_usuarios = UsuarioModel.objects.count()
    total_eventos_pendientes = (
        VirtualEvent.objects.filter(estado='pendiente').count() +
        EventoPresencial.objects.filter(status='pendiente').count()
    )
    total_resenas_pendientes = Resena.objects.filter(aprobada=False).count()
    total_consultas_no_respondidas = Consulta.objects.filter(respondido=False).count()
    total_suscripciones = (
        EventFollower.objects.count() + Suscripcion.objects.count()
    )
    
    context = {
        'total_usuarios': total_usuarios,
        'total_eventos_pendientes': total_eventos_pendientes,
        'total_resenas_pendientes': total_resenas_pendientes,
        'total_consultas_no_respondidas': total_consultas_no_respondidas,
        'total_suscripciones': total_suscripciones,
    }
    return render(request, 'core/admin_panel.html', context)


@login_required
@role_required(['administrador'])
def admin_usuarios(request):
    """Listado de usuarios con opciones de cambiar rol y eliminar."""
    usuarios = UsuarioModel.objects.all().order_by('-date_joined')
    paginator = Paginator(usuarios, 15)
    page = request.GET.get('page', 1)
    usuarios_paginados = paginator.get_page(page)
    
    context = {
        'usuarios': usuarios_paginados,
    }
    return render(request, 'core/admin_usuarios.html', context)


@login_required
@role_required(['administrador'])
def admin_eventos_pendientes(request):
    """Lista unificada de eventos virtuales y presenciales pendientes."""
    eventos_virtuales = VirtualEvent.objects.filter(estado='pendiente').select_related('created_by')
    eventos_presenciales = EventoPresencial.objects.filter(status='pendiente').select_related('organizer')
    
    eventos = []
    for ev in eventos_virtuales:
        eventos.append({
            'id': ev.id,
            'titulo': ev.title,
            'tipo': 'virtual',
            'organizador': ev.created_by,
            'fecha': ev.start_datetime,
            'categoria': ev.category,
        })
    for ev in eventos_presenciales:
        eventos.append({
            'id': ev.id,
            'titulo': ev.title,
            'tipo': 'presencial',
            'organizador': ev.organizer,
            'fecha': ev.start_date,
            'categoria': ev.category,
        })
    
    eventos.sort(key=lambda x: x['fecha'], reverse=True)
    
    paginator = Paginator(eventos, 10)
    page = request.GET.get('page', 1)
    eventos_paginados = paginator.get_page(page)
    
    context = {
        'eventos': eventos_paginados,
    }
    return render(request, 'core/admin_eventos.html', context)


@login_required
@role_required(['administrador'])
def admin_aprobar_evento(request, evento_id, tipo):
    if tipo == 'virtual':
        evento = get_object_or_404(VirtualEvent, id=evento_id)
        evento.estado = 'aprobado'
        evento.save()
        send_mail(
            f'Tu evento "{evento.title}" ha sido aprobado',
            f'Hola {evento.created_by.get_full_name()},\n\nTu evento virtual "{evento.title}" ha sido aprobado y ya es visible en la plataforma.\n\nSaludos,\nEquipo EventPulse',
            settings.DEFAULT_FROM_EMAIL,
            [evento.created_by.email],
            fail_silently=False,
        )
        messages.success(request, f'Evento virtual "{evento.title}" aprobado.')
    else:
        evento = get_object_or_404(EventoPresencial, id=evento_id)
        evento.status = 'aprobado'
        evento.save()
        send_mail(
            f'Tu evento "{evento.title}" ha sido aprobado',
            f'Hola {evento.organizer.get_full_name()},\n\nTu evento presencial "{evento.title}" ha sido aprobado y ya es visible en la plataforma.\n\nSaludos,\nEquipo EventPulse',
            settings.DEFAULT_FROM_EMAIL,
            [evento.organizer.email],
            fail_silently=False,
        )
        messages.success(request, f'Evento presencial "{evento.title}" aprobado.')
    
    return redirect('core:admin_eventos')


@login_required
@role_required(['administrador'])
def admin_rechazar_evento(request, evento_id, tipo):
    if tipo == 'virtual':
        evento = get_object_or_404(VirtualEvent, id=evento_id)
        evento.estado = 'rechazado'
        evento.save()
        messages.success(request, f'Evento virtual "{evento.title}" rechazado.')
    else:
        evento = get_object_or_404(EventoPresencial, id=evento_id)
        evento.status = 'rechazado'
        evento.save()
        messages.success(request, f'Evento presencial "{evento.title}" rechazado.')
    
    return redirect('core:admin_eventos')


@login_required
@role_required(['administrador'])
def admin_resenas(request):
    """Listado de reseñas pendientes de aprobación."""
    resenas = Resena.objects.filter(aprobada=False).select_related('evento', 'usuario').order_by('-fecha_creacion')
    paginator = Paginator(resenas, 15)
    page = request.GET.get('page', 1)
    resenas_paginadas = paginator.get_page(page)
    
    context = {
        'resenas': resenas_paginadas,
    }
    return render(request, 'core/admin_resenas.html', context)


@login_required
@role_required(['administrador'])
def admin_aprobar_resena(request, resena_id):
    resena = get_object_or_404(Resena, id=resena_id)
    resena.aprobada = True
    resena.save()
    send_mail(
        'Tu reseña ha sido aprobada',
        f'Hola {resena.nombre},\n\nTu reseña para el evento "{resena.evento.title}" ha sido aprobada y ya está visible.\n\nGracias por tu contribución.\nEquipo EventPulse',
        settings.DEFAULT_FROM_EMAIL,
        [resena.email],
        fail_silently=False,
    )
    messages.success(request, 'Reseña aprobada correctamente.')
    return redirect('core:admin_resenas')


@login_required
@role_required(['administrador'])
def admin_consultas(request):
    """Listado de consultas no respondidas."""
    consultas = Consulta.objects.filter(respondido=False).order_by('-fecha_creacion')
    paginator = Paginator(consultas, 15)
    page = request.GET.get('page', 1)
    consultas_paginadas = paginator.get_page(page)
    
    context = {
        'consultas': consultas_paginadas,
    }
    return render(request, 'core/admin_consultas.html', context)


@login_required
@role_required(['administrador'])
def admin_responder_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        if respuesta:
            consulta.respuesta = respuesta
            consulta.respondido = True
            consulta.save()
            send_mail(
                f'Respuesta a tu consulta: {consulta.asunto}',
                f'Hola {consulta.nombre},\n\nTu consulta:\n"{consulta.mensaje}"\n\nRespuesta:\n{respuesta}\n\nSaludos,\nEquipo EventPulse',
                settings.DEFAULT_FROM_EMAIL,
                [consulta.email],
                fail_silently=False,
            )
            messages.success(request, 'Respuesta enviada correctamente.')
        else:
            messages.error(request, 'Debes escribir una respuesta.')
        return redirect('core:admin_consultas')
    
    return render(request, 'core/admin_responder_consulta.html', {'consulta': consulta})


@login_required
@role_required(['administrador'])
def admin_cambiar_rol(request, usuario_id):
    usuario = get_object_or_404(UsuarioModel, id=usuario_id)
    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        if nuevo_rol in ['espectador', 'organizador', 'expositor', 'administrador']:
            usuario.rol = nuevo_rol
            usuario.save()
            messages.success(request, f'Rol de {usuario.email} cambiado a {nuevo_rol}.')
        else:
            messages.error(request, 'Rol inválido.')
    return redirect('core:admin_usuarios')


@login_required
@role_required(['administrador'])
def admin_eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(UsuarioModel, id=usuario_id)
    if request.user == usuario:
        messages.error(request, 'No puedes eliminar tu propia cuenta desde aquí.')
        return redirect('core:admin_usuarios')
    
    usuario.delete()
    messages.success(request, f'Usuario {usuario.email} eliminado correctamente.')
    return redirect('core:admin_usuarios')


def contacto_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'review':
            form = ResenaForm(request.POST)
            if form.is_valid():
                resena = form.save(commit=False)
                if request.user.is_authenticated:
                    resena.usuario = request.user
                    resena.nombre = request.user.get_full_name() or request.user.email
                    resena.email = request.user.email
                resena.save()
                messages.success(request, '¡Gracias por tu reseña! Será revisada por nuestro equipo.')
                return redirect('core:contacto')
            else:
                messages.error(request, 'Hubo un error al enviar la reseña. Revisa los datos.')
        else:
            form = ConsultaForm(request.POST)
            if form.is_valid():
                consulta = form.save(commit=False)
                if request.user.is_authenticated:
                    consulta.usuario = request.user
                    consulta.nombre = request.user.get_full_name() or request.user.email
                    consulta.email = request.user.email
                consulta.save()
                messages.success(request, 'Consulta enviada correctamente. Te responderemos pronto.')
                return redirect('core:contacto')
            else:
                messages.error(request, 'Hubo un error al enviar la consulta. Revisa los datos.')
    else:
        review_form = ResenaForm()
        inquiry_form = ConsultaForm()

    chat_config = {
        'available': is_chat_available(),
        'user_id': request.user.id if request.user.is_authenticated else 0,
    }

    return render(request, 'contacto.html', {
        'review_form': review_form,
        'inquiry_form': inquiry_form,
        'chat_config': chat_config,
    })


def about_view(request):
    return render(request, 'about.html')


def terms_view(request):
    return render(request, 'terms.html')


def privacy_view(request):
    return render(request, 'privacy.html')


def aviso_legal_view(request):
    return render(request, 'aviso_legal.html')


def politica_cookies_view(request):
    return render(request, 'politica_cookies.html')


def detalle_evento_presencial(request, evento_id):
    evento = get_object_or_404(EventoPresencial, id=evento_id, status='aprobado')
    evento_data = {
        'id': evento.id,
        'titulo': evento.title,
        'descripcion': evento.description,
        'imagen': evento.image.url if evento.image else 'https://via.placeholder.com/1200x400?text=Evento',
        'fecha': evento.start_date.strftime('%d/%m/%Y %H:%M'),
        'tipo': 'presencial',
        'categoria': normalizar_categoria(evento.category),
        'ubicacion': evento.location,
        'capacidad': evento.capacity,
        'organizador': evento.organizer.get_full_name() or evento.organizer.email,
        'creado_por': evento.organizer.id,
    }
    esta_suscrito = False
    es_organizador = False
    es_favorito = False
    if request.user.is_authenticated:
        es_organizador = (request.user == evento.organizer)
        if not es_organizador:
            esta_suscrito = Suscripcion.objects.filter(
                usuario=request.user, evento_id=evento.id, tipo_evento='presencial'
            ).exists()
            es_favorito = FavoritoPresencial.objects.filter(usuario=request.user, evento=evento).exists()
    context = {
        'evento': evento_data,
        'esta_suscrito': esta_suscrito,
        'es_organizador': es_organizador,
        'es_favorito': es_favorito,
    }
    return render(request, 'evento_presencial_detalle.html', context)


class AdminUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, 
        required=False, 
        help_text="Dejar en blanco para generar una automática (12 caracteres)"
    )
    rol = forms.ChoiceField(choices=UsuarioModel.ROLES)
    
    class Meta:
        model = UsuarioModel
        fields = ['first_name', 'last_name', 'email', 'telefono', 'rol', 'is_active']


@login_required
@role_required(['administrador'])
def admin_crear_usuario(request):
    if request.method == 'POST':
        form = AdminUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            else:
                import secrets
                import string
                alphabet = string.ascii_letters + string.digits
                password = ''.join(secrets.choice(alphabet) for _ in range(12))
                user.set_password(password)
            user.save()
            messages.success(request, f'Usuario {user.email} creado. Contraseña: {password}')
            return redirect('core:admin_usuarios')
    else:
        form = AdminUsuarioForm()
    return render(request, 'core/admin_usuario_form.html', {'form': form, 'titulo': 'Crear nuevo usuario'})


@login_required
@role_required(['administrador'])
def admin_editar_usuario(request, usuario_id):
    usuario = get_object_or_404(UsuarioModel, id=usuario_id)
    if request.method == 'POST':
        form = AdminUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, f'Usuario {user.email} actualizado.')
            return redirect('core:admin_usuarios')
    else:
        form = AdminUsuarioForm(instance=usuario, initial={'password': ''})
    return render(request, 'core/admin_usuario_form.html', {'form': form, 'titulo': f'Editar usuario: {usuario.email}'})


# ========== NUEVA VISTA DE MÉTRICAS CON GRÁFICOS ==========

@login_required
@role_required(['administrador'])
def admin_metrics(request):
    """Vista de métricas globales con gráficos y etiquetas traducibles."""
    total_usuarios = UsuarioModel.objects.count()
    total_suscripciones = (
        EventFollower.objects.count() + Suscripcion.objects.count()
    )
    total_resenas_aprobadas = Resena.objects.filter(aprobada=True).count()
    total_consultas = Consulta.objects.count()

    # 1. Eventos por categoría
    categorias = {}
    for ev in VirtualEvent.objects.filter(estado='aprobado'):
        cat = normalizar_categoria(ev.category) if ev.category else 'Sin categoría'
        categorias[cat] = categorias.get(cat, 0) + 1
    for ev in EventoPresencial.objects.filter(status='aprobado'):
        cat = normalizar_categoria(ev.category) if ev.category else 'Sin categoría'
        categorias[cat] = categorias.get(cat, 0) + 1
    categorias_labels = list(categorias.keys())
    categorias_data = list(categorias.values())

    # 2. Generar los últimos 12 meses en orden cronológico
    #    dos listas de etiquetas: español e inglés
    meses_es = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    meses_en = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    hoy = timezone.now().date()
    inicio_periodo = hoy.replace(day=1) - datetime.timedelta(days=1)
    inicio_periodo = inicio_periodo.replace(day=1)  # primer día del mes anterior
    for _ in range(10):
        inicio_periodo = (inicio_periodo - datetime.timedelta(days=1)).replace(day=1)

    suscripciones_data = []
    suscripciones_labels_es = []
    suscripciones_labels_en = []
    usuarios_data = []

    cursor = inicio_periodo
    for _ in range(12):
        if cursor.month == 12:
            fin_mes = cursor.replace(year=cursor.year + 1, month=1, day=1)
        else:
            fin_mes = cursor.replace(month=cursor.month + 1, day=1)

        # Etiquetas en cada idioma
        suscripciones_labels_es.append(f"{meses_es[cursor.month - 1]} {cursor.year}")
        suscripciones_labels_en.append(f"{meses_en[cursor.month - 1]} {cursor.year}")

        virtuales_mes = EventFollower.objects.filter(
            followed_at__gte=cursor,
            followed_at__lt=fin_mes
        ).count()
        presenciales_mes = Suscripcion.objects.filter(
            fecha_suscripcion__gte=cursor,
            fecha_suscripcion__lt=fin_mes
        ).count()
        suscripciones_data.append(virtuales_mes + presenciales_mes)

        usuarios_mes = UsuarioModel.objects.filter(
            date_joined__gte=cursor,
            date_joined__lt=fin_mes
        ).count()
        usuarios_data.append(usuarios_mes)

        cursor = fin_mes

    context = {
        'total_usuarios': total_usuarios,
        'total_suscripciones': total_suscripciones,
        'total_resenas_aprobadas': total_resenas_aprobadas,
        'total_consultas': total_consultas,
        'categorias_labels': categorias_labels,
        'categorias_data': categorias_data,
        # Listas bilingües para las gráficas de tiempo
        'suscripciones_labels_es': suscripciones_labels_es,
        'suscripciones_labels_en': suscripciones_labels_en,
        'suscripciones_data': suscripciones_data,
        'usuarios_labels_es': suscripciones_labels_es,  # mismas etiquetas
        'usuarios_labels_en': suscripciones_labels_en,
        'usuarios_data': usuarios_data,
    }
    return render(request, 'core/admin_metrics.html', context)