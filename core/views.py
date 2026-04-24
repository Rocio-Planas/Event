from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from chat.views import is_chat_available
from .models import CategoriaEvento, Favorito, FavoritoPresencial, Suscripcion, Consulta, Resena
from .forms import ConsultaForm, ResenaForm
from virtualEvent.models import VirtualEvent
from ve_invitations.models import EventFollower
from in_person_events.models import Event as EventoPresencial


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
            'url_detalle': f"/eventos-virtuales/{ev.id}/",
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
        # Si no se encuentra, buscar por el nombre original antes de normalizar (puede que no coincida exactamente)
        if not predef_original:
            # Intentar buscar por el nombre normalizado (pero puede no estar en la tabla)
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


# ========== OTRAS VISTAS (suscribirse, contacto, etc.) ==========
# (Mantén el resto de tus vistas igual, solo se incluyen las necesarias)
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