from django.urls import path
from . import views

app_name = 've_streaming'

urlpatterns = [
    path('sala/<uuid:unique_link>/', views.waiting_room, name='waiting_room'),
    path('live/<uuid:unique_link>/', views.streaming_room, name='streaming_room'),
    path('api/event-id/<uuid:unique_link>/', views.event_id_by_slug, name='event_id_by_slug'),
]
