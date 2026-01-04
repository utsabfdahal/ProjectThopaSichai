import logging
from rest_framework import serializers
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import SoilMoisture, Motor, SystemMode, ThresholdConfig, Sensor

logger = logging.getLogger('soil_moisture')


# ==========================================
# Base Mixins for Common Functionality
# ==========================================

class TimestampMixin:
    """Mixin to add timestamp fields to serializers."""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ChoiceValidationMixin:
    """Mixin to automatically validate choice fields against model choices."""
    
    def validate_choice_field(self, value, field_name):
        """Generic choice field validator."""
        model_field = self.Meta.model._meta.get_field(field_name)
        valid_choices = [choice[0] for choice in model_field.choices]
        
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"{field_name.title()} must be one of: {', '.join(valid_choices)}"
            )
        return value


# ==========================================
# Sensor Serializer
# ==========================================

class SensorSerializer(serializers.ModelSerializer):
    """Serializer for Sensor model."""
    
    class Meta:
        model = Sensor
        fields = ['nodeid', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# ==========================================
# Motor Serializer
# ==========================================

class MotorSerializer(ChoiceValidationMixin, serializers.ModelSerializer):
    """
    Serializer for Motor model with automatic choice validation.
    Motors are mapped to sensors via sensor_nodeid.
    """
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    sensor_nodeid = serializers.CharField(source='sensor.nodeid', read_only=True)
    
    class Meta:
        model = Motor
        fields = ['id', 'name', 'sensor_nodeid', 'state', 'state_display', 'created_at', 'updated_at']
        read_only_fields = ['id', 'sensor_nodeid', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {
                'min_length': 1,
                'max_length': 100,
                'trim_whitespace': True,
                'error_messages': {
                    'blank': 'Motor name cannot be empty',
                    'required': 'Motor name is required',
                }
            },
            'state': {
                'error_messages': {
                    'invalid_choice': "State must be 'ON' or 'OFF'",
                }
            }
        }
    
    def validate_state(self, value):
        """Validate motor state using mixin."""
        return self.validate_choice_field(value, 'state')
    
    def to_representation(self, instance):
        """Customize output representation."""
        data = super().to_representation(instance)
        # Add runtime information
        data['is_on'] = instance.state == 'ON'
        return data


# ==========================================
# System Mode Serializer
# ==========================================

class SystemModeSerializer(ChoiceValidationMixin, serializers.ModelSerializer):
    """
    Serializer for SystemMode with automatic choice validation.
    """
    mode_display = serializers.CharField(source='get_mode_display', read_only=True)
    
    class Meta:
        model = SystemMode
        fields = ['id', 'mode', 'mode_display', 'updated_at']
        read_only_fields = ['id', 'updated_at']
        extra_kwargs = {
            'mode': {
                'error_messages': {
                    'invalid_choice': "Mode must be 'MANUAL' or 'AUTOMATIC'",
                }
            }
        }
    
    def validate_mode(self, value):
        """Validate system mode using mixin."""
        return self.validate_choice_field(value, 'mode')


# ==========================================
# Soil Moisture Serializer
# ==========================================

class SoilMoistureSerializer(serializers.ModelSerializer):
    """
    Serializer for SoilMoisture with built-in validators and cleaner validation.
    """
    # Use DRF's built-in validators for cleaner code
    value = serializers.FloatField(
        validators=[
            MinValueValidator(0.0, message="Moisture value cannot be negative"),
            MaxValueValidator(100.0, message="Moisture value cannot exceed 100%")
        ],
        help_text="Soil moisture percentage (0-100)"
    )
    
    timestamp = serializers.DateTimeField(
        required=False,
        default=timezone.now,
        allow_null=True,
        help_text="Timestamp of the reading"
    )
    
    # Nodeid comes from sensor relationship (read-only)
    nodeid = serializers.CharField(source='sensor.nodeid', read_only=True)
    
    class Meta:
        model = SoilMoisture
        fields = [
            'id', 'nodeid', 'value', 'timestamp', 
            'ip_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'nodeid', 'created_at', 'updated_at']
        extra_kwargs = {
            'ip_address': {'required': False, 'allow_blank': True},
        }
    
    def validate_timestamp(self, value):
        """Minimal timestamp validation - auto-convert naive datetimes."""
        # Auto-convert naive datetime to aware
        if value and not timezone.is_aware(value):
            value = timezone.make_aware(value)
        
        # Just log warning but allow future timestamps (loose system)
        if value and value > timezone.now():
            logger.warning(f"Timestamp in future (accepted): {value}")
        
        return value
        return value
    
    def to_representation(self, instance):
        """Add computed fields to output."""
        data = super().to_representation(instance)
        
        # Add helpful computed fields
        data['moisture_status'] = self._get_moisture_status(instance.value)
        data['age_seconds'] = (timezone.now() - instance.created_at).total_seconds()
        
        return data
    
    @staticmethod
    def _get_moisture_status(value):
        """Categorize moisture level."""
        if value < 30:
            return 'DRY'
        elif value < 60:
            return 'OPTIMAL'
        elif value < 80:
            return 'WET'
        else:
            return 'SATURATED'


# ==========================================
# Convenience Serializers
# ==========================================

class MotorControlSerializer(serializers.Serializer):
    """Serializer for motor control endpoint - cleaner than using request.data directly."""
    state = serializers.ChoiceField(
        choices=['ON', 'OFF'],
        error_messages={
            'invalid_choice': "State must be 'ON' or 'OFF'",
            'required': 'State is required',
        }
    )


class SystemModeSetSerializer(serializers.Serializer):
    """Serializer for setting system mode - with validation."""
    mode = serializers.ChoiceField(
        choices=['MANUAL', 'AUTOMATIC'],
        error_messages={
            'invalid_choice': "Mode must be 'MANUAL' or 'AUTOMATIC'",
            'required': 'Mode is required',
        }
    )


class SensorDataWithMotorSerializer(SoilMoistureSerializer):
    """Extended serializer that includes motor recommendation."""
    motor_recommendation = serializers.SerializerMethodField()
    
    class Meta(SoilMoistureSerializer.Meta):
        fields = SoilMoistureSerializer.Meta.fields + ['motor_recommendation']
    
    def get_motor_recommendation(self, obj):
        """Get motor recommendation based on moisture value."""
        # This will be populated by the view if needed
        return self.context.get('motor_recommendation', None)


# ==========================================
# New Serializers for Additional Endpoints
# ==========================================

class ThresholdConfigSerializer(serializers.ModelSerializer):
    """Serializer for threshold configuration per nodeid."""
    nodeid = serializers.CharField(source='sensor.nodeid', read_only=True)
    
    class Meta:
        model = ThresholdConfig
        fields = ['nodeid', 'threshold', 'updated_at']
        read_only_fields = ['nodeid', 'updated_at']


class BulkMotorControlSerializer(serializers.Serializer):
    """Serializer for bulk motor control."""
    motors = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        help_text="List of motors with id and state"
    )
    
    def validate_motors(self, value):
        """Validate motor control data."""
        for motor_data in value:
            if 'id' not in motor_data:
                raise serializers.ValidationError("Each motor must have an 'id'")
            if 'state' not in motor_data:
                raise serializers.ValidationError("Each motor must have a 'state'")
            if motor_data['state'] not in ['ON', 'OFF']:
                raise serializers.ValidationError("State must be 'ON' or 'OFF'")
        return value


class SystemStatusSerializer(serializers.Serializer):
    """Serializer for combined system status."""
    latest_moisture = SoilMoistureSerializer(read_only=True)
    motors = MotorSerializer(many=True, read_only=True)
    system_mode = SystemModeSerializer(read_only=True)
    thresholds = ThresholdConfigSerializer(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    total_readings = serializers.IntegerField(read_only=True)
    avg_moisture_24h = serializers.FloatField(read_only=True)
    avg_moisture_7d = serializers.FloatField(read_only=True)
    motors_on_count = serializers.IntegerField(read_only=True)
    motors_off_count = serializers.IntegerField(read_only=True)
    system_mode = serializers.CharField(read_only=True)
    last_reading_time = serializers.DateTimeField(read_only=True, allow_null=True)
    unique_nodes = serializers.IntegerField(read_only=True)


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check response."""
    status = serializers.CharField(read_only=True)
    database = serializers.CharField(read_only=True)
    last_sensor_update = serializers.DateTimeField(read_only=True, allow_null=True)
    time_since_last_update = serializers.CharField(read_only=True, allow_null=True)
    motors_count = serializers.IntegerField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)

