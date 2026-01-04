# Testing Checklist - Smart Drip Irrigation System

## Pre-Flight Checklist

### Hardware Requirements
- [ ] ESP32 development board
- [ ] USB cable for ESP32
- [ ] Laptop/computer on same WiFi network
- [ ] WiFi router (2.4GHz - ESP32 compatible)
- [ ] Stable power supply for ESP32

### Software Requirements
- [ ] MicroPython installed on ESP32
- [ ] Mosquitto MQTT broker on laptop
- [ ] Python 3.7+ on laptop
- [ ] Required Python libraries (`paho-mqtt`)
- [ ] Serial terminal software (`screen` or `picocom`)

---

## Phase 1: Laptop Server Setup ✅

### Step 1.1: Network Configuration
- [ ] Laptop connected to WiFi router
- [ ] Laptop IP address identified (e.g., 192.168.1.100)
- [ ] Router gateway confirmed (usually 192.168.1.1)
- [ ] WiFi credentials available

**Commands:**
```bash
ip addr show
# Note your IP: _______________
```

### Step 1.2: Install MQTT Broker
- [ ] Mosquitto installed
- [ ] Mosquitto service enabled
- [ ] Mosquitto service started
- [ ] Mosquitto service status verified

**Commands:**
```bash
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
sudo systemctl status mosquitto
```

**Expected:** Active (running)

### Step 1.3: Test MQTT Locally
- [ ] Can subscribe to test topic
- [ ] Can publish to test topic
- [ ] Message received successfully

**Commands:**
```bash
# Terminal 1:
mosquitto_sub -h localhost -t test/topic

# Terminal 2:
mosquitto_pub -h localhost -t test/topic -m "Hello MQTT"
```

**Expected:** "Hello MQTT" appears in Terminal 1

### Step 1.4: Firewall Configuration
- [ ] MQTT port (1883) opened in firewall
- [ ] API port (5000) opened (optional for now)

**Commands:**
```bash
sudo ufw allow 1883/tcp
sudo ufw status
```

### Step 1.5: Python Environment
- [ ] Python 3 installed
- [ ] pip3 installed
- [ ] paho-mqtt library installed

**Commands:**
```bash
python3 --version
pip3 install paho-mqtt
```

---

## Phase 2: ESP32 Preparation ✅

### Step 2.1: Flash MicroPython
- [ ] MicroPython firmware downloaded
- [ ] ESP32 connected via USB
- [ ] USB port identified (`/dev/ttyUSB0`)
- [ ] Flash memory erased
- [ ] MicroPython firmware flashed
- [ ] ESP32 boots into MicroPython REPL

**Commands:**
```bash
ls /dev/ttyUSB*
# Expected: /dev/ttyUSB0 (or similar)

esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin

screen /dev/ttyUSB0 115200
# Press Ctrl+D to reboot into REPL
```

**Expected:** `>>>` prompt appears

### Step 2.2: Install MicroPython Libraries
- [ ] Connected to ESP32 REPL
- [ ] `umqtt.simple` installed
- [ ] `urequests` installed (optional)

**Commands (in MicroPython REPL):**
```python
import upip
upip.install('micropython-umqtt.simple')
```

**Expected:** "Installing..." then "Done"

### Step 2.3: Update Configuration
- [ ] `config.py` file edited
- [ ] WiFi SSID updated to match your router
- [ ] WiFi password set correctly
- [ ] MQTT_BROKER set to laptop IP
- [ ] Device ID set to "imshiva2"

**Edit:** `/home/krishna/Projects/drip-irrigation/micropy/src/config.py`

```python
WIFI_SSID = "YOUR_ROUTER_NAME"  # ← Update this
WIFI_PASSWORD = "@Namnagar29"
MQTT_BROKER = "192.168.1.100"  # ← Update with your laptop IP
```

### Step 2.4: Upload Code to ESP32
- [ ] `config.py` uploaded
- [ ] `main.py` uploaded
- [ ] Files verified on ESP32

**Commands:**
```bash
ampy --port /dev/ttyUSB0 put micropy/src/config.py
ampy --port /dev/ttyUSB0 put micropy/src/main.py
ampy --port /dev/ttyUSB0 ls
```

**Expected:** Shows `config.py` and `main.py`

---

## Phase 3: First Connection Test ✅

### Step 3.1: Start Laptop Server
- [ ] Navigated to server directory
- [ ] Python server script started
- [ ] Server shows "Waiting for devices..."

**Commands:**
```bash
cd /home/krishna/Projects/drip-irrigation/server
python3 mqtt_test_server.py
```

**Expected Output:**
```
======================================================
🌱 Smart Drip Irrigation - MQTT Test Server
======================================================
Broker: localhost:1883
Waiting for ESP32 devices to connect...
```

### Step 3.2: Connect Serial Monitor
- [ ] Opened second terminal
- [ ] Connected to ESP32 serial
- [ ] Ready to see debug output

**Commands:**
```bash
screen /dev/ttyUSB0 115200
```

### Step 3.3: Reset ESP32
- [ ] Pressed RESET button on ESP32
- [ ] Or sent Ctrl+D in REPL

**Expected:** Boot messages appear

### Step 3.4: Verify WiFi Connection
- [ ] WiFi connection attempt logged
- [ ] IP address obtained
- [ ] Signal strength (RSSI) displayed

**Expected Log:**
```
[INFO] Connecting to WiFi: your_router_ssid
[SUCCESS] WiFi connected! IP: 192.168.1.xxx
Signal strength: -45 dBm
```

**Troubleshooting:**
- If timeout → Check SSID and password
- If "not found" → Move ESP32 closer to router
- If "wrong password" → Verify password in config.py

### Step 3.5: Verify Server Ping
- [ ] ESP32 attempts to ping laptop server
- [ ] Ping succeeds
- [ ] "Server reachable" message shown

**Expected Log:**
```
[INFO] Pinging server at 192.168.1.100...
[SUCCESS] Server 192.168.1.100 is reachable!
```

**Troubleshooting:**
- If fails → Check laptop firewall
- If timeout → Verify laptop IP is correct
- Run on laptop: `ip addr show` and update config.py

### Step 3.6: Verify MQTT Connection
- [ ] ESP32 attempts MQTT connection
- [ ] Connection succeeds
- [ ] Subscribed to command topic

**Expected Log (ESP32):**
```
[INFO] Connecting to MQTT broker...
[SUCCESS] MQTT connected and subscribed!
```

**Expected Log (Laptop Server):**
```
[2025-12-23 10:30:15] Topic: irrigation/imshiva2/status
Payload: {
  "device_id": "imshiva2",
  "status": "online",
  ...
}

🆕 New device connected: imshiva2
```

**Troubleshooting:**
- If "connection refused" → Check mosquitto is running
- If timeout → Check MQTT_BROKER IP in config.py
- If auth error → Mosquitto may require username/password

---

## Phase 4: Communication Tests ✅

### Test 4.1: Status Message Reception
- [ ] Server receives online status
- [ ] Device ID is correct ("imshiva2")
- [ ] WiFi RSSI value present
- [ ] Timestamp present

**Verify:** Check laptop server output

### Test 4.2: Heartbeat Messages
- [ ] Wait 30 seconds
- [ ] Heartbeat message received
- [ ] Contains uptime and free memory
- [ ] LED blinks briefly on ESP32

**Expected (Server):**
```
Topic: irrigation/imshiva2/heartbeat
Payload: {
  "device_id": "imshiva2",
  "uptime": 123,
  "free_mem": 102400
}
```

### Test 4.3: Command - Ping
- [ ] Send ping command from laptop
- [ ] ESP32 receives command
- [ ] ESP32 responds with "pong"
- [ ] Server receives response

**Commands (in new terminal):**
```bash
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"ping"}'
```

**Expected (ESP32 log):**
```
[INFO] Received MQTT: irrigation/imshiva2/commands -> {"action":"ping"}
[INFO] Processing command: ping
```

**Expected (Server):**
```
Topic: irrigation/imshiva2/status
Payload: {
  "status": "pong",
  ...
}
```

### Test 4.4: Command - LED Blink
- [ ] Send LED test command
- [ ] ESP32 receives command
- [ ] Built-in LED blinks specified times
- [ ] Visual confirmation

**Commands:**
```bash
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"test_led","times":5}'
```

**Expected:** LED on ESP32 blinks 5 times

### Test 4.5: Command - Status Request
- [ ] Send status request
- [ ] ESP32 receives command
- [ ] Full telemetry published
- [ ] Server receives complete data

**Commands:**
```bash
mosquitto_pub -h localhost -t "irrigation/imshiva2/commands" -m '{"action":"status"}'
```

**Expected (Server):**
```
Topic: irrigation/imshiva2/telemetry
Payload: {
  "status": "running",
  "uptime": 456,
  "free_memory": 102400,
  "wifi_rssi": -45,
  "sensors": {
    "soil_moisture": [45, 52, 48, 50],
    "tank_level": 75,
    ...
  }
}
```

### Test 4.6: Sensor Data Publishing
- [ ] Wait 60 seconds (sensor read interval)
- [ ] ESP32 publishes sensor data
- [ ] Server receives sensor data
- [ ] All sensor values present

**Expected (Server):**
```
Topic: irrigation/imshiva2/sensors
Payload: {
  "device_id": "imshiva2",
  "sensors": {
    "soil_moisture": [...],
    "tank_level": 75,
    "temperature": 25.5,
    "humidity": 65
  }
}
```

---

## Phase 5: Reliability Tests 🔄

### Test 5.1: WiFi Reconnection
- [ ] Manually disconnect ESP32 from WiFi
- [ ] Wait 5 seconds
- [ ] ESP32 automatically reconnects
- [ ] MQTT reconnects
- [ ] Status published again

**How to test:**
```bash
# On router admin panel, block ESP32 MAC temporarily
# OR disable WiFi on router briefly
```

**Expected:** ESP32 logs show reconnection attempt and success

### Test 5.2: MQTT Reconnection
- [ ] Restart Mosquitto on laptop
- [ ] ESP32 detects disconnect
- [ ] Automatic reconnection attempt
- [ ] Connection restored
- [ ] Messages resume

**Commands (laptop):**
```bash
sudo systemctl restart mosquitto
```

**Expected:** ESP32 reconnects within ~5-10 seconds

### Test 5.3: Server Offline (Offline Mode)
- [ ] Stop laptop server script (Ctrl+C)
- [ ] ESP32 continues running
- [ ] Local sensor reading continues
- [ ] No crash or freeze
- [ ] Restart server
- [ ] ESP32 reconnects

**Expected:** System remains stable without server

### Test 5.4: Long-Running Stability
- [ ] Leave system running for 1+ hour
- [ ] Monitor for crashes
- [ ] Check memory leaks (free_mem decreasing?)
- [ ] Verify consistent heartbeats
- [ ] No disconnections

**Monitor:**
```bash
# On laptop, watch all traffic:
mosquitto_sub -h localhost -t "irrigation/#" -v
```

### Test 5.5: Power Cycle
- [ ] Disconnect ESP32 power
- [ ] Wait 10 seconds
- [ ] Reconnect power
- [ ] ESP32 boots automatically
- [ ] WiFi connects
- [ ] MQTT connects
- [ ] System operational

**Expected:** Full boot sequence completes successfully

---

## Phase 6: Network Diagnostics 🔍

### Diagnostic 6.1: WiFi Signal Strength
- [ ] Check RSSI value in status messages
- [ ] Optimal: -30 to -67 dBm (excellent to good)
- [ ] Acceptable: -68 to -80 dBm (fair)
- [ ] Poor: below -80 dBm

**Value:** _______ dBm

### Diagnostic 6.2: Message Latency
- [ ] Send ping command
- [ ] Note time sent
- [ ] Note time of pong received
- [ ] Calculate round-trip time

**Latency:** _______ ms (should be < 500ms)

### Diagnostic 6.3: Memory Usage
- [ ] Check `free_mem` in heartbeat
- [ ] Note initial value: _______ bytes
- [ ] Wait 10 minutes
- [ ] Check again: _______ bytes
- [ ] Memory should be stable (±10KB)

### Diagnostic 6.4: Packet Loss
- [ ] Send 10 ping commands rapidly
- [ ] Count responses received
- [ ] Packet loss = (10 - responses) / 10 * 100%

**Results:** _____ / 10 received (___% loss)
**Acceptable:** < 5% loss

### Diagnostic 6.5: Network Scan
- [ ] Verify ESP32 can see router
- [ ] Check channel congestion

**Commands (MicroPython REPL on ESP32):**
```python
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
networks = wlan.scan()
for net in networks:
    print(net)
```

---

## Phase 7: Final Integration Tests 🎯

### Integration 7.1: Multi-Device Test
- [ ] Add second ESP32 (optional)
- [ ] Both devices connect simultaneously
- [ ] No interference between devices
- [ ] Server tracks both separately
- [ ] Commands route correctly

### Integration 7.2: Command Variety
Test all planned commands:
- [ ] `ping` → pong response
- [ ] `status` → full telemetry
- [ ] `test_led` → LED blinks
- [ ] `irrigate` → (future, placeholder)
- [ ] `stop` → (future, placeholder)

### Integration 7.3: Load Test
- [ ] Send 100 commands rapidly
- [ ] Monitor ESP32 responsiveness
- [ ] Check for message queue overflow
- [ ] Verify all commands processed

### Integration 7.4: 24-Hour Burn-In
- [ ] System runs continuously for 24 hours
- [ ] No manual intervention
- [ ] Monitor logs for errors
- [ ] Check uptime value
- [ ] Verify stable memory usage

**Start time:** _______________
**End time:** _______________
**Total uptime:** _______ hours
**Errors encountered:** _______

---

## Common Issues & Solutions 🔧

### Issue: "WiFi connection timeout"
**Causes:**
- Incorrect SSID or password
- ESP32 too far from router
- Router on 5GHz (ESP32 needs 2.4GHz)

**Solutions:**
- Double-check credentials in config.py
- Move ESP32 closer to router
- Verify router has 2.4GHz enabled

### Issue: "Cannot reach server"
**Causes:**
- Laptop firewall blocking port 1883
- Incorrect IP address in config
- Laptop IP changed (DHCP)

**Solutions:**
- `sudo ufw allow 1883/tcp`
- Verify laptop IP: `ip addr show`
- Set static IP on laptop

### Issue: "MQTT connection failed"
**Causes:**
- Mosquitto not running
- Port 1883 in use by another service
- Authentication required but not configured

**Solutions:**
- `sudo systemctl start mosquitto`
- `netstat -tuln | grep 1883`
- Add username/password to config

### Issue: "ESP32 crashes/reboots"
**Causes:**
- Memory leak
- Power supply insufficient
- Code error in callback

**Solutions:**
- Add `gc.collect()` in main loop
- Use better USB cable / power supply
- Check for exceptions in logs

### Issue: "Messages not received"
**Causes:**
- Topic mismatch
- QoS level issues
- Network congestion

**Solutions:**
- Verify topic strings match exactly
- Use `mosquitto_sub -t "#"` to see all
- Check WiFi signal strength

---

## Success Criteria ✅

All tests passed if:
- ✅ ESP32 connects to WiFi reliably
- ✅ ESP32 pings laptop server successfully
- ✅ MQTT connection establishes
- ✅ Commands sent from laptop are executed
- ✅ Sensor data is received by server
- ✅ System reconnects after disconnections
- ✅ No memory leaks after 1+ hour
- ✅ LED blinks on command
- ✅ Heartbeat messages arrive every 30 seconds
- ✅ No crashes or unexpected reboots

---

## Next Steps After Testing 🚀

Once basic connectivity is verified:

1. **Implement Real Sensors**
   - Replace simulated data with actual ADC readings
   - Calibrate soil moisture sensors
   - Add ultrasonic sensor for tank level

2. **Add Actuator Control**
   - Implement valve control (relay/MOSFET)
   - Add pump control logic
   - Safety interlocks (max duration, cooldown)

3. **Develop Mobile App**
   - React Native frontend
   - Real-time dashboard
   - Schedule configuration UI

4. **Cloud Integration**
   - Firebase/AWS IoT setup
   - Historical data storage
   - Remote access from anywhere

5. **Field Testing**
   - Deploy on pilot farm
   - 24-hour+ outdoor testing
   - Weatherproofing verification

---

**Testing Date:** ______________
**Tester:** ______________
**Result:** PASS / FAIL
**Notes:**
_______________________________________________
_______________________________________________
_______________________________________________
