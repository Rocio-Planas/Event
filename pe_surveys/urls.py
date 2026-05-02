from django.urls import path
from . import views

app_name = 'pe_surveys'

urlpatterns = [
    path('', views.SurveyManagementView.as_view(), name='survey_list'),
    path('create/', views.SurveyCreateUpdateView.as_view(), name='survey_create'),
    path('edit/<int:pk>/', views.SurveyCreateUpdateView.as_view(), name='survey_edit'),
    path('delete/<int:pk>/', views.SurveyDeleteView.as_view(), name='survey_delete'),
    path('toggle/<int:pk>/', views.SurveyToggleView.as_view(), name='survey_toggle'),
    path('api/send-survey/<int:pk>/', views.SendSurveyAPIView.as_view(), name='send_survey'),
    path('results/<int:pk>/', views.SurveyResultsView.as_view(), name='survey_results'),
]