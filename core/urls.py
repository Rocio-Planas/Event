# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('suscribirse/', views.suscribirse, name='suscribirse'),
    path('cancelar-suscripcion/<int:suscripcion_id>/', views.cancelar_suscripcion, name='cancelar_suscripcion'),
    path('contacto/', views.contacto_view, name='contacto'),
    path('about/', views.about_view, name='about'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('cancelar-suscripcion-virtual/<int:evento_id>/', views.cancelar_suscripcion_virtual, name='cancelar_suscripcion_virtual'),
    path('aviso-legal/', views.aviso_legal_view, name='aviso_legal'),
    path('politica-cookies/', views.politica_cookies_view, name='politica_cookies'),
    path('toggle-favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('toggle-favorito-presencial/', views.toggle_favorito_presencial, name='toggle_favorito_presencial'),
    path('eventos-presenciales/<int:evento_id>/', views.detalle_evento_presencial, name='detalle_evento_presencial'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin-panel/eventos/', views.admin_eventos_pendientes, name='admin_eventos'),
    path('admin-panel/resenas/', views.admin_resenas, name='admin_resenas'),
    path('admin-panel/consultas/', views.admin_consultas, name='admin_consultas'),
    path('admin-panel/aprobar-evento/<int:evento_id>/<str:tipo>/', views.admin_aprobar_evento, name='admin_aprobar_evento'),
    path('admin-panel/rechazar-evento/<int:evento_id>/<str:tipo>/', views.admin_rechazar_evento, name='admin_rechazar_evento'),
    path('admin-panel/aprobar-resena/<int:resena_id>/', views.admin_aprobar_resena, name='admin_aprobar_resena'),
    path('admin-panel/responder-consulta/<int:consulta_id>/', views.admin_responder_consulta, name='admin_responder_consulta'),
    path('admin-panel/cambiar-rol/<int:usuario_id>/', views.admin_cambiar_rol, name='admin_cambiar_rol'),
    path('admin-panel/eliminar-usuario/<int:usuario_id>/', views.admin_eliminar_usuario, name='admin_eliminar_usuario'),
    path('admin-panel/usuarios/crear/', views.admin_crear_usuario, name='admin_crear_usuario'),
    path('admin-panel/usuarios/editar/<int:usuario_id>/', views.admin_editar_usuario, name='admin_editar_usuario'),
]