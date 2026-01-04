#!/bin/bash
# Quick Setup Script for Smart Drip Irrigation Server
# Run this on your laptop (Ubuntu/Debian)

set -e  # Exit on error

echo "======================================================"
echo "Smart Drip Irrigation - Laptop Server Setup"
echo "======================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Please don't run as root. Use regular user.${NC}"
   exit 1
fi

# Get laptop IP
echo -e "${YELLOW}[1/6] Detecting network configuration...${NC}"
LAPTOP_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n1)
echo "Detected IP: $LAPTOP_IP"
echo ""

# Update package list
echo -e "${YELLOW}[2/6] Updating package list...${NC}"
sudo apt update
echo ""

# Install Mosquitto MQTT broker
echo -e "${YELLOW}[3/6] Installing Mosquitto MQTT broker...${NC}"
if ! command -v mosquitto &> /dev/null; then
    sudo apt install -y mosquitto mosquitto-clients
    echo -e "${GREEN}✓ Mosquitto installed${NC}"
else
    echo -e "${GREEN}✓ Mosquitto already installed${NC}"
fi

# Enable and start Mosquitto
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

if systemctl is-active --quiet mosquitto; then
    echo -e "${GREEN}✓ Mosquitto is running${NC}"
else
    echo -e "${RED}✗ Mosquitto failed to start${NC}"
    exit 1
fi
echo ""

# Install Python dependencies
echo -e "${YELLOW}[4/6] Installing Python dependencies...${NC}"
if ! command -v pip3 &> /dev/null; then
    sudo apt install -y python3-pip
fi

pip3 install --user paho-mqtt pyserial python-dotenv colorlog
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Configure firewall
echo -e "${YELLOW}[5/6] Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    sudo ufw allow 1883/tcp  # MQTT
    sudo ufw allow 5000/tcp  # API (future)
    echo -e "${GREEN}✓ Firewall rules added${NC}"
else
    echo -e "${YELLOW}⚠ UFW not installed, skipping firewall config${NC}"
fi
echo ""

# Test MQTT broker
echo -e "${YELLOW}[6/6] Testing MQTT broker...${NC}"
timeout 2 mosquitto_sub -h localhost -t test/topic &
sleep 0.5
mosquitto_pub -h localhost -t test/topic -m "test"
sleep 0.5
echo -e "${GREEN}✓ MQTT broker is working${NC}"
echo ""

# Create summary
echo "======================================================"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "======================================================"
echo ""
echo "Configuration Summary:"
echo "  • Laptop IP:        $LAPTOP_IP"
echo "  • MQTT Broker:      localhost:1883"
echo "  • Status:           Running"
echo ""
echo "Update your ESP32 config.py with:"
echo "  MQTT_BROKER = \"$LAPTOP_IP\""
echo ""
echo "Next steps:"
echo "  1. cd server"
echo "  2. python3 mqtt_test_server.py"
echo "  3. Flash ESP32 with updated config"
echo "  4. Power on ESP32 and watch it connect!"
echo ""
echo "To monitor MQTT traffic:"
echo "  mosquitto_sub -h localhost -t 'irrigation/#' -v"
echo ""
echo "======================================================"
