from django.urls import path
from . import views

app_name = 'soil_moisture'

urlpatterns = [
    # Sensor data endpoints (renamed from soil-moisture to data)
    path('data/', views.list_soil_moisture, name='data-list'),
    path('data/filtered/', views.list_soil_moisture_filtered, name='data-filtered'),
    path('data/receive/', views.receive_soil_moisture, name='data-receive'),
    path('data/latest/', views.get_latest_sensor_data, name='data-latest'),
    
    # Motor management endpoints
    path('motors/', views.list_create_motors, name='motors-list'),
    path('motors/bulk-control/', views.bulk_motor_control, name='motors-bulk-control'),
    path('motors/<int:motor_id>/', views.motor_detail, name='motors-detail'),
    path('motors/<int:motor_id>/control/', views.control_motor, name='motors-control'),
    
    # Simple motor info endpoint (no auth, no IDs)
    path('motorsinfo/', views.motors_info, name='motors-info'),
    
    # System mode endpoints
    path('mode/', views.get_system_mode, name='mode-get'),
    path('mode/set/', views.set_system_mode, name='mode-set'),
    
    # Threshold configuration endpoints
    path('config/thresholds/', views.get_thresholds, name='thresholds-get'),
    path('config/thresholds/set/', views.set_thresholds, name='thresholds-set'),
    
    # System status and statistics endpoints
    path('status/', views.get_system_status, name='system-status'),
    path('stats/dashboard/', views.dashboard_stats, name='dashboard-stats'),
    path('health/', views.health_check, name='health-check'),
]
