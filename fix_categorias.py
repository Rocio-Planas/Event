import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CategoriaEvento

# Lista definitiva de categorías correctas
categorias_correctas = [
    {'nombre': 'Conciertos', 'icono': 'mic', 'color': '#FF6B6B', 'orden': 1},
    {'nombre': 'Teatro', 'icono': 'theater_comedy', 'color': '#4ECDC4', 'orden': 2},
    {'nombre': 'Baile', 'icono': 'sports_gymnastics', 'color': '#FF9F4A', 'orden': 3},
    {'nombre': 'Exposiciones', 'icono': 'art_track', 'color': '#4A90E2', 'orden': 4},
    {'nombre': 'Conferencias', 'icono': 'forum', 'color': '#9B59B6', 'orden': 5},
    {'nombre': 'Gastronomía', 'icono': 'restaurant', 'color': '#F1C40F', 'orden': 6},
    {'nombre': 'Deportes', 'icono': 'sports_soccer', 'color': '#2ECC71', 'orden': 7},
    {'nombre': 'Eventos familiares', 'icono': 'family_history', 'color': '#E67E22', 'orden': 8},
    {'nombre': 'Networking', 'icono': 'groups', 'color': '#1ABC9C', 'orden': 9},
    {'nombre': 'Eventos virtuales', 'icono': 'videocam', 'color': '#3498DB', 'orden': 10},
]

# Nombres incorrectos que queremos eliminar
nombres_incorrectos = [
    'Exposicións',      # con s al final
    'GastronomAa',      # con A mayúscula extra
    'Gastronomía',      # este es correcto, pero lo reemplazaremos también
]

print("🔧 Limpiando categorías duplicadas e incorrectas...")

# Eliminar categorías con nombres incorrectos (incluyendo el correcto para luego recrearlo)
for nombre in nombres_incorrectos:
    deleted, _ = CategoriaEvento.objects.filter(nombre=nombre).delete()
    if deleted:
        print(f"  ✓ Eliminada categoría incorrecta: '{nombre}'")

# También eliminar cualquier otra categoría que no esté en la lista correcta (opcional)
# Para evitar duplicados, borramos todas y las recreamos limpiamente
CategoriaEvento.objects.all().delete()
print("  ✓ Todas las categorías eliminadas. Se recrearán limpiamente.")

# Insertar las categorías correctas
for cat in categorias_correctas:
    obj, created = CategoriaEvento.objects.get_or_create(
        nombre=cat['nombre'],
        defaults={
            'icono': cat['icono'],
            'color': cat['color'],
            'orden': cat['orden'],
            'activo': True
        }
    )
    # Si ya existía (por algún resto), actualizamos
    if not created:
        obj.icono = cat['icono']
        obj.color = cat['color']
        obj.orden = cat['orden']
        obj.activo = True
        obj.save()
        print(f"  ♻️ Actualizada categoría: {cat['nombre']}")
    else:
        print(f"  ✅ Creada categoría: {cat['nombre']} (ícono: {cat['icono']})")

print("\n🎉 ¡Categorías corregidas exitosamente!")