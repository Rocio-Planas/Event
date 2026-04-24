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
]