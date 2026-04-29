from django.urls import path
from . import views

app_name = 'pe_staff'

urlpatterns = [
    # Dashboard
    path('staff/<int:event_id>/', views.StaffDashboardView.as_view(), name='dashboard'),
    
    # Invitaciones
    path('staff/<int:event_id>/invite/', views.invite_staff, name='invite'),
    path('staff/<int:event_id>/invitations/', views.get_invitations, name='get_invitations'),
    path('staff/<int:event_id>/cancel-invitation/<int:invitation_id>/', views.cancel_invitation, name='cancel_invitation'),
    
    # Aceptar invitación (público)
    path('accept/<uuid:token>/', views.accept_invitation, name='accept_invitation'),
    
    # Gestión de miembros
    path('staff/<int:event_id>/members/', views.get_members, name='get_members'),
    path('staff/<int:event_id>/assign-zone/<int:member_id>/', views.assign_zone, name='assign_zone'),
    path('staff/<int:event_id>/remove-member/<int:member_id>/', views.remove_member, name='remove_member'),
    
    # Detalle por zona
    path('staff/<int:event_id>/zone/<str:zone_name>/', views.ZoneDetailView.as_view(), name='zone_detail'),
]