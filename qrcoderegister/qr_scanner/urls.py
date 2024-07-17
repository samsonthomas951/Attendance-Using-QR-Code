from django.urls import path
from . import views

urlpatterns = [
    path('', views.scan_qr, name='scan_qr'),
]