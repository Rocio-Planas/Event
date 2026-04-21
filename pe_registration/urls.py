from django.urls import path
from . import views

app_name = 'pe_registration'

urlpatterns = [
    path('', views.home, name='home'),
]