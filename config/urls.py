"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language  # noqa: F401
# ❌ Comenta esta línea porque ya no la usamos
# from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('core.urls')),
    path('', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    
    # ✅ Comentado - ya usamos nuestras propias vistas de recuperación
    # path('password-reset/', include('django.contrib.auth.urls')),
    
    path('chat/', include('chat.urls')),
    path("cookies/", include("cookie_consent.urls")),

    # Eventos virtuales
    path('eventos/', include('virtualEvent.urls', namespace='virtualEvent')),
    path('streaming/', include('ve_streaming.urls')),
    path('chat/', include('ve_chat.urls')),
    path('invitacion/', include('ve_invitations.urls')),
    
    # Eventos presenciales
    path('eventos-presenciales/', include('in_person_events.urls', namespace='in_person_events')),
    path('tickets/', include('pe_registration.urls', namespace='pe_registration')),
    path('agenda/', include('pe_agenda.urls', namespace='pe_agenda')),
    path('inventario/', include('pe_inventory.urls', namespace='pe_inventory')),
    path('stands/', include('pe_stand.urls', namespace='pe_stand')),
    path('equipo/', include('pe_staff.urls', namespace='pe_staff')),
    path('analytics/', include('pe_analytics.urls', namespace='pe_analytics')),
    path('encuestas/', include('pe_surveys.urls', namespace='pe_surveys')),
    path('comunicacion/', include('pe_communication.urls')),

    # ❌ ELIMINA o COMENTA esta línea - está causando conflicto
    # Tu login ya está en usuarios.urls con la ruta 'login/'
    # path('accounts/login/', auth_views.LoginView.as_view(
    #     template_name='usuarios/login.html',
    #     redirect_authenticated_user=True
    # ), name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)