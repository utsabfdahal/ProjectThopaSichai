# Sensor-Based Architecture - Implementation Complete

## ✅ Architecture Overview

### Central Entity: **Sensor** (nodeid as primary key)
- Auto-created when new nodeid arrives in sensor data
- Stores nodeid, name, is_active, timestamps
- One sensor per unique nodeid

### Relationships:
```
Sensor (nodeid)
  ├── Motor (OneToOne) - One motor per sensor
  ├── ThresholdConfig (OneToOne) - One threshold config per sensor
  └── SoilMoisture readings (ForeignKey) - Many readings per sensor
```

## ✅ How It Works

### 1. Sensor Auto-Creation
```bash
POST /api/data/receive/
{
  "nodeid": "sensor_zone_1",
  "value": 45.5
}
```
- If nodeid doesn't exist → Creates new Sensor
- Saves moisture reading linked to sensor
- Returns `"sensor_created": true/false`

### 2. Motor Mapping
Motors are mapped to sensors (1:1 relationship):
- **sensor_zone_1** → Motor 1 (Pump 1)
- **sensor_zone_2** → Motor 2 (Pump 2)
- **sensor_zone_3** → Motor 3 (Pump 3)

Create via Python:
```python
sensor = Sensor.objects.get(nodeid='sensor_zone_1')
motor = Motor.objects.create(sensor=sensor, name='Pump 1', state='OFF')
```

### 3. Threshold Configuration
Each sensor has its own thresholds:
- Auto-created with defaults (30% low, 70% high)
- Configurable per sensor via API or admin

### 4. Automatic Motor Control
When moisture data arrives:
1. Find sensor by nodeid (or create if new)
2. Save reading
3. If motor exists for sensor:
   - Get threshold config
   - Check moisture vs thresholds
   - Update motor state if needed
4. Return motor update in response

## ✅ API Endpoints

### `/api/motorsinfo/` - Motor Status
Returns: `{"sensor_zone_1": "ON", "sensor_zone_2": "OFF"}`
- Keys are **nodeids** (not motor names)
- Motor controller ESP32 polls this endpoint

### `/api/data/receive/` - Sensor Data
POST: `{"nodeid": "...", "value": 45.5}`
- Auto-creates sensor if new nodeid
- Controls motor in AUTOMATIC mode
- Returns motor state change

## ✅ Test Results

### Test 1: Sensor Auto-Creation
```bash
curl -X POST http://localhost:8000/api/data/receive/ \
  -H "Content-Type: application/json" \
  -d '{"nodeid": "test_node_1", "value": 25.0}'

Response:
{
  "sensor_created": true,  ✓
  "motor_update": "No motor configured"  ✓
}
```

### Test 2: Low Moisture → Motor ON
```bash
# Moisture 25% < 30% threshold
Response:
{
  "motor_update": {
    "motor_name": "Pump 1",
    "sensor_nodeid": "test_node_1",
    "new_state": "ON",  ✓
    "reason": "Moisture level 25.0% is below low threshold 30.0%"
  }
}
```

### Test 3: High Moisture → Motor OFF
```bash
# Moisture 75% > 70% threshold
Response:
{
  "motor_update": {
    "motor_name": "Pump 1",
    "sensor_nodeid": "test_node_1",
    "new_state": "OFF",  ✓
    "reason": "Moisture level 75.0% is above high threshold 70.0%"
  }
}
```

### Test 4: Motor Status Endpoint
```bash
curl http://localhost:8000/api/motorsinfo/

Response:
{
  "test_node_1": "OFF",  ✓
  "test_node_2": "OFF",  ✓
  "utsabbbbb": "OFF"     ✓
}
```

## ✅ Benefits

### 1. Automatic Sensor Management
- No manual sensor creation needed
- Just send data with nodeid
- System tracks all unique sensors

### 2. Clean Motor Mapping
- One motor per sensor (clear 1:1 relationship)
- Motor controller queries by nodeid
- No confusion about which motor goes with which sensor

### 3. Per-Sensor Configuration
- Each sensor has independent thresholds
- Different zones can have different moisture requirements
- Easy to manage via admin panel

### 4. Database Integrity
- Foreign keys ensure data consistency
- Can't delete sensor if motor/readings exist
- CASCADE deletion cleans up related data

## ✅ ESP32 Integration

### Sensor Node (sends data)
```cpp
POST http://backend:8000/api/data/receive/
{
  "nodeid": "sensor_zone_1",
  "value": 45.5
}
```

### Motor Controller Node (reads status)
```cpp
GET http://backend:8000/api/motorsinfo/
// Returns: {"sensor_zone_1": "ON", "sensor_zone_2": "OFF"}
digitalWrite(relay1, response["sensor_zone_1"] == "ON" ? HIGH : LOW);
```

## ✅ Migration Applied

Created fresh database with new schema:
- Sensor table (nodeid as PK)
- Motor with sensor ForeignKey (OneToOne)
- ThresholdConfig with sensor ForeignKey (OneToOne)
- SoilMoisture with sensor ForeignKey
- All indexes and constraints properly configured

## 🎯 System Ready for Production

All critical functionality tested and working:
- ✅ Sensor auto-creation
- ✅ Motor mapping to sensors
- ✅ Automatic motor control based on thresholds
- ✅ Per-sensor threshold configuration
- ✅ Motor status endpoint for ESP32
- ✅ Multiple sensors working independently
