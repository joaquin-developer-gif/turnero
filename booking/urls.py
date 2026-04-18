from django.urls import path
from . import views

urlpatterns = [
    # Wizard de reserva (Crear o Modificar)
    path('', views.booking_wizard, name='booking_wizard'),
    path('reprogramar/<uuid:token>/', views.booking_wizard, name='reprogram_appointment'),
    
    # API para horarios
    path('api/times/<str:date_str>/', views.get_available_times, name='get_available_times'),
    
    # Gestión de turno
    path('exito/', views.booking_success, name='booking_success'),
    path('exito/<uuid:token>/', views.booking_success, name='booking_success_with_token'),
    path('mi-turno/<uuid:token>/', views.manage_appointment, name='manage_appointment'),
    path('cancelar/<uuid:token>/', views.cancel_appointment, name='cancel_appointment'),
    
    # Admin Pro
    path('admin/calendario/', views.admin_calendar_view, name='admin_calendar'),
    path('admin/calendario/events/', views.admin_calendar_events, name='admin_calendar_events'),
]
