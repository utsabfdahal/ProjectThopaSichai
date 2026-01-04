#!/usr/bin/env python3
"""
Complete test of nodeid-based motor control architecture
"""
import requests
import json

BASE = "http://localhost:8000/api"

def test(name, url, method='GET', data=None):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    if method == 'GET':
        r = requests.get(url)
    else:
        r = requests.post(url, json=data)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
    return r.json()

print("\n" + "="*60)
print("NODEID-BASED MOTOR CONTROL ARCHITECTURE TEST")
print("="*60)

# 1. Check current motors
test("1. Check existing motors (should have nodeid)", f"{BASE}/motors/")

# 2. Check motorsinfo endpoint
test("2. Simple motorsinfo endpoint", f"{BASE}/motorsinfo/")

# 3. Set to AUTOMATIC mode
test("3. Set system to AUTOMATIC mode", f"{BASE}/mode/set/", 'POST', {"mode": "AUTOMATIC"})

# 4. Send low moisture data for sensor_zone1 (should turn motor ON)
print("\n" + "="*60)
print("TEST: 4. Send LOW moisture data (25%) for sensor_zone1")
print("Expected: Motor 'Pump 1' should turn ON")
print("="*60)
response = test("Sending sensor data", f"{BASE}/data/receive/", 'POST', {
    "nodeid": "sensor_zone1",
    "value": 25.0
})

#5. Check motorsinfo after automatic control
test("5. Check motorsinfo after automatic control", f"{BASE}/motorsinfo/")

# 6. Send high moisture data (should turn motor OFF)
print("\n" + "="*60)
print("TEST: 6. Send HIGH moisture data (75%) for sensor_zone1")
print("Expected: Motor 'Pump 1' should turn OFF")
print("="*60)
test("Sending high moisture", f"{BASE}/data/receive/", 'POST', {
    "nodeid": "sensor_zone1",
    "value": 75.0
})

# 7. Check motorsinfo again
test("7. Check motorsinfo after motor turns off", f"{BASE}/motorsinfo/")

# 8. Test sensor_zone2
print("\n" + "="*60)
print("TEST: 8. Send data for sensor_zone2")
print("Expected: Motor 'Pump 2' should turn ON")
print("="*60)
test("Sending sensor_zone2 data", f"{BASE}/data/receive/", 'POST', {
    "nodeid": "sensor_zone2",
    "value": 20.0
})

# 9. Final motorsinfo check
test("9. Final motorsinfo check (both motors)", f"{BASE}/motorsinfo/")

print("\n" + "="*60)
print("ARCHITECTURE SUMMARY")
print("="*60)
print("""
✓ Each sensor node has unique nodeid (e.g., "sensor_zone1", "sensor_zone2")
✓ Each motor is linked to a sensor by nodeid (Motor.nodeid = sensor nodeid)
✓ Each nodeid has its own ThresholdConfig (low/high thresholds)
✓ When sensor data arrives with nodeid:
  1. System finds motor with matching nodeid
  2. Gets threshold config for that nodeid
  3. Checks moisture vs thresholds
  4. Updates motor state (ON/OFF) if needed
✓ Motor controller ESP32 periodically fetches /motorsinfo
✓ /motorsinfo returns: {"Pump 1": "ON", "Pump 2": "OFF"}

DATA FLOW:
-----------
Sensor ESP32 → POST /api/data/receive/
  {
    "nodeid": "sensor_zone1",  # Links to motor
    "value": 25.0              # Moisture %
  }
  ↓
Backend finds Motor with nodeid="sensor_zone1"
Backend gets ThresholdConfig for nodeid="sensor_zone1" 
Checks: value < low_threshold? → Turn motor ON
Checks: value > high_threshold? → Turn motor OFF
  ↓
Motor controller ESP32 → GET /api/motorsinfo/
  Returns: {"Pump 1": "ON", "Pump 2": "OFF"}
  ↓
Motor controller turns physical relay ON/OFF
""")
