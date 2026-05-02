from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('mi-conversacion/', views.obtener_conversacion_usuario, name='mi_conversacion'),
    path('mensajes/<int:conversacion_id>/', views.obtener_mensajes, name='obtener_mensajes'),
    path('enviar/<int:conversacion_id>/', views.enviar_mensaje, name='enviar_mensaje'),
    path('get/', views.obtener_mensajes_chat, name='obtener_mensajes_chat'),
    path('send/', views.enviar_mensaje_chat, name='enviar_mensaje_chat'),
    path('admin-inbox/', views.admin_chat_inbox, name='admin_inbox'),
    path('admin-conversacion/<int:conversacion_id>/', views.admin_chat_conversacion, name='admin_conversacion'),
    # Línea corregida: ahora apunta a la nueva función
    path('contar/', views.contar_mensajes_no_leidos, name='contar_conversaciones'),
    # Nueva ruta para contar mensajes no leídos
    path('contar-no-leidos/', views.contar_mensajes_no_leidos, name='contar_mensajes_no_leidos'),
]