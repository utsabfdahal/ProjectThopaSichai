# Motor Control API Documentation

This document describes the motor control integration for the soil moisture monitoring system.

## Overview

The system now includes:
1. **GET endpoint** to retrieve the latest sensor data
2. **Motor state logic** that determines whether the irrigation motor should be ON or OFF based on moisture thresholds
3. **Hysteresis logic** to prevent rapid on/off cycling

## New Endpoint

### Get Latest Sensor Data

**Endpoint:** `GET /api/soil-moisture/latest/`

**Description:** Retrieves the most recent soil moisture reading, optionally with motor state recommendation.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `nodeid` | string | No | None | Filter by specific sensor node ID |
| `check_motor` | boolean | No | false | Include motor state recommendation |
| `low_threshold` | float | No | 30.0 | Moisture % below which motor turns ON |
| `high_threshold` | float | No | 70.0 | Moisture % above which motor turns OFF |
| `current_motor_state` | string | No | OFF | Current motor state (ON/OFF) for hysteresis |

**Response Format:**

```json
{
  "success": true,
  "data": {
    "sensor_data": {
      "id": "uuid",
      "nodeid": "ESP32_001",
      "value": 25.5,
      "timestamp": "2025-12-24T10:30:00Z",
      "ip_address": "192.168.1.100",
      "created_at": "2025-12-24T10:30:00Z",
      "updated_at": "2025-12-24T10:30:00Z"
    },
    "motor_recommendation": {
      "desired_state": "ON",
      "reason": "Moisture level 25.5% is below low threshold 30.0%",
      "moisture_level": 25.5,
      "thresholds": {
        "low": 30.0,
        "high": 70.0
      }
    }
  },
  "message": "Latest sensor data retrieved successfully"
}
```

## Motor Control Logic

### Thresholds

The motor control uses two thresholds to create a hysteresis zone:

- **Low Threshold** (default: 30%): When moisture falls below this, motor turns **ON**
- **High Threshold** (default: 70%): When moisture rises above this, motor turns **OFF**

### Hysteresis Zone

When moisture is between the two thresholds (30% - 70%), the motor maintains its current state. This prevents rapid switching and extends motor lifetime.

### Decision Logic

```python
if moisture < low_threshold:
    motor_state = "ON"  # Soil too dry, start watering
elif moisture > high_threshold:
    motor_state = "OFF"  # Soil wet enough, stop watering
else:
    motor_state = current_state  # In middle zone, keep current state
```

## Usage Examples

### Example 1: Get Latest Data Only

```bash
curl "http://localhost:8000/api/soil-moisture/latest/"
```

### Example 2: Get Latest Data with Motor Recommendation

```bash
curl "http://localhost:8000/api/soil-moisture/latest/?check_motor=true"
```

### Example 3: Custom Thresholds

```bash
curl "http://localhost:8000/api/soil-moisture/latest/?check_motor=true&low_threshold=25&high_threshold=75"
```

### Example 4: Filter by Node ID with Motor Check

```bash
curl "http://localhost:8000/api/soil-moisture/latest/?nodeid=ESP32_001&check_motor=true&current_motor_state=ON"
```

### Example 5: Python Client

```python
import requests

response = requests.get(
    'http://localhost:8000/api/soil-moisture/latest/',
    params={
        'check_motor': 'true',
        'low_threshold': 30,
        'high_threshold': 70,
        'current_motor_state': 'OFF'
    }
)

data = response.json()
if data['success']:
    sensor_data = data['data']['sensor_data']
    motor_rec = data['data']['motor_recommendation']
    
    print(f"Moisture: {sensor_data['value']}%")
    print(f"Motor should be: {motor_rec['desired_state']}")
    print(f"Reason: {motor_rec['reason']}")
```

## Motor Logic Module

The motor control logic is separated into `soil_moisture/motor_logic.py` for maintainability.

### Using the Motor Logic Directly

```python
from soil_moisture.motor_logic import get_motor_state, MotorController

# Quick usage
decision = get_motor_state(
    moisture_value=45.0,
    current_state='OFF',
    low_threshold=30.0,
    high_threshold=70.0
)
print(decision['desired_state'])  # 'OFF'

# Using the class for multiple checks
controller = MotorController(low_threshold=30.0, high_threshold=70.0)
decision1 = controller.determine_motor_state(25.0, 'OFF')  # Returns 'ON'
decision2 = controller.determine_motor_state(75.0, 'ON')   # Returns 'OFF'
decision3 = controller.determine_motor_state(50.0, 'ON')   # Returns 'ON' (hysteresis)
```

## Testing

A test script is provided at `test_motor_endpoint.py`:

```bash
# Start the Django server
./dev.sh

# In another terminal, run the test
python test_motor_endpoint.py
```

## Integration with ESP32

Your ESP32 can now:

1. **Send sensor data** (existing functionality):
   ```
   POST /api/soil-moisture/receive/
   ```

2. **Query motor state**:
   ```
   GET /api/soil-moisture/latest/?check_motor=true&current_motor_state=OFF
   ```

3. **Parse response** and control the motor based on `desired_state` field

### ESP32 Example Flow

```cpp
// 1. Read soil moisture sensor
float moisture = readSoilMoisture();

// 2. Send to server
sendSensorData(moisture);

// 3. Get motor recommendation
String response = httpGET("/api/soil-moisture/latest/?check_motor=true&current_motor_state=" + currentMotorState);

// 4. Parse JSON and extract desired_state
String desiredState = parseMotorState(response);

// 5. Control motor
if (desiredState == "ON" && currentMotorState == "OFF") {
    turnMotorOn();
} else if (desiredState == "OFF" && currentMotorState == "ON") {
    turnMotorOff();
}
```

## Error Responses

### No Data Found
```json
{
  "success": false,
  "message": "No sensor data found"
}
```

### Invalid Threshold Parameters
```json
{
  "success": false,
  "errors": {
    "threshold": "low_threshold must be less than high_threshold"
  }
}
```

## Configuration

You can customize default thresholds in `soil_moisture/motor_logic.py`:

```python
DEFAULT_LOW_THRESHOLD = 30.0   # Change this value
DEFAULT_HIGH_THRESHOLD = 70.0  # Change this value
```

## Future Enhancements

Potential improvements:
- Store motor state history in database
- Add endpoint to update thresholds dynamically
- Multiple threshold profiles for different plant types
- Time-based watering schedules
- Weather integration to adjust thresholds
