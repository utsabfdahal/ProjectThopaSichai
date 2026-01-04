#!/usr/bin/env python3
"""
Create motors and test full system
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ThopaSichai_backend.settings')
django.setup()

from soil_moisture.models import Sensor, Motor, ThresholdConfig, SoilMoisture

def setup_system():
    """Create motors for existing sensors"""
    print("=" * 60)
    print("SETTING UP MOTORS FOR SENSORS")
    print("=" * 60)
    
    # Get all sensors
    sensors = Sensor.objects.all()
    print(f"\nFound {sensors.count()} sensors:")
    for sensor in sensors:
        print(f"  - {sensor.nodeid}")
    
    # Create motors for each sensor
    motors_created = []
    for i, sensor in enumerate(sensors, 1):
        try:
            motor, created = Motor.objects.get_or_create(
                sensor=sensor,
                defaults={
                    'name': f'Pump {i}',
                    'state': 'OFF'
                }
            )
            if created:
                print(f"\n✓ Created motor: {motor.name} for sensor {sensor.nodeid}")
                motors_created.append(motor)
            else:
                print(f"\n- Motor already exists: {motor.name} for sensor {sensor.nodeid}")
                motors_created.append(motor)
            
            # Create threshold config
            threshold, t_created = ThresholdConfig.objects.get_or_create(
                sensor=sensor,
                defaults={
                    'low_threshold': 30.0,
                    'high_threshold': 70.0
                }
            )
            if t_created:
                print(f"  ✓ Created threshold config: {threshold.low_threshold}% - {threshold.high_threshold}%")
            else:
                print(f"  - Threshold config exists: {threshold.low_threshold}% - {threshold.high_threshold}%")
                
        except Exception as e:
            print(f"\n❌ Error creating motor for {sensor.nodeid}: {e}")
    
    print("\n" + "=" * 60)
    print("SYSTEM STATUS")
    print("=" * 60)
    print(f"\nSensors: {Sensor.objects.count()}")
    print(f"Motors: {Motor.objects.count()}")
    print(f"Threshold Configs: {ThresholdConfig.objects.count()}")
    print(f"Sensor Readings: {SoilMoisture.objects.count()}")
    
    # Show mapping
    print("\n" + "=" * 60)
    print("SENSOR → MOTOR MAPPING")
    print("=" * 60)
    for motor in Motor.objects.select_related('sensor').all():
        print(f"\n{motor.sensor.nodeid} → {motor.name} ({motor.state})")
        try:
            threshold = motor.sensor.threshold
            print(f"  Thresholds: {threshold.low_threshold}% - {threshold.high_threshold}%")
        except:
            print(f"  Thresholds: Not configured")
    
    return motors_created

if __name__ == '__main__':
    setup_system()
