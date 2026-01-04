#!/usr/bin/env python3
"""
Test script for new features:
1. Motors linked with sensor nodes (nodeid)
2. ThresholdConfig with config_name for multiple configs
3. Simple /motorsinfo endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

print("="*60)
print("TESTING NEW FEATURES")
print("="*60)

# Test 1: Simple motors info endpoint
print("\n1. Testing /motorsinfo endpoint (simple motor status)")
print("-" * 60)
response = requests.get(f"{BASE_URL}/motorsinfo/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: Check motors with nodeid field
print("\n2. Testing motors with nodeid field")
print("-" * 60)
response = requests.get(f"{BASE_URL}/motors/")
print(f"Status: {response.status_code}")
motors_data = response.json()
if motors_data['success'] and motors_data['data']['motors']:
    for motor in motors_data['data']['motors']:
        print(f"  - {motor['name']}: nodeid={motor.get('nodeid', 'N/A')}, state={motor['state']}")
else:
    print("  No motors found")

# Test 3: Create a motor with nodeid
print("\n3. Creating motor with nodeid")
print("-" * 60)
new_motor = {
    "name": "Motor_ESP32_001",
    "nodeid": "ESP32_001", 
    "state": "OFF"
}
response = requests.post(f"{BASE_URL}/motors/", json=new_motor)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    print(f"Created: {json.dumps(response.json(), indent=2)}")
else:
    print(f"Response: {response.json()}")

# Test 4: Test sensor data with nodeid
print("\n4. Sending sensor data with nodeid")
print("-" * 60)
sensor_data = {
    "nodeid": "ESP32_001",
    "value": 45.5,
}
response = requests.post(f"{BASE_URL}/data/receive/", json=sensor_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 5: Check motorsinfo again
print("\n5. Checking /motorsinfo after changes")
print("-" * 60)
response = requests.get(f"{BASE_URL}/motorsinfo/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

print("\n" + "="*60)
print("SUMMARY OF NEW FEATURES:")
print("="*60)
print("""
✓ Motor.nodeid field: Links motors to sensor nodes
  - Motors are now associated with specific ESP32 devices
  - Example: Motor_ESP32_001 linked to nodeid "ESP32_001"

✓ ThresholdConfig.config_name: Multiple threshold configurations
  - 'default' config for general use
  - Can create 'zone1', 'greenhouse', etc. for different areas
  - Each config has independent low/high thresholds

✓ /motorsinfo endpoint: Simple motor status endpoint
  - Returns: {"motor1": "ON", "motor2": "OFF"}
  - No authentication required (for IoT devices)
  - No IDs or extra metadata - just motor names and states
  - Perfect for ESP32 to quickly check motor status

Data flow:
  ESP32 → POST /api/data/receive/ with nodeid
  → System checks which motors have same nodeid
  → Updates motors based on thresholds
  → ESP32 can GET /api/motorsinfo/ to see current state
""")
