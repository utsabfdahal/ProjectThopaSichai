# Smart Drip Irrigation - Deployment Guide

## 🎯 Quick Start: Connect ESP32 to Laptop Server

### Prerequisites
- ESP32 with MicroPython installed
- Laptop on same Wi-Fi network as ESP32
- Python 3.7+ on laptop
- Mosquitto MQTT broker

---

## 📋 Step-by-Step Setup

### 1. Setup Laptop Server (192.168.1.100)

#### A. Find Your Laptop's IP Address
```bash
# On Linux:
ip addr show | grep inet

# Note your IP address (e.g., 192.168.1.100)
```

#### B. Install MQTT Broker (Mosquitto)
```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients python3-pip -y

# Start mosquitto service
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Verify it's running
sudo systemctl status mosquitto
```

#### C. Install Python Dependencies
```bash
cd /home/krishna/Projects/drip-irrigation/server
pip3 install paho-mqtt
```

#### D. Test MQTT Broker
```bash
# Terminal 1 - Subscribe to test topic
mosquitto_sub -h localhost -t test/topic

# Terminal 2 - Publish a test message
mosquitto_pub -h localhost -t test/topic -m "Hello MQTT"

# You should see "Hello MQTT" in Terminal 1
```

---

### 2. Configure ESP32 (imshiva2)

#### A. Update Configuration File
Edit `/home/krishna/Projects/drip-irrigation/micropy/src/config.py`:

```python
# Update these values:
WIFI_SSID = "YOUR_ACTUAL_WIFI_NAME"  # Your router's SSID
WIFI_PASSWORD = "@Namnagar29"
MQTT_BROKER = "192.168.1.100"  # Your laptop's IP
```

#### B. Flash MicroPython (if not done already)
```bash
# Install esptool
pip3 install esptool

# Download MicroPython firmware for ESP32
wget https://micropython.org/resources/firmware/esp32-20231005-v1.21.0.bin

# Erase flash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash

# Flash MicroPython
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20231005-v1.21.0.bin
```

#### C. Install Required MicroPython Libraries
```bash
# Connect to ESP32
screen /dev/ttyUSB0 115200
# or
picocom /dev/ttyUSB0 -b 115200

# In MicroPython REPL:
>>> import upip
>>> upip.install('micropython-umqtt.simple')
>>> upip.install('micropython-urequests')
```

#### D. Upload Code to ESP32
```bash
# Using ampy tool
pip3 install adafruit-ampy

# Upload config
ampy --port /dev/ttyUSB0 put /home/krishna/Projects/drip-irrigation/micropy/src/config.py

# Upload main.py
ampy --port /dev/ttyUSB0 put /home/krishna/Projects/drip-irrigation/micropy/src/main.py

# Verify files
ampy --port /dev/ttyUSB0 ls
```

**OR** Use the micropy tool from your project:
```bash
cd /home/krishna/Projects/drip-irrigation/micropy
python3 -m micropy.scripts deploy --port /dev/ttyUSB0
```

---

### 3. Run the System

#### Terminal 1: Start Laptop Server
```bash
cd /home/krishna/Projects/drip-irrigation/server
python3 mqtt_test_server.py
```

You should see:
```
======================================================
🌱 Smart Drip Irrigation - MQTT Test Server
======================================================
Starting at: 2025-12-23 10:30:00
Broker: localhost:1883

Waiting for ESP32 devices to connect...
```

#### Terminal 2: Monitor ESP32 Serial Output
```bash
screen /dev/ttyUSB0 115200
```

Press the **RESET** button on ESP32. You should see:
```
==================================================
Smart Drip Irrigation System Starting...
Device ID: imshiva2
Target Server: 192.168.1.100
==================================================
[1234567890] [INFO] Connecting to WiFi: your_router_ssid
[1234567891] [SUCCESS] WiFi connected! IP: 192.168.1.200
[1234567892] [INFO] Pinging server at 192.168.1.100...
[1234567893] [SUCCESS] Server 192.168.1.100 is reachable!
[1234567894] [INFO] Connecting to MQTT broker...
[1234567895] [SUCCESS] MQTT connected and subscribed!
```

#### Terminal 3: Manual MQTT Testing (Optional)
```bash
# Subscribe to all irrigation topics
mosquitto_sub -h localhost -t "irrigation/#" -v

# Publish a test command
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"ping"}'

# You should see the ESP32 respond with "pong"
```

---

## 🧪 Testing & Verification

### Test 1: Connectivity Test
On laptop server terminal, you should see:
```
[2025-12-23 10:30:15] Topic: irrigation/imshiva2/status
Payload: {
  "device_id": "imshiva2",
  "status": "online",
  "timestamp": 1234567890,
  "wifi_rssi": -45
}

🆕 New device connected: imshiva2
```

### Test 2: Ping Command
```bash
# Send command from laptop
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"ping"}'

# ESP32 should respond with:
# Topic: irrigation/imshiva2/status -> "pong"
```

### Test 3: LED Test
```bash
# Blink ESP32 LED 5 times
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"test_led","times":5}'

# Watch the built-in LED blink on your ESP32!
```

### Test 4: Status Request
```bash
# Request full status
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"status"}'

# Server should receive full telemetry data
```

---

## 📊 Expected Data Flow

```
ESP32 (imshiva2)                    Laptop Server
================                    =============
     |                                    |
     |-- WiFi Connect ------------------> Router
     |                                    |
     |-- Ping 192.168.1.100 ------------>|
     |                                    |
     |<---- TCP ACK ---------------------|
     |                                    |
     |-- MQTT Connect ------------------->| (port 1883)
     |<---- CONNACK ----------------------|
     |                                    |
     |-- Publish: status="online" ------>|
     |                                    |
     |-- Subscribe: commands ------------>|
     |                                    |
     |<---- Command: "status" ------------|
     |                                    |
     |-- Publish: telemetry data ------->|
     |                                    |
     |-- Heartbeat (every 30s) --------->|
     |                                    |
```

---

## 🐛 Troubleshooting

### Issue 1: ESP32 Can't Connect to WiFi
```bash
# Check SSID and password in config.py
# Verify router is on 2.4GHz (ESP32 doesn't support 5GHz)
# Check signal strength - move ESP32 closer to router
```

### Issue 2: Can't Reach Laptop Server
```bash
# On laptop, check firewall:
sudo ufw status
sudo ufw allow 1883/tcp  # Allow MQTT port

# Verify laptop IP hasn't changed:
ip addr show

# Update config.py on ESP32 if needed
```

### Issue 3: MQTT Connection Fails
```bash
# Check if mosquitto is running:
sudo systemctl status mosquitto

# Check mosquitto logs:
sudo tail -f /var/log/mosquitto/mosquitto.log

# Restart mosquitto:
sudo systemctl restart mosquitto
```

### Issue 4: No Output from ESP32
```bash
# Check USB connection:
ls /dev/ttyUSB*  # Should show /dev/ttyUSB0

# Check serial connection:
screen /dev/ttyUSB0 115200

# Press Ctrl+D to soft-reboot ESP32 in REPL
```

---

## 🔧 Advanced Configuration

### Static IP for Laptop
Edit `/etc/netplan/01-network-manager-all.yaml`:
```yaml
network:
  version: 2
  ethernets:
    eth0:  # Or your interface name
      dhcp4: no
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

Apply:
```bash
sudo netplan apply
```

### MQTT Authentication (Optional)
```bash
# Create password file
sudo mosquitto_passwd -c /etc/mosquitto/passwd admin

# Edit /etc/mosquitto/mosquitto.conf
allow_anonymous false
password_file /etc/mosquitto/passwd

# Restart mosquitto
sudo systemctl restart mosquitto

# Update config.py on ESP32:
MQTT_USERNAME = "admin"
MQTT_PASSWORD = "your_password"
```

---

## 📈 Next Steps

1. ✅ **Verify basic connectivity** (this guide)
2. 🔄 **Add sensor reading** (soil moisture, tank level)
3. 🚰 **Implement pump control**
4. 📱 **Build mobile app interface**
5. ☁️ **Add cloud sync** (Firebase/AWS)
6. 🌾 **Field testing** on pilot farm

---

## 📞 Quick Reference

### Important IPs
- **Router**: 192.168.1.1
- **Laptop Server**: 192.168.1.100
- **ESP32 (imshiva2)**: Auto-assigned by DHCP (typically 192.168.1.200+)

### Key Ports
- **MQTT**: 1883
- **HTTP API**: 5000 (future)
- **WebSocket**: 8080 (future)

### Useful Commands
```bash
# See laptop IP
ip addr show | grep inet

# Monitor MQTT traffic
mosquitto_sub -h localhost -t "#" -v

# Test MQTT locally
mosquitto_pub -h localhost -t test -m "hello"

# ESP32 serial connection
screen /dev/ttyUSB0 115200

# Check mosquitto status
sudo systemctl status mosquitto

# Restart mosquitto
sudo systemctl restart mosquitto
```

---

**Last Updated**: December 23, 2025  
**Status**: Ready for Testing ✅
