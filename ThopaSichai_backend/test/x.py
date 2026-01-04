#!/usr/bin/env python3
"""
Test script to send POST request to soil moisture API endpoint
"""
import subprocess
import json
from datetime import datetime, timezone

# API endpoint
url = "http://localhost:8000/api/data/receive/"

# Data with just nodeid and value (timestamp will be auto-generated)
data = {
    "nodeid": "utsabbbbb",
    "value": 45.5,
}

# Build curl command
curl_command = [
    "curl",
    "-X", "POST",
    url,
    "-H", "Content-Type: application/json",
    "-d", json.dumps(data),
    "-v"  # verbose output to see response headers
]

print("Sending POST request to:", url)
print("Data:", json.dumps(data, indent=2))
print("\nCurl command:")
print(" ".join(curl_command))
print("\n" + "="*60 + "\n")

# Execute curl command
try:
    result = subprocess.run(curl_command, capture_output=True, text=True)
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    print("\nReturn code:", result.returncode)
except Exception as e:
    print(f"Error running curl: {e}")
