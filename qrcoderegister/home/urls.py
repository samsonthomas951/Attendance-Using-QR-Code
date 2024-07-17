from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.auth import views as auht_views
urlpatterns = [
    path('',views.frontpage, name="frontpage"),
    path('signup/',views.signup, name= "signup"),
    path('accounts/login/', auht_views.LoginView.as_view(template_name='login.html'), name="login"),
    path('logout/',views.logout_view, name='logout'),
    path('register/',views.register, name='register'),
    path('qr-code/', views.serve_qr_code, name='serve_qr_code'),
    path('api/register-attendance/', views.validate_attendance, name='register_attendance'),
    path('export/', views.export_to_excel, name='export_to_excel'),
    #path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('upload/', views.upload_file, name='upload_file'),
    path('attendance-stats/', views.attendance_stats, name='attendance_stats'),
    # path('<slug:slug>/',views.register, name='register')
    path('poll/', views.poll_view, name='poll'),
]

