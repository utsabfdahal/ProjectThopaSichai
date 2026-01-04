"""
Smart Drip Irrigation System - ESP32 Main Controller
Device: imshiva2 (Test Node)
Purpose: Connect to router, communicate with laptop server, control irrigation
"""

import machine
import network
import time
import ujson
import gc
from umqtt.simple import MQTTClient
import config

# Initialize LED for status indication
led = machine.Pin(config.LED_PIN, machine.Pin.OUT)

# Global state
wifi_connected = False
mqtt_connected = False
last_sensor_read = 0
last_mqtt_publish = 0
last_heartbeat = 0
system_state = {
    "status": "initializing",
    "wifi_rssi": 0,
    "uptime": 0,
    "free_memory": 0,
    "sensors": {},
    "actuators": {}
}

def blink_led(times=3, delay=0.2):
    """Blink LED for visual feedback"""
    for _ in range(times):
        led.value(1)
        time.sleep(delay)
        led.value(0)
        time.sleep(delay)

def log(message, level="INFO"):
    """Simple logging function"""
    if config.DEBUG_MODE:
        timestamp = time.time()
        print(f"[{timestamp}] [{level}] {message}")

def connect_wifi():
    """Connect to WiFi network"""
    global wifi_connected
    
    log(f"Connecting to WiFi: {config.WIFI_SSID}")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        
        # Wait for connection with timeout
        start_time = time.time()
        while not wlan.isconnected():
            if time.time() - start_time > config.WIFI_CONNECT_TIMEOUT:
                log("WiFi connection timeout!", "ERROR")
                wifi_connected = False
                return False
            
            blink_led(1, 0.1)  # Fast blink while connecting
            time.sleep(1)
    
    # Connection successful
    wifi_connected = True
    ifconfig = wlan.ifconfig()
    log(f"WiFi connected! IP: {ifconfig[0]}", "SUCCESS")
    log(f"Gateway: {ifconfig[2]}, DNS: {ifconfig[3]}")
    
    # Get signal strength
    system_state["wifi_rssi"] = wlan.status('rssi')
    log(f"Signal strength: {system_state['wifi_rssi']} dBm")
    
    blink_led(5, 0.1)  # Celebrate connection!
    return True

def ping_server():
    """Ping the laptop server to verify connectivity"""
    import socket
    
    try:
        log(f"Pinging server at {config.SERVER_IP}...")
        addr_info = socket.getaddrinfo(config.SERVER_IP, config.MQTT_PORT)
        addr = addr_info[0][-1]
        
        s = socket.socket()
        s.settimeout(2)
        s.connect(addr)
        s.close()
        
        log(f"Server {config.SERVER_IP} is reachable!", "SUCCESS")
        return True
    except Exception as e:
        log(f"Cannot reach server: {e}", "ERROR")
        return False

def mqtt_callback(topic, msg):
    """Handle incoming MQTT messages"""
    try:
        topic_str = topic.decode('utf-8')
        msg_str = msg.decode('utf-8')
        log(f"Received MQTT: {topic_str} -> {msg_str}")
        
        # Handle commands
        if topic_str.endswith('/commands'):
            handle_command(msg_str)
        
    except Exception as e:
        log(f"MQTT callback error: {e}", "ERROR")

def handle_command(cmd_json):
    """Process incoming commands from server"""
    try:
        cmd = ujson.loads(cmd_json)
        action = cmd.get('action')
        
        log(f"Processing command: {action}")
        
        if action == 'ping':
            publish_status("pong")
        elif action == 'status':
            publish_full_status()
        elif action == 'test_led':
            blink_led(int(cmd.get('times', 3)))
        # Add more command handlers as needed
        
    except Exception as e:
        log(f"Command handling error: {e}", "ERROR")

def connect_mqtt():
    """Connect to MQTT broker on laptop server"""
    global mqtt_connected
    
    try:
        log(f"Connecting to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")
        
        client = MQTTClient(
            config.MQTT_CLIENT_ID,
            config.MQTT_BROKER,
            port=config.MQTT_PORT,
            user=config.MQTT_USERNAME,
            password=config.MQTT_PASSWORD,
            keepalive=config.MQTT_KEEPALIVE
        )
        
        # Set callback for incoming messages
        client.set_callback(mqtt_callback)
        
        # Connect to broker
        client.connect()
        
        # Subscribe to command topic
        client.subscribe(config.TOPIC_COMMANDS)
        
        mqtt_connected = True
        log("MQTT connected and subscribed!", "SUCCESS")
        
        # Announce presence
        publish_status("online")
        
        blink_led(3, 0.3)
        return client
        
    except Exception as e:
        log(f"MQTT connection failed: {e}", "ERROR")
        mqtt_connected = False
        return None

def publish_status(status):
    """Publish status message to MQTT"""
    global mqtt_client
    
    if not mqtt_connected or mqtt_client is None:
        return False
    
    try:
        payload = ujson.dumps({
            "device_id": config.DEVICE_ID,
            "status": status,
            "timestamp": time.time(),
            "wifi_rssi": system_state["wifi_rssi"]
        })
        
        mqtt_client.publish(config.TOPIC_STATUS, payload)
        log(f"Published status: {status}")
        return True
        
    except Exception as e:
        log(f"Status publish error: {e}", "ERROR")
        return False

def publish_heartbeat():
    """Send periodic heartbeat to confirm device is alive"""
    global mqtt_client, last_heartbeat
    
    current_time = time.time()
    if current_time - last_heartbeat < config.HEARTBEAT_INTERVAL:
        return
    
    if not mqtt_connected or mqtt_client is None:
        return
    
    try:
        payload = ujson.dumps({
            "device_id": config.DEVICE_ID,
            "uptime": time.time(),
            "free_mem": gc.mem_free(),
            "timestamp": current_time
        })
        
        mqtt_client.publish(config.TOPIC_HEARTBEAT, payload)
        log("Heartbeat sent")
        last_heartbeat = current_time
        
        # Quick LED flash to show activity
        led.value(1)
        time.sleep(0.05)
        led.value(0)
        
    except Exception as e:
        log(f"Heartbeat error: {e}", "ERROR")

def publish_full_status():
    """Publish complete system status"""
    global mqtt_client
    
    if not mqtt_connected or mqtt_client is None:
        return
    
    try:
        system_state["uptime"] = time.time()
        system_state["free_memory"] = gc.mem_free()
        
        payload = ujson.dumps(system_state)
        mqtt_client.publish(config.TOPIC_TELEMETRY, payload)
        log("Full status published")
        
    except Exception as e:
        log(f"Full status publish error: {e}", "ERROR")

def read_sensors():
    """Read all sensor values (placeholder for now)"""
    global last_sensor_read
    
    current_time = time.time()
    if current_time - last_sensor_read < config.SENSOR_READ_INTERVAL:
        return
    
    # TODO: Implement actual sensor reading
    # For now, just update timestamp
    log("Reading sensors...")
    
    # Simulated sensor data
    system_state["sensors"] = {
        "soil_moisture": [45, 52, 48, 50],  # 4 zones
        "tank_level": 75,  # percentage
        "temperature": 25.5,  # Celsius
        "humidity": 65  # percentage
    }
    
    last_sensor_read = current_time
    log(f"Sensors read: {system_state['sensors']}")

def check_mqtt_messages():
    """Non-blocking check for incoming MQTT messages"""
    global mqtt_client
    
    if mqtt_connected and mqtt_client is not None:
        try:
            mqtt_client.check_msg()
        except Exception as e:
            log(f"MQTT check error: {e}", "ERROR")

def reconnect_if_needed():
    """Check connections and reconnect if necessary"""
    global wifi_connected, mqtt_connected, mqtt_client
    
    # Check WiFi
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        log("WiFi disconnected, reconnecting...", "WARNING")
        wifi_connected = False
        mqtt_connected = False
        connect_wifi()
    
    # Check MQTT
    if wifi_connected and not mqtt_connected:
        log("MQTT disconnected, reconnecting...", "WARNING")
        mqtt_client = connect_mqtt()

def main():
    """Main control loop"""
    global mqtt_client, system_state
    
    log("=" * 50)
    log("Smart Drip Irrigation System Starting...")
    log(f"Device ID: {config.DEVICE_ID}")
    log(f"Target Server: {config.SERVER_IP}")
    log("=" * 50)
    
    # Initialize connections
    if connect_wifi():
        # Test server connectivity
        if ping_server():
            log("Initial ping successful!", "SUCCESS")
        
        # Connect to MQTT
        mqtt_client = connect_mqtt()
    
    system_state["status"] = "running"
    
    # Main loop
    log("Entering main control loop...")
    loop_count = 0
    
    while True:
        try:
            loop_count += 1
            
            # Periodic LED blink to show we're alive
            if loop_count % 10 == 0:
                led.value(1)
                time.sleep(0.05)
                led.value(0)
            
            # Check and maintain connections
            reconnect_if_needed()
            
            # Read sensors
            read_sensors()
            
            # Send heartbeat
            publish_heartbeat()
            
            # Check for incoming MQTT commands
            check_mqtt_messages()
            
            # Garbage collection to prevent memory leaks
            if loop_count % 100 == 0:
                gc.collect()
                log(f"Memory cleanup - Free: {gc.mem_free()} bytes")
            
            # Small delay to prevent CPU overload
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            log("User interrupted, shutting down...", "WARNING")
            if mqtt_connected:
                publish_status("offline")
            break
            
        except Exception as e:
            log(f"Main loop error: {e}", "ERROR")
            time.sleep(5)  # Wait before retrying

# Entry point
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Fatal error: {e}", "CRITICAL")
        # Flash LED rapidly to indicate error
        for _ in range(20):
            led.value(not led.value())
            time.sleep(0.1) 
