# ThopaSichai - Smart Drip Irrigation System

ThopaSichai (meaning "Drip Irrigation" in Nepali) is an autonomous, solar-powered IoT-based smart drip irrigation system designed for small-to-medium-hold farmers. The system uses real-time soil moisture sensors and automated motor control to optimize water usage and reduce manual labor in agricultural irrigation.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Components](#components)
  - [Backend Server](#backend-server)
  - [ESP32 Firmware](#esp32-firmware)
  - [Mobile Application](#mobile-application)
  - [MQTT Server](#mqtt-server)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Testing](#testing)
- [License](#license)

## Overview

The ThopaSichai system consists of three main components working together:

1. **ESP32 Sensor Nodes** - Field devices that collect soil moisture data and control irrigation valves
2. **Django Backend Server** - Central server that processes sensor data, makes irrigation decisions, and provides REST API
3. **Flutter Mobile Application** - User interface for farmers to monitor and control the irrigation system

The system supports both automatic and manual operation modes. In automatic mode, motors are controlled based on configurable soil moisture thresholds. The system can operate autonomously during network outages using local decision-making on ESP32 nodes.

## System Architecture

![System Architecture](vdv.drawio.svg)

### Network Topology

The system uses a star topology with the following components:

- **Central Router** - Acts as the network hub (192.168.1.x network)
- **Backend Server** - Runs Django REST API and MQTT broker
- **ESP32 Gateway** - Receives data from sensor nodes via ESP-NOW and forwards to server via WiFi
- **ESP32 Sensor Nodes** - Field devices with soil moisture sensors
- **ESP32 Actuator Node** - Controls relay switches for motors/pumps

### Communication Protocols

- **ESP-NOW** - Low-power communication between sensor nodes and gateway
- **MQTT** - Real-time messaging between ESP32 devices and server
- **HTTP REST API** - Mobile app to backend communication
- **WiFi** - Gateway and actuator connection to local network

### Data Flow

```
Sensor Nodes (ESP-NOW) --> Gateway (WiFi/HTTP) --> Django Backend --> Mobile App
                                                        |
                                                        v
Actuator Node (WiFi/HTTP) <-- Motor Commands <-- Motor Logic
```

## Project Structure

```
ThopaSichai/
|
|-- drip-irrigation-main/       # System documentation and MQTT server
|   |-- server/                 # MQTT test server
|   |-- micropy/                # ESP32 MicroPython libraries
|   |-- NETWORK_ARCHITECTURE.md
|   |-- DEPLOYMENT_GUIDE.md
|   |-- TESTING_CHECKLIST.md
|   +-- setup_server.sh
|
|-- ThopaSichai_backend/        # Django REST API backend
|   |-- accounts/               # User authentication module
|   |-- soil_moisture/          # Sensor data and motor control module
|   |-- ThopaSichai_backend/    # Django project settings
|   |-- manage.py
|   +-- requirements.txt
|
|-- ThopaSichai_Frontend/       # Flutter mobile application
|   +-- thopa_sichai_app/
|       |-- lib/                # Dart source code
|       |-- android/            # Android build files
|       +-- pubspec.yaml
|
+-- EspCodes/                   # ESP32 MicroPython firmware
    |-- Gateway.py              # WiFi gateway node
    |-- Actuator.py             # Motor controller node
    |-- Kullo1.py               # Sensor node 1
    +-- Kullo2.py               # Sensor node 2
```

## Components

### Backend Server

The backend is built with Django REST Framework and provides:

- **User Authentication** - Registration, login, logout with token-based authentication
- **Sensor Data API** - Receives and stores soil moisture readings
- **Motor Control** - Automatic and manual motor state management
- **Threshold Configuration** - Per-sensor moisture thresholds

Key models:
- `Sensor` - Represents a sensor node identified by nodeid
- `Motor` - One-to-one relationship with sensor, stores ON/OFF state
- `ThresholdConfig` - Low and high moisture thresholds per sensor
- `SoilMoisture` - Time-series moisture readings

### ESP32 Firmware

The system uses multiple ESP32 nodes running MicroPython:

**Gateway Node (Gateway.py)**
- Connects to WiFi network
- Receives sensor data via ESP-NOW
- Forwards data to Django backend via HTTP

**Sensor Nodes (Kullo1.py, Kullo2.py)**
- Reads soil moisture from capacitive sensors
- Transmits data to gateway via ESP-NOW
- Low power consumption design

**Actuator Node (Actuator.py)**
- Polls backend for motor states
- Controls relay module for pumps
- Reads ultrasonic tank level sensors

### Mobile Application

Flutter-based cross-platform mobile application providing:

- User registration and login
- Real-time dashboard with sensor readings
- Manual motor control
- Threshold configuration
- Historical data visualization
- Notification settings

### MQTT Server

Optional MQTT broker (Mosquitto) for real-time communication:

Topic structure:
- `irrigation/{device_id}/status` - Device status updates
- `irrigation/{device_id}/sensors` - Sensor data
- `irrigation/{device_id}/commands` - Control commands
- `irrigation/{device_id}/telemetry` - Device telemetry

## Hardware Requirements

### Per Zone Kit
- 1x ESP32 Development Board (sensor node)
- 1x Capacitive Soil Moisture Sensor
- 1x 12V Solenoid Valve
- Power supply (solar panel + battery recommended)

### Central Controller
- 1x ESP32 (Gateway)
- 1x ESP32 (Actuator with relay module)
- 1x Ultrasonic Tank Level Sensor
- 1x 12V DC Pump

### Server
- Laptop or Raspberry Pi running Ubuntu/Linux
- WiFi connectivity

## Software Requirements

### Backend Server
- Python 3.8+
- Django 4.x
- Django REST Framework
- SQLite (development) or PostgreSQL (production)

### ESP32 Nodes
- MicroPython firmware
- Required libraries: network, espnow, urequests, machine

### Mobile Application
- Flutter SDK 3.x
- Dart 3.x
- Android SDK (for Android builds)

### MQTT Server (Optional)
- Mosquitto MQTT Broker

## Installation

### Backend Setup

```bash
cd ThopaSichai_backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### ESP32 Setup

1. Flash MicroPython firmware to ESP32
2. Update WiFi credentials and server IP in configuration
3. Upload code using ampy or Thonny:

```bash
ampy --port /dev/ttyUSB0 put Gateway.py main.py
```

### Mobile App Setup

```bash
cd ThopaSichai_Frontend/thopa_sichai_app
flutter pub get
flutter run
```

### MQTT Server Setup (Optional)

```bash
cd drip-irrigation-main
./setup_server.sh
```

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register/ | Register new user |
| POST | /api/auth/login/ | User login |
| POST | /api/auth/logout/ | User logout |
| GET | /api/auth/profile/ | Get user profile |

### Sensor Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/data/receive/ | Submit sensor reading |
| GET | /api/motorsinfo/ | Get all motor states |
| GET | /api/motor/{nodeid}/ | Get specific motor state |
| POST | /api/motor/{nodeid}/control/ | Manual motor control |

### Data Format

Sensor data submission:
```json
{
    "nodeid": "sensor_zone_1",
    "value": 45.5
}
```

Motor info response:
```json
{
    "sensor_zone_1": "ON",
    "sensor_zone_2": "OFF"
}
```

## Configuration

### Threshold Configuration

Each sensor can have independent moisture thresholds:

- **Low Threshold** (default: 30%) - Motor turns ON when moisture drops below this value
- **High Threshold** (default: 70%) - Motor turns OFF when moisture rises above this value

Configure via Django admin panel or API.

### ESP32 Configuration

Edit the configuration section in each ESP32 script:

```python
WIFI_SSID = "your_network"
WIFI_PASS = "your_password"
SERVER_HOST = "192.168.1.100"
SERVER_PORT = 8000
```

## Testing

### Backend Tests

```bash
cd ThopaSichai_backend
python manage.py test
```

### API Testing

```bash
# Test sensor data submission
curl -X POST http://localhost:8000/api/data/receive/ \
  -H "Content-Type: application/json" \
  -d '{"nodeid": "test_node_1", "value": 25.0}'

# Test motor info endpoint
curl http://localhost:8000/api/motorsinfo/
```

### ESP32 Testing

Monitor serial output:
```bash
screen /dev/ttyUSB0 115200
```

## License

This project is developed for agricultural modernization in Nepal.
