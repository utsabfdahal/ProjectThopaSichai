# 🌱 Smart Drip Irrigation System - ESP32 to Laptop Communication

## 📁 Project Structure

```
drip-irrigation/
├── 📄 NETWORK_ARCHITECTURE.md    ← Start here for system design
├── 📄 DEPLOYMENT_GUIDE.md         ← Step-by-step setup instructions
├── 📄 TESTING_CHECKLIST.md        ← Complete testing procedures
├── 📄 NETWORK_DIAGRAM.txt         ← Visual network layout
├── 📄 README_SETUP.md             ← This file
├── 🔧 setup_server.sh             ← Quick server setup script
│
├── micropy/                       ← ESP32 MicroPython code
│   └── src/
│       ├── config.py              ← Network & device configuration
│       └── main.py                ← Main ESP32 control logic
│
└── server/                        ← Laptop server code
    ├── mqtt_test_server.py        ← MQTT test server
    └── requirements.txt           ← Python dependencies
```

---

## 🎯 Quick Start (TL;DR)

### On Laptop (Ubuntu/Linux):
```bash
# 1. Run automated setup
cd /home/krishna/Projects/drip-irrigation
./setup_server.sh

# 2. Note your laptop IP (e.g., 192.168.1.100)

# 3. Start server
cd server
python3 mqtt_test_server.py
```

### On ESP32:
```bash
# 1. Edit config.py with your WiFi credentials and laptop IP

# 2. Upload code to ESP32
ampy --port /dev/ttyUSB0 put micropy/src/config.py
ampy --port /dev/ttyUSB0 put micropy/src/main.py

# 3. Connect to serial monitor
screen /dev/ttyUSB0 115200

# 4. Press RESET on ESP32
```

### Verify Communication:
```bash
# In another terminal, watch MQTT traffic
mosquitto_sub -h localhost -t "irrigation/#" -v

# Send test command
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"ping"}'
```

---

## 📚 Documentation Overview

### 1. **NETWORK_ARCHITECTURE.md**
Complete technical architecture including:
- Network topology (star configuration)
- MQTT topic structure
- Communication protocols
- IP allocation plan
- Security measures
- Offline operation mode
- Scalability considerations

**Read this first** to understand how everything connects.

### 2. **DEPLOYMENT_GUIDE.md**
Detailed step-by-step instructions for:
- Installing Mosquitto MQTT broker on laptop
- Configuring ESP32 with MicroPython
- Uploading code to ESP32
- Testing connectivity
- Troubleshooting common issues

**Use this for** actual implementation.

### 3. **TESTING_CHECKLIST.md**
Comprehensive testing procedures with checkboxes:
- Pre-flight checks
- Laptop server setup verification
- ESP32 preparation steps
- First connection tests
- Communication tests (ping, LED, status)
- Reliability tests (reconnection, stability)
- Network diagnostics
- 24-hour burn-in test

**Use this to** systematically verify everything works.

### 4. **NETWORK_DIAGRAM.txt**
ASCII art visualization of:
- System architecture
- Data flow diagrams
- MQTT topic tree
- Message payload examples
- Offline operation flowchart
- Power management

**Use this for** quick visual reference.

---

## 🔑 Key Configuration

### WiFi Credentials
**File:** `micropy/src/config.py`
```python
WIFI_SSID = "your_router_ssid"      # ← Update this
WIFI_PASSWORD = "@Namnagar29"       # ← Already set
```

### Laptop Server IP
**File:** `micropy/src/config.py`
```python
MQTT_BROKER = "192.168.1.100"       # ← Update with your laptop IP
```

### Device Identity
**File:** `micropy/src/config.py`
```python
DEVICE_ID = "imshiva2"              # Test node name
```

---

## 🧪 Testing Commands

### Check Laptop IP:
```bash
ip addr show | grep inet
```

### Test MQTT Broker:
```bash
# Subscribe to all topics
mosquitto_sub -h localhost -t "#" -v

# Publish test message
mosquitto_pub -h localhost -t test -m "hello"
```

### Monitor ESP32 Serial:
```bash
screen /dev/ttyUSB0 115200
# To exit: Ctrl+A then K then Y
```

### Send Commands to ESP32:
```bash
# Ping
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"ping"}'

# Request status
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"status"}'

# Blink LED 5 times
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"test_led","times":5}'
```

---

## 🎓 Understanding the System

### Communication Flow:
```
ESP32 → WiFi → Router → Laptop → MQTT Broker → Server Script
                                      ↓
                                Mobile App (future)
```

### MQTT Topics:
```
irrigation/
  ├── imshiva2/
  │   ├── status       (ESP32 publishes: online/offline)
  │   ├── sensors      (ESP32 publishes: sensor data)
  │   ├── commands     (Server publishes: ESP32 subscribes)
  │   ├── telemetry    (ESP32 publishes: full status)
  │   └── heartbeat    (ESP32 publishes: every 30s)
```

### Data Types:
- **Status**: JSON with device_id, status, timestamp
- **Sensors**: JSON with soil moisture, tank level, temp, humidity
- **Commands**: JSON with action (ping, status, irrigate, etc.)
- **Heartbeat**: JSON with uptime, free memory

---

## 🚨 Troubleshooting

### ESP32 won't connect to WiFi
1. Check SSID spelling in `config.py`
2. Verify password: `@Namnagar29`
3. Ensure router uses 2.4GHz (not 5GHz)
4. Move ESP32 closer to router

### Can't ping laptop server
1. Check laptop IP: `ip addr show`
2. Update `MQTT_BROKER` in `config.py`
3. Check firewall: `sudo ufw allow 1883/tcp`
4. Verify Mosquitto running: `systemctl status mosquitto`

### MQTT connection fails
1. Start Mosquitto: `sudo systemctl start mosquitto`
2. Check port 1883: `netstat -tuln | grep 1883`
3. View logs: `sudo tail -f /var/log/mosquitto/mosquitto.log`

### ESP32 crashes/reboots
1. Check power supply (use quality USB cable)
2. Monitor memory: look for `free_mem` dropping
3. Check serial logs for exceptions

---

## 📊 Expected Behavior

### On ESP32 Boot:
```
Smart Drip Irrigation System Starting...
Device ID: imshiva2
Target Server: 192.168.1.100
==================================================
[INFO] Connecting to WiFi: your_router_ssid
[SUCCESS] WiFi connected! IP: 192.168.1.200
[INFO] Pinging server at 192.168.1.100...
[SUCCESS] Server 192.168.1.100 is reachable!
[INFO] Connecting to MQTT broker...
[SUCCESS] MQTT connected and subscribed!
[INFO] Entering main control loop...
```

### On Laptop Server:
```
🌱 Smart Drip Irrigation - MQTT Test Server
Broker: localhost:1883
Waiting for ESP32 devices to connect...

[2025-12-23 10:30:15] Topic: irrigation/imshiva2/status
Payload: {
  "device_id": "imshiva2",
  "status": "online",
  "timestamp": 1703318400,
  "wifi_rssi": -45
}

🆕 New device connected: imshiva2
```

### Heartbeat (every 30 seconds):
```
[INFO] Heartbeat sent
```

LED flashes briefly to show activity.

---

## 🛠️ Hardware Requirements

### For Testing (Current):
- ✅ ESP32 Dev Board
- ✅ USB cable
- ✅ Laptop/Computer
- ✅ WiFi Router

### For Production (Future):
- ESP32 in weatherproof enclosure
- 30W Solar panel
- 12V LiFePO4 battery
- 4x Soil moisture sensors
- Ultrasonic tank level sensor
- 4x Solenoid valves
- 2x 12V DC pumps
- Voltage regulator (12V → 3.3V)
- PCB with terminal blocks

---

## 📞 Support & Resources

### Useful Links:
- **MicroPython Docs**: https://docs.micropython.org/
- **ESP32 Pinout**: https://randomnerdtutorials.com/esp32-pinout-reference-gpios/
- **MQTT Tutorial**: http://www.steves-internet-guide.com/mqtt/
- **Mosquitto Docs**: https://mosquitto.org/documentation/

### Tools:
- **ampy**: Upload files to ESP32 (`pip install adafruit-ampy`)
- **esptool**: Flash ESP32 (`pip install esptool`)
- **screen**: Serial terminal (`sudo apt install screen`)
- **mosquitto**: MQTT broker (`sudo apt install mosquitto`)

### Important Files to Edit:
1. `micropy/src/config.py` - Update WiFi and server IP
2. `micropy/src/main.py` - Main ESP32 logic (ready to use)
3. `server/mqtt_test_server.py` - Laptop server (ready to run)

---

## 🎯 Project Goals

### Current Phase: **Connectivity Testing**
- ✅ ESP32 connects to WiFi
- ✅ ESP32 communicates with laptop server
- ✅ MQTT messaging works bidirectionally
- ✅ Commands can control ESP32 remotely

### Next Phase: **Sensor Integration**
- Read soil moisture (4 sensors)
- Read tank level (ultrasonic)
- Read temperature & humidity
- Publish real sensor data

### Future Phase: **Actuation Control**
- Control solenoid valves
- Control irrigation pump
- Control refill pump
- Safety interlocks

### Final Phase: **Production**
- Mobile app (React Native)
- Cloud sync (Firebase/AWS)
- OTA updates
- Field deployment

---

## 📝 Notes

- **Device ID**: `imshiva2` is the test node
- **Password**: `@Namnagar29` (already configured)
- **Target**: Nepal agricultural market
- **Language**: Will support Nepali localization
- **Power**: Solar-powered for 24/7 operation
- **Ruggedness**: IP65 rated for monsoon conditions

---

## ✅ Success Checklist

Before moving to next phase, verify:
- [ ] ESP32 connects to WiFi reliably
- [ ] Laptop server receives status messages
- [ ] Can send commands from laptop to ESP32
- [ ] LED blinks on command (test_led)
- [ ] Ping/pong works
- [ ] Heartbeat messages arrive every 30s
- [ ] System recovers from WiFi disconnect
- [ ] System recovers from server restart
- [ ] No crashes after 1+ hour runtime
- [ ] Memory usage is stable

---

**Version**: 1.0  
**Date**: December 23, 2025  
**Status**: Ready for Testing ✅  
**Author**: Krishna (@krishna-ji)  
**Device**: imshiva2 (ESP32 Test Node)  

---

## 🚀 Ready to Start?

1. Read **NETWORK_ARCHITECTURE.md** (5 minutes)
2. Follow **DEPLOYMENT_GUIDE.md** (30 minutes)
3. Use **TESTING_CHECKLIST.md** (1 hour)
4. Reference **NETWORK_DIAGRAM.txt** as needed

**Let's connect imshiva2 to your laptop server! 🌱💧**
