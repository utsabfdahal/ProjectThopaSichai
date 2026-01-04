# ThopaSichai Backend API - Complete Documentation

## Base URL
```
http://localhost:8000/api
```

## 🎯 Quick Start

### Access API Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

---

## 📡 Sensor Data Endpoints

### 1. List All Sensor Readings
```http
GET /api/data/
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `page_size` (int, optional): Items per page (default: 100, max: 1000)

**Response:**
```json
{
  "success": true,
  "data": {
    "records": [
      {
        "id": "uuid",
        "nodeid": "ESP32_001",
        "value": 65.5,
        "timestamp": "2025-12-25T10:30:00Z",
        "ip_address": "192.168.1.100",
        "created_at": "2025-12-25T10:30:00Z",
        "updated_at": "2025-12-25T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 100,
      "total_count": 250,
      "total_pages": 3
    }
  },
  "message": "Records retrieved successfully"
}
```

---

### 2. Receive Sensor Data (ESP32 Endpoint)
```http
POST /api/data/receive/
```

**Request Body:**
```json
{
  "nodeid": "ESP32_001",
  "value": 45.5,
  "timestamp": "2025-12-25T10:30:00Z"  // optional
}
```

**Response (AUTOMATIC Mode):**
```json
{
  "status": "ok",
  "message": "Data received successfully",
  "moisture_value": 45.5,
  "mode": "AUTOMATIC",
  "motor_updates": [
    {
      "motor_id": 1,
      "motor_name": "Pump 1",
      "new_state": "ON",
      "reason": "Moisture level 45.5% is below low threshold 45.0%"
    }
  ]
}
```

**Response (MANUAL Mode):**
```json
{
  "status": "ok",
  "message": "Data received successfully",
  "moisture_value": 45.5,
  "mode": "MANUAL",
  "motor_updates": "Manual mode - motors not automatically controlled"
}
```

---

### 3. Get Latest Sensor Reading
```http
GET /api/data/latest/
```

**Query Parameters:**
- `nodeid` (string, optional): Filter by specific node
- `check_motor` (boolean, optional): Include motor recommendation (default: true)
- `low_threshold` (float, optional): Low moisture threshold (default: 45.0)
- `high_threshold` (float, optional): High moisture threshold (default: 70.0)
- `current_motor_state` (string, optional): Current motor state for hysteresis (default: OFF)

**Response:**
```json
{
  "success": true,
  "data": {
    "sensor_data": {
      "id": "uuid",
      "nodeid": "ESP32_001",
      "value": 45.5,
      "timestamp": "2025-12-25T10:30:00Z",
      "ip_address": "192.168.1.100"
    },
    "motor_recommendation": {
      "desired_state": "ON",
      "reason": "Moisture level 45.5% is below low threshold 45.0%",
      "moisture_level": 45.5,
      "thresholds": {
        "low": 45.0,
        "high": 70.0
      }
    }
  },
  "message": "Latest sensor data retrieved successfully"
}
```

---

## ⚙️ Motor Management Endpoints

### 4. List All Motors
```http
GET /api/motors/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "motors": [
      {
        "id": 1,
        "name": "Pump 1",
        "state": "OFF",
        "created_at": "2025-12-25T09:00:00Z",
        "updated_at": "2025-12-25T10:30:00Z"
      },
      {
        "id": 2,
        "name": "Pump 2",
        "state": "ON",
        "created_at": "2025-12-25T09:00:00Z",
        "updated_at": "2025-12-25T10:35:00Z"
      }
    ]
  },
  "message": "Motors retrieved successfully"
}
```

---

### 5. Create New Motor
```http
POST /api/motors/
```

**Request Body:**
```json
{
  "name": "Pump 3",
  "state": "OFF"  // optional, default: OFF
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "motor": {
      "id": 3,
      "name": "Pump 3",
      "state": "OFF",
      "created_at": "2025-12-25T10:40:00Z",
      "updated_at": "2025-12-25T10:40:00Z"
    }
  },
  "message": "Motor created successfully"
}
```

---

### 6. Get Motor Details
```http
GET /api/motors/{motor_id}/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "motor": {
      "id": 1,
      "name": "Pump 1",
      "state": "OFF",
      "created_at": "2025-12-25T09:00:00Z",
      "updated_at": "2025-12-25T10:30:00Z"
    }
  },
  "message": "Motor retrieved successfully"
}
```

---

### 7. Update Motor
```http
PUT /api/motors/{motor_id}/
```

**Request Body:**
```json
{
  "name": "Main Pump",  // optional
  "state": "ON"         // requires MANUAL mode
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "motor": {
      "id": 1,
      "name": "Main Pump",
      "state": "ON",
      "created_at": "2025-12-25T09:00:00Z",
      "updated_at": "2025-12-25T10:45:00Z"
    }
  },
  "message": "Motor updated successfully"
}
```

**Response (Error - AUTOMATIC Mode):**
```json
{
  "success": false,
  "errors": {
    "detail": "Cannot manually control motor state in AUTOMATIC mode. Switch to MANUAL mode first."
  }
}
```

---

### 8. Delete Motor
```http
DELETE /api/motors/{motor_id}/
```

**Response:**
```json
{
  "success": true,
  "message": "Motor deleted successfully"
}
```

---

### 9. Control Motor (Quick Control)
```http
POST /api/motors/{motor_id}/control/
```

**Request Body:**
```json
{
  "state": "ON"  // or "OFF"
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "motor": {
      "id": 1,
      "name": "Pump 1",
      "state": "ON",
      "created_at": "2025-12-25T09:00:00Z",
      "updated_at": "2025-12-25T10:50:00Z"
    }
  },
  "message": "Motor turned ON"
}
```

**Response (Error - AUTOMATIC Mode):**
```json
{
  "success": false,
  "errors": {
    "detail": "Cannot manually control motor in AUTOMATIC mode. Switch to MANUAL mode first."
  }
}
```

---

## 🔄 System Mode Endpoints

### 10. Get Current System Mode
```http
GET /api/mode/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "system_mode": {
      "id": 1,
      "mode": "AUTOMATIC",
      "updated_at": "2025-12-25T09:00:00Z"
    }
  },
  "message": "System mode retrieved successfully"
}
```

---

### 11. Set System Mode
```http
POST /api/mode/set/
```

**Request Body:**
```json
{
  "mode": "MANUAL"  // or "AUTOMATIC"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "system_mode": {
      "id": 1,
      "mode": "MANUAL",
      "updated_at": "2025-12-25T10:55:00Z"
    }
  },
  "message": "System mode set to MANUAL"
}
```

---

## 🔐 Authentication

### Most endpoints require NO authentication (for ESP32 compatibility)

For secured endpoints in production, use Token Authentication:

**Header:**
```
Authorization: Token <your_token_here>
```

**Get Token:**
```http
POST /api/auth/login/
```

---

## 🚦 System Mode Behavior

### AUTOMATIC Mode
- ✅ ESP32 sends sensor data → Motors automatically controlled
- ❌ Manual motor control endpoints are **blocked**
- ✅ Motor state changes based on thresholds:
  - `moisture < 45%` → Motor turns **ON**
  - `moisture > 70%` → Motor turns **OFF**
  - Between 45-70% → No change (hysteresis)

### MANUAL Mode
- ❌ ESP32 sensor data → Motors **NOT** controlled automatically
- ✅ Manual motor control endpoints are **enabled**
- ✅ User can control motors via API

---

## 🎯 Typical Workflows

### Workflow 1: Automatic Irrigation
```bash
# 1. Set to AUTOMATIC mode
POST /api/mode/set/
{"mode": "AUTOMATIC"}

# 2. ESP32 sends sensor data
POST /api/data/receive/
{"nodeid": "ESP32_001", "value": 40.0}

# 3. System automatically turns motors ON/OFF
# Response includes motor_updates showing what changed
```

### Workflow 2: Manual Control
```bash
# 1. Set to MANUAL mode
POST /api/mode/set/
{"mode": "MANUAL"}

# 2. Turn motor ON
POST /api/motors/1/control/
{"state": "ON"}

# 3. Check motor status
GET /api/motors/1/

# 4. Turn motor OFF
POST /api/motors/1/control/
{"state": "OFF"}
```

### Workflow 3: Monitor Sensor Data
```bash
# Get latest reading
GET /api/data/latest/?nodeid=ESP32_001

# Get historical data (paginated)
GET /api/data/?page=1&page_size=50
```

---

## 🐛 Error Responses

### Standard Error Format
```json
{
  "success": false,
  "errors": {
    "field_name": "Error message"
  }
}
```

### Common HTTP Status Codes
- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Deleted successfully
- `400 Bad Request` - Validation error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## 📊 ESP32 Integration Example

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* serverUrl = "http://your-server:8000/api/data/receive/";

void sendSensorData(float moistureValue) {
  if(WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    StaticJsonDocument<200> doc;
    doc["nodeid"] = "ESP32_001";
    doc["value"] = moistureValue;
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    int httpCode = http.POST(jsonString);
    
    if(httpCode == 201) {
      String response = http.getString();
      Serial.println("Data sent successfully");
      Serial.println(response);
      
      // Parse response to check motor updates
      StaticJsonDocument<512> responseDoc;
      deserializeJson(responseDoc, response);
      
      if(responseDoc["mode"] == "AUTOMATIC") {
        // Motor state might have changed
        Serial.println("System in AUTOMATIC mode");
      }
    }
    
    http.end();
  }
}
```

---

## 🔧 Testing with curl

```bash
# Create a motor
curl -X POST http://localhost:8000/api/motors/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Pump", "state": "OFF"}'

# Set to MANUAL mode
curl -X POST http://localhost:8000/api/mode/set/ \
  -H "Content-Type: application/json" \
  -d '{"mode": "MANUAL"}'

# Control motor
curl -X POST http://localhost:8000/api/motors/1/control/ \
  -H "Content-Type: application/json" \
  -d '{"state": "ON"}'

# Send sensor data
curl -X POST http://localhost:8000/api/data/receive/ \
  -H "Content-Type: application/json" \
  -d '{"nodeid": "ESP32_001", "value": 45.5}'

# Get latest data
curl http://localhost:8000/api/data/latest/
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- Motor state values: `"ON"` or `"OFF"` (case-sensitive)
- System mode values: `"MANUAL"` or `"AUTOMATIC"` (case-sensitive)
- IP addresses are automatically captured from requests
- Default thresholds: LOW=45%, HIGH=70%
