from django.urls import path
from . import views

urlpatterns = [
    path('', views.fetch_uksi_data, name='fetch_uksi_data'),
]