from django.urls import path
from . import views

app_name = 'in_person_events'

urlpatterns = [
    path('', views.home, name='home'),
    path('create-event/', views.create_event_form, name='create_event_form'),
    path('create-event/success/<int:event_id>/', views.success_page, name='success_page'),
    path('dashboard-organizer/<int:event_id>/', views.dashboard_organizer, name='dashboard_organizer'),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit_event'),
]