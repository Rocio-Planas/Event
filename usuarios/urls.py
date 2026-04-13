from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recuperar-password/', views.recuperar_password_view, name='recuperar_password'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    path('perfil/cambiar-password/', views.cambiar_password_view, name='cambiar_password'),
    path('perfil/preferencias/', views.editar_preferencias, name='editar_preferencias'),
    path('contacto/', views.contacto_view, name='contacto'),
    # NUEVO: dashboard unificado (ya no usamos dashboard_redirect)
    path('dashboard/', views.dashboard_unificado, name='dashboard'),
    # Las siguientes rutas se mantienen por si quieres acceso directo, pero ya no son el punto de entrada principal
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/organizador/', views.dashboard_organizador, name='dashboard_organizador'),
    path('dashboard/expositor/', views.dashboard_expositor, name='dashboard_expositor'),
    path('dashboard/espectador/', views.dashboard_espectador, name='dashboard_espectador'),
    path('dashboard/metricas/', views.dashboard_metrics, name='dashboard_metrics'),
]