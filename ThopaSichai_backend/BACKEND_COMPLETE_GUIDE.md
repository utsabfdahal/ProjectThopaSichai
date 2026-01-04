# 🌱 ThopaSichai Backend - Complete Beginner's Guide

Welcome! This document explains **everything** about the ThopaSichai irrigation system backend. We'll start from the basics and work our way to understanding every component.

---

## 📚 Table of Contents

1. [What is ThopaSichai?](#1-what-is-thopasichai)
2. [Understanding the Basics](#2-understanding-the-basics)
3. [Project Structure](#3-project-structure)
4. [How Django Works (Quick Intro)](#4-how-django-works-quick-intro)
5. [Database Models Explained](#5-database-models-explained)
6. [The Data Flow - How Everything Connects](#6-the-data-flow---how-everything-connects)
7. [All API Endpoints Explained](#7-all-api-endpoints-explained)
8. [Authentication System](#8-authentication-system)
9. [Motor Control Logic](#9-motor-control-logic)
10. [ESP32 Integration](#10-esp32-integration)
11. [Running the Server](#11-running-the-server)

---

## 1. What is ThopaSichai?

**ThopaSichai** (थोपा सिचाई) means "Drip Irrigation" in Nepali. This is a smart irrigation system that:

- 📊 **Collects** soil moisture data from sensors (ESP32 devices)
- 🧠 **Decides** when to turn water pumps ON/OFF
- 🔧 **Controls** motors/pumps automatically or manually
- 📱 **Provides** a mobile app interface for farmers

### The System Has 3 Main Parts:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ESP32 Nodes   │────▶│  Django Backend │◀────│   Mobile App    │
│   (Hardware)    │     │    (This!)      │     │   (Flutter)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 2. Understanding the Basics

### What is a Backend?

Think of a restaurant:
- **Frontend** (Mobile App) = The dining area where customers order
- **Backend** (This server) = The kitchen where food is prepared
- **Database** = The storage room with ingredients

The backend:
- Receives requests (like orders)
- Processes them (like cooking)
- Sends responses (like serving food)

### What is Django?

Django is a Python web framework - it provides pre-built tools to create web applications quickly. Key concepts:

| Term | What It Is | Restaurant Analogy |
|------|------------|-------------------|
| **Model** | Database table structure | Recipe card |
| **View** | Code that handles requests | The chef |
| **URL** | Web address/endpoint | Menu item number |
| **Serializer** | Converts data to JSON | Plating the food |

### What is REST API?

API = Application Programming Interface (a way for apps to talk to each other)
REST = A style of designing APIs

Example API call:
```
POST /api/auth/login/
{
    "username": "farmer1",
    "password": "password123"
}
```

Response:
```json
{
    "token": "abc123...",
    "message": "Login successful!"
}
```

---

## 3. Project Structure

```
ThopaSichai_backend-main/
├── manage.py                 # Django's command-line tool
├── db.sqlite3               # The database file (stores all data)
├── requirements.txt         # Python packages needed
│
├── ThopaSichai_backend/     # Main project settings
│   ├── settings.py         # Configuration (database, apps, etc.)
│   ├── urls.py             # Main URL router
│   ├── wsgi.py             # Web server interface
│   └── asgi.py             # Async server interface
│
├── accounts/                # User authentication app
│   ├── models.py           # (Empty - uses Django's built-in User)
│   ├── views.py            # Login, Register, Logout logic
│   ├── serializers.py      # Data validation for auth
│   └── urls.py             # Auth-related URLs
│
└── soil_moisture/          # Main irrigation app
    ├── models.py           # Sensor, Motor, SoilMoisture tables
    ├── views.py            # All API endpoint handlers
    ├── serializers.py      # Data validation & formatting
    ├── motor_logic.py      # Motor ON/OFF decision logic
    └── urls.py             # Sensor/motor-related URLs
```

### What Each Folder Does:

| Folder | Purpose |
|--------|---------|
| `ThopaSichai_backend/` | Project-level settings and configuration |
| `accounts/` | Handles user registration, login, logout |
| `soil_moisture/` | Core functionality - sensors, motors, moisture data |

---

## 4. How Django Works (Quick Intro)

### The Request-Response Cycle:

```
📱 Mobile App                    🖥️ Django Server
     │                                  │
     │   1. HTTP Request               │
     │   POST /api/auth/login/   ────▶ │
     │   {"username": "x"}              │
     │                                  │
     │                           2. URL matches to view
     │                           3. View processes request
     │                           4. Queries database
     │                           5. Formats response
     │                                  │
     │   6. HTTP Response         ◀──── │
     │   {"token": "abc123"}            │
     ▼                                  ▼
```

### The MVC Pattern (Django's MTV):

1. **Model** - Defines data structure (database tables)
2. **View** - Handles business logic (not visual!)
3. **Template** - Renders HTML (not used in this API project)
4. **Serializer** - Converts between Python objects and JSON

---

## 5. Database Models Explained

The database has **5 main tables**:

### 5.1 Sensor Model

```python
class Sensor(TimeStampedModel):
    nodeid = CharField(unique=True, primary_key=True)  # e.g., "sensor_zone1"
    name = CharField(blank=True)                        # e.g., "Field A Sensor"
    is_active = BooleanField(default=True)
```

**What it stores:** Information about each physical sensor device.

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `nodeid` | String | "sensor_zone1" | Unique ID for each sensor |
| `name` | String | "Greenhouse Sensor" | Human-readable name |
| `is_active` | Boolean | True | Is sensor currently active? |

### 5.2 Motor Model

```python
class Motor(TimeStampedModel):
    id = AutoField(primary_key=True)
    sensor = OneToOneField(Sensor)  # 1 motor per sensor
    name = CharField()               # e.g., "Pump 1"
    state = CharField(choices=['ON', 'OFF'])
```

**What it stores:** Water pumps/motors linked to sensors.

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `id` | Integer | 1 | Auto-generated ID |
| `sensor` | ForeignKey | sensor_zone1 | Which sensor this motor belongs to |
| `name` | String | "Pump Zone 1" | Human-readable name |
| `state` | String | "ON" or "OFF" | Current motor state |

### 5.3 SoilMoisture Model

```python
class SoilMoisture(TimeStampedModel):
    id = UUIDField(primary_key=True)
    sensor = ForeignKey(Sensor)      # Which sensor recorded this
    value = FloatField()             # 0-100%
    timestamp = DateTimeField()
    ip_address = CharField()
```

**What it stores:** Every soil moisture reading from sensors.

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `id` | UUID | "abc-123-..." | Unique ID |
| `sensor` | ForeignKey | sensor_zone1 | Which sensor sent this |
| `value` | Float | 45.5 | Moisture percentage (0-100) |
| `timestamp` | DateTime | 2025-12-28 10:30:00 | When reading was taken |

### 5.4 SystemMode Model (Singleton)

```python
class SystemMode(models.Model):
    mode = CharField(choices=['MANUAL', 'AUTOMATIC'])
```

**What it stores:** Whether the system controls motors automatically or manually.

| Mode | Behavior |
|------|----------|
| `AUTOMATIC` | System decides motor ON/OFF based on moisture levels |
| `MANUAL` | User controls motors directly via app |

### 5.5 ThresholdConfig Model

```python
class ThresholdConfig(models.Model):
    sensor = OneToOneField(Sensor)  # 1 config per sensor
    threshold = FloatField(default=50.0)
```

**What it stores:** When to turn motor ON for each sensor.

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `sensor` | ForeignKey | sensor_zone1 | Which sensor |
| `threshold` | Float | 50.0 | Motor turns ON when moisture > this |

### Visual Database Relationships:

```
┌─────────────┐       ┌─────────────┐       ┌─────────────────┐
│   Sensor    │◀─────▶│    Motor    │       │ ThresholdConfig │
│  (nodeid)   │1    1│   (state)   │       │   (threshold)   │
└─────────────┘       └─────────────┘       └────────┬────────┘
       │                                             │
       │1                                            │1
       ▼n                                            │
┌─────────────┐                                      │
│SoilMoisture │                              ◀───────┘
│   (value)   │
│  (readings) │
└─────────────┘
```

**Key Relationships:**
- One Sensor → One Motor (1:1)
- One Sensor → Many SoilMoisture readings (1:n)
- One Sensor → One ThresholdConfig (1:1)

---

## 6. The Data Flow - How Everything Connects

### Complete System Flow:

```
┌──────────────────────────────────────────────────────────────────────┐
│                    STEP 1: SENSOR SENDS DATA                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ESP32 Sensor (in field)                                            │
│       │                                                              │
│       │ POST /api/data/receive/                                     │
│       │ {"nodeid": "sensor_zone1", "value": 25.0}                   │
│       ▼                                                              │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                 DJANGO BACKEND                            │       │
│  │                                                           │       │
│  │  1. Receive request                                       │       │
│  │  2. Check if sensor exists                                │       │
│  │  3. If new nodeid → Auto-create Sensor record            │       │
│  │  4. Save SoilMoisture reading to database                │       │
│  │  5. IF MODE = AUTOMATIC:                                  │       │
│  │     a. Find Motor linked to this sensor                   │       │
│  │     b. Get Threshold for this sensor                      │       │
│  │     c. If moisture > threshold → Motor = ON              │       │
│  │     d. If moisture <= threshold → Motor = OFF            │       │
│  │  6. Return response                                       │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                 STEP 2: MOTOR CONTROLLER FETCHES STATES             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ESP32 Motor Controller (every 5 seconds)                           │
│       │                                                              │
│       │ GET /api/motorsinfo/                                        │
│       ▼                                                              │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                 DJANGO BACKEND                            │       │
│  │                                                           │       │
│  │  Returns: {"sensor_zone1": "ON", "sensor_zone2": "OFF"}  │       │
│  └──────────────────────────────────────────────────────────┘       │
│       │                                                              │
│       ▼                                                              │
│  ESP32 Motor Controller                                             │
│       │                                                              │
│       │ Turns physical relays ON/OFF based on response              │
│       ▼                                                              │
│  💧 Water pump turns ON or OFF                                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                    STEP 3: MOBILE APP MONITORING                    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📱 Flutter Mobile App                                               │
│       │                                                              │
│       │ GET /api/status/                                            │
│       ▼                                                              │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                 DJANGO BACKEND                            │       │
│  │                                                           │       │
│  │  Returns combined status:                                 │       │
│  │  - Latest moisture reading                                │       │
│  │  - All motor states                                       │       │
│  │  - System mode (MANUAL/AUTOMATIC)                        │       │
│  │  - Threshold configurations                               │       │
│  └──────────────────────────────────────────────────────────┘       │
│       │                                                              │
│       ▼                                                              │
│  📱 App displays dashboard with all information                      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 7. All API Endpoints Explained

The API has two main groups: **Authentication** and **Soil Moisture/Motor Control**.

### 🔐 Authentication Endpoints (`/api/auth/`)

#### 7.1 Register New User

```http
POST /api/auth/register/
```

**Purpose:** Create a new user account

**Request Body:**
```json
{
    "username": "farmer1",
    "email": "farmer1@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Success Response (201):**
```json
{
    "token": "abc123def456...",
    "user": {
        "id": 1,
        "username": "farmer1",
        "email": "farmer1@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "message": "Registration successful!"
}
```

**What happens internally:**
1. Validates username doesn't exist
2. Validates email doesn't exist
3. Checks passwords match
4. Creates User in database
5. Creates authentication Token
6. Returns token (for future authenticated requests)

---

#### 7.2 Login

```http
POST /api/auth/login/
```

**Purpose:** Authenticate user and get access token

**Request Body:**
```json
{
    "username": "farmer1",
    "password": "securepass123"
}
```

**Success Response (200):**
```json
{
    "token": "ce0a0d6d69025b72cc5025113cab649149de967b",
    "user": {
        "id": 1,
        "username": "farmer1",
        "email": "farmer1@example.com"
    },
    "message": "Login successful!"
}
```

**Error Response (401):**
```json
{
    "error": "Invalid username or password"
}
```

---

#### 7.3 Get User Profile

```http
GET /api/auth/profile/
Authorization: Token <your-token>
```

**Purpose:** Get current logged-in user's information

**Success Response (200):**
```json
{
    "id": 1,
    "username": "farmer1",
    "email": "farmer1@example.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

---

#### 7.4 Logout

```http
POST /api/auth/logout/
Authorization: Token <your-token>
```

**Purpose:** Invalidate the user's token

**Success Response (200):**
```json
{
    "message": "Logout successful!"
}
```

---

### 📊 Sensor Data Endpoints (`/api/data/`)

#### 7.5 Receive Sensor Data (ESP32 → Backend)

```http
POST /api/data/receive/
```

**Purpose:** ESP32 sensors send moisture readings here

**Request Body:**
```json
{
    "nodeid": "sensor_zone1",
    "value": 45.5
}
```

**Success Response (201):**
```json
{
    "status": "ok",
    "message": "Data received successfully",
    "nodeid": "sensor_zone1",
    "sensor_created": false,
    "moisture_value": 45.5,
    "mode": "AUTOMATIC",
    "motor_update": {
        "motor_name": "Pump 1",
        "sensor_nodeid": "sensor_zone1",
        "new_state": "OFF",
        "reason": "Moisture 45.5% is below threshold 50%"
    },
    "threshold": 50.0
}
```

**Key Features:**
- No authentication required (for IoT devices)
- Auto-creates Sensor if nodeid is new
- In AUTOMATIC mode, updates motor state based on threshold

---

#### 7.6 List All Sensor Data

```http
GET /api/data/
GET /api/data/?page=1&page_size=100
```

**Purpose:** Get all moisture readings with pagination

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "records": [
            {
                "id": "uuid-here",
                "nodeid": "sensor_zone1",
                "value": 45.5,
                "timestamp": "2025-12-28T10:30:00Z",
                "moisture_status": "OPTIMAL",
                "age_seconds": 120.5
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 100,
            "total_count": 500,
            "total_pages": 5
        }
    },
    "message": "Records retrieved successfully"
}
```

---

#### 7.7 Get Latest Sensor Data

```http
GET /api/data/latest/
GET /api/data/latest/?nodeid=sensor_zone1
```

**Purpose:** Get the most recent reading

**Success Response (200):**
```json
{
    "success": true,
    "data": {
        "sensor_data": {
            "nodeid": "sensor_zone1",
            "value": 45.5,
            "moisture_status": "OPTIMAL"
        },
        "motor_recommendation": {
            "desired_state": "OFF",
            "reason": "Moisture adequate"
        }
    }
}
```

---

#### 7.8 Filtered Sensor Data

```http
GET /api/data/filtered/?nodeid=sensor_zone1&start_date=2025-12-01&end_date=2025-12-31
```

**Purpose:** Get filtered data by date range and/or sensor

---

### 🔧 Motor Control Endpoints (`/api/motors/`)

#### 7.9 List/Create Motors

```http
GET /api/motors/
POST /api/motors/
```

**GET Response:**
```json
{
    "success": true,
    "data": {
        "motors": [
            {
                "id": 1,
                "name": "Pump Zone 1",
                "sensor_nodeid": "sensor_zone1",
                "state": "ON",
                "state_display": "On",
                "is_on": true
            }
        ]
    }
}
```

**POST Request (Create Motor):**
```json
{
    "name": "Pump Zone 2",
    "sensor": "sensor_zone2",
    "state": "OFF"
}
```

---

#### 7.10 Motor Detail

```http
GET /api/motors/<id>/
PUT /api/motors/<id>/
DELETE /api/motors/<id>/
```

**Purpose:** Get, update, or delete a specific motor

---

#### 7.11 Control Motor (Manual Mode Only)

```http
POST /api/motors/<id>/control/
```

**Request Body:**
```json
{
    "state": "ON"
}
```

**Success Response:**
```json
{
    "success": true,
    "data": {
        "motor": {
            "id": 1,
            "name": "Pump 1",
            "state": "ON"
        }
    },
    "message": "Motor turned ON"
}
```

**Error (if in AUTOMATIC mode):**
```json
{
    "success": false,
    "errors": {
        "detail": "Cannot manually control motor in AUTOMATIC mode"
    }
}
```

---

#### 7.12 Motors Info (Simple - For ESP32)

```http
GET /api/motorsinfo/
```

**Purpose:** ESP32 motor controller fetches this to know which motors to turn ON/OFF

**Response (Simple JSON):**
```json
{
    "sensor_zone1": "ON",
    "sensor_zone2": "OFF",
    "greenhouse_01": "ON"
}
```

**Why so simple?**
- ESP32 has limited memory
- Easy to parse
- No authentication overhead

---

#### 7.13 Bulk Motor Control

```http
POST /api/motors/bulk-control/
```

**Request Body:**
```json
{
    "motors": [
        {"id": 1, "state": "ON"},
        {"id": 2, "state": "OFF"},
        {"id": 3, "state": "ON"}
    ]
}
```

**Purpose:** Control multiple motors at once (MANUAL mode only)

---

### ⚙️ System Configuration Endpoints

#### 7.14 Get/Set System Mode

```http
GET /api/mode/
POST /api/mode/set/
```

**POST Request:**
```json
{
    "mode": "AUTOMATIC"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "system_mode": {
            "mode": "AUTOMATIC",
            "mode_display": "Automatic"
        }
    },
    "message": "System mode set to AUTOMATIC"
}
```

| Mode | Description |
|------|-------------|
| `AUTOMATIC` | Motors controlled by sensor readings vs thresholds |
| `MANUAL` | User controls motors directly via app |

---

#### 7.15 Get/Set Thresholds

```http
GET /api/config/thresholds/
GET /api/config/thresholds/?nodeid=sensor_zone1
POST /api/config/thresholds/set/
```

**POST Request:**
```json
{
    "nodeid": "sensor_zone1",
    "threshold": 55.0
}
```

**What thresholds do:**
- Motor turns **ON** when moisture value **exceeds** the threshold
- Motor turns **OFF** when moisture value is **below or equal** to threshold

---

### 📈 Dashboard & Health Endpoints

#### 7.16 System Status (Combined)

```http
GET /api/status/
```

**Purpose:** Get everything at once (for mobile app dashboard)

**Response:**
```json
{
    "success": true,
    "data": {
        "latest_moisture": { ... },
        "motors": [ ... ],
        "system_mode": { ... },
        "thresholds": [ ... ],
        "timestamp": "2025-12-28T10:30:00Z"
    }
}
```

---

#### 7.17 Dashboard Statistics

```http
GET /api/stats/dashboard/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "total_readings": 5000,
        "avg_moisture_24h": 45.5,
        "avg_moisture_7d": 48.2,
        "motors_on_count": 2,
        "motors_off_count": 3,
        "system_mode": "AUTOMATIC",
        "last_reading_time": "2025-12-28T10:30:00Z",
        "unique_nodes": 5
    }
}
```

---

#### 7.18 Health Check

```http
GET /api/health/
```

**Purpose:** Check if system is working properly

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "database": "healthy",
        "last_sensor_update": "2025-12-28T10:30:00Z",
        "time_since_last_update": "5 minutes ago",
        "motors_count": 5
    }
}
```

---

## 8. Authentication System

### How Token Authentication Works:

```
┌─────────────────┐                           ┌─────────────────┐
│   Mobile App    │                           │  Django Server  │
└────────┬────────┘                           └────────┬────────┘
         │                                             │
         │  1. POST /api/auth/login/                  │
         │  {"username": "farmer1", "password": "x"}  │
         │ ──────────────────────────────────────────▶│
         │                                             │
         │  2. Server validates credentials           │
         │                                             │
         │  3. Response with token                    │
         │  {"token": "abc123..."}                    │
         │◀────────────────────────────────────────── │
         │                                             │
         │  4. Store token locally                    │
         │                                             │
         │  5. Future requests include token          │
         │  GET /api/auth/profile/                    │
         │  Header: Authorization: Token abc123...    │
         │ ──────────────────────────────────────────▶│
         │                                             │
         │  6. Server validates token                 │
         │  7. Response with user data                │
         │◀────────────────────────────────────────── │
```

### Token Storage:
- Django stores tokens in `authtoken_token` table
- Each user has one token
- Token is a random 40-character string
- Token doesn't expire (until logout or manually deleted)

### Public vs Protected Endpoints:

| Endpoint | Authentication |
|----------|----------------|
| `/api/auth/register/` | ❌ Public |
| `/api/auth/login/` | ❌ Public |
| `/api/auth/profile/` | ✅ Required |
| `/api/auth/logout/` | ✅ Required |
| `/api/data/receive/` | ❌ Public (IoT devices) |
| `/api/motorsinfo/` | ❌ Public (IoT devices) |
| `/api/motors/` | ❌ Public |
| All other endpoints | ❌ Public |

**Note:** Most sensor/motor endpoints are public because ESP32 devices can't easily handle authentication.

---

## 9. Motor Control Logic

### The Threshold Logic:

```python
# From motor_logic.py

def get_motor_state(moisture_value, current_state, threshold):
    """
    Motor turns ON when moisture > threshold
    Motor turns OFF when moisture <= threshold
    """
    if moisture_value > threshold:
        return 'ON'
    else:
        return 'OFF'
```

### Example Scenarios:

| Threshold | Moisture Reading | Motor State | Reason |
|-----------|-----------------|-------------|--------|
| 50% | 60% | ON | 60 > 50, moisture too high |
| 50% | 45% | OFF | 45 ≤ 50, moisture okay |
| 50% | 50% | OFF | Equal to threshold |
| 30% | 25% | OFF | Below threshold |

### Why This Logic?

In drip irrigation:
- **High moisture** = Too much water = Turn pump ON to drain/circulate
- **Low moisture** = Needs water = Turn pump OFF (sensor might indicate dry soil needs watering differently)

**Note:** The logic might seem inverted. Adjust the threshold meaning based on your actual use case!

### Automatic vs Manual Mode:

```
┌─────────────────────────────────────────────────────┐
│                  AUTOMATIC MODE                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Sensor sends data → Backend checks threshold →     │
│  Backend updates motor state automatically          │
│                                                      │
│  ✅ Motor state changes based on sensor readings    │
│  ❌ User cannot manually control motors             │
│                                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                   MANUAL MODE                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  User sends command → Backend updates motor state   │
│                                                      │
│  ✅ User can turn motors ON/OFF directly           │
│  ❌ Sensor readings don't affect motor state        │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 10. ESP32 Integration

### Two Types of ESP32 Nodes:

#### 1. Sensor Node (Sends Data)

```cpp
// Arduino/ESP32 code concept
const char* nodeid = "sensor_zone1";
const char* serverUrl = "http://server:8000/api/data/receive/";

void sendMoistureData(float moisture) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    String payload = "{\"nodeid\":\"" + String(nodeid) + 
                     "\",\"value\":" + String(moisture) + "}";
    
    int httpCode = http.POST(payload);
    http.end();
}
```

#### 2. Motor Controller Node (Fetches States)

```cpp
// Arduino/ESP32 code concept
const char* motorsUrl = "http://server:8000/api/motorsinfo/";

void controlMotors() {
    HTTPClient http;
    http.begin(motorsUrl);
    int httpCode = http.GET();
    
    if (httpCode == 200) {
        String payload = http.getString();
        // Parse JSON: {"sensor_zone1": "ON", "sensor_zone2": "OFF"}
        // Control relays based on states
    }
    http.end();
}

void loop() {
    controlMotors();
    delay(5000);  // Check every 5 seconds
}
```

### Communication Flow:

```
┌──────────────────┐          ┌──────────────────┐
│  Sensor ESP32    │          │  Controller ESP32│
│  (reads soil)    │          │  (has relays)    │
└────────┬─────────┘          └────────┬─────────┘
         │                             │
         │ Every 30 seconds            │ Every 5 seconds
         │                             │
         ▼                             ▼
    POST /api/data/receive/       GET /api/motorsinfo/
    {"nodeid":"x","value":45}     
         │                             │
         ▼                             ▼
┌────────────────────────────────────────────────────┐
│                  DJANGO BACKEND                     │
│  - Saves moisture data                             │
│  - Updates motor states (if AUTOMATIC)             │
│  - Serves motor states via /motorsinfo             │
└────────────────────────────────────────────────────┘
```

---

## 11. Running the Server

### Development Server:

```bash
# Navigate to project directory
cd ThopaSichai_backend-main

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations (set up database)
python manage.py migrate

# Create admin user (first time only)
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000
```

### Accessing the Server:

| URL | Purpose |
|-----|---------|
| `http://localhost:8000/admin/` | Django Admin Panel |
| `http://localhost:8000/api/docs/` | Swagger API Documentation |
| `http://localhost:8000/api/redoc/` | ReDoc API Documentation |

### Admin Panel:

Access at `http://localhost:8000/admin/` to:
- View all users
- View all sensors
- View all motors
- View all moisture readings
- Manage system mode
- Manage thresholds

---

## 📝 Quick Reference: All Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login and get token |
| POST | `/api/auth/logout/` | Logout (invalidate token) |
| GET | `/api/auth/profile/` | Get user profile |
| | | |
| POST | `/api/data/receive/` | ESP32 sends moisture data |
| GET | `/api/data/` | List all readings (paginated) |
| GET | `/api/data/latest/` | Get latest reading |
| GET | `/api/data/filtered/` | Filter by date/nodeid |
| | | |
| GET/POST | `/api/motors/` | List/create motors |
| GET/PUT/DEL | `/api/motors/<id>/` | Motor CRUD |
| POST | `/api/motors/<id>/control/` | Control single motor |
| POST | `/api/motors/bulk-control/` | Control multiple motors |
| GET | `/api/motorsinfo/` | Simple motor states (ESP32) |
| | | |
| GET | `/api/mode/` | Get system mode |
| POST | `/api/mode/set/` | Set system mode |
| GET | `/api/config/thresholds/` | Get thresholds |
| POST | `/api/config/thresholds/set/` | Set threshold |
| | | |
| GET | `/api/status/` | Combined system status |
| GET | `/api/stats/dashboard/` | Dashboard statistics |
| GET | `/api/health/` | Health check |

---

## 🎯 Key Takeaways

1. **Everything links by `nodeid`** - Sensors, Motors, and Thresholds are all connected by the unique sensor node ID.

2. **Two modes**: AUTOMATIC (system controls motors) and MANUAL (user controls motors).

3. **Simple ESP32 endpoints**: `/api/data/receive/` and `/api/motorsinfo/` are designed for IoT devices - no auth, simple JSON.

4. **Auto-creation**: New sensors are automatically created when a new nodeid sends data.

5. **Token auth for users**: Mobile app users authenticate with tokens, but IoT endpoints are public.

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot control motor in AUTOMATIC mode" | Switch to MANUAL mode first via `/api/mode/set/` |
| Sensor data not saving | Check nodeid is provided in request |
| Motor not updating | Ensure motor is linked to sensor via nodeid |
| Token invalid | User needs to login again |
| Database errors | Run `python manage.py migrate` |

---

*Created for ThopaSichai Drip Irrigation System*
*Last Updated: December 28, 2025*
