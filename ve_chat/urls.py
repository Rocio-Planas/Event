from django.urls import path
from . import views

app_name = 've_chat'

urlpatterns = [
    # Chat
    path('api/<slug:room_slug>/send/', views.send_message, name='send_message'),
    path('api/<slug:room_slug>/messages/', views.get_messages, name='get_messages'),
    path('api/<slug:room_slug>/pin/<int:message_id>/', views.pin_message, name='pin_message'),

    # Manos
    path('api/<slug:room_slug>/raise/', views.raise_hand, name='raise_hand'),
    path('api/<slug:room_slug>/hands/', views.get_hands, name='get_hands'),
    path('api/<slug:room_slug>/attend/<int:user_id>/', views.attend_hand, name='attend_hand'),

    # Encuestas
    path('api/<slug:room_slug>/poll/create/', views.create_poll, name='create_poll'),
    path('api/<slug:room_slug>/poll/<int:poll_id>/vote/', views.vote_poll, name='vote_poll'),
    path('api/<slug:room_slug>/poll/<int:poll_id>/results/', views.get_poll_results, name='poll_results'),
    path('api/<slug:room_slug>/poll/active/', views.get_active_poll, name='active_poll'),

    # Satisfacción
    path('api/<slug:room_slug>/satisfaction/', views.satisfaction_rating, name='satisfaction_rating'),
]
