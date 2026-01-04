# Example: WiFi and Web Server on ESP32

from machine import Pin
import network
import socket
import time

# Configure LED
led = Pin(2, Pin.OUT)

# WiFi Configuration
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

def connect_wifi():
    """Connect to WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(SSID, PASSWORD)
        
        while not wlan.isconnected():
            time.sleep(1)
            print('.', end='')
    
    print('\nWiFi Connected!')
    print('IP Address:', wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

def web_server():
    """Simple web server to control LED"""
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    
    print('Web server running on http://' + connect_wifi())
    
    html = """<!DOCTYPE html>
<html>
<head><title>ESP32 Control</title></head>
<body>
    <h1>ESP32 LED Control</h1>
    <p><a href="/led/on"><button style="font-size:20px;padding:10px">LED ON</button></a></p>
    <p><a href="/led/off"><button style="font-size:20px;padding:10px">LED OFF</button></a></p>
</body>
</html>
"""
    
    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024)
        request = str(request)
        
        if '/led/on' in request:
            led.on()
            print('LED turned ON')
        elif '/led/off' in request:
            led.off()
            print('LED turned OFF')
        
        response = html
        cl.send('HTTP/1.1 200 OK\r\n')
        cl.send('Content-Type: text/html\r\n')
        cl.send('Connection: close\r\n\r\n')
        cl.sendall(response)
        cl.close()

# Uncomment to run web server
# web_server()
