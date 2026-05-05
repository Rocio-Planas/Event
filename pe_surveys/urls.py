from django.urls import path
from . import views

app_name = 'pe_surveys'

urlpatterns = [
    path('<int:event_id>/', views.SurveyManagementView.as_view(), name='survey_list'),
    path('<int:event_id>/create/', views.SurveyCreateUpdateView.as_view(), name='survey_create'),
    path('<int:event_id>/edit/<int:pk>/', views.SurveyCreateUpdateView.as_view(), name='survey_edit'),
    path('<int:event_id>/delete/<int:pk>/', views.SurveyDeleteView.as_view(), name='survey_delete'),
    path('<int:event_id>/toggle/<int:pk>/', views.SurveyToggleView.as_view(), name='survey_toggle'),
    path('<int:event_id>/api/send-survey/<int:pk>/', views.SendSurveyAPIView.as_view(), name='send_survey'),
    path('<int:event_id>/api/update-survey/', views.UpdateSurveyAPIView.as_view(), name='update_survey'),
    path('<int:event_id>/api/delete-survey/', views.DeleteSurveyAPIView.as_view(), name='delete_survey'),
    path('<int:event_id>/results/<int:pk>/', views.SurveyResultsView.as_view(), name='survey_results'),
    path('<int:event_id>/responder/<int:survey_id>/', views.SurveyAnswerView.as_view(), name='survey_answer'),
    path('<int:event_id>/responder/<int:survey_id>/api/', views.SurveyResponseAPIView.as_view(), name='survey_response'),
]