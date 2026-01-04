# Configuration File for Smart Drip Irrigation ESP32
# Device: Smart Kisan Test Node

# Network Configuration
WIFI_SSID = "imshiva2"  # Your WiFi router SSID
WIFI_PASSWORD = "@Namnagar29"

# MQTT Broker Configuration
MQTT_BROKER = "192.168.1.100"  # Your laptop server IP (update this!)
MQTT_PORT = 1883
MQTT_CLIENT_ID = "smartkisan_test"  # Unique device ID
MQTT_USERNAME = None  # Set if broker requires auth
MQTT_PASSWORD = None

# Device Configuration
DEVICE_ID = "smartkisan_test"  # Change to: smartkisan_zone1, smartkisan_zone2, etc. for production
DEVICE_TYPE = "test_node"  # or "zone_controller"
ZONE_NUMBER = 0  # 0 for test node, 1-4 for field zones

# MQTT Topics (automatically generated from DEVICE_ID)
TOPIC_STATUS = f"irrigation/{DEVICE_ID}/status"
TOPIC_SENSORS = f"irrigation/{DEVICE_ID}/sensors"
TOPIC_COMMANDS = f"irrigation/{DEVICE_ID}/commands"
TOPIC_TELEMETRY = f"irrigation/{DEVICE_ID}/telemetry"
TOPIC_HEARTBEAT = f"irrigation/{DEVICE_ID}/heartbeat"

# Server Endpoints (HTTP fallback)
SERVER_IP = "192.168.1.100"
SERVER_PORT = 5000
API_BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}/api"

# Pin Configuration (Adjust based on your ESP32 board)
# GPIO pins
LED_PIN = 2  # Built-in LED for status indication

# Sensor Pins (example configuration)
SOIL_MOISTURE_PINS = [32, 33, 34, 35]  # ADC pins for 4 sensors
TANK_LEVEL_ECHO = 25
TANK_LEVEL_TRIG = 26
FLOW_SENSOR_PIN = 27
TEMP_HUMIDITY_PIN = 14  # DHT22 data pin

# Actuator Pins
VALVE_PINS = [16, 17, 18, 19]  # 4 solenoid valves
PUMP_IRRIGATION_PIN = 21
PUMP_REFILL_PIN = 22

# Timing Configuration (seconds)
SENSOR_READ_INTERVAL = 60  # Read sensors every 60 seconds
MQTT_PUBLISH_INTERVAL = 120  # Publish to MQTT every 2 minutes
HEARTBEAT_INTERVAL = 30  # Send heartbeat every 30 seconds
RECONNECT_DELAY = 5  # Wait 5 seconds before WiFi reconnect
MQTT_KEEPALIVE = 60  # MQTT keepalive in seconds

# Soil Moisture Thresholds (adjust based on calibration)
SOIL_MOISTURE_DRY = 30  # Below this = dry (start irrigation)
SOIL_MOISTURE_WET = 70  # Above this = wet (stop irrigation)

# Tank Level Thresholds (percentage)
TANK_LEVEL_LOW = 20  # Start refill
TANK_LEVEL_HIGH = 90  # Stop refill
TANK_LEVEL_CRITICAL = 10  # Emergency alert

# Safety Settings
MAX_IRRIGATION_DURATION = 3600  # Max 1 hour continuous irrigation
MAX_REFILL_DURATION = 7200  # Max 2 hours continuous refill
PUMP_COOLDOWN_TIME = 300  # 5 minutes between pump cycles

# Power Management
LOW_BATTERY_THRESHOLD = 11.0  # Volts (for 12V system)
DEEP_SLEEP_ENABLED = False  # Enable for extreme power saving
DEEP_SLEEP_DURATION = 600  # Sleep 10 minutes if enabled

# Debug Settings
DEBUG_MODE = True  # Enable verbose logging
LOG_TO_SD = False  # Log to SD card (if available)

# Offline Mode Configuration
OFFLINE_AUTO_IRRIGATION = True  # Run autonomously if WiFi/MQTT down
OFFLINE_SCHEDULE = [
    # (hour, minute, duration_minutes, zones)
    (6, 0, 30, [0, 1, 2, 3]),  # 6 AM - 30 min all zones
    (18, 0, 20, [0, 1, 2, 3])  # 6 PM - 20 min all zones
]

# Network Timeout Settings
WIFI_CONNECT_TIMEOUT = 30  # Seconds to wait for WiFi connection
MQTT_CONNECT_TIMEOUT = 10  # Seconds to wait for MQTT connection
HTTP_TIMEOUT = 5  # Seconds for HTTP requests
