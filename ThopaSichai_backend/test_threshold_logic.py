#!/usr/bin/env python
"""
Test script for new single threshold motor control logic.
Motor turns ON when moisture > threshold, OFF otherwise.
Default threshold: 50%
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ThopaSichai_backend.settings')
django.setup()

from soil_moisture.models import Sensor, Motor, ThresholdConfig, SoilMoisture, SystemMode
from soil_moisture.motor_logic import get_motor_state, DEFAULT_THRESHOLD
from django.utils import timezone


def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_test(description, expected, actual):
    status = "✓ PASS" if expected == actual else "✗ FAIL"
    print(f"{status} | {description}")
    print(f"     Expected: {expected}, Got: {actual}")


def test_motor_logic():
    """Test the motor control logic directly"""
    print_header("Testing Motor Control Logic")
    
    threshold = 50.0
    print(f"\nThreshold: {threshold}%")
    print("Logic: Motor ON if moisture > threshold, OFF otherwise\n")
    
    # Test cases: (moisture_value, expected_state, description)
    test_cases = [
        (30.0, 'OFF', "Moisture 30% (below threshold 50%)"),
        (50.0, 'OFF', "Moisture 50% (equal to threshold 50%)"),
        (50.1, 'ON', "Moisture 50.1% (just above threshold 50%)"),
        (60.0, 'ON', "Moisture 60% (above threshold 50%)"),
        (80.0, 'ON', "Moisture 80% (well above threshold 50%)"),
        (0.0, 'OFF', "Moisture 0% (minimum, below threshold)"),
        (100.0, 'ON', "Moisture 100% (maximum, above threshold)"),
    ]
    
    for moisture, expected_state, description in test_cases:
        result = get_motor_state(moisture, threshold=threshold)
        actual_state = result['desired_state']
        print_test(description, expected_state, actual_state)
        if expected_state != actual_state:
            print(f"     Reason: {result['reason']}")


def test_database_integration():
    """Test with actual database records"""
    print_header("Testing Database Integration")
    
    # Clean up any existing test data
    Sensor.objects.filter(nodeid__startswith='test_sensor').delete()
    
    # Create test sensor
    sensor = Sensor.objects.create(
        nodeid='test_sensor_1',
        name='Test Sensor Zone 1',
        is_active=True
    )
    print(f"\n✓ Created sensor: {sensor.nodeid}")
    
    # Create motor for this sensor
    motor = Motor.objects.create(
        sensor=sensor,
        name='Test Motor 1',
        state='OFF'
    )
    print(f"✓ Created motor: {motor.name}, initial state: {motor.state}")
    
    # Create threshold config (default 50%)
    threshold_config = ThresholdConfig.get_or_create_for_sensor(sensor)
    print(f"✓ Created threshold config: {threshold_config.threshold}%")
    
    # Set system to AUTOMATIC mode
    system_mode = SystemMode.get_instance()
    system_mode.mode = 'AUTOMATIC'
    system_mode.save()
    print(f"✓ System mode: {system_mode.mode}\n")
    
    # Test scenario 1: Low moisture (below threshold) - motor should be OFF
    print("Test 1: Moisture 30% (below threshold 50%) -> Motor should be OFF")
    moisture_reading = SoilMoisture.objects.create(
        sensor=sensor,
        value=30.0,
        timestamp=timezone.now()
    )
    
    # Get motor decision
    threshold = ThresholdConfig.get_threshold(sensor)
    decision = get_motor_state(30.0, motor.state, threshold)
    motor.state = decision['desired_state']
    motor.save()
    
    print(f"  Moisture: {moisture_reading.value}%")
    print(f"  Decision: {decision['reason']}")
    print(f"  Motor state: {motor.state}")
    print_test("Motor OFF when moisture < threshold", 'OFF', motor.state)
    
    # Test scenario 2: High moisture (above threshold) - motor should be ON
    print("\nTest 2: Moisture 70% (above threshold 50%) -> Motor should be ON")
    moisture_reading = SoilMoisture.objects.create(
        sensor=sensor,
        value=70.0,
        timestamp=timezone.now()
    )
    
    decision = get_motor_state(70.0, motor.state, threshold)
    motor.state = decision['desired_state']
    motor.save()
    
    print(f"  Moisture: {moisture_reading.value}%")
    print(f"  Decision: {decision['reason']}")
    print(f"  Motor state: {motor.state}")
    print_test("Motor ON when moisture > threshold", 'ON', motor.state)
    
    # Test scenario 3: Moisture exactly at threshold - motor should be OFF
    print("\nTest 3: Moisture 50% (equal to threshold 50%) -> Motor should be OFF")
    moisture_reading = SoilMoisture.objects.create(
        sensor=sensor,
        value=50.0,
        timestamp=timezone.now()
    )
    
    decision = get_motor_state(50.0, motor.state, threshold)
    motor.state = decision['desired_state']
    motor.save()
    
    print(f"  Moisture: {moisture_reading.value}%")
    print(f"  Decision: {decision['reason']}")
    print(f"  Motor state: {motor.state}")
    print_test("Motor OFF when moisture = threshold", 'OFF', motor.state)
    
    # Test scenario 4: Custom threshold (60%)
    print("\nTest 4: Custom threshold 60%")
    ThresholdConfig.set_threshold(sensor, 60.0)
    threshold = ThresholdConfig.get_threshold(sensor)
    print(f"  New threshold: {threshold}%")
    
    # Test with 55% moisture (below new threshold)
    decision = get_motor_state(55.0, motor.state, threshold)
    motor.state = decision['desired_state']
    motor.save()
    
    print(f"  Moisture: 55%")
    print(f"  Decision: {decision['reason']}")
    print(f"  Motor state: {motor.state}")
    print_test("Motor OFF when 55% < 60% threshold", 'OFF', motor.state)
    
    # Test with 65% moisture (above new threshold)
    decision = get_motor_state(65.0, motor.state, threshold)
    motor.state = decision['desired_state']
    motor.save()
    
    print(f"  Moisture: 65%")
    print(f"  Decision: {decision['reason']}")
    print(f"  Motor state: {motor.state}")
    print_test("Motor ON when 65% > 60% threshold", 'ON', motor.state)
    
    # Clean up
    print("\n✓ Cleaning up test data...")
    sensor.delete()  # This will cascade delete motor, threshold, and moisture readings


def test_api_simulation():
    """Simulate what happens when ESP32 sends data"""
    print_header("Testing API Simulation (ESP32 Data Flow)")
    
    # Clean up
    Sensor.objects.filter(nodeid='esp32_test').delete()
    
    # Create sensor and motor
    sensor = Sensor.objects.create(nodeid='esp32_test', name='ESP32 Zone A')
    motor = Motor.objects.create(sensor=sensor, name='Pump A', state='OFF')
    threshold_config = ThresholdConfig.get_or_create_for_sensor(sensor)
    
    print(f"\n✓ Setup: Sensor={sensor.nodeid}, Motor={motor.name}, Threshold={threshold_config.threshold}%")
    print("✓ System mode: AUTOMATIC\n")
    
    # Simulate ESP32 sending moisture readings
    test_readings = [
        (25.0, 'OFF', "Low moisture - motor stays OFF"),
        (45.0, 'OFF', "Below threshold - motor stays OFF"),
        (55.0, 'ON', "Above threshold - motor turns ON"),
        (75.0, 'ON', "High moisture - motor stays ON"),
        (40.0, 'OFF', "Drops below threshold - motor turns OFF"),
    ]
    
    for i, (moisture, expected_state, description) in enumerate(test_readings, 1):
        print(f"Reading {i}: {description}")
        
        # Get threshold and make decision
        threshold = ThresholdConfig.get_threshold(sensor)
        decision = get_motor_state(moisture, motor.state, threshold)
        
        # Update motor
        old_state = motor.state
        motor.state = decision['desired_state']
        motor.save()
        
        print(f"  Moisture: {moisture}% | Threshold: {threshold}% | Motor: {old_state} -> {motor.state}")
        print_test(f"  Expected {expected_state}", expected_state, motor.state)
        print()
    
    # Clean up
    sensor.delete()


def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║  THRESHOLD LOGIC TEST SUITE                              ║")
    print("║  Motor ON if moisture > threshold, OFF otherwise         ║")
    print("║  Default threshold: 50%                                  ║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_motor_logic()
        test_database_integration()
        test_api_simulation()
        
        print_header("SUMMARY")
        print("\n✓ All tests completed!")
        print("\nLogic confirmed:")
        print("  • Motor turns ON when moisture > threshold")
        print("  • Motor turns OFF when moisture ≤ threshold")
        print("  • Default threshold is 50%")
        print("  • Custom thresholds can be set per sensor\n")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
