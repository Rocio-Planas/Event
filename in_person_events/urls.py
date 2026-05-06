from django.urls import path
from . import views

app_name = 'in_person_events'

urlpatterns = [
    path('create-event/', views.create_event_form, name='create_event_form'),
    path('create-event/success/<int:event_id>/', views.success_page, name='success_page'),
    path('dashboard-organizer/<int:event_id>/', views.dashboard_organizer, name='dashboard_organizer'),
    path('dashboard-assistant/<int:event_id>/', views.dashboard_assistant, name='dashboard_assistant'),
    path('dashboard-assistant/<int:event_id>/select-ticket/', views.select_ticket_type, name='select_ticket_type'),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('configure-event/<int:event_id>/', views.configure_event, name='configure_event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('delete-event/', views.delete_page, name='delete_page'),
    path('send-announcement/<int:event_id>/', views.send_announcement, name='send_announcement'),
]