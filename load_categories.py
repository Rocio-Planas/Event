import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CategoriaEvento

categorias = [
    {'nombre': 'Conciertos', 'icono': 'mic', 'color': '#FF6B6B', 'orden': 1},
    {'nombre': 'Teatro', 'icono': 'theater_comedy', 'color': '#4ECDC4', 'orden': 2},
    {'nombre': 'Baile', 'icono': 'sports_dance', 'color': '#FF9F4A', 'orden': 3},
    {'nombre': 'Exposiciones', 'icono': 'art_track', 'color': '#4A90E2', 'orden': 4},
    {'nombre': 'Conferencias', 'icono': 'forum', 'color': '#9B59B6', 'orden': 5},
    {'nombre': 'Gastronomía', 'icono': 'restaurant', 'color': '#F1C40F', 'orden': 6},
    {'nombre': 'Deportes', 'icono': 'sports_soccer', 'color': '#2ECC71', 'orden': 7},
    {'nombre': 'Eventos familiares', 'icono': 'family_history', 'color': '#E67E22', 'orden': 8},
    {'nombre': 'Networking', 'icono': 'groups', 'color': '#1ABC9C', 'orden': 9},
    {'nombre': 'Seminario', 'icono': 'school', 'color': '#FFA07A', 'orden': 11},
    {'nombre': 'Taller', 'icono': 'handyman', 'color': '#9370DB', 'orden': 12},
]

for cat in categorias:
    obj, created = CategoriaEvento.objects.update_or_create(
        nombre=cat['nombre'],
        defaults={
            'icono': cat['icono'],
            'color': cat['color'],
            'orden': cat['orden'],
            'activo': True
        }
    )
    if created:
        print(f'✅ Creada categoría: {cat["nombre"]} (ícono: {cat["icono"]})')
    else:
        print(f'🔄 Actualizada categoría: {cat["nombre"]} (ícono: {cat["icono"]})')