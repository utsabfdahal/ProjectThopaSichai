"""
Example script demonstrating how to use the new motor control endpoints.
Run the Django server first with: ./dev.sh
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"  # Adjust if your server runs on a different port


def get_latest_sensor_data(nodeid=None):
    """Get the latest sensor data without motor recommendation."""
    url = f"{BASE_URL}/soil-moisture/latest/"
    params = {}
    if nodeid:
        params['nodeid'] = nodeid
    
    response = requests.get(url, params=params)
    print(f"\n=== Get Latest Sensor Data (nodeid={nodeid}) ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


def get_latest_with_motor_check(nodeid=None, low_threshold=30, high_threshold=70, current_motor_state='OFF'):
    """Get the latest sensor data WITH motor state recommendation."""
    url = f"{BASE_URL}/soil-moisture/latest/"
    params = {
        'check_motor': 'true',
        'low_threshold': low_threshold,
        'high_threshold': high_threshold,
        'current_motor_state': current_motor_state
    }
    if nodeid:
        params['nodeid'] = nodeid
    
    response = requests.get(url, params=params)
    print(f"\n=== Get Latest with Motor Check ===")
    print(f"Parameters: nodeid={nodeid}, thresholds=[{low_threshold}, {high_threshold}], current_state={current_motor_state}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


def send_test_data(nodeid, moisture_value):
    """Send test sensor data to the database."""
    url = f"{BASE_URL}/soil-moisture/receive/"
    data = {
        'nodeid': nodeid,
        'value': moisture_value
    }
    
    response = requests.post(url, json=data)
    print(f"\n=== Sending Test Data ===")
    print(f"Data: nodeid={nodeid}, value={moisture_value}%")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


def demonstrate_motor_logic():
    """Demonstrate the motor control logic with various moisture levels."""
    print("\n" + "="*60)
    print("MOTOR CONTROL LOGIC DEMONSTRATION")
    print("="*60)
    
    test_nodeid = "ESP32_TEST_001"
    
    # Test scenario 1: Very dry soil (should turn motor ON)
    print("\n--- Scenario 1: Very Dry Soil (20%) ---")
    send_test_data(test_nodeid, 20.0)
    result = get_latest_with_motor_check(test_nodeid, low_threshold=30, high_threshold=70)
    
    # Test scenario 2: Optimal moisture (should maintain current state)
    print("\n--- Scenario 2: Optimal Moisture (50%) ---")
    send_test_data(test_nodeid, 50.0)
    result = get_latest_with_motor_check(test_nodeid, low_threshold=30, high_threshold=70, current_motor_state='ON')
    
    # Test scenario 3: Very wet soil (should turn motor OFF)
    print("\n--- Scenario 3: Very Wet Soil (80%) ---")
    send_test_data(test_nodeid, 80.0)
    result = get_latest_with_motor_check(test_nodeid, low_threshold=30, high_threshold=70, current_motor_state='ON')
    
    # Test scenario 4: Custom thresholds
    print("\n--- Scenario 4: Custom Thresholds (moisture=45%, thresholds=[40, 60]) ---")
    send_test_data(test_nodeid, 45.0)
    result = get_latest_with_motor_check(test_nodeid, low_threshold=40, high_threshold=60)


if __name__ == "__main__":
    try:
        print("Starting Motor Control API Tests...")
        print(f"Base URL: {BASE_URL}")
        
        # Run the demonstration
        demonstrate_motor_logic()
        
        print("\n" + "="*60)
        print("Tests completed successfully!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the Django server.")
        print("Please make sure the server is running with: ./dev.sh")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
