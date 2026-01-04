"""
Simple MQTT Test Server for Smart Drip Irrigation
Run this on your laptop (192.168.1.100)
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# Configuration
MQTT_BROKER = "localhost"  # This server will run locally
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

# Store connected devices
connected_devices = {}

def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    print(f"[{datetime.now()}] Connected to MQTT broker with result code {rc}")
    
    # Subscribe to all irrigation topics
    client.subscribe("irrigation/#")
    print("Subscribed to: irrigation/#")

def on_message(client, userdata, msg):
    """Callback when message is received"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    topic = msg.topic
    
    try:
        # Try to parse as JSON
        payload = json.loads(msg.payload.decode())
        print(f"\n[{timestamp}] Topic: {topic}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Update device registry
        if 'device_id' in payload:
            device_id = payload['device_id']
            if device_id not in connected_devices:
                print(f"🆕 New device connected: {device_id}")
            
            connected_devices[device_id] = {
                'last_seen': time.time(),
                'status': payload.get('status', 'unknown')
            }
        
    except json.JSONDecodeError:
        # Not JSON, just print raw
        print(f"\n[{timestamp}] Topic: {topic}")
        print(f"Payload: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    """Callback when disconnected"""
    print(f"[{datetime.now()}] Disconnected with result code {rc}")
    if rc != 0:
        print("Unexpected disconnection. Attempting to reconnect...")

def send_test_command(client, device_id, action):
    """Send a test command to a device"""
    topic = f"irrigation/{device_id}/commands"
    command = {
        "action": action,
        "timestamp": time.time()
    }
    
    client.publish(topic, json.dumps(command))
    print(f"\n✉️  Sent command '{action}' to {device_id}")

def main():
    """Main server loop"""
    print("=" * 60)
    print("🌱 Smart Drip Irrigation - MQTT Test Server")
    print("=" * 60)
    print(f"Starting at: {datetime.now()}")
    print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print("\nWaiting for ESP32 devices to connect...")
    print("Press Ctrl+C to exit\n")
    
    # Create MQTT client
    client = mqtt.Client(client_id="laptop_server")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Connect to broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    except Exception as e:
        print(f"❌ Error connecting to MQTT broker: {e}")
        print("\nMake sure Mosquitto is installed and running:")
        print("  sudo apt install mosquitto mosquitto-clients")
        print("  sudo systemctl start mosquitto")
        return
    
    # Start network loop in background
    client.loop_start()
    
    # Main loop
    try:
        last_status_time = time.time()
        
        while True:
            time.sleep(1)
            
            # Print status every 30 seconds
            if time.time() - last_status_time > 30:
                print(f"\n--- Status Update [{datetime.now().strftime('%H:%M:%S')}] ---")
                if connected_devices:
                    for device_id, info in connected_devices.items():
                        age = time.time() - info['last_seen']
                        status = "🟢 ACTIVE" if age < 60 else "🔴 STALE"
                        print(f"  {status} {device_id}: {info['status']} (seen {int(age)}s ago)")
                else:
                    print("  No devices connected yet")
                print("-" * 40)
                last_status_time = time.time()
            
            # Optional: Send periodic test commands
            # Uncomment to test:
            # if time.time() % 60 < 1 and connected_devices:
            #     device_id = list(connected_devices.keys())[0]
            #     send_test_command(client, device_id, "status")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        client.loop_stop()
        client.disconnect()
        print("Goodbye!")

if __name__ == "__main__":
    main()
