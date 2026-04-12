from django.urls import path
from . import views

app_name = 'virtualEvent'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('crear/', views.event_create, name='event_create'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/editar/', views.event_edit, name='event_edit'),
    path('<int:pk>/eliminar/', views.event_delete, name='event_delete'),
    path('<int:event_id>/dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('<int:event_id>/generar-invitacion/', views.generate_invitation, name='generate_invitation'),
    path('evento/<int:event_id>/metrics/', views.event_metrics, name='event_metrics'),  # una sola vez
    path('evento/<int:event_id>/guardar-youtube/', views.save_youtube_embed, name='save_youtube_embed'),
    path('evento/<int:event_id>/heartbeat/', views.update_heartbeat, name='update_heartbeat'),
    path('evento/<int:event_id>/pdf-report/', views.generate_pdf_report, name='generate_pdf_report'),
    
    
    path('upload-material/<int:event_id>/', views.upload_material, name='upload_material'),
]
