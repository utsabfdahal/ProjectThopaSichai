# Nodeid-Based Motor Control Architecture

## Overview
Simplified architecture where **everything is linked by nodeid** - no separate IDs, just sensor node identifiers.

## Core Components

### 1. **Sensor Nodes** (ESP32 with soil moisture sensors)
- Each sensor has unique `nodeid`: "sensor_zone1", "sensor_zone2", "greenhouse_01", etc.
- Sends data: `{"nodeid": "sensor_zone1", "value": 45.5}`

### 2. **Motors** (pumps controlled by nodeid)
- Model fields:
  - `name`: Human-readable name ("Pump 1", "Zone A Motor")
  - `nodeid`: **UNIQUE identifier linking to sensor** (e.g., "sensor_zone1")
  - `state`: ON/OFF
- One motor per sensor nodeid
- Motor nodeid matches sensor nodeid

### 3. **ThresholdConfig** (per-nodeid thresholds)
- Model fields:
  - `nodeid`: **UNIQUE identifier** (matches sensor/motor nodeid)
  - `low_threshold`: Turn motor ON when moisture < this (default: 30%)
  - `high_threshold`: Turn motor OFF when moisture > this (default: 70%)
- Each sensor-motor pair has its own thresholds
- Auto-created with defaults when first sensor data arrives

### 4. **Motor Controller Node** (ESP32 that controls relay switches)
- Periodically fetches `/motorsinfo`
- Gets simple JSON: `{"Pump 1": "ON", "Pump 2": "OFF"}`
- Turns physical relays ON/OFF based on response

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. SENSOR NODES (Multiple ESP32 with soil moisture sensors)    │
└─────────────────────────────────────────────────────────────────┘
   │
   │  POST /api/data/receive/
   │  {
   │    "nodeid": "sensor_zone1",
   │    "value": 25.0
   │  }
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. BACKEND (Django REST API)                                    │
│                                                                  │
│  IF MODE = AUTOMATIC:                                            │
│    ├─> Find Motor WHERE nodeid = "sensor_zone1"                 │
│    ├─> Get ThresholdConfig WHERE nodeid = "sensor_zone1"        │
│    ├─> IF value < low_threshold → Motor.state = "ON"            │
│    └─> IF value > high_threshold → Motor.state = "OFF"          │
│                                                                  │
│  Response: {                                                     │
│    "status": "ok",                                               │
│    "nodeid": "sensor_zone1",                                     │
│    "moisture_value": 25.0,                                       │
│    "motor_update": {                                             │
│      "motor_name": "Pump 1",                                     │
│      "nodeid": "sensor_zone1",                                   │
│      "new_state": "ON",                                          │
│      "reason": "Moisture 25% below threshold 30%"                │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
   │
   │  Motor states updated in database
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. MOTOR CONTROLLER NODE (ESP32 with relay module)              │
│                                                                  │
│  Every 5 seconds:                                                │
│    GET /api/motorsinfo/                                          │
│                                                                  │
│  Response: {                                                     │
│    "Pump 1": "ON",                                               │
│    "Pump 2": "OFF"                                               │
│  }                                                               │
│                                                                  │
│  Controller reads response and:                                  │
│    - Turns relay for "Pump 1" → ON                              │
│    - Turns relay for "Pump 2" → OFF                             │
└─────────────────────────────────────────────────────────────────┘
```

## Database Schema

### Motor
```sql
id (AutoField)            -- Internal ID
name (CharField)          -- "Pump 1", "Pump 2"
nodeid (CharField, UNIQUE) -- "sensor_zone1", "sensor_zone2"
state (CharField)         -- "ON" or "OFF"
created_at, updated_at
```

### ThresholdConfig
```sql
id (AutoField)
nodeid (CharField, UNIQUE) -- "sensor_zone1", "sensor_zone2"
low_threshold (Float)      -- Default: 30.0
high_threshold (Float)     -- Default: 70.0
updated_at
```

### SoilMoisture
```sql
id (UUID)
nodeid (CharField)        -- "sensor_zone1", "sensor_zone2"
value (Float 0-100)
timestamp
ip_address
created_at, updated_at
```

## API Endpoints

### 1. `/api/data/receive/` (Sensor Data)
**Method**: POST (CSRF exempt, no auth)  
**Used by**: Sensor ESP32 nodes  
**Request**:
```json
{
  "nodeid": "sensor_zone1",
  "value": 45.5
}
```

**Response** (AUTOMATIC mode):
```json
{
  "status": "ok",
  "nodeid": "sensor_zone1",
  "moisture_value": 45.5,
  "mode": "AUTOMATIC",
  "motor_update": {
    "motor_name": "Pump 1",
    "nodeid": "sensor_zone1",
    "new_state": "ON",
    "reason": "Moisture 45.5% below threshold 30%"
  },
  "thresholds": {
    "low": 30.0,
    "high": 70.0
  }
}
```

### 2. `/api/motorsinfo/` (Simple Motor Status)
**Method**: GET (CSRF exempt, no auth)  
**Used by**: Motor controller ESP32  
**Response**:
```json
{
  "sensor_zone1": "ON",
  "sensor_zone2": "OFF",
  "test_sensor_01": "ON"
}
```

### 3. `/api/motors/` (Full Motor Management)
**Method**: GET, POST  
**GET Response**:
```json
{
  "success": true,
  "data": {
    "motors": [
      {
        "id": 1,
        "name": "Pump 1",
        "nodeid": "sensor_zone1",
        "state": "ON",
        "state_display": "On",
        "is_on": true,
        "created_at": "...",
        "updated_at": "..."
      }
    ]
  }
}
```

**POST Request** (Create motor):
```json
{
  "name": "Pump 3",
  "nodeid": "sensor_greenhouse",
  "state": "OFF"
}
```

### 4. `/api/mode/set/` (System Mode)
**Method**: POST  
**Request**:
```json
{
  "mode": "AUTOMATIC"  // or "MANUAL"
}
```

## Setup Example

### 1. Create Motors
```bash
# Motor for sensor_zone1
curl -X POST http://localhost:8000/api/motors/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Pump Zone 1", "nodeid": "sensor_zone1", "state": "OFF"}'

# Motor for sensor_zone2
curl -X POST http://localhost:8000/api/motors/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Pump Zone 2", "nodeid": "sensor_zone2", "state": "OFF"}'
```

### 2. (Optional) Set Custom Thresholds
```bash
# Set thresholds for sensor_zone1
curl -X POST http://localhost:8000/api/config/thresholds/set/ \
  -H "Content-Type: application/json" \
  -d '{"nodeid": "sensor_zone1", "low_threshold": 25.0, "high_threshold": 65.0}'
```

If not set, defaults are used (low=30%, high=70%)

### 3. Set to AUTOMATIC Mode
```bash
curl -X POST http://localhost:8000/api/mode/set/ \
  -H "Content-Type: application/json" \
  -d '{"mode": "AUTOMATIC"}'
```

### 4. Sensor ESP32 Code (Arduino)
```cpp
#include <WiFi.h>
#include <HTTPClient.h>

const char* nodeid = "sensor_zone1";  // UNIQUE for each sensor
const char* serverUrl = "http://backend:8000/api/data/receive/";

void sendMoistureData(float moisture) {
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\"nodeid\":\"" + String(nodeid) + "\",\"value\":" + String(moisture) + "}";
  int httpCode = http.POST(payload);
  
  if (httpCode == 201) {
    Serial.println("Data sent successfully");
  }
  http.end();
}
```

### 5. Motor Controller ESP32 Code (Arduino)
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* motorsUrl = "http://backend:8000/api/motorsinfo/";
const char* myNodeId1 = "sensor_zone1";  // First nodeid
const char* myNodeId2 = "sensor_zone2";  // Second nodeid
const int relay1 = 13;  // Relay pin for sensor_zone1 motor
const int relay2 = 14;  // Relay pin for sensor_zone2 motor

void controlMotors() {
  HTTPClient http;
  http.begin(motorsUrl);
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String payload = http.getString();
    JsonDocument doc;
    deserializeJson(doc, payload);
    
    // Control relays based on motor states (using nodeid as key)
    digitalWrite(relay1, doc[myNodeId1] == "ON" ? HIGH : LOW);
    digitalWrite(relay2, doc[myNodeId2] == "ON" ? HIGH : LOW);
  }
  http.end();
}

void loop() {
  controlMotors();
  delay(5000);  // Check every 5 seconds
}
```

## Key Design Decisions

1. **No Separate IDs**: Everything uses nodeid as the linking identifier
2. **CSRF Exempt**: Sensor and motorsinfo endpoints don't require CSRF tokens
3. **No Authentication**: IoT devices can't handle token auth easily
4. **Simple Response**: /motorsinfo returns nodeid:state pairs (e.g., `{"sensor_zone1":"ON"}`)
5. **Auto-create Thresholds**: Default thresholds created on first data from nodeid
6. **Hysteresis Zone**: Between low and high thresholds, motor maintains current state

## Migrations Applied

- `0007_motor_nodeid_thresholdconfig_config_name_and_more.py` - Added nodeid fields
- `0008_remove_thresholdconfig_config_name_and_more.py` - Changed to nodeid-based linking

## Testing

Run: `python test_nodeid_architecture.py`

Tests:
1. ✓ Motors have nodeid field
2. ✓ /motorsinfo returns simple JSON
3. ✓ Automatic mode controls motors by nodeid
4. ✓ Low moisture turns motor ON
5. ✓ High moisture turns motor OFF
6. ✓ Multiple sensors control different motors
