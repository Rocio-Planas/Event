from django.urls import path
from . import views

app_name = 'pe_inventory'

urlpatterns = [
    # Vista principal del dashboard (ruta: /inventario/<event_id>/)
    path('<int:event_id>/', views.InventoryDashboardView.as_view(), name='stands'),
    
    # Endpoints para CRUD
    path('<int:event_id>/create/', views.create_item, name='create_item'),
    path('<int:event_id>/update/<int:item_id>/', views.update_item, name='update_item'),
    path('<int:event_id>/delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('<int:event_id>/items/', views.get_items, name='get_items'),
]