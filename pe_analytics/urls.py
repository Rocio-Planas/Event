from django.urls import path
from . import views

app_name = 'pe_analytics'

urlpatterns = [
    path('dashboard/<int:event_id>/', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('api/stats/<int:event_id>/', views.AnalyticsStatsAPIView.as_view(), name='stats_api'),
    path('export/<int:event_id>/', views.ExportReportView.as_view(), name='export_report'),
]