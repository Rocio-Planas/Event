from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from chat.views import is_chat_available
from .models import CategoriaEvento, Suscripcion, Consulta, Resena
from .forms import ConsultaForm, ResenaForm

def home(request):
    categorias = CategoriaEvento.objects.filter(activo=True).order_by('orden')
    
    # Lista de eventos mock (luego reemplazar por BD de compañeras)
    eventos_mock = [
        {'id': 1, 'titulo': 'Concierto Rock 2025', 'categoria': 'Conciertos', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento1', 'tipo': 'presencial', 'fecha': '2025-05-15'},
        {'id': 2, 'titulo': 'Teatro Nacional', 'categoria': 'Teatro', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento2', 'tipo': 'presencial', 'fecha': '2025-06-20'},
        {'id': 3, 'titulo': 'Webinar IA', 'categoria': 'Conferencias', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento3', 'tipo': 'virtual', 'fecha': '2025-07-10'},
        {'id': 4, 'titulo': 'Feria Gastronómica', 'categoria': 'Gastronomía', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento4', 'tipo': 'presencial', 'fecha': '2025-08-05'},
        {'id': 5, 'titulo': 'Campeonato de Fútbol', 'categoria': 'Deportes', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento5', 'tipo': 'presencial', 'fecha': '2025-09-12'},
        {'id': 6, 'titulo': 'Exposición de Arte', 'categoria': 'Exposiciones', 'imagen': 'https://via.placeholder.com/1200x400?text=Evento6', 'tipo': 'presencial', 'fecha': '2025-10-01'},
    ]
    
    # Filtros de usuario (búsqueda y categoría)
    categoria_filtro = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda', '').strip()
    
    # Aplicar filtros explícitos
    eventos_filtrados = eventos_mock
    if categoria_filtro:
        eventos_filtrados = [e for e in eventos_filtrados if e['categoria'].lower() == categoria_filtro.lower()]
    if busqueda:
        eventos_filtrados = [e for e in eventos_filtrados if busqueda.lower() in e['titulo'].lower() or busqueda.lower() in e['categoria'].lower()]
    
    # Si NO hay filtros activos Y el usuario está autenticado, personalizar recomendados
    if not categoria_filtro and not busqueda and request.user.is_authenticated:
        # Obtener IDs de las categorías preferidas del usuario
        categorias_preferidas = request.user.preferencias.values_list('nombre', flat=True)
        # Filtrar eventos que pertenezcan a esas categorías
        eventos_preferidos = [e for e in eventos_mock if e['categoria'] in categorias_preferidas]
        # Si hay menos de 3 eventos preferidos, completar con otros eventos
        if len(eventos_preferidos) < 3:
            otros_eventos = [e for e in eventos_mock if e not in eventos_preferidos]
            eventos_recomendados = eventos_preferidos + otros_eventos[:3 - len(eventos_preferidos)]
        else:
            eventos_recomendados = eventos_preferidos[:6]  # máximo 6
        eventos_filtrados = eventos_recomendados
    
    return render(request, 'homepage.html', {
        'categorias': categorias,
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
    
    # Configuración del chat (para pasar al template)
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