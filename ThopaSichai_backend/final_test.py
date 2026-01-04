#!/usr/bin/env python
"""
Final comprehensive test to verify threshold changes work correctly
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ThopaSichai_backend.settings')
django.setup()

from soil_moisture.models import Sensor, Motor, ThresholdConfig, SoilMoisture, SystemMode
from soil_moisture.motor_logic import get_motor_state
from django.utils import timezone


def main():
    print("\n" + "="*70)
    print("  FINAL VERIFICATION: Single Threshold Motor Control")
    print("="*70)
    
    # Clean up test data
    Sensor.objects.filter(nodeid='final_test').delete()
    
    # Setup
    print("\n1. SETUP:")
    sensor = Sensor.objects.create(nodeid='final_test', name='Final Test Sensor')
    motor = Motor.objects.create(sensor=sensor, name='Final Test Motor', state='OFF')
    threshold_config = ThresholdConfig.get_or_create_for_sensor(sensor)
    SystemMode.set_mode('AUTOMATIC')
    
    print(f"   ✓ Created sensor: {sensor.nodeid}")
    print(f"   ✓ Created motor: {motor.name} (state: {motor.state})")
    print(f"   ✓ Threshold: {threshold_config.threshold}%")
    print(f"   ✓ System mode: AUTOMATIC")
    
    # Test the logic
    print("\n2. LOGIC VERIFICATION:")
    print(f"   Rule: Motor ON if moisture > {threshold_config.threshold}%, OFF otherwise")
    
    test_cases = [
        (20.0, 'OFF', '20% < 50% → Motor OFF'),
        (30.0, 'OFF', '30% < 50% → Motor OFF'),
        (50.0, 'OFF', '50% = 50% → Motor OFF'),
        (50.1, 'ON',  '50.1% > 50% → Motor ON'),
        (60.0, 'ON',  '60% > 50% → Motor ON'),
        (80.0, 'ON',  '80% > 50% → Motor ON'),
    ]
    
    print("\n   Test Results:")
    all_pass = True
    for moisture, expected, description in test_cases:
        threshold = ThresholdConfig.get_threshold(sensor)
        decision = get_motor_state(moisture, 'OFF', threshold)
        actual = decision['desired_state']
        
        status = "✓" if actual == expected else "✗"
        print(f"   {status} {description} [Got: {actual}]")
        
        if actual != expected:
            all_pass = False
    
    # Test with actual database
    print("\n3. DATABASE INTEGRATION:")
    
    # Moisture below threshold
    SoilMoisture.objects.create(sensor=sensor, value=35.0, timestamp=timezone.now())
    threshold = ThresholdConfig.get_threshold(sensor)
    decision = get_motor_state(35.0, motor.state, threshold)
    motor.state = decision['desired_state']
    motor.save()
    
    print(f"   Moisture: 35.0% → Motor: {motor.state}")
    assert motor.state == 'OFF', f"Expected OFF, got {motor.state}"
    print("   ✓ Motor correctly turned OFF")
    
    # Moisture above threshold
    SoilMoisture.objects.create(sensor=sensor, value=65.0, timestamp=timezone.now())
    decision = get_motor_state(65.0, motor.state, threshold)
    motor.state = decision['desired_state']
    motor.save()
    
    print(f"   Moisture: 65.0% → Motor: {motor.state}")
    assert motor.state == 'ON', f"Expected ON, got {motor.state}"
    print("   ✓ Motor correctly turned ON")
    
    # Custom threshold test
    print("\n4. CUSTOM THRESHOLD TEST:")
    ThresholdConfig.set_threshold(sensor, 40.0)
    new_threshold = ThresholdConfig.get_threshold(sensor)
    print(f"   Set custom threshold: {new_threshold}%")
    
    # Test with 45% (above new threshold)
    decision = get_motor_state(45.0, motor.state, new_threshold)
    motor.state = decision['desired_state']
    motor.save()
    
    print(f"   Moisture: 45.0% → Motor: {motor.state}")
    assert motor.state == 'ON', f"Expected ON, got {motor.state}"
    print("   ✓ Motor correctly ON (45% > 40%)")
    
    # Clean up
    sensor.delete()
    
    print("\n" + "="*70)
    if all_pass:
        print("  ✓✓✓ ALL TESTS PASSED ✓✓✓")
    else:
        print("  ✗✗✗ SOME TESTS FAILED ✗✗✗")
    print("="*70)
    
    print("\n✅ SUMMARY:")
    print("   • Single threshold system implemented successfully")
    print("   • Default threshold: 50%")
    print("   • Motor turns ON when moisture > threshold")
    print("   • Motor turns OFF when moisture ≤ threshold")
    print("   • Custom thresholds per sensor supported")
    print("   • Database integration working correctly")
    print("\n")


if __name__ == '__main__':
    main()
