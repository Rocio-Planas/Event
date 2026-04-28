from django.urls import path
from . import views

app_name = 'pe_stand'

urlpatterns = [
    path('<int:event_id>/', views.StandDashboardView.as_view(), name='dashboard'),
    path('<int:event_id>/<int:pk>/', views.StandDetailView.as_view(), name='detail'),
    path('api/<int:event_id>/create-stand/', views.create_stand, name='create_stand'),
    path('stands/<int:stand_id>/update-resource/', views.update_resource, name='update_resource'),
    path('stands/<int:stand_id>/delete-resource/', views.delete_resource, name='delete_resource'),
]