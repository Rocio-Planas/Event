from django.urls import path
from . import views
from . import registration_views

app_name = 'pe_registration'

urlpatterns = [
    path('', views.home, name='home'),
    path('attendees/<int:event_id>/', views.AttendeesView.as_view(), name='attendees'),
    path('api/attendees/<int:event_id>/', views.get_attendees, name='get_attendees'),
    path('api/attendees/<int:event_id>/update/<int:registration_id>/', views.update_registration, name='update_registration'),
    path('api/attendees/<int:event_id>/delete/<int:registration_id>/', views.delete_registration, name='delete_registration'),
    path('api/register/<int:event_id>/', registration_views.register_to_event, name='register_to_event'),
    path('api/waitlist/<int:event_id>/', views.get_waitlist, name='get_waitlist'),
    path('api/waitlist/<int:event_id>/promote/', views.promote_from_waitlist, name='promote_from_waitlist'),
    path('api/waitlist/<int:event_id>/remove/<int:waitlist_id>/', views.remove_from_waitlist, name='remove_from_waitlist'),
]