import network
import espnow
import urequests
import json
import time
import ubinascii
from machine import Pin, time_pulse_us

# ---------------- CONFIG ----------------
WIFI_SSID = "x"
WIFI_PASS = "duckduckduck"

SERVER_HOST = "192.168.16.112"
SERVER_PORT = 8000
DJANGO_URL = "http://{}:{}/api/data/receive/".format(SERVER_HOST, SERVER_PORT)

# Ultrasonic config
ULTRASONIC_NODE_ID = "us01"
ULTRASONIC_INTERVAL_MS = 3000

# Ultrasonic 1 pins
TRIG1_PIN = 5
ECHO1_PIN = 18

# Ultrasonic 2 pins
TRIG2_PIN = 19
ECHO2_PIN = 21
# ----------------------------------------

# ---------- WiFi Setup ----------
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(dhcp_hostname="Gateway")
sta.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not sta.isconnected():
    time.sleep(1)

try:
    sta.config(pm=0xa11140)
except:
    pass

print("IP Address:", sta.ifconfig()[0])
mac_bytes = sta.config("mac")
print("Gateway MAC:", ubinascii.hexlify(mac_bytes, b":").decode())
print("===========================\n")

# ---------- ESP-NOW Setup ----------
e = espnow.ESPNow()
e.active(True)

# ---------- Ultrasonic Setup ----------
trig1 = Pin(TRIG1_PIN, Pin.OUT, pull=None)
echo1 = Pin(ECHO1_PIN, Pin.IN, pull=None)

trig2 = Pin(TRIG2_PIN, Pin.OUT, pull=None)
echo2 = Pin(ECHO2_PIN, Pin.IN, pull=None)

trig1.value(0)
trig2.value(0)

def read_ultrasonic_cm(trig, echo):
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    try:
        duration = time_pulse_us(echo, 1, 30000)
    except OSError:
        print('la muji')
        return None

    if duration <= 0:
        print('barbad muji')
        return None

    return round((duration * 0.0343) / 2, 2)

def forward_to_django(payload):
    try:
        headers = {"Content-Type": "application/json"}
        r = urequests.post(
            DJANGO_URL,
            data=json.dumps(payload),
            headers=headers
        )
        r.close()
        print(">> Forwarded to Server:", payload)
    except Exception as err:
        print("!! HTTP Error:", err)

# ---------- Main Loop ----------
print("Gateway running...")
last_ultrasonic_time = 0

while True:
    now = time.ticks_ms()

    # 1. Receive ESP-NOW packets
    try:
        host, msg = e.irecv(0)
        if msg:
            try:
                data = json.loads(msg.decode())
                print("<< Received ESP-NOW:", data)
                forward_to_django(data)
            except ValueError:
                print("Received non-JSON ESP-NOW payload")
    except Exception:
        pass

    # 2. Read both ultrasonic sensors and average
    if time.ticks_diff(now, last_ultrasonic_time) > ULTRASONIC_INTERVAL_MS:
        d1 = read_ultrasonic_cm(trig1, echo1)
        d2 = read_ultrasonic_cm(trig2, echo2)

        valid_readings = []
        if d1 is not None:
            valid_readings.append(d1)
        if d2 is not None:
            valid_readings.append(d2)

        if valid_readings:
            avg_distance = round(
                sum(valid_readings) / len(valid_readings),
                2
            )

            payload = {
                "nodeid": ULTRASONIC_NODE_ID,
                "value": avg_distance,
 #               "raw": {
  #                  "sensor1": d1,
   #                 "sensor2": d2
       #         }
            }

            forward_to_django(payload)
        else:
            print("Ultrasonic read failed on both sensors")

        last_ultrasonic_time = now

    time.sleep_ms(10)

