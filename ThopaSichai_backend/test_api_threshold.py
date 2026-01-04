#!/usr/bin/env python
"""
Quick API endpoint test for single threshold logic
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_sensor_post():
    """Test posting sensor data and checking motor control"""
    print("\n=== Testing Sensor Data POST with Automatic Motor Control ===\n")
    
    # Test data
    nodeid = "test_api_sensor"
    
    # Test 1: Post low moisture (below 50% threshold) - motor should be OFF
    print("Test 1: Posting moisture 30% (below threshold 50%)")
    data = {
        "nodeid": nodeid,
        "value": 30.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/data/receive/", json=data, timeout=5)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            motor_updates = result.get('data', {}).get('motor_updates', [])
            if motor_updates:
                motor_state = motor_updates[0].get('new_state')
                print(f"✓ Motor state: {motor_state}")
                assert motor_state == 'OFF', f"Expected OFF, got {motor_state}"
        print()
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 2: Post high moisture (above 50% threshold) - motor should be ON
    print("Test 2: Posting moisture 70% (above threshold 50%)")
    data = {
        "nodeid": nodeid,
        "value": 70.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/data/receive/", json=data, timeout=5)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            motor_updates = result.get('data', {}).get('motor_updates', [])
            if motor_updates:
                motor_state = motor_updates[0].get('new_state')
                print(f"✓ Motor state: {motor_state}")
                assert motor_state == 'ON', f"Expected ON, got {motor_state}"
        print()
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 3: Check threshold config
    print("Test 3: Checking threshold configuration")
    try:
        response = requests.get(f"{BASE_URL}/api/threshold/all/", timeout=5)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            thresholds = result.get('data', [])
            for threshold in thresholds:
                if threshold.get('nodeid') == nodeid:
                    print(f"✓ Threshold for {nodeid}: {threshold.get('threshold')}%")
                    print(json.dumps(threshold, indent=2))
        print()
    except Exception as e:
        print(f"✗ Error: {e}\n")


if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════╗")
    print("║  API Endpoint Test - Single Threshold Logic         ║")
    print("╚══════════════════════════════════════════════════════╝")
    
    test_sensor_post()
    
    print("\n✓ API tests completed!")
    print("Note: Ensure dev server is running (./dev.sh)")
