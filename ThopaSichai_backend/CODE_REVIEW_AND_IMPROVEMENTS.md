# Code Review & Architecture Improvements

## ✅ Completed Changes

### 1. **API Schema & Documentation**
- ✅ Installed `drf-spectacular` for OpenAPI 3.0 schema generation
- ✅ Added Swagger UI at `/api/docs/`
- ✅ Added ReDoc at `/api/redoc/`
- ✅ Schema available at `/api/schema/`

### 2. **Improved API Naming Conventions**

**OLD** → **NEW** (RESTful & Cleaner)
```
/api/soil-moisture/              → /api/data/
/api/soil-moisture/receive/      → /api/data/receive/
/api/soil-moisture/latest/       → /api/data/latest/
/api/system-mode/                → /api/mode/
/api/system-mode/set/            → /api/mode/set/
```

### 3. **New Features Implemented**
- ✅ Motor management table (id, name, state)
- ✅ System mode switching (MANUAL/AUTOMATIC)
- ✅ Manual motor control endpoints
- ✅ Automatic motor control based on sensor data

---

## 🔍 Code Issues Found & Recommendations

### **CRITICAL ISSUES** 🔴

#### 1. **Security: DEBUG=True in Production**
**File:** [ThopaSichai_backend/settings.py](ThopaSichai_backend/settings.py#L26)
```python
DEBUG = True  # ❌ DANGEROUS!
ALLOWED_HOSTS = ['*']  # ❌ TOO PERMISSIVE!
SECRET_KEY = 'django-insecure-...'  # ❌ EXPOSED!
```

**Fix:**
```python
import os
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
```

#### 2. **CORS Security Issue**
**File:** [ThopaSichai_backend/settings.py](ThopaSichai_backend/settings.py#L155)
```python
CORS_ALLOW_ALL_ORIGINS = True  # ❌ Security vulnerability!
```

**Fix:**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://192.168.1.100",  # Your ESP32 IP
]
```

#### 3. **No Authentication for Motor Control**
Currently, anyone can control motors without authentication.

**Fix:** Add authentication classes to critical endpoints:
```python
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def control_motor(request, motor_id):
    # ...
```

---

### **HIGH PRIORITY ISSUES** 🟠

#### 4. **Hardcoded Thresholds in Automatic Mode**
**File:** [soil_moisture/views.py](soil_moisture/views.py#L118)
```python
motor_decision = get_motor_state(
    moisture_value=moisture_record.value,
    current_state=motor.state,
    low_threshold=45.0,  # ❌ Hardcoded
    high_threshold=70.0   # ❌ Hardcoded
)
```

**Recommendation:** Create a `MotorConfiguration` model:
```python
class MotorConfiguration(models.Model):
    motor = models.OneToOneField(Motor, on_delete=models.CASCADE)
    low_threshold = models.FloatField(default=45.0)
    high_threshold = models.FloatField(default=70.0)
    sensor_node = models.CharField(max_length=100, blank=True)
```

#### 5. **No Logging Configuration**
You're using `logger` but haven't configured logging in settings.

**Fix:** Add to [settings.py](ThopaSichai_backend/settings.py):
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'soil_moisture': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

#### 6. **Missing Input Validation**
Motor state changes don't validate if motor exists or is in a valid state before changing.

#### 7. **Race Condition Risk**
Multiple ESP32 devices sending data simultaneously could cause race conditions in motor state updates.

**Fix:** Use database transactions:
```python
from django.db import transaction

@transaction.atomic
def receive_soil_moisture(request):
    # ...
```

---

### **MEDIUM PRIORITY ISSUES** 🟡

#### 8. **No Pagination on Motor List**
The motors endpoint doesn't have pagination while soil moisture does.

#### 9. **Inconsistent Response Format**
Some endpoints return `{"status": "ok"}` while others return `{"success": true}`.

**Fix:** Use the `create_response` helper consistently everywhere.

#### 10. **No Rate Limiting**
ESP32 devices could spam the API. Consider adding throttling:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
    }
}
```

#### 11. **Missing Indexes**
Motor table should have indexes for frequently queried fields:
```python
class Motor(models.Model):
    # ...
    class Meta:
        indexes = [
            models.Index(fields=['state']),
        ]
```

#### 12. **No Motor History/Audit Trail**
Consider creating a `MotorStateLog` model to track all state changes:
```python
class MotorStateLog(models.Model):
    motor = models.ForeignKey(Motor, on_delete=models.CASCADE)
    old_state = models.CharField(max_length=3)
    new_state = models.CharField(max_length=3)
    changed_by = models.CharField(max_length=20)  # 'MANUAL' or 'AUTOMATIC'
    moisture_value = models.FloatField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
```

---

### **LOW PRIORITY / NICE TO HAVE** 🟢

#### 13. **No API Versioning**
Consider versioning: `/api/v1/data/`, `/api/v2/data/`

#### 14. **No Health Check Endpoint**
Add a simple health check:
```python
@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'timestamp': timezone.now()})
```

#### 15. **Environment Configuration**
Use `.env` files for configuration instead of hardcoded values.

#### 16. **Testing**
No unit tests found. Create tests in `soil_moisture/tests.py`.

---

## 🏗️ Architecture Recommendations

### **1. Separate Concerns Better**

**Current Structure:**
```
soil_moisture/
  ├── models.py       (All models)
  ├── views.py        (All views)
  ├── serializers.py  (All serializers)
```

**Recommended Structure (as project grows):**
```
soil_moisture/
  ├── models/
  │   ├── __init__.py
  │   ├── sensor.py
  │   ├── motor.py
  │   └── system.py
  ├── views/
  │   ├── __init__.py
  │   ├── sensor_views.py
  │   ├── motor_views.py
  │   └── system_views.py
  ├── serializers/
  └── services/
      └── motor_control_service.py
```

### **2. Create a Service Layer**

Extract business logic from views into services:

**File:** `soil_moisture/services/motor_control_service.py`
```python
class MotorControlService:
    @staticmethod
    def update_motors_automatic(moisture_value: float, nodeid: str):
        """Update all motors based on sensor reading in automatic mode."""
        # Business logic here
        pass
    
    @staticmethod
    def control_motor_manual(motor_id: int, state: str, user=None):
        """Control a specific motor in manual mode."""
        # Business logic here
        pass
```

### **3. Use Django Signals for Motor State Changes**

Instead of directly changing motor state, emit signals:

```python
from django.dispatch import Signal, receiver

motor_state_changed = Signal()

@receiver(motor_state_changed)
def log_motor_change(sender, motor, old_state, new_state, **kwargs):
    MotorStateLog.objects.create(...)
```

### **4. Add WebSocket Support for Real-Time Updates**

Since you have `channels` installed, use it:
```python
# When motor state changes, notify connected clients
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()
async_to_sync(channel_layer.group_send)(
    'motor_updates',
    {'type': 'motor_state_update', 'motor_id': motor.id, 'state': motor.state}
)
```

### **5. Configuration Management**

Create a settings model for system-wide configuration:
```python
class SystemConfiguration(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)
    
    @classmethod
    def get(cls, key, default=None):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default
```

---

## 📊 Current API Endpoints (Updated)

### **Sensor Data**
- `GET /api/data/` - List all sensor readings (paginated)
- `POST /api/data/receive/` - Receive data from ESP32
- `GET /api/data/latest/` - Get latest sensor reading

### **Motor Control**
- `GET /api/motors/` - List all motors
- `POST /api/motors/` - Create new motor
- `GET /api/motors/{id}/` - Get motor details
- `PUT /api/motors/{id}/` - Update motor
- `DELETE /api/motors/{id}/` - Delete motor
- `POST /api/motors/{id}/control/` - Control motor (MANUAL mode only)

### **System Mode**
- `GET /api/mode/` - Get current system mode
- `POST /api/mode/set/` - Set system mode (MANUAL/AUTOMATIC)

### **Documentation**
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc UI
- `GET /api/schema/` - OpenAPI schema

---

## 🚀 Quick Wins to Implement Now

1. **Add environment variables** - 10 minutes
2. **Fix CORS settings** - 5 minutes
3. **Add motor configuration model** - 20 minutes
4. **Add logging configuration** - 10 minutes
5. **Add health check endpoint** - 5 minutes
6. **Add motor state history** - 15 minutes

---

## 📝 Summary

Your architecture is solid for an IoT backend. The main improvements needed are:
- **Security hardening** (environment variables, CORS, authentication)
- **Better configuration management** (motor thresholds, sensor mapping)
- **Audit logging** (motor state changes)
- **Error handling and recovery**

The new motor control system with MANUAL/AUTOMATIC modes is well-designed and should work effectively!
