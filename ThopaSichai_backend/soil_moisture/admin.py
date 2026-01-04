from django.contrib import admin
from django.utils.html import format_html
from .models import SoilMoisture, Motor, SystemMode, ThresholdConfig, Sensor


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('nodeid', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('nodeid', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SoilMoisture)
class SoilMoistureAdmin(admin.ModelAdmin):
    list_display = ('get_nodeid', 'value', 'timestamp', 'ip_address', 'created_at')
    list_filter = ('timestamp', 'sensor', 'ip_address')
    search_fields = ('sensor__nodeid', 'ip_address', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-timestamp',)
    
    def get_nodeid(self, obj):
        return obj.sensor.nodeid
    get_nodeid.short_description = 'Node ID'
    
    fieldsets = (
        ('Sensor Information', {
            'fields': ('id', 'sensor', 'value', 'timestamp')
        }),
        ('Network Information', {
            'fields': ('ip_address',)
        }),
        ('System Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('sensor')


@admin.register(Motor)
class MotorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state_badge', 'updated_at')
    list_filter = ('state',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    def state_badge(self, obj):
        """Display state with color badge"""
        if obj.state == 'ON':
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
                obj.state
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
                obj.state
            )
    state_badge.short_description = 'State'


@admin.register(SystemMode)
class SystemModeAdmin(admin.ModelAdmin):
    list_display = ('id', 'mode_badge', 'updated_at')
    readonly_fields = ('id', 'updated_at')
    
    def mode_badge(self, obj):
        """Display mode with color badge"""
        if obj.mode == 'AUTOMATIC':
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
                obj.mode
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 3px;">{}</span>',
                obj.mode
            )
    mode_badge.short_description = 'Mode'
    
    def has_add_permission(self, request):
        """Prevent adding multiple system mode records"""
        return not SystemMode.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion"""
        return False


@admin.register(ThresholdConfig)
class ThresholdConfigAdmin(admin.ModelAdmin):
    list_display = ('get_sensor_nodeid', 'threshold', 'updated_at')
    readonly_fields = ('sensor', 'updated_at')
    
    def get_sensor_nodeid(self, obj):
        return obj.sensor.nodeid
    get_sensor_nodeid.short_description = 'Sensor Node ID'
    
    fieldsets = (
        ('Sensor', {
            'fields': ('sensor',)
        }),
        ('Threshold Configuration', {
            'fields': ('threshold',),
            'description': 'Motor turns ON when moisture exceeds this threshold'
        }),
        ('System Information', {
            'fields': ('updated_at',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent adding multiple threshold config records"""
        return not ThresholdConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion"""
        return False
