# Threshold System Changes - Summary

## Changes Made

### 1. Model Changes
**File:** `soil_moisture/models.py`

Changed from:
- `low_threshold` (default: 30.0) - Motor ON when below this
- `high_threshold` (default: 70.0) - Motor OFF when above this

Changed to:
- `threshold` (default: 50.0) - Motor ON when moisture > threshold

### 2. Motor Logic Changes
**File:** `soil_moisture/motor_logic.py`

**New Logic:**
- Motor turns ON when moisture > threshold
- Motor turns OFF when moisture ≤ threshold
- No hysteresis zone (simple on/off logic)

**Updated methods:**
- `MotorController.__init__(threshold)` - Takes single threshold
- `get_motor_state(moisture_value, current_state, threshold)` - Uses single threshold

### 3. Serializer Changes
**File:** `soil_moisture/serializers.py`

- Removed `low_threshold` and `high_threshold` from `ThresholdConfigSerializer`
- Now only has `threshold` field
- Removed validation for low < high (not needed anymore)

### 4. Admin Changes
**File:** `soil_moisture/admin.py`

- Updated `ThresholdConfigAdmin` to display single `threshold` field
- Removed `low_threshold` and `high_threshold` from list_display

### 5. View Changes
**File:** `soil_moisture/views.py`

- Updated motor control logic to use `ThresholdConfig.get_threshold(sensor)`
- Pass single `threshold` parameter to `get_motor_state()`

### 6. Database Migration
**Migration:** `soil_moisture/migrations/0002_*.py`

- Removed `high_threshold` field
- Removed `low_threshold` field  
- Added `threshold` field (default: 50.0)

## Testing Results

### ✅ All Tests Passed

1. **Motor Logic Tests:** Verified motor turns ON/OFF correctly based on threshold
2. **Database Integration:** Confirmed threshold config and motor updates work
3. **API Schema:** Fixed ImproperlyConfigured error - Swagger docs now working
4. **Custom Thresholds:** Verified per-sensor threshold customization works

### Test Coverage

| Scenario | Threshold | Moisture | Expected | Result |
|----------|-----------|----------|----------|---------|
| Below threshold | 50% | 30% | OFF | ✓ PASS |
| Equal to threshold | 50% | 50% | OFF | ✓ PASS |
| Just above threshold | 50% | 50.1% | ON | ✓ PASS |
| Above threshold | 50% | 70% | ON | ✓ PASS |
| Custom threshold | 40% | 45% | ON | ✓ PASS |

## Usage Examples

### Get Threshold
```python
from soil_moisture.models import ThresholdConfig

# Get threshold for a sensor
threshold = ThresholdConfig.get_threshold(sensor)
# Returns: 50.0 (default)
```

### Set Custom Threshold
```python
# Set custom threshold for a sensor
ThresholdConfig.set_threshold(sensor, 60.0)
```

### Motor Control Logic
```python
from soil_moisture.motor_logic import get_motor_state

# Check what motor state should be
decision = get_motor_state(
    moisture_value=65.0,
    current_state='OFF',
    threshold=50.0
)

# Returns:
# {
#     'desired_state': 'ON',
#     'reason': 'Moisture level 65.0% exceeds threshold 50.0%',
#     'moisture_level': 65.0,
#     'threshold': 50.0
# }
```

## API Endpoints

### View Thresholds
```bash
GET /api/threshold/all/
```

### Update Threshold
```bash
PUT /api/threshold/{nodeid}/
Content-Type: application/json

{
  "threshold": 60.0
}
```

## Migration Instructions

If you have existing data:

1. **Backup your database**
   ```bash
   cp db.sqlite3 db.sqlite3.backup
   ```

2. **Apply migration**
   ```bash
   python manage.py migrate
   ```

3. **Old data handling:**
   - Old `low_threshold` and `high_threshold` values are discarded
   - All sensors get default threshold of 50.0
   - Adjust individual sensor thresholds via API or admin panel as needed

## Next Steps

1. Update any documentation that references two thresholds
2. Update ESP32 firmware if it expects threshold info in responses
3. Update Flutter app if it displays threshold values
4. Consider adding threshold to motor status API responses

## Files Modified

- `soil_moisture/models.py`
- `soil_moisture/serializers.py`
- `soil_moisture/motor_logic.py`
- `soil_moisture/views.py`
- `soil_moisture/admin.py`
- Created migration: `0002_*.py`

## Test Files Created

- `test_threshold_logic.py` - Comprehensive logic tests
- `test_api_threshold.py` - API endpoint tests
- `final_test.py` - Final verification test
