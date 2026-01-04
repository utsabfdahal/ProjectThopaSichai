import network
import urequests
import json
import time
import gc

gc.collect()

SSID = "x"
PASSWORD = "duckduckduck"

URL = "http://192.168.16.106:8000/api/soil-moisture/receive/"
# this is the ip address of the pc where django backend is running
# this endpoint takes json data from esp32 into port 8000

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)

    ip = wlan.ifconfig()[0]
    print("Connected with IP:", ip)
    return ip

ip = connect_wifi()

payload = {
    "data": {
      "moisture_level": 7777,
    },
    "metadata": {
      "location": "ku",
    },
    "ip_address": ip
  }

headers = {
    "Content-Type": "application/json",
    "Connection": "close"
}

try:
    gc.collect()

    response = urequests.post(
        URL,
        data=json.dumps(payload),
        headers=headers
    )

    print("Status:", response.status_code)
    print("Response:", response.text)

    response.close()
    del response
    gc.collect()

except Exception as e:
    print("Request failed:", e)
