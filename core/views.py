from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from chat.views import is_chat_available
from .models import CategoriaEvento, Suscripcion, Consulta, Resena
from .forms import ConsultaForm, ResenaForm
from virtualEvent.models import VirtualEvent
from django.utils import timezone
from virtualEvent.models import VirtualEvent
from ve_invitations.models import EventFollower
from ve_invitations.views import follow_event 
from django.db.models import Q

def home(request):
    # 1. Obtener tus categorías predefinidas (con sus iconos)
    tus_categorias = {cat.nombre.lower(): cat for cat in CategoriaEvento.objects.filter(activo=True)}
    
    # 2. Obtener todos los eventos virtuales
    if request.user.is_authenticated and request.user.rol == 'organizador':
        # El organizador ve sus propios eventos (aprobados o pendientes) + eventos aprobados de otros
        eventos_virtuales = VirtualEvent.objects.filter(
            Q(estado='aprobado') | Q(created_by=request.user)
        ).order_by('-start_datetime')
    else:
        # Usuarios normales o no autenticados solo ven eventos aprobados
        eventos_virtuales = VirtualEvent.objects.filter(estado='aprobado').order_by('-start_datetime')
    
    # 3. Extraer categorías únicas de los eventos virtuales
    categorias_virtuales = {}
    for ev in eventos_virtuales:
        if ev.category:
            nombre_original = ev.category.strip()
            clave = nombre_original.lower()
            if clave not in categorias_virtuales:
                categorias_virtuales[clave] = nombre_original
    
    # 4. Construir la lista de categorías para el filtro con sus iconos
    categorias_filtro = []
    for clave, nombre in sorted(categorias_virtuales.items()):
        # Buscar si esta categoría existe en tus categorías predefinidas
        if clave in tus_categorias:
            icono = tus_categorias[clave].icono
        else:
            # Icono por defecto para categorías nuevas
            icono = 'event'
        categorias_filtro.append({
            'nombre': nombre,
            'icono': icono,
            'activo': True,
            'orden': len(categorias_filtro) + 1,
        })
    
    # 5. Convertir eventos a lista de diccionarios
    eventos = []
    for ev in eventos_virtuales:
        eventos.append({
            'id': ev.id,
            'titulo': ev.title,
            'categoria': ev.category,
            'imagen': ev.image.url if ev.image else 'https://via.placeholder.com/1200x400?text=Evento',
            'tipo': 'virtual',
            'fecha': ev.start_datetime.strftime('%Y-%m-%d'),
            'descripcion': ev.description,
            'creado_por': ev.created_by.id,
        })
    
    # 6. Filtros
    categoria_filtro = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda', '').strip()
    
    eventos_filtrados = eventos
    if categoria_filtro:
        eventos_filtrados = [e for e in eventos_filtrados if e['categoria'].lower() == categoria_filtro.lower()]
    if busqueda:
        eventos_filtrados = [e for e in eventos_filtrados if busqueda.lower() in e['titulo'].lower() or busqueda.lower() in e['categoria'].lower()]
    
    # 7. Personalización para usuario autenticado
    if not categoria_filtro and not busqueda and request.user.is_authenticated:
        categorias_preferidas = list(request.user.preferencias.values_list('nombre', flat=True))
        categorias_preferidas_lower = [c.lower() for c in categorias_preferidas]
        eventos_preferidos = [e for e in eventos if e['categoria'].lower() in categorias_preferidas_lower]
        
        if len(eventos_preferidos) < 3:
            otros_eventos = [e for e in eventos if e not in eventos_preferidos]
            eventos_recomendados = eventos_preferidos + otros_eventos[:3 - len(eventos_preferidos)]
        else:
            eventos_recomendados = eventos_preferidos[:6]
        eventos_filtrados = eventos_recomendados
    
    return render(request, 'homepage.html', {
        'categorias': categorias_filtro,
        'eventos': eventos_filtrados,
        'categoria_seleccionada': categoria_filtro,
        'busqueda': busqueda,
        'user_authenticated': request.user.is_authenticated,
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