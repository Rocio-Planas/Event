from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('suscribirse/', views.suscribirse, name='suscribirse'),
    path('cancelar-suscripcion/<int:suscripcion_id>/', views.cancelar_suscripcion, name='cancelar_suscripcion'),
    path('evento/<int:evento_id>/', views.detalle_evento, name='detalle_evento'),
    path('contacto/', views.contacto_view, name='contacto'),
    path('about/', views.about_view, name='about'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
]