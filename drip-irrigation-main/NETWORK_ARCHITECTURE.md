# Network Architecture - Smart Drip Irrigation System

## System Overview
```
┌──────────────────────────────────────────────────────────────┐
│                     Home Wi-Fi Router                         │
│                   (192.168.1.x network)                       │
└─────────┬────────────┬────────────┬──────────────────────────┘
          │            │            │
    ┌─────┴─────┐ ┌───┴────┐  ┌────┴─────────────┐
    │  Laptop   │ │ ESP32  │  │  ESP32 Nodes     │
    │  Server   │ │imshiva2│  │ (Field Devices)  │
    │(Main Hub) │ │        │  │  1, 2, 3, 4...   │
    └───────────┘ └────────┘  └──────────────────┘
```

## Architecture Components

### 1. **Network Topology: Star Topology**
- **Router**: Acts as central hub (192.168.1.1)
- **Laptop Server**: Main backend (e.g., 192.168.1.100)
- **ESP32 Nodes**: Field devices (192.168.1.201-250 range)

### 2. **Communication Protocols**

#### A. **MQTT (Primary Protocol)**
```
Laptop Server runs Mosquitto MQTT Broker
├── Topic Structure:
│   ├── irrigation/{device_id}/status
│   ├── irrigation/{device_id}/sensors
│   ├── irrigation/{device_id}/commands
│   └── irrigation/{device_id}/telemetry
```

#### B. **HTTP REST API (Secondary)**
```
Laptop Server exposes REST endpoints
├── GET  /api/devices
├── POST /api/devices/{id}/control
├── GET  /api/devices/{id}/status
└── POST /api/devices/{id}/schedule
```

### 3. **Device Roles**

#### **Laptop Server (192.168.1.100)**
- **Services Running:**
  - Mosquitto MQTT Broker (port 1883)
  - Node.js/Python REST API (port 3000/5000)
  - MongoDB/SQLite Database
  - Firebase/AWS IoT Bridge
  
- **Functions:**
  - Data aggregation from all ESP32 nodes
  - Decision-making logic (scheduling, alerts)
  - Mobile app backend
  - Historical data storage
  - OTA update server

#### **ESP32 "imshiva2" (Test Node)**
- **IP**: Static/DHCP assigned by router
- **Functions:**
  - Testing and development node
  - Can act as field controller or gateway
  - Sensor data collection
  - Local irrigation control

#### **ESP32 Field Nodes (192.168.1.201+)**
- **Naming**: `smartkisan_zone_{1-4}`
- **Functions:**
  - Soil moisture monitoring (4 sensors per zone)
  - Solenoid valve control
  - Tank level monitoring
  - Pump control (irrigation + refill)
  - Local autonomous operation (offline mode)

## 4. **Data Flow**

### Normal Operation (Online)
```
ESP32 Node → WiFi → Router → Laptop Server → Firebase/AWS
     ↓                                ↓
 Local Control                   Mobile App
 (Autonomous)                    (Monitoring)
```

### Offline Mode (No Internet)
```
ESP32 Node → Local Memory → Auto-irrigation based on:
   ├── Soil moisture thresholds
   ├── Tank level
   └── Pre-programmed schedules
```

## 5. **Network Configuration**

### IP Allocation Plan
```
Router:           192.168.1.1
Laptop Server:    192.168.1.100 (static)
ESP32 Test Node:  192.168.1.200 (imshiva2)
ESP32 Zone 1:     192.168.1.201
ESP32 Zone 2:     192.168.1.202
ESP32 Zone 3:     192.168.1.203
ESP32 Zone 4:     192.168.1.204
Reserved Range:   192.168.1.205-250 (future expansion)
```

### WiFi Credentials Storage
```python
# On ESP32 (encrypted in flash)
WIFI_SSID = "your_router_ssid"
WIFI_PASSWORD = "@Namnagar29"
MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883
```

## 6. **Security Measures**

1. **Network Level:**
   - WPA2/WPA3 encryption on router
   - MAC address filtering (optional)
   - Guest network isolation

2. **Application Level:**
   - MQTT authentication (username/password)
   - TLS/SSL for external communication
   - Device unique IDs and API keys
   - OTA update verification (signed firmware)

3. **Physical Level:**
   - IP65 rated enclosures
   - Tamper detection (optional)

## 7. **Redundancy & Failover**

### Network Failure
```
Internet Down → ESP32 continues local operation
WiFi Down → ESP32 runs on last known schedule + sensor logic
Server Down → Mobile app shows "offline" but devices work autonomously
```

### Power Failure
```
Solar Panel + Battery → 24/7 operation
Low Battery → Enter power-saving mode:
   ├── Reduce WiFi polling
   ├── Disable non-critical sensors
   └── Maintain critical irrigation only
```

## 8. **Testing Plan**

### Phase 1: Local Network Testing
1. ✅ Connect ESP32 (imshiva2) to router
2. ✅ Ping laptop server from ESP32
3. ✅ Establish MQTT connection
4. ✅ Send test telemetry data

### Phase 2: Multi-Device Testing
1. Add second ESP32 node
2. Test simultaneous connections
3. Verify data separation
4. Test command broadcast

### Phase 3: Stress Testing
1. Network dropout simulation
2. Server restart scenarios
3. Rapid command sequences
4. 24-hour burn-in test

## 9. **Scalability**

### Current Setup (Local Network)
- Up to 20 ESP32 devices per router
- Single laptop server

### Future Expansion
- **LoRaWAN Gateway**: For nodes beyond WiFi range
- **Edge Computing**: Raspberry Pi as local aggregator
- **Mesh Network**: ESP-NOW for inter-device communication
- **Cellular Backup**: 4G modem for critical updates

## 10. **Development Environment**

### On ESP32 (MicroPython)
```python
# Dependencies:
- umqtt.simple (MQTT client)
- urequests (HTTP requests)
- ujson (JSON parsing)
- network (WiFi management)
```

### On Laptop Server (Node.js/Python)
```javascript
// Dependencies:
- mosquitto (MQTT broker)
- express (REST API)
- socket.io (real-time updates)
- mongodb/sqlite (database)
```

---

## Quick Start Guide

1. **Setup Laptop Server:**
   ```bash
   sudo apt install mosquitto mosquitto-clients
   sudo systemctl enable mosquitto
   sudo systemctl start mosquitto
   ```

2. **Configure ESP32:**
   - Flash MicroPython firmware
   - Upload network config
   - Test connectivity

3. **Verify Communication:**
   ```bash
   # On laptop, subscribe to MQTT:
   mosquitto_sub -h localhost -t "irrigation/#"
   
   # ESP32 publishes:
   mosquitto_pub -h 192.168.1.100 -t "irrigation/imshiva2/status" -m "online"
   ```

---

**Next Steps:**
- Implement full ESP32 firmware (main.py)
- Create laptop server API
- Develop mobile app backend integration
- Field testing on pilot farm
