from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from chat.views import is_chat_available
from .models import CategoriaEvento, Favorito, Suscripcion, Consulta, Resena
from .forms import ConsultaForm, ResenaForm
from virtualEvent.models import VirtualEvent
from django.utils import timezone
from virtualEvent.models import VirtualEvent
from ve_invitations.models import EventFollower
from ve_invitations.views import follow_event 
from django.db.models import Q, Avg, Count
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.views.decorators.http import require_POST

def home(request):
    # 1. Categorías predefinidas
    categorias_predefinidas = CategoriaEvento.objects.filter(activo=True).order_by('orden', 'nombre')
    nombres_predefinidos = list(categorias_predefinidas.values_list('nombre', flat=True))

    # 2. Base de eventos según rol y estado
    if request.user.is_authenticated and request.user.rol == 'organizador':
        eventos_qs = VirtualEvent.objects.filter(
            Q(estado='aprobado') | Q(created_by=request.user)
        ).order_by('-start_datetime')
    else:
        eventos_qs = VirtualEvent.objects.filter(estado='aprobado').order_by('-start_datetime')

    # 3. Categorías únicas de eventos (para el filtro combinado)
    categorias_eventos = eventos_qs.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct()
    categorias_combinadas = list(nombres_predefinidos)
    for cat in categorias_eventos:
        if cat not in categorias_combinadas:
            categorias_combinadas.append(cat)

    categorias_para_template = []
    for nombre in categorias_combinadas:
        predef = categorias_predefinidas.filter(nombre=nombre).first()
        icono = predef.icono if predef else 'category'
        categorias_para_template.append({'nombre': nombre, 'icono': icono})

    # 4. Filtros
    categoria_seleccionada = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda', '').strip()

    if categoria_seleccionada:
        eventos_qs = eventos_qs.filter(category__iexact=categoria_seleccionada)
    if busqueda:
        eventos_qs = eventos_qs.filter(
            Q(title__icontains=busqueda) |
            Q(category__icontains=busqueda) |
            Q(description__icontains=busqueda) |
            Q(created_by__first_name__icontains=busqueda) |
            Q(created_by__last_name__icontains=busqueda) |
            Q(created_by__email__icontains=busqueda)
        )

    # 5. Anotar promedio y cantidad de reseñas
    eventos_qs = eventos_qs.annotate(
        promedio_resenas=Avg('resenas__calificacion', filter=Q(resenas__aprobada=True)),
        total_resenas=Count('resenas', filter=Q(resenas__aprobada=True))
    )

    # 6. Convertir a lista de diccionarios ANTES de paginar (para poder reordenar)
    eventos_lista = []
    for ev in eventos_qs:
        eventos_lista.append({
            'id': ev.id,
            'titulo': ev.title,
            'categoria': ev.category,
            'imagen': ev.image.url if ev.image else 'https://via.placeholder.com/1200x400?text=Evento',
            'tipo': 'virtual',
            'fecha': ev.start_datetime.strftime('%Y-%m-%d'),
            'descripcion': ev.description,
            'creado_por': ev.created_by.id,
            'promedio': round(ev.promedio_resenas or 0, 1),
            'total_resenas': ev.total_resenas or 0,
        })

    # 7. Personalización por preferencias (solo si NO hay filtros activos y usuario autenticado)
    if not categoria_seleccionada and not busqueda and request.user.is_authenticated:
        preferencias = list(request.user.preferencias.values_list('nombre', flat=True))
        if preferencias:
            categorias_preferidas_lower = [c.lower() for c in preferencias]
            # Eventos preferidos (coincidencia insensible a mayúsculas)
            eventos_preferidos = [e for e in eventos_lista if e['categoria'].lower() in categorias_preferidas_lower]
            if len(eventos_preferidos) < 3:
                otros_eventos = [e for e in eventos_lista if e not in eventos_preferidos]
                eventos_recomendados = eventos_preferidos + otros_eventos[:3 - len(eventos_preferidos)]
            else:
                eventos_recomendados = eventos_preferidos[:6]
            eventos_lista = eventos_recomendados

    # 8. Paginación (6 elementos por página)
    paginator = Paginator(eventos_lista, 6)
    page = request.GET.get('page', 1)
    try:
        eventos_paginados = paginator.page(page)
    except PageNotAnInteger:
        eventos_paginados = paginator.page(1)
    except EmptyPage:
        eventos_paginados = paginator.page(paginator.num_pages)

    # 9. IDs de eventos favoritos del usuario
    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(request.user.favoritos.values_list('evento_id', flat=True))

    # Añadir campo 'es_favorito' a cada evento de la página actual
    for evento in eventos_paginados:
        evento['es_favorito'] = evento['id'] in favoritos_ids

    context = {
        'categorias': categorias_para_template,
        'eventos': eventos_paginados,
        'categoria_seleccionada': categoria_seleccionada,
        'busqueda': busqueda,
        'user_authenticated': request.user.is_authenticated,
        'paginator': paginator,
        'page_obj': eventos_paginados,
    }
    return render(request, 'homepage.html', context)


# ========== VISTA PARA TOGGLE FAVORITO (AJAX) ==========
@login_required
@require_POST
def toggle_favorito(request):
    evento_id = request.POST.get('evento_id')
    if not evento_id:
        return JsonResponse({'error': 'ID de evento requerido'}, status=400)

    try:
        evento = VirtualEvent.objects.get(id=evento_id)
    except VirtualEvent.DoesNotExist:
        return JsonResponse({'error': 'Evento no encontrado'}, status=404)

    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        evento=evento
    )
    if not created:
        favorito.delete()
        liked = False
    else:
        liked = True

    total_likes = Favorito.objects.filter(evento=evento).count()

    return JsonResponse({
        'liked': liked,
        'total_likes': total_likes,
        'evento_id': evento_id
    })

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
                # No permitir que el organizador se suscriba a su propio evento
                if event.created_by == request.user:
                    messages.error(request, 'No puedes suscribirte a tu propio evento.')
                    return redirect('core:home')
                
                follow, created = EventFollower.objects.get_or_create(
                    user=request.user,
                    event=event
                )
                if created:
                    messages.success(request, f'✅ Te has suscrito al evento virtual "{titulo}"')
                else:
                    messages.info(request, f'ℹ️ Ya estabas suscrito a "{titulo}"')
            except VirtualEvent.DoesNotExist:
                messages.error(request, 'Evento virtual no encontrado')
        else:
            # Lógica para eventos presenciales (cuando Diana integre sus eventos)
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
    return redirect('perfil')

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
        else:  # inquiry
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

def detalle_evento(request, evento_id):
    # Lista de eventos mock (debe coincidir con la de home)
    eventos_mock = [
        {'id': 1, 'titulo': 'Concierto Rock 2025', 'categoria': 'Conciertos', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento1', 'tipo': 'presencial', 'fecha': '2025-05-15'},
        {'id': 2, 'titulo': 'Teatro Nacional', 'categoria': 'Teatro', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento2', 'tipo': 'presencial', 'fecha': '2025-06-20'},
        {'id': 3, 'titulo': 'Webinar IA', 'categoria': 'Conferencias', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento3', 'tipo': 'virtual', 'fecha': '2025-07-10'},
        {'id': 4, 'titulo': 'Feria Gastronómica', 'categoria': 'Gastronomía', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento4', 'tipo': 'presencial', 'fecha': '2025-08-05'},
        {'id': 5, 'titulo': 'Campeonato de Fútbol', 'categoria': 'Deportes', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento5', 'tipo': 'presencial', 'fecha': '2025-09-12'},
    ]
    evento = next((e for e in eventos_mock if e['id'] == evento_id), None)
    if not evento:
        return render(request, '404.html', status=404)
    
    resenas = Resena.objects.filter(evento_id=evento_id, aprobada=True).order_by('-fecha_creacion')
    promedio = 0
    if resenas.exists():
        promedio = round(sum(r.calificacion for r in resenas) / resenas.count(), 1)
    
    return render(request, 'evento_detalle.html', {
        'evento': evento,
        'resenas': resenas,
        'promedio': promedio,
        'total_resenas': resenas.count()
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

@login_required
@require_POST
def toggle_favorito(request):
    evento_id = request.POST.get('evento_id')
    if not evento_id:
        return JsonResponse({'error': 'ID de evento requerido'}, status=400)
    
    try:
        evento = VirtualEvent.objects.get(id=evento_id)
    except VirtualEvent.DoesNotExist:
        return JsonResponse({'error': 'Evento no encontrado'}, status=404)
    
    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        evento=evento
    )
    if not created:
        favorito.delete()
        liked = False
    else:
        liked = True
    
    # Opcional: contar cuántos likes tiene el evento
    total_likes = Favorito.objects.filter(evento=evento).count()
    
    return JsonResponse({
        'liked': liked,
        'total_likes': total_likes,
        'evento_id': evento_id
    })