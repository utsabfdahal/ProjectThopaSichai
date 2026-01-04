import network
import espnow
import time
import json
from machine import ADC, Pin

# ---------------- CONFIG ----------------
NODE_ID = "001"
DEVICE_NAME = "Kullo1"
SENSOR_PIN = 34
READ_INTERVAL = 5000 

# !!! UPDATE THESE TWO LINES FROM GATEWAY OUTPUT !!!
GATEWAY_MAC = b'\xcc\x50\xe3\x93\x0f\x58'  # Example: b'\x24\x6f...'
WIFI_CHANNEL = 3  # MUST match the Gateway's channel
# ----------------------------------------

# Setup WLAN
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(dhcp_hostname=DEVICE_NAME)

# Set the channel to match Gateway
sta.config(channel=WIFI_CHANNEL)
sta.disconnect() # Ensure we are not connected to any AP

print(f"Node started on Channel {WIFI_CHANNEL}")

# Setup ESP-NOW
e = espnow.ESPNow()
e.active(True)
try:
    e.add_peer(GATEWAY_MAC)
except OSError:
    print("Peer already exists or invalid MAC")

# Setup Sensor
adc = ADC(Pin(SENSOR_PIN))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

def read_humidity():
    raw = adc.read()
    # Map 0-4095 to 0-100%
    return round((raw / 4095.0) * 100, 2)

def send_data(val):
    payload = {
        "nodeid": NODE_ID,
        "value": val
    }
    msg = json.dumps(payload)
    
    try:
        e.send(GATEWAY_MAC, msg)
        print(f"Sent: {msg}")
    except OSError as err:
        if err.args[0] == 116: # ESP_ERR_ESPNOW_NOT_FOUND
            print("Error: Gateway not found (Check Channel/MAC)")
        else:
            print("Send Error:", err)

while True:
    hum = read_humidity()
    send_data(hum)
    time.sleep_ms(READ_INTERVAL)

