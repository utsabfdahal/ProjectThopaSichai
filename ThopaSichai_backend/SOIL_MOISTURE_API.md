# 🌱 Soil Moisture API Documentation

## Overview
The Soil Moisture API provides endpoints for collecting, storing, and managing soil moisture data from ESP32 devices. This API is specifically designed for IoT agriculture applications.

## Base URL
```
http://10.164.63.195:8000/api/
```

## Endpoints

### 1. List Soil Moisture Records
**GET** `/api/soil-moisture/`

Retrieve all soil moisture records with pagination support.

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Number of records per page (default: 100, max: 1000)

**Example Request:**
```bash
curl -X GET "http://10.164.63.195:8000/api/soil-moisture/?page=1&page_size=10"
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "records": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "data": {
          "moisture_level": 75
        },
        "metadata": {
          "location": "Field A"
        },
        "ip_address": "192.168.1.100",
        "created_at": "2025-12-24T10:30:00Z",
        "updated_at": "2025-12-24T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_count": 1,
      "total_pages": 1
    }
  },
  "message": "Records retrieved successfully"
}
```

---

### 2. Create Soil Moisture Record
**POST** `/api/soil-moisture/create/`

Create a new soil moisture record manually.

**Request Body:**
```json
{
  "data": {
    "moisture_level": 75,
    "temperature": 25
  },
  "metadata": {
    "location": "Field A",
    "sensor_id": "SENSOR_001"
  },
  "ip_address": "192.168.1.100"
}
```

**Example Request:**
```bash
curl -X POST "http://10.164.63.195:8000/api/soil-moisture/create/" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"moisture_level": 75},
    "metadata": {"location": "Field A"},
    "ip_address": "192.168.1.100"
  }'
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "data": {
      "moisture_level": 75
    },
    "metadata": {
      "location": "Field A"
    },
    "ip_address": "192.168.1.100",
    "created_at": "2025-12-24T10:30:00Z",
    "updated_at": "2025-12-24T10:30:00Z"
  },
  "message": "Record created successfully"
}
```

---

### 3. Receive Data from ESP32 (Primary Endpoint)
**POST** `/api/soil-moisture/receive/`

**This is the main endpoint ESP32 devices should use to send sensor data.**

**Request Body:**
```json
{
  "data": {
    "moisture_level": 75,
    "temperature": 25
  },
  "metadata": {
    "location": "Field A"
  }
}
```

**Note:** The `ip_address` is automatically captured from the request, so ESP32 doesn't need to send it.

**Example Request from ESP32:**
```bash
curl -X POST "http://10.164.63.195:8000/api/soil-moisture/receive/" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"moisture_level": 75},
    "metadata": {"location": "ku"}
  }'
```

**Response (201 Created):**
```json
{
  "status": "ok",
  "message": "Data received successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "status": "error",
  "errors": {
    "data": ["Data cannot be empty."]
  }
}
```

---

### 4. Update Soil Moisture Record
**PUT** `/api/soil-moisture/<uuid:id>/update/`

Update an existing soil moisture record.

**Example Request:**
```bash
curl -X PUT "http://10.164.63.195:8000/api/soil-moisture/550e8400-e29b-41d4-a716-446655440000/update/" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"moisture_level": 80},
    "metadata": {"location": "Field B"},
    "ip_address": "192.168.1.100"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "data": {
      "moisture_level": 80
    },
    "metadata": {
      "location": "Field B"
    },
    "ip_address": "192.168.1.100",
    "created_at": "2025-12-24T10:30:00Z",
    "updated_at": "2025-12-24T10:35:00Z"
  },
  "message": "Record updated successfully"
}
```

---

### 5. Delete Soil Moisture Record
**DELETE** `/api/soil-moisture/<uuid:id>/delete/`

Delete a soil moisture record.

**Example Request:**
```bash
curl -X DELETE "http://10.164.63.195:8000/api/soil-moisture/550e8400-e29b-41d4-a716-446655440000/delete/"
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Record 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

---

## ESP32 MicroPython Example

See `esp32_example.py` for a complete MicroPython script that:
1. Connects to WiFi
2. Sends soil moisture data to the Django backend
3. Handles errors and connection issues

**Key points for ESP32:**
- Use the `/api/soil-moisture/receive/` endpoint
- Send data as JSON with `data` and `metadata` fields
- IP address is automatically captured
- Keep WiFi credentials and URL updated

**Example ESP32 payload:**
```python
payload = {
    "data": {
        "moisture_level": 75,
        "temperature": 25,
        "humidity": 60
    },
    "metadata": {
        "location": "Field A",
        "sensor_type": "capacitive",
        "device_id": "ESP32_001"
    }
}
```

---

## Data Structure

### SoilMoisture Model
- **id** (UUID): Unique identifier (auto-generated)
- **data** (JSON): Main sensor data (required, must be a dict)
- **metadata** (JSON): Optional additional information (nullable)
- **ip_address** (string): Source IP address (max 45 chars)
- **created_at** (datetime): Record creation timestamp
- **updated_at** (datetime): Last update timestamp

### Validation Rules
1. **data**: Must be a non-empty JSON object (dict)
2. **metadata**: Must be a JSON object or null
3. **ip_address**: Must be a valid IPv4 or IPv6 address

---

## Error Codes

- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid data or validation error
- **404 Not Found**: Record not found
- **500 Internal Server Error**: Server error

---

## Testing

### Test with curl:
```bash
# Send test data
curl -X POST "http://10.164.63.195:8000/api/soil-moisture/receive/" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"moisture_level": 75, "temperature": 25},
    "metadata": {"location": "test field", "device": "test"}
  }'

# View all records
curl "http://10.164.63.195:8000/api/soil-moisture/"
```

### View in Admin Panel:
1. Go to: http://10.164.63.195:8000/admin/
2. Login with: `bipul` / `password`
3. Navigate to "Soil Moisture" section

### View in Database:
```bash
cd /home/bipul/Bipul/ThopaSichai/ThopaSichai_backend
python view_db.py
```

---

## Database Schema

```sql
CREATE TABLE "SoilMoisture" (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    metadata JSONB,
    ip_address VARCHAR(45) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX ON "SoilMoisture" (created_at DESC);
CREATE INDEX ON "SoilMoisture" (ip_address);
```

---

## Integration Checklist

- [x] Django model created
- [x] PostgreSQL migrations applied
- [x] API endpoints configured
- [x] CSRF protection disabled for ESP32 endpoint
- [x] CORS enabled for all origins
- [x] Admin interface registered
- [ ] ESP32 code updated with correct URL
- [ ] ESP32 tested with real sensor
- [ ] Flutter app integrated

---

## Next Steps

1. **Update ESP32 Code**: Edit `esp32_example.py` with your WiFi credentials
2. **Upload to ESP32**: Flash the code to your ESP32 device
3. **Test Connection**: Verify data is being received in the database
4. **Flutter Integration**: Create API calls from Flutter app to fetch and display data
5. **Add Authentication**: (Optional) Protect endpoints with token authentication
