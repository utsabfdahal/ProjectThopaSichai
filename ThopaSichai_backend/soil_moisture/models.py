import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


# ==========================================
# Abstract Base Models
# ==========================================

class TimeStampedModel(models.Model):
    """Abstract base model with created_at and updated_at fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# ==========================================
# Sensor Model
# ==========================================

class Sensor(TimeStampedModel):
    """
    Model to store sensor node information.
    Central entity - auto-created when unique nodeid arrives.
    """
    nodeid = models.CharField(
        max_length=100,
        unique=True,
        primary_key=True,
        db_index=True,
        help_text="Unique sensor node identifier (e.g., 'sensor_zone1')"
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional human-readable name for the sensor"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this sensor is currently active"
    )
    
    class Meta:
        db_table = 'Sensor'
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensors'
        ordering = ['nodeid']
    
    def __str__(self):
        return f"Sensor: {self.nodeid}" + (f" ({self.name})" if self.name else "")


# ==========================================
# Motor Model
# ==========================================

class Motor(TimeStampedModel):
    """
    Model to store motor information and current state.
    Motors are mapped to sensors via ForeignKey.
    """
    class State(models.TextChoices):
        ON = 'ON', 'On'
        OFF = 'OFF', 'Off'
    
    id = models.AutoField(primary_key=True)
    sensor = models.OneToOneField(
        Sensor,
        on_delete=models.CASCADE,
        related_name='motor',
        help_text="Sensor this motor is mapped to (1:1 relationship)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Human-readable name for the motor (e.g., 'Pump 1', 'Zone A Motor')"
    )
    state = models.CharField(
        max_length=3,
        choices=State.choices,
        default=State.OFF,
        help_text="Current state of the motor (ON/OFF)"
    )
    
    class Meta:
        db_table = 'Motor'
        ordering = ['id']
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['name']),
            models.Index(fields=['sensor']),
        ]
    
    def __str__(self):
        return f"{self.name} (sensor: {self.sensor.nodeid}) - {self.state}"
    
    def turn_on(self):
        """Turn motor ON."""
        if self.state != self.State.ON:
            self.state = self.State.ON
            self.save(update_fields=['state', 'updated_at'])
    
    def turn_off(self):
        """Turn motor OFF."""
        if self.state != self.State.OFF:
            self.state = self.State.OFF
            self.save(update_fields=['state', 'updated_at'])
    
    def toggle(self):
        """Toggle motor state."""
        self.state = self.State.OFF if self.state == self.State.ON else self.State.ON
        self.save(update_fields=['state', 'updated_at'])
    
    @property
    def is_on(self):
        """Check if motor is currently ON."""
        return self.state == self.State.ON


# ==========================================
# System Mode Model
# ==========================================

class SystemMode(models.Model):
    """
    Model to store system mode (manual or automatic).
    Singleton pattern - should only have one record.
    """
    class Mode(models.TextChoices):
        MANUAL = 'MANUAL', 'Manual'
        AUTOMATIC = 'AUTOMATIC', 'Automatic'
    
    id = models.AutoField(primary_key=True)
    mode = models.CharField(
        max_length=10,
        choices=Mode.choices,
        default=Mode.AUTOMATIC,
        help_text="System mode: MANUAL or AUTOMATIC"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'SystemMode'
        verbose_name = 'System Mode'
        verbose_name_plural = 'System Mode'
    
    def __str__(self):
        return f"System Mode: {self.get_mode_display()}"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)."""
        self.id = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of singleton."""
        raise ValidationError("Cannot delete system mode. Use update instead.")
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance."""
        instance, created = cls.objects.get_or_create(
            id=1,
            defaults={'mode': cls.Mode.AUTOMATIC}
        )
        return instance
    
    @classmethod
    def get_current_mode(cls):
        """Get current system mode."""
        return cls.get_instance().mode
    
    @classmethod
    def set_mode(cls, new_mode):
        """Set the system mode."""
        if new_mode not in cls.Mode.values:
            raise ValueError(f"Mode must be one of: {', '.join(cls.Mode.values)}")
        
        instance = cls.get_instance()
        instance.mode = new_mode
        instance.save()
        return instance
    
    @classmethod
    def is_manual(cls):
        """Check if system is in manual mode."""
        return cls.get_current_mode() == cls.Mode.MANUAL
    
    @classmethod
    def is_automatic(cls):
        """Check if system is in automatic mode."""
        return cls.get_current_mode() == cls.Mode.AUTOMATIC


# ==========================================
# Soil Moisture Model
# ==========================================

class SoilMoisture(TimeStampedModel):
    """
    Model to store soil moisture data with validation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='readings',
        help_text="Sensor that recorded this reading"
    )
    value = models.FloatField(
        validators=[
            MinValueValidator(0.0, message="Moisture value cannot be negative"),
            MaxValueValidator(100.0, message="Moisture value cannot exceed 100%")
        ],
        help_text="Soil moisture value (percentage 0-100)"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Timestamp when the reading was taken"
    )
    ip_address = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        help_text="IP address of the device sending data"
    )
    
    class Meta:
        db_table = 'SoilMoisture'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['sensor']),
            models.Index(fields=['ip_address']),
        ]
        verbose_name = 'Soil Moisture Reading'
        verbose_name_plural = 'Soil Moisture Readings'
    
    def __str__(self):
        return f"{self.sensor.nodeid} - {self.value}% at {self.timestamp}"
    
    @property
    def moisture_status(self):
        """Get human-readable moisture status."""
        if self.value < 30:
            return 'DRY'
        elif self.value < 60:
            return 'OPTIMAL'
        elif self.value < 80:
            return 'WET'
        else:
            return 'SATURATED'
    
    @property
    def age_seconds(self):
        """Get age of reading in seconds."""
        return (timezone.now() - self.created_at).total_seconds()
    
    @classmethod
    def get_latest_by_sensor(cls, sensor):
        """Get latest reading for a specific sensor."""
        return cls.objects.filter(sensor=sensor).order_by('-timestamp').first()
    
    @classmethod
    def get_average_value(cls, sensor=None, hours=24):
        """Get average moisture value for last N hours."""
        from django.db.models import Avg
        from datetime import timedelta
        
        queryset = cls.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=hours)
        )
        
        if sensor:
            queryset = queryset.filter(sensor=sensor)
        
        result = queryset.aggregate(avg=Avg('value'))
        return result['avg'] or 0.0


# ==========================================
# Threshold Configuration Model
# ==========================================

class ThresholdConfig(models.Model):
    """
    Model to store moisture threshold configuration per sensor.
    Each sensor has its own threshold configuration.
    Motor turns ON when moisture value exceeds threshold.
    """
    sensor = models.OneToOneField(
        Sensor,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='threshold',
        help_text="Sensor this threshold config applies to (1:1 relationship)"
    )
    threshold = models.FloatField(
        default=50.0,
        validators=[
            MinValueValidator(0.0, message="Threshold cannot be negative"),
            MaxValueValidator(100.0, message="Threshold cannot exceed 100%")
        ],
        help_text="Motor turns ON when moisture value exceeds this threshold"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ThresholdConfig'
        verbose_name = 'Threshold Configuration'
        verbose_name_plural = 'Threshold Configuration'
    
    def __str__(self):
        return f"Threshold for {self.sensor.nodeid}: {self.threshold}%"
        super().save(*args, **kwargs)
    
    @classmethod
    def get_or_create_for_sensor(cls, sensor):
        """Get or create a threshold config instance for a sensor."""
        instance, created = cls.objects.get_or_create(
            sensor=sensor,
            defaults={'threshold': 50.0}
        )
        return instance
    
    @classmethod
    def get_threshold(cls, sensor):
        """Get threshold for a specific sensor."""
        instance = cls.get_or_create_for_sensor(sensor)
        return instance.threshold
    
    @classmethod
    def set_threshold(cls, sensor, threshold):
        """Set new threshold value for a sensor."""
        if threshold < 0 or threshold > 100:
            raise ValueError("Threshold must be between 0 and 100")
        
        instance = cls.get_or_create_for_sensor(sensor)
        instance.threshold = threshold
        instance.save()
        return instance

