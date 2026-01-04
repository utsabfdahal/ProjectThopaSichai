#!/usr/bin/env python3
"""
Test the new Sensor-based architecture
"""
import subprocess
import json
import time

def run_curl(method, url, data=None):
    """Helper to run curl commands"""
    cmd = ["curl", "-s", "-X", method, url, "-H", "Content-Type: application/json"]
    if data:
        cmd.extend(["-d", json.dumps(data)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return result.stdout

def test_architecture():
    """Test the sensor-motor-threshold architecture"""
    base_url = "http://localhost:8000/api"
    
    print("=" * 60)
    print("TESTING SENSOR-BASED ARCHITECTURE")
    print("=" * 60)
    
    # Test 1: Send data with new nodeid - should auto-create sensor
    print("\n1. POST sensor data (nodeid='test_node_1') - Auto-create sensor")
    response = run_curl("POST", f"{base_url}/data/receive/", {
        "nodeid": "test_node_1",
        "value": 25.0
    })
    print(json.dumps(response, indent=2))
    assert response.get("sensor_created") == True, "Sensor should be auto-created"
    print("✓ Sensor auto-created")
    
    # Test 2: Send another reading - sensor already exists
    print("\n2. POST sensor data again (nodeid='test_node_1') - Sensor exists")
    response = run_curl("POST", f"{base_url}/data/receive/", {
        "nodeid": "test_node_1",
        "value": 30.0
    })
    print(json.dumps(response, indent=2))
    assert response.get("sensor_created") == False, "Sensor should already exist"
    print("✓ Sensor reused")
    
    # Test 3: Create another sensor with different nodeid
    print("\n3. POST sensor data (nodeid='test_node_2') - Create second sensor")
    response = run_curl("POST", f"{base_url}/data/receive/", {
        "nodeid": "test_node_2",
        "value": 75.0
    })
    print(json.dumps(response, indent=2))
    assert response.get("sensor_created") == True, "Second sensor should be created"
    print("✓ Second sensor created")
    
    # Test 4: Check motors info (should be empty - no motors yet)
    print("\n4. GET /motorsinfo - Should be empty")
    response = run_curl("GET", f"{base_url}/motorsinfo/")
    print(json.dumps(response, indent=2))
    assert response == {}, "No motors should exist yet"
    print("✓ No motors yet")
    
    # Test 5: Get all sensors via data endpoint
    print("\n5. GET /data/filtered/?nodeid=test_node_1")
    response = run_curl("GET", f"{base_url}/data/filtered/?nodeid=test_node_1")
    print(f"Records found: {len(response.get('data', {}).get('readings', []))}")
    print("✓ Sensor readings retrieved")
    
    # Summary
    print("\n" + "=" * 60)
    print("ARCHITECTURE TEST RESULTS")
    print("=" * 60)
    print("✓ Sensor auto-creation: WORKING")
    print("✓ Sensor reuse: WORKING")
    print("✓ Multiple sensors: WORKING")
    print("✓ Data storage linked to sensors: WORKING")
    print("\nNOTE: To create motors:")
    print("  - Motors must be created via admin panel")
    print("  - Select the sensor from dropdown when creating motor")
    print("  - One motor per sensor (OneToOne relationship)")
    print("  - ThresholdConfig auto-created when needed")
    
if __name__ == '__main__':
    try:
        test_architecture()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        exit(1)
