from django.urls import path
from . import views

app_name = 'pe_stand'

urlpatterns = [
    path('<int:event_id>/', views.StandDashboardView.as_view(), name='dashboard'),
    path('<int:event_id>/<int:pk>/', views.StandDetailView.as_view(), name='detail'),
    path('api/<int:event_id>/create-stand/', views.create_stand, name='create_stand'),
    path('api/<int:stand_id>/add-staff/', views.add_staff_to_stand, name='add_staff'),
    path('api/<int:stand_id>/remove-staff/', views.remove_staff_from_stand, name='remove_staff'),
    path('api/<int:stand_id>/add-activities/', views.add_activities_to_stand, name='add_activities'),
    path('api/<int:stand_id>/move-activity/', views.move_activity_in_stand, name='move_activity'),
    path('api/<int:stand_id>/remove-activity/', views.remove_activity_from_stand, name='remove_activity'),
    path('api/<int:stand_id>/add-resources/', views.add_resources, name='add_resources'),
    path('<int:stand_id>/update-resource/', views.update_resource, name='update_resource'),
    path('<int:stand_id>/delete-resource/', views.delete_resource, name='delete_resource'),
]