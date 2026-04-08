# ve_invitations/urls.py
from django.urls import path
from . import views

app_name = "ve_invitations"


urlpatterns = [
    # Ruta existente para invitaciones (si la tienes)
    path("invite/<str:token>/", views.accept_invitation, name="accept_invitation"),
    # Nuevas rutas para seguir eventos
    path("follow/<int:event_id>/", views.follow_event, name="follow_event"),
    path(
        "follow-ajax/<int:event_id>/", views.follow_event_ajax, name="follow_event_ajax"
    ),
]
