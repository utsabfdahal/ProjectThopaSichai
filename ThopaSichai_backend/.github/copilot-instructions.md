# ThopaSichai Backend - Copilot Instructions

## Project Overview
Django REST Framework backend for an IoT irrigation system (ThopaSichai). Designed for ESP32 soil moisture sensors to POST readings, with automatic motor control based on moisture thresholds. Token authentication for Flutter mobile app and CSRF-exempt endpoints for IoT devices.

## Architecture Patterns

### Core Apps
- **soil_moisture/**: IoT data ingestion, motor control logic, system mode management (MANUAL/AUTOMATIC)
- **accounts/**: Token authentication (register, login, logout, profile)
- **Project root**: Settings use `uv` for dependency management, SQLite default (PostgreSQL ready)

### Key Design Decisions
1. **CSRF-Exempt for IoT**: ESP32 sensor endpoint (`/api/data/receive/`) uses `@csrf_exempt` - IoT devices can't handle CSRF tokens
2. **CORS Fully Open**: `CORS_ALLOW_ALL_ORIGINS = True` - necessary for ESP32 devices with dynamic IPs
3. **AllowAny Permissions**: Sensor endpoints don't require authentication - IoT devices use direct HTTP POST
4. **Singleton Pattern**: `SystemMode` model uses id=1 singleton to store MANUAL/AUTOMATIC mode
5. **Hysteresis Control**: Motor logic prevents rapid on/off cycling using low/high thresholds (see `soil_moisture/motor_logic.py`)

### Request/Response Standardization
All API endpoints use `create_response()` utility (see [soil_moisture/views.py](soil_moisture/views.py#L17-L24)):
```python
{
  "success": true/false,
  "data": {...},
  "message": "...",
  "errors": {...}
}
```

## Critical Patterns

### Serializer Architecture
All serializers inherit from base mixins for consistency:
- **TimestampMixin**: Auto-adds `created_at`/`updated_at` fields
- **ChoiceValidationMixin**: Validates model choices with `validate_choice_field()`
- Example: `MotorSerializer(ChoiceValidationMixin, serializers.ModelSerializer)` in [soil_moisture/serializers.py](soil_moisture/serializers.py#L39)

### Model Conventions
- **Abstract Base**: `TimeStampedModel` provides timestamp fields for all models
- **TextChoices**: All state/mode fields use Django's `models.TextChoices` (e.g., `Motor.State`, `SystemMode.Mode`)
- **Helper Methods**: Models have business logic methods like `Motor.turn_on()`, `SystemMode.get_instance()`, `SoilMoisture.moisture_status`
- **Indexes**: Heavy indexing on timestamp, nodeid, state fields for query performance

### Automatic Motor Control Flow
When sensor data arrives at `/api/data/receive/`:
1. Check `SystemMode.get_current_mode()`
2. If AUTOMATIC: Query all motors, call `get_motor_state()` for each
3. Update motor states if threshold crossed
4. Return motor changes in response (ESP32 sees what happened)

Hysteresis zone (30%-70% default): Motor maintains current state to prevent oscillation.

## Developer Workflows

### Starting Development
```bash
./dev.sh                    # Runs: uv run python manage.py runserver 0.0.0.0:8000
python manage.py migrate    # Apply database migrations
python manage.py createsuperuser  # Admin access
```

### Testing ESP32 Integration
Use `test_motor_endpoint.py` or `esp32_example.py` for sensor POST examples:
```bash
python test_motor_endpoint.py  # Full motor control tests
```

### Database Management
```bash
python view_db.py           # Custom script to inspect SQLite tables
python check_users.py       # List all registered users
```

### API Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- Uses `drf-spectacular` for OpenAPI 3.0 schema generation

## File Location Guide

| Pattern/Feature | Implementation File |
|----------------|---------------------|
| Motor control logic | [soil_moisture/motor_logic.py](soil_moisture/motor_logic.py) |
| Response formatting | [soil_moisture/views.py](soil_moisture/views.py#L17) `create_response()` |
| Serializer mixins | [soil_moisture/serializers.py](soil_moisture/serializers.py#L12-L29) |
| Singleton pattern | [soil_moisture/models.py](soil_moisture/models.py#L107-L148) `SystemMode` |
| IoT endpoint | [soil_moisture/views.py](soil_moisture/views.py#L77) `receive_soil_moisture()` |
| Auth endpoints | [accounts/views.py](accounts/views.py) |

## Common Gotchas

1. **Time Zone**: Set to `Asia/Kathmandu` (UTC+5:45) in [ThopaSichai_backend/settings.py](ThopaSichai_backend/settings.py#L130)
2. **Pagination**: Default 100 items, max 1000 per page in list endpoints
3. **Motor State Changes**: Always use model methods (`motor.turn_on()`) not direct field assignment - ensures proper `updated_at` handling
4. **SystemMode Deletion**: Prevented in model - use `SystemMode.set_mode()` classmethod instead
5. **ESP32 Response**: Sensor POST returns motor changes in response body so ESP32 can log/display them
6. **UUID Primary Keys**: `SoilMoisture` uses UUID, but `Motor` uses AutoField - intentional for different use cases

## Integration Points

### ESP32 Sensor Flow
```
ESP32 → POST /api/data/receive/ → Save to DB → Check AUTOMATIC mode → 
Update motors → Return {"motor_updates": [...]} → ESP32 displays
```

### Flutter App Flow
```
1. POST /api/auth/register/ → Get token
2. Include "Authorization: Token <key>" in headers for authenticated endpoints
3. Use token for future requests (profile, etc.)
```

### Future MQTT Integration
Channels/Daphne configured in settings but not active. MQTT bridge would:
- Subscribe to `thopa/sensors/+/moisture`
- POST to `/api/data/receive/` internally
- Broadcast motor updates via WebSocket

## Adding New Features

### New Sensor Type Pattern
1. Create model in `soil_moisture/models.py` (inherit `TimeStampedModel`)
2. Add serializer with validation mixins in `serializers.py`
3. Create view using `create_response()` utility
4. Register URL in `soil_moisture/urls.py`
5. Add to `drf_spectacular` schema with `@extend_schema` decorator

### Authentication Changes
- Default: Token auth required unless `@permission_classes([AllowAny])`
- IoT endpoints: Always use `AllowAny` + `@csrf_exempt`
- Add `@authentication_classes([])` for unauthenticated endpoints

## Documentation Files
Comprehensive docs in project root:
- [API_DOCUMENTATION_V2.md](API_DOCUMENTATION_V2.md): Complete API reference with examples
- [MOTOR_CONTROL_API.md](MOTOR_CONTROL_API.md): Motor logic and hysteresis explanation
- [README.md](README.md): Quick start, testing examples, Flutter integration
