from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('mi-conversacion/', views.obtener_conversacion_usuario, name='mi_conversacion'),
    path('mensajes/<int:conversacion_id>/', views.obtener_mensajes, name='obtener_mensajes'),
    path('enviar/<int:conversacion_id>/', views.enviar_mensaje, name='enviar_mensaje'),
]