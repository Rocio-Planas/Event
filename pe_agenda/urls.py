from django.urls import path
from . import views

app_name = 'pe_agenda'

urlpatterns = [
    path('activities/<int:event_id>/', views.activities, name='activities'),
    path('activities/<int:event_id>/create/', views.create_activity, name='create_activity'),
    path('activities/<int:event_id>/edit/<int:activity_id>/', views.edit_activity, name='edit_activity'),
    path('activities/<int:event_id>/cancel/<int:activity_id>/', views.cancel_activity, name='cancel_activity'),
    path('activities/<int:event_id>/delete/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    path('activities/<int:event_id>/view/<int:activity_id>/', views.view_activity, name='view_activity'),
    path('activities/<int:event_id>/info/<int:activity_id>/', views.info_activity, name='info_activity'),
    path('chronogram-assistant/<int:event_id>/', views.chronogram_assistant, name='chronogram_assistant'),
    path('api/activities/<int:event_id>/', views.get_activities_json, name='get_activities_json'),
]
