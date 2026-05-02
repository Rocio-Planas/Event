from django.urls import path
from . import views

app_name = 'pe_registration'

urlpatterns = [
    path('', views.home, name='home'),
    path('attendees/<int:event_id>/', views.AttendeesView.as_view(), name='attendees'),
    path('api/attendees/<int:event_id>/', views.get_attendees, name='get_attendees'),
    path('api/attendees/<int:event_id>/update/<int:registration_id>/', views.update_registration, name='update_registration'),
    path('api/attendees/<int:event_id>/delete/<int:registration_id>/', views.delete_registration, name='delete_registration'),
]